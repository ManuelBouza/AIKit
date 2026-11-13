"""Comportamiento del generador local de notas."""

from pathlib import Path
from unittest.mock import patch

import pytest
from tablero_notas import generate, main, read_notes

HEADER = "## Abiertas\n\n| Nota | Estado | Idea |\n| --- | --- | --- |\n"
ROW = "| [001 — Prueba](001-prueba.md) | Pendiente | Texto |\n"


def test_generation_escapes_untrusted_markdown(tmp_path: Path) -> None:
    notes = tmp_path / "notas"
    notes.mkdir()
    (notes / "IDEAS.md").write_text(HEADER + ROW, encoding="utf-8")
    (notes / "001-prueba.md").write_text(
        "# Título\n\n<script>alert(1)</script>\n\n[enlace](javascript:alert(1))\n\n"
        "![imagen](https://example.com/x.png)\n\n</script>",
        encoding="utf-8",
    )
    out = tmp_path / "out.html"
    assert generate(notes, out) == 1
    page = out.read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in page
    assert "<img " not in page
    assert 'href="javascript:' not in page
    assert "\\u003cscript" not in page
    assert "Content-Security-Policy" in page


def test_content_and_paths_are_preserved(tmp_path: Path) -> None:
    notes = tmp_path / "notas"
    notes.mkdir()
    (notes / "IDEAS.md").write_text(HEADER + ROW, encoding="utf-8")
    (notes / "001-prueba.md").write_text(
        "`__GENERATED__` [evidencia](archivo.md)", encoding="utf-8"
    )
    output = tmp_path / "out.html"
    generate(notes, output)
    result = output.read_text(encoding="utf-8")
    assert "__GENERATED__" in result
    assert "archivo.md" in result


@pytest.mark.parametrize(
    "broken",
    [
        "| Notas | Estado | Idea |",
        "[001 — Prueba](001-prueba.md) | Pendiente | Texto |",
    ],
)
def test_missing_or_broken_rows_are_rejected(tmp_path: Path, broken: str) -> None:
    (tmp_path / "001-prueba.md").write_text("hola", encoding="utf-8")
    (tmp_path / "IDEAS.md").write_text(
        HEADER.replace("| Nota | Estado | Idea |", broken) + ROW
        if broken.startswith("|")
        else HEADER + broken,
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="IDEAS.md"):
        read_notes(tmp_path)


def test_failed_replace_preserves_previous_output(tmp_path: Path) -> None:
    (tmp_path / "IDEAS.md").write_text(HEADER + ROW, encoding="utf-8")
    (tmp_path / "001-prueba.md").write_text("hola", encoding="utf-8")
    output = tmp_path / "old.html"
    output.write_text("anterior", encoding="utf-8")
    with (
        patch("tablero_notas.os.replace", side_effect=OSError("fallo")),
        pytest.raises(OSError, match="fallo"),
    ):
        generate(tmp_path, output)
    assert output.read_text(encoding="utf-8") == "anterior"


def test_generation_failure_does_not_open_browser() -> None:
    with (
        patch("sys.argv", ["tablero_notas.py"]),
        patch("tablero_notas.generate", side_effect=OSError("fallo")),
        patch("tablero_notas.webbrowser.open") as browser,
    ):
        assert main() == 1
        browser.assert_not_called()


@pytest.mark.parametrize(
    "rows",
    [ROW + ROW, "| fila incorrecta |\n", "| [001 — X](../escape.md) | X | X |\n", ""],
)
def test_invalid_input_preserves_previous_output(tmp_path: Path, rows: str) -> None:
    notes = tmp_path / "notas"
    notes.mkdir()
    (notes / "IDEAS.md").write_text(HEADER + rows, encoding="utf-8")
    (notes / "001-prueba.md").write_text("contenido", encoding="utf-8")
    out = tmp_path / "out.html"
    out.write_text("anterior", encoding="utf-8")
    with pytest.raises(ValueError, match="IDEAS.md|no contiene"):
        generate(notes, out)
    assert out.read_text(encoding="utf-8") == "anterior"


def test_repository_index_includes_all_notes() -> None:
    root = Path(__file__).resolve().parents[1]
    notes = read_notes(root / "notas")
    assert {note.number for note in notes} == {
        p.name[:3] for p in (root / "notas").glob("[0-9][0-9][0-9]-*.md")
    }
