"""Recuperación local de entrega durable sin repetir inferencia."""

from __future__ import annotations

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
