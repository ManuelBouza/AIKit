from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import delegate
import host_registry as hr
import pytest
import session_worker as sw
from service_identity import HostContext, ServiceError
from session_store import StoreError, load_task, save_task
from session_stream import open_artifact

from tests.fakes import finish_event, text_event
from tests.test_session_store import make_record


def test_supervise_requires_valid_task(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    with pytest.raises(StoreError):
        sw.supervise(root, "not-a-uuid")


def test_bound_supervisor_has_explicit_context_contract() -> None:
    import inspect

    assert "context" in inspect.signature(sw.supervise).parameters
    assert "context" in inspect.signature(sw.launch_worker).parameters


TOKEN = "aikit-owner-v1-" + "a" * 64


class Binding:
    token = TOKEN
    registration = type("Registration", (), {"url": "http://127.0.0.1:9876/"})()
    expected_owner = object()

    def __init__(self) -> None:
        self.closed = False
        self.valid = True
        self.restricted = True

    def verify_owner(self, **kwargs: Any) -> object | None:
        return self.expected_owner if self.valid else None

    def config_sources(self, project: Path, **kwargs: Any) -> object:
        from tests.test_restrictions import PROVIDER_DENY, TOOL_DENY, document

        return (
            [document({"policies": [PROVIDER_DENY, TOOL_DENY]})]
            if self.restricted
            else {}
        )

    def child_environment(self, base: Any) -> dict[str, str]:
        return {**base, "OPENCODE_PASSWORD": "test-secret"}

    def close(self) -> None:
        self.closed = True


def prepared(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[HostContext, Any, Binding]:
    root = tmp_path / "project"
    root.mkdir()
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    record = replace(
        make_record(root),
        server_identity=TOKEN,
        previous_attempt_ids=[],
        execution_timeout_seconds=2,
    )
    save_task(root, record)
    (root / ".aikit" / "sessions" / record.task_id / "task.txt").write_text(
        "prompt-private"
    )
    binding = Binding()
    monkeypatch.setattr(sw, "discover_existing", lambda ctx: binding)
    monkeypatch.setattr(delegate, "find_opencode", lambda: "fake-opencode")
    return context, record, binding


def test_host_reserved_before_project_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ctx, record, _ = prepared(tmp_path, monkeypatch)
    root = Path(record.cwd)
    before = (
        root / ".aikit" / "sessions" / record.task_id / "record.json"
    ).read_bytes()
    monkeypatch.setattr(
        sw, "save_task", lambda *a: (_ for _ in ()).throw(OSError("disk"))
    )
    with pytest.raises(OSError, match="disk"):
        sw.launch_worker(root, record.task_id, context=ctx)
    assert (
        hr.load_host_task(ctx, record.task_id).current_attempt_id == record.attempt_id
    )
    assert (
        root / ".aikit" / "sessions" / record.task_id / "record.json"
    ).read_bytes() == before
    with pytest.raises(hr.HostRegistryError):
        sw.launch_worker(root, record.task_id, context=ctx)


def test_bound_child_credential_only_in_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ctx, record, binding = prepared(tmp_path, monkeypatch)
    hr.reserve_host_attempt(ctx, record, agent="plan")
    captured: dict[str, Any] = {}
    popen = subprocess.Popen

    def child(argv: Any, **kwargs: Any) -> Any:
        captured.update(argv=argv, env=kwargs.get("env"))
        # Actual isolated Python child proves credential propagation and drain.
        assert kwargs["env"]["OPENCODE_PASSWORD"] == "test-secret"
        code = f"import os; assert os.environ['OPENCODE_PASSWORD']=='test-secret'; print({text_event('ok')!r}); print({finish_event(0)!r})"
        return popen([sys.executable, "-c", code], **kwargs)

    monkeypatch.setattr(subprocess, "Popen", child)
    assert sw.supervise(Path(record.cwd), record.task_id, context=ctx) == 0
    assert "--server" in captured["argv"]
    assert "--standalone" not in captured["argv"]
    assert captured["argv"][captured["argv"].index("--agent") + 1] == "plan"
    assert "test-secret" not in repr(captured["argv"])
    assert os.environ.get("OPENCODE_PASSWORD") != "test-secret"
    loaded = load_task(Path(record.cwd), record.task_id)
    assert hr.verify_provenance(ctx, loaded).session_id == "ses_prueba"
    assert binding.closed
    raw = hr._host_file(ctx, record.task_id).read_text()
    assert "prompt-private" not in raw
    assert "test-secret" not in raw
    assert '"summary"' not in raw


@pytest.mark.parametrize("condition", ["rotated", "unsafe", "missing"])
def test_bound_preflight_failure_never_starts_client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, condition: str
) -> None:
    ctx, record, binding = prepared(tmp_path, monkeypatch)
    if condition != "missing":
        hr.reserve_host_attempt(ctx, record, agent="build")
    binding.valid = condition != "rotated"
    binding.restricted = condition != "unsafe"
    monkeypatch.setattr(
        subprocess,
        "Popen",
        lambda *a, **k: pytest.fail("no client on failed preflight"),
    )
    with pytest.raises(
        (hr.HostRegistryError, ServiceError, delegate.DelegateError)
    ) as exc:
        sw.supervise(Path(record.cwd), record.task_id, context=ctx)
    assert not isinstance(exc.value, (AttributeError, TypeError))


def test_session_host_write_failure_keeps_output_and_project_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ctx, record, _ = prepared(tmp_path, monkeypatch)
    hr.reserve_host_attempt(ctx, record, agent="build")
    before = hr._host_file(ctx, record.task_id).read_bytes()
    monkeypatch.setattr(
        sw,
        "record_host_session",
        lambda *a: (_ for _ in ()).throw(hr.HostRegistryError("host_io")),
    )
    code = f"print({text_event('recoverable')!r}); print({finish_event(0)!r})"
    assert (
        sw.supervise(
            Path(record.cwd),
            record.task_id,
            context=ctx,
            prepare_command=lambda _: [sys.executable, "-c", code],
        )
        == 1
    )
    assert load_task(Path(record.cwd), record.task_id).session is None
    # Host remains reserved/client_started, never publishes an unproven session.
    assert hr.load_host_task(ctx, record.task_id).attempts[-1].session_id is None
    directory = (
        Path(record.cwd) / ".aikit" / "sessions" / record.task_id / record.attempt_id
    )
    assert b"recoverable" in (directory / "stdout.partial").read_bytes()
    assert json.loads((directory / "result.json").read_text())["status"] == "pending"
    assert before


def test_host_session_precedes_failed_project_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ctx, record, _ = prepared(tmp_path, monkeypatch)
    hr.reserve_host_attempt(ctx, record, agent="build")
    original = save_task

    def save(root: Path, value: Any) -> None:
        if value.session:
            assert (
                hr.load_host_task(ctx, value.task_id).attempts[-1].session_id
                == value.session
            )
            raise OSError("project failure")
        original(root, value)

    monkeypatch.setattr(sw, "save_task", save)
    code = f"print({text_event('recoverable')!r}); print({finish_event(0)!r})"
    assert (
        sw.supervise(
            Path(record.cwd),
            record.task_id,
            context=ctx,
            prepare_command=lambda _: [sys.executable, "-c", code],
        )
        == 1
    )
    on_disk = load_task(Path(record.cwd), record.task_id)
    assert on_disk.session is None
    assert (
        hr.load_host_task(ctx, record.task_id).attempts[-1].session_id == "ses_prueba"
    )
    with pytest.raises(hr.HostRegistryError):
        hr.verify_provenance(ctx, on_disk)


def test_interrupt_uses_same_binding_and_verified_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ctx, record, binding = prepared(tmp_path, monkeypatch)
    record.execution_timeout_seconds = 0.05
    save_task(Path(record.cwd), record)
    hr.reserve_host_attempt(ctx, record, agent="build")
    seen = []

    def interrupt(value: Any, *, binding: Any) -> Any:
        hr.verify_provenance(ctx, value)
        seen.append(binding)
        return type("Outcome", (), {"confirmed": True})()

    monkeypatch.setattr(sw, "interrupt_session", interrupt)
    code = f"import time; print({text_event('partial')!r},flush=True); time.sleep(.2)"
    sw.supervise(
        Path(record.cwd),
        record.task_id,
        context=ctx,
        prepare_command=lambda _: [sys.executable, "-c", code],
        grace_seconds=0,
    )
    assert seen == [binding]


def test_parent_can_exit_while_supervisor_publishes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess
    import time

    ctx, record, _ = prepared(tmp_path, monkeypatch)
    repo = str(Path.cwd())
    scripts = str(Path(sw.__file__).parent)
    # Seams remain local Python test code; no production flags or env bypass.
    client_code = f"import time; time.sleep(.2); print({text_event('after-parent')!r}); print({finish_event(0)!r})"
    child_code = f"""
import sys
from pathlib import Path
sys.path[:0]=[{scripts!r},{repo!r}]
import session_worker as sw
import delegate
from tests.test_bound_worker import Binding
from service_identity import HostContext
sw.discover_existing=lambda ctx: Binding()
delegate.find_opencode=lambda: 'fake-opencode'
ctx=HostContext(Path({str(ctx.opencode_registration)!r}),Path({str(ctx.aikit_state)!r}),'2.2.0')
sw.supervise(Path({record.cwd!r}),{record.task_id!r},context=ctx,prepare_command=lambda r:[sys.executable,'-c',{client_code!r}])
"""
    launcher = f"""
import sys,os
from pathlib import Path
sys.path[:0]=[{scripts!r},{repo!r}]
import session_worker as sw
from service_identity import HostContext
ctx=HostContext(Path({str(ctx.opencode_registration)!r}),Path({str(ctx.aikit_state)!r}),'2.2.0')
sw.launch_worker(Path({record.cwd!r}),{record.task_id!r},context=ctx,worker_command=lambda r:[sys.executable,'-c',{child_code!r}])
os._exit(0)
"""
    options: dict[str, Any] = (
        {"creationflags": subprocess.CREATE_NO_WINDOW}
        if sys.platform == "win32"
        else {}
    )
    parent = subprocess.run(
        [sys.executable, "-c", launcher], capture_output=True, timeout=10, **options
    )
    assert parent.returncode == 0, parent.stderr.decode()
    result = (
        Path(record.cwd)
        / ".aikit"
        / "sessions"
        / record.task_id
        / record.attempt_id
        / "result.json"
    )
    deadline = time.monotonic() + 10
    while not result.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert json.loads(result.read_text())["delivery"] == "completed"
    observed = load_task(Path(record.cwd), record.task_id)
    assert hr.verify_provenance(ctx, observed).session_id == "ses_prueba"
    observed.server_identity = "aikit-owner-v1-" + "b" * 64
    with pytest.raises(hr.HostRegistryError):
        hr.verify_provenance(ctx, observed)


def test_terminal_or_uncertain_host_observation_is_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ctx, record, _ = prepared(tmp_path, monkeypatch)
    hr.reserve_host_attempt(ctx, record, agent="build")
    code = f"print({text_event('done')!r}); print({finish_event(0)!r})"
    assert (
        sw.supervise(
            Path(record.cwd),
            record.task_id,
            context=ctx,
            prepare_command=lambda _: [sys.executable, "-c", code],
        )
        == 0
    )
    assert (
        hr.load_host_task(ctx, record.task_id).attempts[-1].phase == "terminal_observed"
    )


def test_failure_only_at_final_project_write_returns_uncertain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ctx, record, _ = prepared(tmp_path, monkeypatch)
    hr.reserve_host_attempt(ctx, record, agent="build")

    def save(root: Path, value: Any) -> None:
        if value.delivery.source == "cli_terminal":
            raise OSError("final write")
        save_task(root, value)

    monkeypatch.setattr(sw, "save_task", save)
    code = f"print({text_event('done')!r}); print({finish_event(0)!r})"
    assert (
        sw.supervise(
            Path(record.cwd),
            record.task_id,
            context=ctx,
            prepare_command=lambda _: [sys.executable, "-c", code],
        )
        == 1
    )
    assert hr.load_host_task(ctx, record.task_id).attempts[-1].phase == "uncertain"


def test_result_write_failure_keeps_host_uncertain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ctx, record, _ = prepared(tmp_path, monkeypatch)
    hr.reserve_host_attempt(ctx, record, agent="build")
    original = open_artifact

    def artifact(path: Path) -> Any:
        if path.name == "result.json":
            raise OSError("result disk")
        return original(path)

    monkeypatch.setattr(sw, "open_artifact", artifact)
    code = f"print({text_event('recoverable')!r}); print({finish_event(0)!r})"
    assert (
        sw.supervise(
            Path(record.cwd),
            record.task_id,
            context=ctx,
            prepare_command=lambda _: [sys.executable, "-c", code],
        )
        == 1
    )
    assert hr.load_host_task(ctx, record.task_id).attempts[-1].phase == "uncertain"
