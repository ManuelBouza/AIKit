from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from global_instructions import install_block

BEGIN = "<!-- AIKIT:ROUTING:BEGIN -->"
END = "<!-- AIKIT:ROUTING:END -->"


def install_routing(codex_home: Path, template: Path) -> Path | None:
    return install_block(codex_home, template, BEGIN, END, "routing-")


def _print_result(changed: bool, backup: Path | None) -> None:
    payload = {
        "status": "changed" if changed else "unchanged",
        "backup": str(backup) if backup is not None else None,
    }
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Instala el bloque global de enrutamiento en AGENTS.md"
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=None,
        help="Directorio CODEX_HOME (por defecto CODEX_HOME o ~/.codex)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "config" / "codex" / "routing.md",
        help="Plantilla con bloque AIKIT:ROUTING",
    )
    args = parser.parse_args()

    codex_home = args.codex_home
    if codex_home is None:
        env = os.environ.get("CODEX_HOME")
        codex_home = Path(env) if env else Path.home() / ".codex"

    try:
        backup = install_routing(codex_home, args.template)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    _print_result(backup is not None, backup)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
