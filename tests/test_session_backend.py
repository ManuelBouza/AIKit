"""Contrato del backend sin red, modelos ni servidores reales."""

from __future__ import annotations

import importlib
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from session_store import DeliveryObservation

from tests.test_session_store import OBSERVED_AT, make_record


def backend() -> ModuleType:
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
    """Solo transporte externo falso; las decisiones pertenecen al backend real."""

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
            }
        )
        self.clock = Clock()
        self.cost = 0.01
        self.calls: list[tuple[str, float, bool | None]] = []
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
        session_id: str | None,
        timeout: float,
        resume: bool | None = None,
    ) -> Any:
        assert 0 < timeout <= 10
        assert session_id == (
            None if operation in {"server.info", "session.active"} else "ses_example"
        )
        self.calls.append((operation, timeout, resume))
        self.clock.sleep(self.cost)
        if self.error:
            raise self.error
        if operation == "session.active":
            body = self.active.pop(0) if len(self.active) > 1 else self.active[0]
        else:
            body = self.responses[operation]
        if self.after_request:
            self.after_request(operation)
        return backend().ApiResponse(self.status.get(operation, 200), body)

    def inspect(self, record: Any) -> Any:
        return backend().inspect_session(record, binding=self, _clock=self.clock.now)

    def interrupt(self, record: Any) -> Any:
        return backend().interrupt_session(
            record, binding=self, _clock=self.clock.now, _sleep=self.clock.sleep
        )


def record(root: Path) -> Any:
    return replace(make_record(root), session="ses_example", server_identity="owner-1")


def test_no_binding_preserves_history_without_claiming_current_state(
    tmp_path: Path,
) -> None:
    module = backend()
    source = record(tmp_path)
    source.delivery = DeliveryObservation("completed", "old_cli", OBSERVED_AT)
    result = module.inspect_session(source)
    assert result.code == "control_unavailable"
    assert result.execution.state == "unknown"
    assert result.local_execution == source.execution
    assert result.local_delivery == source.delivery
    assert result.local_delivery is not source.delivery
    assert result.exists is None
    assert not result.capabilities.observation
    assert not result.capabilities.control
    assert not result.capabilities.quota_resume
    outcome = module.interrupt_session(source)
    assert not outcome.requested
    assert outcome.confirmed is None
    assert module.worker_interrupt(source) is None


@pytest.mark.parametrize(
    "identity", ["http://169.254.169.254/latest/meta-data", "owner-2", None]
)
def test_untrusted_record_identity_never_connects(
    tmp_path: Path, identity: str | None
) -> None:
    transport = Binding(tmp_path)
    source = replace(record(tmp_path), server_identity=identity)
    assert transport.interrupt(source).code in {"control_unavailable", "owner_mismatch"}
    assert transport.calls == []
    assert transport.owner_checks == 0


@pytest.mark.parametrize(
    "change",
    [
        {"pid": 43},
        {"started_at": "2026-10-30T13:00:00+00:00"},
        {"started_at": None},
        {"version": "2.3.0"},
        {"started_at": "invalid"},
    ],
)
def test_owner_restart_reuse_or_unprovable_birth_prevents_requests(
    tmp_path: Path, change: dict[str, object]
) -> None:
    transport = Binding(tmp_path)
    transport.observed_owner = replace(transport.expected_owner, **change)
    assert transport.interrupt(record(tmp_path)).code in {
        "owner_mismatch",
        "owner_unverified",
    }
    assert transport.calls == []


def test_fresh_owner_check_before_every_request(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.owner_change_at = 4
    outcome = transport.interrupt(record(tmp_path))
    assert outcome.code == "owner_mismatch"
    assert not outcome.requested
    assert "session.interrupt" not in [x[0] for x in transport.calls]


def test_wrong_server_info_is_rejected(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.responses["server.info"] = {
        "version": "2.2.0",
        "pid": 999,
        "urls": [],
        "paths": {"tmp": "x"},
    }
    assert transport.inspect(record(tmp_path)).code == "owner_mismatch"


def test_record_identity_is_rechecked_before_every_request(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    source = record(tmp_path)

    def replace_record_identity(operation: str) -> None:
        if operation == "server.info":
            source.server_identity = "owner-changed"

    transport.after_request = replace_record_identity
    outcome = transport.interrupt(source)
    assert outcome.code == "owner_mismatch"
    assert not outcome.requested
    assert [entry[0] for entry in transport.calls] == ["server.info"]


def test_inspection_includes_verified_owner_and_metadata_counts(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.permission.list"] = {
        "data": [{"id": "opaque-request"}]
    }
    outcome = transport.inspect(record(tmp_path))
    assert outcome.owner == transport.expected_owner
    assert outcome.permission_count == 1
    assert outcome.execution.state == "active"
    assert outcome.execution.waiting_reason is None
    assert outcome.capabilities.observation
    assert outcome.capabilities.control


def test_owner_change_after_ack_cannot_be_confirmed(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.owner_change_at = 5
    outcome = transport.interrupt(record(tmp_path))
    assert outcome.requested
    assert outcome.acknowledged is True
    assert outcome.confirmed is None
    assert outcome.code == "owner_mismatch"


def test_unavailable_operation_does_not_fall_back_to_other_transport(
    tmp_path: Path,
) -> None:
    transport = Binding(tmp_path)
    transport.operations -= {"session.interrupt"}
    outcome = transport.interrupt(record(tmp_path))
    assert outcome.code == "operation_unavailable"
    assert not outcome.requested


def test_missing_session_does_not_interrupt(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.status["session.get"] = 404
    transport.responses["session.get"] = {
        "_tag": "SessionNotFoundError",
        "sessionID": "ses_example",
        "message": "private",
    }
    assert transport.inspect(record(tmp_path)).exists is False
    assert not transport.interrupt(record(tmp_path)).requested


def test_cwd_mismatch_does_not_interrupt(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.get"]["data"]["location"]["directory"] = str(
        tmp_path / "other"
    )
    assert transport.inspect(record(tmp_path)).cwd_matches is False
    assert not transport.interrupt(record(tmp_path)).requested


def test_old_terminal_and_duplicate_cursor_never_override_current_running(
    tmp_path: Path,
) -> None:
    transport = Binding(tmp_path)
    source = record(tmp_path)
    source.delivery = DeliveryObservation("completed", "cli_terminal", OBSERVED_AT)
    first, second = transport.inspect(source), transport.inspect(source)
    for result in (first, second):
        assert result.execution.state == "active"
        assert result.execution.waiting_reason is None
        assert result.cursor == "event-1"
        assert result.local_delivery.state == "completed"
        assert result.log_evidence == ()
        assert result.pending_count == 0
        assert result.permission_count == 0
        assert not result.capabilities.logs
        assert not result.capabilities.model_change
        assert not result.capabilities.quota_resume
    assert all(call[0] != "session.log" for call in transport.calls)


def test_nonempty_unverified_metadata_never_invents_waiting(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.inbox.list"] = {
        "data": [{"private": "unknown-schema"}]
    }
    outcome = transport.inspect(record(tmp_path))
    assert outcome.execution.state == "active"
    assert outcome.pending_count is None
    assert "pending_metadata_unavailable" in outcome.limitations


@pytest.mark.parametrize(
    ("operation", "body"),
    [
        (
            "server.info",
            {"version": "2.2.0", "pid": True, "urls": [], "paths": {"tmp": "x"}},
        ),
        ("session.get", {"data": []}),
        ("session.get", {"data": {"id": "ses_other"}}),
        ("session.active", {"data": {"ses_example": {"type": "retrying"}}}),
        ("session.active", {"data": []}),
        ("session.active", {"data": {"ses_example": {"type": "running", "extra": 1}}}),
        ("session.inbox.list", {"data": "secret"}),
        ("session.permission.list", {"data": False}),
    ],
)
def test_malformed_json_is_controlled(
    tmp_path: Path, operation: str, body: object
) -> None:
    transport = Binding(tmp_path)
    if operation == "session.active":
        transport.active = [body]
    else:
        transport.responses[operation] = body
    result = transport.inspect(record(tmp_path))
    assert result.code == "invalid_response"
    assert "secret" not in repr(result)


def test_transport_error_never_leaks_message(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.error = OSError("https://private:password@host/private-transcript")
    result = transport.inspect(record(tmp_path))
    assert result.code == "backend_unavailable"
    assert "password" not in repr(result)
    assert "private-transcript" not in repr(result)


def test_acknowledgement_only_becomes_confirmed_after_stable_idle(
    tmp_path: Path,
) -> None:
    transport = Binding(tmp_path)
    transport.active = [
        {"data": {"ses_example": {"type": "running"}}},
        {"data": {}},
        {"data": {}},
    ]
    result = transport.interrupt(record(tmp_path))
    assert result.requested
    assert result.acknowledged is True
    assert result.confirmed is True
    posts = [c for c in transport.calls if c[0] == "session.interrupt"]
    assert len(posts) == 1
    assert posts[0][2] is False


def test_successor_after_idle_is_not_confirmed(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.active = [
        {"data": {"ses_example": {"type": "running"}}},
        {"data": {}},
        {"data": {"ses_example": {"type": "running"}}},
    ]
    result = transport.interrupt(record(tmp_path))
    assert result.acknowledged is True
    assert result.confirmed is None
    assert result.code == "successor_activity"


def test_ack_without_settlement_exhausts_total_budget(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    result = transport.interrupt(record(tmp_path))
    assert result.acknowledged is True
    assert result.confirmed is None
    assert result.code == "backend_timeout"
    assert transport.clock.value <= 10
    assert all(0 < timeout <= 10 for _, timeout, _ in transport.calls)


def test_expensive_preflight_uses_same_total_budget(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.cost = 2.5
    result = transport.interrupt(record(tmp_path))
    assert result.code == "backend_timeout"
    assert not result.requested
    assert transport.clock.value == 10


@pytest.mark.parametrize("ack", [False, 1, "true", None])
def test_rejected_or_malformed_ack_never_confirms(tmp_path: Path, ack: object) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.interrupt"] = {"interrupted": ack}
    result = transport.interrupt(record(tmp_path))
    assert result.requested
    assert result.confirmed is None
    assert result.code == (
        "interrupt_unacknowledged" if ack is False else "invalid_response"
    )


def test_idle_owner_does_not_receive_post(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.active = [{"data": {}}]
    result = transport.interrupt(record(tmp_path))
    assert not result.requested
    assert result.confirmed is None
    assert result.code == "owner_idle"


def test_json_integer_overflow_is_invalid_response(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.responses["session.get"]["data"]["cost"] = 10**400
    assert transport.inspect(record(tmp_path)).code == "invalid_response"


def test_timeout_during_post_records_uncertain_send_without_retry(
    tmp_path: Path,
) -> None:
    transport = Binding(tmp_path)

    def fail_after_post(operation: str) -> None:
        if operation == "session.interrupt":
            raise TimeoutError("private credentials")

    transport.after_request = fail_after_post
    result = transport.interrupt(record(tmp_path))
    assert result.requested
    assert result.acknowledged is None
    assert result.confirmed is None
    assert result.code == "backend_timeout"
    assert [entry[0] for entry in transport.calls].count("session.interrupt") == 1
    assert "private credentials" not in repr(result)


def test_uri_shaped_identity_cannot_become_connection_authority(tmp_path: Path) -> None:
    transport = Binding(tmp_path)
    transport.expected_owner = replace(
        transport.expected_owner, identity="http:169.254.169.254"
    )
    transport.observed_owner = transport.expected_owner
    source = replace(record(tmp_path), server_identity="http:169.254.169.254")
    outcome = transport.interrupt(source)
    assert outcome.code == "control_unavailable"
    assert transport.calls == []


@pytest.mark.parametrize("field", ["session", "cwd"])
def test_changed_record_target_cannot_redirect_interrupt(
    tmp_path: Path, field: str
) -> None:
    transport = Binding(tmp_path)
    source = record(tmp_path)

    def change_target(operation: str) -> None:
        if operation == "session.active":
            setattr(
                source,
                field,
                "ses_other" if field == "session" else str(tmp_path / "other"),
            )

    transport.after_request = change_target
    outcome = transport.interrupt(source)
    assert outcome.code == "record_changed"
    assert not outcome.requested
    assert all(entry[0] != "session.interrupt" for entry in transport.calls)
