"""Perfil puro de rendimiento observado para disponibilidad OpenCode.

Extrae, agrega, deduplica y serializa mediciones de eventos reales ya
capturados por el transporte. No consulta red, no ejecuta inferencias, no
programa ni transporta nada. Los datos ausentes quedan desconocidos.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, TypeAlias

from session_store import Role

MeasurementKind: TypeAlias = Literal[
    "ttft", "generation", "model", "task", "tool", "total"
]
Confidence: TypeAlias = Literal["low", "medium", "high", "unknown"]

MAX_TEXT_CHARS = 256
MAX_LIMITATIONS = 32
MAX_SAMPLES_DEFAULT = 100
MAX_SAMPLES_LIMIT = 10000


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def _aware_datetime(value: Any) -> datetime | None:
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return None
    return value.astimezone(timezone.utc)


def _require_aware(value: datetime, name: str = "timestamp") -> datetime:
    parsed = _aware_datetime(value)
    if parsed is None:
        raise ValueError(f"{name} debe ser datetime con zona horaria.")
    return parsed


def _non_negative_int(value: Any) -> int | None:
    if value is None:
        return None
    if _is_bool(value) or not isinstance(value, int):
        raise ValueError("El contador de tokens debe ser entero no negativo.")
    if value < 0:
        raise ValueError("El contador de tokens no puede ser negativo.")
    return value


def _non_negative_float(value: Any, name: str) -> float | None:
    if value is None:
        return None
    if _is_bool(value) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} debe ser numérico o None.")
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} debe ser finito y no negativo.")
    return result


def _text(value: Any, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str):
        raise ValueError("El texto debe ser una cadena.")
    cleaned = value.strip()
    if not cleaned or len(cleaned) > MAX_TEXT_CHARS:
        raise ValueError("El texto está vacío o excede el límite.")
    return cleaned


def _mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("Se esperaba un objeto JSON.")
    return value


def _sequence(value: Any) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Se esperaba una secuencia.")
    return value


@dataclass(frozen=True)
class PerformanceModelKey:
    """Clave comparable por proveedor, modelo y variante de esfuerzo."""

    provider: str
    model: str
    variant: str | None = None
    account_alias: str | None = None

    def __post_init__(self) -> None:
        provider = _text(self.provider)
        model = _text(self.model)
        variant = (
            _text(self.variant, optional=True) if self.variant is not None else None
        )
        alias = (
            _text(self.account_alias, optional=True)
            if self.account_alias is not None
            else None
        )
        if provider is None or model is None:
            raise ValueError("Proveedor y modelo son obligatorios.")
        object.__setattr__(self, "provider", provider)
        object.__setattr__(self, "model", model)
        object.__setattr__(self, "variant", variant)
        object.__setattr__(self, "account_alias", alias)


@dataclass(frozen=True)
class TokenStats:
    """Solo contadores públicos de tokens, nunca contenido ni razonamiento."""

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cache_read_tokens: int | None = None
    cache_write_tokens: int | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "cache_read_tokens",
            "cache_write_tokens",
        ):
            value = getattr(self, field_name)
            normalized = _non_negative_int(value)
            object.__setattr__(self, field_name, normalized)

    def has_enough_for_throughput(self) -> bool:
        return self.output_tokens is not None and self.output_tokens > 0


@dataclass(frozen=True)
class PerformanceSample:
    """Una medición individual obtenida de una tarea real ya autorizada."""

    key: PerformanceModelKey
    task_id: str
    attempt_id: str
    source: str
    measurement_kind: MeasurementKind
    observed_at: datetime
    event_id: str | None = None
    role: Role | None = None
    context_bucket: str | None = None
    ttft_seconds: float | None = None
    generation_seconds: float | None = None
    model_seconds: float | None = None
    task_seconds: float | None = None
    tool_seconds: float | None = None
    tokens: TokenStats = field(default_factory=TokenStats)
    tokens_per_second: float | None = None
    limitations: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.key, PerformanceModelKey):
            raise ValueError("La clave de rendimiento no es válida.")
        task_id = _text(self.task_id)
        attempt_id = _text(self.attempt_id)
        source = _text(self.source)
        if task_id is None or attempt_id is None or source is None:
            raise ValueError("task_id, attempt_id y source son obligatorios.")
        if self.measurement_kind not in (
            "ttft",
            "generation",
            "model",
            "task",
            "tool",
            "total",
        ):
            raise ValueError("Tipo de medición no soportado.")
        observed_at = _require_aware(self.observed_at, "observed_at")
        event_id = (
            _text(self.event_id, optional=True) if self.event_id is not None else None
        )
        role = self.role
        if role is not None and role not in ("implementer", "reviewer"):
            raise ValueError("Rol no soportado.")
        context_bucket = (
            _text(self.context_bucket, optional=True)
            if self.context_bucket is not None
            else None
        )
        ttft_seconds = _non_negative_float(self.ttft_seconds, "ttft_seconds")
        generation_seconds = _non_negative_float(
            self.generation_seconds, "generation_seconds"
        )
        model_seconds = _non_negative_float(self.model_seconds, "model_seconds")
        task_seconds = _non_negative_float(self.task_seconds, "task_seconds")
        tool_seconds = _non_negative_float(self.tool_seconds, "tool_seconds")
        tokens = self.tokens if isinstance(self.tokens, TokenStats) else TokenStats()
        tps = _non_negative_float(self.tokens_per_second, "tokens_per_second")
        limitations = tuple(
            item
            for item in (_text(x, optional=True) for x in self.limitations)
            if item is not None
        )[:MAX_LIMITATIONS]
        # Modelo, herramientas y tarea son relojes independientes; no imponer
        # una relacion de inclusion que la fuente no acredita.
        object.__setattr__(self, "task_id", task_id)
        object.__setattr__(self, "attempt_id", attempt_id)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "observed_at", observed_at)
        object.__setattr__(self, "event_id", event_id)
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "context_bucket", context_bucket)
        object.__setattr__(self, "ttft_seconds", ttft_seconds)
        object.__setattr__(self, "generation_seconds", generation_seconds)
        object.__setattr__(self, "model_seconds", model_seconds)
        object.__setattr__(self, "task_seconds", task_seconds)
        object.__setattr__(self, "tool_seconds", tool_seconds)
        object.__setattr__(self, "tokens", tokens)
        object.__setattr__(self, "tokens_per_second", tps)
        object.__setattr__(self, "limitations", limitations)


@dataclass(frozen=True)
class PerformanceWindow:
    """Historial acotado de mediciones con deduplicación real."""

    max_samples: int = MAX_SAMPLES_DEFAULT
    samples: tuple[PerformanceSample, ...] = field(default_factory=tuple)
    seen: frozenset[tuple[Any, ...]] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if _is_bool(self.max_samples) or not isinstance(self.max_samples, int):
            raise ValueError("max_samples debe ser entero.")
        if self.max_samples <= 0 or self.max_samples > MAX_SAMPLES_LIMIT:
            raise ValueError("max_samples fuera de rango.")
        samples = tuple(self.samples)
        if not all(isinstance(item, PerformanceSample) for item in samples):
            raise ValueError("Todas las muestras deben ser PerformanceSample.")
        object.__setattr__(self, "samples", samples)
        object.__setattr__(self, "seen", frozenset(self.seen))


def dedupe_key(sample: PerformanceSample) -> tuple[Any, ...]:
    """Identidad real de la medición: tarea, intento, evento y tipo."""

    return (
        sample.key,
        sample.task_id,
        sample.attempt_id,
        sample.event_id,
        sample.source,
        sample.measurement_kind,
    )


def _merge_optional_float(
    existing: float | None, incoming: float | None
) -> float | None:
    return existing if existing is not None else incoming


def _merge_token_stats(existing: TokenStats, incoming: TokenStats) -> TokenStats:
    return TokenStats(
        input_tokens=existing.input_tokens
        if existing.input_tokens is not None
        else incoming.input_tokens,
        output_tokens=existing.output_tokens
        if existing.output_tokens is not None
        else incoming.output_tokens,
        total_tokens=existing.total_tokens
        if existing.total_tokens is not None
        else incoming.total_tokens,
        cache_read_tokens=existing.cache_read_tokens
        if existing.cache_read_tokens is not None
        else incoming.cache_read_tokens,
        cache_write_tokens=existing.cache_write_tokens
        if existing.cache_write_tokens is not None
        else incoming.cache_write_tokens,
    )


def _merge_samples(
    existing: PerformanceSample, incoming: PerformanceSample
) -> PerformanceSample:
    """Completa campos ausentes de una misma identidad de evento."""

    if (
        existing.role is not None
        and incoming.role is not None
        and existing.role != incoming.role
        or existing.context_bucket is not None
        and incoming.context_bucket is not None
        and existing.context_bucket != incoming.context_bucket
    ):
        raise ValueError("Identidad de evento con contexto contradictorio.")
    limitations = tuple(sorted(set(existing.limitations) | set(incoming.limitations)))
    tokens = _merge_token_stats(existing.tokens, incoming.tokens)
    observed_at = min(existing.observed_at, incoming.observed_at)
    tps = existing.tokens_per_second
    if tps is None:
        tps = incoming.tokens_per_second
    if tps is None:
        tps = tokens_per_second(
            tokens,
            _merge_optional_float(
                existing.generation_seconds, incoming.generation_seconds
            ),
        )
    return PerformanceSample(
        key=existing.key,
        task_id=existing.task_id,
        attempt_id=existing.attempt_id,
        source=existing.source,
        measurement_kind=existing.measurement_kind,
        observed_at=observed_at,
        event_id=existing.event_id or incoming.event_id,
        role=existing.role if existing.role is not None else incoming.role,
        context_bucket=existing.context_bucket
        if existing.context_bucket is not None
        else incoming.context_bucket,
        ttft_seconds=_merge_optional_float(
            existing.ttft_seconds, incoming.ttft_seconds
        ),
        generation_seconds=_merge_optional_float(
            existing.generation_seconds, incoming.generation_seconds
        ),
        model_seconds=_merge_optional_float(
            existing.model_seconds, incoming.model_seconds
        ),
        task_seconds=_merge_optional_float(
            existing.task_seconds, incoming.task_seconds
        ),
        tool_seconds=_merge_optional_float(
            existing.tool_seconds, incoming.tool_seconds
        ),
        tokens=tokens,
        tokens_per_second=tps,
        limitations=limitations,
    )


def add_sample(
    window: PerformanceWindow, sample: PerformanceSample
) -> PerformanceWindow:
    """Agrega una muestra si no es duplicada y recorta el historial."""

    if not isinstance(window, PerformanceWindow):
        raise ValueError("La ventana no es válida.")
    if not isinstance(sample, PerformanceSample):
        raise ValueError("La muestra no es válida.")
    key = dedupe_key(sample)
    existing_index: int | None = None
    for index, current in enumerate(window.samples):
        if dedupe_key(current) == key:
            existing_index = index
            break
    if existing_index is not None:
        merged = _merge_samples(window.samples[existing_index], sample)
        new_samples = (
            window.samples[:existing_index]
            + (merged,)
            + window.samples[existing_index + 1 :]
        )
        return PerformanceWindow(
            max_samples=window.max_samples,
            samples=new_samples,
            seen=window.seen,
        )
    new_samples = window.samples + (sample,)
    new_seen = set(window.seen)
    new_seen.add(key)
    if len(new_samples) > window.max_samples:
        ordered = sorted(new_samples, key=lambda item: item.observed_at)
        kept = ordered[-window.max_samples :]
        new_samples = tuple(kept)
        new_seen = {dedupe_key(item) for item in kept}
    return PerformanceWindow(
        max_samples=window.max_samples,
        samples=new_samples,
        seen=frozenset(new_seen),
    )


def tokens_per_second(tokens: TokenStats, seconds: float | None) -> float | None:
    """Calcula TPS solo cuando hay tokens suficientes y tiempo válido."""

    if not isinstance(tokens, TokenStats):
        raise ValueError("Tokens no válidos.")
    if seconds is None or seconds <= 0:
        return None
    if not tokens.has_enough_for_throughput():
        return None
    count = tokens.output_tokens
    if count is None or count <= 0:
        return None
    result = count / seconds
    if not math.isfinite(result):
        return None
    return result


def _median(values: Sequence[float]) -> float | None:
    cleaned = [value for value in values if value is not None]
    if not cleaned:
        return None
    return float(statistics.median(cleaned))


@dataclass(frozen=True)
class PerformanceResult:
    """Agregado comparable de una clave, sin elegir ni modificar niveles."""

    key: PerformanceModelKey
    sample_count: int
    first_observed_at: datetime | None
    last_observed_at: datetime | None
    ttft_seconds: float | None = None
    generation_seconds: float | None = None
    model_seconds: float | None = None
    task_seconds: float | None = None
    tool_seconds: float | None = None
    tokens_per_second: float | None = None
    freshness_seconds: float | None = None
    confidence: Confidence = "unknown"
    limitations: tuple[str, ...] = field(default_factory=tuple)
    role: Role | None = None
    context_bucket: str | None = None
    source: str | None = None
    measurement_kind: MeasurementKind | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.key, PerformanceModelKey):
            raise ValueError("La clave de rendimiento no es válida.")
        if _is_bool(self.sample_count) or not isinstance(self.sample_count, int):
            raise ValueError("sample_count debe ser entero.")
        if self.sample_count < 0:
            raise ValueError("sample_count no puede ser negativo.")
        first = (
            _aware_datetime(self.first_observed_at)
            if self.first_observed_at is not None
            else None
        )
        last = (
            _aware_datetime(self.last_observed_at)
            if self.last_observed_at is not None
            else None
        )
        if self.first_observed_at is not None and first is None:
            raise ValueError("first_observed_at debe tener zona horaria.")
        if self.last_observed_at is not None and last is None:
            raise ValueError("last_observed_at debe tener zona horaria.")
        for name in (
            "ttft_seconds",
            "generation_seconds",
            "model_seconds",
            "task_seconds",
            "tool_seconds",
            "tokens_per_second",
            "freshness_seconds",
        ):
            value = getattr(self, name)
            normalized = _non_negative_float(value, name) if value is not None else None
            object.__setattr__(self, name, normalized)
        if self.confidence not in ("low", "medium", "high", "unknown"):
            raise ValueError("Confianza no soportada.")
        limitations = tuple(
            item
            for item in (_text(x, optional=True) for x in self.limitations)
            if item is not None
        )[:MAX_LIMITATIONS]
        role = self.role
        if role is not None and role not in ("implementer", "reviewer"):
            raise ValueError("Rol no soportado.")
        context_bucket = (
            _text(self.context_bucket, optional=True)
            if self.context_bucket is not None
            else None
        )
        source = _text(self.source, optional=True) if self.source is not None else None
        measurement_kind = self.measurement_kind
        if measurement_kind is not None and measurement_kind not in (
            "ttft",
            "generation",
            "model",
            "task",
            "tool",
            "total",
        ):
            raise ValueError("Tipo de medición no soportado.")
        object.__setattr__(self, "first_observed_at", first)
        object.__setattr__(self, "last_observed_at", last)
        object.__setattr__(self, "limitations", limitations)
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "context_bucket", context_bucket)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "measurement_kind", measurement_kind)


def aggregate_samples(samples: Iterable[PerformanceSample]) -> PerformanceResult:
    """Agrega muestras de una misma clave en estadísticas comparables."""

    unique: dict[tuple[Any, ...], PerformanceSample] = {}
    for sample in samples:
        if not isinstance(sample, PerformanceSample):
            raise ValueError("Todas las entradas deben ser PerformanceSample.")
        identity = dedupe_key(sample)
        unique[identity] = (
            _merge_samples(unique[identity], sample) if identity in unique else sample
        )
    items = tuple(unique.values())
    if not items:
        raise ValueError("No hay muestras para agregar.")
    if not all(isinstance(item, PerformanceSample) for item in items):
        raise ValueError("Todas las entradas deben ser PerformanceSample.")
    key = items[0].key
    if any(item.key != key for item in items):
        raise ValueError("No se mezclan claves de rendimiento distintas.")
    role = items[0].role
    if any(item.role != role for item in items):
        raise ValueError("No se mezclan roles no comparables.")
    context_bucket = items[0].context_bucket
    if any(item.context_bucket != context_bucket for item in items):
        raise ValueError("No se mezclan contextos no comparables.")
    source = items[0].source
    if any(item.source != source for item in items):
        raise ValueError("No se mezclan fuentes no comparables.")
    measurement_kind = items[0].measurement_kind
    if any(item.measurement_kind != measurement_kind for item in items):
        raise ValueError("No se mezclan tipos de medición no comparables.")
    limitations: set[str] = set()
    for item in items:
        limitations.update(item.limitations)
    ttft_values = [item.ttft_seconds for item in items if item.ttft_seconds is not None]
    generation_values = [
        item.generation_seconds for item in items if item.generation_seconds is not None
    ]
    model_values = [
        item.model_seconds for item in items if item.model_seconds is not None
    ]
    task_values = [item.task_seconds for item in items if item.task_seconds is not None]
    tool_values = [item.tool_seconds for item in items if item.tool_seconds is not None]
    tps_values = [
        item.tokens_per_second for item in items if item.tokens_per_second is not None
    ]
    # Si falta TPS individual pero hay datos suficientes, se calcula por muestra.
    computed_tps: list[float] = []
    for item in items:
        if item.tokens_per_second is None:
            value = tokens_per_second(item.tokens, item.generation_seconds)
            if value is not None:
                computed_tps.append(value)
    if computed_tps:
        tps_values = tps_values + computed_tps
    count = len(items)
    if count >= 10:
        confidence: Confidence = "high"
    elif count >= 3:
        confidence = "medium"
    else:
        confidence = "low"
    return PerformanceResult(
        key=key,
        sample_count=count,
        first_observed_at=min(item.observed_at for item in items),
        last_observed_at=max(item.observed_at for item in items),
        ttft_seconds=_median(ttft_values),
        generation_seconds=_median(generation_values),
        model_seconds=_median(model_values),
        task_seconds=_median(task_values),
        tool_seconds=_median(tool_values),
        tokens_per_second=_median(tps_values),
        confidence=confidence,
        limitations=tuple(sorted(limitations)),
        role=role,
        context_bucket=context_bucket,
        source=source,
        measurement_kind=measurement_kind,
    )


def aggregate_comparable(
    samples: Iterable[PerformanceSample],
) -> tuple[PerformanceResult, ...]:
    """Particion explicita: mismo modelo/esfuerzo/cuenta, fuente/tipo, rol/contexto."""
    unique: dict[tuple[Any, ...], PerformanceSample] = {}
    for sample in samples:
        if not isinstance(sample, PerformanceSample):
            raise ValueError("Todas las entradas deben ser PerformanceSample.")
        identity = dedupe_key(sample)
        unique[identity] = (
            _merge_samples(unique[identity], sample) if identity in unique else sample
        )
    groups: dict[tuple[Any, ...], list[PerformanceSample]] = {}
    for sample in unique.values():
        comparison = (
            sample.key,
            sample.source,
            sample.measurement_kind,
            sample.role,
            sample.context_bucket,
        )
        groups.setdefault(comparison, []).append(sample)
    return tuple(aggregate_samples(items) for items in groups.values())


def aggregate_window(window: PerformanceWindow) -> PerformanceResult:
    return aggregate_samples(window.samples)


def freshness_seconds(
    result: PerformanceResult, now: datetime | None = None
) -> float | None:
    """Segundos desde la última observación; now debe ser consciente."""

    if result.last_observed_at is None:
        return None
    current = _utc_now() if now is None else _require_aware(now, "now")
    delta = (current - result.last_observed_at).total_seconds()
    if delta < 0:
        return 0.0
    return delta


def performance_sort_key(result: PerformanceResult) -> tuple[Any, ...]:
    """Clave de comparación honesta: menor TTFT/latencia primero, mayor TPS primero.

    No elige modelo ni nivel; solo ordena estadísticas comparables.
    """

    ttft = result.ttft_seconds if result.ttft_seconds is not None else float("inf")
    model = result.model_seconds if result.model_seconds is not None else float("inf")
    task = result.task_seconds if result.task_seconds is not None else float("inf")
    tps = (
        result.tokens_per_second
        if result.tokens_per_second is not None
        else float("-inf")
    )
    # Mayor TPS primero => negar para orden ascendente.
    return (ttft, model, task, -tps, result.sample_count * -1)


def _parse_timestamp_value(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return _aware_datetime(value)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        return _aware_datetime(parsed)
    if isinstance(value, (int, float)) and not _is_bool(value):
        number = float(value)
        if not math.isfinite(number):
            return None
        if number > 1e12:
            number /= 1000.0
        try:
            return datetime.fromtimestamp(number, tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            return None
    return None


def _event_mapping(event: Any) -> Mapping[str, Any] | None:
    if not isinstance(event, Mapping):
        return None
    return event


def _nested_part(event: Mapping[str, Any]) -> Mapping[str, Any]:
    part = event.get("part")
    if isinstance(part, Mapping):
        return part
    return {}


def _optional_text_from_event(event: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = event.get(key)
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                return cleaned
        part = _nested_part(event)
        value = part.get(key)
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                return cleaned
    return None


def _optional_float_from_event(event: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        for source in (event, _nested_part(event)):
            value = source.get(key)
            if value is None:
                continue
            try:
                return _non_negative_float(value, key)
            except ValueError:
                continue
    return None


def _token_stats_from_event(event: Mapping[str, Any]) -> TokenStats:
    tokens: Mapping[str, Any] | None = None
    for key in ("tokens", "token_counts", "usage"):
        for source in (event, _nested_part(event)):
            value = source.get(key)
            if isinstance(value, Mapping):
                tokens = value
                break
        if tokens is not None:
            break
    if tokens is None:
        # Contadores planos opcionales.
        input_tokens = _optional_int_from_event(event, "input_tokens", "prompt_tokens")
        output_tokens = _optional_int_from_event(
            event, "output_tokens", "completion_tokens", "response_tokens"
        )
        total_tokens = _optional_int_from_event(event, "total_tokens")
        cache_read = _optional_int_from_event(event, "cache_read_tokens")
        cache_write = _optional_int_from_event(event, "cache_write_tokens")
        return TokenStats(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cache_read_tokens=cache_read,
            cache_write_tokens=cache_write,
        )
    input_tokens = _optional_int_from_mapping(
        tokens, "input", "input_tokens", "prompt_tokens"
    )
    output_tokens = _optional_int_from_mapping(
        tokens, "output", "output_tokens", "completion_tokens", "response_tokens"
    )
    total_tokens = _optional_int_from_mapping(tokens, "total", "total_tokens")
    cache_read = _optional_int_from_mapping(tokens, "cache_read", "cache_read_tokens")
    cache_write = _optional_int_from_mapping(
        tokens, "cache_write", "cache_write_tokens"
    )
    return TokenStats(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cache_read_tokens=cache_read,
        cache_write_tokens=cache_write,
    )


def _optional_int_from_event(event: Mapping[str, Any], *keys: str) -> int | None:
    for key in keys:
        for source in (event, _nested_part(event)):
            value = source.get(key)
            if value is None:
                continue
            try:
                return _non_negative_int(value)
            except ValueError:
                continue
    return None


def _optional_int_from_mapping(mapping: Mapping[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = mapping.get(key)
        if value is None:
            continue
        try:
            return _non_negative_int(value)
        except ValueError:
            continue
    return None


def _derive_task_seconds_from_time(event: Mapping[str, Any]) -> float | None:
    for source in (event, _nested_part(event)):
        time_value = source.get("time")
        if not isinstance(time_value, Mapping):
            continue
        created = _parse_timestamp_value(time_value.get("created"))
        updated = _parse_timestamp_value(time_value.get("updated"))
        if created is not None and updated is not None:
            delta = (updated - created).total_seconds()
            if delta >= 0:
                return delta
    return None


def extract_performance_sample(
    event: Any,
    *,
    task_id: str,
    attempt_id: str,
    key: PerformanceModelKey,
    source: str = "cli_json_v2",
    observed_at: datetime | None = None,
    role: Role | None = None,
    context_bucket: str | None = None,
    event_id: str | None = None,
    measurement_kind: MeasurementKind = "model",
) -> PerformanceSample | None:
    """Extrae una muestra solo de campos con semántica explícita.

    Nunca usa sessionID ni el inicio inmediato del cliente como primera
    respuesta del modelo. Los campos ausentes quedan desconocidos.
    """

    mapping = _event_mapping(event)
    if mapping is None:
        return None
    if event_id is None:
        event_id = _optional_text_from_event(mapping, "id", "event_id")
    if observed_at is None:
        observed = _optional_text_from_event(mapping, "observed_at", "timestamp")
        if observed is not None:
            try:
                parsed = datetime.fromisoformat(observed)
                observed_at = _aware_datetime(parsed)
            except ValueError:
                observed_at = None
    if observed_at is None:
        observed_at = _utc_now()
    else:
        observed_at = _require_aware(observed_at, "observed_at")

    ttft_seconds = _optional_float_from_event(
        mapping, "ttft_seconds", "time_to_first_token", "first_token_seconds"
    )
    generation_seconds = _optional_float_from_event(
        mapping, "generation_seconds", "generation_time", "generation_duration"
    )
    model_seconds = _optional_float_from_event(
        mapping, "model_seconds", "model_time", "model_duration"
    )
    tool_seconds = _optional_float_from_event(
        mapping, "tool_seconds", "tool_time", "tool_duration"
    )
    task_seconds = _optional_float_from_event(
        mapping,
        "task_seconds",
        "total_seconds",
        "wall_time",
        "duration_seconds",
        "elapsed_seconds",
    )
    if task_seconds is None:
        task_seconds = _derive_task_seconds_from_time(mapping)

    # El backend puede exponer solo walltime de tarea: se etiqueta como task.
    if (
        measurement_kind == "model"
        and ttft_seconds is None
        and generation_seconds is None
        and model_seconds is None
        and task_seconds is not None
    ):
        measurement_kind = "task"

    tokens = _token_stats_from_event(mapping)
    tps = tokens_per_second(tokens, generation_seconds)

    # Sin ninguna medida ni contador público, no hay muestra útil.
    if all(
        value is None
        for value in (
            ttft_seconds,
            generation_seconds,
            model_seconds,
            task_seconds,
            tool_seconds,
        )
    ) and not any(
        value is not None
        for value in (
            tokens.input_tokens,
            tokens.output_tokens,
            tokens.total_tokens,
        )
    ):
        return None

    limitations: list[str] = []
    if ttft_seconds is None:
        limitations.append("ttft_unavailable")
    if generation_seconds is None:
        limitations.append("generation_unavailable")
    if task_seconds is None:
        limitations.append("task_time_unavailable")
    if tokens.total_tokens is None and tokens.output_tokens is None:
        limitations.append("token_count_unavailable")

    return PerformanceSample(
        key=key,
        task_id=task_id,
        attempt_id=attempt_id,
        source=source,
        measurement_kind=measurement_kind,
        observed_at=observed_at,
        event_id=event_id,
        role=role,
        context_bucket=context_bucket,
        ttft_seconds=ttft_seconds,
        generation_seconds=generation_seconds,
        model_seconds=model_seconds,
        task_seconds=task_seconds,
        tool_seconds=tool_seconds,
        tokens=tokens,
        tokens_per_second=tps,
        limitations=tuple(limitations),
    )


def extract_samples_from_events(
    events: Iterable[Any],
    *,
    task_id: str,
    attempt_id: str,
    key: PerformanceModelKey,
    source: str = "cli_json_v2",
    observed_at: datetime | None = None,
    role: Role | None = None,
    context_bucket: str | None = None,
    measurement_kind: MeasurementKind = "model",
) -> tuple[PerformanceSample, ...]:
    result: list[PerformanceSample] = []
    for event in events:
        sample = extract_performance_sample(
            event,
            task_id=task_id,
            attempt_id=attempt_id,
            key=key,
            source=source,
            observed_at=observed_at,
            role=role,
            context_bucket=context_bucket,
            measurement_kind=measurement_kind,
        )
        if sample is not None:
            result.append(sample)
    return tuple(result)


def _sample_to_dict(sample: PerformanceSample) -> dict[str, Any]:
    return {
        "key": {
            "provider": sample.key.provider,
            "model": sample.key.model,
            "variant": sample.key.variant,
            "account_alias": sample.key.account_alias,
        },
        "task_id": sample.task_id,
        "attempt_id": sample.attempt_id,
        "event_id": sample.event_id,
        "source": sample.source,
        "measurement_kind": sample.measurement_kind,
        "observed_at": sample.observed_at.isoformat(),
        "role": sample.role,
        "context_bucket": sample.context_bucket,
        "ttft_seconds": sample.ttft_seconds,
        "generation_seconds": sample.generation_seconds,
        "model_seconds": sample.model_seconds,
        "task_seconds": sample.task_seconds,
        "tool_seconds": sample.tool_seconds,
        "tokens": {
            "input_tokens": sample.tokens.input_tokens,
            "output_tokens": sample.tokens.output_tokens,
            "total_tokens": sample.tokens.total_tokens,
            "cache_read_tokens": sample.tokens.cache_read_tokens,
            "cache_write_tokens": sample.tokens.cache_write_tokens,
        },
        "tokens_per_second": sample.tokens_per_second,
        "limitations": list(sample.limitations),
    }


def _sample_from_dict(data: Mapping[str, Any]) -> PerformanceSample:
    allowed = {
        "key",
        "task_id",
        "attempt_id",
        "event_id",
        "source",
        "measurement_kind",
        "observed_at",
        "role",
        "context_bucket",
        "ttft_seconds",
        "generation_seconds",
        "model_seconds",
        "task_seconds",
        "tool_seconds",
        "tokens",
        "tokens_per_second",
        "limitations",
    }
    required = {
        "key",
        "task_id",
        "attempt_id",
        "source",
        "measurement_kind",
        "observed_at",
    }
    if set(data) - allowed or not required.issubset(data):
        raise ValueError("Campos de muestra no permitidos.")

    def text(value: object) -> str:
        parsed = _text(value)
        if parsed is None:
            raise ValueError("Identidad ausente.")
        return parsed

    key_data = _mapping(data["key"])
    if set(key_data) - {"provider", "model", "variant", "account_alias"}:
        raise ValueError("Clave no permitida.")
    key = PerformanceModelKey(
        provider=text(key_data.get("provider")),
        model=text(key_data.get("model")),
        variant=key_data.get("variant"),
        account_alias=key_data.get("account_alias"),
    )
    observed_at = _require_aware(datetime.fromisoformat(text(data["observed_at"])))
    raw = data.get("tokens", {})
    tokens_raw = _mapping(raw)
    if set(tokens_raw) - {
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
    }:
        raise ValueError("Contadores no permitidos.")
    tokens = TokenStats(
        input_tokens=tokens_raw.get("input_tokens"),
        output_tokens=tokens_raw.get("output_tokens"),
        total_tokens=tokens_raw.get("total_tokens"),
        cache_read_tokens=tokens_raw.get("cache_read_tokens"),
        cache_write_tokens=tokens_raw.get("cache_write_tokens"),
    )
    limitations_raw = data.get("limitations", [])
    if not isinstance(limitations_raw, list) or len(limitations_raw) > MAX_LIMITATIONS:
        raise ValueError("Limitaciones fuera de contrato.")
    kind = data["measurement_kind"]
    if kind == "model":
        measurement: MeasurementKind = "model"
    elif kind == "task":
        measurement = "task"
    elif kind == "ttft":
        measurement = "ttft"
    elif kind == "generation":
        measurement = "generation"
    elif kind == "tool":
        measurement = "tool"
    elif kind == "total":
        measurement = "total"
    else:
        raise ValueError("Tipo de muestra no permitido.")
    return PerformanceSample(
        key=key,
        task_id=text(data["task_id"]),
        attempt_id=text(data["attempt_id"]),
        source=text(data["source"]),
        measurement_kind=measurement,
        observed_at=observed_at,
        event_id=data.get("event_id"),
        role=data.get("role"),
        context_bucket=data.get("context_bucket"),
        ttft_seconds=data.get("ttft_seconds"),
        generation_seconds=data.get("generation_seconds"),
        model_seconds=data.get("model_seconds"),
        task_seconds=data.get("task_seconds"),
        tool_seconds=data.get("tool_seconds"),
        tokens=tokens,
        tokens_per_second=data.get("tokens_per_second"),
        limitations=tuple(text(item) for item in limitations_raw),
    )


def _window_to_dict(window: PerformanceWindow) -> dict[str, Any]:
    return {
        "max_samples": window.max_samples,
        "samples": [_sample_to_dict(item) for item in window.samples],
    }


def _window_from_dict(data: Mapping[str, Any]) -> PerformanceWindow:
    mapping = _mapping(data)
    max_samples = mapping.get("max_samples", MAX_SAMPLES_DEFAULT)
    if _is_bool(max_samples) or not isinstance(max_samples, int):
        raise ValueError("max_samples inválido.")
    samples_raw = mapping.get("samples", [])
    if not isinstance(samples_raw, Sequence) or isinstance(samples_raw, (str, bytes)):
        raise ValueError("samples debe ser una lista.")
    samples = tuple(
        _sample_from_dict(item) for item in samples_raw if isinstance(item, Mapping)
    )
    window = PerformanceWindow(max_samples=max_samples, samples=())
    for sample in samples:
        window = add_sample(window, sample)
    return window


def _result_to_dict(result: PerformanceResult) -> dict[str, Any]:
    return {
        "key": {
            "provider": result.key.provider,
            "model": result.key.model,
            "variant": result.key.variant,
            "account_alias": result.key.account_alias,
        },
        "sample_count": result.sample_count,
        "first_observed_at": result.first_observed_at.isoformat()
        if result.first_observed_at is not None
        else None,
        "last_observed_at": result.last_observed_at.isoformat()
        if result.last_observed_at is not None
        else None,
        "ttft_seconds": result.ttft_seconds,
        "generation_seconds": result.generation_seconds,
        "model_seconds": result.model_seconds,
        "task_seconds": result.task_seconds,
        "tool_seconds": result.tool_seconds,
        "tokens_per_second": result.tokens_per_second,
        "freshness_seconds": result.freshness_seconds,
        "confidence": result.confidence,
        "limitations": list(result.limitations),
        "role": result.role,
        "context_bucket": result.context_bucket,
        "source": result.source,
        "measurement_kind": result.measurement_kind,
    }


def sample_to_dict(sample: PerformanceSample) -> dict[str, Any]:
    return _sample_to_dict(sample)


def sample_from_dict(data: Mapping[str, Any]) -> PerformanceSample:
    return _sample_from_dict(data)


def window_to_dict(window: PerformanceWindow) -> dict[str, Any]:
    return _window_to_dict(window)


def window_from_dict(data: Mapping[str, Any]) -> PerformanceWindow:
    return _window_from_dict(data)


def result_to_dict(result: PerformanceResult) -> dict[str, Any]:
    return _result_to_dict(result)


# Alias públicos para facilitar integración futura.
PerformanceKey = PerformanceModelKey
ModelPerformanceKey = PerformanceModelKey
PerformanceMeasurement = PerformanceSample
PerformanceObservation = PerformanceSample
PerformanceAggregate = PerformanceResult
PerformanceSummary = PerformanceResult
PerformanceStats = PerformanceResult
PerformanceHistory = PerformanceWindow
PerformanceHistoryWindow = PerformanceWindow
BoundedHistory = PerformanceWindow

extract_performance = extract_performance_sample
extract_sample = extract_performance_sample
extract_samples = extract_samples_from_events
samples_from_events = extract_samples_from_events
record_sample = add_sample
aggregate = aggregate_samples
summarize = aggregate_samples
summarize_window = aggregate_window


__all__ = [
    "PerformanceModelKey",
    "PerformanceKey",
    "ModelPerformanceKey",
    "TokenStats",
    "PerformanceSample",
    "PerformanceMeasurement",
    "PerformanceObservation",
    "PerformanceWindow",
    "PerformanceHistory",
    "PerformanceHistoryWindow",
    "BoundedHistory",
    "PerformanceResult",
    "PerformanceAggregate",
    "PerformanceSummary",
    "PerformanceStats",
    "MeasurementKind",
    "Confidence",
    "Role",
    "dedupe_key",
    "add_sample",
    "record_sample",
    "tokens_per_second",
    "aggregate_samples",
    "aggregate_comparable",
    "aggregate",
    "summarize",
    "aggregate_window",
    "summarize_window",
    "freshness_seconds",
    "performance_sort_key",
    "extract_performance_sample",
    "extract_performance",
    "extract_sample",
    "extract_samples_from_events",
    "extract_samples",
    "samples_from_events",
    "sample_to_dict",
    "sample_from_dict",
    "window_to_dict",
    "window_from_dict",
    "result_to_dict",
]
