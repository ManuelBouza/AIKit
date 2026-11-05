"""Contrato de CLI: JSON compacto, ASCII y timeouts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import delegate
import pytest

from tests.conftest import Harness
from tests.fakes import DEFAULT_MODEL, api_model, error_event, text_event

ROOT = Path(__file__).resolve().parents[1]
DELEGATE_PATH = ROOT / "skills" / "delegating-to-opencode" / "scripts" / "delegate.py"


@pytest.mark.parametrize(
    ("include_model", "code"),
    [(False, "model_required"), (True, "reason_required")],
    ids=["modelo-ausente", "motivo-ausente"],
)
def test_missing_selection_returns_json_without_process(
    harness: Harness, capsys: pytest.CaptureFixture[str], include_model: bool, code: str
) -> None:
    transport = harness.fake()
    args = ["run", "--cwd", str(harness.project), "--task-file", str(harness.task)]
    if include_model:
        args += ["--model", DEFAULT_MODEL]
    assert delegate.main(args) == 1
    assert json.loads(capsys.readouterr().out)["code"] == code
    assert transport.calls == []


def test_error_event_with_exit_zero_returns_failure(
    harness: Harness, capsys: pytest.CaptureFixture[str]
) -> None:
    harness.fake(run_stdout=text_event("parcial") + "\n" + error_event("sin cuota"))
    assert (
        delegate.main(
            [
                "run",
                "--cwd",
                str(harness.project),
                "--task-file",
                str(harness.task),
                "--model",
                DEFAULT_MODEL,
                "--reason",
                "tarea mecánica",
            ]
        )
        == 1
    )
    assert json.loads(capsys.readouterr().out)["code"] == "opencode_event_error"


def test_main_prints_one_compact_json_line(
    harness: Harness, capsys: pytest.CaptureFixture[str]
) -> None:
    harness.fake()
    assert (
        delegate.main(
            [
                "run",
                "--cwd",
                str(harness.project),
                "--task-file",
                str(harness.task),
                "--model",
                DEFAULT_MODEL,
                "--reason",
                "tarea mecánica",
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert len(output.strip().splitlines()) == 1
    assert output.strip() == json.dumps(
        json.loads(output), ensure_ascii=True, separators=(",", ":")
    )


def test_subprocess_cp1252_stdout_still_emits_ascii_json(harness: Harness) -> None:
    bad_cwd = harness.project / "carpeta-inexistente-ñandú"
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252"
    completed = subprocess.run(
        [
            sys.executable,
            str(DELEGATE_PATH),
            "doctor",
            "--cwd",
            str(bad_cwd),
            "--timeout",
            "30",
        ],
        capture_output=True,
        env=env,
        timeout=30,
        check=False,
    )
    payload = json.loads(completed.stdout.decode("ascii"))
    assert completed.returncode == 1
    assert payload["status"] == "error"
    assert payload["code"] == "invalid_cwd"
    assert "ñandú" in payload["message"]


def test_doctor_version_count_and_calls(harness: Harness) -> None:
    harness.fake(version="2.2.0", models=[api_model("uno"), api_model("dos")])
    result = harness.doctor()
    assert (result["status"], result["version"], result["catalog_count"]) == (
        "ok",
        "2.2.0",
        2,
    )
    assert harness.binding is not None
    assert harness.binding.catalog_calls == [harness.project.resolve()]
    assert harness.binding.config_calls == [harness.project.resolve()]
    assert len(result["catalog"]) == 2


def test_doctor_rejects_an_unavailable_required_catalog(harness: Harness) -> None:
    harness.fake(version="1.0.0", catalog_returncode=1)
    assert harness.doctor()["code"] == "catalog_capability_unavailable"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), 3601])
def test_timeout_api_rejects_nonfinite_or_out_of_range(value: float) -> None:
    with pytest.raises(delegate.DelegateError) as error:
        delegate._validate_timeout(value)
    assert error.value.code == "invalid_timeout"


def test_timeout_api_accepts_limit() -> None:
    assert delegate._validate_timeout(3600) == 3600


@pytest.mark.parametrize("value", ["nan", "inf", "-inf", "3601"])
def test_timeout_cli_rejects_nonfinite_or_out_of_range(
    value: str, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        delegate._parser().parse_args(["doctor", "--cwd", ".", "--timeout", value])
    capsys.readouterr()


def test_timeout_cli_accepts_limit() -> None:
    args = delegate._parser().parse_args(["doctor", "--cwd", ".", "--timeout", "3600"])
    assert args.timeout == 3600
