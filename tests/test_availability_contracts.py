"""Regresiones funcionales de integración y datos de disponibilidad."""

from __future__ import annotations

import json
from pathlib import Path

import availability_state as state
import delegate
import pytest
import session_worker as worker
from availability_performance import sample_to_dict
from session_store import StoreError

from tests.conftest import Harness
from tests.fakes import DEFAULT_MODEL, FakeBinding, api_model, default_config_sources
from tests.test_availability_performance import _sample
from tests.test_availability_supervisor import seed_state
from tests.test_session_store import make_record


def test_configuration_change_invalidates_cached_selection(harness: Harness) -> None:
    harness.fake()
    assert harness.doctor()["status"] == "ok"
    assert harness.binding is not None
    context = harness.binding.context
    binding = FakeBinding(
        context=context,
        sources=[
            *default_config_sources(),
            {
                "type": "document",
                "info": {"models": {"other/model": {"enabled": False}}},
            },
        ],
    )
    harness.monkeypatch.setattr(
        delegate, "discover_existing", lambda *args, **kwargs: binding
    )
    prepared = delegate._prepare_run(
        harness.project,
        lambda: "real authorized task",
        DEFAULT_MODEL,
        None,
        "reason",
        "build",
        30,
        context=context,
    )
    assert len(binding.catalog_calls) == 1
    prepared.binding.close()


def test_new_compatible_service_version_refreshes_capability_contract(
    harness: Harness,
) -> None:
    harness.fake()
    assert harness.doctor()["status"] == "ok"
    assert harness.binding is not None
    context = harness.binding.context
    binding = FakeBinding(context=context, version="3.1.0")
    harness.monkeypatch.setattr(
        delegate, "discover_existing", lambda *args, **kwargs: binding
    )
    prepared = delegate._prepare_run(
        harness.project,
        lambda: "task",
        DEFAULT_MODEL,
        None,
        "reason",
        "build",
        30,
        context=context,
    )
    assert len(binding.catalog_calls) == 1
    prepared.binding.close()


def test_same_model_keeps_metadata_for_both_projects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    a = tmp_path / "A"
    b = tmp_path / "B"
    a.mkdir()
    b.mkdir()
    from service_identity import HostContext

    context = HostContext(tmp_path / "registration", tmp_path / "host", "2.2.0")
    bindings = []

    def discover(*args: object, **kwargs: object) -> FakeBinding:
        binding = FakeBinding(context=context)
        bindings.append(binding)
        return binding

    monkeypatch.setattr(delegate, "resolve_host_context", lambda: context)
    monkeypatch.setattr(delegate, "discover_existing", discover)
    monkeypatch.setattr(delegate, "find_opencode", lambda: "fake-opencode")
    for project in (a, b, a):
        result = delegate._prepare_run(
            project,
            lambda: "task",
            DEFAULT_MODEL,
            None,
            "reason",
            "build",
            30,
            context=context,
        )
        result.binding.close()
    assert len(bindings[0].catalog_calls) == 1
    assert len(bindings[1].catalog_calls) == 1
    assert not any(
        kind in {"catalog", "usage", "openapi", "integrations"}
        for kind, _ in bindings[2].calls
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prompt", "secret"),
        ("task_id", None),
        ("source", "x" * 300),
        ("limitations", ["x"] * 33),
        ("task_seconds", True),
    ],
)
def test_state_rejects_unsanitized_performance(
    tmp_path: Path, field: str, value: object
) -> None:
    path = tmp_path / "state" / "availability-state.json"
    state.write_snapshot(path, state.empty_snapshot())
    payload = json.loads(path.read_text())
    sample = sample_to_dict(_sample())
    sample[field] = value
    payload["performance_samples"] = [sample]
    path.write_text(json.dumps(payload))
    with pytest.raises(StoreError):
        state.read_snapshot(path)


@pytest.mark.parametrize(
    ("event_type", "expected", "exhausted"),
    [
        ("provider.quota-exhausted", "quota_exhausted", True),
        ("provider.rate-limit", "rate_limited", False),
        ("provider.auth", "auth_error", False),
        ("provider.output-budget", "unaffordable_output", False),
        ("provider.insufficient-credits", "balance_exhausted", True),
        ("task.compilation", "task_failed", False),
    ],
)
def test_durable_outcome_classifies_only_structured_errors(
    tmp_path: Path, event_type: str, expected: str, exhausted: bool
) -> None:
    from service_identity import HostContext

    root = tmp_path / "project"
    root.mkdir()
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    record = make_record(root)
    seed_state(context, root, record.model)
    output = json.dumps(
        {
            "type": "error",
            "error": {
                "type": event_type,
                "message": "private text mentioning auth timeout quota",
            },
        }
    )
    worker._record_availability_outcome(
        context, record, output, ["opencode_event_error"], "failed", False
    )
    snapshot = state.read_snapshot(state.state_path(context.aikit_state))
    assert snapshot is not None
    entry = snapshot.models[record.model]
    assert entry.query_attempt is not None
    assert entry.query_attempt.result == expected
    assert (entry.quota is not None and entry.quota.status == "exhausted") == exhausted


def test_outcome_recovery_enriches_one_stable_typed_sample(tmp_path: Path) -> None:
    from service_identity import HostContext

    root = tmp_path / "project"
    root.mkdir()
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    record = make_record(root)
    seed_state(context, root, record.model)
    first = json.dumps({"id": "real-event", "type": "text", "task_seconds": 1})
    second = json.dumps(
        {
            "id": "real-event",
            "type": "text",
            "task_seconds": 1,
            "tool_seconds": 0.5,
            "observed_at": "2026-12-01T00:00:00+00:00",
        }
    )
    worker._record_availability_outcome(context, record, first, [], "completed", False)
    before = state.read_snapshot(state.state_path(context.aikit_state))
    assert before is not None
    worker._record_availability_outcome(context, record, second, [], "completed", False)
    after = state.read_snapshot(state.state_path(context.aikit_state))
    assert after is not None
    assert len(after.performance_samples) == 1
    assert after.performance_samples[0].tool_seconds == 0.5
    assert (
        after.performance_samples[0].observed_at
        == before.performance_samples[0].observed_at
    )
    assert (
        after.models[record.model].query_attempt
        == before.models[record.model].query_attempt
    )


def test_missing_catalog_capability_is_bounded_and_never_submits(
    harness: Harness,
) -> None:
    transport = harness.fake(catalog_returncode=1)
    result = harness.run_text("no submission")
    assert result["code"] == "catalog_capability_unavailable"
    assert transport.run_calls == []


def test_refresh_store_error_is_a_fixed_public_diagnostic(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    transport = harness.fake()

    def failure(*args: object, **kwargs: object) -> object:
        raise StoreError("lock_contended", "private untrusted details")

    monkeypatch.setattr("availability_refresh.coalesced_refresh", failure)
    result = harness.run_text("no submission")
    assert result["code"] == "availability_state_unavailable"
    assert "private" not in json.dumps(result)
    assert transport.run_calls == []


def test_doctor_respects_explicit_prefer_free_override(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    harness.fake(
        models=[
            api_model("free"),
            api_model("paid", provider="opencode-go", cost=[{"input": 1, "output": 1}]),
        ]
    )
    monkeypatch.setattr(delegate, "load_policy", lambda: {"prefer_free": True})
    result = harness.doctor()
    assert result["status"] == "ok"
    assert result["catalog"][0]["model"] == "opencode/free"


def test_refresh_missing_host_is_a_bounded_public_result(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    from service_identity import ServiceError

    def missing() -> object:
        raise ServiceError("host_context_unavailable")

    monkeypatch.setattr(delegate, "resolve_host_context", missing)
    result = delegate.availability_refresh_command(harness.project)
    assert result["status"] == "error"
    assert result["code"] == "host_context_unavailable"


def test_performance_state_rejects_more_than_bounded_window(tmp_path: Path) -> None:
    path = tmp_path / "availability-state.json"
    state.write_snapshot(path, state.empty_snapshot())
    payload = json.loads(path.read_text())
    payload["performance_samples"] = [sample_to_dict(_sample())] * 1001
    path.write_text(json.dumps(payload))
    with pytest.raises(StoreError):
        state.read_snapshot(path)


def test_admission_survives_other_context_generation_but_rejects_changed_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dataclasses import replace

    import host_registry as registry

    from tests.test_bound_worker import prepared

    context, record, binding = prepared(tmp_path, monkeypatch)
    path = state.state_path(context.aikit_state)
    snapshot = state.read_snapshot(path)
    assert snapshot is not None
    project_key = delegate._project_key(Path(record.cwd))
    admission = state.admission_for(snapshot, project_key, record.model, record.variant)
    registry.reserve_host_attempt(context, record, agent="build", admission=admission)
    other = tmp_path / "other"
    other.mkdir()
    other_key = delegate._project_key(other)
    state.write_snapshot(
        path,
        replace(
            snapshot,
            generation=snapshot.generation + 1,
            catalog_contexts=(
                *snapshot.catalog_contexts,
                replace(snapshot.catalog_contexts[0], project_key=other_key),
            ),
        ),
    )
    from unittest.mock import Mock

    from service_connection import ManagedBinding

    authenticated = Mock(spec=ManagedBinding, wraps=binding)
    authenticated.token = binding.token
    authenticated.registration = binding.registration
    command = worker._bound_command(record, "task", context, authenticated)
    assert "--server" in command
    assert (
        registry.load_host_task(context, record.task_id).attempts[0].admission
        == admission
    )
    binding.restricted = False
    with pytest.raises(delegate.DelegateError, match="Configuracion"):
        worker._bound_command(record, "task", context, authenticated)
