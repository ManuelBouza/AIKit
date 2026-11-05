"""Fixtures compartidas para escenarios sin procesos OpenCode reales."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import bound_execution
import delegate
import pytest
from service_identity import HostContext
from session_store import DeliveryState, Role

from tests.fakes import (
    DEFAULT_MODEL,
    FakeBinding,
    FakeTransport,
    api_model,
    default_config_sources,
    finish_event,
    text_event,
)


def _terminal(stdout: str) -> bool:
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") not in ("step_finish", "step-finish"):
            continue
        part = event.get("part")
        if isinstance(part, dict) and part.get("reason") == "stop":
            return True
    return False


def _attempt_directory(record: Any) -> Path:
    root = Path(str(record.cwd))
    return root / ".aikit" / "sessions" / str(record.task_id) / str(record.attempt_id)


def _write_report(
    record: Any,
    stdout: str,
    *,
    returncode: int = 0,
    interrupted: bool = False,
    context: HostContext,
) -> None:
    summary, session, _cost, errors = delegate.parse_events(stdout)
    if interrupted:
        status, delivery, limitations = "pending", "interrupted", ["deadline_exceeded"]
    elif returncode != 0 or errors:
        status, delivery, limitations = "error", "failed", []
    elif _terminal(stdout) and summary:
        status, delivery, limitations = "ok", "completed", []
    elif summary:
        status, delivery, limitations = "pending", "partial", []
    else:
        status, delivery, limitations = "pending", "pending", []
    report = {
        "status": status,
        "task_id": record.task_id,
        "attempt_id": record.attempt_id,
        "session": session,
        "delivery": delivery,
        "execution": "unknown",
        "client_exit_code": returncode,
        "summary": summary,
        "deadline_exceeded": interrupted,
        "stdout_truncated": False,
        "stderr_truncated": False,
        "line_truncated": False,
        "limitations": limitations,
    }
    from host_registry import record_host_observation, record_host_session
    from session_store import DeliveryObservation, save_task

    if session is not None:
        record_host_session(context, record, session)
        record.session = session
    record.delivery = DeliveryObservation(
        cast(DeliveryState, delivery), "fake_supervisor", "2026-10-31T00:00:00+00:00"
    )
    save_task(Path(record.cwd), record)
    record_host_observation(context, record, terminal=delivery == "completed")
    directory = _attempt_directory(record)
    (directory / "stdout.partial").write_text(stdout, encoding="utf-8")
    (directory / "result.json").write_text(json.dumps(report), encoding="utf-8")


@dataclass
class Harness:
    project: Path
    task: Path
    monkeypatch: pytest.MonkeyPatch
    binding: FakeBinding | None = None
    context: HostContext | None = None
    bindings: list[FakeBinding] = field(default_factory=list)

    def fake(
        self,
        transport: FakeTransport | None = None,
        *,
        version: str = "2.2.0",
        models: list[dict[str, Any]] | None = None,
        run_stdout: str | None = None,
        run_returncode: int = 0,
        run_stderr: str = "",
        fail_run: bool = False,
        timeout_error: bool = False,
        version_returncode: int = 0,
        version_stderr: str = "",
        catalog_returncode: int = 0,
        catalog_stderr: str = "",
        config_sources: list[dict[str, Any]] | None = None,
        config_returncode: int = 0,
        config_stdout: str | None = None,
        config_stderr: str = "",
    ) -> FakeTransport:
        if transport is None:
            transport = FakeTransport(
                version=version,
                models=models if models is not None else [api_model()],
                run_stdout=run_stdout
                if run_stdout is not None
                else text_event("ok") + "\n" + finish_event(0),
                run_returncode=run_returncode,
                run_stderr=run_stderr,
                fail_run=fail_run,
                timeout_error=timeout_error,
                version_returncode=version_returncode,
                version_stderr=version_stderr,
                catalog_returncode=catalog_returncode,
                catalog_stderr=catalog_stderr,
                config_sources=config_sources
                if config_sources is not None
                else default_config_sources(),
                config_returncode=config_returncode,
                config_stdout=config_stdout,
                config_stderr=config_stderr,
            )
        host_root = self.project.parent / (self.project.name + "-host")
        context = HostContext(
            host_root / "registration.json", host_root / "state", "2.2.0"
        )
        sources = (
            config_sources if config_sources is not None else default_config_sources()
        )
        catalog = models if models is not None else [api_model()]

        self.context = context

        def discover(_context: HostContext, **kwargs: Any) -> FakeBinding:
            binding = FakeBinding(
                context=_context,
                version=version,
                sources=sources,
                catalog=catalog,
                config_returncode=config_returncode,
                config_stdout=config_stdout,
                config_stderr=config_stderr,
                catalog_returncode=catalog_returncode,
                catalog_stderr=catalog_stderr,
            )
            self.binding = binding
            self.bindings.append(binding)
            return binding

        from unittest.mock import MagicMock

        def launch(prepared: Any, record: Any, *, context: HostContext) -> MagicMock:
            if transport.timeout_error:
                _write_report(record, "", interrupted=True, context=context)
                mock = MagicMock()
                mock.communicate.side_effect = subprocess.TimeoutExpired(
                    "cmd", prepared.timeout
                )
                return mock
            completed = transport(prepared.argv, prepared.project, prepared.timeout)
            _write_report(
                record,
                completed.stdout or "",
                returncode=completed.returncode,
                context=context,
            )
            mock = MagicMock()
            mock.communicate.return_value = (None, None)
            return mock

        self.monkeypatch.setattr(delegate, "resolve_host_context", lambda: context)
        self.monkeypatch.setattr(delegate, "discover_existing", discover)
        self.monkeypatch.setattr(
            delegate, "find_opencode", lambda: "C:/fake/opencode.exe"
        )
        self.monkeypatch.setattr(bound_execution, "_launch_supervisor", launch)
        return transport

    def run(
        self,
        *,
        cwd: Path | None = None,
        task_file: Path | None = None,
        model: str | None = DEFAULT_MODEL,
        variant: str | None = None,
        reason: str | None = "tarea mecánica con herramientas de texto",
        agent: str = "build",
        timeout: float = 30,
        role: Role = "implementer",
    ) -> dict[str, Any]:
        return delegate.run_task(
            cwd=cwd or self.project,
            task_file=task_file or self.task,
            model=model,
            variant=variant,
            reason=reason,
            agent=agent,
            timeout=timeout,
            role=role,
        )

    def run_text(
        self,
        task: str,
        *,
        cwd: Path | None = None,
        model: str | None = DEFAULT_MODEL,
        variant: str | None = None,
        reason: str | None = "tarea mecánica con herramientas de texto",
        agent: str = "build",
        timeout: float = 30,
        role: Role = "implementer",
    ) -> dict[str, Any]:
        return delegate.run_text_task(
            cwd=cwd or self.project,
            task=task,
            model=model,
            variant=variant,
            reason=reason,
            agent=agent,
            timeout=timeout,
            role=role,
        )

    def doctor(
        self, *, model: str | None = None, timeout: float = 30
    ) -> dict[str, Any]:
        return delegate.doctor(cwd=self.project, model=model, timeout=timeout)


@pytest.fixture
def anyio_backend() -> str:
    """Los transportes MCP en memoria corren sobre asyncio."""

    return "asyncio"


@pytest.fixture
def harness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Harness:
    task = tmp_path / "tarea.txt"
    task.write_text("Tarea de prueba", encoding="utf-8")
    return Harness(tmp_path, task, monkeypatch)


@pytest.fixture(autouse=True)
def _hide_own_test_processes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Los auxiliares de pruebas no deben crear consolas Windows visibles."""
    import subprocess
    import sys

    if sys.platform != "win32":
        return
    original = subprocess.Popen

    def hidden(*args: Any, **kwargs: Any) -> Any:
        kwargs["creationflags"] = (
            kwargs.get("creationflags", 0) | subprocess.CREATE_NO_WINDOW
        )
        return original(*args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", hidden)
