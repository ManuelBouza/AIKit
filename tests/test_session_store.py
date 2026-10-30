"""Persistencia validada, confinada y atómica de tareas OpenCode."""

from __future__ import annotations

import json
import os
from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest
from session_store import (
    DeliveryObservation,
    ExecutionObservation,
    ProcessIdentity,
    QuotaResume,
    StoreError,
    TaskRecord,
    WaitingReason,
    load_task,
    lock_session,
    lock_task,
    save_task,
)

TASK_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
OTHER_TASK_ID = "4fa85f64-5717-4562-b3fc-2c963f66afa6"
ATTEMPT_ID = "7c9e6679-7425-40de-944b-e07fc1f90ae7"
PREVIOUS_ATTEMPT_ID = "9b2f7b1c-6f2d-4f7b-a5e3-3c9f6f3a2b1d"
OBSERVED_AT = "2026-10-30T12:00:00+00:00"


def make_record(root: Path) -> TaskRecord:
    return TaskRecord(
        version=1,
        task_id=TASK_ID,
        attempt_id=ATTEMPT_ID,
        previous_attempt_ids=[PREVIOUS_ATTEMPT_ID],
        role="implementer",
        cwd=str(root.resolve()),
        model="opencode-go/kimi-k3.1-pro",
        variant="high",
        reason="capacidad suficiente para la implementación",
        pricing="unknown",
        session=None,
        server_identity=None,
        client=None,
        supervisor=None,
        client_timeout_seconds=30.0,
        execution_timeout_seconds=300.0,
        execution=ExecutionObservation(
            state="active", source="supervisor", observed_at=OBSERVED_AT
        ),
        delivery=DeliveryObservation(
            state="pending", source="supervisor", observed_at=OBSERVED_AT
        ),
        last_event_at=OBSERVED_AT,
        cursor="event-1",
        quota_resume=None,
    )


def record_path(root: Path) -> Path:
    return root / ".aikit" / "sessions" / TASK_ID / "record.json"


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    return cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))


def test_roundtrip_allows_unknown_session_during_startup(tmp_path: Path) -> None:
    original = make_record(tmp_path)

    save_task(tmp_path, original)

    assert load_task(tmp_path, TASK_ID) == original
    assert load_task(tmp_path, TASK_ID).session is None


def test_roundtrip_preserves_attempt_history_and_quota_resume_data(
    tmp_path: Path,
) -> None:
    original = replace(
        make_record(tmp_path),
        session="ses_abc-123",
        server_identity="server-1",
        client=ProcessIdentity(pid=1234, started_at=OBSERVED_AT),
        supervisor=ProcessIdentity(pid=5678, started_at=OBSERVED_AT),
        quota_resume=QuotaResume(
            scope="quota_resume",
            evidence="cuota agotada; evidencia sanitizada",
            previous_model="opencode-go/kimi-k3.1-pro",
            new_model="openai/gpt-5.2",
            alternatives_reason="no había alternativas adecuadas disponibles",
        ),
    )

    save_task(tmp_path, original)

    restored = load_task(tmp_path, TASK_ID)
    assert restored.previous_attempt_ids == [PREVIOUS_ATTEMPT_ID]
    assert restored.quota_resume == original.quota_resume
    assert restored == original


def test_execution_waiting_reason_is_optional_but_validated(tmp_path: Path) -> None:
    record = make_record(tmp_path)
    record.execution = ExecutionObservation(
        state="waiting",
        source="backend",
        observed_at=OBSERVED_AT,
        waiting_reason="permission",
    )
    save_task(tmp_path, record)
    assert load_task(tmp_path, TASK_ID).execution == record.execution

    record.execution.waiting_reason = cast(WaitingReason, "unexpected")
    with pytest.raises(StoreError) as error:
        save_task(tmp_path, record)
    assert error.value.code == "invalid_record"


def test_future_version_fails_without_being_overwritten(tmp_path: Path) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    payload = read_json(path)
    payload["version"] = 2
    write_json(path, payload)
    before = path.read_bytes()

    with pytest.raises(StoreError) as load_error:
        load_task(tmp_path, TASK_ID)
    with pytest.raises(StoreError) as save_error:
        save_task(tmp_path, make_record(tmp_path))

    assert load_error.value.code == "unsupported_version"
    assert save_error.value.code == "unsupported_version"
    assert path.read_bytes() == before


def test_corrupt_record_fails_without_being_overwritten(tmp_path: Path) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    path.write_bytes(b'{"version": 1,')
    before = path.read_bytes()

    with pytest.raises(StoreError) as load_error:
        load_task(tmp_path, TASK_ID)
    with pytest.raises(StoreError) as save_error:
        save_task(tmp_path, make_record(tmp_path))

    assert load_error.value.code == "record_corrupt"
    assert save_error.value.code == "record_corrupt"
    assert path.read_bytes() == before


def test_unknown_record_fields_are_rejected(tmp_path: Path) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    payload = read_json(path)
    payload["prompt"] = "contenido que no pertenece al registro"
    write_json(path, payload)

    with pytest.raises(StoreError) as error:
        load_task(tmp_path, TASK_ID)
    assert error.value.code == "invalid_record"


def test_record_identity_must_match_its_directory(tmp_path: Path) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    payload = read_json(path)
    payload["task_id"] = OTHER_TASK_ID
    write_json(path, payload)
    before = path.read_bytes()

    with pytest.raises(StoreError) as load_error:
        load_task(tmp_path, TASK_ID)
    with pytest.raises(StoreError) as save_error:
        save_task(tmp_path, make_record(tmp_path))

    assert load_error.value.code == "task_id_mismatch"
    assert save_error.value.code == "task_id_mismatch"
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "field_path",
    [
        ("role",),
        ("pricing",),
        ("execution", "state"),
        ("execution", "waiting_reason"),
        ("delivery", "state"),
    ],
)
@pytest.mark.parametrize("malformed", [[], {}, 1, True])
def test_non_string_enumeration_values_raise_invalid_record(
    tmp_path: Path, field_path: tuple[str, ...], malformed: object
) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    payload = read_json(path)
    target = payload
    for component in field_path[:-1]:
        target = cast(dict[str, object], target[component])
    target[field_path[-1]] = malformed
    write_json(path, payload)

    with pytest.raises(StoreError) as error:
        load_task(tmp_path, TASK_ID)
    assert error.value.code == "invalid_record"


@pytest.mark.parametrize(
    "field_path",
    [("role",), ("pricing",), ("execution", "state"), ("delivery", "state")],
)
def test_null_required_enumeration_values_raise_invalid_record(
    tmp_path: Path, field_path: tuple[str, ...]
) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    payload = read_json(path)
    target = payload
    for component in field_path[:-1]:
        target = cast(dict[str, object], target[component])
    target[field_path[-1]] = None
    write_json(path, payload)

    with pytest.raises(StoreError) as error:
        load_task(tmp_path, TASK_ID)
    assert error.value.code == "invalid_record"


@pytest.mark.parametrize(
    "field", ["client_timeout_seconds", "execution_timeout_seconds"]
)
@pytest.mark.parametrize("operation", ["load", "save"])
def test_huge_json_timeout_raises_invalid_record_and_preserves_bytes(
    tmp_path: Path, field: str, operation: str
) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    payload = read_json(path)
    payload[field] = 10**400
    write_json(path, payload)
    before = path.read_bytes()

    if operation == "load":
        with pytest.raises(StoreError) as error:
            load_task(tmp_path, TASK_ID)
    else:
        with pytest.raises(StoreError) as error:
            save_task(tmp_path, make_record(tmp_path))

    assert error.value.code == "invalid_record"
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "field", ["client_timeout_seconds", "execution_timeout_seconds"]
)
def test_save_rejects_huge_timeout_before_replacing_previous_json(
    tmp_path: Path, field: str
) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    before = path.read_bytes()
    record = make_record(tmp_path)
    setattr(record, field, 10**400)

    with pytest.raises(StoreError) as error:
        save_task(tmp_path, record)

    assert error.value.code == "invalid_record"
    assert path.read_bytes() == before


TEXT_FIELD_PATHS = [
    ("model",),
    ("variant",),
    ("reason",),
    ("server_identity",),
    ("cursor",),
    ("execution", "source"),
    ("delivery", "source"),
    ("quota_resume", "evidence"),
    ("quota_resume", "previous_model"),
    ("quota_resume", "new_model"),
    ("quota_resume", "alternatives_reason"),
]


def record_with_quota_resume(root: Path) -> TaskRecord:
    return replace(
        make_record(root),
        quota_resume=QuotaResume(
            scope="quota_resume",
            evidence="cuota agotada; evidencia sanitizada",
            previous_model="provider/previous",
            new_model="provider/next",
            alternatives_reason="sin alternativa adecuada",
        ),
    )


@pytest.mark.parametrize("field_path", TEXT_FIELD_PATHS)
@pytest.mark.parametrize("surrogate_code", [0xD800, 0xDFFF], ids=["high", "low"])
@pytest.mark.parametrize("operation", ["load", "save"])
def test_json_surrogate_raises_invalid_record_and_preserves_bytes(
    tmp_path: Path, field_path: tuple[str, ...], surrogate_code: int, operation: str
) -> None:
    save_task(tmp_path, record_with_quota_resume(tmp_path))
    path = record_path(tmp_path)
    payload = read_json(path)
    target = payload
    for component in field_path[:-1]:
        target = cast(dict[str, object], target[component])
    target[field_path[-1]] = "bad" + chr(surrogate_code) + "value"
    write_json(path, payload)
    before = path.read_bytes()

    if operation == "load":
        with pytest.raises(StoreError) as error:
            load_task(tmp_path, TASK_ID)
    else:
        with pytest.raises(StoreError) as error:
            save_task(tmp_path, make_record(tmp_path))

    assert error.value.code == "invalid_record"
    assert path.read_bytes() == before


@pytest.mark.parametrize("field_path", TEXT_FIELD_PATHS)
@pytest.mark.parametrize("surrogate_code", [0xD800, 0xDFFF], ids=["high", "low"])
def test_save_rejects_surrogate_before_replacing_previous_json(
    tmp_path: Path, field_path: tuple[str, ...], surrogate_code: int
) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    before = path.read_bytes()
    record = record_with_quota_resume(tmp_path)
    target: object = record
    for component in field_path[:-1]:
        target = getattr(target, component)
    setattr(target, field_path[-1], "bad" + chr(surrogate_code) + "value")

    with pytest.raises(StoreError) as error:
        save_task(tmp_path, record)

    assert error.value.code == "invalid_record"
    assert path.read_bytes() == before


@pytest.mark.parametrize("operation", ["load", "save"])
def test_deep_json_raises_record_corrupt_and_preserves_bytes(
    tmp_path: Path, operation: str
) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    path.write_text("[" * 20_000 + "0" + "]" * 20_000, encoding="utf-8")
    before = path.read_bytes()

    if operation == "load":
        with pytest.raises(StoreError) as error:
            load_task(tmp_path, TASK_ID)
    else:
        with pytest.raises(StoreError) as error:
            save_task(tmp_path, make_record(tmp_path))

    assert error.value.code == "record_corrupt"
    assert path.read_bytes() == before


def test_replace_failure_preserves_previous_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    before = path.read_bytes()

    def fail_replace(source: object, destination: object) -> None:
        raise OSError("fallo simulado antes del reemplazo")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(StoreError) as error:
        save_task(tmp_path, replace(make_record(tmp_path), variant=None))

    assert error.value.code == "store_io"
    assert path.read_bytes() == before
    assert load_task(tmp_path, TASK_ID).variant == "high"


@pytest.mark.parametrize(
    "task_id",
    [
        "",
        TASK_ID.upper(),
        "../" + TASK_ID,
        "/tmp/" + TASK_ID,
        r"C:\tmp\task",
        r"\\server\share\task",
    ],
)
def test_task_identifiers_reject_noncanonical_ids_and_paths(
    tmp_path: Path, task_id: str
) -> None:
    with pytest.raises(StoreError) as load_error:
        load_task(tmp_path, task_id)
    with pytest.raises(StoreError) as lock_error:
        with lock_task(tmp_path, task_id):
            pass
    assert load_error.value.code == "invalid_task_id"
    assert lock_error.value.code == "invalid_task_id"


@pytest.mark.parametrize(
    "session_id",
    [
        "",
        ".",
        "..",
        "../session",
        "session/other",
        r"session\other",
        r"C:\tmp\session",
        r"\rooted-session",
        r"\\server\share\session",
    ],
)
def test_session_identifiers_reject_traversal_and_windows_paths(
    tmp_path: Path, session_id: str
) -> None:
    with pytest.raises(StoreError) as error:
        with lock_session(tmp_path, session_id):
            pass
    assert error.value.code == "invalid_session_id"


def test_record_rejects_a_pid_without_startup_identity(tmp_path: Path) -> None:
    save_task(tmp_path, make_record(tmp_path))
    path = record_path(tmp_path)
    payload = read_json(path)
    payload["client"] = {"pid": os.getpid()}
    write_json(path, payload)

    with pytest.raises(StoreError) as error:
        load_task(tmp_path, TASK_ID)
    assert error.value.code == "invalid_record"


def test_non_directory_root_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "not-a-directory"
    root.write_text("archivo", encoding="utf-8")

    with pytest.raises(StoreError) as error:
        save_task(root, make_record(tmp_path))
    assert error.value.code == "invalid_root"


def test_non_directory_managed_component_is_rejected(tmp_path: Path) -> None:
    (tmp_path / ".aikit").write_text("archivo", encoding="utf-8")

    with pytest.raises(StoreError) as error:
        save_task(tmp_path, make_record(tmp_path))
    assert error.value.code == "unsafe_path"


def make_symlink(link: Path, target: Path, directory: bool) -> None:
    try:
        os.symlink(target, link, target_is_directory=directory)
    except (NotImplementedError, OSError) as error:
        pytest.skip(f"el sistema no permite crear este enlace: {error}")


def test_aikit_symlink_cannot_redirect_writes(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "project"
    root.mkdir()
    make_symlink(root / ".aikit", outside, directory=True)

    with pytest.raises(StoreError) as save_error:
        save_task(root, make_record(root))
    with pytest.raises(StoreError) as load_error:
        load_task(root, TASK_ID)
    assert save_error.value.code == "unsafe_path"
    assert load_error.value.code == "unsafe_path"
    assert list(outside.iterdir()) == []


def test_task_directory_symlink_cannot_redirect_writes(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    sessions = tmp_path / ".aikit" / "sessions"
    sessions.mkdir(parents=True)
    make_symlink(sessions / TASK_ID, outside, directory=True)

    with pytest.raises(StoreError) as save_error:
        save_task(tmp_path, make_record(tmp_path))
    with pytest.raises(StoreError) as load_error:
        load_task(tmp_path, TASK_ID)
    assert save_error.value.code == "unsafe_path"
    assert load_error.value.code == "unsafe_path"
    assert list(outside.iterdir()) == []


def test_record_symlink_is_not_read_or_replaced(tmp_path: Path) -> None:
    outside = tmp_path / "outside.json"
    outside.write_text('{"privado": true}', encoding="utf-8")
    task_dir = tmp_path / ".aikit" / "sessions" / TASK_ID
    task_dir.mkdir(parents=True)
    link = task_dir / "record.json"
    make_symlink(link, outside, directory=False)
    before = outside.read_bytes()

    for operation in (
        lambda: load_task(tmp_path, TASK_ID),
        lambda: save_task(tmp_path, make_record(tmp_path)),
    ):
        with pytest.raises(StoreError) as error:
            operation()
        assert error.value.code == "unsafe_path"
    assert outside.read_bytes() == before


def test_lock_contention_has_stable_error_and_releases_in_process(
    tmp_path: Path,
) -> None:
    with lock_task(tmp_path, TASK_ID):
        with pytest.raises(StoreError) as error:
            with lock_task(tmp_path, TASK_ID):
                pass
        assert error.value.code == "lock_contended"

    with lock_task(tmp_path, TASK_ID):
        pass
