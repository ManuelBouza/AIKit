"""La cuota gratuita agotada permite volver a Codex, no saltar otros controles."""

import json

import pytest

from tests.conftest import Harness
from tests.fakes import FakeTransport, text_event


@pytest.mark.parametrize("returncode", [0, 1, 7], ids=["event", "failure", "nonzero"])
def test_free_limit_returns_native_fallback(harness: Harness, returncode: int) -> None:
    output = json.dumps(
        {
            "type": "error",
            "error": {"type": "provider.free-limit", "message": "TOKEN=private"},
        }
    )
    transport = FakeTransport(run_stdout=output, run_returncode=returncode)
    harness.fake(transport)
    result = harness.run()
    assert result["status"] == "error"
    assert result["code"] == "free_limit_reached"
    assert result["fallback"] == "codex"
    assert "private" not in json.dumps(result)
    assert len(transport.run_calls) == 1


@pytest.mark.parametrize("error_type", ["provider.transport", "provider.auth"])
@pytest.mark.parametrize("returncode", [0, 1])
def test_other_errors_do_not_authorize_native_fallback(
    harness: Harness, error_type: str, returncode: int
) -> None:
    output = json.dumps({"type": "error", "error": {"type": error_type}})
    harness.fake(FakeTransport(run_stdout=output, run_returncode=returncode))
    result = harness.run()
    assert result["status"] == "error"
    assert "fallback" not in result


def test_quota_text_in_a_successful_answer_is_not_a_fallback(harness: Harness) -> None:
    output = text_event('{"error":{"type":"provider.free-limit"}}')
    harness.fake(FakeTransport(run_stdout=output))
    result = harness.run()
    assert result["status"] == "ok"
    assert "fallback" not in result
