"""Exporta el complemento independiente AIKit y su catálogo local."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from build_go import _reject_links

SOURCE_ROOT = Path(__file__).absolute().parents[1]
FILES = {
    "packaging/assets/aikit-icon.png": "aikit-preferencias/assets/aikit-icon.png",
    "packaging/skills/aikit-setup/SKILL.md": "aikit-preferencias/skills/aikit-setup/SKILL.md",
    "packaging/skills/director-de-ideas/SKILL.md": "aikit-preferencias/skills/director-de-ideas/SKILL.md",
    "packaging/skills/aikit-setup/references/herramientas.md": "aikit-preferencias/skills/aikit-setup/references/herramientas.md",
    "packaging/aikit-plugin.json": "aikit-preferencias/plugin.json",
    "packaging/aikit-marketplace.json": ".agents/plugins/marketplace.json",
    "docs/complemento-aikit-independiente.md": "aikit-preferencias/README.md",
    "config/codex/go.md": "aikit-preferencias/config/codex/go.md",
    "config/codex/context7.md": "aikit-preferencias/config/codex/context7.md",
    "config/codex/investigacion.md": "aikit-preferencias/config/codex/investigacion.md",
    "scripts/global_instructions.py": "aikit-preferencias/scripts/global_instructions.py",
    "scripts/install_go.py": "aikit-preferencias/scripts/install_go.py",
    "scripts/install_context7.py": "aikit-preferencias/scripts/install_context7.py",
    "packages/aikit-installer/package.json": "aikit-preferencias/installer/package.json",
    "packages/aikit-installer/LICENSE": "aikit-preferencias/installer/LICENSE",
    "packages/aikit-installer/templates/go.md": "aikit-preferencias/installer/templates/go.md",
    "packages/aikit-installer/templates/context7.md": "aikit-preferencias/installer/templates/context7.md",
    "packages/aikit-installer/templates/investigacion.md": "aikit-preferencias/installer/templates/investigacion.md",
    "packages/aikit-installer/dist/cli.js": "aikit-preferencias/installer/dist/cli.js",
    "packages/aikit-installer/dist/windows-replace.js": "aikit-preferencias/installer/dist/windows-replace.js",
    "packages/aikit-installer/dist/replace-recovery.js": "aikit-preferencias/installer/dist/replace-recovery.js",
}


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
    for name in ("go.md", "context7.md", "investigacion.md"):
        if (
            files[f"aikit-preferencias/installer/templates/{name}"]
            != files[f"aikit-preferencias/config/codex/{name}"]
        ):
            raise ValueError(f"Plantilla del instalador desactualizada: {name}")
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
