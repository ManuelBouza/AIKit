"""Comando determinista de disponibilidad: lectura local y refresco explícito."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import delegate
import pytest

from tests.fakes import api_model


def test_availability_status_does_not_call_service_or_infer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setattr(
        delegate,
        "resolve_host_context",
        lambda: (_ for _ in ()).throw(AssertionError("no debe resolver servicio")),
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(Path(delegate.__file__).resolve()),
            "availability",
            "status",
            "--cwd",
            str(project),
            "--json",
        ],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(Path(delegate.__file__).resolve().parent)},
        timeout=10,
        check=False,
    )
    assert completed.returncode == 1, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["code"] == "host_context_unavailable"
    assert not (project / ".aikit-state").exists()


def test_availability_refresh_uses_registered_service_and_does_not_start(
    harness: object, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.conftest import Harness

    assert isinstance(harness, Harness)
    harness.fake()
    monkeypatch.setattr(
        subprocess,
        "Popen",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("no debe arrancar")),
    )
    code = delegate.main(
        ["availability", "refresh", "--cwd", str(harness.project), "--json"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["status"] == "ok"
    assert payload["refreshed"] is True
    assert harness.binding is not None
    assert any(kind == "catalog" for kind, _ in harness.binding.calls)


def test_availability_missing_state_refreshes_once_then_status_is_local(
    harness: object, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.conftest import Harness

    assert isinstance(harness, Harness)
    harness.fake(models=[api_model("uno"), api_model("dos")])
    assert (
        delegate.main(
            ["availability", "refresh", "--cwd", str(harness.project), "--json"]
        )
        == 0
    )
    capsys.readouterr()
    assert harness.binding is not None
    catalog_calls_after_refresh = len(harness.binding.catalog_calls)
    assert (
        delegate.main(
            ["availability", "status", "--cwd", str(harness.project), "--json"]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["exists"] is True
    assert payload["snapshot"]["generation"] == 1
    assert harness.binding is not None
    assert len(harness.binding.catalog_calls) == catalog_calls_after_refresh
