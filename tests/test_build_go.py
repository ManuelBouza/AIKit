"""Exportación aislada e instalación de go en perfiles temporales."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest
from build_go import FILES, export_go

ROOT = Path(__file__).resolve().parents[1]


def test_export_and_install_are_isolated_and_idempotent(tmp_path: Path) -> None:
    package = export_go(ROOT, tmp_path / "paquete con espacios")
    expected = {
        "README.md": "docs/artefacto-go-readme.md",
        "config/codex/go.md": "config/codex/go.md",
        "scripts/global_instructions.py": "scripts/global_instructions.py",
        "scripts/install_go.py": "scripts/install_go.py",
    }
    assert {
        p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file()
    } == set(expected)
    for target, source in expected.items():
        assert (package / target).read_bytes() == (ROOT / source).read_bytes()
    profile = tmp_path / "perfil con espacios"
    profile.mkdir()
    original = b"# Ajeno\r\n<!-- AIKIT:ROUTING:BEGIN -->\r\nficticio\r\n<!-- AIKIT:ROUTING:END -->\r\n"
    agents = profile / "AGENTS.md"
    agents.write_bytes(original)
    env = os.environ.copy()
    env["PATH"] = ""
    env.pop("PYTHONPATH", None)
    command = [
        sys.executable,
        str(package / "scripts/install_go.py"),
        "--codex-home",
        str(profile),
    ]
    first = subprocess.run(
        command,
        cwd=package,
        env=env,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    result = json.loads(first.stdout)
    assert result["status"] == "changed"
    assert Path(result["backup"]).read_bytes() == original
    content = agents.read_bytes()
    assert content.startswith(original)
    assert b"<!-- AIKIT:GO:BEGIN -->" in content
    backups = list((profile / "backups/aikit").iterdir())
    second = subprocess.run(
        command,
        cwd=package,
        env=env,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    assert json.loads(second.stdout) == {"status": "unchanged", "backup": None}
    assert agents.read_bytes() == content
    assert list((profile / "backups/aikit").iterdir()) == backups


def test_missing_source_and_existing_output_do_not_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "salida"
    with pytest.raises(FileNotFoundError):
        export_go(tmp_path, output)
    assert not output.exists()
    output.mkdir()
    marker = output / "existente"
    marker.write_text("conservar", encoding="utf-8")
    with pytest.raises(FileExistsError):
        export_go(ROOT, output)
    assert marker.read_text(encoding="utf-8") == "conservar"


def test_cli_exports_and_rejects_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "salida con espacios"
    command = [
        sys.executable,
        str(ROOT / "scripts/build_go.py"),
        "--output",
        str(output),
    ]
    first = subprocess.run(command, capture_output=True, text=True, timeout=15)
    assert first.returncode == 0, first.stderr
    assert (output / "README.md").is_file()
    second = subprocess.run(command, capture_output=True, text=True, timeout=15)
    assert second.returncode != 0
    assert (output / "README.md").is_file()


@pytest.mark.skipif(os.name != "nt", reason="Las junctions requieren Windows")
@pytest.mark.parametrize("location", ["source", "output"])
def test_real_junction_is_rejected(tmp_path: Path, location: str) -> None:
    target = ROOT if location == "source" else tmp_path / "target"
    if location == "output":
        target.mkdir()
    junction = tmp_path / "junction"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode:
        pytest.skip(f"No se pudo crear junction: {result.stderr or result.stdout}")
    try:
        output = tmp_path / "salida" if location == "source" else junction / "salida"
        script = (
            junction / "scripts/build_go.py"
            if location == "source"
            else ROOT / "scripts/build_go.py"
        )
        run = subprocess.run(
            [sys.executable, str(script), "--output", str(output)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert run.returncode != 0
        assert "reanálisis" in run.stderr or "enlaces" in run.stderr
        assert not output.exists()
    finally:
        os.rmdir(junction)


def test_symlink_source_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "fuente"
    for relative in FILES:
        file = source / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes((ROOT / relative).read_bytes())
    template = source / "config/codex/go.md"
    template.unlink()
    try:
        template.symlink_to(ROOT / "config/codex/go.md")
    except OSError:
        pytest.skip("El sistema no permite crear enlaces simbólicos")
    with pytest.raises(ValueError, match="enlaces"):
        export_go(source, tmp_path / "salida")
    assert not (tmp_path / "salida").exists()


def test_write_failure_reports_partial_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "salida"
    original_write = Path.write_bytes

    def fail_on_template(path: Path, data: bytes) -> int:
        if path == output / "config/codex/go.md":
            raise OSError("fallo simulado")
        return original_write(path, data)

    monkeypatch.setattr(Path, "write_bytes", fail_on_template)
    with pytest.raises(OSError, match="Exportación incompleta"):
        export_go(ROOT, output)
    assert (output / "README.md").exists()


@pytest.mark.parametrize("location", ["source", "output"])
def test_rejects_linked_ancestor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, location: str
) -> None:
    source = ROOT if location == "output" else tmp_path / "linked" / "source"
    output = (
        tmp_path / "linked" / "output" if location == "output" else tmp_path / "output"
    )
    linked = tmp_path / "linked"
    original_is_symlink = Path.is_symlink

    def simulated_link(path: Path) -> bool:
        return path == linked or original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", simulated_link)
    with pytest.raises(ValueError, match="enlaces"):
        export_go(source, output)
    assert not output.exists()


def test_rejects_reparse_point_ancestor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    junction = tmp_path / "junction"
    output = junction / "output"
    original_lstat = Path.lstat
    original_is_symlink = Path.is_symlink
    reparse_flag = 0x400
    monkeypatch.setattr(
        stat, "FILE_ATTRIBUTE_REPARSE_POINT", reparse_flag, raising=False
    )

    def simulated_lstat(path: Path) -> os.stat_result:
        if path == junction:
            return cast(
                os.stat_result, SimpleNamespace(st_file_attributes=reparse_flag)
            )
        return original_lstat(path)

    def simulated_is_symlink(path: Path) -> bool:
        return False if path == junction else original_is_symlink(path)

    monkeypatch.setattr(Path, "lstat", simulated_lstat)
    monkeypatch.setattr(Path, "is_symlink", simulated_is_symlink)
    with pytest.raises(ValueError, match="reanálisis"):
        export_go(ROOT, output)
    assert not output.exists()


@pytest.mark.parametrize("case", ["override", "markers"])
def test_exported_installer_rejects_invalid_profile(tmp_path: Path, case: str) -> None:
    package = export_go(ROOT, tmp_path / "package")
    profile = tmp_path / "profile"
    profile.mkdir()
    agents = profile / "AGENTS.md"
    original = b"<!-- AIKIT:GO:BEGIN -->" if case == "markers" else b"ajeno"
    agents.write_bytes(original)
    if case == "override":
        (profile / "AGENTS.override.md").write_text("ajeno", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(package / "scripts/install_go.py"),
            "--codex-home",
            str(profile),
        ],
        cwd=package,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode != 0
    assert agents.read_bytes() == original
    assert not (profile / "backups").exists()
