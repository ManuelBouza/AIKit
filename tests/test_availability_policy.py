"""Pruebas de política pura de disponibilidad."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import availability_policy as ap
import availability_state as a
import pytest


def _entry(
    quota_status: str | None = None, reset_at: datetime | None = None
) -> a.ModelEntry:
    metadata = a.ModelMetadata(
        model="opencode-go/beam-free",
        name="Beam Free",
        pricing=(a.PricingTier(input=0.0, output=0.0),),
        variants=("high",),
        tools=True,
        input_modalities=("text",),
        output_modalities=("text",),
        context_limit=100000,
        output_limit=8000,
        free_candidate=False,
        may_use_openai_quota=False,
    )
    quota = None
    if quota_status is not None:
        quota = a.QuotaObservation(
            status=quota_status,  # type: ignore[arg-type]
            source="test",
            asof=datetime.now(timezone.utc),
            limit_scope="model",
            reset_at=reset_at,
            precision="confirmed",
            percent=100 if quota_status == "exhausted" else 0,
            limited=quota_status == "exhausted",
        )
    return a.ModelEntry(metadata=metadata, quota=quota, context_key="ctx")


def test_sort_candidates_prioritizes_paid_before_free() -> None:
    paid = _entry()
    free_meta = a.ModelMetadata(
        model="opencode/free-model",
        name="Free",
        pricing=(a.PricingTier(input=0.0, output=0.0),),
        variants=(),
        tools=True,
        input_modalities=("text",),
        output_modalities=("text",),
        context_limit=100000,
        output_limit=8000,
        free_candidate=True,
        may_use_openai_quota=False,
    )
    free = a.ModelEntry(metadata=free_meta, quota=None, context_key="ctx")
    assert ap.sort_candidates([free, paid]) == [
        "opencode-go/beam-free",
        "opencode/free-model",
    ]


def test_reset_past_requires_refresh() -> None:
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=1)
    snapshot = a.AvailabilitySnapshot(
        schema_version=a.STATE_SCHEMA_VERSION,
        generation=1,
        published_at=now,
        catalog_contexts=(),
        models={"m": _entry("exhausted", past)},
        data_sources=(),
    )
    assert ap.should_refresh(snapshot, now) is True


def test_outcome_preserves_quota_on_service_error() -> None:
    entry = _entry("available")
    updated = ap.record_outcome(entry, "service_error", datetime.now(timezone.utc))
    assert updated.quota is not None
    assert updated.quota.status == "available"
    assert updated.query_attempt is not None
    assert updated.query_attempt.result == "service_error"


def test_unknown_status_permits_one_attempt() -> None:
    entry = _entry("unknown")
    assert ap.eligible_for_attempt(entry) is True


def test_unaffordable_output_does_not_imply_zero_balance() -> None:
    entry = _entry("available")
    updated = ap.record_outcome(
        entry, "unaffordable_output", datetime.now(timezone.utc)
    )
    assert updated.quota is not None
    assert updated.quota.status == "available"


def test_past_reset_does_not_authorize_attempt_before_verification() -> None:
    assert not ap.eligible_for_attempt(
        _entry("exhausted", datetime.now(timezone.utc) - timedelta(days=1))
    )


def test_outcome_idempotence_uses_attempt_identity_and_survives_other_attempts(
    tmp_path: Path,
) -> None:
    from pathlib import Path

    entry = _entry()
    now = datetime.now(timezone.utc)
    one = ap.record_outcome(entry, "success", now, attempt_id="first")
    two = ap.record_outcome(
        one, "success", now + timedelta(seconds=1), attempt_id="second"
    )
    assert two.query_attempt is not None
    assert two.query_attempt.attempt_id == "second"
    assert two.query_attempt.at == now + timedelta(seconds=1)
    state = replace(a.empty_snapshot(now), models={"m": two})
    path = Path(tmp_path) / "state" / "availability-state.json"
    a.write_snapshot(path, state)
    saved = a.read_snapshot(path)
    assert saved is not None
    loaded = saved.models["m"]
    duplicate = ap.record_outcome(
        loaded, "quota_exhausted", now + timedelta(seconds=2), attempt_id="first"
    )
    assert duplicate == loaded


@pytest.mark.parametrize(
    ("instant", "offset"),
    [
        ("2026-03-29T00:59:59+00:00", 1),
        ("2026-03-29T01:00:00+00:00", 2),
        ("2026-10-25T00:59:59+00:00", 2),
        ("2026-10-25T01:00:00+00:00", 1),
    ],
)
def test_madrid_dst_changes_at_utc_one(instant: str, offset: int) -> None:
    assert ap._madrid_offset(datetime.fromisoformat(instant)) == timedelta(hours=offset)


def test_daily_refresh_is_due_at_nine_madrid_not_midnight() -> None:
    before = datetime.fromisoformat("2026-10-30T09:00:00+00:00")
    state = replace(a.empty_snapshot(before), generation=1)
    assert not ap.should_refresh(
        state, datetime.fromisoformat("2026-10-31T07:59:59+00:00")
    )
    assert ap.should_refresh(state, datetime.fromisoformat("2026-10-31T08:00:00+00:00"))


def test_error_cooldown_is_explicit_and_never_becomes_a_preexecution_ttl() -> None:
    now = datetime.fromisoformat("2026-10-31T12:00:00+00:00")
    snapshot = replace(
        a.empty_snapshot(now),
        generation=1,
        data_sources=(a.DataSourceStatus("catalog", "error", "unavailable"),),
    )
    assert not ap.should_refresh(snapshot, now + timedelta(seconds=299))
    assert not ap.should_refresh(
        snapshot,
        now + timedelta(seconds=299),
        error_cooldown_seconds=ap.ERROR_COOLDOWN_SECONDS,
    )
    assert ap.should_refresh(
        snapshot,
        now + timedelta(seconds=300),
        error_cooldown_seconds=ap.ERROR_COOLDOWN_SECONDS,
    )


def test_unknown_single_attempt_is_scoped_by_real_attempt_id() -> None:
    now = datetime.now(timezone.utc)
    entry = ap.record_outcome(
        _entry("unknown"), "service_error", now, attempt_id="first"
    )
    assert not ap.eligible_for_attempt(entry, "first")
    assert ap.eligible_for_attempt(entry, "different-real-attempt")
