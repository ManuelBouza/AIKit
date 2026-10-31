"""Outcome y rendimiento durables del supervisor sobre la tabla compartida."""

from __future__ import annotations

import sys
from pathlib import Path

import delegate
import host_registry as hr
import pytest
import session_worker as sw
from availability_state import (
    state_path,
)
from service_identity import HostContext
from session_store import save_task

from tests.test_bound_worker import Binding
from tests.test_session_store import TASK_ID, make_record


def seed_state(context: HostContext, root: Path, model: str) -> None:
    from tests.fakes import api_model, seed_availability, variant

    provider, name = model.split("/", 1)
    seed_availability(
        context, root, [api_model(name, provider=provider, variants=[variant("high")])]
    )


def test_supervisor_records_success_outcome_and_performance_sample(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    root = tmp_path / "project"
    root.mkdir()
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    model = "opencode-go/kimi-k3.1-pro"
    record = make_record(root)
    record = record.__class__(
        **{
            **record.__dict__,
            "model": model,
            "variant": "high",
            "server_identity": Binding.token,
            "previous_attempt_ids": [],
        }
    )
    save_task(root, record)
    hr.reserve_host_attempt(context, record, agent="build")
    (root / ".aikit" / "sessions" / TASK_ID / "task.txt").write_text(
        "prompt", encoding="utf-8"
    )

    binding = Binding()
    monkeypatch.setattr(sw, "discover_existing", lambda ctx: binding)
    monkeypatch.setattr(delegate, "find_opencode", lambda: "fake-opencode")
    seed_state(context, root, model)

    event = {
        "type": "text",
        "sessionID": "ses",
        "part": {"text": "ok", "task_seconds": 1.5},
    }
    finish = {"type": "step_finish", "sessionID": "ses", "part": {"reason": "stop"}}
    code = (
        f"import json,sys; print(json.dumps({event!r})); print(json.dumps({finish!r}))"
    )
    rc = sw.supervise(
        root,
        TASK_ID,
        context=context,
        prepare_command=lambda _: [sys.executable, "-c", code],
    )
    assert rc == 0

    from availability_state import read_snapshot

    snapshot = read_snapshot(state_path(context.aikit_state))
    assert snapshot is not None
    entry = snapshot.models[model]
    assert record.attempt_id in entry.outcome_attempt_ids
    assert entry.query_attempt is not None
    assert entry.query_attempt.result == "success"
    assert len(snapshot.performance_samples) >= 1
    assert snapshot.performance_samples[0].task_seconds == 1.5
    from bound_execution import recover_local_result
    from session_store import load_task

    settled = load_task(root, TASK_ID)
    before = snapshot.performance_samples
    recover_local_result(context, settled)
    recover_local_result(context, settled)
    recovered = read_snapshot(state_path(context.aikit_state))
    assert recovered is not None
    assert recovered.performance_samples == before


def test_supervisor_free_limit_triggers_one_refresh_not_task_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    root = tmp_path / "project"
    root.mkdir()
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    model = "opencode-go/kimi-k3.1-pro"
    record = make_record(root)
    record = record.__class__(
        **{
            **record.__dict__,
            "model": model,
            "variant": "high",
            "server_identity": Binding.token,
            "previous_attempt_ids": [],
        }
    )
    save_task(root, record)
    hr.reserve_host_attempt(context, record, agent="build")
    (root / ".aikit" / "sessions" / TASK_ID / "task.txt").write_text(
        "prompt", encoding="utf-8"
    )

    binding = Binding()
    monkeypatch.setattr(sw, "discover_existing", lambda ctx: binding)
    monkeypatch.setattr(delegate, "find_opencode", lambda: "fake-opencode")
    seed_state(context, root, model)

    refresh_calls = {"count": 0}

    def fake_refresh(*args: object, **kwargs: object) -> object:
        refresh_calls["count"] += 1
        from availability_refresh import RefreshResult
        from availability_state import read_snapshot

        snap = read_snapshot(state_path(context.aikit_state))
        assert snap is not None
        return RefreshResult(
            snapshot=snap, refreshed=True, generation=snap.generation + 1, errors=()
        )

    monkeypatch.setattr("availability_refresh.coalesced_refresh", fake_refresh)

    event = {
        "type": "error",
        "sessionID": "ses",
        "error": {"type": "provider.free-limit", "message": "quota"},
    }
    finish = {"type": "step_finish", "sessionID": "ses", "part": {"reason": "stop"}}
    code = (
        "import json,sys; "
        + f"print(json.dumps({event!r})); "
        + f"print(json.dumps({finish!r}))"
    )
    rc = sw.supervise(
        root,
        TASK_ID,
        context=context,
        prepare_command=lambda _: [sys.executable, "-c", code],
    )
    assert rc != 0
    assert refresh_calls["count"] == 1

    from availability_state import read_snapshot

    snapshot = read_snapshot(state_path(context.aikit_state))
    assert snapshot is not None
    entry = snapshot.models[model]
    assert entry.quota is not None
    assert entry.quota.status == "exhausted"
    assert entry.query_attempt is not None
    assert entry.query_attempt.result == "quota_exhausted"
    assert entry.outcome_attempt_ids == (record.attempt_id,)
