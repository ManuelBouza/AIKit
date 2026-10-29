"""Exportación por lista permitida, sin incluir archivos privados del checkout."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def builder() -> ModuleType:
    path = ROOT / "scripts" / "build_plugin.py"
    spec = importlib.util.spec_from_file_location("build_plugin", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_export_excludes_unlisted_files_and_generates_compatibility(
    builder: ModuleType, tmp_path: Path
) -> None:
    source = tmp_path / "fuentes"
    for relative in builder.PACKAGE_FILES:
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    for relative in [
        ".env",
        ".venv/private",
        "skills/private.txt",
        ".git/config",
        ".aikit/private",
    ]:
        secret = source / relative
        secret.parent.mkdir(parents=True, exist_ok=True)
        secret.write_text("ficticio", encoding="utf-8")
    output = tmp_path / "distribucion con espacios"
    package = builder.export_plugin(source, output)
    assert package == output / "aikit"
    actual = {
        p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file()
    }
    assert actual == (set(builder.PACKAGE_FILES) - {"plugin.json", "mcp.json"}) | {
        ".codex-plugin/plugin.json",
        ".mcp.json",
    }
    legacy = json.loads((package / ".codex-plugin/plugin.json").read_text())
    assert legacy["mcpServers"] == "./.mcp.json"
    portable = json.loads((source / "mcp.json").read_text())
    compatible = json.loads((package / ".mcp.json").read_text())
    for name, server in portable["mcpServers"].items():
        assert compatible["mcpServers"][name] == {
            key: value for key, value in server.items() if key != "type"
        }
    marketplace = json.loads((output / ".agents/plugins/marketplace.json").read_text())
    assert marketplace["plugins"][0]["source"]["path"] == "./aikit"


def test_effective_openai_overlay_resolves_bundled_mcp(
    builder: ModuleType, tmp_path: Path
) -> None:
    package = builder.export_plugin(ROOT, tmp_path / "salida")
    assert not (package / "plugin.json").exists()
    assert not (package / "mcp.json").exists()
    effective = json.loads((package / ".codex-plugin/plugin.json").read_text())
    mcp_path = package / effective["mcpServers"]
    assert set(json.loads(mcp_path.read_text())["mcpServers"]) == {"aikit-opencode"}
    server = json.loads(mcp_path.read_text())["mcpServers"]["aikit-opencode"]
    assert server["cwd"] == "${PLUGIN_ROOT}"
    assert server["args"][:7] == [
        "run",
        "--project",
        "${PLUGIN_ROOT}",
        "--locked",
        "--no-dev",
        "--extra",
        "mcp",
    ]
    assert server["tool_timeout_sec"] == 15000
    assert server["startup_timeout_sec"] == 120


def test_existing_output_is_preserved(builder: ModuleType, tmp_path: Path) -> None:
    sentinel = tmp_path / "sentinel"
    sentinel.write_text("conservar", encoding="utf-8")
    with pytest.raises(FileExistsError):
        builder.export_plugin(ROOT, tmp_path)
    assert sentinel.read_text() == "conservar"


def test_missing_source_creates_no_output(builder: ModuleType, tmp_path: Path) -> None:
    source = tmp_path / "fuentes"
    source.mkdir()
    output = tmp_path / "salida"
    with pytest.raises(FileNotFoundError):
        builder.export_plugin(source, output)
    assert not output.exists()


def test_output_inside_source_skills_is_rejected(
    builder: ModuleType, tmp_path: Path
) -> None:
    source = tmp_path / "fuentes"
    source.mkdir()
    output = source / "skills" / "salida"
    with pytest.raises(ValueError, match="skills"):
        builder.export_plugin(source, output)
    assert not output.exists()


def test_symlink_parent_is_rejected(builder: ModuleType, tmp_path: Path) -> None:
    source = tmp_path / "fuentes"
    source.mkdir()
    for relative in builder.PACKAGE_FILES:
        if relative.startswith("skills/"):
            continue
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / relative).read_bytes())
    try:
        (source / "skills").symlink_to(ROOT / "skills", target_is_directory=True)
    except OSError:
        pytest.skip("El sistema no permite crear enlaces simbólicos")
    output = tmp_path / "salida"
    with pytest.raises(ValueError, match="enlace"):
        builder.export_plugin(source, output)
    assert not output.exists()


def test_symlink_source_is_rejected(builder: ModuleType, tmp_path: Path) -> None:
    source = tmp_path / "fuentes"
    for relative in builder.PACKAGE_FILES:
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / relative).read_bytes())
    target = source / "plugin.json"
    target.unlink()
    try:
        target.symlink_to(ROOT / "plugin.json")
    except OSError:
        pytest.skip("El sistema no permite crear enlaces simbólicos")
    output = tmp_path / "salida"
    with pytest.raises(ValueError, match="enlace"):
        builder.export_plugin(source, output)
    assert not output.exists()
