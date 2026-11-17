"""Regresión DOM opcional: usa Playwright y navegador instalados, sin descargas."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from tablero_notas import generate

from tests.test_seguimiento_tareas import notes_fixture, ticket, write_ticket


def test_task_filters_selection_and_relations(tmp_path: Path) -> None:
    if os.environ.get("AIKIT_PLAYWRIGHT_PATH"):
        sys.path.insert(0, os.environ["AIKIT_PLAYWRIGHT_PATH"])
    playwright = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright opcional no instalado; consulta docs/tablero-notas.md",
    )
    notes = notes_fixture(tmp_path)
    first = ticket()
    first.update(ideas=[1], responsable="Ana", dependencias=["IMP-0002"])
    second = ticket("IMP-0002")
    second.update(
        ideas=[2],
        responsable="Luis",
        fase="en_revision",
        atencion="bloqueada",
        motivo="Falta evidencia",
        autorizacion=dict(
            estado="autorizada", alcance="Revisar", referencia="Mensaje ficticio"
        ),
    )
    third = ticket("IMP-0003")
    third.update(ideas=[1], responsable="Ana")
    for data in (first, second, third):
        write_ticket(tmp_path, data)
    output = tmp_path / "index.html"
    generate(notes, output)
    with playwright.sync_playwright() as runtime:
        executable = os.environ.get("AIKIT_BROWSER_EXECUTABLE")
        options = (
            {"executable_path": executable}
            if executable
            else {"channel": "msedge"}
            if sys.platform == "win32"
            else {}
        )
        browser = runtime.chromium.launch(headless=True, **options)
        try:
            page = browser.new_page()
            errors: list[str] = []
            requests: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: requests.append(request.url))
            page.goto(output.as_uri())
            page.locator("#tasks-view").focus()
            page.keyboard.press("Enter")
            assert page.locator("#board .note").count() == 3
            for selector, value, total in (
                ("#phase", "en_revision", 1),
                ("#attention", "bloqueada", 1),
                ("#owner", "Luis", 1),
                ("#idea", "002", 1),
            ):
                page.locator(selector).select_option(value)
                assert page.locator("#board .note").count() == total
                page.locator(selector).select_option("")
            page.locator("#board .note").filter(has_text="IMP-0001").click()
            page.locator("#owner").select_option("Luis")
            assert page.locator("#detail-title").inner_text() == "Selecciona una tarea"
            assert page.locator("#detail-content").inner_text() == ""
            page.locator("#owner").select_option("Ana")
            page.locator("#board .note").filter(has_text="IMP-0001").click()
            page.locator("#detail-content button").filter(has_text="IMP-0002").click()
            assert "IMP-0002" in page.locator("#detail-title").inner_text()
            assert page.locator("#owner").input_value() == "Ana"
            page.locator("#detail-content button").filter(has_text="Idea 002").click()
            assert "002" in page.locator("#detail-title").inner_text()
            page.locator("#detail-content button").filter(has_text="IMP-0002").click()
            assert "IMP-0002" in page.locator("#detail-title").inner_text()
            page.locator("#search").fill("IMP-0001")
            assert page.locator("#detail-title").inner_text() == "Selecciona una tarea"
            assert not errors
            assert all(url.startswith("file:") for url in requests)
        finally:
            browser.close()
