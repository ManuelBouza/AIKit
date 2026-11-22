from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from build_aikit import FILES, INVENTORY, export_aikit

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
    assert not (package / "scripts/seguimiento_tareas.py").exists()
    assert not (package / "coordinacion").exists()
    assert not (package / "skills/coordinacion-chats").exists()
    for document in (package / "skills/aikit-setup/SKILL.md",):
        for target in re.findall(
            r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")
        ):
            destination = (document.parent / target).resolve()
            assert destination.is_relative_to(package.resolve()), target
            assert destination.is_file(), target
    assert not (package / "skills/delegating-to-opencode").exists()
    assert not (package / "packages/aikit-coordination").exists()
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
    inventory = json.loads((package / INVENTORY).read_text(encoding="utf-8"))
    names = [entry["id"] for entry in inventory if entry["tipo"] == "preferencia"]
    options = [f"--{name}" for name in names]
    original = agents.read_bytes()
    assert {path.name for path in profile.iterdir()} == {"AGENTS.md"}
    cli = package / "installer/dist/cli.js"
    env = {**os.environ, "CODEX_HOME": str(profile)}

    def run(
        *args: str, cwd: Path = tmp_path, success: bool = True
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [node, str(cli), *args],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        assert (result.returncode == 0) == success, result.stderr
        return result

    preview = json.loads(run("install", "--global", "--dry-run", *options).stdout)
    assert preview["status"] == "preview"
    assert preview["before"] == original.decode("utf-8")
    assert preview["backup"] is None
    assert agents.read_bytes() == original
    assert not (profile / "backups").exists()
    assert (
        json.loads(run("install", "--global", *options).stdout)["status"] == "changed"
    )
    configured = agents.read_bytes()
    assert configured.startswith(original)
    assert preview["after"] == configured.decode("utf-8")
    for name in names:
        assert f"AIKIT:{name.upper()}:BEGIN".encode() in configured
    assert (
        json.loads(run("install", "--global", *options).stdout)["status"] == "unchanged"
    )

    remove_flag = "--quitar-visualizacion"
    run("install", "--global", "--dry-run", remove_flag)
    assert agents.read_bytes() == configured
    removal = json.loads(run("install", "--global", remove_flag).stdout)
    assert Path(removal["backup"]).read_bytes() == configured
    remaining = agents.read_bytes()
    assert remaining.startswith(original)
    assert b"AIKIT:VISUALIZACION:BEGIN" not in remaining
    assert b"AIKIT:ESCRITURA:BEGIN" in remaining

    project = tmp_path / "proyecto"
    project.mkdir()
    repo = subprocess.run(
        ["git", "init", "-q", str(project)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert repo.returncode == 0, repo.stderr
    project_agents = project / "AGENTS.md"
    project_agents.write_bytes(original)
    workdir = project / "subdirectorio"
    workdir.mkdir()
    preview = json.loads(
        run("install", "--project", "--dry-run", "--visualizacion", cwd=workdir).stdout
    )
    assert Path(preview["path"]) == project_agents
    assert project_agents.read_bytes() == original
    applied = json.loads(
        run("install", "--project", "--visualizacion", cwd=workdir).stdout
    )
    assert Path(applied["backup"]).read_bytes() == original
    assert project_agents.read_bytes() == preview["after"].encode("utf-8")
    assert b"AIKIT:VISUALIZACION:BEGIN" in project_agents.read_bytes()
    assert b"AIKIT:GO:BEGIN" not in project_agents.read_bytes()
    assert agents.read_bytes() == remaining

    (profile / "AGENTS.override.md").write_bytes(b"instrucciones prioritarias\n")
    run("install", "--global", "--dry-run", "--visualizacion", success=False)
    assert agents.read_bytes() == remaining


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


@pytest.fixture
def export_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    source = tmp_path / "source"
    for relative in FILES:
        destination = source / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    monkeypatch.setattr(
        subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess(args, 0)
    )
    return source


@pytest.mark.parametrize("name", ["escritura.md", "visualizacion.md"])
def test_export_rejects_divergent_optional_template(
    tmp_path: Path, export_source: Path, name: str
) -> None:
    (export_source / "packages/aikit-installer/templates" / name).write_text(
        "divergente", encoding="utf-8"
    )
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="Plantilla del instalador desactualizada"):
        export_aikit(export_source, output)
    assert not output.exists()


@pytest.mark.parametrize("name", ["director-de-ideas", "go", "responsabilidad-chats"])
def test_export_rejects_missing_inventory_entry(
    tmp_path: Path, export_source: Path, name: str
) -> None:
    path = export_source / "packaging" / INVENTORY
    entries = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(
        json.dumps([entry for entry in entries if entry["id"] != name]),
        encoding="utf-8",
    )
    output = tmp_path / "output"
    with pytest.raises(ValueError, match=f"Cobertura del inventario.*{name}"):
        export_aikit(export_source, output)
    assert not output.exists()


def test_exported_setup_chat_flow_without_git(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node no está disponible")
    package = export_aikit(ROOT, tmp_path / "output")
    capabilities = json.loads((package / INVENTORY).read_text(encoding="utf-8"))
    entry = next(item for item in capabilities if item["id"] == "responsabilidad-chats")
    assert entry["tipo"] == "guiada"
    guide = (package / entry["ruta"]).read_text(encoding="utf-8")
    assert "project-chats enable" in guide
    assert "project-chats disable" in guide
    project = tmp_path / "proyecto sin Git"
    project.mkdir()
    profile = tmp_path / "perfil ficticio"
    profile.mkdir()
    global_instructions = profile / "AGENTS.md"
    global_instructions.write_bytes(b"# Perfil ajeno\n")
    instructions = project / "AGENTS.md"
    original = b"# Proyecto ajeno\r\n"
    instructions.write_bytes(original)

    def chats(*args: str, data: str | None = None) -> dict[str, object]:
        result = subprocess.run(
            [
                node,
                str(package / "installer/dist/cli.js"),
                "project-chats",
                *args,
                "--root",
                str(project),
            ],
            input=data,
            cwd=tmp_path,
            env={**os.environ, "CODEX_HOME": str(profile)},
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        response = json.loads(result.stdout)
        assert isinstance(response, dict)
        return response

    assert chats("status")["status"] == "disabled"
    assert chats("enable", "--dry-run")["status"] == "preview"
    assert list(project.iterdir()) == [instructions]
    assert instructions.read_bytes() == original
    assert chats("enable")["status"] == "changed"
    assert chats("status")["status"] == "enabled"
    data = json.dumps(
        {
            "id": "00000000-0000-4000-8000-000000000001",
            "project": "Ejemplo",
            "responsibility": "Preparar pruebas",
            "state": "En curso",
        }
    )
    assert chats("upsert", "--expected-revision", "0", data=data)["status"] == "changed"
    records = chats("list")["records"]
    assert isinstance(records, list)
    assert len(records) == 1
    assert records[0]["title"] == "[En curso] Ejemplo · Preparar pruebas"
    assert chats("disable", "--dry-run")["status"] == "preview"
    assert chats("disable")["status"] == "changed"
    assert instructions.read_bytes() == original
    assert chats("list")["records"] == records
    assert global_instructions.read_bytes() == b"# Perfil ajeno\n"


def test_export_rejects_invalid_inventory_reference(
    tmp_path: Path, export_source: Path
) -> None:
    path = export_source / "packaging" / INVENTORY
    entries = json.loads(path.read_text(encoding="utf-8"))
    director = next(entry for entry in entries if entry["id"] == "director-de-ideas")
    director["ruta"] = "no-existe.md"
    path.write_text(json.dumps(entries), encoding="utf-8")
    output = tmp_path / "output"
    with pytest.raises(
        ValueError, match="inválida en el inventario.*director-de-ideas"
    ):
        export_aikit(export_source, output)
    assert not output.exists()


@pytest.mark.parametrize(
    ("reference", "error"),
    [
        ("[enlace](no-existe.md)", "Referencia"),
        ('[enlace](no-existe.md "título")', "Referencia"),
        ("[enlace][ref]\n\n[ref]: no-existe.md", "Referencia"),
        ("[enlace][ref]\n\n[ref]:\n  no-existe.md", "Referencia"),
        ("[enlace](#no-existe)", "Fragmento"),
        ("```markdown\n# Ejemplo\n````\n\n[enlace](no-existe.md)", "Referencia"),
    ],
)
def test_export_rejects_invalid_guided_reference(
    tmp_path: Path, export_source: Path, reference: str, error: str
) -> None:
    path = export_source / "packaging/skills/aikit-setup/SKILL.md"
    path.write_text(reference + "\n", encoding="utf-8")
    output = tmp_path / "output"
    with pytest.raises(
        ValueError, match=f"{error} de setup o skill inexistente.*no-existe"
    ):
        export_aikit(export_source, output)
    assert not output.exists()


def test_export_rejects_skill_absent_from_package(
    tmp_path: Path, export_source: Path
) -> None:
    skill = export_source / "packaging/skills/nueva/SKILL.md"
    skill.parent.mkdir()
    skill.write_text("# Skill nueva\n", encoding="utf-8")
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="Cobertura del exportador.*nueva/SKILL.md"):
        export_aikit(export_source, output)
    assert not output.exists()


def test_export_rejects_preference_absent_from_installer(
    tmp_path: Path, export_source: Path
) -> None:
    path = export_source / "packages/aikit-installer/package.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    del manifest["aikitPreferences"]["go"]
    path.write_text(json.dumps(manifest), encoding="utf-8")
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="Cobertura del instalador.*go.md"):
        export_aikit(export_source, output)
    assert not output.exists()


def test_export_ignores_example_links_in_fenced_code(
    tmp_path: Path, export_source: Path
) -> None:
    path = export_source / "packaging/skills/aikit-setup/SKILL.md"
    with path.open("a", encoding="utf-8") as target:
        target.write("\n```markdown\n[ejemplo](no-existe.md)\n```\n")
    package = export_aikit(export_source, tmp_path / "output")
    assert (package / "skills/aikit-setup/SKILL.md").read_bytes() == path.read_bytes()
