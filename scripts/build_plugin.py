"""Exporta un complemento limpio y su catálogo, sin copiar el checkout completo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SOURCE_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_FILES = (
    "plugin.json",
    "mcp.json",
    "pyproject.toml",
    "uv.lock",
    "README.md",
    "docs/plugin-aikit.md",
    "docs/validacion-plugin.md",
    "docs/principios-aikit.md",
    "docs/prioridad-opencode-go.md",
    "docs/mcp-opencode.md",
    "docs/correcciones-revision-funcional.md",
    "skills/delegating-to-opencode/SKILL.md",
    "skills/delegating-to-opencode/policy.json",
    "skills/delegating-to-opencode/scripts/delegate.py",
    "skills/delegating-to-opencode/scripts/restrictions.py",
    "skills/delegating-to-opencode/scripts/mcp_server.py",
)


def _read_source(source: Path, relative: str) -> bytes:
    candidate = source / relative
    for component in (candidate, *candidate.parents):
        if component == source:
            break
        if component.is_symlink():
            raise ValueError(f"No se exportan enlaces: {relative}")
    if not candidate.resolve().is_relative_to(source):
        raise ValueError(f"Archivo fuera del origen: {relative}")
    return candidate.read_bytes()


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def export_plugin(source: Path, output: Path) -> Path:
    """Crea una salida nueva; valida todos los archivos antes de escribir."""
    source = source.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"La salida ya existe: {output}")
    output = output.resolve()
    if output.is_relative_to(source / "skills"):
        raise ValueError("La salida no puede estar dentro de las skills fuente.")
    files = {relative: _read_source(source, relative) for relative in PACKAGE_FILES}
    manifest = json.loads(files["plugin.json"])
    portable_mcp = json.loads(files["mcp.json"])
    if manifest["name"] != "aikit":
        raise ValueError("Se esperaba el paquete aikit.")
    if not isinstance(portable_mcp.get("mcpServers"), dict):
        raise ValueError("Se esperaba mcpServers en mcp.json.")
    allowed = {"type", "command", "args", "env", "cwd"}
    for server in portable_mcp["mcpServers"].values():
        if (
            not isinstance(server, dict)
            or server.get("type") != "stdio"
            or set(server) - allowed
        ):
            raise ValueError(
                "MCP portable: se esperaba STDIO sin campos específicos de Codex."
            )
    # No sobrescribir ni borrar: un fallo de E/S puede dejar una salida parcial.
    output.mkdir(parents=True, exist_ok=False)
    package = output / "aikit"
    for relative, content in files.items():
        destination = package / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    catalog = output / ".agents/plugins/marketplace.json"
    catalog.parent.mkdir(parents=True, exist_ok=True)
    marketplace = {
        "name": "aikit-local",
        "interface": {"displayName": "AIKit privado"},
        "plugins": [
            {
                "name": "aikit",
                "source": {"source": "local", "path": "./aikit"},
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Developer Tools",
            }
        ],
    }
    catalog.write_bytes(_json_bytes(marketplace))
    return package


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Directorio nuevo")
    args = parser.parse_args()
    try:
        package = export_plugin(SOURCE_ROOT, args.output)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"No se pudo exportar AIKit: {exc}\n")
    print(package)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
