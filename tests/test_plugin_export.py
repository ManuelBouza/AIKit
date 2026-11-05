"""Exportación por lista permitida, sin incluir archivos privados del checkout."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
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


def test_export_excludes_unlisted_files_and_preserves_portable_manifests(
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
    assert actual == set(builder.PACKAGE_FILES)
    assert (package / "plugin.json").read_bytes() == (
        source / "plugin.json"
    ).read_bytes()
    assert (package / "mcp.json").read_bytes() == (source / "mcp.json").read_bytes()
    assert not (package / ".codex-plugin").exists()
    assert not (package / ".mcp.json").exists()
    marketplace = json.loads((output / ".agents/plugins/marketplace.json").read_text())
    assert marketplace["plugins"][0]["source"]["path"] == "./aikit"


def test_portable_entrypoint_resolves_bundled_mcp(
    builder: ModuleType, tmp_path: Path
) -> None:
    package = builder.export_plugin(ROOT, tmp_path / "salida")
    manifest = json.loads((package / "plugin.json").read_text())
    assert manifest["extensions"]["com.openai"]["requires_local_executor"] is True
    assert manifest["extensions"]["com.openai"]["interface"]["displayName"] == "AIKit"
    mcp_path = package / "mcp.json"
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
    assert server["type"] == "stdio"
    assert set(server) <= {"type", "command", "args", "env", "cwd"}
    script = package / server["args"][-1].removeprefix("${PLUGIN_ROOT}/")
    assert script.is_file()


def test_exported_public_entrypoints_import(
    builder: ModuleType, tmp_path: Path
) -> None:
    package = builder.export_plugin(ROOT, tmp_path / "salida")
    scripts = package / "skills/delegating-to-opencode/scripts"
    for name in (
        "bound_execution.py",
        "service_identity.py",
        "service_connection.py",
        "session_store.py",
        "session_backend.py",
        "session_worker.py",
        "session_stream.py",
        "host_registry.py",
    ):
        assert (scripts / name).is_file()
    code = (
        "import sys;"
        f"sys.path.insert(0, {str(scripts)!r});"
        "import delegate, bound_execution, mcp_server, session_worker;"
        "print('ok')"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        cwd=str(package),
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "ok"


def test_existing_output_is_preserved(builder: ModuleType, tmp_path: Path) -> None:
    sentinel = tmp_path / "sentinel"
    sentinel.write_text("conservar", encoding="utf-8")
    with pytest.raises(FileExistsError):
        builder.export_plugin(ROOT, tmp_path)
    assert sentinel.read_text() == "conservar"


@pytest.mark.parametrize(
    "field", ["startup_timeout_sec", "tool_timeout_sec", "enabled_tools"]
)
def test_nonportable_settings_are_rejected_before_writing(
    builder: ModuleType, tmp_path: Path, field: str
) -> None:
    source = tmp_path / "fuentes"
    for relative in builder.PACKAGE_FILES:
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / relative).read_bytes())
    config = source / "mcp.json"
    settings = json.loads(config.read_text())
    settings["mcpServers"]["aikit-opencode"][field] = 15000
    config.write_text(json.dumps(settings), encoding="utf-8")
    output = tmp_path / "salida"
    with pytest.raises(ValueError, match="MCP portable"):
        builder.export_plugin(source, output)
    assert not output.exists()


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


def test_exported_cli_main_has_no_host_or_model_side_effects(
    builder: ModuleType, tmp_path: Path
) -> None:
    import os

    package = builder.export_plugin(ROOT, tmp_path / "clean-export")
    scripts = package / "skills/delegating-to-opencode/scripts"
    env = os.environ.copy()
    for name in (
        "AIKIT_OPENCODE_REGISTRATION",
        "AIKIT_STATE",
        "AIKIT_EXPECTED_OPENCODE_VERSION",
    ):
        env.pop(name, None)
    env["PYTHONPATH"] = str(scripts)
    env["PATH"] = ""
    task = tmp_path / "task.txt"
    task.write_text("no inference")
    for args in (
        ["doctor", "--cwd", str(package)],
        [
            "run",
            "--cwd",
            str(package),
            "--task-file",
            str(task),
            "--model",
            "fake/provider",
            "--reason",
            "test",
        ],
    ):
        completed = subprocess.run(
            [sys.executable, str(scripts / "delegate.py"), *args],
            capture_output=True,
            text=True,
            env=env,
            cwd=package,
            timeout=10,
        )
        assert completed.returncode == 1, completed.stderr
        payload = json.loads(completed.stdout)
        assert payload["code"] == "host_context_unavailable"
    assert not (package / ".aikit").exists()
