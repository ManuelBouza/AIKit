"""Estado compartido y tipado de disponibilidad de cuentas OpenCode.

No consulta red ni infiere. Solo valida, serializa y persiste el snapshot
mutable fuera de Git, reutilizando locks y reemplazo atómico del almacén.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, NewType, TypeAlias, cast

from availability_performance import PerformanceSample, sample_from_dict, sample_to_dict
from availability_public_terms import PublicTerm
from session_store import (
    StoreError,
    _atomic_replace,
    _lock_file,
    _open_shared_read,
    _require_directory,
    _require_regular_file,
    _without_duplicate_keys,
)

STATE_SCHEMA_VERSION = 1
STATE_FILENAME = "availability-state.json"
STATE_MAX_BYTES = 4 * 1024 * 1024
STATE_MAX_DEPTH = 16
MAX_TEXT_CHARS = 256
MAX_ALIAS_CHARS = 128

AccountAlias = NewType("AccountAlias", str)
ModelKey = NewType("ModelKey", str)

AvailabilityStatus: TypeAlias = Literal["available", "exhausted", "unknown", "error"]
LimitScope: TypeAlias = Literal["model", "account", "shared_group", "unknown"]
Precision: TypeAlias = Literal["confirmed", "estimated", "unavailable"]
DataSourceState: TypeAlias = Literal["ok", "error", "unknown"]


@dataclass(frozen=True)
class PricingTier:
    input: float
    output: float
    cache_read: float = 0.0
    cache_write: float = 0.0
    context_size: float | None = None


@dataclass(frozen=True)
class ModelMetadata:
    model: str
    name: str
    pricing: tuple[PricingTier, ...]
    variants: tuple[str, ...]
    tools: bool
    input_modalities: tuple[str, ...]
    output_modalities: tuple[str, ...]
    context_limit: int | None
    output_limit: int | None
    free_candidate: bool | None
    may_use_openai_quota: bool | None
    input_limit: int | None = None


@dataclass(frozen=True)
class CatalogContext:
    project_key: str
    config_sources: tuple[str, ...]
    config_signature: str | None = None
    service_version: str | None = None
    capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class QuotaObservation:
    status: AvailabilityStatus
    source: str
    asof: datetime
    limit_scope: LimitScope
    reset_at: datetime | None
    precision: Precision
    percent: int | None
    limited: bool | None


@dataclass(frozen=True)
class QueryAttempt:
    at: datetime
    result: str
    error_code: str | None
    attempt_id: str | None = None


@dataclass(frozen=True)
class AvailabilityRecord:
    provider: str
    account_alias: AccountAlias
    model: str
    limit_scope: LimitScope
    status: AvailabilityStatus
    observed_at: datetime
    last_valid_observation: QuotaObservation | None
    last_query_attempt: QueryAttempt | None
    reset_at: datetime | None
    precision: Precision
    next_check_at: datetime | None
    shared_scope_known: bool


@dataclass(frozen=True)
class ModelEntry:
    metadata: ModelMetadata
    quota: QuotaObservation | None
    context_key: str
    query_attempt: QueryAttempt | None = None
    outcome_attempt_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class DataSourceStatus:
    name: str
    status: DataSourceState
    error_code: str | None


@dataclass(frozen=True)
class AggregateObservation:
    provider: str
    scope: str
    observation: QuotaObservation


@dataclass(frozen=True)
class AvailabilitySnapshot:
    schema_version: int
    generation: int
    published_at: datetime
    catalog_contexts: tuple[CatalogContext, ...]
    models: dict[str, ModelEntry]
    data_sources: tuple[DataSourceStatus, ...]
    aggregates: tuple[AggregateObservation, ...] = ()
    performance_samples: tuple[PerformanceSample, ...] = ()
    project_models: dict[str, dict[str, ModelEntry]] = field(default_factory=dict)
    last_refresh: CatalogContext | None = None
    public_terms: tuple[PublicTerm, ...] = ()

    def __init__(
        self,
        schema_version: int,
        generation: int,
        published_at: datetime,
        catalog_contexts: tuple[CatalogContext, ...],
        models: dict[str, ModelEntry],
        data_sources: tuple[DataSourceStatus, ...],
        aggregates: tuple[AggregateObservation, ...] = (),
        performance_samples: tuple[PerformanceSample, ...] = (),
        project_models: dict[str, dict[str, ModelEntry]] | None = None,
        last_refresh: CatalogContext | None = None,
        public_terms: tuple[PublicTerm, ...] = (),
        **kwargs: object,
    ) -> None:
        canonical = public_terms
        for alias in (
            "public_facts",
            "public_access",
            "public_access_terms",
            "conditional_access",
        ):
            candidate = kwargs.get(alias)
            if not canonical and isinstance(candidate, tuple):
                canonical = candidate
        if project_models is None:
            project_models = {}
        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "generation", generation)
        object.__setattr__(self, "published_at", published_at)
        object.__setattr__(self, "catalog_contexts", catalog_contexts)
        object.__setattr__(self, "models", models)
        object.__setattr__(self, "data_sources", data_sources)
        object.__setattr__(self, "aggregates", aggregates)
        object.__setattr__(self, "performance_samples", performance_samples)
        object.__setattr__(self, "project_models", project_models)
        object.__setattr__(self, "last_refresh", last_refresh)
        object.__setattr__(self, "public_terms", canonical)

    @property
    def public_facts(self) -> tuple[PublicTerm, ...]:
        return self.public_terms

    @property
    def public_access(self) -> tuple[PublicTerm, ...]:
        return self.public_terms

    @property
    def public_access_terms(self) -> tuple[PublicTerm, ...]:
        return self.public_terms

    @property
    def conditional_access(self) -> tuple[PublicTerm, ...]:
        return self.public_terms


@dataclass(frozen=True)
class CatalogAdmission:
    generation: int
    project_key: str
    config_signature: str
    service_version: str
    model: str
    variant: str | None
    metadata_signature: str


def configuration_signature(payload: object) -> str:
    """Huella SOLO del contrato publico de seleccion/permisos; no identidad de cuenta.

    Cambios privados de credencial requieren notificacion/refresco explicito.
    Nunca se serializa ni se deriva una huella de esos valores.
    """
    allowed = {
        "type",
        "info",
        "policies",
        "experimental",
        "action",
        "resource",
        "effect",
        "permission",
        "permissions",
        "pattern",
        "model",
        "models",
        "provider",
        "providers",
        "enabled",
        "disabled",
        "variants",
        "tools",
        "capabilities",
        "limit",
        "limits",
        "context",
        "input",
        "output",
        "agent",
        "agents",
        "default",
    }
    model_maps = {"models", "providers", "agents", "variants"}

    def project(value: object, *, dynamic: bool = False, depth: int = 0) -> object:
        if depth > 32:
            raise ValueError("Contrato de configuracion demasiado profundo.")
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    continue
                if key in {
                    "password",
                    "token",
                    "credential",
                    "apiKey",
                    "api_key",
                    "headers",
                    "env",
                    "auth",
                    "name",
                    "email",
                    "path",
                    "url",
                    "workspace",
                }:
                    continue
                if (
                    key in allowed
                    or dynamic
                    and re.fullmatch(r"[A-Za-z0-9_./:#*-]{1,256}", key)
                ):
                    result[key] = project(
                        item, dynamic=key in model_maps, depth=depth + 1
                    )
            return result
        if isinstance(value, list):
            return [project(item, depth=depth + 1) for item in value]
        if isinstance(value, (str, bool, int, float)) or value is None:
            return value
        raise ValueError("Contrato de configuracion invalido.")

    raw = json.dumps(
        project(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()
    return "selection-v1-" + hashlib.sha256(raw).hexdigest()


def model_entry(
    snapshot: AvailabilitySnapshot, project_key: str, model: str
) -> ModelEntry | None:
    entries = snapshot.project_models.get(project_key)
    if entries is not None:
        return entries.get(model)
    entry = snapshot.models.get(model)
    return entry if entry is not None and entry.context_key == project_key else None


def metadata_signature(metadata: ModelMetadata) -> str:
    payload = _metadata_to_json(metadata)
    payload.pop("name", None)
    return hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def admission_for(
    snapshot: AvailabilitySnapshot, project_key: str, model: str, variant: str | None
) -> CatalogAdmission:
    context = next(
        (item for item in snapshot.catalog_contexts if item.project_key == project_key),
        None,
    )
    entry = model_entry(snapshot, project_key, model)
    if (
        context is None
        or context.config_signature is None
        or context.service_version is None
        or not {"config.get", "model.catalog"}.issubset(context.capabilities)
        or entry is None
    ):
        raise StoreError(
            "availability_context_unavailable", "Contrato de catalogo no acreditado."
        )
    return CatalogAdmission(
        snapshot.generation,
        project_key,
        context.config_signature,
        context.service_version,
        model,
        variant,
        metadata_signature(entry.metadata),
    )


def admission_from_json(value: object) -> CatalogAdmission | None:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != set(
        CatalogAdmission.__dataclass_fields__
    ):
        raise _corrupt()
    generation = _int(value["generation"])
    if generation <= 0:
        raise _corrupt()
    project_key = _text(value["project_key"])
    signature = _text(value["config_signature"])
    version = _text(value["service_version"])
    model = _text(value["model"])
    variant = _text(value["variant"], optional=True)
    metadata = _text(value["metadata_signature"])
    if (
        project_key is None
        or signature is None
        or version is None
        or model is None
        or metadata is None
        or re.fullmatch(r"selection-v1-[0-9a-f]{64}", signature) is None
        or re.fullmatch(r"[0-9a-f]{64}", metadata) is None
    ):
        raise _corrupt()
    return CatalogAdmission(
        generation, project_key, signature, version, model, variant, metadata
    )


def state_path(state_dir: Path) -> Path:
    """Ruta del snapshot bajo el estado del host; nunca una ruta personal fija."""
    return state_dir / STATE_FILENAME


def empty_snapshot(now: datetime | None = None) -> AvailabilitySnapshot:
    return AvailabilitySnapshot(
        schema_version=STATE_SCHEMA_VERSION,
        generation=0,
        published_at=now or datetime.now(timezone.utc),
        catalog_contexts=(),
        models={},
        data_sources=(),
    )


def record_with_unknown_alias(provider: str, model: str) -> AvailabilityRecord:
    """Alias no acreditable: nunca se marca disponible ni se reutiliza certeza."""
    now = datetime.now(timezone.utc)
    return AvailabilityRecord(
        provider=provider,
        account_alias=AccountAlias(""),
        model=model,
        limit_scope="unknown",
        status="unknown",
        observed_at=now,
        last_valid_observation=None,
        last_query_attempt=None,
        reset_at=None,
        precision="unavailable",
        next_check_at=None,
        shared_scope_known=False,
    )


def read_snapshot(path: Path) -> AvailabilitySnapshot | None:
    """Lee el snapshot sin crear ni reparar nada; None si aún no existe."""
    try:
        _require_regular_file(path)
    except StoreError as error:
        if isinstance(error.__cause__, FileNotFoundError):
            return None
        raise
    try:
        with _open_shared_read(path) as stream:
            raw = stream.read(STATE_MAX_BYTES + 1)
    except OSError as exc:
        raise StoreError("availability_io", "No se pudo leer el estado.") from exc
    if len(raw) > STATE_MAX_BYTES:
        raise StoreError("availability_too_large", "El estado excede el límite.")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise StoreError("availability_corrupt", "El estado no es UTF-8.") from exc
    try:
        data = json.loads(text, object_pairs_hook=_without_duplicate_keys)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise StoreError("availability_corrupt", "El estado está corrupto.") from exc
    if _depth(data) > STATE_MAX_DEPTH:
        raise StoreError("availability_corrupt", "El estado es demasiado profundo.")
    return _snapshot_from_json(data)


def write_snapshot(
    path: Path,
    snapshot: AvailabilitySnapshot,
    *,
    fail_before_replace: bool = False,
    timeout: float = 10.0,
) -> None:
    """Escribe con bloqueo y reemplazo atómico; nunca deja bytes a medias."""
    _ensure_state_directory(path.parent)

    def action() -> None:
        _write_snapshot_locked(path, snapshot, fail_before_replace=fail_before_replace)

    _with_state_lock(path, action, timeout=timeout)


def update_snapshot(
    path: Path, mutate: Callable[[AvailabilitySnapshot], AvailabilitySnapshot]
) -> AvailabilitySnapshot:
    """Lee-modifica-escribe bajo el mismo bloqueo que write_snapshot."""
    _ensure_state_directory(path.parent)

    def action() -> AvailabilitySnapshot:
        current = read_snapshot(path) or empty_snapshot()
        updated = mutate(current)
        _write_snapshot_locked(path, updated)
        return updated

    return cast(AvailabilitySnapshot, _with_state_lock(path, action))


def _with_state_lock(
    path: Path, action: Callable[[], Any], *, timeout: float = 10.0
) -> Any:
    """Reintenta de forma acotada si otro proceso mantiene el bloqueo breve."""
    deadline = time.monotonic() + max(0.0, timeout)
    lock_path = path.parent / (STATE_FILENAME + ".lock")
    while True:
        try:
            with _lock_file(lock_path):
                return action()
        except StoreError as error:
            if error.code != "lock_contended" or time.monotonic() >= deadline:
                raise
            time.sleep(min(0.02, max(0.0, deadline - time.monotonic())))


def _write_snapshot_locked(
    path: Path, snapshot: AvailabilitySnapshot, *, fail_before_replace: bool = False
) -> None:
    _validate_snapshot(snapshot)
    payload = _snapshot_to_json(snapshot)
    if path.exists() or path.is_symlink():
        _require_regular_file(path)
    descriptor = -1
    temporary: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".availability-", suffix=".tmp", dir=path.parent
        )
        temporary = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            descriptor = -1
            json.dump(
                payload,
                stream,
                ensure_ascii=False,
                allow_nan=False,
                indent=2,
                sort_keys=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        if fail_before_replace:
            raise StoreError("availability_io", "Fallo inyectado antes de publicar.")
        _atomic_replace(temporary, path)
        temporary = None
    except StoreError:
        raise
    except OSError as exc:
        raise StoreError("availability_io", "No se pudo guardar el estado.") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass


def _ensure_state_directory(state_dir: Path) -> None:
    try:
        _require_directory(state_dir)
    except StoreError as error:
        if not isinstance(error.__cause__, FileNotFoundError):
            raise
        try:
            state_dir.mkdir(parents=True, mode=0o700, exist_ok=True)
        except OSError as exc:
            raise StoreError("availability_io", "No se pudo crear el estado.") from exc
        _require_directory(state_dir)


def _depth(value: Any, current: int = 0) -> int:
    if current > STATE_MAX_DEPTH:
        return current
    if isinstance(value, dict):
        if not value:
            return current + 1
        return max(_depth(v, current + 1) for v in value.values())
    if isinstance(value, list):
        if not value:
            return current + 1
        return max(_depth(v, current + 1) for v in value)
    return current


def _timestamp(value: object) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise _corrupt()
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise _corrupt() from exc
    if parsed.tzinfo is None:
        raise _corrupt()
    return parsed.astimezone(timezone.utc)


def _timestamp_required(value: object) -> datetime:
    parsed = _timestamp(value)
    if parsed is None:
        raise _corrupt()
    return parsed


def _text(value: object, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value or len(value) > MAX_TEXT_CHARS:
        raise _corrupt()
    return value


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise _corrupt()
    return value


def _bool(value: object) -> bool:
    if not isinstance(value, bool):
        raise _corrupt()
    return value


def _float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _corrupt()
    return float(value)


def _status(value: object) -> AvailabilityStatus:
    if value == "available":
        return "available"
    if value == "exhausted":
        return "exhausted"
    if value == "unknown":
        return "unknown"
    if value == "error":
        return "error"
    raise _corrupt()


def _scope(value: object) -> LimitScope:
    if value == "model":
        return "model"
    if value == "account":
        return "account"
    if value == "shared_group":
        return "shared_group"
    if value == "unknown":
        return "unknown"
    raise _corrupt()


def _precision(value: object) -> Precision:
    if value == "confirmed":
        return "confirmed"
    if value == "estimated":
        return "estimated"
    if value == "unavailable":
        return "unavailable"
    raise _corrupt()


def _data_state(value: object) -> DataSourceState:
    if value == "ok":
        return "ok"
    if value == "error":
        return "error"
    if value == "unknown":
        return "unknown"
    raise _corrupt()


def _corrupt() -> StoreError:
    return StoreError("availability_corrupt", "El estado no cumple el esquema.")


def _snapshot_to_json(snapshot: AvailabilitySnapshot) -> dict[str, Any]:
    return {
        "schema_version": snapshot.schema_version,
        "generation": snapshot.generation,
        "published_at": snapshot.published_at.isoformat(),
        "catalog_contexts": [
            _context_to_json(item) for item in snapshot.catalog_contexts
        ],
        "models": {
            key: {
                "metadata": _metadata_to_json(entry.metadata),
                "quota": _observation_to_json(entry.quota),
                "context_key": entry.context_key,
                "query_attempt": _query_attempt_to_json(entry.query_attempt),
                "outcome_attempt_ids": list(entry.outcome_attempt_ids),
            }
            for key, entry in snapshot.models.items()
        },
        "data_sources": [
            {"name": s.name, "status": s.status, "error_code": s.error_code}
            for s in snapshot.data_sources
        ],
        "aggregates": [
            {
                "provider": item.provider,
                "scope": item.scope,
                "observation": _observation_to_json(item.observation),
            }
            for item in snapshot.aggregates
            if item.observation is not None
        ],
        "performance_samples": [
            sample_to_dict(item) for item in snapshot.performance_samples
        ],
        "project_models": {
            project: {key: _entry_to_json(entry) for key, entry in entries.items()}
            for project, entries in snapshot.project_models.items()
        },
        "last_refresh": _context_to_json(snapshot.last_refresh)
        if snapshot.last_refresh is not None
        else None,
        "public_terms": [item.to_dict() for item in snapshot.public_terms],
        "public_facts": [item.to_dict() for item in snapshot.public_terms],
        "public_access": [item.to_dict() for item in snapshot.public_terms],
        "public_access_terms": [item.to_dict() for item in snapshot.public_terms],
        "conditional_access": [item.to_dict() for item in snapshot.public_terms],
    }


def _context_to_json(context: CatalogContext) -> dict[str, Any]:
    return {
        "project_key": context.project_key,
        "config_sources": list(context.config_sources),
        "config_signature": context.config_signature,
        "service_version": context.service_version,
        "capabilities": list(context.capabilities),
    }


def _entry_to_json(entry: ModelEntry) -> dict[str, Any]:
    return {
        "metadata": _metadata_to_json(entry.metadata),
        "quota": _observation_to_json(entry.quota),
        "context_key": entry.context_key,
        "query_attempt": _query_attempt_to_json(entry.query_attempt),
        "outcome_attempt_ids": list(entry.outcome_attempt_ids),
    }


def _metadata_to_json(metadata: ModelMetadata) -> dict[str, Any]:
    return {
        "model": metadata.model,
        "name": metadata.name,
        "pricing": [
            {
                "input": tier.input,
                "output": tier.output,
                "cache_read": tier.cache_read,
                "cache_write": tier.cache_write,
                "context_size": tier.context_size,
            }
            for tier in metadata.pricing
        ],
        "variants": list(metadata.variants),
        "tools": metadata.tools,
        "input_modalities": list(metadata.input_modalities),
        "output_modalities": list(metadata.output_modalities),
        "context_limit": metadata.context_limit,
        "input_limit": metadata.input_limit,
        "output_limit": metadata.output_limit,
        "free_candidate": metadata.free_candidate,
        "may_use_openai_quota": metadata.may_use_openai_quota,
    }


def _observation_to_json(observation: QuotaObservation | None) -> dict[str, Any] | None:
    if observation is None:
        return None
    return {
        "status": observation.status,
        "source": observation.source,
        "asof": observation.asof.isoformat(),
        "limit_scope": observation.limit_scope,
        "reset_at": observation.reset_at.isoformat() if observation.reset_at else None,
        "precision": observation.precision,
        "percent": observation.percent,
        "limited": observation.limited,
    }


def _public_terms_from_json(value: object) -> tuple[PublicTerm, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise _corrupt()
    result: list[PublicTerm] = []
    seen: set[tuple[str, str]] = set()
    for item in value:
        if not isinstance(item, dict):
            raise _corrupt()
        try:
            term = PublicTerm.from_dict(item)
        except (ValueError, TypeError, KeyError) as exc:
            raise _corrupt() from exc
        key = (term.provider, term.model)
        if key in seen:
            raise _corrupt()
        seen.add(key)
        result.append(term)
    if len(result) > 1000:
        raise _corrupt()
    return tuple(result)


def _snapshot_from_json(data: object) -> AvailabilitySnapshot:
    if not isinstance(data, dict):
        raise _corrupt()
    version = _int(data.get("schema_version"))
    if version > STATE_SCHEMA_VERSION:
        raise StoreError(
            "availability_schema_future", "El estado pertenece a un esquema futuro."
        )
    if version != STATE_SCHEMA_VERSION:
        raise _corrupt()
    generation = _int(data.get("generation"))
    if generation < 0:
        raise _corrupt()
    published_at = _timestamp_required(data.get("published_at"))
    contexts_raw = data.get("catalog_contexts")
    if not isinstance(contexts_raw, list):
        raise _corrupt()
    contexts = tuple(_context_from_json(item) for item in contexts_raw)
    models_raw = data.get("models")
    if not isinstance(models_raw, dict):
        raise _corrupt()
    models: dict[str, ModelEntry] = {}
    for key, value in models_raw.items():
        if not isinstance(key, str) or len(key) > MAX_TEXT_CHARS:
            raise _corrupt()
        models[key] = _entry_from_json(value)
    sources_raw = data.get("data_sources")
    if not isinstance(sources_raw, list):
        raise _corrupt()
    sources = tuple(_source_from_json(item) for item in sources_raw)
    aggregates_raw = data.get("aggregates", [])
    if not isinstance(aggregates_raw, list):
        raise _corrupt()
    aggregates = tuple(_aggregate_from_json(item) for item in aggregates_raw)
    performance_raw = data.get("performance_samples", [])
    if not isinstance(performance_raw, list):
        raise _corrupt()
    performance_samples_list: list[PerformanceSample] = []
    for item in performance_raw:
        if not isinstance(item, dict):
            raise _corrupt()
        try:
            sample = sample_from_dict(item)
        except (ValueError, TypeError, KeyError, RecursionError) as exc:
            raise _corrupt() from exc
        performance_samples_list.append(sample)
    if len(performance_samples_list) > 1000:
        raise _corrupt()
    performance_samples = tuple(performance_samples_list)
    raw_projects = data.get("project_models", {})
    if not isinstance(raw_projects, dict):
        raise _corrupt()
    projects: dict[str, dict[str, ModelEntry]] = {}
    for project, raw_entries in raw_projects.items():
        if (
            not isinstance(project, str)
            or len(project) > MAX_TEXT_CHARS
            or not isinstance(raw_entries, dict)
        ):
            raise _corrupt()
        entries = {}
        for key, raw_entry in raw_entries.items():
            if not isinstance(key, str) or len(key) > MAX_TEXT_CHARS:
                raise _corrupt()
            entry = _entry_from_json(raw_entry)
            if entry.context_key != project or entry.metadata.model != key:
                raise _corrupt()
            entries[key] = entry
        projects[project] = entries
    last = data.get("last_refresh")
    public_raw = None
    for key in (
        "public_terms",
        "public_facts",
        "public_access",
        "public_access_terms",
        "conditional_access",
    ):
        candidate = data.get(key)
        if isinstance(candidate, list) and candidate:
            public_raw = candidate
            break
    if public_raw is None:
        # Soporta alias aunque venga vacío.
        for key in (
            "public_terms",
            "public_facts",
            "public_access",
            "public_access_terms",
            "conditional_access",
        ):
            if key in data:
                public_raw = data.get(key)
                break
    public_terms = _public_terms_from_json(public_raw)
    return AvailabilitySnapshot(
        schema_version=version,
        generation=generation,
        published_at=published_at,
        catalog_contexts=contexts,
        models=models,
        data_sources=sources,
        aggregates=aggregates,
        performance_samples=performance_samples,
        project_models=projects,
        last_refresh=_context_from_json(last) if last is not None else None,
        public_terms=public_terms,
    )


def _context_from_json(data: object) -> CatalogContext:
    if not isinstance(data, dict):
        raise _corrupt()
    project_key = _text(data.get("project_key"))
    sources = data.get("config_sources")
    if not isinstance(sources, list):
        raise _corrupt()
    cleaned: list[str] = []
    for item in sources:
        value = _text(item)
        assert value is not None
        cleaned.append(value)
    return CatalogContext(
        project_key=project_key or "",
        config_sources=tuple(cleaned),
        config_signature=_text(data.get("config_signature"), optional=True),
        service_version=_text(data.get("service_version"), optional=True),
        capabilities=_string_tuple(data.get("capabilities", [])),
    )


def _entry_from_json(data: object) -> ModelEntry:
    if not isinstance(data, dict):
        raise _corrupt()
    metadata = _metadata_from_json(data.get("metadata"))
    quota_raw = data.get("quota")
    quota = None if quota_raw is None else _observation_from_json(quota_raw)
    context_key = _text(data.get("context_key"))
    attempt_raw = data.get("query_attempt")
    attempt = None if attempt_raw is None else _query_attempt_from_json(attempt_raw)
    return ModelEntry(
        metadata=metadata,
        quota=quota,
        context_key=context_key or "",
        query_attempt=attempt,
        outcome_attempt_ids=_string_tuple(data.get("outcome_attempt_ids", [])),
    )


def _metadata_from_json(data: object) -> ModelMetadata:
    if not isinstance(data, dict):
        raise _corrupt()
    model = _text(data.get("model"))
    name = _text(data.get("name"))
    if model is None or name is None:
        raise _corrupt()
    pricing_raw = data.get("pricing")
    if not isinstance(pricing_raw, list):
        raise _corrupt()
    pricing = tuple(_tier_from_json(item) for item in pricing_raw)
    variants = _string_tuple(data.get("variants"))
    input_modalities = _string_tuple(data.get("input_modalities"))
    output_modalities = _string_tuple(data.get("output_modalities"))
    context_limit = _optional_int(data.get("context_limit"))
    input_limit = _optional_int(data.get("input_limit"))
    output_limit = _optional_int(data.get("output_limit"))
    free_candidate = _optional_bool(data.get("free_candidate"))
    may_use_openai_quota = _optional_bool(data.get("may_use_openai_quota"))
    return ModelMetadata(
        model=model,
        name=name,
        pricing=pricing,
        variants=variants,
        tools=_bool(data.get("tools")),
        input_modalities=input_modalities,
        output_modalities=output_modalities,
        context_limit=context_limit,
        input_limit=input_limit,
        output_limit=output_limit,
        free_candidate=free_candidate,
        may_use_openai_quota=may_use_openai_quota,
    )


def _tier_from_json(data: object) -> PricingTier:
    if not isinstance(data, dict):
        raise _corrupt()
    return PricingTier(
        input=_float(data.get("input")),
        output=_float(data.get("output")),
        cache_read=_float(data.get("cache_read")),
        cache_write=_float(data.get("cache_write")),
        context_size=None
        if data.get("context_size") is None
        else _float(data["context_size"]),
    )


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise _corrupt()
    result: list[str] = []
    for item in value:
        text = _text(item)
        if text is None:
            raise _corrupt()
        result.append(text)
    return tuple(result)


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    return _int(value)


def _optional_bool(value: object) -> bool | None:
    if value is None:
        return None
    return _bool(value)


def _observation_from_json(data: object) -> QuotaObservation:
    if not isinstance(data, dict):
        raise _corrupt()
    source = _text(data.get("source"))
    if source is None:
        raise _corrupt()
    percent_raw = data.get("percent")
    percent = None if percent_raw is None else _int(percent_raw)
    limited_raw = data.get("limited")
    limited = None if limited_raw is None else _bool(limited_raw)
    return QuotaObservation(
        status=_status(data.get("status")),
        source=source,
        asof=_timestamp_required(data.get("asof")),
        limit_scope=_scope(data.get("limit_scope")),
        reset_at=_timestamp(data.get("reset_at")),
        precision=_precision(data.get("precision")),
        percent=percent,
        limited=limited,
    )


def _source_from_json(data: object) -> DataSourceStatus:
    if not isinstance(data, dict):
        raise _corrupt()
    name = _text(data.get("name"))
    if name is None:
        raise _corrupt()
    error_raw = data.get("error_code")
    error = None if error_raw is None else _text(error_raw)
    return DataSourceStatus(
        name=name, status=_data_state(data.get("status")), error_code=error
    )


def _query_attempt_to_json(attempt: QueryAttempt | None) -> dict[str, Any] | None:
    if attempt is None:
        return None
    return {
        "at": attempt.at.isoformat(),
        "result": attempt.result,
        "error_code": attempt.error_code,
        "attempt_id": attempt.attempt_id,
    }


def _query_attempt_from_json(data: object) -> QueryAttempt:
    if not isinstance(data, dict):
        raise _corrupt()
    result = _text(data.get("result"))
    if result is None:
        raise _corrupt()
    error_raw = data.get("error_code")
    error = None if error_raw is None else _text(error_raw)
    return QueryAttempt(
        at=_timestamp_required(data.get("at")),
        result=result,
        error_code=error,
        attempt_id=_text(data.get("attempt_id"), optional=True),
    )


def _aggregate_from_json(data: object) -> AggregateObservation:
    if not isinstance(data, dict):
        raise _corrupt()
    provider = _text(data.get("provider"))
    scope = _text(data.get("scope"))
    if provider is None or scope is None:
        raise _corrupt()
    observation = _observation_from_json(data.get("observation"))
    return AggregateObservation(provider=provider, scope=scope, observation=observation)


def _validate_snapshot(snapshot: AvailabilitySnapshot) -> None:
    try:
        _snapshot_from_json(_snapshot_to_json(snapshot))
    except (ValueError, TypeError, AttributeError, KeyError, RecursionError) as exc:
        raise StoreError(
            "availability_corrupt", "Snapshot o muestras fuera de contrato."
        ) from exc
