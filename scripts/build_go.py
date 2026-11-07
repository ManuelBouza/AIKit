"""Exporta el instalador de go como directorio portable independiente."""

from __future__ import annotations

import argparse
import stat
from pathlib import Path

SOURCE_ROOT = Path(__file__).absolute().parents[1]
FILES = {
    "docs/artefacto-go-readme.md": "README.md",
    "config/codex/go.md": "config/codex/go.md",
    "scripts/global_instructions.py": "scripts/global_instructions.py",
    "scripts/install_go.py": "scripts/install_go.py",
}


def _reject_links(path: Path) -> None:
    """Rechaza enlaces y puntos de reanálisis, incluidos sus antecesores."""
    for component in (path, *path.parents):
        if component.is_symlink():
            raise ValueError(f"No se permiten enlaces: {component}")
        try:
            attributes = getattr(component.lstat(), "st_file_attributes", 0)
        except FileNotFoundError:
            continue
        if attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            raise ValueError(
                f"No se permiten enlaces o puntos de reanálisis: {component}"
            )


def export_go(source: Path, output: Path) -> Path:
    """Valida las fuentes antes de crear una salida nueva, sin sobrescribir."""
    source = source.absolute()
    output = output.absolute()
    _reject_links(source)
    _reject_links(output)
    if not source.is_dir():
        raise ValueError("La raíz de fuentes debe ser un directorio sin enlace")
    source = source.resolve()
    files: dict[str, bytes] = {}
    for relative, destination in FILES.items():
        candidate = source / relative
        _reject_links(candidate)
        if not candidate.resolve().is_relative_to(source):
            raise ValueError(f"Archivo fuera del origen: {relative}")
        files[destination] = candidate.read_bytes()

    if output.exists() or output.is_symlink():
        raise FileExistsError(f"La salida ya existe: {output}")
    output.mkdir(parents=True, exist_ok=False)
    try:
        for relative, content in files.items():
            destination_path = output / relative
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            destination_path.write_bytes(content)
    except OSError as exc:
        raise OSError(f"Exportación incompleta en {output}: {exc}") from exc
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Directorio nuevo")
    args = parser.parse_args()
    try:
        output = export_go(SOURCE_ROOT, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"No se pudo exportar go: {exc}\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
