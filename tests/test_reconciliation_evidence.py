"""Evidencia diagnóstica, publicación atómica y recuperación conservadora."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from typing import Any

import bound_execution as be
import pytest
import session_worker as worker_module
from service_identity import HostContext, ServiceError
from session_store import StoreError, load_task

from tests.fakes import FakeBinding, finish_event, text_event
from tests.test_session_store import TASK_ID
from tests.test_session_worker import prepare, result, run_fake, worker
from tests.test_worker_reconciliation import _message_event, _seed


def _context(root: Path) -> HostContext:
    return HostContext(root / "registration", root / "state", "2.2.0")


def _bound(
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
    code: str | None = None,
) -> tuple[ModuleType, FakeBinding, HostContext, int, Path]:
    directory = prepare(root)
    context = _context(root)
    binding = FakeBinding(context=context)
    _seed(root, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    outcome = run_fake(
        root,
        code or f"print({_message_event()!r})",
        context=context,
    )
    return module, binding, context, outcome, directory


def _message_gets(binding: FakeBinding) -> list[tuple[Any, ...]]:
    return [call for call in binding.request_calls if call[0] == "session.message.get"]


def test_write_result_atomic_preserves_bytes_and_prior_destination_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    attempt = tmp_path / "attempt"
    attempt.mkdir()
    report = {"delivery": "pending", "summary": "caf\u00e9"}
    expected = json.dumps(report, ensure_ascii=True).encode("utf-8")

    payload, digest = worker_module._write_result_atomic(attempt, report)
    assert payload == expected
    assert digest == hashlib.sha256(expected).hexdigest()
    assert digest == worker_module._result_sha256(expected)
    assert (attempt / "result.json").read_bytes() == expected

    prior = (attempt / "result.json").read_bytes()
    unrelated = attempt / ".result-other.tmp"
    unrelated.write_bytes(b"other writer")

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(worker_module, "_atomic_replace", fail_replace)
    with pytest.raises(OSError, match="replace failed"):
        worker_module._write_result_atomic(attempt, report)
    assert (attempt / "result.json").read_bytes() == prior
    assert list(attempt.glob(".result-*.tmp")) == [unrelated]
    assert unrelated.read_bytes() == b"other writer"


def test_pending_save_failure_prevents_get_or_new_completed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = worker()
    original_save = module.save_task

    def fail_provisional(root: Path, record: Any) -> None:
        observation = getattr(record, "reconciliation", None)
        if observation is not None and observation.lifecycle == "provisional":
            raise StoreError("record_save_failed", "pending save failed")
        original_save(root, record)

    monkeypatch.setattr(module, "save_task", fail_provisional)
    module, binding, _context_value, outcome, directory = _bound(tmp_path, monkeypatch)
    record = load_task(tmp_path, TASK_ID)
    assert outcome == 1
    assert not _message_gets(binding)
    assert record.delivery is not None
    assert record.delivery.state != "completed"
    assert not (directory / record.attempt_id / "result.json").exists()
    assert (
        record.reconciliation is None or record.reconciliation.lifecycle != "committed"
    )


def test_result_write_failure_keeps_record_provisional(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_result(*args: Any, **kwargs: Any) -> Any:
        raise OSError("result write failed")

    monkeypatch.setattr(
        worker_module, "_write_result_atomic", fail_result, raising=False
    )
    module, binding, _context_value, outcome, directory = _bound(tmp_path, monkeypatch)
    record = load_task(tmp_path, TASK_ID)
    assert outcome == 1
    assert record.reconciliation is not None
    assert record.reconciliation.lifecycle == "provisional"
    assert record.delivery is not None
    assert record.delivery.state == "pending"
    assert be.recover_local_result(_context_value, record)["status"] == "pending"


def test_host_observation_failure_blocks_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_observation = worker().record_host_observation

    def fail_terminal(*args: Any, **kwargs: Any) -> None:
        if kwargs.get("terminal") is True:
            raise StoreError("provenance_unavailable", "host observation failed")
        original_observation(*args, **kwargs)

    monkeypatch.setattr(worker_module, "record_host_observation", fail_terminal)
    module, binding, context, outcome, directory = _bound(tmp_path, monkeypatch)
    record = load_task(tmp_path, TASK_ID)
    assert outcome == 1
    assert record.reconciliation is not None
    assert record.reconciliation.lifecycle == "provisional"
    assert be.recover_local_result(context, record)["status"] == "pending"


@pytest.mark.parametrize("raises", [True, False])
def test_last_owner_check_failure_blocks_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raises: bool
) -> None:
    module = worker()
    original_verify = FakeBinding.verify_owner
    terminal_seen = False

    def fail_after_terminal(self: FakeBinding, *, timeout: float = 1.0) -> Any:
        if terminal_seen:
            if raises:
                raise ServiceError("owner_mismatch", "private-owner-detail")
            return None
        return original_verify(self, timeout=timeout)

    original_observation = worker().record_host_observation

    def observe_and_mark(*args: Any, **kwargs: Any) -> None:
        nonlocal terminal_seen
        original_observation(*args, **kwargs)
        if kwargs.get("terminal") is True:
            terminal_seen = True

    monkeypatch.setattr(worker_module, "record_host_observation", observe_and_mark)
    monkeypatch.setattr(FakeBinding, "verify_owner", fail_after_terminal)
    module, binding, context, outcome, directory = _bound(tmp_path, monkeypatch)
    record = load_task(tmp_path, TASK_ID)
    assert outcome == 1
    assert record.reconciliation is not None
    assert record.reconciliation.lifecycle in {"provisional", "invalidated"}
    assert record.delivery is not None
    assert record.delivery.state != "completed"
    assert be.recover_local_result(context, record)["status"] == "pending"
    assert "private-owner-detail" not in result(directory)["limitations"]


def test_commit_save_failure_recovery_stays_pending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = worker()
    original_save = module.save_task

    def fail_commit(root: Path, record: Any) -> None:
        observation = getattr(record, "reconciliation", None)
        if observation is not None and observation.lifecycle == "committed":
            raise StoreError("record_save_failed", "commit save failed")
        original_save(root, record)

    monkeypatch.setattr(module, "save_task", fail_commit)
    module, binding, context, outcome, directory = _bound(tmp_path, monkeypatch)
    record = load_task(tmp_path, TASK_ID)
    assert outcome == 1
    assert record.reconciliation is not None
    assert record.reconciliation.lifecycle == "provisional"
    assert record.delivery is not None
    assert record.delivery.state == "pending"
    assert be.recover_local_result(context, record)["status"] == "pending"


def test_crash_after_host_terminal_before_commit_stays_pending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    worker()
    original_observation = worker().record_host_observation

    def crash_after_terminal(*args: Any, **kwargs: Any) -> None:
        original_observation(*args, **kwargs)
        if kwargs.get("terminal") is True:
            raise RuntimeError("injected crash after host terminal")

    monkeypatch.setattr(worker_module, "record_host_observation", crash_after_terminal)
    with pytest.raises(RuntimeError, match="injected crash"):
        _bound(tmp_path, monkeypatch)
    context = _context(tmp_path)
    record = load_task(tmp_path, TASK_ID)
    assert record.reconciliation is not None
    assert record.reconciliation.lifecycle == "provisional"
    assert record.delivery is not None
    assert record.delivery.state == "pending"
    assert be.recover_local_result(context, record)["status"] == "pending"


def test_postcommit_result_rewrite_fails_digest_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, binding, context, outcome, directory = _bound(tmp_path, monkeypatch)
    record = load_task(tmp_path, TASK_ID)
    assert outcome == 0
    assert record.reconciliation is not None
    assert record.reconciliation.lifecycle == "committed"
    assert record.reconciliation.result_sha256 is not None
    assert be.recover_local_result(context, record)["status"] == "ok"
    result_path = directory / record.attempt_id / "result.json"
    result_path.write_bytes(result_path.read_bytes() + b" ")

    recovered = be.recover_local_result(context, record)

    assert recovered["status"] == "pending"
    assert recovered["delivery"] == "pending"
    assert "result_mismatch" in recovered["limitations"]


def test_negative_outcome_commits_diagnostic_without_promoting_delivery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = worker()
    original_binding = FakeBinding(context=_context(tmp_path))
    binding = original_binding
    binding.responses["session.message.get"]["data"]["finish"] = "length"
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    context = binding.context
    prepare(tmp_path)
    _seed(tmp_path, context, binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    outcome = run_fake(tmp_path, f"print({_message_event()!r})", context=context)
    record = load_task(tmp_path, TASK_ID)
    assert outcome == 1
    assert record.reconciliation is not None
    assert record.reconciliation.accepted is False
    assert record.reconciliation.outcome == "partial"
    assert record.reconciliation.reason == "finish_length"
    assert record.reconciliation.lifecycle == "committed"
    assert record.delivery is not None
    assert record.delivery.state == "partial"
    assert be.recover_local_result(context, record)["delivery"] == "partial"


def test_cli_terminal_completion_needs_no_reconciliation_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = worker()
    context = _context(tmp_path)
    binding = FakeBinding(context=context)
    prepare(tmp_path)
    _seed(tmp_path, context, binding)
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    code = f"print({text_event('ok')!r}); print({finish_event(0)!r})"
    outcome = run_fake(tmp_path, code, context=context)
    record = load_task(tmp_path, TASK_ID)
    assert outcome == 0
    assert record.reconciliation is None
    assert record.delivery is not None
    assert record.delivery.state == "completed"
    assert not _message_gets(binding)


@pytest.mark.parametrize("field", ["attempt", "session", "server", "generation"])
def test_changed_record_identity_does_not_overwrite_or_complete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    module = worker()
    original_load = module.load_task
    changed = False

    def foreign_load(root: Path, task_id: str) -> Any:
        nonlocal changed
        current = original_load(root, task_id)
        if changed:
            if field == "attempt":
                return replace(
                    current, attempt_id="00000000-0000-4000-8000-000000000001"
                )
            if field == "session":
                return replace(current, session="ses_foreign")
            if field == "server":
                return replace(current, server_identity="foreign")
            assert current.reconciliation is not None
            return replace(
                current,
                reconciliation=replace(
                    current.reconciliation,
                    generation=current.reconciliation.generation + 1,
                ),
            )
        return current

    original_observation = worker().record_host_observation

    def mark_before_final_commit(*args: Any, **kwargs: Any) -> None:
        nonlocal changed
        original_observation(*args, **kwargs)
        if kwargs.get("terminal") is True:
            changed = True

    monkeypatch.setattr(module, "load_task", foreign_load)
    monkeypatch.setattr(
        worker_module, "record_host_observation", mark_before_final_commit
    )
    module, binding, context, outcome, directory = _bound(tmp_path, monkeypatch)
    record = load_task(tmp_path, TASK_ID)
    assert outcome == 1
    assert record.session == "ses_prueba"
    assert record.reconciliation is not None
    assert record.reconciliation.lifecycle == "provisional"
    assert record.delivery is not None
    assert record.delivery.state == "pending"
    assert be.recover_local_result(context, record)["status"] == "pending"


def test_completed_record_is_reused_without_new_message_get(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module, binding, context, outcome, directory = _bound(tmp_path, monkeypatch)
    assert outcome == 0
    assert len(_message_gets(binding)) == 1
    second_outcome = run_fake(tmp_path, f"print({_message_event()!r})", context=context)
    assert second_outcome == 0
    assert len(_message_gets(binding)) == 1
    record = load_task(tmp_path, TASK_ID)
    assert record.reconciliation is not None
    assert record.reconciliation.lifecycle == "committed"


def test_local_precheck_failure_persists_no_remote_outcome(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_verify = FakeBinding.verify_owner
    calls = 0

    def fail_precheck(self: FakeBinding, *, timeout: float = 1.0) -> Any:
        nonlocal calls
        calls += 1
        if calls == 4:
            return None
        return original_verify(self, timeout=timeout)

    monkeypatch.setattr(FakeBinding, "verify_owner", fail_precheck)
    _, binding, _, outcome, _ = _bound(tmp_path, monkeypatch)
    record = load_task(tmp_path, TASK_ID)
    assert outcome == 1
    assert not _message_gets(binding)
    assert record.reconciliation is not None
    assert record.reconciliation.phase == "not_attempted"
    assert record.reconciliation.source == "local"
    assert record.reconciliation.outcome is None
    assert record.reconciliation.accepted is None
    assert record.delivery is not None
    assert record.delivery.state == "pending"
