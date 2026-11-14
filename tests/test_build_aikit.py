from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from build_aikit import FILES, export_aikit

ROOT = Path(__file__).resolve().parents[1]


def run_install(
    package: Path, name: str, profile: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(package / f"scripts/install_{name}.py"),
            "--codex-home",
            str(profile),
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )


def test_export_and_install(tmp_path: Path) -> None:
    output = tmp_path / "catalogo"
    package = export_aikit(ROOT, output)
    assert {
        p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()
    } == set(FILES.values())
    assert (
        json.loads((package / "plugin.json").read_text(encoding="utf-8"))["name"]
        == "aikit-preferencias"
    )
    manifest = json.loads((package / "plugin.json").read_text(encoding="utf-8"))
    interface = manifest["extensions"]["com.openai"]["interface"]
    for key in ("logo", "composerIcon"):
        assert interface[key] == "./assets/aikit-icon.png"
        assert (package / interface[key]).read_bytes() == (
            ROOT / "packaging/assets/aikit-icon.png"
        ).read_bytes()
    onboarding = manifest["extensions"]["com.openai"]["onboardingSkill"]
    assert (package / onboarding).is_file()
    director = "skills/director-de-ideas/SKILL.md"
    assert (package / director).read_bytes() == (
        ROOT / "packaging" / director
    ).read_bytes()
    assert not (package / "mcp.json").exists()
    profile = tmp_path / "perfil"
    profile.mkdir()
    agents = profile / "AGENTS.md"
    foreign = b"# Ajeno\r\n"
    agents.write_bytes(foreign)
    assert run_install(package, "go", profile).returncode == 0
    before = agents.read_bytes()
    first = run_install(package, "context7", profile)
    assert first.returncode == 0, first.stderr
    first_result = json.loads(first.stdout)
    assert first_result["status"] == "changed"
    assert Path(first_result["backup"]).read_bytes() == before
    after = agents.read_bytes()
    assert after.startswith(before)
    assert after.startswith(foreign)
    assert b"<!-- AIKIT:CONTEXT7:BEGIN -->" in after
    repeated_go = run_install(package, "go", profile)
    assert repeated_go.returncode == 0
    assert json.loads(repeated_go.stdout)["status"] == "unchanged"
    second = run_install(package, "context7", profile)
    assert second.returncode == 0
    second_result = json.loads(second.stdout)
    assert second_result["status"] == "unchanged"
    assert second_result["backup"] is None
    assert agents.read_bytes() == after
    with pytest.raises(FileExistsError):
        export_aikit(ROOT, output)
    assert agents.read_bytes() == after


def test_empty_profile_and_existing_file(tmp_path: Path) -> None:
    package = export_aikit(ROOT, tmp_path / "output")
    profile = tmp_path / "nuevo"
    assert run_install(package, "go", profile).returncode == 0
    assert run_install(package, "context7", profile).returncode == 0
    content = (profile / "AGENTS.md").read_text(encoding="utf-8")
    assert "AIKIT:GO:BEGIN" in content
    assert "AIKIT:CONTEXT7:BEGIN" in content
    occupied = tmp_path / "ocupado"
    occupied.write_bytes(b"ajeno")
    with pytest.raises(FileExistsError):
        export_aikit(ROOT, occupied)
    assert occupied.read_bytes() == b"ajeno"


@pytest.mark.parametrize("case", ["missing", "duplicate", "reversed", "override"])
def test_invalid_profile_is_unchanged(tmp_path: Path, case: str) -> None:
    package = export_aikit(ROOT, tmp_path / "output")
    profile = tmp_path / "profile"
    profile.mkdir()
    begin, end = "<!-- AIKIT:CONTEXT7:BEGIN -->", "<!-- AIKIT:CONTEXT7:END -->"
    original = {
        "missing": begin,
        "duplicate": begin + end + begin + end,
        "reversed": end + begin,
        "override": "ajeno",
    }[case].encode()
    agents = profile / "AGENTS.md"
    agents.write_bytes(original)
    if case == "override":
        (profile / "AGENTS.override.md").write_text("ajeno", encoding="utf-8")
    assert run_install(package, "context7", profile).returncode != 0
    assert agents.read_bytes() == original
    assert not (profile / "backups").exists()


def test_catalog_resolves_to_manifest(tmp_path: Path) -> None:
    output = tmp_path / "catalog"
    package = export_aikit(ROOT, output)
    catalog = json.loads(
        (output / ".agents/plugins/marketplace.json").read_text(encoding="utf-8")
    )
    entry = catalog["plugins"][0]
    assert entry["source"]["source"] == "local"
    assert (output / entry["source"]["path"]).resolve() == package.resolve()
    manifest = json.loads((package / "plugin.json").read_text(encoding="utf-8"))
    assert entry["name"] == manifest["name"]


def test_packaged_node_installer_runs_without_source_checkout(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node no está disponible")
    package = export_aikit(ROOT, tmp_path / "export")
    profile = tmp_path / "perfil"
    profile.mkdir()
    agents = profile / "AGENTS.md"
    agents.write_text("Instrucción ajena\n", encoding="utf-8")
    cli = package / "installer/dist/cli.js"
    for template in (
        "go.md",
        "context7.md",
        "investigacion.md",
        "escritura.md",
        "visualizacion.md",
    ):
        assert (package / "installer/templates" / template).read_bytes() == (
            ROOT / "config/codex" / template
        ).read_bytes()
    result = subprocess.run(
        [
            node,
            str(cli),
            "install",
            "--codex-home",
            str(profile),
            "--escritura",
            "--visualizacion",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "changed"
    content = agents.read_text(encoding="utf-8")
    assert "Instrucción ajena" in content
    assert "AIKIT:GO:BEGIN" in content
    assert "AIKIT:CONTEXT7:BEGIN" in content
    assert "AIKIT:INVESTIGACION:BEGIN" in content
    assert "AIKIT:ESCRITURA:BEGIN" in content
    assert "AIKIT:VISUALIZACION:BEGIN" in content


@pytest.mark.parametrize("location", ["source", "output"])
def test_export_rejects_linked_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, location: str
) -> None:
    linked = tmp_path / "linked"
    source = linked / "source" if location == "source" else ROOT
    output = linked / "output" if location == "output" else tmp_path / "output"
    original = Path.is_symlink
    monkeypatch.setattr(
        Path, "is_symlink", lambda path: path == linked or original(path)
    )
    with pytest.raises(ValueError, match="enlaces"):
        export_aikit(source, output)
    assert not output.exists()


def test_second_installer_failure_preserves_first_step(tmp_path: Path) -> None:
    package = export_aikit(ROOT, tmp_path / "output")
    profile = tmp_path / "profile"
    profile.mkdir()
    agents = profile / "AGENTS.md"
    foreign = b"# Ajeno\n<!-- AIKIT:CONTEXT7:BEGIN -->\n"
    agents.write_bytes(foreign)
    first = run_install(package, "go", profile)
    assert first.returncode == 0, first.stderr
    after_first = agents.read_bytes()
    assert after_first.startswith(foreign)
    assert b"<!-- AIKIT:GO:BEGIN -->" in after_first
    second = run_install(package, "context7", profile)
    assert second.returncode != 0
    assert second.stderr
    assert agents.read_bytes() == after_first


@pytest.mark.parametrize("name", ["go", "context7"])
def test_installer_json_with_ascii_stdout(tmp_path: Path, name: str) -> None:
    package = export_aikit(ROOT, tmp_path / "output")
    profile = tmp_path / "perfil-漢"
    profile.mkdir()
    (profile / "AGENTS.md").write_bytes(b"contenido previo\n")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "ascii:strict"
    result = subprocess.run(
        [
            sys.executable,
            str(package / f"scripts/install_{name}.py"),
            "--codex-home",
            str(profile),
        ],
        capture_output=True,
        text=True,
        encoding="ascii",
        env=env,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "changed"
    assert Path(payload["backup"]).read_bytes() == b"contenido previo\n"


@pytest.mark.parametrize("name", ["escritura.md", "visualizacion.md"])
def test_export_rejects_divergent_optional_template(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    source = tmp_path / "source"
    for relative in FILES:
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    (source / "packages/aikit-installer/templates" / name).write_text(
        "divergente", encoding="utf-8"
    )
    monkeypatch.setattr(
        subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess(args, 0)
    )
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="Plantilla del instalador desactualizada"):
        export_aikit(source, output)
    assert not output.exists()
