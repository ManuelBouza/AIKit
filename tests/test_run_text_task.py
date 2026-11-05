"""Núcleo por texto: mismas políticas que la ejecución por archivo de tarea."""

from __future__ import annotations

import json

import delegate
import pytest

from tests.conftest import Harness
from tests.fakes import DEFAULT_MODEL, FakeTransport, api_model, variant


def test_text_task_reaches_the_backend_without_task_file(harness: Harness) -> None:
    transport = harness.fake()
    result = harness.run_text("Tarea en memoria")
    assert result["status"] == "ok"
    assert transport.run_calls[0].argv[-1] == delegate.TASK_PREFIX + "Tarea en memoria"


def test_text_task_keeps_quotes_unicode_and_options_literal(
    harness: Harness,
) -> None:
    original = '--auto & "comillas" | > $HOME ; ñ'
    transport = harness.fake()
    assert harness.run_text(original)["status"] == "ok"
    argv = transport.run_calls[0].argv
    assert argv[-2:] == ["--", delegate.TASK_PREFIX + original]
    assert argv.count("--auto") == 0


def test_text_task_only_writes_managed_state(harness: Harness) -> None:
    harness.fake()
    before = {path.name for path in harness.project.iterdir()}
    assert harness.run_text("Tarea sin archivo")["status"] == "ok"
    assert {path.name for path in harness.project.iterdir()} == before | {".aikit"}
    assert not (harness.project / "Tarea sin archivo").exists()


def test_blocked_provider_is_rejected_before_any_process(harness: Harness) -> None:
    transport = harness.fake()
    result = harness.run_text("Tarea", model="openai/gpt-5")
    assert result["code"] == "provider_not_allowed"
    assert transport.calls == []


@pytest.mark.parametrize("task", ["", "   "], ids=["vacio", "espacios"])
def test_empty_text_task_is_rejected_before_any_process(
    harness: Harness, task: str
) -> None:
    transport = harness.fake()
    result = harness.run_text(task)
    assert result["code"] == "empty_task"
    assert transport.calls == []


def test_missing_reason_is_rejected_before_any_process(harness: Harness) -> None:
    transport = harness.fake()
    result = harness.run_text("Tarea", reason="  ")
    assert result["code"] == "reason_required"
    assert transport.calls == []


def test_unknown_variant_is_rejected_before_running(harness: Harness) -> None:
    transport = harness.fake(models=[api_model(variants=[variant("high")])])
    result = harness.run_text("Tarea", variant="imaginaria")
    assert result["code"] == "invalid_variant"
    assert transport.run_calls == []


def test_free_limit_is_preserved_for_the_text_entry(harness: Harness) -> None:
    output = json.dumps(
        {"type": "error", "error": {"type": "provider.free-limit", "message": "x"}}
    )
    harness.fake(FakeTransport(run_stdout=output))
    result = harness.run_text("Tarea")
    assert result["code"] == "free_limit_reached"
    assert result.get("fallback") != "reselect"
    assert result["uncertain"] is True


def test_text_task_reports_selection_and_summary(harness: Harness) -> None:
    harness.fake(models=[api_model(variants=[variant("high")])])
    result = harness.run_text(
        "Tarea", model=DEFAULT_MODEL + "#high", reason="integración acotada"
    )
    expected = {
        "status": "ok",
        "session": "ses_prueba",
        "model": DEFAULT_MODEL,
        "variant": "high",
        "effort": "high",
        "reason": "integración acotada",
        "agent": "build",
        "summary": "ok",
        "cost": 0,
        "delivery": "completed",
        "execution": "unknown",
        "limitations": [],
    }
    assert {key: result[key] for key in expected} == expected
    assert result["task_id"]
    assert result["attempt_id"]


def test_text_task_uses_the_same_transport_as_the_file_entry(
    harness: Harness,
) -> None:
    transport = harness.fake()
    harness.run_text("Tarea en memoria")
    file_result = harness.run()
    assert file_result["status"] == "ok"
    assert len(transport.run_calls) == 2
    assert transport.run_calls[0].argv[-1] == delegate.TASK_PREFIX + "Tarea en memoria"
    assert transport.run_calls[1].argv[-1] == delegate.TASK_PREFIX + "Tarea de prueba"
