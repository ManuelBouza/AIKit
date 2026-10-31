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
