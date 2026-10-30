"""Supervisor real con procesos Python falsos, sin modelos ni red."""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import threading
import time
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest
from session_store import StoreError, load_task, lock_task, save_task

from tests.fakes import finish_event, text_event
from tests.test_session_store import TASK_ID, make_record


def worker() -> ModuleType:
    assert importlib.util.find_spec("session_worker"), "Falta el supervisor incremental"
    return importlib.import_module("session_worker")


def prepare(root: Path, *, timeout: float = 5) -> Path:
    save_task(root, replace(make_record(root), execution_timeout_seconds=timeout))
    directory = root / ".aikit" / "sessions" / TASK_ID
    (directory / "task.txt").write_text("tarea ficticia", encoding="utf-8")
    return directory


def command(code: str) -> list[str]:
    return [sys.executable, "-u", "-c", code]


def run_fake(root: Path, code: str, **kwargs: Any) -> int:
    return int(
        worker().supervise(
            root, TASK_ID, prepare_command=lambda _: command(code), **kwargs
        )
    )


def result(directory: Path) -> dict[str, Any]:
    attempt = make_record(directory).attempt_id
    return cast(
        dict[str, Any],
        json.loads((directory / attempt / "result.json").read_text(encoding="utf-8")),
    )


def test_session_persists_before_client_finishes(tmp_path: Path) -> None:
    worker()
    directory = prepare(tmp_path)
    gate = tmp_path / "release"
    code = f"import pathlib,time; print({text_event('temprano')!r},flush=True)\nwhile not pathlib.Path({str(gate)!r}).exists(): time.sleep(.01)\nprint({finish_event(0)!r})"
    outcome: list[int] = []
    thread = threading.Thread(target=lambda: outcome.append(run_fake(tmp_path, code)))
    thread.start()
    try:
        deadline = time.monotonic() + 5
        while (
            load_task(tmp_path, TASK_ID).session is None
            and thread.is_alive()
            and time.monotonic() < deadline
        ):
            time.sleep(0.01)
        assert load_task(tmp_path, TASK_ID).session == "ses_prueba"
        assert thread.is_alive()
    finally:
        gate.touch()
        thread.join(5)
    assert outcome == [0]
    assert result(directory)["delivery"] == "completed"


def test_fragmented_utf8_and_jsonl_survive(tmp_path: Path) -> None:
    directory = prepare(tmp_path)
    payload = (text_event("mañana ☀") + "\n" + finish_event(0) + "\n").encode()
    code = f"import os\nfor b in {payload!r}: os.write(1,bytes([b]))"
    assert run_fake(tmp_path, code) == 0
    assert result(directory)["summary"] == "mañana ☀"


def test_oversized_stdout_and_stderr_are_drained_and_bounded(tmp_path: Path) -> None:
    directory = prepare(tmp_path)
    code = f"import os; os.write(2,b's'*2200000); os.write(1,b'x'*2200000+b'\\n'); print({text_event('ok')!r}); print({finish_event(0)!r})"
    assert run_fake(tmp_path, code) == 0
    report = result(directory)
    assert report["stdout_truncated"] is True
    assert report["stderr_truncated"] is True
    assert report["line_truncated"] is True
    for name in ("stdout.partial", "stderr.partial"):
        assert (
            directory / make_record(tmp_path).attempt_id / name
        ).stat().st_size == 1048576
    assert report["summary"] == "ok"


@pytest.mark.parametrize(
    ("payload", "exit_code", "delivery"),
    [
        ("invalid-json", 0, "pending"),
        (text_event("parcial"), 0, "partial"),
        (finish_event(0), 0, "pending"),
        (text_event("ok") + "\n" + finish_event(0, session="ses_otro"), 0, "partial"),
        (
            text_event("ok") + "\n" + finish_event(0) + "\n" + text_event("nuevo"),
            0,
            "partial",
        ),
        (text_event("fallo") + "\n" + finish_event(0), 7, "failed"),
    ],
)
def test_exit_is_not_server_or_delivery_evidence(
    tmp_path: Path, payload: str, exit_code: int, delivery: str
) -> None:
    directory = prepare(tmp_path)
    run_fake(tmp_path, f"import sys; print({payload!r}); sys.exit({exit_code})")
    assert result(directory)["delivery"] == delivery
    execution = load_task(tmp_path, TASK_ID).execution
    assert execution is not None
    assert execution.state == "unknown"


def test_deadline_without_control_keeps_draining_and_does_not_kill(
    tmp_path: Path,
) -> None:
    directory = prepare(tmp_path, timeout=0.05)
    gate = tmp_path / "release"
    callbacks: list[str] = []

    def interrupt(record: Any) -> None:
        callbacks.append(record.task_id)
        gate.touch()

    code = f"import pathlib,time; print({text_event('vivo')!r},flush=True)\nwhile not pathlib.Path({str(gate)!r}).exists(): time.sleep(.005)\nprint({finish_event(0)!r})"
    assert run_fake(tmp_path, code, interrupt=interrupt, grace_seconds=0.02) == 0
    assert callbacks == [TASK_ID]
    assert result(directory)["deadline_exceeded"] is True
    assert result(directory)["delivery"] == "completed"


def test_deadline_uses_backend_callback_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = prepare(tmp_path, timeout=0.05)
    module = worker()
    calls: list[str] = []

    def observe_backend(record: Any) -> None:
        calls.append(record.task_id)

    monkeypatch.setattr(module, "worker_interrupt", observe_backend)
    assert run_fake(tmp_path, "import time; time.sleep(.15)", grace_seconds=0) == 1
    assert calls == [TASK_ID]
    report = result(directory)
    assert report["execution"] == "unknown"
    assert "interrupt_unconfirmed" in report["limitations"]
    assert report["delivery"] == "pending"


def test_final_save_failure_still_prints_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    directory = prepare(tmp_path)
    module = worker()
    original = module.save_task

    def failing_save(root: Path, record: Any) -> None:
        if record.delivery and record.delivery.state == "completed":
            raise StoreError("store_io", "fallo falso")
        original(root, record)

    monkeypatch.setattr(module, "save_task", failing_save)
    assert (
        run_fake(
            tmp_path,
            f"print({text_event('recuperable')!r}); print({finish_event(0)!r})",
        )
        == 0
    )
    report = json.loads(capsys.readouterr().out)
    assert report["summary"] == "recuperable"
    assert "record_save_failed" in report["limitations"]
    assert result(directory)["summary"] == "recuperable"


def test_same_attempt_is_never_restarted(tmp_path: Path) -> None:
    prepare(tmp_path)
    run_fake(tmp_path, "print('no terminal')")
    with pytest.raises(StoreError, match="reservado"):
        run_fake(tmp_path, "raise AssertionError('no debe ejecutarse')")


def test_unsafe_task_input_is_rejected(tmp_path: Path) -> None:
    directory = prepare(tmp_path)
    (directory / "task.txt").unlink()
    (directory / "task.txt").mkdir()
    with pytest.raises(StoreError):
        run_fake(tmp_path, "raise AssertionError('no debe ejecutarse')")


@pytest.mark.parametrize("timeout", [None, 0, 3601])
def test_finite_execution_deadline_required(
    tmp_path: Path, timeout: float | None
) -> None:
    prepare(tmp_path)
    record = replace(make_record(tmp_path), execution_timeout_seconds=timeout)
    if timeout == 0:
        # El almacén ya rechaza cero; el worker debe cubrir además None y >3600.
        with pytest.raises(StoreError):
            save_task(tmp_path, record)
        return
    save_task(tmp_path, record)
    with pytest.raises(Exception, match="ejecución|timeout"):
        run_fake(tmp_path, "print('no debe ejecutarse')")


def wait_for(path: Path, timeout: float = 8) -> None:
    end = time.monotonic() + timeout
    while not path.exists() and time.monotonic() < end:
        time.sleep(0.01)
    assert path.exists(), f"No se publicó {path.name}"


def launcher_code(root: Path, fake: str, *, stay: bool = False) -> str:
    scripts = (
        Path(__file__).resolve().parents[1]
        / "skills"
        / "delegating-to-opencode"
        / "scripts"
    )
    supervisor = (
        f"import sys;sys.path.insert(0,{str(scripts)!r});from pathlib import Path;"
        f"from session_worker import supervise;supervise(Path({str(root)!r}),{TASK_ID!r},"
        f"prepare_command=lambda r:{command(fake)!r})"
    )
    code = (
        f"import sys;sys.path.insert(0,{str(scripts)!r});from pathlib import Path;"
        "from session_worker import launch_worker;"
        f"launch_worker(Path({str(root)!r}),{TASK_ID!r},worker_command=lambda r:{command(supervisor)!r});"
    )
    if stay:
        code += (
            f"Path({str(root / 'parent-ready')!r}).touch();import time;time.sleep(30)"
        )
    return code


def test_detached_worker_survives_parent_disconnect_and_wait_timeout(
    tmp_path: Path,
) -> None:
    directory = prepare(tmp_path)
    gate = tmp_path / "release"
    fake = f"import pathlib,time;print({text_event('retenido')!r},flush=True)\nwhile not pathlib.Path({str(gate)!r}).exists(): time.sleep(.005)\nprint({finish_event(0)!r})"
    parent = subprocess.Popen(command(launcher_code(tmp_path, fake, stay=True)))
    try:
        wait_for(tmp_path / "parent-ready")
        with pytest.raises(subprocess.TimeoutExpired):
            parent.wait(0.02)
        parent.terminate()  # Solo el padre falso propio; no supervisor ni CLI.
        parent.wait(5)
        end = time.monotonic() + 8
        while load_task(tmp_path, TASK_ID).session is None and time.monotonic() < end:
            time.sleep(0.01)
        assert load_task(tmp_path, TASK_ID).session == "ses_prueba"
    finally:
        gate.touch()
        if parent.poll() is None:
            parent.terminate()
            parent.wait(5)
    wait_for(directory / make_record(tmp_path).attempt_id / "result.json")
    assert result(directory)["summary"] == "retenido"
    assert result(directory)["delivery"] == "completed"


def test_two_launcher_processes_only_send_one_task(tmp_path: Path) -> None:
    directory = prepare(tmp_path)
    effect = tmp_path / "effects"
    fake = f"from pathlib import Path; f=Path({str(effect)!r}).open('a');f.write('one\\n');f.close();print({text_event('ok')!r});print({finish_event(0)!r})"
    launchers = [
        subprocess.Popen(
            command(launcher_code(tmp_path, fake)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for _ in range(2)
    ]
    outcomes = [process.communicate(timeout=8) for process in launchers]
    assert sorted(process.returncode for process in launchers) == [0, 1], outcomes
    wait_for(directory / make_record(tmp_path).attempt_id / "result.json")
    assert effect.read_text() == "one\n"
    with pytest.raises(StoreError, match="reservado"):
        worker().launch_worker(tmp_path, TASK_ID)


@pytest.mark.parametrize(
    ("change", "code"),
    [
        ({"model": "openai/gpt-falso"}, "provider_not_allowed"),
        ({"reason": " "}, "invalid_record"),
        ({"model": "opencode/inexistente", "variant": None}, "model_unavailable"),
        (
            {"model": "opencode/kimi-k2.5-free", "variant": "inexistente"},
            "model_unavailable",
        ),
    ],
)
def test_supervisor_revalidates_before_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: dict[str, Any], code: str
) -> None:
    from tests.conftest import Harness

    directory = prepare(tmp_path)
    Harness(tmp_path, directory / "task.txt", monkeypatch).fake()
    record = replace(make_record(tmp_path), **change)
    if code == "invalid_record":
        with pytest.raises(StoreError):
            save_task(tmp_path, record)
        return
    save_task(tmp_path, record)
    import delegate

    with pytest.raises(delegate.DelegateError) as caught:
        worker().supervise(tmp_path, TASK_ID)
    assert caught.value.code == code


@pytest.mark.parametrize(
    "suffix",
    [
        '{"type":"error","error":{"message":"secreto ficticio"}}\n',
        "x" * 1100000 + "\n",
    ],
)
def test_unattributed_error_or_oversized_tail_invalidates_terminal(
    tmp_path: Path, suffix: str
) -> None:
    directory = prepare(tmp_path)
    prefix = text_event("parcial") + "\n" + finish_event(0) + "\n"
    # La línea enorme se crea en el hijo; no exceder límite argv de Windows.
    tail = "'x'*1100000+'\\n'" if suffix.startswith("xxx") else repr(suffix)
    run_fake(
        tmp_path,
        f"import os;os.write(1,({prefix!r}).encode());os.write(1,({tail}).encode())",
    )
    assert result(directory)["status"] != "ok"


def test_metadata_journal_never_contains_output_text(tmp_path: Path) -> None:
    directory = prepare(tmp_path)
    run_fake(
        tmp_path,
        f"print({text_event('dato privado ficticio')!r});print({finish_event(0)!r})",
    )
    journal = directory / make_record(tmp_path).attempt_id / "observations.jsonl"
    lines = journal.read_text(encoding="utf-8").splitlines()
    assert 2 <= len(lines) <= 5
    assert "dato privado ficticio" not in journal.read_text(encoding="utf-8")
    assert json.loads(lines[-1])["event"] == "client_exited"


def test_launch_does_not_hold_task_lock_when_starting_child(tmp_path: Path) -> None:
    prepare(tmp_path)

    def child_command(record: Any) -> list[str]:
        with lock_task(tmp_path, TASK_ID):
            return command("print('falso sin inferencia')")

    worker().launch_worker(tmp_path, TASK_ID, worker_command=child_command)


@pytest.mark.parametrize("kind", ["text", "step_finish"])
@pytest.mark.parametrize(
    "identities",
    [
        {"sessionID": "ses_a", "part": {"sessionID": "ses_b"}},
        {"sessionID": "ses_a", "sessionId": "ses_b"},
        {"part": {"sessionID": "ses_a", "sessionId": "ses_b"}},
        {"sessionId": "ses_a", "part": {"sessionId": "ses_b"}},
        {"sessionID": "ses_a", "sessionId": None},
        {"sessionID": "", "sessionId": "ses_a"},
        {"sessionID": "ses_a", "part": {"sessionID": []}},
    ],
)
def test_conflicting_or_invalid_session_identities_never_complete(
    tmp_path: Path, kind: str, identities: dict[str, Any]
) -> None:
    directory = prepare(tmp_path)
    event = {"type": kind, **identities}
    part = dict(event.get("part", {}))
    part.update({"reason": "stop"} if kind == "step_finish" else {"text": "ambiguo"})
    event["part"] = part
    payload = text_event("previo", session="ses_a") + "\n" + json.dumps(event)
    if kind == "text":
        # Una contradicción en actividad no se borra por un terminal posterior.
        payload += "\n" + finish_event(0, session="ses_a")
    run_fake(tmp_path, f"print({payload!r})")
    report = result(directory)
    assert report["status"] == "pending"
    assert report["delivery"] == "partial"
    assert "session_mismatch" in report["limitations"]
    assert report["session"] == "ses_a"


def test_matching_session_aliases_can_complete(tmp_path: Path) -> None:
    directory = prepare(tmp_path)
    terminal = {
        "type": "step_finish",
        "sessionID": "ses_a",
        "sessionId": "ses_a",
        "part": {"sessionID": "ses_a", "sessionId": "ses_a", "reason": "stop"},
    }
    payload = text_event("coherente", session="ses_a") + "\n" + json.dumps(terminal)
    assert run_fake(tmp_path, f"print({payload!r})") == 0
    assert result(directory)["delivery"] == "completed"
