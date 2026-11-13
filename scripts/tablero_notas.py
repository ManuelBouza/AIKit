"""Genera y abre una instantánea local del backlog de notas."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import tempfile
import webbrowser
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import mistune

ROOT = Path(__file__).resolve().parents[1]
ROW = re.compile(
    r"^\|\s*\[(\d{3})\s*[—–-]\s*(.+?)\]\(([^)]+)\)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$"
)


class SafeRenderer(mistune.HTMLRenderer):
    """Presenta enlaces e imágenes como texto, sin acceso externo."""

    def link(self, text: str, url: str, title: str | None = None) -> str:
        return f"{text} ({html.escape(url)})"

    def image(self, text: str, url: str, title: str | None = None) -> str:
        return f"{html.escape(text)} ({html.escape(url)})"


@dataclass(frozen=True)
class Note:
    number: str
    title: str
    group: str
    status: str
    summary: str
    content: str


def read_notes(directory: Path) -> list[Note]:
    """Lee las tablas de notas y rechaza entradas incompletas o inseguras."""
    directory = directory.resolve()
    lines = (directory / "IDEAS.md").read_text(encoding="utf-8").splitlines()
    render = mistune.create_markdown(
        renderer=SafeRenderer(escape=True), plugins=["table"]
    )
    notes: list[Note] = []
    seen: set[str] = set()
    group = ""
    in_table = False
    for lineno, line in enumerate(lines, 1):
        if line.startswith("## "):
            group = line[3:].strip()
            in_table = False
        elif re.match(r"^\|\s*Nota\s*\|\s*Estado\s*\|\s*Idea\s*\|", line):
            in_table = True
        elif in_table and line.startswith("|"):
            if re.match(r"^\|[\s|:-]+$", line):
                continue
            match = ROW.fullmatch(line)
            if not match:
                raise ValueError(f"IDEAS.md:{lineno}: fila de nota inválida")
            number, title, path, status, summary = match.groups()
            candidate = (directory / path).resolve()
            if (
                number in seen
                or candidate.parent != directory
                or not candidate.is_file()
                or not candidate.name.startswith(f"{number}-")
            ):
                raise ValueError(
                    f"IDEAS.md:{lineno}: número duplicado o ruta de nota inválida: {path}"
                )
            seen.add(number)
            content = render(candidate.read_text(encoding="utf-8"))
            if not isinstance(content, str):
                raise ValueError(f"No se pudo renderizar la nota {number}")
            notes.append(Note(number, title, group, status, summary, content))
        elif re.search(r"\[\d{3}\s*[—–-]", line):
            raise ValueError(f"IDEAS.md:{lineno}: fila de nota fuera de tabla válida")
        elif in_table and line.strip() and not line.startswith("|"):
            in_table = False
    if not notes:
        raise ValueError("IDEAS.md no contiene notas reconocidas")
    present = {p.name[:3] for p in directory.glob("[0-9][0-9][0-9]-*.md")}
    missing = present - seen
    if missing:
        raise ValueError(f"IDEAS.md no incluye notas: {', '.join(sorted(missing))}")
    return notes


def generate(directory: Path, output: Path) -> int:
    notes = read_notes(directory)
    template = (ROOT / "scripts/tablero_notas.html").read_text(encoding="utf-8")
    payload = (
        json.dumps([asdict(n) for n in notes], ensure_ascii=True)
        .replace("<", r"\u003c")
        .replace(">", r"\u003e")
        .replace("&", r"\u0026")
    )
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    document = template.replace("__GENERATED__", html.escape(stamp)).replace(
        "__NOTES_JSON__", payload
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=output.parent, delete=False, suffix=".tmp"
        ) as temp:
            temp_name = temp.name
            temp.write(document)
        os.replace(temp_name, output)
    finally:
        if temp_name and Path(temp_name).exists():
            Path(temp_name).unlink()
    return len(notes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sin-abrir", action="store_true", help="Genera sin abrir el navegador"
    )
    args = parser.parse_args()
    output = ROOT / ".aikit/tablero-notas/index.html"
    try:
        count = generate(ROOT / "notas", output)
        print(f"Tablero generado: {count} notas; {output}")
        if not args.sin_abrir and not webbrowser.open(output.resolve().as_uri()):
            print("No se pudo abrir el navegador; abre la ruta indicada manualmente.")
            return 1
    except (OSError, ValueError) as exc:
        print(f"No se generó el tablero: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
