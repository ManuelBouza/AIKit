"""Registro local validado y bloqueos para sesiones de OpenCode.

El módulo solo conserva metadatos de coordinación. No ejecuta clientes, no
consulta servidores y no almacena prompts, credenciales ni conversaciones.
"""

from __future__ import annotations

import json
import math
import os
import re
import stat
import sys
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Literal, TypedDict, cast

if sys.platform == "win32":
    import msvcrt
else:
    import fcntl

Role = Literal["implementer", "reviewer"]
Pricing = Literal["free", "paid", "unknown"]
ExecutionState = Literal["active", "waiting", "retrying", "idle", "unknown"]
DeliveryState = Literal["pending", "partial", "completed", "failed", "interrupted"]
WaitingReason = Literal["permission", "input"]


class StoreError(Exception):
    """Error controlado del almacén, con un código estable y breve."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class ExecutionObservation:
    state: ExecutionState
    source: str
    observed_at: str
    waiting_reason: WaitingReason | None = None


@dataclass
class DeliveryObservation:
    state: DeliveryState
    source: str
    observed_at: str


@dataclass
class ProcessIdentity:
    """Un PID solo se registra junto a su instante de arranque comprobable."""

    pid: int
    started_at: str


@dataclass
class QuotaResume:
    """Datos de una autorización acotada; no habilitan recuperación por sí solos."""

    scope: Literal["quota_resume"]
    evidence: str
    previous_model: str
    new_model: str
    alternatives_reason: str


@dataclass
class TaskRecord:
    version: int
    task_id: str
    attempt_id: str
    previous_attempt_ids: list[str]
    role: Role
    cwd: str
    model: str
    variant: str | None
    reason: str
    pricing: Pricing
    session: str | None
    server_identity: str | None
    client: ProcessIdentity | None
    supervisor: ProcessIdentity | None
    client_timeout_seconds: float | None
    execution_timeout_seconds: float | None
    execution: ExecutionObservation | None
    delivery: DeliveryObservation | None
    last_event_at: str | None
    cursor: str | None
    quota_resume: QuotaResume | None


class TaskReply(TypedDict):
    status: Literal["ok", "pending", "error"]
    task_id: str
    attempt_id: str
    session: str | None
    execution: ExecutionObservation | None
    delivery: DeliveryObservation | None
    capabilities: list[str]
    limitations: list[str]
    code: str | None


_SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,255}\Z")
_REPARSE_POINT = 0x400
_RECORD_KEYS = {
    "version",
    "task_id",
    "attempt_id",
    "previous_attempt_ids",
    "role",
    "cwd",
    "model",
    "variant",
    "reason",
    "pricing",
    "session",
    "server_identity",
    "client",
    "supervisor",
    "client_timeout_seconds",
    "execution_timeout_seconds",
    "execution",
    "delivery",
    "last_event_at",
    "cursor",
    "quota_resume",
}


def _invalid_record() -> StoreError:
    return StoreError("invalid_record", "El registro de tarea no es válido.")


def _canonical_uuid(value: object, code: str) -> str:
    if not isinstance(value, str):
        raise StoreError(code, "El identificador debe ser un UUID canónico.")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise StoreError(code, "El identificador debe ser un UUID canónico.") from exc
    if str(parsed) != value:
        raise StoreError(code, "El identificador debe ser un UUID canónico.")
    return value


def _validate_task_id(task_id: str) -> str:
    return _canonical_uuid(task_id, "invalid_task_id")


def _validate_session_id(session_id: str) -> str:
    if not isinstance(session_id, str) or _SESSION_ID.fullmatch(session_id) is None:
        raise StoreError(
            "invalid_session_id", "La sesión debe ser un identificador opaco simple."
        )
    return session_id


def _string(value: object, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise _invalid_record()
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise _invalid_record() from exc
    return value


def _timestamp(value: object, *, optional: bool = False) -> str | None:
    text = _string(value, optional=optional)
    if text is None:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        offset = parsed.utcoffset()
    except (ValueError, OverflowError) as exc:
        raise _invalid_record() from exc
    if parsed.tzinfo is None or offset is None:
        raise _invalid_record()
    return text


def _canonical_cwd(value: object) -> str:
    text = _string(value)
    assert text is not None
    try:
        path = Path(text)
        if not path.is_absolute() or os.path.normpath(text) != text:
            raise _invalid_record()
    except (OSError, ValueError) as exc:
        raise _invalid_record() from exc
    return text


def _timeout(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _invalid_record()
    try:
        number = float(value)
    except OverflowError as exc:
        raise _invalid_record() from exc
    if not math.isfinite(number) or number <= 0:
        raise _invalid_record()
    return number


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _invalid_record()
    return value


def _exact_keys(value: dict[str, Any], expected: set[str]) -> None:
    if set(value) != expected:
        raise _invalid_record()


def _process_identity_from_json(value: object) -> ProcessIdentity | None:
    if value is None:
        return None
    data = _object(value)
    _exact_keys(data, {"pid", "started_at"})
    pid = data["pid"]
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise _invalid_record()
    started_at = _timestamp(data["started_at"])
    assert started_at is not None
    return ProcessIdentity(pid=pid, started_at=started_at)


def _process_identity_to_json(value: ProcessIdentity | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {"pid": value.pid, "started_at": value.started_at}


def _execution_from_json(value: object) -> ExecutionObservation | None:
    if value is None:
        return None
    data = _object(value)
    _exact_keys(data, {"state", "source", "observed_at", "waiting_reason"})
    state = data["state"]
    if not isinstance(state, str) or state not in {
        "active",
        "waiting",
        "retrying",
        "idle",
        "unknown",
    }:
        raise _invalid_record()
    reason = data["waiting_reason"]
    if reason is not None and (
        not isinstance(reason, str) or reason not in {"permission", "input"}
    ):
        raise _invalid_record()
    if reason is not None and state != "waiting":
        raise _invalid_record()
    source = _string(data["source"])
    observed_at = _timestamp(data["observed_at"])
    assert source is not None
    assert observed_at is not None
    return ExecutionObservation(
        state=cast(ExecutionState, state),
        source=source,
        observed_at=observed_at,
        waiting_reason=cast(WaitingReason | None, reason),
    )


def _execution_to_json(value: ExecutionObservation | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "state": value.state,
        "source": value.source,
        "observed_at": value.observed_at,
        "waiting_reason": value.waiting_reason,
    }


def _delivery_from_json(value: object) -> DeliveryObservation | None:
    if value is None:
        return None
    data = _object(value)
    _exact_keys(data, {"state", "source", "observed_at"})
    state = data["state"]
    if not isinstance(state, str) or state not in {
        "pending",
        "partial",
        "completed",
        "failed",
        "interrupted",
    }:
        raise _invalid_record()
    source = _string(data["source"])
    observed_at = _timestamp(data["observed_at"])
    assert source is not None
    assert observed_at is not None
    return DeliveryObservation(
        state=cast(DeliveryState, state), source=source, observed_at=observed_at
    )


def _delivery_to_json(value: DeliveryObservation | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "state": value.state,
        "source": value.source,
        "observed_at": value.observed_at,
    }


def _quota_resume_from_json(value: object) -> QuotaResume | None:
    if value is None:
        return None
    data = _object(value)
    _exact_keys(
        data,
        {
            "scope",
            "evidence",
            "previous_model",
            "new_model",
            "alternatives_reason",
        },
    )
    if data["scope"] != "quota_resume":
        raise _invalid_record()
    evidence = _string(data["evidence"])
    previous_model = _string(data["previous_model"])
    new_model = _string(data["new_model"])
    alternatives_reason = _string(data["alternatives_reason"])
    assert evidence is not None
    assert previous_model is not None
    assert new_model is not None
    assert alternatives_reason is not None
    return QuotaResume(
        scope="quota_resume",
        evidence=evidence,
        previous_model=previous_model,
        new_model=new_model,
        alternatives_reason=alternatives_reason,
    )


def _quota_resume_to_json(value: QuotaResume | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "scope": value.scope,
        "evidence": value.evidence,
        "previous_model": value.previous_model,
        "new_model": value.new_model,
        "alternatives_reason": value.alternatives_reason,
    }


def _record_from_json(value: object) -> TaskRecord:
    data = _object(value)
    version = data.get("version")
    if isinstance(version, bool) or not isinstance(version, int):
        raise _invalid_record()
    if version != 1:
        raise StoreError(
            "unsupported_version", "La versión del registro no está soportada."
        )
    _exact_keys(data, _RECORD_KEYS)

    task_id = _canonical_uuid(data["task_id"], "invalid_record")
    attempt_id = _canonical_uuid(data["attempt_id"], "invalid_record")
    previous_value = data["previous_attempt_ids"]
    if not isinstance(previous_value, list):
        raise _invalid_record()
    previous_attempt_ids = [
        _canonical_uuid(item, "invalid_record") for item in previous_value
    ]
    if (
        len(set(previous_attempt_ids)) != len(previous_attempt_ids)
        or attempt_id in previous_attempt_ids
    ):
        raise _invalid_record()

    role = data["role"]
    if not isinstance(role, str) or role not in {"implementer", "reviewer"}:
        raise _invalid_record()
    pricing = data["pricing"]
    if not isinstance(pricing, str) or pricing not in {"free", "paid", "unknown"}:
        raise _invalid_record()
    model = _string(data["model"])
    variant = _string(data["variant"], optional=True)
    reason = _string(data["reason"])
    server_identity = _string(data["server_identity"], optional=True)
    cursor = _string(data["cursor"], optional=True)
    session_value = data["session"]
    if session_value is not None:
        try:
            _validate_session_id(session_value)
        except StoreError as exc:
            raise _invalid_record() from exc
    assert model is not None
    assert reason is not None
    return TaskRecord(
        version=version,
        task_id=task_id,
        attempt_id=attempt_id,
        previous_attempt_ids=previous_attempt_ids,
        role=cast(Role, role),
        cwd=_canonical_cwd(data["cwd"]),
        model=model,
        variant=variant,
        reason=reason,
        pricing=cast(Pricing, pricing),
        session=session_value,
        server_identity=server_identity,
        client=_process_identity_from_json(data["client"]),
        supervisor=_process_identity_from_json(data["supervisor"]),
        client_timeout_seconds=_timeout(data["client_timeout_seconds"]),
        execution_timeout_seconds=_timeout(data["execution_timeout_seconds"]),
        execution=_execution_from_json(data["execution"]),
        delivery=_delivery_from_json(data["delivery"]),
        last_event_at=_timestamp(data["last_event_at"], optional=True),
        cursor=cursor,
        quota_resume=_quota_resume_from_json(data["quota_resume"]),
    )


def _record_to_json(record: TaskRecord) -> dict[str, Any]:
    return {
        "version": record.version,
        "task_id": record.task_id,
        "attempt_id": record.attempt_id,
        "previous_attempt_ids": list(record.previous_attempt_ids),
        "role": record.role,
        "cwd": record.cwd,
        "model": record.model,
        "variant": record.variant,
        "reason": record.reason,
        "pricing": record.pricing,
        "session": record.session,
        "server_identity": record.server_identity,
        "client": _process_identity_to_json(record.client),
        "supervisor": _process_identity_to_json(record.supervisor),
        "client_timeout_seconds": record.client_timeout_seconds,
        "execution_timeout_seconds": record.execution_timeout_seconds,
        "execution": _execution_to_json(record.execution),
        "delivery": _delivery_to_json(record.delivery),
        "last_event_at": record.last_event_at,
        "cursor": record.cursor,
        "quota_resume": _quota_resume_to_json(record.quota_resume),
    }


def _validate_record(record: TaskRecord) -> None:
    if not isinstance(record, TaskRecord):
        raise _invalid_record()
    _record_from_json(_record_to_json(record))


def _is_reparse(info: os.stat_result) -> bool:
    attributes = getattr(info, "st_file_attributes", 0)
    return bool(attributes & _REPARSE_POINT)


def _root_path(root: Path) -> Path:
    path = root.absolute()
    try:
        info = path.lstat()
    except OSError as exc:
        raise StoreError("invalid_root", "La raíz del proyecto no es válida.") from exc
    if path.is_symlink() or _is_reparse(info) or not stat.S_ISDIR(info.st_mode):
        raise StoreError("invalid_root", "La raíz del proyecto no es válida.")
    return path


def _require_directory(path: Path) -> None:
    try:
        info = path.lstat()
    except OSError as exc:
        raise StoreError("unsafe_path", "La ruta del almacén no es segura.") from exc
    if path.is_symlink() or _is_reparse(info) or not stat.S_ISDIR(info.st_mode):
        raise StoreError("unsafe_path", "La ruta del almacén no es segura.")


def _require_regular_file(path: Path) -> None:
    try:
        info = path.lstat()
    except OSError as exc:
        raise StoreError("unsafe_path", "El archivo del almacén no es seguro.") from exc
    if path.is_symlink() or _is_reparse(info) or not stat.S_ISREG(info.st_mode):
        raise StoreError("unsafe_path", "El archivo del almacén no es seguro.")


def _managed_directory(root: Path, parts: tuple[str, ...], create: bool) -> Path:
    path = _root_path(root)
    for part in parts:
        path = path / part
        try:
            _require_directory(path)
        except StoreError as error:
            if not isinstance(error.__cause__, FileNotFoundError):
                raise
            if not create:
                raise StoreError(
                    "record_not_found", "La tarea no está registrada."
                ) from error
        else:
            continue
        try:
            path.mkdir(mode=0o700)
        except FileExistsError:
            pass
        except OSError as exc:
            raise StoreError(
                "store_io", "No se pudo crear el directorio local."
            ) from exc
        _require_directory(path)
    return path


def _task_directory(root: Path, task_id: str, create: bool) -> Path:
    return _managed_directory(root, (".aikit", "sessions", task_id), create)


def _record_path(root: Path, task_id: str) -> Path:
    return _task_directory(root, task_id, create=False) / "record.json"


def _without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _atomic_replace(source: Path, destination: Path) -> None:
    """Publica un snapshot sin retirar transitoriamente el nombre anterior.

    Win32 FileRenameInfoEx con POSIX semantics mantiene handles existentes y
    publica el nombre nuevo en una operacion. ReplaceFileW tiene un hueco de
    nombre observable por lectores. No se reintenta ni ignora ningun error.
    """
    if source.parent != destination.parent:
        raise OSError("El reemplazo debe pertenecer al mismo directorio.")
    _require_regular_file(source)
    if destination.exists() or destination.is_symlink():
        _require_regular_file(destination)
    if sys.platform != "win32":
        os.replace(source, destination)
        return
    import ctypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    security = ctypes.WinDLL("advapi32", use_last_error=True)
    # Conservar DACL/proteccion del destino antes de publicar el temporal.
    # El temporal sigue en el mismo directorio validado y solo pertenece a este intento.
    if destination.exists():
        security.GetFileSecurityW.argtypes = [
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        security.GetFileSecurityW.restype = ctypes.c_int
        security.SetFileSecurityW.argtypes = [
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        security.SetFileSecurityW.restype = ctypes.c_int
        security.GetSecurityDescriptorControl.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ushort),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        security.GetSecurityDescriptorControl.restype = ctypes.c_int
        size = ctypes.c_uint32()
        security.GetFileSecurityW(str(destination), 4, None, 0, ctypes.byref(size))
        if not 0 < size.value <= 128 * 1024:
            raise ctypes.WinError(ctypes.get_last_error())
        descriptor = ctypes.create_string_buffer(size.value)
        if not security.GetFileSecurityW(
            str(destination), 4, descriptor, size.value, ctypes.byref(size)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        control, revision = ctypes.c_ushort(), ctypes.c_uint32()
        if not security.GetSecurityDescriptorControl(
            descriptor, ctypes.byref(control), ctypes.byref(revision)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        protection = 0x80000000 if control.value & 0x1000 else 0x20000000
        if not security.SetFileSecurityW(str(source), 4 | protection, descriptor):
            raise ctypes.WinError(ctypes.get_last_error())

    class RenameInfo(ctypes.Structure):
        _fields_ = [
            ("flags", ctypes.c_uint32),
            ("root", ctypes.c_void_p),
            ("length", ctypes.c_uint32),
            ("name", ctypes.c_wchar * 1),
        ]

    target = str(destination).encode("utf-16-le")
    buffer = ctypes.create_string_buffer(RenameInfo.name.offset + len(target) + 2)
    info = ctypes.cast(buffer, ctypes.POINTER(RenameInfo)).contents
    info.flags = 3  # REPLACE_IF_EXISTS | POSIX_SEMANTICS; no IGNORE_READONLY.
    info.root = None
    info.length = len(target)
    ctypes.memmove(
        ctypes.addressof(buffer) + RenameInfo.name.offset, target, len(target)
    )
    kernel.CreateFileW.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    ]
    kernel.CreateFileW.restype = ctypes.c_void_p
    kernel.SetFileInformationByHandle.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_uint32,
    ]
    kernel.SetFileInformationByHandle.restype = ctypes.c_int
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle.restype = ctypes.c_int
    # DELETE access on the own temporary; share READ|WRITE|DELETE, OPEN_EXISTING.
    handle = kernel.CreateFileW(str(source), 0x10000, 7, None, 3, 0x00200000, None)
    if handle is None or handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        if not kernel.SetFileInformationByHandle(handle, 22, buffer, len(buffer)):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(handle)


def _open_shared_read(path: Path) -> BinaryIO:
    """Lector de snapshot: permite replace atomico mientras el handle sigue vivo.

    En Windows fopen no concede FILE_SHARE_DELETE. Un lector de estado no debe
    hacer fallar la escritura del supervisor; el handle conserva sus bytes viejos.
    No omite validacion de rutas ni ACL del llamador.
    """
    _require_regular_file(path)
    if sys.platform != "win32":
        return path.open("rb")
    import ctypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    ]
    kernel.CreateFileW.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.CloseHandle.restype = ctypes.c_int
    # GENERIC_READ; SHARE_READ|WRITE|DELETE; OPEN_EXISTING; OPEN_REPARSE_POINT.
    handle = kernel.CreateFileW(str(path), 0x80000000, 7, None, 3, 0x00200000, None)
    if handle is None or handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except BaseException:
        kernel.CloseHandle(handle)
        raise
    try:
        return os.fdopen(descriptor, "rb")
    except BaseException:
        os.close(descriptor)
        raise


def load_task(root: Path, task_id: str) -> TaskRecord:
    """Carga una tarea sin modificar registros ausentes, corruptos o futuros."""

    _validate_task_id(task_id)
    path = _record_path(root, task_id)
    try:
        _require_regular_file(path)
    except StoreError as error:
        if isinstance(error.__cause__, FileNotFoundError):
            raise StoreError(
                "record_not_found", "La tarea no está registrada."
            ) from error
        raise
    try:
        with _open_shared_read(path) as stream:
            text = stream.read().decode("utf-8")
        data = json.loads(text, object_pairs_hook=_without_duplicate_keys)
    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        ValueError,
        RecursionError,
    ) as exc:
        raise StoreError("record_corrupt", "El registro local está corrupto.") from exc
    except OSError as exc:
        raise StoreError("store_io", "No se pudo leer el registro local.") from exc
    record = _record_from_json(data)
    if record.task_id != task_id:
        raise StoreError(
            "task_id_mismatch", "La identidad del registro no coincide con su ruta."
        )
    return record


def save_task(root: Path, record: TaskRecord) -> None:
    """Guarda metadatos validados mediante reemplazo atómico en el mismo directorio."""

    _validate_record(record)
    _validate_task_id(record.task_id)
    directory = _task_directory(root, record.task_id, create=True)
    path = directory / "record.json"
    if path.exists() or path.is_symlink():
        _require_regular_file(path)
        load_task(root, record.task_id)

    descriptor = -1
    temporary: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".record-", suffix=".tmp", dir=directory
        )
        temporary = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            descriptor = -1
            json.dump(
                _record_to_json(record),
                stream,
                ensure_ascii=False,
                allow_nan=False,
                indent=2,
                sort_keys=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        _atomic_replace(temporary, path)
        temporary = None
    except OSError as exc:
        raise StoreError("store_io", "No se pudo guardar el registro local.") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass


def _acquire(descriptor: int) -> None:
    try:
        if sys.platform == "win32":
            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        raise StoreError(
            "lock_contended", "Ya existe una mutación coordinada para este recurso."
        ) from exc


def _release(descriptor: int) -> None:
    if sys.platform == "win32":
        os.lseek(descriptor, 0, os.SEEK_SET)
        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(descriptor, fcntl.LOCK_UN)


@contextmanager
def _lock_file(path: Path) -> Iterator[None]:
    if path.exists() or path.is_symlink():
        _require_regular_file(path)
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as exc:
        raise StoreError("store_io", "No se pudo abrir el bloqueo local.") from exc
    acquired = False
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise StoreError("unsafe_path", "El archivo de bloqueo no es regular.")
        _require_regular_file(path)
        os.lseek(descriptor, 0, os.SEEK_SET)
        if info.st_size == 0:
            os.write(descriptor, b"\0")
        os.lseek(descriptor, 0, os.SEEK_SET)
        _acquire(descriptor)
        acquired = True
        yield
    finally:
        try:
            if acquired:
                _release(descriptor)
        finally:
            os.close(descriptor)


@contextmanager
def lock_task(root: Path, task_id: str) -> Iterator[None]:
    """Serializa mutaciones locales de una tarea sin esperas indefinidas."""

    _validate_task_id(task_id)
    directory = _task_directory(root, task_id, create=True)
    with _lock_file(directory / "task.lock"):
        yield


@contextmanager
def lock_session(root: Path, session_id: str) -> Iterator[None]:
    """Serializa mutaciones locales asociadas a una sesión OpenCode conocida."""

    _validate_session_id(session_id)
    directory = _managed_directory(root, (".aikit", "session-locks"), create=True)
    with _lock_file(directory / (session_id + ".lock")):
        yield
