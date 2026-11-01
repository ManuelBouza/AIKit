"""Preflight ligado, reserva y recuperación local sin inferencia adicional."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, cast

import delegate
import pytest
from service_connection import BoundLaunch
from service_identity import HostContext, ServiceError
from session_store import DeliveryState, Role, load_task

from tests.fakes import (
    DEFAULT_MODEL,
    FakeBinding,
    api_model,
    default_config_sources,
    finish_event,
    text_event,
)


def _mock_supervisor_process() -> Any:
    """Crea un mock de proceso supervisor con método communicate()."""
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.communicate.return_value = (None, None)
    return mock


def make_context(tmp_path: Path) -> HostContext:
    return HostContext(
        opencode_registration=tmp_path / "registration.json",
        aikit_state=tmp_path / "host-state",
        expected_version="2.2.0",
    )


def install(
    monkeypatch: pytest.MonkeyPatch,
    context: HostContext,
    binding: FakeBinding,
) -> None:
    monkeypatch.setattr(delegate, "resolve_host_context", lambda: context)
    monkeypatch.setattr(
        delegate, "discover_existing", lambda _context, **kwargs: binding
    )
    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")


def prepare(
    project: Path,
    context: HostContext,
    *,
    task: str = "Tarea literal",
    model: str = DEFAULT_MODEL,
    variant: str | None = None,
    reason: str = "motivo acotado",
    agent: str = "build",
    timeout: float = 30,
    role: Role = "implementer",
) -> BoundLaunch:
    return delegate._prepare_run(
        project,
        lambda: task,
        model,
        variant,
        reason,
        agent,
        timeout,
        role=role,
        context=context,
    )


def attempt_directory(record: Any) -> Path:
    root = Path(str(record.cwd))
    return root / ".aikit" / "sessions" / str(record.task_id) / str(record.attempt_id)


def write_terminal(
    record: Any,
    stdout: str,
    *,
    returncode: int = 0,
    delivery: str | None = None,
    publish: bool = True,
) -> None:
    summary, session, _cost, errors = delegate.parse_events(stdout)
    terminal = '"type": "step_finish"' in stdout or '"type":"step_finish"' in stdout
    if delivery is None:
        delivery = (
            "failed"
            if returncode != 0 or errors
            else "completed"
            if terminal and summary
            else "partial"
            if summary
            else "pending"
        )
    report = {
        "status": "ok"
        if delivery == "completed"
        else "error"
        if delivery == "failed"
        else "pending",
        "task_id": record.task_id,
        "attempt_id": record.attempt_id,
        "session": session,
        "delivery": delivery,
        "execution": "unknown",
        "client_exit_code": returncode,
        "summary": summary,
        "deadline_exceeded": False,
        "limitations": [],
    }
    if publish:
        from host_registry import record_host_observation, record_host_session
        from session_store import DeliveryObservation, save_task

        context = make_context(Path(record.cwd).parent)
        if session is not None:
            record_host_session(context, record, session)
            record.session = session
        record.delivery = DeliveryObservation(
            cast(DeliveryState, delivery),
            "fake_supervisor",
            "2026-10-31T00:00:00+00:00",
        )
        save_task(Path(record.cwd), record)
        record_host_observation(context, record, terminal=delivery == "completed")
    directory = attempt_directory(record)
    (directory / "stdout.partial").write_text(stdout, encoding="utf-8")
    (directory / "result.json").write_text(json.dumps(report), encoding="utf-8")


def test_prepare_returns_bound_launch_and_uses_one_binding_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(context=context)
    install(monkeypatch, context, binding)

    prepared = prepare(project, context, task="prompt-privado", reason="motivo-privado")

    assert isinstance(prepared, BoundLaunch)
    assert id(prepared.binding) == id(binding)
    assert prepared.project == project.resolve()
    assert [kind for kind, _ in binding.calls] == [
        "config",
        "openapi",
        "integrations",
        "catalog",
        "usage",
    ]
    assert {path for _, path in binding.calls if path is not None} == {
        project.resolve()
    }
    assert prepared.argv[6:10] == [
        "--server",
        binding.registration.url,
        "--format",
        "json",
    ]
    assert "--standalone" not in prepared.argv
    assert prepared.argv[-1] == delegate.TASK_PREFIX + "prompt-privado"
    rendered = repr(prepared) + json.dumps(prepared.metadata())
    for secret in (
        "prompt-privado",
        "motivo-privado",
        binding.registration.url,
        "OPENCODE_PASSWORD",
    ):
        assert secret not in rendered


def test_unsafe_certificate_stops_before_catalog_and_send(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(context=context, sources=[])
    install(monkeypatch, context, binding)
    monkeypatch.setattr(
        subprocess, "Popen", lambda *a, **k: pytest.fail("no debe arrancar nada")
    )

    with pytest.raises(delegate.DelegateError) as error:
        prepare(project, context)

    assert error.value.code == "unsafe_configuration"
    assert binding.catalog_calls == []
    assert binding.closed is True


def test_direct_openai_is_rejected_before_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(context=context)
    install(monkeypatch, context, binding)

    with pytest.raises(delegate.DelegateError) as error:
        prepare(project, context, model="openai/gpt-5")

    assert error.value.code == "provider_not_allowed"
    assert binding.calls == []


def test_catalog_location_must_match_the_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(
        context=context, catalog_location=str(tmp_path / "otro-proyecto")
    )
    install(monkeypatch, context, binding)

    with pytest.raises(delegate.DelegateError) as error:
        prepare(project, context)

    assert error.value.code == "catalog_capability_unavailable"
    assert binding.closed is True


def test_doctor_queries_without_certificate_but_run_rejects_unsafe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(
        context=context,
        sources=[],
        catalog=[
            api_model("gpt-5.3", provider="openai"),
            api_model("seguro", provider="opencode"),
        ],
    )
    install(monkeypatch, context, binding)

    catalog = delegate.doctor(project, timeout=30)

    assert catalog["status"] == "ok"
    assert [item["model"] for item in catalog["catalog"]] == ["opencode/seguro"]
    assert binding.config_calls == [project.resolve()]

    fresh = FakeBinding(context=context, sources=[], catalog=binding.catalog)
    monkeypatch.setattr(delegate, "discover_existing", lambda _context, **kwargs: fresh)

    with pytest.raises(delegate.DelegateError) as error:
        prepare(project, context)

    assert error.value.code == "unsafe_configuration"
    assert fresh.catalog_calls == []


@pytest.mark.parametrize("entrypoint", ["doctor", "run"])
def test_service_unavailable_returns_without_starting_anything(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, entrypoint: str
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    monkeypatch.setattr(delegate, "resolve_host_context", lambda: context)

    def unavailable(_context: HostContext, **kwargs: Any) -> Any:
        raise ServiceError("service_unavailable", "Servicio no disponible.")

    monkeypatch.setattr(delegate, "discover_existing", unavailable)
    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")
    monkeypatch.setattr(
        subprocess, "Popen", lambda *a, **k: pytest.fail("no debe arrancar nada")
    )

    if entrypoint == "doctor":
        result = delegate.doctor(project, timeout=30)
    else:
        result = delegate.run_text_task(
            project,
            "Tarea",
            DEFAULT_MODEL,
            None,
            "motivo",
            "build",
            30,
        )

    assert result["status"] == "error"
    assert result["code"] == "service_unavailable"


def test_execute_bound_reserves_host_before_project_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import bound_execution
    from host_registry import load_host_task

    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(context=context)
    install(monkeypatch, context, binding)
    prepared = prepare(project, context)
    launches: list[Any] = []
    original_save = bound_execution.save_task

    def save_after_host(root: Path, record: Any) -> None:
        host = load_host_task(context, record.task_id)
        assert host.current_attempt_id == record.attempt_id
        original_save(root, record)

    def launch(value: Any, record: Any, *, context: HostContext) -> subprocess.Popen:  # type: ignore
        launches.append(value)
        write_terminal(record, text_event("listo") + "\n" + finish_event(0))
        # Return a mock process with communicate method
        from unittest.mock import MagicMock

        mock_process = MagicMock()
        mock_process.communicate.return_value = (None, None)
        return mock_process

    monkeypatch.setattr(bound_execution, "save_task", save_after_host)
    monkeypatch.setattr(bound_execution, "_launch_supervisor", launch)

    result = bound_execution.execute_bound(prepared, context=context, wait_seconds=2)

    assert result["status"] == "ok"
    assert result["summary"] == "listo"
    assert len(launches) == 1
    assert binding.closed is True
    record = load_task(project, result["task_id"])
    assert record.attempt_id == result["attempt_id"]
    assert (
        load_host_task(context, record.task_id).attempts[-1].phase
        == "terminal_observed"
    )


def test_execute_bound_revalidates_after_reservation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import bound_execution
    from host_registry import load_host_task

    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(context=context)
    install(monkeypatch, context, binding)
    prepared = prepare(project, context)
    binding.valid = False
    monkeypatch.setattr(
        bound_execution,
        "_launch_supervisor",
        lambda *a, **k: pytest.fail("no debe enviar tras cambiar el propietario"),
    )

    result = bound_execution.execute_bound(prepared, context=context, wait_seconds=1)

    assert result["status"] == "error"
    assert result["code"] in {"owner_mismatch", "service_unavailable"}
    record = load_task(project, result["task_id"])
    assert (
        load_host_task(context, record.task_id).current_attempt_id == record.attempt_id
    )


def test_pending_is_tracked_and_recovery_does_not_launch_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess

    import bound_execution
    from host_registry import load_host_task

    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(context=context)
    install(monkeypatch, context, binding)
    prepared = prepare(project, context)
    launches: list[Any] = []

    def slow_launch(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        launches.append(record)
        # Return a mock process that times out on communicate
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.side_effect = subprocess.TimeoutExpired("cmd", 0.05)
        return mock

    monkeypatch.setattr(bound_execution, "_launch_supervisor", slow_launch)

    result = bound_execution.execute_bound(prepared, context=context, wait_seconds=0.05)

    assert result["status"] == "pending"
    assert result["task_id"]
    assert result["attempt_id"]
    assert result["uncertain"] is True
    assert len(launches) == 1
    record = load_task(project, result["task_id"])
    assert (
        load_host_task(context, record.task_id).current_attempt_id == record.attempt_id
    )

    recovered = bound_execution.recover_local_result(context, record)

    assert recovered["status"] == "pending"
    assert recovered["task_id"] == result["task_id"]
    assert recovered["attempt_id"] == result["attempt_id"]
    assert len(launches) == 1


def test_recover_local_result_reads_terminal_without_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    import bound_execution

    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(context=context)
    install(monkeypatch, context, binding)
    prepared = prepare(project, context)

    def launch_with_terminal(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        write_terminal(record, text_event("recuperado") + "\n" + finish_event(0))
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(bound_execution, "_launch_supervisor", launch_with_terminal)
    result = bound_execution.execute_bound(prepared, context=context, wait_seconds=2)
    binding.verify_owner = lambda **kwargs: pytest.fail("recuperar no usa binding")  # type: ignore[method-assign]

    recovered = bound_execution.recover_local_result(
        context, load_task(project, result["task_id"])
    )

    assert recovered["status"] == "ok"
    assert recovered["summary"] == "recuperado"
    assert recovered["task_id"] == result["task_id"]


def test_free_limit_preserves_tracking_and_hides_secret(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    import bound_execution

    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(context=context)
    install(monkeypatch, context, binding)
    prepared = prepare(project, context)
    output = json.dumps(
        {
            "type": "error",
            "error": {"type": "provider.free-limit", "message": "TOKEN=privado"},
        }
    )

    def launch_with_terminal(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        write_terminal(record, output)
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(bound_execution, "_launch_supervisor", launch_with_terminal)

    result = bound_execution.execute_bound(prepared, context=context, wait_seconds=2)

    assert result["status"] == "pending"
    assert result["code"] == "free_limit_reached"
    assert result.get("fallback") != "reselect"
    assert result["uncertain"] is True
    assert result["task_id"]
    assert result["attempt_id"]
    assert "privado" not in json.dumps(result)


def test_role_is_reserved_in_host_and_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    import bound_execution
    from host_registry import load_host_task

    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(context=context)
    install(monkeypatch, context, binding)
    prepared = prepare(project, context, role="reviewer")

    def launch_with_terminal(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        write_terminal(record, text_event("revisado") + "\n" + finish_event(0))
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(bound_execution, "_launch_supervisor", launch_with_terminal)

    result = bound_execution.execute_bound(prepared, context=context, wait_seconds=2)

    record = load_task(project, result["task_id"])
    host = load_host_task(context, record.task_id)
    assert record.role == "reviewer"
    assert host.role == "reviewer"
    assert host.attempts[-1].role == "reviewer"


def test_client_death_does_not_kill_the_detached_worker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import bound_execution

    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    binding = FakeBinding(context=context)
    install(monkeypatch, context, binding)
    prepared = prepare(project, context)
    created: list[subprocess.Popen[bytes]] = []

    def launch(value: Any, record: Any, *, context: HostContext) -> subprocess.Popen:  # type: ignore
        scripts = str(Path(delegate.__file__).parent)
        repo = str(Path.cwd())
        code = (
            "import sys,time; from pathlib import Path;"
            f"sys.path[:0]=[{scripts!r},{repo!r}];"
            "from session_store import load_task; from tests.test_bound_execution import write_terminal;"
            f"time.sleep(.3); r=load_task(Path({record.cwd!r}),{record.task_id!r});"
            f"write_terminal(r,{(text_event('tardio', session='ses_tarde') + 'chrnewlineplaceholder' + finish_event(0, session='ses_tarde'))!r}.replace('chrnewlineplaceholder',chr(10)))"
        )
        options: dict[str, Any] = (
            {"creationflags": subprocess.CREATE_NO_WINDOW}
            if sys.platform == "win32"
            else {}
        )
        proc = subprocess.Popen(
            [sys.executable, "-c", code],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **options,
        )
        created.append(proc)
        return proc

    monkeypatch.setattr(bound_execution, "_launch_supervisor", launch)
    result = bound_execution.execute_bound(prepared, context=context, wait_seconds=0.05)

    assert result["status"] == "pending"
    target = attempt_directory(load_task(project, result["task_id"])) / "result.json"
    deadline = time.monotonic() + 5
    while not target.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert target.exists()
    assert created
    assert created[0].wait(timeout=5) == 0
    recovered = bound_execution.recover_local_result(
        context, load_task(project, result["task_id"])
    )
    assert recovered["status"] == "ok"
    assert recovered["summary"] == "tardio"


def test_default_config_sources_are_certified(tmp_path: Path) -> None:
    import restrictions

    assert restrictions.configuration_is_restricted(default_config_sources())
    assert os.path.isabs(str(tmp_path))


def test_reserved_host_does_not_certify_forged_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    launch = prepare(project, ctx)

    def launch_forged(
        prepared: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        write_terminal(
            record, text_event("forged") + "\n" + finish_event(0), publish=False
        )
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(be, "_launch_supervisor", launch_forged)
    result = be.execute_bound(launch, context=ctx, wait_seconds=0)
    assert result["status"] == "pending"
    assert result["uncertain"] is True


def test_same_prepared_attempt_is_not_submitted_twice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    launch = prepare(project, ctx)
    launched = []

    def slow_launch(
        prepared: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        launched.append(record)
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.side_effect = subprocess.TimeoutExpired("cmd", 0)
        return mock

    monkeypatch.setattr(be, "_launch_supervisor", slow_launch)
    first = be.execute_bound(launch, context=ctx, wait_seconds=0)
    second = be.execute_bound(launch, context=ctx, wait_seconds=0)
    assert first["task_id"] == second["task_id"]
    assert first["attempt_id"] == second["attempt_id"]
    assert len(launched) == 1


def test_quota_without_correlated_rejection_cannot_release_uncertainty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    launch = prepare(project, ctx)
    output = json.dumps(
        {
            "type": "error",
            "error": {"type": "provider.free-limit", "message": "private"},
        }
    )

    def launch_quota(
        prepared: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        write_terminal(record, output)
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(be, "_launch_supervisor", launch_quota)
    result = be.execute_bound(launch, context=ctx, wait_seconds=0)
    assert result["status"] == "pending"
    assert result.get("fallback") != "reselect"
    assert result["uncertain"] is True


def test_public_launch_hands_prompt_to_supervisor_in_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import io

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx, task="literal-unique-prompt-ñ")
    seen: dict[str, Any] = {}

    class Buffer(io.BytesIO):
        def close(self) -> None:
            seen["payload"] = self.getvalue()
            super().close()

    class Child:
        def __init__(self, argv: Any, **kwargs: Any) -> None:
            seen.update(argv=argv, kwargs=kwargs)
            self.stdin = Buffer()
            self.pid = 12345

        def wait(self) -> int:
            return 0

        def communicate(self, timeout: float | None = None) -> tuple[None, None]:
            return (None, None)

    monkeypatch.setattr(subprocess, "Popen", Child)
    result = be.execute_bound(prepared, context=ctx, wait_seconds=0)
    assert result["status"] == "pending"
    assert seen["kwargs"]["stdin"] == subprocess.PIPE
    assert "literal-unique-prompt" not in repr(seen["argv"])
    assert "--task-stdin" in seen["argv"]
    assert seen["payload"] == prepared.task.encode("utf-8")
    assert not list((project / ".aikit").rglob("task.txt"))


def test_preflight_queries_share_ten_second_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import types

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    now = [0.0]
    budgets = []

    def config(project: Path, *, timeout: float) -> object:
        budgets.append(timeout)
        now[0] = 8.0
        return default_config_sources()

    def catalog(project: Path, *, timeout: float) -> object:
        budgets.append(timeout)
        return {"location": {"directory": str(project)}, "data": [api_model()]}

    monkeypatch.setattr(binding, "config_sources", config)
    monkeypatch.setattr(binding, "model_catalog", catalog)
    monkeypatch.setattr(
        delegate, "time", types.SimpleNamespace(monotonic=lambda: now[0]), raising=False
    )
    prepared = prepare(project, ctx, timeout=300)
    assert 0 < budgets[0] <= 10
    assert 0 < budgets[1] <= 2
    prepared.binding.close()


def test_unexpected_disk_failure_is_tracked_without_leaking_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx)

    def broken(*args: Any, **kwargs: Any) -> Any:
        raise OSError("secret-registration-content")

    monkeypatch.setattr(be, "reserve_host_attempt", broken)
    result = be.execute_bound(prepared, context=ctx, wait_seconds=0)
    assert result["status"] in {"error", "pending"}
    assert result["task_id"]
    assert result["attempt_id"]
    assert "secret-registration-content" not in json.dumps(result)
    assert binding.closed


@pytest.mark.skipif(sys.platform != "win32", reason="Binding acredita nacimiento Win32")
def test_integrated_http_supervisor_pipe_and_local_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nucleo real; HTTP/CLI ficticios propios, sin modelos ni perfil del usuario."""
    import base64
    import http.server
    import threading
    import urllib.request
    from urllib.parse import parse_qs, urlsplit

    import bound_execution as be
    import service_connection as sc
    import session_worker as sw

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    submissions = []
    requests = []
    prompt = '--literal "comillas" \u00f1 & | >'

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args: Any) -> None:
            return

        def do_GET(self) -> None:  # noqa: N802
            path = urlsplit(self.path).path
            requests.append(path)
            if path == "/api/info":
                body: Any = {"pid": os.getpid(), "version": "2.2.0"}
            elif path == "/api/config":
                body = default_config_sources()
            elif path == "/api/model":
                directory = parse_qs(urlsplit(self.path).query)["location[directory]"][
                    0
                ]
                body = {"location": {"directory": directory}, "data": [api_model()]}
            else:
                body = {"unrelated_session": "still_running"}
            raw = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self) -> None:  # noqa: N802
            expected = (
                "Basic " + base64.b64encode(b"opencode:test-only-password").decode()
            )
            assert self.headers.get("Authorization") == expected
            submissions.append(
                self.rfile.read(int(self.headers["Content-Length"])).decode()
            )
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/"
    ctx.opencode_registration.write_text(
        json.dumps(
            {
                "id": "fake-own-service",
                "url": url,
                "pid": os.getpid(),
                "version": "2.2.0",
                "password": "test-only-password",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(delegate, "discover_existing", sc.discover_existing)
    monkeypatch.setattr(delegate, "find_opencode", lambda: sys.executable)
    scripts = str(Path(delegate.__file__).parent)
    client_code = (
        "import os,sys,time,urllib.request,base64;time.sleep(.15);"
        f"r=urllib.request.Request({url + 'fake-submit'!r},data=sys.argv[1].encode(),method='POST');"
        "r.add_header('Authorization','Basic '+base64.b64encode(('opencode:'+os.environ['OPENCODE_PASSWORD']).encode()).decode());"
        "urllib.request.urlopen(r,timeout=3).read();"
        f"print({text_event('literal-ok')!r});print({finish_event(0)!r})"
    )
    supervisor_code = f"""
import sys
from pathlib import Path
sys.path.insert(0,{scripts!r})
import session_worker as sw
from service_identity import HostContext
sw.delegate.find_opencode=lambda:sys.executable
ctx=HostContext(Path({str(ctx.opencode_registration)!r}),Path({str(ctx.aikit_state)!r}),'2.2.0')
text=sw._stdin_task()
sw.supervise(Path({str(project)!r}),sys.argv[1],context=ctx,_task=text,prepare_command=lambda record:[sys.executable,'-c',{client_code!r},text])
"""

    def launch(
        value: BoundLaunch, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        _, process = sw.launch_worker(
            project,
            record.task_id,
            context=context,
            _host_reserved=True,
            _task=value.task,
            worker_command=lambda r: [sys.executable, "-c", supervisor_code, r.task_id],
        )
        return process

    monkeypatch.setattr(be, "_launch_supervisor", launch)
    try:
        prepared = prepare(project, ctx, task=prompt, timeout=5)
        first = be.execute_bound(prepared, context=ctx, wait_seconds=0.01)
        assert first["status"] == "pending"
        deadline = time.monotonic() + 8
        recovered = first
        while recovered["status"] == "pending" and time.monotonic() < deadline:
            time.sleep(0.03)
            recovered = be.recover_local_result(
                ctx, load_task(project, first["task_id"])
            )
        errors = (
            attempt_directory(load_task(project, first["task_id"]))
            / "supervisor.errors"
        )
        assert recovered["status"] == "ok", errors.read_text(
            encoding="utf-8", errors="replace"
        )
        assert recovered["summary"] == "literal-ok"
        assert submissions == [prompt]
        assert requests.count("/api/config") == 2
        assert requests.count("/api/model") == 1
        assert (
            be.execute_bound(prepared, context=ctx, wait_seconds=0)["task_id"]
            == first["task_id"]
        )
        assert len(submissions) == 1
        assert os.environ.get("OPENCODE_PASSWORD") != "test-only-password"
        assert not list((project / ".aikit").rglob("task.txt"))
        with urllib.request.urlopen(url + "other-session", timeout=2) as response:
            assert json.load(response) == {"unrelated_session": "still_running"}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(2)


@pytest.mark.parametrize("change", ["task", "attempt", "session"])
def test_recovery_rejects_mismatched_result_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: str
) -> None:

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx)

    def launch_ok(value: Any, record: Any, *, context: HostContext) -> subprocess.Popen:  # type: ignore
        write_terminal(record, text_event("ok") + "\n" + finish_event(0))
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(be, "_launch_supervisor", launch_ok)
    original = be.execute_bound(prepared, context=ctx, wait_seconds=1)
    assert original["status"] == "ok"
    record = load_task(project, original["task_id"])
    path = attempt_directory(record) / "result.json"
    data = json.loads(path.read_text())
    if change == "task":
        data.pop("task_id")
    elif change == "attempt":
        data["attempt_id"] = "00000000-0000-0000-0000-000000000000"
    else:
        data["session"] = "ses_foreign"
    path.write_text(json.dumps(data))
    recovered = be.recover_local_result(ctx, record)
    assert recovered["status"] == "pending"
    assert recovered["uncertain"] is True
    assert recovered["task_id"] == original["task_id"]


def test_local_recovery_does_not_adopt_a_record_copied_to_another_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dataclasses import replace

    import bound_execution as be
    from session_store import save_task

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx)

    def launch_own(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        write_terminal(record, text_event("own") + "\n" + finish_event(0))
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(be, "_launch_supervisor", launch_own)
    result = be.execute_bound(prepared, context=ctx, wait_seconds=1)
    assert result["status"] == "ok"
    record = load_task(project, result["task_id"])
    other = tmp_path / "other-project"
    other.mkdir()
    save_task(other, record)  # Copia con cwd original: no constituye autoridad aqui.
    displaced = replace(record, cwd=str(other.resolve()))
    assert be.recover_local_result(ctx, displaced)["status"] == "pending"


@pytest.mark.skipif(sys.platform != "win32", reason="FILE_SHARE_DELETE Win32")
def test_active_metadata_reader_allows_atomic_supervisor_write(tmp_path: Path) -> None:
    from dataclasses import replace

    import session_store as store

    from tests.test_session_store import make_record

    record = make_record(tmp_path)
    store.save_task(tmp_path, record)
    path = tmp_path / ".aikit" / "sessions" / record.task_id / "record.json"
    opener = getattr(store, "_open_shared_read", lambda p: p.open("rb"))
    with opener(path) as reader:
        before = reader.read()
        store.save_task(tmp_path, replace(record, reason="updated-by-supervisor"))
        reader.seek(0)
        assert reader.read() == before
    assert store.load_task(tmp_path, record.task_id).reason == "updated-by-supervisor"


# --- Completion-aware coordination and attempt timing regression tests ---


def test_wait_result_returns_before_deadline_on_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """_wait_result returns immediately when result.json has terminal delivery, not after full deadline."""
    import time

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx)

    # Launch supervisor that writes terminal result quickly
    def fast_launch(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        write_terminal(record, text_event("done") + "\n" + finish_event(0))
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(be, "_launch_supervisor", fast_launch)

    start = time.monotonic()
    result = be.execute_bound(prepared, context=ctx, wait_seconds=10.0)
    elapsed = time.monotonic() - start

    assert result["status"] == "ok"
    # Should return quickly (well before 10s deadline), not sleep full timeout
    assert elapsed < 5.0, f"Waited {elapsed:.2f}s, should return early on ready result"


def test_async_notify_does_not_turn_deadline_into_fixed_sleep(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Simulated async notification (early result.json) wakes wait before deadline."""
    import time

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx)

    # Simulate async notification: result.json appears early during wait
    def notify_launch(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        # Write result.json immediately (simulating async notify waking the wait)
        write_terminal(record, text_event("notified") + "\n" + finish_event(0))
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(be, "_launch_supervisor", notify_launch)

    start = time.monotonic()
    result = be.execute_bound(prepared, context=ctx, wait_seconds=10.0)
    elapsed = time.monotonic() - start

    assert result["status"] == "ok"
    assert result["summary"] == "notified"
    # Should NOT wait full 10s; returns early on notification
    assert elapsed < 5.0, f"Waited {elapsed:.2f}s despite early notification"


def test_host_without_notification_has_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without async notification, polling fallback still works (20ms interval)."""
    import subprocess
    import time

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx)

    # Delayed result: supervisor writes after ~200ms
    def delayed_launch(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        time.sleep(0.2)
        write_terminal(record, text_event("delayed") + "\n" + finish_event(0))
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.side_effect = subprocess.TimeoutExpired("cmd", 10.0)
        return mock

    monkeypatch.setattr(be, "_launch_supervisor", delayed_launch)

    start = time.monotonic()
    result = be.execute_bound(prepared, context=ctx, wait_seconds=5.0)
    elapsed = time.monotonic() - start

    assert result["status"] == "ok"
    assert result["summary"] == "delayed"
    # Should detect via polling (~200ms + polling overhead), not full 5s
    assert elapsed < 2.0, f"Polling fallback took {elapsed:.2f}s"


def test_pending_uncertain_never_success_or_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """delivery=pending/uncertain never yields status=ok or permits retry."""

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx)

    # Supervisor writes pending result (no terminal event)
    def pending_launch(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        write_terminal(
            record, text_event("partial only"), delivery="pending", publish=False
        )
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(be, "_launch_supervisor", pending_launch)

    result = be.execute_bound(prepared, context=ctx, wait_seconds=1.0)

    # Must be pending with uncertain=True, never ok
    assert result["status"] == "pending"
    assert result["uncertain"] is True
    assert result["delivery"] == "pending"
    # No fallback="reselect" for pending (only for free-limit with reconciliation)
    assert result.get("fallback") != "reselect"


def test_unrelated_session_attempt_provenance_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Recovery rejects result.json with mismatched task_id/attempt_id/session."""

    import bound_execution as be
    from session_store import load_task

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx)

    def ok_launch(value: Any, record: Any, *, context: HostContext) -> subprocess.Popen:  # type: ignore
        write_terminal(record, text_event("ok") + "\n" + finish_event(0))
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.communicate.return_value = (None, None)
        return mock

    monkeypatch.setattr(be, "_launch_supervisor", ok_launch)
    result = be.execute_bound(prepared, context=ctx, wait_seconds=2.0)
    assert result["status"] == "ok"

    record = load_task(project, result["task_id"])
    attempt_dir = project / ".aikit" / "sessions" / record.task_id / record.attempt_id

    # Corrupt result.json with foreign attempt_id
    import json

    data = json.loads((attempt_dir / "result.json").read_text())
    data["attempt_id"] = "00000000-0000-0000-0000-000000000000"
    (attempt_dir / "result.json").write_text(json.dumps(data))

    recovered = be.recover_local_result(ctx, record)
    assert recovered["status"] == "pending"
    assert recovered["uncertain"] is True
    assert "provenance_unavailable" in recovered.get(
        "limitations", []
    ) or "result_mismatch" in recovered.get("limitations", [])


def test_transport_tool_adapter_boundaries_with_fakes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test transport/tool adapter boundaries with fakes/owned short processes, no model probes."""
    import subprocess
    import sys

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx)

    # Use a real short-lived Python subprocess as the "CLI" to verify transport boundaries
    def real_child_launch(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen:  # type: ignore
        from tests.fakes import finish_event, text_event

        code = f"print({text_event('transport-ok')!r}); print({finish_event(0)!r})"
        options = (
            {"creationflags": subprocess.CREATE_NO_WINDOW}
            if sys.platform == "win32"
            else {}
        )
        child = subprocess.Popen(  # type: ignore[call-overload, attr-defined, arg-type, unused-ignore]
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            **options,
        )
        stdout, _ = child.communicate(timeout=5)
        # Simulate supervisor writing result.json
        write_terminal(record, stdout)
        return child  # type: ignore[no-any-return]

    monkeypatch.setattr(be, "_launch_supervisor", real_child_launch)

    result = be.execute_bound(prepared, context=ctx, wait_seconds=5.0)

    assert result["status"] == "ok"
    assert result["summary"] == "transport-ok"
    # No model inference occurred; pure transport test


def test_supervisor_returns_early_while_process_still_alive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Supervisor (real subprocess) writes result.json quickly then stays alive;
    coordinator returns terminal result while process.poll() is None."""
    import subprocess
    import sys
    import time

    import bound_execution as be

    project = tmp_path / "project"
    project.mkdir()
    ctx = make_context(tmp_path)
    binding = FakeBinding(context=ctx)
    install(monkeypatch, ctx, binding)
    prepared = prepare(project, ctx)

    fake_session = "ses_test_early"

    # Child script: call write_terminal (which updates host registry and writes result.json) then sleep
    child_script = tmp_path / "child_supervisor.py"
    child_script.write_text(
        "import sys, time, json, os\n"
        "from pathlib import Path\n"
        "scripts = " + repr(str(Path(delegate.__file__).parent)) + "\n"
        "repo = " + repr(str(Path.cwd())) + "\n"
        "sys.path[:0] = [scripts, repo]\n"
        "from session_store import load_task\n"
        "from tests.test_bound_execution import write_terminal\n"
        "from tests.fakes import finish_event, text_event\n"
        "import datetime\n"
        "\n"
        "task_id = sys.argv[1]\n"
        "attempt_id = sys.argv[2]\n"
        "r = load_task(Path(" + repr(str(project)) + "), task_id)\n"
        "# Write terminal result immediately via write_terminal (updates host registry)\n"
        "write_terminal(r, "
        + repr(
            text_event("early", session=fake_session)
            + "\n"
            + finish_event(0, session=fake_session)
        )
        + ")\n"
        "# Stay alive for delayed cleanup (safety margin)\n"
        "time.sleep(3.0)\n",
        encoding="utf-8",
    )

    child_proc: subprocess.Popen[bytes] | None = None

    def real_launch(
        value: Any, record: Any, *, context: HostContext
    ) -> subprocess.Popen[bytes]:
        nonlocal child_proc
        # Do NOT set record.session here - let child process set it via record_host_session
        # The coordinator will reload the record via _recover which will have the updated session

        options = (
            {"creationflags": subprocess.CREATE_NO_WINDOW}
            if sys.platform == "win32"
            else {}
        )
        # Pass both task_id and attempt_id to child script; use DEVNULL to avoid pipe buffer blocking
        child_proc = subprocess.Popen(  # type: ignore[call-overload, attr-defined, arg-type, unused-ignore]
            [sys.executable, str(child_script), record.task_id, record.attempt_id],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **options,
        )
        # Give child a moment to write result.json and update host registry
        time.sleep(1.0)
        return child_proc

    monkeypatch.setattr(be, "_launch_supervisor", real_launch)

    try:
        start = time.monotonic()
        result = be.execute_bound(prepared, context=ctx, wait_seconds=5.0)
        elapsed = time.monotonic() - start

        # Coordinator returned terminal result quickly (well before child's 3s sleep)
        assert result["status"] == "ok"
        assert result["summary"] == "early"
        assert elapsed < 2.0, f"Coordinator took {elapsed:.2f}s, should return early"

        # Process should still be alive (delayed cleanup)
        assert child_proc is not None
        assert child_proc.poll() is None, "Supervisor process should still be alive"
    finally:
        # Clean up ONLY our owned process
        if child_proc is not None:
            if child_proc.poll() is None:
                if sys.platform == "win32":
                    subprocess.run(
                        ["taskkill", "/T", "/F", "/PID", str(child_proc.pid)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                        creationflags=subprocess.CREATE_NO_WINDOW
                        if sys.platform == "win32"
                        else 0,
                    )
                else:
                    child_proc.terminate()
            child_proc.wait(timeout=2)
