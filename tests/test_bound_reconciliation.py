"""Recuperación local de entrega durable sin repetir inferencia."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import bound_execution as be
import delegate
import pytest
from service_connection import BoundLaunch
from service_identity import HostContext
from session_store import (
    DeliveryObservation,
    DeliveryState,
    ReconciliationObservation,
    TaskRecord,
    load_task,
    save_task,
)

from tests.fakes import FakeBinding, text_event
from tests.test_bound_execution import (
    _mock_supervisor_process,
    attempt_directory,
    install,
    make_context,
    prepare,
    write_terminal,
)


@dataclass(frozen=True)
class StoredResult:
    project: Path
    context: HostContext
    record: TaskRecord
    path: Path

    def read(self) -> dict[str, Any]:
        value: dict[str, Any] = json.loads(self.path.read_text(encoding="utf-8"))
        return value

    def write(self, value: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def stored_result(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> StoredResult:
    project = tmp_path / "project"
    project.mkdir()
    context = make_context(tmp_path)
    install(monkeypatch, context, FakeBinding(context=context))
    prepared = prepare(project, context)

    def publish(
        prepared: BoundLaunch, record: TaskRecord, *, context: HostContext
    ) -> Any:
        # El productor acredita la entrega sin un evento step_finish en stdout.
        write_terminal(record, text_event("entrega reconciliada"), delivery="completed")
        record.delivery = DeliveryObservation(
            "completed", "durable_message", "2026-11-02T00:00:00+00:00"
        )
        save_task(project, record)
        path = attempt_directory(record) / "result.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["limitations"] = ["server_state_unknown"]
        path.write_text(json.dumps(data), encoding="utf-8")
        return _mock_supervisor_process()

    monkeypatch.setattr(be, "_launch_supervisor", publish)
    first = be.execute_bound(prepared, context=context, wait_seconds=0)
    assert first["status"] == "ok"
    record = load_task(project, first["task_id"])
    return StoredResult(
        project, context, record, attempt_directory(record) / "result.json"
    )


def test_recover_completed_durable_without_terminal_event(
    stored_result: StoredResult,
) -> None:
    stored = stored_result
    stdout = (stored.path.parent / "stdout.partial").read_text(encoding="utf-8")
    assert "step_finish" not in stdout
    result = be.recover_local_result(stored.context, stored.record)
    assert result["status"] == "ok"
    assert result["delivery"] == "completed"
    assert result["execution"] == "unknown"
    assert result["summary"] == "entrega reconciliada"
    assert "server_state_unknown" in result["limitations"]
    assert stored.record.delivery is not None
    assert stored.record.delivery.source == "durable_message"


def test_recover_is_idempotent_and_never_relaunches_or_discovers(
    stored_result: StoredResult, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("La recuperación local no puede lanzar ni consultar backend")

    monkeypatch.setattr(be, "_launch_supervisor", forbidden)
    monkeypatch.setattr(delegate, "discover_existing", forbidden)
    monkeypatch.setattr(FakeBinding, "request", forbidden)
    before = stored_result.path.read_bytes()
    first = be.recover_local_result(stored_result.context, stored_result.record)
    second = be.recover_local_result(stored_result.context, stored_result.record)
    assert first == second
    assert first["status"] == "ok"
    assert stored_result.path.read_bytes() == before


@pytest.mark.parametrize("field", ["task_id", "attempt_id", "session"])
def test_recover_rejects_mismatched_result_identity(
    stored_result: StoredResult, field: str
) -> None:
    data = stored_result.read()
    data[field] = "identidad_ajena"
    stored_result.write(data)
    result = be.recover_local_result(stored_result.context, stored_result.record)
    assert result["status"] == "pending"
    assert result["uncertain"] is True
    assert "result_mismatch" in result["limitations"]


def test_recover_rejects_changed_model(stored_result: StoredResult) -> None:
    current = load_task(stored_result.project, stored_result.record.task_id)
    current.model = "other/model"
    save_task(stored_result.project, current)
    result = be.recover_local_result(stored_result.context, stored_result.record)
    assert result["status"] == "pending"
    assert "provenance_unavailable" in result["limitations"]


def test_durable_source_without_host_provenance_is_not_success(
    stored_result: StoredResult, tmp_path: Path
) -> None:
    other_host = make_context(tmp_path / "other-host")
    result = be.recover_local_result(other_host, stored_result.record)
    assert result["status"] == "pending"
    assert "provenance_unavailable" in result["limitations"]


def test_durable_source_without_terminal_observation_is_not_success(
    stored_result: StoredResult,
) -> None:
    result = be._map_result(
        stored_result.record, stored_result.read(), agent="build", terminal=False
    )
    assert result["status"] == "pending"
    assert "terminal_unconfirmed" in result["limitations"]


@pytest.mark.parametrize("state", ["pending", "partial", "failed", "interrupted"])
def test_recover_rejects_completed_result_after_record_demotion(
    stored_result: StoredResult, state: DeliveryState
) -> None:
    current = load_task(stored_result.project, stored_result.record.task_id)
    current.delivery = DeliveryObservation(
        state, "durable_message", "2026-11-02T00:01:00+00:00"
    )
    save_task(stored_result.project, current)
    result = be.recover_local_result(stored_result.context, stored_result.record)
    assert result["status"] == "pending"
    assert result["delivery"] == "pending"
    assert result["uncertain"] is True
    assert "result_mismatch" in result["limitations"]


def test_legacy_completed_record_remains_accepted(stored_result: StoredResult) -> None:
    current = load_task(stored_result.project, stored_result.record.task_id)
    current.delivery = DeliveryObservation(
        "completed", "cli_event", "2026-11-02T00:00:00+00:00"
    )
    save_task(stored_result.project, current)
    result = be.recover_local_result(stored_result.context, stored_result.record)
    assert result["status"] == "ok"
    assert result["delivery"] == "completed"


def _observation(
    stored: StoredResult,
    *,
    accepted: bool = True,
    outcome: str = "completed",
    reason: str = "accepted",
    finish: str | None = "stop",
    identity: str = "verified",
    lifecycle: str = "committed",
    digest: str | None = None,
) -> ReconciliationObservation:
    return ReconciliationObservation(
        attempt_id=stored.record.attempt_id,
        session_id=stored.record.session,
        assistant_message_id="msg_1",
        observed_at="2026-11-03T09:00:00+00:00",
        generation=1,
        phase="response_observed",
        identity=identity,  # type: ignore[arg-type]
        lifecycle=lifecycle,  # type: ignore[arg-type]
        source="durable_message",
        accepted=accepted,
        outcome=outcome,  # type: ignore[arg-type]
        reason=reason,  # type: ignore[arg-type]
        finish=finish,  # type: ignore[arg-type]
        completed_at=123,
        limitations=(),
        result_sha256=digest or hashlib.sha256(stored.path.read_bytes()).hexdigest(),
    )


def _save_observation(
    stored: StoredResult, observation: ReconciliationObservation
) -> None:
    current = load_task(stored.project, stored.record.task_id)
    current.reconciliation = observation
    save_task(stored.project, current)


def test_recover_accepts_current_committed_observation(
    stored_result: StoredResult,
) -> None:
    _save_observation(stored_result, _observation(stored_result))

    result = be.recover_local_result(stored_result.context, stored_result.record)

    assert result["status"] == "ok"
    assert result["delivery"] == "completed"


@pytest.mark.parametrize("source", ["cli_event", "durable_message"])
def test_recover_rejects_negative_observation_regardless_of_delivery_source(
    stored_result: StoredResult,
    monkeypatch: pytest.MonkeyPatch,
    source: str,
) -> None:
    current = load_task(stored_result.project, stored_result.record.task_id)
    assert current.delivery is not None
    current.delivery = DeliveryObservation(
        "completed", source, "2026-11-02T00:01:00+00:00"
    )
    save_task(stored_result.project, current)
    _save_observation(
        stored_result,
        _observation(
            stored_result,
            accepted=False,
            outcome="partial",
            reason="finish_length",
            finish="length",
        ),
    )
    monkeypatch.setattr(
        FakeBinding,
        "request",
        lambda *args, **kwargs: pytest.fail("La recovery no debe consultar el backend"),
    )

    result = be.recover_local_result(stored_result.context, stored_result.record)

    assert result["status"] == "pending"
    assert result["delivery"] == "pending"
    assert "result_mismatch" in result["limitations"]


def test_recover_rejects_reconciliation_digest_mismatch(
    stored_result: StoredResult, monkeypatch: pytest.MonkeyPatch
) -> None:
    _save_observation(
        stored_result,
        _observation(stored_result, digest="0" * 64),
    )
    monkeypatch.setattr(
        FakeBinding,
        "request",
        lambda *args, **kwargs: pytest.fail("La recovery no debe consultar el backend"),
    )

    result = be.recover_local_result(stored_result.context, stored_result.record)

    assert result["status"] == "pending"
    assert result["delivery"] == "pending"
    assert "result_mismatch" in result["limitations"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("attempt_id", "9b2f7b1c-6f2d-4f7b-a5e3-3c9f6f3a2b1d"),
        ("session_id", "ses_foreign"),
        ("generation", True),
    ],
)
def test_recover_malformed_or_cross_attempt_observation_never_completes(
    stored_result: StoredResult, field: str, value: object
) -> None:
    current = load_task(stored_result.project, stored_result.record.task_id)
    current.reconciliation = _observation(stored_result)
    save_task(stored_result.project, current)
    record_file = (
        stored_result.project / ".aikit" / "sessions" / current.task_id / "record.json"
    )
    payload: dict[str, Any] = json.loads(record_file.read_text(encoding="utf-8"))
    reconciliation = payload["reconciliation"]
    assert isinstance(reconciliation, dict)
    reconciliation[field] = value
    record_file.write_text(json.dumps(payload), encoding="utf-8")

    result = be.recover_local_result(stored_result.context, stored_result.record)

    assert result["status"] == "pending"
    assert result["delivery"] == "pending"
    assert "provenance_unavailable" in result["limitations"]


def test_recover_committed_negative_keeps_conservative_delivery(
    stored_result: StoredResult,
) -> None:
    report = stored_result.read()
    report["status"] = "pending"
    report["delivery"] = "partial"
    stored_result.write(report)
    current = load_task(stored_result.project, stored_result.record.task_id)
    current.delivery = DeliveryObservation(
        "partial", "cli_event", "2026-11-03T09:00:00+00:00"
    )
    save_task(stored_result.project, current)
    _save_observation(
        stored_result,
        _observation(
            stored_result,
            accepted=False,
            outcome="partial",
            reason="finish_length",
            finish="length",
        ),
    )

    result = be.recover_local_result(stored_result.context, stored_result.record)

    assert result["status"] == "pending"
    assert result["delivery"] == "partial"


def test_recover_uses_one_result_snapshot_for_parse_and_digest(
    stored_result: StoredResult, monkeypatch: pytest.MonkeyPatch
) -> None:
    _save_observation(stored_result, _observation(stored_result))
    original_read = be._read_artifact
    exact_bytes = stored_result.path.read_bytes()
    snapshot_taken = False

    def replace_after_snapshot(record: TaskRecord, name: str) -> bytes | None:
        nonlocal snapshot_taken
        if name == "result.json" and not snapshot_taken:
            snapshot_taken = True
            stored_result.path.write_bytes(exact_bytes + b" ")
            return exact_bytes
        return original_read(record, name)

    monkeypatch.setattr(be, "_read_artifact", replace_after_snapshot)

    result = be.recover_local_result(stored_result.context, stored_result.record)

    assert snapshot_taken is True
    assert result["status"] == "ok"
    assert result["delivery"] == "completed"
