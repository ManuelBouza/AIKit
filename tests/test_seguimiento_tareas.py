"""Contrato estricto y relaciones de tickets locales ficticios."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from seguimiento_tareas import read_tasks
from tablero_notas import generate


def ticket(identifier: str = "IMP-0001") -> dict[str, Any]:
    return dict(
        schemaVersion=1,
        id=identifier,
        projectId="fiction",
        titulo="Entrega",
        creada="2026-11-17T10:00:00+01:00",
        actualizada="2026-11-17T10:00:00+01:00",
        ideas=[],
        origen="Mensaje humano ficticio 1",
        responsable="Coordinador",
        chat=None,
        fase="pendiente",
        atencion="normal",
        motivo="",
        siguienteAccion="Concretar",
        autorizacion=dict(estado="pendiente", alcance="", referencia=""),
        dependencias=[],
        referencias=[],
    )


def write_ticket(root: Path, data: dict[str, Any], *, raw: str | None = None) -> Path:
    coordination = root / "coordinacion"
    coordination.mkdir(exist_ok=True)
    (coordination / "PROYECTO.md").write_text(
        f"- Identidad del registro: fiction.\n- Raíz canónica: {coordination.resolve().as_posix()}.\n- Seguimiento local de ideas/tareas: activo.\n",
        encoding="utf-8",
    )
    path = coordination / "tareas" / str(data["id"]) / "TAREA.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Entrega\n\n```json\n"
        + (raw or json.dumps(data))
        + "\n```\n\n## Resultado\nEntrega concreta\n\n## Alcance\nAlcance concreto\n\n## Exclusiones\nNinguna\n\n## Aceptacion\nCriterio concreto\n\n## Historial\nAlta ficticia\n",
        encoding="utf-8",
    )
    return path


def test_direct_task_and_multiple_deliveries_keep_independent_states(
    tmp_path: Path,
) -> None:
    first = ticket()
    first.update(
        ideas=[1],
        fase="finalizada",
        autorizacion=dict(
            estado="autorizada", alcance="Entrega", referencia="Mensaje 1"
        ),
    )
    second = ticket("IMP-0002")
    second.update(ideas=[1], chat="chat-compartido", dependencias=["IMP-0001"])
    write_ticket(tmp_path, first)
    write_ticket(tmp_path, second)
    direct = ticket("IMP-0003")
    write_ticket(tmp_path, direct)
    tasks = read_tasks(tmp_path, {1})
    assert [t["fase"] for t in tasks] == ["finalizada", "pendiente", "pendiente"]
    assert tasks[2]["ideas"] == []
    assert len(read_tasks(tmp_path, {1})) == 3


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schemaVersion", True),
        ("schemaVersion", 2),
        ("extra", 1),
        ("projectId", "foreign"),
        ("titulo", "Diferente"),
        ("creada", "ayer"),
        ("actualizada", "2020-01-01T00:00:00Z"),
        ("ideas", [True]),
        ("ideas", [9]),
        ("ideas", [1, 1]),
        ("chat", ""),
        ("fase", "inventada"),
        ("atencion", "otra"),
        ("dependencias", ["IMP-9999"]),
        ("dependencias", ["IMP-0001"]),
        ("dependencias", ["IMP-0002", "IMP-0002"]),
        ("referencias", [dict(tipo="archivo", destino="../escape", etiqueta="x")]),
        ("referencias", [dict(tipo="archivo", destino="C:/Windows/a", etiqueta="x")]),
        ("referencias", [dict(tipo="archivo", destino="CON.txt", etiqueta="x")]),
        (
            "referencias",
            [dict(tipo="https", destino="https://user:pass@example.com", etiqueta="x")],
        ),
        ("autorizacion", dict(estado="autorizada", alcance="", referencia="")),
    ],
)
def test_invalid_metadata(tmp_path: Path, field: str, value: Any) -> None:
    data = ticket()
    data[field] = value
    write_ticket(tmp_path, data)
    with pytest.raises(ValueError, match=".+"):
        read_tasks(tmp_path, {1})


@pytest.mark.parametrize(
    "raw",
    [
        '{"schemaVersion":1,"schemaVersion":1}',
        '{"schemaVersion":NaN}',
        '{"schemaVersion":Infinity}',
    ],
)
def test_json_rejects_duplicates_and_nonfinite_values(tmp_path: Path, raw: str) -> None:
    write_ticket(tmp_path, ticket(), raw=raw)
    with pytest.raises(ValueError, match=".+"):
        read_tasks(tmp_path, set())


def test_cycles_and_path_mismatch(tmp_path: Path) -> None:
    a, b = ticket(), ticket("IMP-0002")
    a["dependencias"], b["dependencias"] = [b["id"]], [a["id"]]
    write_ticket(tmp_path, a)
    write_ticket(tmp_path, b)
    with pytest.raises(ValueError, match="ciclo"):
        read_tasks(tmp_path, set())
    b["dependencias"] = []
    path = write_ticket(tmp_path, b)
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            '"id": "IMP-0002"', '"id": "IMP-0003"'
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Identidad"):
        read_tasks(tmp_path, set())


def test_attention_preserves_review_phase_and_requires_reason(tmp_path: Path) -> None:
    data = ticket()
    data.update(
        fase="en_revision",
        atencion="bloqueada",
        motivo="Falta herramienta",
        autorizacion=dict(
            estado="autorizada", alcance="Revisar", referencia="Mensaje 2"
        ),
    )
    write_ticket(tmp_path, data)
    assert read_tasks(tmp_path, set())[0]["fase"] == "en_revision"
    data["motivo"] = ""
    write_ticket(tmp_path, data)
    with pytest.raises(ValueError, match="Motivo"):
        read_tasks(tmp_path, set())


def test_sections_acceptance_and_reference_file(tmp_path: Path) -> None:
    data = ticket()
    evidence = tmp_path / "evidencia.md"
    evidence.write_text("Ficticia", encoding="utf-8")
    data["referencias"] = [
        dict(tipo="archivo", destino="evidencia.md", etiqueta="Prueba")
    ]
    path = write_ticket(tmp_path, data)
    assert len(read_tasks(tmp_path, set())) == 1
    path.write_text(
        path.read_text(encoding="utf-8").replace("## Alcance", "## Ausente"),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Secciones"):
        read_tasks(tmp_path, set())


def test_task_failure_preserves_html_and_hostile_content_is_safe(
    tmp_path: Path,
) -> None:
    notes = tmp_path / "notas"
    notes.mkdir()
    (notes / "IDEAS.md").write_text(
        "## Abiertas\n| Nota | Estado | Idea |\n| --- | --- | --- |\n| [001 — Idea](001-idea.md) | Pendiente | Una idea |\n",
        encoding="utf-8",
    )
    (notes / "001-idea.md").write_text("Idea", encoding="utf-8")
    data = ticket()
    data["responsable"] = "</script><script>alert(1)</script>"
    path = write_ticket(tmp_path, data)
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n<script>alert(2)</script>\n![externa](https://example.com/x)\n",
        encoding="utf-8",
    )
    output = tmp_path / "index.html"
    generate(notes, output)
    old = output.read_bytes()
    assert b"<script>alert" not in old
    assert b"<img " not in old
    assert b"IMP-0001" in old
    data["fase"] = "desconocida"
    write_ticket(tmp_path, data)
    with pytest.raises(ValueError, match=".+"):
        generate(notes, output)
    assert output.read_bytes() == old


def notes_fixture(root: Path) -> Path:
    notes = root / "notas"
    notes.mkdir()
    (notes / "IDEAS.md").write_text(
        "## Abiertas\n| Nota | Estado | Idea |\n| --- | --- | --- |\n| [001 — Idea](001-idea.md) | Pendiente | Una idea |\n| [002 — Otra](002-otra.md) | Pendiente | Otra idea |\n",
        encoding="utf-8",
    )
    (notes / "001-idea.md").write_text("Idea", encoding="utf-8")
    (notes / "002-otra.md").write_text("Otra", encoding="utf-8")
    return notes


@pytest.mark.parametrize("offset", ["+00:99", "+01:60", "-24:00", "+99:00"])
def test_invalid_rfc3339_offset(tmp_path: Path, offset: str) -> None:
    data = ticket()
    data["creada"] = "2026-11-17T10:00:00" + offset
    write_ticket(tmp_path, data)
    with pytest.raises(ValueError, match="Offset RFC3339"):
        read_tasks(tmp_path, set())


def test_copied_contract_rejects_worktree_before_publication(tmp_path: Path) -> None:
    import shutil

    main = tmp_path / "main"
    main.mkdir()
    notes_fixture(main)
    write_ticket(main, ticket())
    copy = tmp_path / "worktree"
    shutil.copytree(main, copy)
    output = copy / "index.html"
    output.write_bytes(b"previous")
    with pytest.raises(ValueError, match="Raíz canónica"):
        generate(copy / "notas", output)
    assert output.read_bytes() == b"previous"


def test_missing_active_source_preserves_html_and_legacy_notes_work(
    tmp_path: Path,
) -> None:
    import shutil

    notes = notes_fixture(tmp_path)
    output = tmp_path / "index.html"
    generate(notes, output)
    write_ticket(tmp_path, ticket())
    generate(notes, output)
    previous = output.read_bytes()
    shutil.rmtree(tmp_path / "coordinacion/tareas")
    with pytest.raises(ValueError, match="Fuente de tareas ausente"):
        generate(notes, output)
    assert output.read_bytes() == previous


@pytest.mark.parametrize(
    ("opening", "closing"),
    [("   ```python", "   ```"), ("  ~~~", " ~~~~"), ("```", "````"), ("   ```", "")],
)
def test_code_fences_do_not_supply_sections(
    tmp_path: Path, opening: str, closing: str
) -> None:
    path = write_ticket(tmp_path, ticket())
    original = path.read_text(encoding="utf-8")
    header, body = original.split("## Resultado", 1)
    path.write_text(
        header + opening + "\n## Resultado" + body + "\n" + closing, encoding="utf-8"
    )
    with pytest.raises(ValueError, match="Secciones"):
        read_tasks(tmp_path, set())
    # A properly closed indented fence must not swallow genuine sections after it.
    path.write_text(
        header
        + opening
        + "\n## Resultado\nEjemplo\n"
        + (closing or "```")
        + "\n\n## Resultado"
        + body,
        encoding="utf-8",
    )
    assert len(read_tasks(tmp_path, set())) == 1


def test_long_acyclic_dependency_chain(tmp_path: Path) -> None:
    for number in range(1, 1012):
        data = ticket(f"IMP-{number:04}")
        if number < 1011:
            data["dependencias"] = [f"IMP-{number + 1:04}"]
        write_ticket(tmp_path, data)
    assert len(read_tasks(tmp_path, set())) == 1011


def test_external_symlink_reference_preserves_html(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    notes = notes_fixture(root)
    write_ticket(root, ticket())
    output = root / "index.html"
    generate(notes, output)
    previous = output.read_bytes()
    external = tmp_path / "external-fiction.md"
    external.write_text("Only isolated fixture", encoding="utf-8")
    link = root / "linked.md"
    try:
        link.symlink_to(external)
    except OSError as exc:
        pytest.skip(f"El entorno no permite crear enlaces simbólicos: {exc}")
    data = ticket()
    data["referencias"] = [
        dict(tipo="archivo", destino="linked.md", etiqueta="Ficticia")
    ]
    write_ticket(root, data)
    with pytest.raises(ValueError, match="Referencia fuera de raíz"):
        generate(notes, output)
    assert output.read_bytes() == previous
    assert external.read_text(encoding="utf-8") == "Only isolated fixture"
