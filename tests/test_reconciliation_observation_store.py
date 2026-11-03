"""Compatibilidad legacy y validación de la observación de reconciliación."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
import session_store
from session_store import StoreError, load_task, save_task

from tests.test_session_store import (
    OBSERVED_AT,
    TASK_ID,
    make_record,
    read_json,
    record_path,
    write_json,
)


def _observation_type() -> Any:
    observation_type = getattr(session_store, "ReconciliationObservation", None)
    assert observation_type is not None, "Falta el tipo de observación opcional"
    return observation_type


def _observation() -> Any:
    return _observation_type()(
        attempt_id="7c9e6679-7425-40de-944b-e07fc1f90ae7",
        session_id="ses_abc-123",
        assistant_message_id="msg_1",
        observed_at=OBSERVED_AT,
        generation=1,
        phase="response_observed",
        identity="verified",
        lifecycle="committed",
        source="durable_message",
        accepted=True,
        outcome="completed",
        reason="accepted",
        finish="stop",
        completed_at=123,
        limitations=(),
        result_sha256="a" * 64,
    )


def test_legacy_record_without_reconciliation_loads_and_omits_key(
    tmp_path: Path,
) -> None:
    original = make_record(tmp_path)

    save_task(tmp_path, original)

    assert load_task(tmp_path, TASK_ID) == original
    assert load_task(tmp_path, TASK_ID).reconciliation is None
    assert "reconciliation" not in read_json(record_path(tmp_path))


def test_reconciliation_record_round_trips_and_validates(tmp_path: Path) -> None:
    observation = _observation()
    original = replace(
        make_record(tmp_path),
        session="ses_abc-123",
        server_identity="owner-1",
        reconciliation=observation,
    )

    save_task(tmp_path, original)

    restored = load_task(tmp_path, TASK_ID)
    assert restored == original
    assert (
        restored.reconciliation is observation or restored.reconciliation == observation
    )
    assert read_json(record_path(tmp_path))["reconciliation"] is not None


@pytest.mark.parametrize(
    ("field", "malformed"),
    [
        ("lifecycle", "trusted"),
        ("identity", "verified-ish"),
        ("generation", True),
        ("completed_at", True),
        ("result_sha256", "not-a-sha256"),
        ("reason", "password=never-persist-this"),
    ],
)
def test_malformed_reconciliation_fails_closed_without_echoing_input(
    tmp_path: Path, field: str, malformed: object
) -> None:
    original = replace(
        make_record(tmp_path),
        session="ses_abc-123",
        server_identity="owner-1",
        reconciliation=_observation(),
    )
    save_task(tmp_path, original)
    payload = read_json(record_path(tmp_path))
    observation = payload["reconciliation"]
    assert isinstance(observation, dict)
    observation[field] = malformed
    write_json(record_path(tmp_path), payload)

    with pytest.raises(StoreError) as error:
        load_task(tmp_path, TASK_ID)

    assert error.value.code == "invalid_record"
    assert "password=never-persist-this" not in str(error.value)
