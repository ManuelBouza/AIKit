"""Integración del supervisor con reconciliación terminal por mensaje durable (Task 3)."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import replace
from pathlib import Path
from typing import Any

import host_registry as hr
import pytest
from service_identity import HostContext
from session_store import StoreError, load_task, save_task

from tests.fakes import (
    FakeBinding,
    api_model,
    default_config_sources,
    seed_availability,
)
from tests.test_session_store import TASK_ID, make_record
from tests.test_session_worker import prepare, result, run_fake, worker

NO_CALLS: list[Any] = []


def _collect_no_call(*args: Any, **kwargs: Any) -> None:
    NO_CALLS.append((args, kwargs))


def _seed(root: Path, context: HostContext, binding: FakeBinding) -> None:

    seed_availability(
        context,
        root,
        [api_model("kimi-k3.1-pro", provider="opencode-go", variants=[{"id": "high"}])],
        sources=default_config_sources(),
    )
    record = replace(
        make_record(root),
        server_identity=binding.token,
        previous_attempt_ids=[],
        session=None,
    )
    save_task(root, record)
    hr.reserve_host_attempt(context, record, agent="build")


def _message_event(message_id: str = "msg_1", session: str = "ses_prueba") -> str:
    return json.dumps(
        {
            "type": "text",
            "sessionID": session,
            "messageID": message_id,
            "part": {"type": "text", "text": "ok", "messageID": message_id},
        }
    )


def test_supervisor_reconciles_accepted_to_durable_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")

    calls: list[tuple[str | None, float]] = []
    original_reconcile = module.reconcile_terminal_message

    def fake_reconcile(
        record: Any,
        binding: Any,
        *,
        assistant_message_id: str | None,
        timeout: float,
        **kwargs: Any,
    ) -> Any:
        calls.append((assistant_message_id, timeout))
        return original_reconcile(
            record,
            binding,
            assistant_message_id=assistant_message_id,
            timeout=timeout,
            **kwargs,
        )

    monkeypatch.setattr(module, "reconcile_terminal_message", fake_reconcile)

    outcome = run_fake(tmp_path, f"print({_message_event()!r})", context=context)
    assert outcome == 0
    assert len(calls) == 1
    assert calls[0][0] == "msg_1"
    assert 0 < calls[0][1] <= 10.0
    record = load_task(tmp_path, TASK_ID)
    assert record.delivery is not None
    assert record.delivery.state == "completed"
    assert record.delivery.source == "durable_message"
    report = result(directory)
    assert report["delivery"] == "completed"


def test_supervisor_does_not_reconcile_when_terminal_stream_valid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tests.fakes import text_event

    prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    NO_CALLS.clear()
    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        _collect_no_call,
    )
    payload = (
        text_event("ok")
        + "\n"
        + __import__("json").dumps(
            {
                "type": "step_finish",
                "sessionID": "ses_prueba",
                "messageID": "msg_1",
                "part": {
                    "sessionID": "ses_prueba",
                    "messageID": "msg_1",
                    "reason": "stop",
                },
            }
        )
    )
    run_fake(tmp_path, f"print({payload!r})", context=context)
    assert NO_CALLS == []


def test_supervisor_does_not_reconcile_on_error_stream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    NO_CALLS.clear()
    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        _collect_no_call,
    )
    payload = json.dumps(
        {"type": "error", "sessionID": "ses_prueba", "error": {"message": "boom"}}
    )
    run_fake(tmp_path, f"print({payload!r})", context=context)
    assert NO_CALLS == []


def test_supervisor_does_not_reconcile_missing_message_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    NO_CALLS.clear()
    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        _collect_no_call,
    )
    payload = json.dumps(
        {
            "type": "text",
            "sessionID": "ses_prueba",
            "part": {"type": "text", "text": "ok"},
        }
    )
    run_fake(tmp_path, f"print({payload!r})", context=context)
    assert NO_CALLS == []


def test_supervisor_does_not_reconcile_assistant_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    NO_CALLS.clear()
    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        _collect_no_call,
    )
    payload = json.dumps(
        {
            "type": "text",
            "sessionID": "ses_prueba",
            "messageID": "msg_1",
            "part": {"type": "text", "text": "ok", "messageID": "msg_2"},
        }
    )
    run_fake(tmp_path, f"print({payload!r})", context=context)
    assert NO_CALLS == []


def test_supervisor_reconcile_negative_keeps_pending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")

    from session_backend import TerminalReconciliation

    def negative() -> TerminalReconciliation:
        return TerminalReconciliation(
            False, "uncertain", None, None, "msg_1", "invalid_response", (), True
        )

    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        lambda *a, **k: negative(),
    )
    outcome = run_fake(tmp_path, f"print({_message_event()!r})", context=context)
    assert outcome == 1
    record = load_task(tmp_path, TASK_ID)
    assert record.delivery is not None
    assert record.delivery.state != "completed"


def test_supervisor_reconcile_owner_changed_no_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    original_verify = binding.verify_owner
    counter = {"n": 0}

    def verify(timeout: float = 1.0) -> Any:
        counter["n"] += 1
        if counter["n"] <= 3:
            return original_verify(timeout=timeout)
        return None

    binding.verify_owner = verify  # type: ignore[method-assign]
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    NO_CALLS.clear()
    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        _collect_no_call,
    )
    run_fake(tmp_path, f"print({_message_event()!r})", context=context)
    assert NO_CALLS == []


def _record_owner_checks(binding: FakeBinding) -> list[float]:
    original = binding.verify_owner
    calls: list[float] = []

    def verify(timeout: float = 1.0) -> Any:
        calls.append(timeout)
        return original(timeout=timeout)

    binding.verify_owner = verify  # type: ignore[method-assign]
    return calls


def _accepted_reconciliation(calls: list[float]) -> Any:
    def factory(
        record: Any,
        binding: Any,
        *,
        assistant_message_id: str | None,
        timeout: float,
        **kwargs: Any,
    ) -> Any:
        calls.append(timeout)
        from session_backend import TerminalReconciliation

        return TerminalReconciliation(
            True, "completed", "stop", 123, assistant_message_id, "accepted", (), True
        )

    return factory


class _FakeClock:
    def __init__(self, base: float, after_wait: float) -> None:
        self.base = base
        self.after_wait = after_wait
        self.exited = False

    def monotonic(self) -> float:
        return self.after_wait if self.exited else self.base

    def sleep(self, _seconds: float) -> None:
        return None


class _PipeStream:
    def __init__(self, data: bytes) -> None:
        read_fd, write_fd = os.pipe()
        try:
            os.write(write_fd, data)
        finally:
            os.close(write_fd)
        self._fd = read_fd

    def fileno(self) -> int:
        return self._fd

    def close(self) -> None:
        os.close(self._fd)


class _FakeProcess:
    def __init__(self, clock: _FakeClock, stdout: bytes) -> None:
        self.clock = clock
        self.pid = 1234
        self.returncode: int | None = None
        self._pending_exit = True
        self.stdout: Any = _PipeStream(stdout)
        self.stderr: Any = _PipeStream(b"")
        self.stdin: Any = None

    def poll(self) -> int | None:
        if self._pending_exit:
            self._pending_exit = False
            return None
        self.returncode = 0
        return 0

    def wait(self) -> int:
        self._pending_exit = False
        self.clock.exited = True
        self.returncode = 0
        return 0


def test_supervisor_owner_precheck_respects_remaining_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    # Presupuesto controlado: _seed fija 300s por defecto; la conciliación
    # solo puede aceptar con `remaining` > 0.
    seeded = load_task(tmp_path, TASK_ID)
    save_task(tmp_path, replace(seeded, execution_timeout_seconds=5.0))
    module = worker()
    clock = _FakeClock(base=1000.0, after_wait=1004.8)
    monkeypatch.setattr(module, "time", clock)
    owner_calls = _record_owner_checks(binding)
    process = _FakeProcess(clock, (_message_event() + "\n").encode("ascii"))

    def fake_popen(*args: Any, **kwargs: Any) -> Any:
        return process

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    reconcile_calls: list[float] = []
    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        _accepted_reconciliation(reconcile_calls),
    )
    outcome = run_fake(tmp_path, "print('fake')", context=context)
    assert outcome == 0
    assert len(owner_calls) == 6
    assert owner_calls[3] == pytest.approx(0.2)
    assert owner_calls[4] == pytest.approx(1.0)
    assert len(reconcile_calls) == 1
    assert reconcile_calls[0] == pytest.approx(0.2)
    assert result(directory)["delivery"] == "completed"


def test_budget_expires_during_owner_precheck_without_remote_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    save_task(
        tmp_path, replace(load_task(tmp_path, TASK_ID), execution_timeout_seconds=5.0)
    )
    module = worker()
    clock = _FakeClock(base=1000.0, after_wait=1004.8)
    monkeypatch.setattr(module, "time", clock)
    original = binding.verify_owner
    calls = 0

    def consuming_owner(*, timeout: float = 1.0) -> Any:
        nonlocal calls
        calls += 1
        owner = original(timeout=timeout)
        if calls == 4:
            clock.after_wait = 1005.0
        return owner

    binding.verify_owner = consuming_owner  # type: ignore[method-assign]
    process = _FakeProcess(clock, (_message_event() + "\n").encode("ascii"))
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    assert run_fake(tmp_path, "print('fake')", context=context) == 1
    record = load_task(tmp_path, TASK_ID)
    assert not [
        call for call in binding.request_calls if call[0] == "session.message.get"
    ]
    assert record.reconciliation is not None
    assert record.reconciliation.phase == "not_attempted"
    assert record.reconciliation.reason == "budget_exhausted"
    assert record.reconciliation.source == "local"
    assert record.reconciliation.outcome is None
    assert record.reconciliation.accepted is None
    assert record.delivery is not None
    assert record.delivery.state != "completed"


def test_supervisor_owner_precheck_skipped_without_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    # Presupuesto controlado: _seed fija 300s por defecto.
    seeded = load_task(tmp_path, TASK_ID)
    save_task(tmp_path, replace(seeded, execution_timeout_seconds=5.0))
    module = worker()
    clock = _FakeClock(base=1000.0, after_wait=1005.0)
    monkeypatch.setattr(module, "time", clock)
    owner_calls = _record_owner_checks(binding)
    process = _FakeProcess(clock, (_message_event() + "\n").encode("ascii"))

    def fake_popen(*args: Any, **kwargs: Any) -> Any:
        return process

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    reconcile_calls: list[float] = []
    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        _accepted_reconciliation(reconcile_calls),
    )
    outcome = run_fake(
        tmp_path, "print('fake')", context=context, interrupt=lambda record: True
    )
    assert outcome == 1
    assert len(owner_calls) == 4
    assert len(reconcile_calls) == 0


def test_supervisor_provenance_failure_keeps_prior_delivery_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")

    def failing_false(_ctx: Any, _rec: Any, *, terminal: bool) -> None:
        if not terminal:
            raise StoreError("store_io", "observacion previa fallida")

    monkeypatch.setattr(module, "record_host_observation", failing_false)
    reconcile_calls: list[float] = []
    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        _accepted_reconciliation(reconcile_calls),
    )
    outcome = run_fake(tmp_path, f"print({_message_event()!r})", context=context)
    assert outcome == 1
    assert len(reconcile_calls) == 0
    record = load_task(tmp_path, TASK_ID)
    assert record.delivery is not None
    assert record.delivery.state == "pending"
    assert record.delivery.source == "cli_event"


def test_supervisor_terminal_observation_failure_demotes_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")

    def failing_true(_ctx: Any, _rec: Any, *, terminal: bool) -> None:
        if terminal:
            raise StoreError("store_io", "observacion terminal fallida")

    monkeypatch.setattr(module, "record_host_observation", failing_true)
    reconcile_calls: list[float] = []
    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        _accepted_reconciliation(reconcile_calls),
    )
    outcome = run_fake(tmp_path, f"print({_message_event()!r})", context=context)
    assert outcome == 1
    assert len(reconcile_calls) == 1
    record = load_task(tmp_path, TASK_ID)
    assert record.delivery is not None
    assert record.delivery.state == "pending"
    assert record.delivery.source == "cli_event"
    report = result(directory)
    assert report["status"] == "ok"
    assert report["delivery"] == "completed"


def test_supervisor_reconcile_write_failure_keeps_conservative(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    original_save = module.save_task

    def failing_save(root: Path, record: Any) -> None:
        if record.delivery and record.delivery.state == "completed":
            raise StoreError("store_io", "fallo falso")
        original_save(root, record)

    monkeypatch.setattr(module, "save_task", failing_save)
    outcome = run_fake(tmp_path, f"print({_message_event()!r})", context=context)
    assert outcome == 1
    # Fallo de persistencia: el disco conserva la observación previa y el
    # resultado no declara completed.
    record = load_task(tmp_path, TASK_ID)
    assert record.delivery is not None
    assert record.delivery.state == "pending"
    assert record.delivery.source == "cli_event"
    report = result(directory)
    assert report["status"] == "ok"
    assert report["delivery"] == "completed"


def test_supervisor_context_free_does_not_reconcile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare(tmp_path)
    module = worker()
    NO_CALLS.clear()
    monkeypatch.setattr(
        module,
        "reconcile_terminal_message",
        _collect_no_call,
    )
    run_fake(tmp_path, f"print({_message_event()!r})")
    assert NO_CALLS == []


def test_supervisor_reconcile_timeout_budget_exact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _ctx: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")

    captured: dict[str, float] = {}

    def fake_reconcile(
        record: Any,
        binding: Any,
        *,
        assistant_message_id: str | None,
        timeout: float,
        **kwargs: Any,
    ) -> Any:
        captured["timeout"] = timeout
        from session_backend import TerminalReconciliation

        return TerminalReconciliation(
            True, "completed", "stop", 123, assistant_message_id, "accepted", (), True
        )

    monkeypatch.setattr(module, "reconcile_terminal_message", fake_reconcile)
    run_fake(tmp_path, f"print({_message_event()!r})", context=context)
    assert "timeout" in captured
    assert 0 < captured["timeout"] <= 10.0
