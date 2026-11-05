"""Motor común para instalar bloques globales en AGENTS.md de Codex."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from pathlib import Path

_PREFIX_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _reject_symlinks(*paths: Path) -> None:
    for p in paths:
        cur = p
        while True:
            if cur.is_symlink():
                raise ValueError(f"Ruta symlink no permitida: {cur}")
            if cur.parent == cur:
                break
            cur = cur.parent


def _validate_prefix(backup_prefix: str) -> None:
    if not backup_prefix or not _PREFIX_RE.fullmatch(backup_prefix):
        raise ValueError("Prefijo de respaldo inválido")


def _validate_markers(begin: str, end: str) -> None:
    if not begin or not end:
        raise ValueError("Marcadores vacíos")
    if begin == end:
        raise ValueError("Marcadores idénticos")
    if not begin.startswith("<!--") or not end.startswith("<!--"):
        raise ValueError("Marcadores malformados")
    if not begin.endswith("-->") or not end.endswith("-->"):
        raise ValueError("Marcadores malformados")


def install_block(
    codex_home: Path,
    template: Path,
    begin: str,
    end: str,
    backup_prefix: str,
) -> Path | None:
    _validate_prefix(backup_prefix)
    _validate_markers(begin, end)

    codex_home = codex_home.expanduser()
    template = template.expanduser()
    _reject_symlinks(codex_home, template)
    if not template.is_file() or template.is_symlink():
        raise ValueError("Plantilla inválida")
    template_text = template.read_text(encoding="utf-8")
    if template_text.count(begin) != 1 or template_text.count(end) != 1:
        raise ValueError("Marcadores inválidos en plantilla")
    if template_text.index(begin) > template_text.index(end):
        raise ValueError("Marcadores mal ordenados en plantilla")
    block = template_text[
        template_text.index(begin) : template_text.index(end) + len(end)
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

    bom = b""
    working = original_bytes
    if working.startswith(b"\xef\xbb\xbf"):
        bom = b"\xef\xbb\xbf"
        working = working[3:]
    text = working.decode("utf-8") if working else ""

    if text.count(begin) > 1 or text.count(end) > 1:
        raise ValueError("Marcadores duplicados en destino")
    if (begin in text) != (end in text):
        raise ValueError("Marcadores malformados en destino")
    if begin in text and text.index(begin) > text.index(end):
        raise ValueError("Marcadores mal ordenados en destino")

    if begin in text:
        start = text.index(begin)
        end_idx = text.index(end) + len(end)
        new_body = text[:start] + block + text[end_idx:]
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

        backup_dir = codex_home / "backups" / "aikit" / f"{backup_prefix}{uuid.uuid4()}"
        backup_path = backup_dir / "AGENTS.md"
        _reject_symlinks(backup_dir, backup_path)
        backup_dir.mkdir(parents=True, exist_ok=False)
        if existed:
            backup_path.write_bytes(original_bytes)
        else:
            (backup_dir / "STATE.txt").write_text(
                "AGENTS.md no existía originalmente.\n", encoding="utf-8"
            )

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
        description="Instala un bloque global en AGENTS.md (motor común)"
    )
    parser.add_argument("--codex-home", type=Path, default=None)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--begin", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--backup-prefix", required=True)
    args = parser.parse_args()

    codex_home = args.codex_home
    if codex_home is None:
        env = os.environ.get("CODEX_HOME")
        codex_home = Path(env) if env else Path.home() / ".codex"

    try:
        backup = install_block(
            codex_home, args.template, args.begin, args.end, args.backup_prefix
        )
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    _print_result(backup is not None, backup)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
