from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

BEGIN = "<!-- AIKIT:GO:BEGIN -->"
END = "<!-- AIKIT:GO:END -->"


def _reject_symlinks(*paths: Path) -> None:
    for p in paths:
        cur = p
        while True:
            if cur.is_symlink():
                raise ValueError(f"Ruta symlink no permitida: {cur}")
            if cur.parent == cur:
                break
            cur = cur.parent


def install_go(codex_home: Path, template: Path) -> Path | None:
    codex_home = codex_home.expanduser()
    template = template.expanduser()
    _reject_symlinks(codex_home, template)
    if not template.is_file() or template.is_symlink():
        raise ValueError("Plantilla inválida")
    template_text = template.read_text(encoding="utf-8")
    if template_text.count(BEGIN) != 1 or template_text.count(END) != 1:
        raise ValueError("Marcadores inválidos en plantilla")
    if template_text.index(BEGIN) > template_text.index(END):
        raise ValueError("Marcadores mal ordenados en plantilla")
    block = template_text[
        template_text.index(BEGIN) : template_text.index(END) + len(END)
    ]

    agents = codex_home / "AGENTS.md"
    override = codex_home / "AGENTS.override.md"
    _reject_symlinks(agents, override, codex_home)

    if override.exists():
        if override.is_symlink():
            raise ValueError("AGENTS.override.md symlink no permitido")
        if override.read_bytes():
            raise ValueError("AGENTS.override.md global no vacío")

    existed = agents.exists()
    if existed:
        if agents.is_symlink():
            raise ValueError("AGENTS.md symlink no permitido")
        original_bytes = agents.read_bytes()
    else:
        original_bytes = b""

    # Validación inicial conservadora; se revalida inmediatamente antes de os.replace.
    bom = b""
    working = original_bytes
    if working.startswith(b"\xef\xbb\xbf"):
        bom = b"\xef\xbb\xbf"
        working = working[3:]
    text = working.decode("utf-8") if working else ""

    if text.count(BEGIN) > 1 or text.count(END) > 1:
        raise ValueError("Marcadores duplicados en destino")
    if (BEGIN in text) != (END in text):
        raise ValueError("Marcadores malformados en destino")
    if BEGIN in text and text.index(BEGIN) > text.index(END):
        raise ValueError("Marcadores mal ordenados en destino")

    if BEGIN in text:
        start = text.index(BEGIN)
        end = text.index(END) + len(END)
        new_body = text[:start] + block + text[end:]
    else:
        if text == "":
            new_body = block
        else:
            new_body = text
            if not new_body.endswith("\n"):
                new_body += "\n"
            new_body += block
            if not new_body.endswith("\n"):
                new_body += "\n"

    new_bytes = bom + new_body.encode("utf-8")
    if new_bytes == original_bytes:
        return None

    codex_home.mkdir(parents=True, exist_ok=True)
    tmp = codex_home / f".agents.md.tmp-{uuid.uuid4()}"
    try:
        tmp.write_bytes(new_bytes)

        backup_dir = codex_home / "backups" / "aikit" / f"go-{uuid.uuid4()}"
        backup_path = backup_dir / "AGENTS.md"
        _reject_symlinks(backup_dir, backup_path)
        backup_dir.mkdir(parents=True, exist_ok=False)
        if existed:
            backup_path.write_bytes(original_bytes)
        else:
            (backup_dir / "STATE.txt").write_text(
                "AGENTS.md no existía originalmente.\n", encoding="utf-8"
            )

        # Revalidación final: existencia, symlink y bytes. Ventana TOCTOU residual.
        _reject_symlinks(agents, codex_home)
        if existed:
            if (not agents.exists()) or agents.is_symlink():
                raise ValueError("Modificación concurrente detectada")
            current = agents.read_bytes()
            if current != original_bytes:
                raise ValueError("Modificación concurrente detectada")
        else:
            if agents.exists():
                raise ValueError("Modificación concurrente detectada")

        os.replace(tmp, agents)
    except Exception:
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass
        raise
    return backup_path if existed else backup_dir


def _print_result(changed: bool, backup: Path | None) -> None:
    payload = {
        "status": "changed" if changed else "unchanged",
        "backup": str(backup) if backup is not None else None,
    }
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Instala el bloque global go en AGENTS.md"
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
        default=Path(__file__).resolve().parents[1] / "config" / "codex" / "go.md",
        help="Plantilla con bloque AIKit:GO",
    )
    args = parser.parse_args()

    codex_home = args.codex_home
    if codex_home is None:
        env = os.environ.get("CODEX_HOME")
        codex_home = Path(env) if env else Path.home() / ".codex"

    try:
        backup = install_go(codex_home, args.template)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    _print_result(backup is not None, backup)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
