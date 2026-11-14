"""El verificador no declara éxito con controles fallidos o preparación incompleta."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")
pytestmark = pytest.mark.skipif(
    sys.platform != "win32" or not POWERSHELL,
    reason="Lanzador de verificación Windows",
)


@pytest.mark.parametrize(
    ("failure", "missing", "expected_code"),
    [
        ("", "", 0),
        ("uv sync --locked", "", 1),
        ("npm ci --include=dev", "", 1),
        ("npm run lint", "", 1),
        ("npm run typecheck", "", 1),
        ("npm run format:check", "", 1),
        ("npm run test", "", 1),
        ("uv run --no-sync pytest", "", 1),
        ("uv --version", "", 1),
        ("", "uv", 1),
        ("", "node", 1),
        ("", "npm", 1),
    ],
)
def test_verificador_respeta_preparacion_y_fallos(
    tmp_path: Path, failure: str, missing: str, expected_code: int
) -> None:
    log = tmp_path / "commands.txt"
    for program in ("uv", "node", "npm"):
        if program == missing:
            continue
        (tmp_path / f"{program}.cmd").write_text(
            "@echo off\n"
            + (
                'if "%~1"=="-e" (\n'
                'echo node compatibility>>"%AIKIT_CHECK_LOG%"\n'
                'echo CWD=%CD%>>"%AIKIT_CHECK_LOG%"\n'
                "exit /b 0\n)\n"
                if program == "node"
                else ""
            )
            + f'echo {program} %*>>"%AIKIT_CHECK_LOG%"\n'
            'echo CWD=%CD%>>"%AIKIT_CHECK_LOG%"\n'
            f'if "{program} %*"=="%AIKIT_CHECK_FAIL%" exit /b 7\n'
            "exit /b 0\n",
            encoding="ascii",
        )
    env = dict(os.environ)
    env.update(
        PATH=str(tmp_path)
        + os.pathsep
        + str(Path(os.environ["SystemRoot"]) / "System32"),
        AIKIT_CHECK_LOG=str(log),
        AIKIT_CHECK_FAIL=failure,
    )
    result = subprocess.run(
        [str(POWERSHELL), "-NoProfile", "-File", str(ROOT / "scripts/verificar.ps1")],
        env=env,
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
        timeout=30,
    )
    assert result.returncode == expected_code, result.stdout + result.stderr
    commands = log.read_text() if log.exists() else ""
    lines = commands.splitlines()
    for position, command in enumerate(lines):
        if command.startswith(("uv ", "npm ", "node ")):
            expected_cwd = (
                ROOT / "packages/aikit-installer"
                if command.startswith("npm ") and command != "npm --version"
                else ROOT
            )
            assert lines[position + 1] == f"CWD={expected_cwd}"
    if failure in ("uv sync --locked", "uv --version") or missing == "uv":
        assert "uv run" not in commands
    if failure == "npm ci --include=dev" or missing in ("node", "npm"):
        assert "npm run" not in commands
    if failure == "npm run lint":
        assert "npm run test" in commands
    if expected_code == 0:
        assert "npm run format:check" in commands
        assert "uv run --no-sync mypy" in commands
        for control in ("typecheck", "lint", "format:check", "test"):
            assert f"npm run {control}" in commands
        for control in ("pytest", "ruff check .", "ruff format --check .", "mypy"):
            assert f"uv run --no-sync {control}" in commands


def test_verificador_registra_fallo_de_lanzamiento(tmp_path: Path) -> None:
    # Get-Command descubre el archivo; Windows no puede ejecutarlo como programa.
    (tmp_path / "uv.exe").write_bytes(b"not a Windows executable")
    env = dict(os.environ)
    env["PATH"] = str(tmp_path)
    result = subprocess.run(
        [str(POWERSHELL), "-NoProfile", "-File", str(ROOT / "scripts/verificar.ps1")],
        env=env,
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
        timeout=30,
    )
    assert result.returncode != 0
    assert "Resumen de verificaciones" in result.stdout
    assert "no ejecutado por fallo previo" in result.stdout
