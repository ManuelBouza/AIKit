"""Fixtures compartidas para escenarios sin procesos OpenCode reales."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import delegate
import pytest

from tests.fakes import (
    DEFAULT_MODEL,
    FakeTransport,
    api_model,
    default_config_sources,
    finish_event,
    text_event,
)


@dataclass
class Harness:
    project: Path
    task: Path
    monkeypatch: pytest.MonkeyPatch

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
        self.monkeypatch.setattr(delegate, "run_process", transport)
        self.monkeypatch.setattr(
            delegate, "find_opencode", lambda: "C:/fake/opencode.exe"
        )
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
    ) -> dict[str, Any]:
        return delegate.run_task(
            cwd=cwd or self.project,
            task_file=task_file or self.task,
            model=model,
            variant=variant,
            reason=reason,
            agent=agent,
            timeout=timeout,
        )

    def doctor(
        self, *, model: str | None = None, timeout: float = 30
    ) -> dict[str, Any]:
        return delegate.doctor(cwd=self.project, model=model, timeout=timeout)


@pytest.fixture
def harness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Harness:
    task = tmp_path / "tarea.txt"
    task.write_text("Tarea de prueba", encoding="utf-8")
    return Harness(tmp_path, task, monkeypatch)
