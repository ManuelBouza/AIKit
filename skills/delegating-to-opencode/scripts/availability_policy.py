"""Política pura de disponibilidad: elegibilidad, orden y resultado."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal

from availability_state import (
    AvailabilitySnapshot,
    ModelEntry,
    QueryAttempt,
    QuotaObservation,
)

ERROR_COOLDOWN_SECONDS = 300
DAILY_REFRESH_HOUR = 9


def _madrid_offset(now: datetime) -> timedelta:
    """Regla UE: transiciones el ultimo domingo a 01:00 UTC, no a medianoche."""
    utc = now.astimezone(timezone.utc)

    def boundary(month: int) -> datetime:
        last = max(
            day
            for day in range(25, 32)
            if datetime(utc.year, month, day).weekday() == 6
        )
        return datetime(utc.year, month, last, 1, tzinfo=timezone.utc)

    return timedelta(hours=2 if boundary(3) <= utc < boundary(10) else 1)


def _to_madrid(value: datetime) -> datetime:
    utc = value.astimezone(timezone.utc)
    return utc + _madrid_offset(utc)


ResultCode = Literal[
    "success",
    "quota_exhausted",
    "rate_limited",
    "auth_error",
    "service_error",
    "unaffordable_output",
    "unknown",
]


def should_refresh(
    snapshot: AvailabilitySnapshot,
    now: datetime,
    *,
    error_cooldown_seconds: float | None = None,
) -> bool:
    """Disparadores puros; error no crea sondeo/TTL implicito antes de ejecutar.

    Cooldown es opt-in explicito. No se acuerda automaticamente el valor 300.
    """
    if snapshot.generation <= 0:
        return True
    published = _to_madrid(snapshot.published_at)
    current = _to_madrid(now)
    scheduled = current.replace(hour=9, minute=0, second=0, microsecond=0)
    if current < scheduled:
        scheduled -= timedelta(days=1)
    if published < scheduled:
        return True
    if error_cooldown_seconds is not None:
        import math

        if not math.isfinite(error_cooldown_seconds) or error_cooldown_seconds < 0:
            raise ValueError("Cooldown invalido.")
        if any(source.status == "error" for source in snapshot.data_sources):
            return (
                now - snapshot.published_at
            ).total_seconds() >= error_cooldown_seconds
    for entry in snapshot.models.values():
        quota = entry.quota
        if (
            quota is not None
            and quota.status == "exhausted"
            and quota.reset_at is not None
            and quota.reset_at <= now
        ):
            return True
    return False


def sort_candidates(entries: list[ModelEntry]) -> list[str]:
    def key(entry: ModelEntry) -> tuple[int, str]:
        paid = entry.metadata.free_candidate is False
        go = entry.metadata.model.startswith("opencode-go/")
        if paid and go:
            return (0, entry.metadata.model)
        if paid:
            return (1, entry.metadata.model)
        if entry.metadata.free_candidate is True:
            return (2, entry.metadata.model)
        return (3, entry.metadata.model)

    return [entry.metadata.model for entry in sorted(entries, key=key)]


def eligible_for_attempt(entry: ModelEntry, attempt_id: str | None = None) -> bool:
    if attempt_id is not None and (
        attempt_id in entry.outcome_attempt_ids
        or entry.query_attempt is not None
        and entry.query_attempt.attempt_id == attempt_id
    ):
        return False
    if entry.quota is None or entry.quota.status == "unknown":
        return True

    if entry.quota.status == "exhausted" and entry.quota.reset_at is not None:
        return False  # Reset pasado exige observacion nueva; no habilita por reloj.
    return entry.quota.status != "exhausted"


def record_outcome(
    entry: ModelEntry,
    result_code: ResultCode,
    observed_at: datetime,
    *,
    reset_at: datetime | None = None,
    attempt_id: str | None = None,
) -> ModelEntry:
    if attempt_id is not None and (
        attempt_id in entry.outcome_attempt_ids
        or entry.query_attempt is not None
        and entry.query_attempt.attempt_id == attempt_id
    ):
        return entry

    if result_code == "success":
        observation = QuotaObservation(
            status="available",
            source="inference_result",
            asof=observed_at,
            limit_scope=entry.quota.limit_scope
            if entry.quota is not None
            else "unknown",
            reset_at=None,
            precision="confirmed",
            percent=0,
            limited=False,
        )
        pass
    elif result_code in ("quota_exhausted", "rate_limited"):
        observation = QuotaObservation(
            status="exhausted",
            source="inference_result",
            asof=observed_at,
            limit_scope=entry.quota.limit_scope
            if entry.quota is not None
            else "unknown",
            reset_at=reset_at,
            precision="confirmed",
            percent=100 if result_code == "quota_exhausted" else None,
            limited=True,
        )
    elif result_code in ("auth_error", "service_error", "unaffordable_output"):
        observation = None
        pass
    else:
        observation = None

    new_quota = observation if observation is not None else entry.quota
    attempt = QueryAttempt(
        at=observed_at,
        result=result_code,
        error_code=result_code if result_code != "success" else None,
        attempt_id=attempt_id,
    )
    return ModelEntry(
        metadata=entry.metadata,
        quota=new_quota,
        context_key=entry.context_key,
        query_attempt=attempt,
        outcome_attempt_ids=entry.outcome_attempt_ids
        + ((attempt_id,) if attempt_id is not None else ()),
    )
