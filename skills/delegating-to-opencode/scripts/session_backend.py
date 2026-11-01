"""Observación conservadora y control solo mediante un binding de código confiable.

No crea conexiones, servidores o credenciales. El transporte futuro debe estar
autenticado, ligado a un propietario y respetar cada timeout recibido. El registro
persistido identifica la expectativa: nunca proporciona una URL ni autoridad.
"""

from __future__ import annotations

import math
import os
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Literal, Protocol

from session_store import (
    DeliveryObservation,
    ExecutionObservation,
    StoreError,
    TaskRecord,
    _validate_session_id,
)

DOCUMENTED_OPERATIONS = (
    "server.info",
    "session.get",
    "session.active",
    "session.inbox.list",
    "session.permission.list",
    "session.log",
    "session.interrupt",
    "session.switchModel",
)
_OPAQUE = re.compile(r"[A-Za-z0-9_.-]{1,128}\Z")


@dataclass(frozen=True)
class OwnerIdentity:
    """El nacimiento debe proceder de una comprobación real del SO del binding."""

    identity: str
    pid: int
    started_at: str | None
    version: str


@dataclass(frozen=True)
class TerminalReconciliation:
    accepted: bool
    outcome: Literal["completed", "partial", "failed", "uncertain", "pending"]
    finish: str | None
    completed_at: int | float | None
    assistant_message_id: str | None
    reason: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ApiResponse:
    status: int
    body: object


class TrustedBinding(Protocol):
    """Autoridad aportada desde código; no deserializarla ni fabricar su prueba.

    verify_owner comprueba el proceso real antes de cada petición, incluyendo su
    nacimiento. request usa exclusivamente el canal ya ligado/autenticado y no
    descubre ni inicia servicios. Ambos métodos deben respetar timeout total.
    Esta interfaz no certifica por sí sola una implementación del transporte.
    """

    @property
    def expected_owner(self) -> OwnerIdentity: ...

    @property
    def operations(self) -> frozenset[str]: ...

    def verify_owner(self, *, timeout: float) -> OwnerIdentity | None: ...

    def request(
        self,
        operation: str,
        *,
        session_id: str | None = None,
        message_id: str | None = None,
        timeout: float = 10.0,
        resume: bool | None = None,
    ) -> ApiResponse: ...


@dataclass(frozen=True)
class BackendCapabilities:
    observation: bool = False
    control: bool = False
    model_change: bool = False
    quota_resume: bool = False
    logs: bool = False
    documented_operations: tuple[str, ...] = DOCUMENTED_OPERATIONS


@dataclass
class SessionInspection:
    exists: bool | None
    cwd_matches: bool | None
    execution: ExecutionObservation
    local_execution: ExecutionObservation | None
    local_delivery: DeliveryObservation | None
    cursor: str | None
    owner: OwnerIdentity | None = None
    capabilities: BackendCapabilities = field(default_factory=BackendCapabilities)
    pending_count: int | None = None
    permission_count: int | None = None
    log_evidence: tuple[str, ...] = ()
    limitations: list[str] = field(default_factory=list)
    code: str | None = None


@dataclass
class InterruptOutcome:
    requested: bool = False
    acknowledged: bool | None = None
    confirmed: bool | None = None
    owner: OwnerIdentity | None = None
    capabilities: BackendCapabilities = field(default_factory=BackendCapabilities)
    limitations: list[str] = field(default_factory=list)
    code: str | None = None


class _Unavailable(Exception):
    def __init__(self, code: str) -> None:
        self.code = code


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _unknown() -> ExecutionObservation:
    return ExecutionObservation("unknown", "owner_not_observed", _now())


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
        raise _Unavailable("invalid_response")
    return value


def _text(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > 32768 or "\0" in value:
        raise _Unavailable("invalid_response")
    return value


def _number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise _Unavailable("invalid_response")
    try:
        converted = float(value)
    except OverflowError:
        raise _Unavailable("invalid_response") from None
    if not math.isfinite(converted) or converted < 0:
        raise _Unavailable("invalid_response")
    return converted


def _birth_known(owner: OwnerIdentity) -> bool:
    if type(owner.pid) is not int or owner.pid <= 0 or owner.started_at is None:
        return False
    try:
        parsed = datetime.fromisoformat(owner.started_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.utcoffset() is not None


class _Context:
    def __init__(
        self,
        record: TaskRecord,
        binding: TrustedBinding | None,
        clock: Callable[[], float],
    ) -> None:
        self.record = record
        self.session_id = record.session
        self.cwd = record.cwd
        self.interrupt_requested = False
        self.clock = clock
        self.end = clock() + 10.0
        if binding is None or record.server_identity is None:
            raise _Unavailable("control_unavailable")
        if not _OPAQUE.fullmatch(record.server_identity):
            raise _Unavailable("control_unavailable")
        self.binding = binding
        self.expected = binding.expected_owner
        if record.server_identity != self.expected.identity:
            raise _Unavailable("owner_mismatch")
        if not _birth_known(self.expected):
            raise _Unavailable("owner_unverified")
        if self.expected.version != "2.2.0":
            raise _Unavailable("unsupported_version")
        if record.session is None:
            raise _Unavailable("session_unknown")
        try:
            _validate_session_id(record.session)
        except StoreError:
            raise _Unavailable("session_unknown") from None

    def remaining(self) -> float:
        remaining = self.end - self.clock()
        if remaining <= 0:
            raise _Unavailable("backend_timeout")
        return remaining

    def unchanged_target(self) -> None:
        if self.record.server_identity != self.expected.identity:
            raise _Unavailable("owner_mismatch")
        if self.record.session != self.session_id or self.record.cwd != self.cwd:
            raise _Unavailable("record_changed")

    def request(self, operation: str, *, resume: bool | None = None) -> ApiResponse:
        self.unchanged_target()
        if operation not in self.binding.operations:
            raise _Unavailable("operation_unavailable")
        try:
            owner = self.binding.verify_owner(timeout=self.remaining())
            self.remaining()
            if owner is None or not _birth_known(owner):
                raise _Unavailable("owner_unverified")
            if owner != self.expected:
                raise _Unavailable("owner_mismatch")
            self.unchanged_target()
            timeout = self.remaining()
            if operation == "session.interrupt":
                self.interrupt_requested = True
            response = self.binding.request(
                operation,
                session_id=None
                if operation in {"server.info", "session.active"}
                else self.session_id,
                timeout=timeout,
                resume=resume,
            )
            self.remaining()
            self.unchanged_target()
        except TimeoutError:
            raise _Unavailable("backend_timeout") from None
        except _Unavailable:
            raise
        except Exception:
            raise _Unavailable("backend_unavailable") from None
        if type(response.status) is not int:
            raise _Unavailable("invalid_response")
        if response.status == 404 and operation == "session.get":
            body = _object(response.body)
            if (
                body.get("_tag") != "SessionNotFoundError"
                or body.get("sessionID") != self.session_id
            ):
                raise _Unavailable("invalid_response")
            raise _Unavailable("session_not_found")
        if response.status != 200:
            raise _Unavailable("backend_unavailable")
        return response

    def info(self) -> None:
        body = _object(self.request("server.info").body)
        pid = body.get("pid")
        if type(pid) is not int or pid < 0 or not isinstance(body.get("version"), str):
            raise _Unavailable("invalid_response")
        urls = body.get("urls")
        if not isinstance(urls, list) or not all(isinstance(url, str) for url in urls):
            raise _Unavailable("invalid_response")
        _text(_object(body.get("paths")).get("tmp"))
        if pid != self.expected.pid or body["version"] != self.expected.version:
            raise _Unavailable("owner_mismatch")

    def session(self) -> bool:
        envelope = _object(self.request("session.get").body)
        body = _object(envelope.get("data"))
        if body.get("id") != self.session_id:
            raise _Unavailable("invalid_response")
        _text(body.get("projectID"))
        _number(body.get("cost"))
        _object(body.get("tokens"))
        timestamps = _object(body.get("time"))
        _number(timestamps.get("created"))
        _number(timestamps.get("updated"))
        directory = _text(_object(body.get("location")).get("directory"))
        if not os.path.isabs(directory):
            raise _Unavailable("invalid_response")
        return os.path.normcase(os.path.normpath(directory)) == os.path.normcase(
            os.path.normpath(self.cwd)
        )

    def active(self) -> bool:
        body = _object(_object(self.request("session.active").body).get("data"))
        for session_id, status in body.items():
            if not session_id.startswith("ses") or _object(status) != {
                "type": "running"
            }:
                raise _Unavailable("invalid_response")
        return self.session_id in body

    def count(self, operation: str) -> list[dict[str, Any]]:
        value = _object(self.request(operation).body).get("data")
        if not isinstance(value, list):
            raise _Unavailable("invalid_response")
        return [_object(item) for item in value]

    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            observation={"server.info", "session.get", "session.active"}.issubset(
                self.binding.operations
            ),
            control="session.interrupt" in self.binding.operations,
        )


def inspect_session(
    record: TaskRecord,
    *,
    binding: TrustedBinding | None = None,
    _clock: Callable[[], float] = time.monotonic,
) -> SessionInspection:
    """Historia local separada de una muestra actual del propietario comprobado."""
    result = SessionInspection(
        exists=None,
        cwd_matches=None,
        execution=_unknown(),
        local_execution=replace(record.execution) if record.execution else None,
        local_delivery=replace(record.delivery) if record.delivery else None,
        cursor=record.cursor,
        limitations=[
            "local_observations_historical",
            "logs_unavailable",
            "quota_resume_unavailable",
        ],
    )
    try:
        context = _Context(record, binding, _clock)
        context.info()
        result.owner = context.expected
        result.cwd_matches = context.session()
        result.exists = True
        if not result.cwd_matches:
            raise _Unavailable("cwd_mismatch")
        running = context.active()
        result.execution = ExecutionObservation(
            "active" if running else "idle", "verified_owner_api", _now()
        )
        result.capabilities = context.capabilities()
        result.limitations.append("activity_process_local_snapshot")
        if "session.inbox.list" in context.binding.operations:
            inbox = context.count("session.inbox.list")
            # No se inspecciona payload. Sin estado de entrega acreditado no
            # convertir la lista en mensajes visibles por el modelo ni espera.
            if not inbox:
                result.pending_count = 0
            else:
                result.limitations.append("pending_metadata_unavailable")
        else:
            result.limitations.append("pending_metadata_unavailable")
        if "session.permission.list" in context.binding.operations:
            result.permission_count = len(context.count("session.permission.list"))
        else:
            result.limitations.append("permission_metadata_unavailable")
    except _Unavailable as error:
        result.code = error.code
        result.limitations.append(error.code)
        if error.code == "session_not_found":
            result.exists = False
        if error.code in {
            "owner_mismatch",
            "owner_unverified",
            "backend_timeout",
            "record_changed",
        }:
            result.execution = _unknown()
            result.owner = None
            result.capabilities = BackendCapabilities()
    return result


def interrupt_session(
    record: TaskRecord,
    *,
    binding: TrustedBinding | None = None,
    _clock: Callable[[], float] = time.monotonic,
    _sleep: Callable[[float], None] = time.sleep,
) -> InterruptOutcome:
    """ACK y dos muestras de cierre; no fencing ni garantía de inactividad futura."""
    result = InterruptOutcome(limitations=["quota_resume_unavailable"])
    context: _Context | None = None
    try:
        context = _Context(record, binding, _clock)
        context.info()
        result.owner = context.expected
        if not context.session():
            raise _Unavailable("cwd_mismatch")
        if not context.active():
            raise _Unavailable("owner_idle")
        if "session.interrupt" not in context.binding.operations:
            raise _Unavailable("operation_unavailable")
        # requested cubre también el envío incierto: nunca habilita reintento.
        body = _object(context.request("session.interrupt", resume=False).body)
        if set(body) != {"interrupted"} or type(body["interrupted"]) is not bool:
            raise _Unavailable("invalid_response")
        result.acknowledged = body["interrupted"]
        result.capabilities = context.capabilities()
        if not result.acknowledged:
            raise _Unavailable("interrupt_unacknowledged")
        idle_seen = False
        while True:
            running = context.active()
            if running and idle_seen:
                raise _Unavailable("successor_activity")
            if not running:
                if idle_seen:
                    result.confirmed = True
                    result.limitations.append(
                        "settlement_process_local_snapshot_not_fencing"
                    )
                    return result
                idle_seen = True
            _sleep(min(0.05, context.remaining()))
    except _Unavailable as error:
        result.code = error.code
        result.limitations.append(error.code)
        if error.code in {"owner_mismatch", "owner_unverified", "record_changed"}:
            result.owner = None
            result.capabilities = BackendCapabilities()
        return result
    finally:
        if context is not None:
            result.requested = context.interrupt_requested


def worker_interrupt(record: TaskRecord) -> bool | None:
    """Sin fábrica de bindings de producción, el worker no tiene control real."""
    return interrupt_session(record).confirmed


def reconcile_terminal_message(
    record: TaskRecord,
    binding: TrustedBinding,
    *,
    assistant_message_id: str | None,
    prompt_message_id: str | None = None,
    timeout: float,
    _clock: Callable[[], float] = time.monotonic,
) -> TerminalReconciliation:
    """Reconcilia por una lectura read-only del mensaje durable.

    Conservador: solo acredita ``finish=stop`` sin error, con identidades válidas
    y marca temporal numérica finita. No muta ``record`` ni persiste.
    """

    if not isinstance(assistant_message_id, str) or not assistant_message_id:
        return TerminalReconciliation(
            False,
            "uncertain",
            None,
            None,
            None,
            "assistant_message_id_unavailable",
            ("assistant_message_id_unavailable",),
        )

    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        return TerminalReconciliation(
            False,
            "pending",
            None,
            None,
            assistant_message_id,
            "budget_exhausted",
            ("budget_exhausted",),
        )

    session_id = getattr(record, "session", None)
    cwd = getattr(record, "cwd", None)
    server_identity = getattr(record, "server_identity", None)
    if not isinstance(session_id, str) or not session_id:
        return TerminalReconciliation(
            False,
            "pending",
            None,
            None,
            assistant_message_id,
            "session_unknown",
            ("session_unknown",),
        )
    try:
        _validate_session_id(session_id)
    except StoreError:
        return TerminalReconciliation(
            False,
            "pending",
            None,
            None,
            assistant_message_id,
            "session_unknown",
            ("session_unknown",),
        )
    if not isinstance(cwd, str) or not cwd:
        return TerminalReconciliation(
            False,
            "pending",
            None,
            None,
            assistant_message_id,
            "record_changed",
            ("record_changed",),
        )

    expected_owner = getattr(binding, "expected_owner", None)
    operations: frozenset[str] = getattr(binding, "operations", frozenset())
    verify_owner = getattr(binding, "verify_owner", None)
    request = getattr(binding, "request", None)
    if (
        expected_owner is None
        or not callable(verify_owner)
        or not callable(request)
        or not _birth_known(expected_owner)
        or getattr(expected_owner, "version", None) != "2.2.0"
    ):
        return TerminalReconciliation(
            False,
            "pending",
            None,
            None,
            assistant_message_id,
            "backend_unavailable",
            ("backend_unavailable",),
        )
    if not isinstance(server_identity, str) or server_identity != getattr(
        expected_owner, "identity", None
    ):
        return TerminalReconciliation(
            False,
            "pending",
            None,
            None,
            assistant_message_id,
            "owner_mismatch",
            ("owner_mismatch",),
        )

    delivery = getattr(record, "delivery", None)
    prior_state = getattr(delivery, "state", None)
    if prior_state in {"failed", "interrupted"}:
        return TerminalReconciliation(
            False,
            "failed" if prior_state == "failed" else "uncertain",
            None,
            None,
            assistant_message_id,
            "prior_delivery_not_success",
            ("prior_delivery_not_success",),
        )

    deadline = _clock() + timeout

    def remaining() -> float:
        value = deadline - _clock()
        if value <= 0:
            raise _Unavailable("backend_timeout")
        return value

    def failure(
        reason: str,
        outcome: Literal["completed", "partial", "failed", "uncertain", "pending"],
        *,
        finish: str | None = None,
        completed_at: int | float | None = None,
        limitations: tuple[str, ...] | None = None,
    ) -> TerminalReconciliation:
        return TerminalReconciliation(
            False,
            outcome,
            finish,
            completed_at,
            assistant_message_id,
            reason,
            limitations if limitations is not None else (reason,),
        )

    try:
        owner = verify_owner(timeout=min(remaining(), 1.0))
        remaining()
        if owner is None or not _birth_known(owner) or owner != expected_owner:
            return failure(
                "owner_mismatch"
                if owner is not None and owner != expected_owner
                else "owner_unverified",
                "pending",
            )
        if (
            getattr(record, "server_identity", None) != server_identity
            or getattr(record, "session", None) != session_id
            or getattr(record, "cwd", None) != cwd
        ):
            return failure("record_changed", "pending")
        if "session.message.get" not in operations:
            return failure("operation_unavailable", "pending")
        response = request(
            "session.message.get",
            session_id=session_id,
            message_id=assistant_message_id,
            timeout=remaining(),
        )
        remaining()
        owner_after = verify_owner(timeout=min(remaining(), 0.5))
        remaining()
        if (
            owner_after is None
            or not _birth_known(owner_after)
            or owner_after != expected_owner
        ):
            return failure("owner_mismatch", "pending")
        if (
            getattr(record, "server_identity", None) != server_identity
            or getattr(record, "session", None) != session_id
            or getattr(record, "cwd", None) != cwd
        ):
            return failure("record_changed", "pending")
    except _Unavailable as error:
        return failure(error.code, "pending")
    except TimeoutError:
        return failure("backend_timeout", "pending")
    except Exception as error:  # noqa: BLE001
        code = getattr(error, "code", None)
        if not isinstance(code, str) or not code:
            code = "backend_unavailable"
        if code == "timeout":
            code = "backend_timeout"
        return failure(code, "pending")

    status = getattr(response, "status", None)
    body = getattr(response, "body", response)
    if type(status) is not int:
        return failure("invalid_response", "uncertain")
    if status != 200:
        return failure("backend_unavailable", "pending")

    if not isinstance(body, dict):
        return failure("invalid_response", "uncertain")
    message = body
    if isinstance(body.get("data"), dict):
        message = body["data"]
    if not isinstance(message, dict):
        return failure("invalid_response", "uncertain")

    info = message
    if isinstance(message.get("info"), dict):
        info = message["info"]
    if not isinstance(info, dict):
        return failure("invalid_response", "uncertain")

    candidate_ids: list[str] = []
    for obj in (message, info):
        value = obj.get("id")
        if isinstance(value, str):
            candidate_ids.append(value)
    if not candidate_ids or any(
        value != assistant_message_id for value in candidate_ids
    ):
        return failure("assistant_message_id_mismatch", "uncertain")

    session_candidates: list[str] = []
    for obj in (message, info):
        for key in ("sessionID", "sessionId", "session"):
            value = obj.get(key)
            if isinstance(value, str):
                session_candidates.append(value)
    if session_candidates and any(value != session_id for value in session_candidates):
        return failure("session_mismatch", "uncertain")

    if info.get("type") != "assistant":
        return failure("invalid_role", "uncertain")

    if info.get("error") is not None:
        return failure("message_error", "failed")

    finish = info.get("finish")
    if not isinstance(finish, str) or not finish:
        return failure("missing_finish", "uncertain")

    completed_at: int | float | None = None
    time_value = info.get("time")
    if isinstance(time_value, dict):
        completed_at = time_value.get("completed")
    if completed_at is None:
        for key in ("completed_at", "completedAt"):
            if key in info:
                completed_at = info.get(key)
                break
    if completed_at is None:
        return failure("missing_completed_at", "uncertain")
    if (
        isinstance(completed_at, bool)
        or not isinstance(completed_at, (int, float))
        or not math.isfinite(completed_at)
    ):
        return failure("invalid_completed_at", "uncertain")

    parent_id: object = None
    parent_found = False
    for obj in (message, info):
        for key in ("parentID", "parent_id", "parentMessageID", "parent_message_id"):
            if key in obj:
                parent_id = obj.get(key)
                parent_found = True
                break
        if parent_found:
            break
    if not parent_found and isinstance(info.get("metadata"), dict):
        metadata = info["metadata"]
        for key in ("parentID", "parent_id", "parentMessageID", "parent_message_id"):
            if key in metadata:
                parent_id = metadata.get(key)
                parent_found = True
                break

    limitations_list: list[str] = []
    if prompt_message_id is not None and not parent_found:
        limitations_list.append("parent_id_unavailable")
    if prompt_message_id is not None and parent_id is None:
        limitations_list.append("parent_id_null_not_correlated")

    if prompt_message_id is not None and parent_id is not None:
        if parent_id != prompt_message_id:
            return failure("parent_message_mismatch", "uncertain")

    if finish == "stop":
        return TerminalReconciliation(
            True,
            "completed",
            finish,
            completed_at,
            assistant_message_id,
            "accepted",
            tuple(limitations_list),
        )
    if finish == "length":
        return TerminalReconciliation(
            False,
            "partial",
            finish,
            completed_at,
            assistant_message_id,
            "finish_length",
            tuple(limitations_list) or ("finish_length",),
        )
    if finish in {"error", "content-filter", "interrupted", "cancel"}:
        return TerminalReconciliation(
            False,
            "failed",
            finish,
            completed_at,
            assistant_message_id,
            f"finish_{finish}",
            tuple(limitations_list) or (f"finish_{finish}",),
        )
    if finish in {"tool-calls", "unknown"}:
        return TerminalReconciliation(
            False,
            "uncertain",
            finish,
            completed_at,
            assistant_message_id,
            "non_final_finish",
            tuple(limitations_list) or ("non_final_finish",),
        )
    return TerminalReconciliation(
        False,
        "uncertain",
        finish,
        completed_at,
        assistant_message_id,
        "unknown_finish",
        tuple(limitations_list) or ("unknown_finish",),
    )
