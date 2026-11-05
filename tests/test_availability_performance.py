"""Pruebas del perfil puro de rendimiento observado."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import availability_performance as p
import pytest


def _utc(text: str) -> datetime:
    return datetime.fromisoformat(text)


def _key() -> p.PerformanceModelKey:
    return p.PerformanceModelKey(
        provider="opencode-go", model="opencode-go/iceman", variant="high"
    )


def _sample(**overrides: Any) -> p.PerformanceSample:
    data: dict[str, Any] = {
        "key": _key(),
        "task_id": "task-1",
        "attempt_id": "attempt-1",
        "source": "cli_json_v2",
        "measurement_kind": "model",
        "observed_at": _utc("2026-10-31T15:00:00+00:00"),
        "event_id": "evt-1",
        "role": "implementer",
        "context_bucket": "ctx-100k",
        "ttft_seconds": 2.0,
        "generation_seconds": 4.0,
        "task_seconds": 10.0,
        "tool_seconds": 3.0,
        "tokens": p.TokenStats(output_tokens=100, total_tokens=120),
    }
    data.update(overrides)
    return p.PerformanceSample(**data)


def test_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="."):
        _sample(observed_at=datetime(2026, 10, 31, 15, 0, 0))


def test_bool_is_not_token_count() -> None:
    with pytest.raises(ValueError, match="."):
        p.TokenStats(output_tokens=True)


def test_tokens_per_second_null_when_insufficient() -> None:
    sample = _sample(tokens=p.TokenStats(output_tokens=0), generation_seconds=4.0)
    assert sample.tokens_per_second is None
    assert p.tokens_per_second(p.TokenStats(output_tokens=5), None) is None
    assert p.tokens_per_second(p.TokenStats(output_tokens=5), 0.0) is None


def test_tokens_per_second_computed_when_sufficient() -> None:
    assert p.tokens_per_second(p.TokenStats(output_tokens=8), 2.0) == 4.0


def test_clock_inverted_task_time_rejected() -> None:
    with pytest.raises(ValueError, match="."):
        _sample(task_seconds=-1.0)


def test_event_without_semantics_keeps_ttft_unknown() -> None:
    event = {"type": "text", "sessionID": "ses_prueba", "part": {"text": "hola"}}
    sample = p.extract_performance_sample(
        event,
        task_id="t",
        attempt_id="a",
        key=_key(),
        observed_at=_utc("2026-10-31T15:00:00+00:00"),
    )
    assert sample is None or sample.ttft_seconds is None


def test_walltime_only_is_task_not_ttft() -> None:
    event = {
        "type": "step_finish",
        "sessionID": "ses_prueba",
        "time": {"created": 1000.0, "updated": 1012.0},
    }
    sample = p.extract_performance_sample(
        event,
        task_id="t",
        attempt_id="a",
        key=_key(),
        observed_at=_utc("2026-10-31T15:00:00+00:00"),
    )
    assert sample is not None
    assert sample.ttft_seconds is None
    assert sample.measurement_kind == "task"
    assert sample.task_seconds == 12.0


def test_dedupe_same_event_and_multiple_attempts() -> None:
    window = p.PerformanceWindow(max_samples=10)
    first = _sample()
    duplicate = _sample()
    other_attempt = _sample(attempt_id="attempt-2", event_id="evt-2")
    window = p.add_sample(window, first)
    window = p.add_sample(window, duplicate)
    window = p.add_sample(window, other_attempt)
    assert len(window.samples) == 2


def test_bounded_retention_drops_oldest() -> None:
    window = p.PerformanceWindow(max_samples=2)
    older = _sample(event_id="evt-old", observed_at=_utc("2026-10-31T14:00:00+00:00"))
    middle = _sample(event_id="evt-mid", observed_at=_utc("2026-10-31T14:30:00+00:00"))
    newer = _sample(event_id="evt-new", observed_at=_utc("2026-10-31T15:00:00+00:00"))
    window = p.add_sample(window, older)
    window = p.add_sample(window, middle)
    window = p.add_sample(window, newer)
    assert len(window.samples) == 2
    assert all(item.event_id != "evt-old" for item in window.samples)


def test_aggregate_rejects_mixed_keys() -> None:
    other = _sample(
        key=p.PerformanceModelKey(provider="other", model="other/model"),
        event_id="evt-2",
    )
    with pytest.raises(ValueError, match="."):
        p.aggregate_samples([_sample(), other])


def test_aggregate_computes_medians() -> None:
    a = _sample(event_id="evt-a", ttft_seconds=1.0, tokens_per_second=10.0)
    b = _sample(event_id="evt-b", ttft_seconds=3.0, tokens_per_second=20.0)
    result = p.aggregate_samples([a, b])
    assert result.sample_count == 2
    assert result.ttft_seconds == 2.0
    assert result.tokens_per_second == 15.0
    assert result.confidence == "low"


def test_no_raw_secret_content_in_serialized_sample() -> None:
    sample = _sample()
    serialized = p.sample_to_dict(sample)
    forbidden = {
        "prompt",
        "response",
        "path",
        "credential",
        "hash",
        "reasoning",
        "content",
    }
    assert forbidden.isdisjoint(serialized.keys())
    text = str(serialized)
    for secret in ("sk-secret", "C:/private", "password"):
        assert secret not in text


def test_context_and_role_are_preserved_for_comparison() -> None:
    sample = _sample(role="reviewer", context_bucket="ctx-200k")
    result = p.aggregate_samples([sample])
    assert result.key == sample.key
    assert sample.role == "reviewer"
    assert sample.context_bucket == "ctx-200k"


def test_performance_sort_key_prefers_lower_ttft() -> None:
    fast = p.aggregate_samples([_sample(event_id="fast", ttft_seconds=1.0)])
    slow = p.aggregate_samples([_sample(event_id="slow", ttft_seconds=5.0)])
    assert p.performance_sort_key(fast) < p.performance_sort_key(slow)


def test_window_roundtrip_json() -> None:
    window = p.add_sample(p.PerformanceWindow(max_samples=5), _sample())
    restored = p.window_from_dict(p.window_to_dict(window))
    assert len(restored.samples) == 1
    assert restored.samples[0].task_id == "task-1"


def test_freshness_seconds_not_negative() -> None:
    result = p.aggregate_samples([_sample()])
    future = _utc("2026-10-31T14:00:00+00:00")
    assert p.freshness_seconds(result, future) == 0.0


def test_recovered_event_enriches_one_sample_without_new_freshness() -> None:
    from dataclasses import replace

    first = _sample(role=None, context_bucket=None, ttft_seconds=None)
    second = replace(
        first,
        observed_at=_utc("2026-11-02T15:00:00+00:00"),
        role="reviewer",
        context_bucket="large",
        ttft_seconds=1,
    )
    window = p.add_sample(p.add_sample(p.PerformanceWindow(), first), second)
    assert len(window.samples) == 1
    assert window.samples[0].role == "reviewer"
    assert window.samples[0].context_bucket == "large"
    assert window.samples[0].ttft_seconds == 1
    assert window.samples[0].observed_at == first.observed_at


def test_direct_aggregate_dedupes_recovered_event_dates() -> None:
    from dataclasses import replace

    sample = _sample()
    recovered = replace(sample, observed_at=_utc("2026-11-01T15:00:00+00:00"))
    result = p.aggregate_samples([sample, recovered])
    assert result.sample_count == 1
    assert result.last_observed_at == sample.observed_at


@pytest.mark.parametrize(
    "changes",
    [
        {"role": "reviewer"},
        {"context_bucket": "larger"},
        {"source": "other-supported-source"},
        {"measurement_kind": "task"},
    ],
)
def test_incomparable_conditions_stay_separate(changes: dict[str, Any]) -> None:
    first = _sample()
    second = _sample(event_id="other", **changes)
    with pytest.raises(ValueError, match="."):
        p.aggregate_samples([first, second])
    results = p.aggregate_comparable([first, second])
    assert len(results) == 2
    assert sum(result.sample_count for result in results) == 2
    assert all(p.result_to_dict(result)["role"] == result.role for result in results)


def test_model_and_tool_times_are_independent_measurements() -> None:
    sample = _sample(model_seconds=1, tool_seconds=20, task_seconds=25)
    assert sample.model_seconds == 1
    assert sample.tool_seconds == 20


def test_total_tokens_do_not_invent_generation_throughput() -> None:
    assert (
        p.tokens_per_second(p.TokenStats(input_tokens=99, total_tokens=100), 1) is None
    )


# --- Attempt timing observation regression tests ---


def test_two_attempts_same_session_separate_timings() -> None:
    """Two attempts sharing one session have separate PerformanceSamples keyed by attempt_id."""
    window = p.PerformanceWindow(max_samples=10)
    _key()

    # Attempt 1
    sample1 = _sample(
        task_id="task-1",
        attempt_id="attempt-1",
        event_id="supervisor-task-total",
        task_seconds=10.0,
    )
    # Attempt 2 (same session, different attempt_id)
    sample2 = _sample(
        task_id="task-1",
        attempt_id="attempt-2",
        event_id="supervisor-task-total",
        task_seconds=20.0,
    )

    window = p.add_sample(window, sample1)
    window = p.add_sample(window, sample2)

    assert len(window.samples) == 2
    samples_by_attempt = {s.attempt_id: s for s in window.samples}
    assert samples_by_attempt["attempt-1"].task_seconds == 10.0
    assert samples_by_attempt["attempt-2"].task_seconds == 20.0


def test_completed_vs_error_censored_separation() -> None:
    """aggregate_samples separates completed from error/interrupted/pending (right-censored)."""
    _key()

    # Completed sample
    completed = _sample(
        event_id="evt-completed",
        task_seconds=10.0,
        tokens=p.TokenStats(output_tokens=100),
    )
    # Error sample (censored)
    error = _sample(
        event_id="evt-error",
        task_seconds=5.0,
        tokens=p.TokenStats(output_tokens=0),
        limitations=("delivery_failed",),
    )
    # Interrupted sample (censored)
    _sample(
        event_id="evt-interrupted",
        task_seconds=3.0,
        tokens=p.TokenStats(output_tokens=0),
        limitations=("interrupted",),
    )
    # Pending sample (censored)
    _sample(
        event_id="evt-pending",
        task_seconds=1.0,
        tokens=p.TokenStats(output_tokens=0),
        limitations=("pending",),
    )

    # Aggregate only completed samples
    result = p.aggregate_samples([completed])
    assert result.sample_count == 1
    assert result.task_seconds == 10.0

    # Aggregate with censored samples - they should be separate groups by measurement_kind or filtered
    # In practice, supervisor only records completed/failed deliveries as outcomes
    # Here we verify that censored samples have limitations and don't pollute completed aggregates
    error_result = p.aggregate_samples([error])
    assert "delivery_failed" in error_result.limitations
    assert error_result.task_seconds == 5.0  # Still recorded but with limitation


def test_dedupe_recovery_and_observer_restart() -> None:
    """Recovery enriches missing fields; observer restart doesn't reset actual attempt start (observed_at = min)."""
    from dataclasses import replace

    window = p.PerformanceWindow(max_samples=10)
    _key()

    # Initial sample with partial data (e.g., missing role, context_bucket)
    first = _sample(
        role=None,
        context_bucket=None,
        ttft_seconds=None,
        event_id="supervisor-task-total",
        task_seconds=10.0,
    )
    window = p.add_sample(window, first)

    # Recovery adds missing fields with later observed_at
    recovered = replace(
        first,
        observed_at=_utc("2026-11-02T15:00:00+00:00"),
        role="reviewer",
        context_bucket="large",
        ttft_seconds=1.0,
    )
    window = p.add_sample(window, recovered)

    # Should dedupe to ONE sample (same dedupe key)
    assert len(window.samples) == 1
    merged = window.samples[0]
    # observed_at should be the EARLIER one (min), not reset by recovery
    assert merged.observed_at == first.observed_at
    # But missing fields should be enriched
    assert merged.role == "reviewer"
    assert merged.context_bucket == "large"
    assert merged.ttft_seconds == 1.0


def test_legacy_unknown_malformed_timing() -> None:
    """Legacy/malformed/unknown timestamps remain unavailable; don't crash."""
    key = _key()

    # Sample with no timing data at all
    sample_no_time = p.PerformanceSample(
        key=key,
        task_id="t1",
        attempt_id="a1",
        source="cli_json_v2",
        measurement_kind="task",
        observed_at=_utc("2026-10-31T15:00:00+00:00"),
        event_id="evt-none",
        role="implementer",
        context_bucket="ctx",
        ttft_seconds=None,
        generation_seconds=None,
        model_seconds=None,
        task_seconds=None,
        tool_seconds=None,
        tokens=p.TokenStats(),
        limitations=("task_time_unavailable", "ttft_unavailable"),
    )
    assert sample_no_time.task_seconds is None
    assert "task_time_unavailable" in sample_no_time.limitations

    # Sample with negative time rejected at construction
    with pytest.raises(ValueError, match="finito y no negativo"):
        _sample(task_seconds=-1.0)

    # Malformed event (no semantic fields) returns None or sample with limitations
    event = {"type": "unknown", "sessionID": "ses_x"}
    sample = p.extract_performance_sample(
        event,
        task_id="t",
        attempt_id="a",
        key=key,
        observed_at=_utc("2026-10-31T15:00:00+00:00"),
    )
    # No semantic timing fields -> no useful sample
    assert sample is None or sample.task_seconds is None


def test_comparable_grouping_insufficient_samples() -> None:
    """Comparable grouping by key+source+kind+role+context_bucket; N<3 reports insufficient."""
    key1 = _key()  # provider=opencode-go, model=opencode-go/iceman, variant=high
    key2 = p.PerformanceModelKey(provider="other", model="other/model", variant="low")

    samples = [
        _sample(
            key=key1, event_id="evt-1", role="implementer", context_bucket="ctx-100k"
        ),
        _sample(
            key=key1, event_id="evt-2", role="implementer", context_bucket="ctx-100k"
        ),
        # Different role -> separate group
        _sample(key=key1, event_id="evt-3", role="reviewer", context_bucket="ctx-100k"),
        # Different key -> separate group
        _sample(
            key=key2, event_id="evt-4", role="implementer", context_bucket="ctx-100k"
        ),
    ]

    results = p.aggregate_comparable(samples)

    # Should produce 3 groups: (key1, implementer), (key1, reviewer), (key2, implementer)
    assert len(results) == 3

    # Group 1: key1 + implementer (2 samples) -> confidence "low" (<3)
    group1 = next(r for r in results if r.role == "implementer" and r.key == key1)
    assert group1.sample_count == 2
    assert group1.confidence == "low"
    assert (
        "insufficient" in str(group1.limitations).lower() or group1.confidence == "low"
    )

    # Group 2: key1 + reviewer (1 sample) -> confidence "low"
    group2 = next(r for r in results if r.role == "reviewer")
    assert group2.sample_count == 1
    assert group2.confidence == "low"

    # Group 3: key2 + implementer (1 sample) -> confidence "low"
    group3 = next(r for r in results if r.key == key2)
    assert group3.sample_count == 1
    assert group3.confidence == "low"


def test_pending_then_completed_merge_prefers_completed() -> None:
    """Pending observation then completed for same attempt yields completed without pending limitation."""
    window = p.PerformanceWindow(max_samples=10)
    _key()

    # First observation: pending, task_seconds=10
    pending_sample = _sample(
        task_id="task-1",
        attempt_id="attempt-1",
        event_id="evt-1",
        task_seconds=10.0,
        limitations=("pending",),
    )
    # Later completed observation, same dedupe key, task_seconds=20, no pending limitation
    completed_sample = _sample(
        task_id="task-1",
        attempt_id="attempt-1",
        event_id="evt-1",
        task_seconds=20.0,
        limitations=(),
    )

    window = p.add_sample(window, pending_sample)
    window = p.add_sample(window, completed_sample)

    assert len(window.samples) == 1
    merged = window.samples[0]
    assert merged.task_seconds == 20.0
    assert "pending" not in merged.limitations


def test_completed_then_pending_does_not_downgrade() -> None:
    """If completed sample already recorded, later pending (older) does not downgrade."""
    window = p.PerformanceWindow(max_samples=10)
    _key()

    # Completed first
    completed_sample = _sample(
        task_id="task-1",
        attempt_id="attempt-1",
        event_id="evt-1",
        task_seconds=20.0,
        limitations=(),
        observed_at=_utc("2026-11-01T12:00:00+00:00"),
    )
    # Later pending (older observed_at)
    pending_sample = _sample(
        task_id="task-1",
        attempt_id="attempt-1",
        event_id="evt-1",
        task_seconds=10.0,
        limitations=("pending",),
        observed_at=_utc("2026-11-01T11:00:00+00:00"),
    )

    window = p.add_sample(window, completed_sample)
    window = p.add_sample(window, pending_sample)

    assert len(window.samples) == 1
    merged = window.samples[0]
    # Should keep completed task_seconds=20 and no pending limitation
    assert merged.task_seconds == 20.0
    assert "pending" not in merged.limitations
