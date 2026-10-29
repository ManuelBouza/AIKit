"""La CLI conserva el runtime stdlib: no carga el SDK de MCP."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "delegating-to-opencode" / "scripts"
DELEGATE = SCRIPTS / "delegate.py"


def _env_with_pythonpath(*entries: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(str(entry) for entry in entries)
    return env


def test_importing_the_cli_does_not_load_the_mcp_sdk() -> None:
    code = "import delegate, sys; print('mcp' in sys.modules)"
    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=_env_with_pythonpath(SCRIPTS),
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "False"


def test_cli_runs_with_the_mcp_sdk_unavailable(tmp_path: Path) -> None:
    blocked = tmp_path / "sin-sdk"
    blocked.mkdir()
    (blocked / "mcp.py").write_text(
        "raise ImportError('SDK de MCP bloqueado')\n", encoding="utf-8"
    )
    task = tmp_path / "tarea.txt"
    task.write_text("Tarea de prueba", encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(DELEGATE),
            "run",
            "--cwd",
            str(tmp_path),
            "--task-file",
            str(task),
        ],
        capture_output=True,
        text=True,
        env=_env_with_pythonpath(blocked, SCRIPTS),
        timeout=60,
        check=False,
    )
    assert completed.returncode == 1, completed.stderr
    assert '"code":"model_required"' in completed.stdout
