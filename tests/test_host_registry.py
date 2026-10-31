from __future__ import annotations

import os
from pathlib import Path

import host_registry as hr
import pytest
import service_identity as si
from session_store import TaskRecord


def _ctx(tmp_path: Path) -> si.HostContext:
    return si.HostContext(
        opencode_registration=tmp_path / "reg.json",
        aikit_state=tmp_path / "state",
        expected_version="2.2.0",
    )


def _record(tmp_path: Path) -> TaskRecord:
    root = tmp_path / "project"
    root.mkdir(exist_ok=True)
    return TaskRecord(
        version=1,
        task_id="11111111-2222-3333-4444-555555555555",
        attempt_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        previous_attempt_ids=[],
        role="implementer",
        cwd=str(root.resolve()),
        model="m",
        variant=None,
        reason="r",
        pricing="free",
        session=None,
        server_identity="aikit-owner-v1-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        client=None,
        supervisor=None,
        client_timeout_seconds=1.0,
        execution_timeout_seconds=1.0,
        execution=None,
        delivery=None,
        last_event_at=None,
        cursor=None,
        quota_resume=None,
    )


def test_load_missing_raises(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    with pytest.raises(hr.HostRegistryError):
        hr.load_host_task(ctx, "11111111-2222-3333-4444-555555555555")


def test_reserve_and_verify(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    record = _record(tmp_path)
    attempt = hr.reserve_host_attempt(ctx, record, agent="build")
    assert (
        attempt.binding_token
        == "aikit-owner-v1-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    )
    host = hr.load_host_task(ctx, record.task_id)
    assert host.current_attempt_id == attempt.attempt_id
    assert hr.verify_provenance(ctx, record).attempt_id == attempt.attempt_id


def test_record_session(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    record = _record(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    hr.record_host_session(ctx, record, "ses_1")
    host = hr.load_host_task(ctx, record.task_id)
    assert host.attempts[0].session_id == "ses_1"


def test_corrupt_host_fails(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    record = _record(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    path = ctx.aikit_state / "tasks" / record.task_id / "host.json"
    path.write_text("{bad", encoding="utf-8")
    with pytest.raises(hr.HostRegistryError):
        hr.load_host_task(ctx, record.task_id)


def test_root_mismatch_fails(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    record = _record(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    other = tmp_path / "other"
    other.mkdir()
    record2 = _record(tmp_path)
    record2.cwd = str(other.resolve())
    with pytest.raises(hr.HostRegistryError):
        hr.verify_provenance(ctx, record2)


def test_binding_mismatch_fails(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    record = _record(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    record.server_identity = "rotated"
    with pytest.raises(hr.HostRegistryError):
        hr.verify_provenance(ctx, record)


# Contratos faltantes: no fabricar procedencia de otro intento ni duplicar reservas.
def test_reserved_attempt_is_the_project_attempt(tmp_path: Path) -> None:
    record = _record(tmp_path)
    assert (
        hr.reserve_host_attempt(_ctx(tmp_path), record, agent="plan").attempt_id
        == record.attempt_id
    )


def test_second_reservation_never_releases_uncertainty(tmp_path: Path) -> None:
    record = _record(tmp_path)
    ctx = _ctx(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    before = hr._host_file(ctx, record.task_id).read_bytes()
    with pytest.raises(hr.HostRegistryError):
        hr.reserve_host_attempt(ctx, record, agent="build")
    assert hr._host_file(ctx, record.task_id).read_bytes() == before


def test_other_attempt_cannot_publish_session(tmp_path: Path) -> None:
    record = _record(tmp_path)
    ctx = _ctx(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    record.attempt_id = "bbbbbbbb-bbbb-cccc-dddd-eeeeeeeeeeee"
    with pytest.raises(hr.HostRegistryError):
        hr.record_host_session(ctx, record, "ses_foreign")


def test_project_session_without_host_session_is_rejected(tmp_path: Path) -> None:
    record = _record(tmp_path)
    ctx = _ctx(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    record.session = "ses_foreign"
    with pytest.raises(hr.HostRegistryError):
        hr.verify_provenance(ctx, record)


@pytest.mark.parametrize("value", ["../escape", "", "NOT-UUID"])
def test_task_id_is_checked_before_any_path(tmp_path: Path, value: str) -> None:
    with pytest.raises(hr.HostRegistryError) as exc:
        hr.load_host_task(_ctx(tmp_path), value)
    assert exc.value.code == "invalid_task_id"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("version", True),
        ("attempts", [1]),
        ("role", []),
        ("task_id", "00000000-0000-0000-0000-000000000000"),
    ],
)
def test_malformed_or_displaced_host_rejected(
    tmp_path: Path, field: str, value: object
) -> None:
    import json

    record = _record(tmp_path)
    ctx = _ctx(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    path = hr._host_file(ctx, record.task_id)
    data = json.loads(path.read_text())
    data[field] = value
    path.write_text(json.dumps(data))
    before = path.read_bytes()
    with pytest.raises(hr.HostRegistryError):
        hr.load_host_task(ctx, record.task_id)
    assert path.read_bytes() == before


def test_two_processes_cannot_reserve_one_attempt(tmp_path: Path) -> None:
    import subprocess
    import sys

    record = _record(tmp_path)
    ctx = _ctx(tmp_path)
    gate = tmp_path / "go"
    scripts = Path(hr.__file__).parent
    code = f"""
import sys,time
from pathlib import Path
sys.path.insert(0,{str(scripts)!r})
import host_registry as hr
from service_identity import HostContext
from tests.test_host_registry import _record
ctx=HostContext(Path({str(ctx.opencode_registration)!r}),Path({str(ctx.aikit_state)!r}),'2.2.0')
while not Path({str(gate)!r}).exists(): time.sleep(.005)
try:
 hr.reserve_host_attempt(ctx,_record(Path({str(tmp_path)!r})),agent='build')
 print('reserved')
except hr.HostRegistryError as exc: print(exc.code)
"""
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    children = [
        subprocess.Popen(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=flags,
        )
        for _ in range(2)
    ]
    gate.touch()
    results = []
    for child in children:
        out, err = child.communicate(timeout=10)
        assert child.returncode == 0, err.decode()
        results.append(out.decode().strip())
    assert results.count("reserved") == 1
    assert set(results) <= {"reserved", "host_locked", "attempt_reserved"}
    assert len(hr.load_host_task(ctx, record.task_id).attempts) == 1


def test_atomic_replace_failure_preserves_host_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record, ctx = _record(tmp_path), _ctx(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    before = hr._host_file(ctx, record.task_id).read_bytes()
    monkeypatch.setattr(
        hr, "_atomic_replace", lambda *a: (_ for _ in ()).throw(OSError("disk"))
    )
    with pytest.raises(hr.HostRegistryError):
        hr.record_host_session(ctx, record, "ses_1")
    assert hr._host_file(ctx, record.task_id).read_bytes() == before


def test_reparse_ancestor_fails_without_touching_target(tmp_path: Path) -> None:
    import subprocess
    import sys

    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "state"
    if sys.platform == "win32":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        assert result.returncode == 0
    else:
        os.symlink(target, link, target_is_directory=True)
    try:
        with pytest.raises(hr.HostRegistryError):
            hr.reserve_host_attempt(_ctx(tmp_path), _record(tmp_path), agent="build")
        assert list(target.iterdir()) == []
    finally:
        link.rmdir() if sys.platform == "win32" else link.unlink()


def test_no_rebuild_absent_host_from_project(tmp_path: Path) -> None:
    record, ctx = _record(tmp_path), _ctx(tmp_path)
    with pytest.raises(hr.HostRegistryError):
        hr.verify_provenance(ctx, record)
    assert not ctx.aikit_state.exists()


def test_host_acl_rejects_foreign_read_grant(tmp_path: Path) -> None:
    import subprocess
    import sys

    if sys.platform != "win32":
        pytest.skip("Win32 ACL contract")
    ctx, record = _ctx(tmp_path), _record(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    path = hr._host_file(ctx, record.task_id)
    change = subprocess.run(
        ["icacls", str(path), "/grant", "*S-1-1-0:(R)"],
        capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    assert change.returncode == 0, change.stderr.decode()
    before = path.read_bytes()
    with pytest.raises(hr.HostRegistryError, match="Procedencia"):
        hr.verify_provenance(ctx, record)
    assert path.read_bytes() == before


def test_next_attempt_requires_terminal_and_exact_ancestry(tmp_path: Path) -> None:
    from dataclasses import replace

    ctx, record = _ctx(tmp_path), _record(tmp_path)
    hr.reserve_host_attempt(ctx, record, agent="build")
    later = replace(
        record,
        attempt_id="bbbbbbbb-bbbb-cccc-dddd-eeeeeeeeeeee",
        previous_attempt_ids=[record.attempt_id],
    )
    with pytest.raises(hr.HostRegistryError):
        hr.reserve_host_attempt(ctx, later, agent="plan")
    hr.record_host_session(ctx, record, "ses_done")
    record.session = "ses_done"
    hr.record_host_observation(ctx, record, terminal=True)
    hr.reserve_host_attempt(ctx, later, agent="plan")
    host = hr.load_host_task(ctx, record.task_id)
    assert [a.attempt_id for a in host.attempts] == later.previous_attempt_ids + [
        later.attempt_id
    ]
    assert hr.verify_provenance(ctx, later).agent == "plan"
