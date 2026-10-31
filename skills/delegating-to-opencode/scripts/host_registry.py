"""Procedencia privada del host: reservas conservadoras y escrituras atómicas."""

from __future__ import annotations

import ctypes
import json
import os
import re
import sys
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from availability_state import CatalogAdmission, admission_from_json
from service_identity import HostContext, _windows_registration_trusted
from session_store import (
    ProcessIdentity,
    StoreError,
    TaskRecord,
    _atomic_replace,
    _managed_directory,
    _open_shared_read,
    _process_identity_from_json,
    _require_directory,
    _require_regular_file,
    _root_path,
    _validate_record,
    _validate_session_id,
    _validate_task_id,
    _without_duplicate_keys,
)

if sys.platform == "win32":
    import msvcrt
else:
    import fcntl

HOST_VERSION = 1
MAX_HOST_BYTES = 64 * 1024
MAX_HOST_DEPTH = 8
_TOKEN = re.compile(r"aikit-owner-v1-[0-9a-f]{64}\Z")


class HostRegistryError(Exception):
    def __init__(
        self, code: str, message: str = "Procedencia del host no disponible."
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


RegistryError = HostRegistryError


@dataclass
class HostAttempt:
    attempt_id: str
    launch_nonce: str
    binding_token: str
    session_id: str | None
    agent: str
    role: str
    model: str
    variant: str | None
    phase: str
    project_root: str
    client: ProcessIdentity | None = None
    supervisor: ProcessIdentity | None = None
    source: str = "host_reservation"
    observed_at: str = ""
    admission: CatalogAdmission | None = None


@dataclass
class HostTask:
    version: int
    task_id: str
    project_root: str
    role: str
    current_attempt_id: str | None = None
    attempts: list[HostAttempt] = field(default_factory=list)


def _uuid(value: Any, code: str = "invalid_host") -> str:
    try:
        return _validate_task_id(value)
    except StoreError as exc:
        raise HostRegistryError(code) from exc


def _root(value: str) -> str:
    try:
        path = Path(value)
        if not path.is_absolute():
            raise HostRegistryError("invalid_root")
        # Reject links in every component before resolving.
        for part in (*reversed(path.parents), path):
            _require_directory(part)
        return os.path.normcase(str(_root_path(path).resolve(strict=True)))
    except (StoreError, ValueError, OSError) as exc:
        raise HostRegistryError("invalid_root") from exc


def _private(path: Path, *, created: bool = False) -> None:
    """DACL protegida de usuario/SYSTEM/Administradores para directorios nuevos."""
    if sys.platform != "win32":
        info = path.stat()
        if info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise HostRegistryError("host_untrusted")
        return
    api = ctypes.windll.advapi32
    kernel = ctypes.windll.kernel32
    if created:
        descriptor = ctypes.c_void_p()
        size = ctypes.c_ulong()
        if not api.ConvertStringSecurityDescriptorToSecurityDescriptorW(
            "D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)(A;OICI;FA;;;OW)",
            1,
            ctypes.byref(descriptor),
            ctypes.byref(size),
        ):
            raise HostRegistryError("host_untrusted")
        try:
            if not api.SetFileSecurityW(str(path), 0x80000004, descriptor):
                raise HostRegistryError("host_untrusted")
        finally:
            kernel.LocalFree(descriptor)
    if not _windows_registration_trusted(path):
        raise HostRegistryError("host_untrusted")
    # Inspect EVERY grant, including read-only grants, against owner and trusted SIDs.
    owner, dacl, sd = ctypes.c_void_p(), ctypes.c_void_p(), ctypes.c_void_p()
    if (
        api.GetNamedSecurityInfoW(
            str(path),
            1,
            5,
            ctypes.byref(owner),
            None,
            ctypes.byref(dacl),
            None,
            ctypes.byref(sd),
        )
        != 0
    ):
        raise HostRegistryError("host_untrusted")
    allocated: list[ctypes.c_void_p] = []
    try:
        if not dacl.value or not owner.value:
            raise HostRegistryError("host_untrusted")
        allowed = [owner]
        for sid in ("S-1-5-18", "S-1-5-32-544", "S-1-3-4"):
            ptr = ctypes.c_void_p()
            if not api.ConvertStringSidToSidW(sid, ctypes.byref(ptr)):
                raise HostRegistryError("host_untrusted")
            allocated.append(ptr)
            allowed.append(ptr)
        count = ctypes.c_ushort.from_address(dacl.value + 4).value
        api.EqualSid.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        for index in range(count):
            ace = ctypes.c_void_p()
            if not api.GetAce(dacl, index, ctypes.byref(ace)) or not ace.value:
                raise HostRegistryError("host_untrusted")
            kind = ctypes.c_ubyte.from_address(ace.value).value
            if kind == 1:  # deny does not confer authority
                continue
            if kind != 0 or not any(api.EqualSid(p, ace.value + 8) for p in allowed):
                raise HostRegistryError("host_untrusted")
    finally:
        for p in allocated:
            kernel.LocalFree(p)
        kernel.LocalFree(sd)


def _host_dir(context: HostContext, task_id: str, *, create: bool = False) -> Path:
    _uuid(task_id, "invalid_task_id")
    state = context.aikit_state
    if not state.is_absolute():
        raise HostRegistryError("unsafe_path")
    try:
        # No mkdir(parents=True): every existing ancestor is checked first.
        for path in (
            *reversed(state.parents),
            state,
            state / "tasks",
            state / "tasks" / task_id,
        ):
            created = False
            if not path.exists() and create:
                try:
                    path.mkdir(mode=0o700)
                    created = True
                except FileExistsError:
                    pass
            _require_directory(path)
            if path == state or state in path.parents:
                _private(path, created=created)
        return _managed_directory(state, ("tasks", task_id), create=False)
    except (StoreError, OSError) as exc:
        raise HostRegistryError(
            "host_not_found"
            if isinstance(exc.__cause__, FileNotFoundError)
            else "unsafe_path"
        ) from exc


def _host_file(context: HostContext, task_id: str) -> Path:
    return _host_dir(context, task_id) / "host.json"


def _parse(data: Any) -> HostTask:
    try:
        if not isinstance(data, dict) or type(data.get("version")) is not int:
            raise ValueError
        if data["version"] != 1:
            raise HostRegistryError("unsupported_version")
        if set(data) != {
            "version",
            "task_id",
            "project_root",
            "role",
            "current_attempt_id",
            "attempts",
        }:
            raise ValueError
        _uuid(data["task_id"])
        if data["project_root"] != _root(data["project_root"]) or data["role"] not in (
            "implementer",
            "reviewer",
        ):
            raise ValueError
        if not isinstance(data["attempts"], list) or not data["attempts"]:
            raise ValueError
        attempts = []
        for raw in data["attempts"]:
            keys = set(HostAttempt.__dataclass_fields__)
            if (
                not isinstance(raw, dict)
                or set(raw) - keys
                or keys - {"admission"} - set(raw)
            ):
                raise ValueError
            item = dict(raw)
            item["admission"] = admission_from_json(item.get("admission"))
            _uuid(item["attempt_id"])
            _uuid(item["launch_nonce"])
            if not isinstance(item["binding_token"], str) or not _TOKEN.fullmatch(
                item["binding_token"]
            ):
                raise ValueError
            if item["session_id"] is not None:
                _validate_session_id(item["session_id"])
            if (
                item["agent"] not in ("build", "plan")
                or item["role"] != data["role"]
                or item["project_root"] != data["project_root"]
            ):
                raise ValueError
            if item["phase"] not in (
                "reserved",
                "client_started",
                "session_observed",
                "terminal_observed",
                "uncertain",
            ):
                raise ValueError
            for key in ("model", "source", "observed_at"):
                if not isinstance(item[key], str) or not item[key].strip():
                    raise ValueError
            if item["variant"] is not None and (
                not isinstance(item["variant"], str) or not item["variant"].strip()
            ):
                raise ValueError
            from session_store import _timestamp

            _timestamp(item["observed_at"])
            item["client"] = _process_identity_from_json(item["client"])
            item["supervisor"] = _process_identity_from_json(item["supervisor"])
            attempts.append(HostAttempt(**item))
        ids = [a.attempt_id for a in attempts]
        if len(set(ids)) != len(ids) or data["current_attempt_id"] != ids[-1]:
            raise ValueError
        return HostTask(**{**data, "attempts": attempts})
    except (ValueError, TypeError, KeyError, StoreError, RecursionError) as exc:
        raise HostRegistryError("invalid_host") from exc


def _read_host(context: HostContext, task_id: str) -> HostTask:
    path = _host_file(context, task_id)
    try:
        _require_regular_file(path)
        _private(path)
        with _open_shared_read(path) as stream:
            raw = stream.read(MAX_HOST_BYTES + 1)
        if len(raw) > MAX_HOST_BYTES:
            raise HostRegistryError("host_too_large")
        task = _parse(json.loads(raw, object_pairs_hook=_without_duplicate_keys))
        if task.task_id != task_id:
            raise HostRegistryError("task_mismatch")
        return task
    except (OSError, StoreError, ValueError, RecursionError) as exc:
        raise HostRegistryError(
            "host_not_found"
            if isinstance(exc, FileNotFoundError)
            or isinstance(exc.__cause__, FileNotFoundError)
            else "invalid_host"
        ) from exc


def _write_host(context: HostContext, task_id: str, host: HostTask) -> None:
    directory = _host_dir(context, task_id)
    data = asdict(host)
    _parse(data)
    payload = json.dumps(data, ensure_ascii=True, allow_nan=False).encode()
    if len(payload) > MAX_HOST_BYTES:
        raise HostRegistryError("host_too_large")
    path = directory / "host.json"
    if path.exists():
        _require_regular_file(path)
        _private(path)
    descriptor, name = tempfile.mkstemp(prefix=".host-", suffix=".tmp", dir=directory)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _private(temporary)
        _atomic_replace(temporary, path)
    except OSError as exc:
        raise HostRegistryError("host_io") from exc
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def _lock_host(context: HostContext, task_id: str) -> Iterator[None]:
    directory = _host_dir(context, task_id, create=True)
    path = directory / "host.lock"
    if path.exists():
        _require_regular_file(path)
        _private(path)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        _private(path)
        try:
            if sys.platform == "win32":
                msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise HostRegistryError("host_locked") from exc
        try:
            yield
        finally:
            if sys.platform == "win32":
                os.lseek(descriptor, 0, 0)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def load_host_task(context: HostContext, task_id: str) -> HostTask:
    return _read_host(context, task_id)


def _validate(record: TaskRecord) -> str:
    try:
        _validate_record(record)
    except StoreError as exc:
        raise HostRegistryError("invalid_record") from exc
    if not isinstance(record.server_identity, str) or not _TOKEN.fullmatch(
        record.server_identity
    ):
        raise HostRegistryError("missing_binding")
    return _root(record.cwd)


def _match(
    host: HostTask, record: TaskRecord, *, allow_unpublished: bool = False
) -> HostAttempt:
    root = _validate(record)
    if (
        host.task_id != record.task_id
        or host.project_root != root
        or host.role != record.role
    ):
        raise HostRegistryError("provenance_unavailable")
    current = host.attempts[-1]
    if (
        current.attempt_id != record.attempt_id
        or current.binding_token != record.server_identity
        or current.model != record.model
        or current.variant != record.variant
    ):
        raise HostRegistryError("provenance_unavailable")
    if [a.attempt_id for a in host.attempts[:-1]] != record.previous_attempt_ids:
        raise HostRegistryError("ancestry_mismatch")
    if current.session_id != record.session and not (
        allow_unpublished and record.session is None
    ):
        raise HostRegistryError("session_mismatch")
    return current


def reserve_host_attempt(
    context: HostContext,
    record: TaskRecord,
    *,
    agent: str = "build",
    admission: CatalogAdmission | None = None,
) -> HostAttempt:
    from datetime import datetime, timezone

    root = _validate(record)
    if agent not in ("build", "plan") or record.session is not None:
        raise HostRegistryError("invalid_reservation")
    with _lock_host(context, record.task_id):
        path = _host_dir(context, record.task_id) / "host.json"
        history: list[HostAttempt] = []
        if path.exists():
            host = _read_host(context, record.task_id)
            history = host.attempts
            if host.project_root != root or host.role != record.role:
                raise HostRegistryError("provenance_unavailable")
            if (
                history[-1].phase != "terminal_observed"
                or [item.attempt_id for item in history] != record.previous_attempt_ids
                or record.attempt_id in record.previous_attempt_ids
            ):
                raise HostRegistryError("attempt_reserved")
        elif record.previous_attempt_ids:
            raise HostRegistryError("ancestry_mismatch")
        attempt = HostAttempt(
            record.attempt_id,
            str(uuid.uuid4()),
            record.server_identity or "",
            None,
            agent,
            record.role,
            record.model,
            record.variant,
            "reserved",
            root,
            observed_at=datetime.now(timezone.utc).isoformat(),
            admission=admission,
        )
        _write_host(
            context,
            record.task_id,
            HostTask(
                1,
                record.task_id,
                root,
                record.role,
                attempt.attempt_id,
                history + [attempt],
            ),
        )
        return attempt


def verify_provenance(context: HostContext, record: TaskRecord) -> HostAttempt:
    return _match(_read_host(context, record.task_id), record)


def record_host_session(
    context: HostContext, record: TaskRecord, session_id: str
) -> None:
    try:
        _validate_session_id(session_id)
    except StoreError as exc:
        raise HostRegistryError("invalid_session") from exc
    with _lock_host(context, record.task_id):
        host = _read_host(context, record.task_id)
        current = _match(host, record, allow_unpublished=True)
        if current.session_id not in (None, session_id):
            raise HostRegistryError("session_mismatch")
        from datetime import datetime, timezone

        current.observed_at = datetime.now(timezone.utc).isoformat()
        current.session_id = session_id
        current.phase = "session_observed"
        current.source = "cli_event"
        _write_host(context, record.task_id, host)


def record_host_processes(context: HostContext, record: TaskRecord) -> None:
    with _lock_host(context, record.task_id):
        host = _read_host(context, record.task_id)
        current = _match(host, record)
        current.client, current.supervisor = record.client, record.supervisor
        current.phase = "client_started"
        current.source = "os_process_birth"
        _write_host(context, record.task_id, host)


def record_host_observation(
    context: HostContext, record: TaskRecord, *, terminal: bool
) -> None:
    from datetime import datetime, timezone

    with _lock_host(context, record.task_id):
        host = _read_host(context, record.task_id)
        current = _match(host, record)
        current.phase = "terminal_observed" if terminal else "uncertain"
        current.source = "cli_terminal" if terminal else "client_observation"
        current.observed_at = datetime.now(timezone.utc).isoformat()
        _write_host(context, record.task_id, host)


def record_host_admission(
    context: HostContext, record: TaskRecord, admission: CatalogAdmission
) -> None:
    """Completa solo una reserva propia aun no enviada; no adopta intentos vivos."""
    with _lock_host(context, record.task_id):
        host = _read_host(context, record.task_id)
        current = _match(host, record)
        if current.admission is not None:
            if current.admission != admission:
                raise HostRegistryError("admission_mismatch")
            return
        if current.phase != "reserved" or current.session_id is not None:
            raise HostRegistryError("admission_unavailable")
        current.admission = admission
        _write_host(context, record.task_id, host)
