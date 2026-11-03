"""Reconciliación terminal conservadora por mensaje durable (Task 2)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from session_store import DeliveryObservation

from tests.test_session_store import OBSERVED_AT, make_record


def backend() -> ModuleType:
    import importlib

    assert importlib.util.find_spec("session_backend"), "Falta backend propietario"
    return importlib.import_module("session_backend")


class Clock:
    def __init__(self) -> None:
        self.value = 0.0

    def now(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += seconds


class Binding:
    """Transporte falso con una única lectura puntual de mensaje durable."""

    def __init__(self, root: Path) -> None:
        module = backend()
        self.expected_owner = module.OwnerIdentity("owner-1", 42, OBSERVED_AT, "2.2.0")
        self.observed_owner = self.expected_owner
        self.operations = frozenset(
            {
                "server.info",
                "session.get",
                "session.active",
                "session.inbox.list",
                "session.permission.list",
                "session.interrupt",
                "session.message.get",
            }
        )
        self.clock = Clock()
        self.cost = 0.01
        self.calls: list[tuple[str, float, bool | None, str | None]] = []
        self.owner_checks = 0
        self.owner_change_at: int | None = None
        self.error: Exception | None = None
        self.after_request: Callable[[str], None] | None = None
        self.active: list[object] = [{"data": {"ses_example": {"type": "running"}}}]
        self.responses: dict[str, Any] = {
            "server.info": {
                "version": "2.2.0",
                "pid": 42,
                "urls": [],
                "paths": {"tmp": "ignored"},
            },
            "session.get": {
                "data": {
                    "id": "ses_example",
                    "projectID": "prj_example",
                    "cost": 0,
                    "tokens": {},
                    "time": {"created": 1, "updated": 2},
                    "location": {"directory": str(root.resolve())},
                }
            },
            "session.inbox.list": {"data": []},
            "session.permission.list": {"data": []},
            "session.interrupt": {"interrupted": True},
            "session.message.get": {
                "data": {
                    "id": "msg_1",
                    "type": "assistant",
                    "finish": "stop",
                    "error": None,
                    "time": {"completed": 123},
                }
            },
        }
        self.status: dict[str, int] = {}

    def verify_owner(self, *, timeout: float) -> Any:
        assert 0 < timeout <= 10
        self.owner_checks += 1
        self.clock.sleep(self.cost)
        if (
            self.owner_change_at is not None
            and self.owner_checks >= self.owner_change_at
        ):
            return replace(self.expected_owner, started_at="2026-10-30T13:00:00+00:00")
        return self.observed_owner

    def request(
        self,
        operation: str,
        *,
        session_id: str | None = None,
        message_id: str | None = None,
        timeout: float = 10.0,
        resume: bool | None = None,
    ) -> Any:
        assert 0 < timeout <= 10
        assert session_id == (
            None if operation in {"server.info", "session.active"} else "ses_example"
        )
        self.calls.append((operation, timeout, resume, message_id))
        self.clock.sleep(self.cost)
        if self.error is not None:
            raise self.error
        if operation == "session.active":
            body = self.active.pop(0) if len(self.active) > 1 else self.active[0]
        else:
            body = self.responses[operation]
        if self.after_request is not None:
            self.after_request(operation)
        return backend().ApiResponse(self.status.get(operation, 200), body)

    def reconcile(
        self,
        root: Path,
        *,
        assistant_message_id: str | None,
        prompt_message_id: str | None = None,
        timeout: float,
    ) -> Any:
        record_value = replace(
            make_record(root), session="ses_example", server_identity="owner-1"
        )
        return backend().reconcile_terminal_message(
            record_value,
            self,
            assistant_message_id=assistant_message_id,
            prompt_message_id=prompt_message_id,
            timeout=timeout,
            _clock=self.clock.now,
        )


def record(root: Path) -> Any:
    return replace(make_record(root), session="ses_example", server_identity="owner-1")


def test_reconcile_terminal_message_accepts_stop_with_valid_ids(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    result = transport.reconcile(
        tmp_path,
        assistant_message_id="msg_1",
        prompt_message_id="msg_user",
        timeout=5.0,
    )
    assert result.accepted is True
    assert result.outcome == "completed"
    assert result.finish == "stop"
    assert result.completed_at == 123
    assert result.assistant_message_id == "msg_1"


def test_reconcile_terminal_message_accepts_parent_null(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.message.get"]["data"]["parentID"] = None
    result = transport.reconcile(
        tmp_path,
        assistant_message_id="msg_1",
        prompt_message_id="msg_user",
        timeout=5.0,
    )
    assert result.accepted is True
    assert result.outcome == "completed"


def test_reconcile_terminal_message_missing_id_avoids_http(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    result = transport.reconcile(tmp_path, assistant_message_id=None, timeout=5.0)
    assert result.accepted is False
    assert not any(call[0] == "session.message.get" for call in transport.calls)


@pytest.mark.parametrize(
    "mutation",
    [
        {"id": "msg_other"},
        {"type": "user"},
        {"finish": "length"},
    ],
)
def test_reconcile_terminal_message_rejects_bad_response_fields(
    tmp_path: Path, mutation: dict[str, Any]
) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.message.get"]["data"].update(mutation)
    result = transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is False


def test_reconcile_terminal_message_rejects_session_mismatch(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.message.get"]["data"]["sessionID"] = "ses_other"
    result = transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is False


def test_reconcile_terminal_message_rejects_parent_mismatch(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.message.get"]["data"]["parentID"] = "msg_other"
    result = transport.reconcile(
        tmp_path,
        assistant_message_id="msg_1",
        prompt_message_id="msg_user",
        timeout=5.0,
    )
    assert result.accepted is False


@pytest.mark.parametrize("completed", [None, True, float("nan"), float("inf")])
def test_reconcile_terminal_message_requires_finite_completed_timestamp(
    tmp_path: Path, completed: object
) -> None:
    transport = Binding(tmp_path)
    if completed is None:
        transport.responses["session.message.get"]["data"]["time"] = {}
    else:
        transport.responses["session.message.get"]["data"]["time"] = {
            "completed": completed
        }
    result = transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is False


@pytest.mark.parametrize("finish", ["length"])
def test_reconcile_terminal_message_length_is_partial(
    tmp_path: Path, finish: str
) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.message.get"]["data"]["finish"] = finish
    result = transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is False
    assert result.outcome == "partial"


@pytest.mark.parametrize("finish", ["error", "content-filter", "cancel", "interrupted"])
def test_reconcile_terminal_message_failed_finishes(
    tmp_path: Path, finish: str
) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.message.get"]["data"]["finish"] = finish
    result = transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is False
    assert result.outcome == "failed"


@pytest.mark.parametrize("finish", ["tool-calls", "unknown"])
def test_reconcile_terminal_message_nonfinal_finishes_are_not_completed(
    tmp_path: Path, finish: str
) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.message.get"]["data"]["finish"] = finish
    result = transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is False
    assert result.outcome != "completed"


def test_reconcile_terminal_message_prior_delivery_failure_blocks_success(
    tmp_path: Path,
) -> None:
    transport = Binding(tmp_path)
    source = record(tmp_path)
    source.delivery = DeliveryObservation("failed", "old", OBSERVED_AT)
    result = backend().reconcile_terminal_message(
        source,
        transport,
        assistant_message_id="msg_1",
        timeout=5.0,
        _clock=transport.clock.now,
    )
    assert result.accepted is False


def test_reconcile_terminal_message_prior_delivery_interrupted_blocks_success(
    tmp_path: Path,
) -> None:
    transport = Binding(tmp_path)
    source = record(tmp_path)
    source.delivery = DeliveryObservation("interrupted", "old", OBSERVED_AT)
    result = backend().reconcile_terminal_message(
        source,
        transport,
        assistant_message_id="msg_1",
        timeout=5.0,
        _clock=transport.clock.now,
    )
    assert result.accepted is False


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf")])
def test_reconcile_terminal_message_invalid_budget_avoids_http(
    tmp_path: Path, timeout: float
) -> None:
    transport = Binding(tmp_path)
    result = transport.reconcile(
        tmp_path, assistant_message_id="msg_1", timeout=timeout
    )
    assert result.accepted is False
    assert not any(call[0] == "session.message.get" for call in transport.calls)


def test_reconcile_terminal_message_api_error_is_conservative(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.error = RuntimeError("boom")
    result = transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is False


def test_reconcile_terminal_message_owner_change_is_conservative(
    tmp_path: Path,
) -> None:
    transport = Binding(tmp_path)
    transport.owner_change_at = 1
    result = transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is False
    assert not any(call[0] == "session.message.get" for call in transport.calls)


def test_reconcile_terminal_message_timeout_during_request_is_conservative(
    tmp_path: Path,
) -> None:
    transport = Binding(tmp_path)

    def fail(operation: str) -> None:
        if operation == "session.message.get":
            raise TimeoutError("private")

    transport.after_request = fail
    result = transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is False
    message_calls = [
        call for call in transport.calls if call[0] == "session.message.get"
    ]
    assert len(message_calls) == 1
    assert 0 < message_calls[0][1] <= 10


def test_reconcile_terminal_message_forwards_message_id(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    message_calls = [
        call for call in transport.calls if call[0] == "session.message.get"
    ]
    assert message_calls
    assert message_calls[-1][3] == "msg_1"


def test_reconcile_terminal_message_rejects_message_error(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.message.get"]["data"]["error"] = {"name": "boom"}
    transport.responses["session.message.get"]["data"]["finish"] = "error"
    result = transport.reconcile(tmp_path, assistant_message_id="msg_1", timeout=5.0)
    assert result.accepted is False
    assert result.outcome == "failed"


@pytest.mark.parametrize(
    ("case", "response_observed", "accepted", "outcome", "reason"),
    [
        ("missing_id", False, False, "uncertain", "assistant_message_id_unavailable"),
        ("request_exception", False, False, "pending", "backend_unavailable"),
        ("http_error", True, False, "pending", "backend_unavailable"),
        ("invalid_body", True, False, "uncertain", "invalid_response"),
        ("non_api_result", False, False, "uncertain", "invalid_response"),
        ("success", True, True, "completed", "accepted"),
        ("owner_changed_after_response", True, False, "pending", "owner_mismatch"),
    ],
)
def test_reconciliation_marks_only_received_http_response(
    tmp_path: Path,
    case: str,
    response_observed: bool,
    accepted: bool,
    outcome: str,
    reason: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = Binding(tmp_path)
    message_id: str | None = "msg_1"
    if case == "missing_id":
        message_id = None
    elif case == "request_exception":
        transport.error = RuntimeError("synthetic-private-detail")
    elif case == "http_error":
        transport.status["session.message.get"] = 500
    elif case == "invalid_body":
        transport.responses["session.message.get"] = []
    elif case == "non_api_result":

        def unexpected_response(*_args: Any, **_kwargs: Any) -> Any:
            return {}

        monkeypatch.setattr(transport, "request", unexpected_response)
    elif case == "owner_changed_after_response":
        transport.owner_change_at = 2

    result = transport.reconcile(tmp_path, assistant_message_id=message_id, timeout=5.0)

    assert getattr(result, "response_observed", None) is response_observed
    assert result.accepted is accepted
    assert result.outcome == outcome
    assert result.reason == reason
    assert "synthetic-private-detail" not in repr(result)
