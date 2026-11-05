"""Refresh read-only de disponibilidad OpenCode."""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from availability_state import (
    AggregateObservation,
    AvailabilitySnapshot,
    CatalogContext,
    DataSourceStatus,
    ModelEntry,
    ModelMetadata,
    PricingTier,
    QuotaObservation,
    _ensure_state_directory,
    empty_snapshot,
    read_snapshot,
    write_snapshot,
)
from delegate import _project_key, _public_model
from session_store import StoreError, _lock_file


class RefreshBinding(Protocol):
    """Lecturas existentes; ManagedBinding aporta autenticacion y verificacion."""

    def openapi_schema(self, *, timeout: float) -> object: ...
    def integrations(self, *, timeout: float) -> object: ...
    def model_catalog(self, project: Path, *, timeout: float) -> object: ...
    def usage_limits(self, project: Path, *, timeout: float) -> object: ...


@dataclass
class RefreshResult:
    snapshot: AvailabilitySnapshot
    refreshed: bool
    generation: int
    errors: tuple[str, ...]
    changes: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: {
            "added": (),
            "removed": (),
            "changed": (),
            "unchanged": (),
        }
    )

    @property
    def delta(self) -> dict[str, tuple[str, ...]]:
        return self.changes

    @property
    def added(self) -> tuple[str, ...]:
        return self.changes.get("added", ())

    @property
    def removed(self) -> tuple[str, ...]:
        return self.changes.get("removed", ())

    @property
    def changed_models(self) -> tuple[str, ...]:
        return self.changes.get("changed", ())

    @property
    def unchanged_models(self) -> tuple[str, ...]:
        return self.changes.get("unchanged", ())

    @property
    def changed(self) -> tuple[str, ...]:
        return self.changes.get("changed", ())

    @property
    def unchanged(self) -> tuple[str, ...]:
        return self.changes.get("unchanged", ())

    @property
    def added_models(self) -> tuple[str, ...]:
        return self.added

    @property
    def removed_models(self) -> tuple[str, ...]:
        return self.removed


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _lock_path(state_dir: Path) -> Path:
    return state_dir / "availability-refresh.lock"


def _with_refresh_lock(
    state_dir: Path, action: Callable[[], Any], timeout: float
) -> Any:
    deadline = time.monotonic() + max(0.1, timeout)
    while True:
        try:
            with _lock_file(_lock_path(state_dir)):
                return action()
        except StoreError as error:
            if (
                getattr(error, "code", "") != "lock_contended"
                or time.monotonic() >= deadline
            ):
                raise
            time.sleep(0.02)


def _capabilities_from_schema(schema: object) -> set[str]:
    if not isinstance(schema, dict):
        return set()
    paths = schema.get("paths")
    if not isinstance(paths, dict):
        return set()
    result: set[str] = set()
    for path, methods in paths.items():
        if not isinstance(path, str) or not isinstance(methods, dict):
            continue
        for method in methods:
            if isinstance(method, str):
                result.add(f"{method.upper()} {path}")
    return result


def _metadata_from_public(public: dict[str, Any]) -> ModelMetadata:
    limits = public.get("limits")
    context_limit = None
    input_limit = None
    output_limit = None
    if isinstance(limits, dict):
        if isinstance(limits.get("context"), int) and not isinstance(
            limits.get("context"), bool
        ):
            context_limit = limits["context"]
        if isinstance(limits.get("input"), int) and not isinstance(
            limits.get("input"), bool
        ):
            input_limit = limits["input"]
        if isinstance(limits.get("output"), int) and not isinstance(
            limits.get("output"), bool
        ):
            output_limit = limits["output"]
    tiers_raw = public.get("pricing_tiers")
    pricing: tuple[PricingTier, ...] = ()
    if isinstance(tiers_raw, list):
        pricing = tuple(
            PricingTier(
                input=float(tier.get("input", 0)),
                output=float(tier.get("output", 0)),
                cache_read=float(tier.get("cache", {}).get("read", 0)),
                cache_write=float(tier.get("cache", {}).get("write", 0)),
                context_size=float(tier["tier"]["size"])
                if isinstance(tier.get("tier"), dict)
                else None,
            )
            for tier in tiers_raw
            if isinstance(tier, dict)
        )
    variants_raw = public.get("variants")
    variants = (
        tuple(
            str(item.get("id"))
            for item in variants_raw
            if isinstance(item, dict) and item.get("id")
        )
        if isinstance(variants_raw, list)
        else ()
    )
    input_modalities = tuple(
        str(x) for x in public.get("input", []) if isinstance(x, str)
    )
    output_modalities = tuple(
        str(x) for x in public.get("output", []) if isinstance(x, str)
    )
    free_candidate = public.get("free_candidate")
    may_use_openai_quota = public.get("may_use_openai_quota")
    return ModelMetadata(
        model=str(public["model"]),
        name=str(public.get("name", public["model"])),
        pricing=pricing,
        variants=variants,
        tools=bool(public.get("tools", False)),
        input_modalities=input_modalities,
        output_modalities=output_modalities,
        context_limit=context_limit,
        input_limit=input_limit,
        output_limit=output_limit,
        free_candidate=free_candidate if isinstance(free_candidate, bool) else None,
        may_use_openai_quota=may_use_openai_quota
        if isinstance(may_use_openai_quota, bool)
        else None,
    )


def _parse_usage_limits(payload: object, project: Path) -> QuotaObservation | None:
    if isinstance(payload, dict) and "data" in payload:
        location = payload.get("location")
        if not isinstance(location, dict):
            return None
        directory = location.get("directory")
        if not isinstance(directory, str) or not directory:
            return None
        location_path = Path(directory)
        if not location_path.is_absolute() or _project_key(
            location_path
        ) != _project_key(project):
            return None
        payload = payload["data"]
    if not isinstance(payload, dict) or not isinstance(payload.get("go"), dict):
        return None
    go = payload["go"]
    if not isinstance(go.get("weekly"), dict):
        return None
    windows = [go[name] for name in ("rolling", "weekly", "monthly") if name in go]
    if any(
        not isinstance(window, dict) or type(window.get("limited")) is not bool
        for window in windows
    ):
        return None
    limited = any(window["limited"] for window in windows)
    selected = (
        [window for window in windows if window["limited"]] if limited else windows
    )
    resets: list[datetime] = []
    for window in selected:
        raw = window.get("resetsAt")
        if isinstance(raw, (int, float)) and not isinstance(raw, bool):
            try:
                if math.isfinite(raw):
                    resets.append(datetime.fromtimestamp(raw / 1000, tz=timezone.utc))
            except (ValueError, OverflowError, OSError):
                pass
    percents = [
        window["percent"]
        for window in windows
        if type(window.get("percent")) is int and 0 <= window["percent"] <= 100
    ]
    return QuotaObservation(
        status="exhausted" if limited else "available",
        source="experimental.usage.limits",
        asof=_now(),
        limit_scope="shared_group",
        reset_at=max(resets) if resets else None,
        precision="confirmed",
        percent=max(percents) if percents else None,
        limited=limited,
    )


def _parse_integrations(payload: object) -> list[str]:
    if isinstance(payload, dict) and "data" in payload:
        payload = payload["data"]
    if not isinstance(payload, list):
        return []
    result: list[str] = []
    for item in payload:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result.append(str(item["id"]))
    return result


def _refresh_once(
    binding: RefreshBinding,
    project: Path,
    timeout: float,
    current: AvailabilitySnapshot,
    *,
    context_signature: str | None = None,
    service_version: str | None = None,
) -> tuple[AvailabilitySnapshot, tuple[str, ...]]:
    deadline = time.monotonic() + timeout
    errors: list[str] = []
    now = _now()

    def remaining() -> float:
        value = deadline - time.monotonic()
        if value <= 0:
            raise TimeoutError("Refresh deadline exhausted")
        return value

    def query(call: Callable[[float], Any]) -> Any:
        result = call(remaining())
        remaining()  # Un resultado tardio no es una observacion actual acreditada.
        return result

    operations: set[str] = set()
    try:
        schema = query(lambda seconds: binding.openapi_schema(timeout=seconds))
        if not isinstance(schema, dict) or not isinstance(schema.get("paths"), dict):
            raise ValueError("Invalid OpenAPI")
        operations = _capabilities_from_schema(schema)
    except Exception:
        errors.append("openapi_unavailable")
    integrations: list[str] | None = None
    try:
        payload = query(lambda seconds: binding.integrations(timeout=seconds))
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise ValueError("Invalid integrations")
        integrations = _parse_integrations(payload)
    except Exception:
        errors.append("integrations_unavailable")

    new_models: dict[str, ModelEntry] = {}
    catalog_ok = False
    context_key = _project_key(project)
    try:
        from delegate import _catalog_from_payload

        payload = query(lambda seconds: binding.model_catalog(project, timeout=seconds))
        models = _catalog_from_payload(payload, project)
        for record in models:
            public = _public_model(record)
            key = str(public["model"])
            previous = current.project_models.get(context_key, current.models).get(key)
            if previous is not None and previous.context_key != context_key:
                previous = None
            new_models[key] = ModelEntry(
                metadata=_metadata_from_public(public),
                quota=previous.quota if previous is not None else None,
                context_key=context_key,
                query_attempt=previous.query_attempt if previous is not None else None,
                outcome_attempt_ids=previous.outcome_attempt_ids
                if previous is not None
                else (),
            )
        catalog_ok = True
    except Exception:
        errors.append("catalog_unavailable")

    aggregates = list(current.aggregates)
    usage_code: str | None = None
    if "GET /api/experimental/usage/limits" not in operations:
        usage_code = "usage_limits_unsupported"
    else:
        try:
            payload = query(
                lambda seconds: binding.usage_limits(project, timeout=seconds)
            )
            observation = _parse_usage_limits(payload, project)
            if observation is None:
                raise ValueError("Invalid quota")
            aggregates = [item for item in aggregates if item.provider != "opencode-go"]
            aggregates.append(
                AggregateObservation(
                    provider="opencode-go",
                    scope="service_aggregate",
                    observation=observation,
                )
            )
        except Exception:
            usage_code = "usage_limits_unavailable"
    if usage_code is not None:
        errors.append(usage_code)

    contexts = list(current.catalog_contexts)
    merged_models = dict(current.models)
    project_models = {
        project: dict(entries) for project, entries in current.project_models.items()
    }
    for model, entry in current.models.items():
        project_models.setdefault(entry.context_key, {}).setdefault(model, entry)
    retired_models = {key: dict(value) for key, value in current.retired_models.items()}
    if catalog_ok:
        previous_context = next(
            (item for item in contexts if item.project_key == context_key), None
        )
        new_context = CatalogContext(
            project_key=context_key,
            config_sources=tuple(integrations)
            if integrations is not None
            else previous_context.config_sources
            if previous_context is not None
            else (),
            config_signature=context_signature,
            service_version=service_version,
            capabilities=("config.get", "model.catalog")
            if context_signature is not None
            else ("model.catalog",),
        )
        previous_entries = current.project_models.get(context_key, {})
        context_retired = dict(retired_models.get(context_key, {}))
        for model, entry in previous_entries.items():
            if model not in new_models:
                context_retired[model] = entry
        for model in new_models:
            context_retired.pop(model, None)
        if context_retired:
            retired_models[context_key] = context_retired
        else:
            retired_models.pop(context_key, None)
        project_models[context_key] = dict(new_models)
        contexts = [item for item in contexts if item.project_key != context_key] + [
            new_context
        ]
        merged_models = {
            key: entry
            for key, entry in current.models.items()
            if entry.context_key != context_key
        }
        merged_models.update(new_models)
    sources = tuple(
        DataSourceStatus(
            name=name,
            status="unknown"
            if code == "usage_limits_unsupported"
            else "error"
            if code in errors
            else "ok",
            error_code=code if code in errors else None,
        )
        for name, code in (
            ("openapi", "openapi_unavailable"),
            ("integrations", "integrations_unavailable"),
            ("catalog", "catalog_unavailable"),
            ("usage_limits", usage_code or "usage_limits_unavailable"),
        )
    )
    snapshot = AvailabilitySnapshot(
        schema_version=current.schema_version,
        generation=current.generation + 1,
        published_at=now,
        catalog_contexts=tuple(contexts),
        models=merged_models,
        data_sources=sources,
        aggregates=tuple(aggregates),
        performance_samples=current.performance_samples,
        project_models=project_models,
        last_refresh=CatalogContext(
            context_key, (), context_signature, service_version
        ),
        public_terms=current.public_terms,
        retired_models=retired_models,
    )
    return snapshot, tuple(errors)


def _metadata_changed(left: Any, right: Any) -> bool:
    return bool(left != right)


def _inventory_changes(
    previous: AvailabilitySnapshot, current: AvailabilitySnapshot, context_key: str
) -> dict[str, tuple[str, ...]]:
    previous_entries = previous.project_models.get(context_key, {})
    current_entries = current.project_models.get(context_key, {})
    added = tuple(sorted(set(current_entries) - set(previous_entries)))
    removed = tuple(sorted(set(previous_entries) - set(current_entries)))
    changed: list[str] = []
    unchanged: list[str] = []
    for model in sorted(set(previous_entries) & set(current_entries)):
        if previous_entries[model].metadata != current_entries[model].metadata:
            changed.append(model)
        else:
            unchanged.append(model)
    return {
        "added": added,
        "removed": removed,
        "changed": tuple(changed),
        "unchanged": tuple(unchanged),
    }


def coalesced_refresh(
    state_path: Path,
    binding: RefreshBinding,
    project: Path,
    timeout: float,
    *,
    force: bool = False,
    context_signature: str | None = None,
    service_version: str | None = None,
) -> RefreshResult:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Timeout debe ser finito y positivo.")
    deadline = time.monotonic() + timeout
    _ensure_state_directory(state_path.parent)
    baseline = read_snapshot(state_path)
    baseline_generation = baseline.generation if baseline is not None else 0
    while True:
        try:
            with _lock_file(_lock_path(state_path.parent)):
                current = read_snapshot(state_path) or empty_snapshot()
                # Una generacion que aparecio mientras esperabamos ya satisface
                # este disparador, incluso si algunas fuentes fallaron.
                same_request = (
                    context_signature is None
                    or current.last_refresh is not None
                    and current.last_refresh.project_key == _project_key(project)
                    and current.last_refresh.config_signature == context_signature
                    and current.last_refresh.service_version == service_version
                )
                if current.generation > baseline_generation and same_request:
                    return RefreshResult(current, False, current.generation, ())
                if not force:
                    from availability_policy import should_refresh

                    if current.generation > 0 and not should_refresh(current, _now()):
                        return RefreshResult(current, False, current.generation, ())
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return RefreshResult(
                        current, False, current.generation, ("refresh_timeout",)
                    )
                snapshot, errors = _refresh_once(
                    binding,
                    project,
                    remaining,
                    current,
                    context_signature=context_signature,
                    service_version=service_version,
                )
                try:
                    write_snapshot(
                        state_path,
                        snapshot,
                        timeout=max(0.0, deadline - time.monotonic()),
                    )
                except StoreError as error:
                    if error.code != "lock_contended":
                        raise
                    return RefreshResult(
                        current,
                        False,
                        current.generation,
                        errors + ("publication_timeout",),
                    )
                changes = _inventory_changes(current, snapshot, _project_key(project))
                return RefreshResult(
                    snapshot, True, snapshot.generation, errors, changes
                )
        except StoreError as error:
            remaining = deadline - time.monotonic()
            if error.code != "lock_contended" or remaining <= 0:
                raise
            time.sleep(min(0.02, remaining))
