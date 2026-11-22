"""Exporta el complemento independiente AIKit y su catálogo local."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build_go import _reject_links

SOURCE_ROOT = Path(__file__).absolute().parents[1]
PACKAGE = "aikit-preferencias"
SETUP = "skills/aikit-setup/SKILL.md"
INVENTORY = "skills/aikit-setup/references/capacidades.json"
FLOWS = "skills/aikit-setup/references/flujos"
FILES = {
    "packaging/assets/aikit-icon.png": "aikit-preferencias/assets/aikit-icon.png",
    "packaging/skills/aikit-setup/SKILL.md": "aikit-preferencias/skills/aikit-setup/SKILL.md",
    "packaging/skills/director-de-ideas/SKILL.md": "aikit-preferencias/skills/director-de-ideas/SKILL.md",
    "packaging/skills/aikit-setup/references/herramientas.md": "aikit-preferencias/skills/aikit-setup/references/herramientas.md",
    f"packaging/{INVENTORY}": f"{PACKAGE}/{INVENTORY}",
    "packaging/aikit-plugin.json": "aikit-preferencias/plugin.json",
    "packaging/aikit-marketplace.json": ".agents/plugins/marketplace.json",
    "docs/complemento-aikit-independiente.md": "aikit-preferencias/README.md",
    "config/codex/go.md": "aikit-preferencias/config/codex/go.md",
    "config/codex/context7.md": "aikit-preferencias/config/codex/context7.md",
    "config/codex/escritura.md": "aikit-preferencias/config/codex/escritura.md",
    "config/codex/visualizacion.md": "aikit-preferencias/config/codex/visualizacion.md",
    "config/codex/investigacion.md": "aikit-preferencias/config/codex/investigacion.md",
    "scripts/global_instructions.py": "aikit-preferencias/scripts/global_instructions.py",
    "scripts/install_go.py": "aikit-preferencias/scripts/install_go.py",
    "scripts/install_context7.py": "aikit-preferencias/scripts/install_context7.py",
    "packages/aikit-installer/package.json": "aikit-preferencias/installer/package.json",
    "packages/aikit-installer/LICENSE": "aikit-preferencias/installer/LICENSE",
    "packages/aikit-installer/templates/go.md": "aikit-preferencias/installer/templates/go.md",
    "packages/aikit-installer/templates/context7.md": "aikit-preferencias/installer/templates/context7.md",
    "packages/aikit-installer/templates/escritura.md": "aikit-preferencias/installer/templates/escritura.md",
    "packages/aikit-installer/templates/visualizacion.md": "aikit-preferencias/installer/templates/visualizacion.md",
    "packages/aikit-installer/templates/investigacion.md": "aikit-preferencias/installer/templates/investigacion.md",
    "packages/aikit-installer/dist/cli.js": "aikit-preferencias/installer/dist/cli.js",
    "packages/aikit-installer/dist/windows-replace.js": "aikit-preferencias/installer/dist/windows-replace.js",
    "packages/aikit-installer/dist/replace-recovery.js": "aikit-preferencias/installer/dist/replace-recovery.js",
}


def _require_coverage(expected: set[str], declared: set[str], label: str) -> None:
    missing = sorted(expected - declared)
    extra = sorted(declared - expected)
    if missing or extra:
        raise ValueError(f"{label}: faltan {missing}; sobran {extra}")


def _markdown_without_code(content: bytes) -> str:
    text = content.decode("utf-8").replace("\r\n", "\n")
    return re.sub(
        r"(?ms)^ {0,3}(?P<fence>(?P<marker>[`~])(?P=marker){2,})[^\n]*\n"
        r".*?(?:^ {0,3}(?P=fence)(?P=marker)*[ \t]*(?:\n|$)|\Z)",
        "\n",
        text,
    )


def _validate_skill_links(package: dict[str, bytes]) -> None:
    for path, content in package.items():
        if not path.startswith("skills/") or not path.endswith(".md"):
            continue
        links = re.findall(
            r"(?m)(?:\]\(\s*|^ {0,3}\[[^\]\n]+\]:[ \t]*(?:\n[ \t]*)?)"
            r"(?:<([^>\n]+)>|([^\s)]+))",
            _markdown_without_code(content),
        )
        for wrapped, bare in links:
            link = wrapped or bare
            target = urlsplit(link)
            if target.scheme or target.netloc:
                continue
            resolved = path
            if target.path:
                resolved = posixpath.normpath(
                    posixpath.join(posixpath.dirname(path), unquote(target.path))
                )
            if resolved not in package:
                raise ValueError(
                    f"Referencia de setup o skill inexistente: {path} → {link}"
                )
            if target.fragment and resolved.endswith(".md"):
                headings = re.findall(
                    r"(?m)^#{1,6} +(.+)$", _markdown_without_code(package[resolved])
                )
                anchors = {
                    re.sub(r"[^\w -]", "", heading.lower()).strip().replace(" ", "-")
                    for heading in headings
                }
                if unquote(target.fragment) not in anchors:
                    raise ValueError(
                        f"Fragmento de setup o skill inexistente: {path} → {link}"
                    )


def _validate_setup(source: Path, files: dict[str, bytes]) -> None:
    package = {
        path.removeprefix(f"{PACKAGE}/"): content
        for path, content in files.items()
        if path.startswith(f"{PACKAGE}/")
    }
    inventory = json.loads(package[INVENTORY])
    if not isinstance(inventory, list):
        raise ValueError("El inventario de setup debe ser una lista de capacidades")
    declared: set[str] = set()
    ids: set[str] = set()
    for entry in inventory:
        if not isinstance(entry, dict) or any(
            not isinstance(entry.get(key), str) or not entry[key].strip()
            for key in ("id", "tipo", "ruta", "proposito")
        ):
            raise ValueError("Entrada incompleta en el inventario de setup")
        name = entry["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or name in ids:
            raise ValueError(f"Identificador inválido o repetido en setup: {name}")
        ids.add(name)
        skill = f"skills/{name}/SKILL.md"
        routes = {
            "skill": skill,
            "preferencia": f"installer/templates/{name}.md",
            "guiada": f"{FLOWS}/{name}.md",
        }
        route = entry["ruta"]
        if route not in package or route != routes.get(entry["tipo"]):
            raise ValueError(
                f"Ruta inválida en el inventario de setup ({name}): {route}"
            )
        declared.add(route)
        if "skill" in entry:
            if (
                entry["tipo"] != "guiada"
                or entry["skill"] != skill
                or skill not in package
            ):
                raise ValueError(
                    f"Skill de apoyo inválida en el inventario de setup: {name}"
                )
            declared.add(skill)

    patterns = ("skills/*/SKILL.md", "installer/templates/*.md", f"{FLOWS}/*.md")
    shipped = {
        path
        for path in package
        if any(Path(path).match(pattern) for pattern in patterns)
    }
    _require_coverage(shipped, declared, "Cobertura del inventario de setup")
    packaging = source / "packaging"
    available = {
        path.relative_to(packaging).as_posix()
        for pattern in (patterns[0], patterns[2])
        for path in packaging.glob(pattern)
        if path.is_file()
    }
    available.update(
        f"installer/templates/{path.name}"
        for path in (source / "packages/aikit-installer/templates").glob("*.md")
        if path.is_file()
    )
    _require_coverage(available, shipped, "Cobertura del exportador")

    templates = {
        posixpath.basename(path)
        for path in shipped
        if path.startswith("installer/templates/")
    }
    prefs = json.loads(package["installer/package.json"]).get("aikitPreferences")
    if not isinstance(prefs, dict) or any(
        not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
        or name in {"global", "project", "codex-home", "dry-run"}
        or name.startswith("quitar-")
        or not isinstance(default, bool)
        for name, default in prefs.items()
    ):
        raise ValueError("Preferencias inválidas en el manifiesto del instalador")
    _require_coverage(
        {f"{name}.md" for name in prefs}, templates, "Cobertura del instalador"
    )
    configs = {
        posixpath.basename(path) for path in package if path.startswith("config/codex/")
    }
    _require_coverage(templates, configs, "Cobertura de preferencias distribuidas")
    for name in sorted(templates):
        if package[f"installer/templates/{name}"] != package[f"config/codex/{name}"]:
            raise ValueError(f"Plantilla del instalador desactualizada: {name}")

    _validate_skill_links(package)

    manifest = json.loads(package["plugin.json"])
    onboarding = manifest["extensions"]["com.openai"]["onboardingSkill"]
    if (
        onboarding != f"./{SETUP}"
        or f"(references/{posixpath.basename(INVENTORY)})"
        not in package[SETUP].decode("utf-8")
    ):
        raise ValueError("El onboarding debe enlazar al inventario desde aikit-setup")


def export_aikit(source: Path, output: Path) -> Path:
    """Valida las fuentes y crea una salida nueva sin sobrescribir."""
    source, output = source.absolute(), output.absolute()
    _reject_links(source)
    _reject_links(output)
    if not source.is_dir():
        raise ValueError("La raíz de fuentes debe ser un directorio sin enlace")
    source = source.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"La salida ya existe: {output}")
    installer = source / "packages/aikit-installer"
    _reject_links(installer)
    _reject_links(installer / "dist")
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if npm is None:
        raise ValueError("Se requiere Node.js y npm para compilar el instalador AIKit")
    result = subprocess.run(
        [npm, "run", "build"],
        cwd=installer,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(
            f"No se pudo compilar el instalador AIKit: {result.stderr or result.stdout}"
        )
    files: dict[str, bytes] = {}
    for relative, destination_name in FILES.items():
        candidate = source / relative
        _reject_links(candidate)
        if not candidate.resolve().is_relative_to(source):
            raise ValueError(f"Archivo fuera del origen: {relative}")
        files[destination_name] = candidate.read_bytes()
    _validate_setup(source, files)
    output.mkdir(parents=True, exist_ok=False)
    try:
        for relative, content in files.items():
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
    except OSError as exc:
        raise OSError(f"Exportación incompleta en {output}: {exc}") from exc
    return output / "aikit-preferencias"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Directorio nuevo")
    args = parser.parse_args()
    try:
        package = export_aikit(SOURCE_ROOT, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"No se pudo exportar AIKit: {exc}\n")
    print(package)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
