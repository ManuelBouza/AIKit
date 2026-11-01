"""Hechos públicos y condiciones de acceso para modelos OpenCode.

Separan tres cosas que no deben confundirse:

* tarifa publicada por el catálogo (``free_candidate``);
* acceso condicional documentado por una fuente oficial (franquicia, grant,
  cuota compartida, plan requerido);
* plan, cuota real y disponibilidad actual verificadas.

No consulta red ni infiere. Solo valida, serializa e ingiere artefactos tipados.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, cast
from urllib.parse import urlparse

MAX_TEXT_CHARS = 512
MAX_CONDITION_KEYS = 32
FORBIDDEN_KEYS = frozenset(
    {
        "password",
        "token",
        "credential",
        "api_key",
        "apiKey",
        "secret",
        "authorization",
        "headers",
        "env",
        "auth",
        "workspace",
        "email",
        "name",
        "path",
        "url_raw",
    }
)


# Dominios oficiales verificados por proveedor. No se infieren ni se aceptan
# dominios de reventa ni lookalikes. Los proveedores sin dominio verificado quedan
# como unknown hasta que exista evidencia primaria.
OFFICIAL_DOMAINS: dict[str, tuple[str, ...]] = {
    "cloudflare-workers-ai": ("developers.cloudflare.com",),
    "google": ("ai.google.dev",),
    "kilo": ("kilo.ai",),
    "nvidia": ("docs.api.nvidia.com",),
    "opencode": ("opencode.ai", "dev.opencode.ai"),
    "opencode-go": ("opencode.ai", "dev.opencode.ai"),
    "openrouter": ("openrouter.ai",),
    "zai": ("docs.z.ai",),
}

OFFICIAL_DOMAIN_ALIASES: dict[str, str] = {
    "cloudflare": "cloudflare-workers-ai",
}


def official_domains_for(provider: str) -> tuple[str, ...]:
    canonical = OFFICIAL_DOMAIN_ALIASES.get(provider, provider)
    return OFFICIAL_DOMAINS.get(canonical, ())


def official_source_diagnostic(provider: str) -> str:
    canonical = OFFICIAL_DOMAIN_ALIASES.get(provider, provider)
    if canonical in OFFICIAL_DOMAINS:
        return "ok"
    return "unsupported_official_source:" + canonical


def _host_of(url: str) -> str:
    from urllib.parse import urlparse

    return (urlparse(url).hostname or "").lower()


def is_official_source(provider: str, url: str) -> bool:
    host = _host_of(url)
    if not host:
        return False
    for domain in official_domains_for(provider):
        if host == domain or host.endswith("." + domain):
            return True
    return False


def validate_official_source(provider: str, url: str) -> None:
    if not url:
        raise ValueError("Fuente oficial requerida.")
    if not is_official_source(provider, url):
        diagnostic = official_source_diagnostic(provider)
        if diagnostic != "ok":
            raise ValueError(diagnostic)
        raise ValueError("Fuente no oficial para el proveedor.")


AccessKind = Literal[
    "zero_price",
    "conditional_access",
    "paid",
    "unknown",
]


SourceStatus = Literal["ok", "error", "unknown"]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _text(
    value: Any, *, max_chars: int = MAX_TEXT_CHARS, allow_empty: bool = False
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned and not allow_empty:
        return None
    if len(cleaned) > max_chars:
        return None
    return cleaned


def _timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)):
        return ()
    result: list[str] = []
    for item in value:
        text = _text(item)
        if text is not None:
            result.append(text)
    return tuple(result)


def _clean_conditions(value: Any) -> dict[str, Any]:
    """Normaliza condiciones a un dict saneado, sin secretos ni campos prohibidos."""
    if value is None:
        return {}
    if isinstance(value, str):
        if len(value) > MAX_TEXT_CHARS:
            raise ValueError("Condicion textual demasiado larga.")
        value = {"description": value}
    if not isinstance(value, dict):
        raise ValueError("Condiciones invalidas.")
    result: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ValueError("Clave de condicion invalida.")
        key_clean = key.strip()
        if not key_clean or len(key_clean) > 64:
            raise ValueError("Clave de condicion invalida.")
        if key_clean.lower() in FORBIDDEN_KEYS:
            raise ValueError("Campo secreto o privado no permitido.")
        if isinstance(item, dict):
            raise ValueError("No se permiten objetos anidados en condiciones.")
        if isinstance(item, (str, bool, int, float)) or item is None:
            if isinstance(item, str) and len(item) > MAX_TEXT_CHARS:
                raise ValueError("Valor de condicion demasiado largo.")
            result[key_clean] = item
        elif isinstance(item, (list, tuple)):
            cleaned_items = [
                x
                for x in item
                if isinstance(x, (str, bool, int, float)) and x is not None
            ]
            if not cleaned_items:
                raise ValueError("Lista de condiciones vacia o invalida.")
            result[key_clean] = cleaned_items[:16]
        else:
            raise ValueError("Tipo de condicion no permitido.")
    if len(result) > MAX_CONDITION_KEYS:
        raise ValueError("Demasiadas condiciones.")
    return result


def _official_url(value: Any) -> str | None:
    text = _text(value)
    if text is None:
        return None
    try:
        parsed = urlparse(text)
    except ValueError:
        return None
    if parsed.scheme != "https":
        return None
    if not parsed.netloc:
        return None
    # Rechaza credenciales en URL.
    if parsed.username or parsed.password:
        return None
    return text


@dataclass(frozen=True)
class PublicTerm:
    """Hecho público contrastado sobre acceso a un modelo/proveedor."""

    provider: str
    model: str
    scope: str = "model"
    access_kind: AccessKind = "unknown"
    conditions: dict[str, Any] = field(default_factory=dict)
    source_url: str = ""
    checked_at: datetime = field(default_factory=_utc_now)
    publication: datetime | None = None
    source_status: SourceStatus = "unknown"
    last_valid: datetime | None = None
    notes: tuple[str, ...] = ()

    # Alias de compatibilidad con nombres alternativos.
    limit_scope: str | None = None
    kind: str | None = None
    access: str | None = None
    access_type: str | None = None
    condition: Any = None
    url: str | None = None
    official_url: str | None = None
    source: str | None = None
    checked: datetime | None = None
    asof: datetime | None = None
    published_at: datetime | None = None
    publication_date: datetime | None = None
    published: datetime | None = None
    status: str | None = None
    provenance: str | None = None
    fetch_status: str | None = None
    last_valid_at: datetime | None = None
    last_valid_checked_at: datetime | None = None
    limitations: tuple[str, ...] = ()
    caveats: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # Normaliza alias de texto.
        provider = self.provider.strip() if isinstance(self.provider, str) else ""
        model = self.model.strip() if isinstance(self.model, str) else ""
        object.__setattr__(self, "provider", provider)
        object.__setattr__(self, "model", model)

        scope: str = self.scope if self.scope else "model"
        if self.limit_scope:
            scope = self.limit_scope
        object.__setattr__(self, "scope", scope)

        access_kind: str = self.access_kind
        for candidate in (self.kind, self.access, self.access_type):
            if isinstance(candidate, str) and candidate:
                access_kind = candidate
        if access_kind in ("franchise", "grant", "conditional"):
            access_kind = "conditional_access"
        if access_kind not in ("zero_price", "conditional_access", "paid", "unknown"):
            access_kind = "unknown"
        object.__setattr__(self, "access_kind", access_kind)

        conditions = self.conditions
        if not conditions and self.condition is not None:
            conditions = _clean_conditions(self.condition)
        else:
            conditions = _clean_conditions(conditions)
        object.__setattr__(self, "conditions", conditions)

        source_url = self.source_url
        for candidate in (self.url, self.official_url, self.source):
            if isinstance(candidate, str) and candidate and not source_url:
                source_url = candidate
        source_url = _official_url(source_url) or ""
        object.__setattr__(self, "source_url", source_url)
        validate_official_source(self.provider, source_url)

        checked_at: datetime = self.checked_at
        if isinstance(self.checked, datetime):
            checked_at = self.checked
        if isinstance(self.asof, datetime):
            checked_at = self.asof
        if not isinstance(checked_at, datetime):
            checked_at = _utc_now()
        object.__setattr__(self, "checked_at", checked_at.astimezone(timezone.utc))

        publication: datetime | None = self.publication
        for pub_candidate in (self.published_at, self.publication_date, self.published):
            if isinstance(pub_candidate, datetime):
                publication = pub_candidate
                break
        if isinstance(publication, datetime):
            publication = publication.astimezone(timezone.utc)
        object.__setattr__(self, "publication", publication)

        status: str = self.source_status
        for candidate in (self.status, self.provenance, self.fetch_status):
            if isinstance(candidate, str) and candidate:
                status = candidate
        if status not in ("ok", "error", "unknown"):
            status = "unknown"
        object.__setattr__(self, "source_status", status)

        last_valid: datetime | None = self.last_valid
        for valid_candidate in (self.last_valid_at, self.last_valid_checked_at):
            if isinstance(valid_candidate, datetime):
                last_valid = valid_candidate
                break
        if isinstance(last_valid, datetime):
            last_valid = last_valid.astimezone(timezone.utc)
        object.__setattr__(self, "last_valid", last_valid)

        notes = self.notes or self.limitations or self.caveats
        object.__setattr__(self, "notes", _string_tuple(notes))

        # Sincroniza alias de salida para lecturas alternativas.
        object.__setattr__(self, "limit_scope", self.scope)
        object.__setattr__(self, "kind", self.access_kind)
        object.__setattr__(self, "access", self.access_kind)
        object.__setattr__(self, "access_type", self.access_kind)
        object.__setattr__(self, "condition", dict(self.conditions))
        object.__setattr__(self, "url", self.source_url)
        object.__setattr__(self, "official_url", self.source_url)
        object.__setattr__(self, "source", self.source_url)
        object.__setattr__(self, "checked", self.checked_at)
        object.__setattr__(self, "asof", self.checked_at)
        object.__setattr__(self, "published_at", self.publication)
        object.__setattr__(self, "publication_date", self.publication)
        object.__setattr__(self, "published", self.publication)
        object.__setattr__(self, "status", self.source_status)
        object.__setattr__(self, "provenance", self.source_status)
        object.__setattr__(self, "fetch_status", self.source_status)
        object.__setattr__(self, "last_valid_at", self.last_valid)
        object.__setattr__(self, "last_valid_checked_at", self.last_valid)
        object.__setattr__(self, "limitations", self.notes)
        object.__setattr__(self, "caveats", self.notes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "scope": self.scope,
            "limit_scope": self.scope,
            "access_kind": self.access_kind,
            "kind": self.access_kind,
            "conditions": dict(self.conditions),
            "source_url": self.source_url,
            "url": self.source_url,
            "checked_at": self.checked_at.isoformat(),
            "publication": self.publication.isoformat() if self.publication else None,
            "source_status": self.source_status,
            "status": self.source_status,
            "last_valid": self.last_valid.isoformat() if self.last_valid else None,
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, value: Any) -> PublicTerm:
        if not isinstance(value, dict):
            raise ValueError("PublicTerm debe ser un objeto.")
        allowed_top = {
            "provider",
            "model",
            "scope",
            "limit_scope",
            "access_kind",
            "kind",
            "access",
            "access_type",
            "conditions",
            "condition",
            "source_url",
            "url",
            "official_url",
            "source",
            "checked_at",
            "checked",
            "asof",
            "publication",
            "published_at",
            "publication_date",
            "published",
            "source_status",
            "status",
            "provenance",
            "fetch_status",
            "last_valid",
            "last_valid_at",
            "last_valid_checked_at",
            "notes",
            "limitations",
            "caveats",
        }
        if not set(value).issubset(allowed_top):
            raise ValueError("Campo de nivel superior no permitido.")
        provider = _text(value.get("provider"))
        model = _text(value.get("model"))
        if provider is None or model is None:
            raise ValueError("PublicTerm requiere provider y model.")
        source_url_raw = (
            value.get("source_url")
            or value.get("url")
            or value.get("official_url")
            or value.get("source")
        )
        source_url = _official_url(source_url_raw)
        if source_url is None:
            raise ValueError("PublicTerm requiere source_url HTTPS válida.")
        scope = _text(value.get("scope") or value.get("limit_scope")) or "model"
        access_kind_raw = (
            value.get("access_kind")
            or value.get("kind")
            or value.get("access")
            or value.get("access_type")
            or "unknown"
        )
        access_kind: str = (
            access_kind_raw if isinstance(access_kind_raw, str) else "unknown"
        )
        checked_at = _timestamp(
            value.get("checked_at") or value.get("checked") or value.get("asof")
        )
        if checked_at is None:
            checked_at = _utc_now()
        publication = _timestamp(
            value.get("publication")
            or value.get("published_at")
            or value.get("publication_date")
            or value.get("published")
        )
        source_status_raw = (
            value.get("source_status")
            or value.get("status")
            or value.get("provenance")
            or value.get("fetch_status")
            or "ok"
        )
        source_status: str = (
            source_status_raw if isinstance(source_status_raw, str) else "unknown"
        )
        if source_status not in ("ok", "error", "unknown"):
            source_status = "unknown"
        last_valid = _timestamp(
            value.get("last_valid")
            or value.get("last_valid_at")
            or value.get("last_valid_checked_at")
        )
        notes = _string_tuple(
            value.get("notes") or value.get("limitations") or value.get("caveats")
        )
        conditions = _clean_conditions(
            value.get("conditions") if "conditions" in value else value.get("condition")
        )
        return cls(
            provider=provider,
            model=model,
            scope=scope,
            access_kind=cast(AccessKind, access_kind),
            conditions=conditions,
            source_url=source_url,
            checked_at=checked_at,
            publication=publication,
            source_status=cast(SourceStatus, source_status),
            last_valid=last_valid,
            notes=notes,
        )


def parse_public_terms(value: Any) -> tuple[PublicTerm, ...]:
    """Parsea una lista de hechos públicos desde JSON o lista."""
    if value is None:
        return ()
    if isinstance(value, dict):
        for alias in (
            "public_terms",
            "public_facts",
            "terms",
            "facts",
            "items",
            "data",
        ):
            if alias in value:
                value = value[alias]
                break
    if not isinstance(value, (list, tuple)):
        raise ValueError("Se esperaba una lista de hechos públicos.")
    result: list[PublicTerm] = []
    seen: set[tuple[str, str]] = set()
    for item in value:
        term = PublicTerm.from_dict(item)
        fact_key = (term.provider, term.model)
        if fact_key in seen:
            raise ValueError(f"Hecho público duplicado: {term.provider}/{term.model}.")
        seen.add(fact_key)
        result.append(term)
    return tuple(result)


def merge_public_terms(
    current: tuple[PublicTerm, ...], incoming: tuple[PublicTerm, ...]
) -> tuple[PublicTerm, ...]:
    """Upsert por (provider, model); conserva no mencionados."""
    by_key = {(t.provider, t.model): t for t in current}
    for term in incoming:
        by_key[(term.provider, term.model)] = term
    return tuple(by_key.values())


def read_public_terms_file(path: Path) -> tuple[PublicTerm, ...]:
    raw = path.read_bytes()
    if len(raw) > 4 * 1024 * 1024:
        raise ValueError("Artefacto de términos públicos demasiado grande.")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Artefacto no es UTF-8.") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Artefacto JSON inválido.") from exc
    return parse_public_terms(data)


def import_public_terms_state(
    state_path: Path, terms: tuple[PublicTerm, ...], *, replace: bool = False
) -> Any:
    """Incorpora hechos públicos al estado compartido.

    Se importa aquí para evitar dependencia circular con availability_state.
    """
    import availability_state as state

    def mutate(snapshot: Any) -> Any:
        current = tuple(getattr(snapshot, "public_terms", ()) or ())
        merged = terms if replace else merge_public_terms(current, terms)
        # Actualiza todos los alias.
        return state.AvailabilitySnapshot(
            schema_version=snapshot.schema_version,
            generation=snapshot.generation + 1,
            published_at=snapshot.published_at,
            catalog_contexts=snapshot.catalog_contexts,
            models=snapshot.models,
            data_sources=snapshot.data_sources,
            aggregates=snapshot.aggregates,
            performance_samples=snapshot.performance_samples,
            project_models=snapshot.project_models,
            last_refresh=snapshot.last_refresh,
            public_terms=merged,
            public_facts=merged,
            public_access=merged,
            public_access_terms=merged,
            conditional_access=merged,
        )

    return state.update_snapshot(state_path, mutate)


def filter_public_terms(
    terms: tuple[PublicTerm, ...],
    *,
    provider: str | None = None,
    model: str | None = None,
) -> tuple[PublicTerm, ...]:
    result = terms
    if provider is not None:
        result = tuple(t for t in result if t.provider == provider)
    if model is not None:
        result = tuple(t for t in result if t.model == model)
    return result


def count_public_terms(terms: tuple[PublicTerm, ...]) -> dict[str, int]:
    counts: dict[str, int] = {
        "total": len(terms),
        "zero_price": 0,
        "conditional_access": 0,
        "paid": 0,
        "unknown": 0,
    }
    for term in terms:
        counts[term.access_kind] = counts.get(term.access_kind, 0) + 1
    return counts
