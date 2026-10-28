"""Argumentos literales, eventos JSONL y errores de ejecución."""

from __future__ import annotations

import pytest

from tests.conftest import Harness
from tests.fakes import (
    DEFAULT_MODEL,
    api_model,
    error_event,
    finish_event,
    text_event,
    variant,
)


def test_command_preserves_order_spaces_and_variant(harness: Harness) -> None:
    text = 'Arregla "esto" & aquello\ncon espacios'
    harness.task.write_text(text, encoding="utf-8")
    transport = harness.fake(models=[api_model(variants=[variant("high")])])
    result = harness.run(model=DEFAULT_MODEL + "#high", reason="integración acotada")
    assert result["status"] == "ok"
    assert transport.run_calls == [transport.calls[-1]]
    call = transport.run_calls[0]
    assert call.argv == [
        "C:/fake/opencode.exe",
        "run",
        "--model",
        DEFAULT_MODEL + "#high",
        "--agent",
        "build",
        "--standalone",
        "--format",
        "json",
        "--",
        "Tarea delegada (contenido literal):\n\n" + text,
    ]
    assert call.cwd == str(harness.project.resolve())
    assert call.timeout == 30
    for flag in ("--variant", "--effort", "--auto", "--allow-paid"):
        assert flag not in call.argv


def test_option_like_task_is_literal(harness: Harness) -> None:
    original = '--auto & "comillas" | > $HOME ; ñ'
    harness.task.write_text(original, encoding="utf-8")
    transport = harness.fake()
    assert harness.run()["status"] == "ok"
    argv = transport.run_calls[0].argv
    assert argv[-2:] == ["--", "Tarea delegada (contenido literal):\n\n" + original]
    assert argv.count("--auto") == 0
    assert not argv[-1].startswith("-")


def test_plan_agent_is_forwarded(harness: Harness) -> None:
    transport = harness.fake()
    assert harness.run(agent="plan")["status"] == "ok"
    assert transport.run_calls[0].argv[5] == "plan"


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), float("-inf"), 3601])
def test_invalid_task_timeout_precedes_process(
    harness: Harness, timeout: float
) -> None:
    transport = harness.fake()
    assert harness.run(timeout=timeout)["code"] == "invalid_timeout"
    assert transport.calls == []


def test_task_accepts_timeout_limit(harness: Harness) -> None:
    transport = harness.fake()
    assert harness.run(timeout=3600)["status"] == "ok"
    assert transport.run_calls[0].timeout == 3600


def test_error_event_message_wins_over_exit_zero(harness: Harness) -> None:
    harness.fake(run_stdout=text_event("parcial") + "\n" + error_event("sin cuota"))
    result = harness.run()
    assert result["code"] == "opencode_event_error"
    assert "sin cuota" in result["message"]


@pytest.mark.parametrize(
    ("stdout", "timeout_error", "fail_run", "code"),
    [
        pytest.param("", False, False, "empty_output", id="sin-texto"),
        pytest.param(None, True, False, "timeout", id="timeout"),
        pytest.param(None, False, True, "opencode_failed", id="inicio-fallido"),
    ],
)
def test_execution_errors(
    harness: Harness, stdout: str | None, timeout_error: bool, fail_run: bool, code: str
) -> None:
    harness.fake(run_stdout=stdout, timeout_error=timeout_error, fail_run=fail_run)
    assert harness.run()["code"] == code


def test_nonzero_exit_hides_transport_output(harness: Harness) -> None:
    harness.fake(
        run_stdout="TOKEN=secreto-en-stdout",
        run_stderr="fallo de transporte TOKEN=secreto-en-stderr",
        run_returncode=7,
    )
    result = harness.run()
    assert result["code"] == "opencode_failed"
    assert "7" in result["message"]
    for secret in ("secreto-en-stdout", "secreto-en-stderr", "fallo de transporte"):
        assert secret not in result["message"]


def test_version_failure_hides_stderr(harness: Harness) -> None:
    harness.fake(version_returncode=3, version_stderr="TOKEN=secreto-version")
    result = harness.run()
    assert result["code"] == "version_check_failed"
    assert "3" in result["message"]
    assert "secreto-version" not in result["message"]


def test_catalog_failure_hides_stderr(harness: Harness) -> None:
    harness.fake(catalog_returncode=5, catalog_stderr="TOKEN=secreto-catalogo")
    result = harness.run()
    assert result["code"] == "catalog_unavailable"
    assert "5" in result["message"]
    assert "secreto-catalogo" not in result["message"]


@pytest.mark.parametrize(
    ("cost", "expected"),
    [
        pytest.param(None, None, id="ausente-es-null"),
        pytest.param(0, 0, id="cero-conservado"),
    ],
)
def test_reported_cost(
    harness: Harness, cost: float | None, expected: float | None
) -> None:
    harness.fake(run_stdout=text_event("ok") + "\n" + finish_event(cost))
    result = harness.run()
    assert result["status"] == "ok"
    assert result["cost"] == expected


def test_summary_capped_at_4000(harness: Harness) -> None:
    harness.fake(run_stdout=text_event("x" * 5000) + "\n" + finish_event(0))
    result = harness.run()
    assert result["status"] == "ok"
    assert result["summary"] == "x" * 4000


def test_success_reports_session_selection_and_summary(harness: Harness) -> None:
    harness.fake(
        run_stdout=text_event("informe final", session="ses_abc")
        + "\n"
        + finish_event(0, session="ses_abc")
    )
    result = harness.run(reason="delegación gratuita suficiente")
    assert result == {
        "status": "ok",
        "session": "ses_abc",
        "model": DEFAULT_MODEL,
        "variant": None,
        "effort": "provider_default",
        "reason": "delegación gratuita suficiente",
        "agent": "build",
        "summary": "informe final",
        "cost": 0,
    }
