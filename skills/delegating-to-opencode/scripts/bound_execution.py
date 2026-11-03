"""Ejecución ligada al servicio existente, sin descubrimiento ni autoarranque.

El preflight lo realiza `delegate._prepare_run`; este módulo reserva el intento,
vuelve a comprobar binding y procedencia, delega el envío al supervisor y
recupera el resultado local sin repetir inferencia.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import delegate
from host_registry import HostRegistryError, reserve_host_attempt, verify_provenance
from service_connection import BoundLaunch
from service_identity import HostContext, ServiceError
from session_store import (
    DeliveryObservation,
    ExecutionObservation,
    StoreError,
    TaskRecord,
    _managed_directory,
    _require_regular_file,
    _validate_record,
    _without_duplicate_keys,
    load_task,
)
from session_store import (
    save_task as save_task,
)

MAX_RESULT_BYTES = 1024 * 1024
POLL_SECONDS = 0.02


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _attempt_directory(record: TaskRecord) -> Path:
    return Path(record.cwd) / ".aikit" / "sessions" / record.task_id / record.attempt_id


def _new_record(prepared: BoundLaunch, *, task_id: str, attempt_id: str) -> TaskRecord:
    observed_at = _now()
    return TaskRecord(
        version=1,
        task_id=task_id,
        attempt_id=attempt_id,
        previous_attempt_ids=[],
        role=prepared.role,
        cwd=os.path.normpath(str(prepared.project)),
        model=prepared.model,
        variant=prepared.variant,
        reason=prepared.reason,
        pricing=prepared.pricing,
        session=None,
        server_identity=prepared.binding.token,
        client=None,
        supervisor=None,
        client_timeout_seconds=prepared.timeout,
        execution_timeout_seconds=prepared.timeout,
        execution=ExecutionObservation("unknown", "launch_reserved", observed_at),
        delivery=DeliveryObservation("pending", "launch_reserved", observed_at),
        last_event_at=None,
        cursor=None,
        quota_resume=None,
    )


def _tracking(record: TaskRecord) -> dict[str, Any]:
    return {
        "task_id": record.task_id,
        "attempt_id": record.attempt_id,
    }


def _tracked_error(
    code: str, message: str, record: TaskRecord, **extra: Any
) -> dict[str, Any]:
    return {**delegate._error(code, message), **_tracking(record), **extra}


def _pending(
    record: TaskRecord,
    *,
    agent: str,
    limitations: list[str],
    summary: str = "",
    session: str | None = None,
    delivery: str = "pending",
    execution: str = "unknown",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": "pending",
        **_tracking(record),
        "session": session if session is not None else record.session,
        "model": record.model,
        "variant": record.variant,
        "effort": record.variant or "provider_default",
        "reason": record.reason,
        "agent": agent,
        "delivery": delivery,
        "execution": execution,
        "limitations": list(limitations),
        "uncertain": True,
    }
    if summary:
        payload["summary"] = delegate._cap(summary)
    return payload


def _result_path(record: TaskRecord) -> Path:
    return _attempt_directory(record) / "result.json"


def _read_artifact(record: TaskRecord, name: str) -> bytes | None:
    try:
        _validate_record(record)
        directory = _managed_directory(
            Path(record.cwd),
            (".aikit", "sessions", record.task_id, record.attempt_id),
            create=False,
        )
        path = directory / name
        _require_regular_file(path)
        with path.open("rb") as stream:
            raw = stream.read(MAX_RESULT_BYTES + 1)
        return raw if len(raw) <= MAX_RESULT_BYTES else None
    except (StoreError, OSError, ValueError):
        return None


def _read_result_snapshot(
    record: TaskRecord,
) -> tuple[bytes, dict[str, Any]] | None:
    raw = _read_artifact(record, "result.json")
    if raw is None:
        return None
    try:
        data = json.loads(raw, object_pairs_hook=_without_duplicate_keys)
    except (UnicodeError, ValueError, RecursionError):
        return None
    return (raw, data) if isinstance(data, dict) else None


def _read_result(record: TaskRecord) -> dict[str, Any] | None:
    snapshot = _read_result_snapshot(record)
    return snapshot[1] if snapshot is not None else None


def _reconciliation_matches_result(record: TaskRecord, result_bytes: bytes) -> bool:
    observation = record.reconciliation
    if observation is None:
        # Legacy records retain only their existing delivery/provenance gates.
        return True
    return bool(
        observation.attempt_id == record.attempt_id
        and observation.session_id == record.session
        and observation.assistant_message_id
        and observation.generation >= 1
        and observation.phase == "response_observed"
        and observation.identity == "verified"
        and observation.lifecycle == "committed"
        and observation.source == "durable_message"
        and observation.accepted is True
        and observation.outcome == "completed"
        and observation.reason == "accepted"
        and observation.finish == "stop"
        and observation.completed_at is not None
        and observation.result_sha256 == hashlib.sha256(result_bytes).hexdigest()
    )


def _read_stdout(record: TaskRecord) -> str:
    return (_read_artifact(record, "stdout.partial") or b"").decode(
        "utf-8", errors="replace"
    )


def _text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _limitations(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _exit_code(value: object) -> int | None:
    return value if type(value) is int else None


def _map_result(
    record: TaskRecord, data: dict[str, Any], *, agent: str, terminal: bool = False
) -> dict[str, Any]:
    if (
        data.get("task_id") != record.task_id
        or data.get("attempt_id") != record.attempt_id
        or data.get("session") != record.session
        or (
            data.get("delivery") == "completed"
            and (record.delivery is None or record.delivery.state != "completed")
        )
    ):
        return _pending(
            record,
            agent=agent,
            limitations=["result_mismatch"],
            delivery="pending",
        )

    stdout = _read_stdout(record)
    summary, parsed_session, cost, errors = delegate.parse_events(stdout)
    reported_summary = _text(data.get("summary"))
    if reported_summary is not None:
        summary = reported_summary
    session = _text(data.get("session")) or parsed_session or record.session
    delivery = _text(data.get("delivery")) or "pending"
    execution = _text(data.get("execution")) or "unknown"
    limitations = _limitations(data.get("limitations"))
    if data.get("deadline_exceeded") is True and "deadline_exceeded" not in limitations:
        limitations.append("deadline_exceeded")
    client_exit_code = _exit_code(data.get("client_exit_code"))

    if delegate._free_limit_reached(stdout):
        pending = _pending(
            record, agent=agent, limitations=limitations + ["admission_unreconciled"]
        )
        pending.update(
            code="free_limit_reached",
            message=(
                "Cuota gratuita agotada; antes de evaluar Go u otra alternativa se requiere reconciliar este intento."
            ),
        )
        return pending

    if (
        terminal
        and data.get("status") == "ok"
        and delivery == "completed"
        and record.session is not None
        and not errors
    ):
        return {
            "status": "ok",
            **_tracking(record),
            "session": session,
            "model": record.model,
            "variant": record.variant,
            "effort": record.variant or "provider_default",
            "reason": record.reason,
            "agent": agent,
            "summary": delegate._cap(summary),
            "cost": cost,
            "delivery": delivery,
            "execution": execution,
            "limitations": limitations,
        }

    if data.get("status") == "error" or delivery == "failed":
        if errors:
            code = "opencode_event_error"
            message = "OpenCode devolvio un evento de error; se requiere reconciliar el intento."
        elif client_exit_code is not None and client_exit_code != 0:
            code = "opencode_failed"
            message = (
                f"OpenCode terminó con código {client_exit_code}. Revisa los "
                "registros locales de OpenCode para el detalle."
            )
        else:
            code = "opencode_failed"
            message = "OpenCode no completó la tarea; revisa sus registros locales."
        return _tracked_error(
            code,
            message,
            record,
            session=session,
            delivery=delivery,
            execution=execution,
            limitations=limitations,
            uncertain=True,
        )

    if delivery == "completed" and not terminal:
        limitations.append("terminal_unconfirmed")
    return _pending(
        record,
        agent=agent,
        limitations=limitations,
        summary=summary,
        session=session,
        delivery="pending" if delivery == "completed" else delivery,
        execution=execution,
    )


def _wait_limit(prepared: BoundLaunch, wait_seconds: float | None) -> float:
    if wait_seconds is None:
        return prepared.timeout
    try:
        value = float(wait_seconds)
    except (TypeError, ValueError):
        return prepared.timeout
    if not math.isfinite(value) or value < 0:
        return prepared.timeout
    return min(value, prepared.timeout)


def _recover(context: HostContext, record: TaskRecord, *, agent: str) -> dict[str, Any]:
    try:
        current = load_task(Path(record.cwd), record.task_id)
        if os.path.normcase(str(Path(current.cwd).resolve())) != os.path.normcase(
            str(Path(record.cwd).resolve())
        ):
            raise HostRegistryError("root_mismatch")
        if (
            current.attempt_id,
            current.server_identity,
            current.role,
            current.model,
            current.variant,
        ) != (
            record.attempt_id,
            record.server_identity,
            record.role,
            record.model,
            record.variant,
        ):
            raise HostRegistryError("provenance_unavailable")
        if record.session is not None and record.session != current.session:
            raise HostRegistryError("session_mismatch")
        attempt = verify_provenance(context, current)
        snapshot = _read_result_snapshot(current)
        if snapshot is not None:
            result_bytes, data = snapshot
            if (
                data.get("delivery") == "completed"
                and current.delivery is not None
                and current.delivery.state == "completed"
                and not _reconciliation_matches_result(current, result_bytes)
            ):
                return _pending(
                    current,
                    agent=attempt.agent,
                    limitations=["result_mismatch"],
                    delivery="pending",
                )
            return _map_result(
                current,
                data,
                agent=attempt.agent,
                terminal=attempt.phase == "terminal_observed",
            )
        return _pending(
            current,
            agent=attempt.agent,
            limitations=["result_unavailable", "server_state_unknown"],
        )
    except (HostRegistryError, StoreError, OSError):
        return _pending(record, agent=agent, limitations=["provenance_unavailable"])


def _wait_result(
    context: HostContext, record: TaskRecord, seconds: float, *, agent: str
) -> dict[str, Any]:
    deadline = time.monotonic() + seconds
    while True:
        result = _recover(context, record, agent=agent)
        if result["status"] != "pending" or time.monotonic() >= deadline:
            return result
        # Any durable client observation already marked uncertain returns tracking.
        if _read_result(
            record
        ) is not None and "terminal_unconfirmed" not in result.get("limitations", []):
            return result
        time.sleep(min(POLL_SECONDS, max(0, deadline - time.monotonic())))


def _launch_supervisor(
    prepared: BoundLaunch, record: TaskRecord, *, context: HostContext
) -> subprocess.Popen[bytes]:
    """Seam de producción: arranca el supervisor independiente ya reservado.
    Returns the supervisor process handle for completion-aware waiting.
    """

    from session_worker import launch_worker

    _, process = launch_worker(
        prepared.project,
        record.task_id,
        context=context,
        agent=prepared.agent,
        _host_reserved=True,
        _task=prepared.task,
    )
    return process


def _host_error_code(exc: HostRegistryError) -> str:
    return exc.code or "provenance_unavailable"


def _service_code(exc: ServiceError) -> str:
    if exc.code in {
        "transport_error",
        "network_error",
        "timeout",
        "invalid_response",
        "redirect",
        "response_too_large",
        "response_too_deep",
        "invalid_url",
        "binding_closed",
    } or exc.code.startswith("http_"):
        return "service_unavailable"
    return exc.code or "service_unavailable"


def _service_message(code: str) -> str:
    if code == "service_unavailable":
        return (
            "El servicio OpenCode existente no está disponible; no se ha iniciado "
            "otro ni se ha enviado la tarea."
        )
    if code == "owner_mismatch":
        return "La identidad del servicio OpenCode cambió; no se reenvía la tarea."
    if code == "version_mismatch":
        return "El servicio OpenCode existente no tiene la versión soportada."
    return "No se pudo usar el servicio OpenCode existente."


def execute_bound(
    prepared: BoundLaunch,
    *,
    context: HostContext,
    wait_seconds: float | None = None,
) -> dict[str, Any]:
    """Reserva, revalida y delega un único envío al supervisor independiente."""

    seconds = _wait_limit(prepared, wait_seconds)
    if context != prepared.binding.context:
        return delegate._error(
            "host_context_mismatch", "El contexto no corresponde al binding preparado."
        )
    with prepared._claim_lock:
        prior = prepared._attempt_ids
        if prior is None:
            prepared._attempt_ids = (str(uuid.uuid4()), str(uuid.uuid4()))
        assert prepared._attempt_ids is not None
        task_id, attempt_id = prepared._attempt_ids
    record = _new_record(prepared, task_id=task_id, attempt_id=attempt_id)
    if prior is not None:
        return _recover(context, record, agent=prepared.agent)
    try:
        try:
            reserve_host_attempt(
                context, record, agent=prepared.agent, admission=prepared.admission
            )
        except (HostRegistryError, StoreError, OSError) as exc:
            return _tracked_error(
                getattr(exc, "code", "host_reservation_failed"),
                "No se pudo reservar la procedencia del intento; requiere reconciliacion.",
                record,
                uncertain=True,
            )

        try:
            save_task(prepared.project, record)
            _managed_directory(
                prepared.project,
                (".aikit", "sessions", record.task_id, record.attempt_id),
                create=True,
            )
        except (StoreError, OSError) as exc:
            return _pending(
                record,
                agent=prepared.agent,
                limitations=[getattr(exc, "code", "record_save_failed")],
            )

        try:
            verify_provenance(context, record)
            if prepared.binding.token != record.server_identity:
                raise ServiceError("owner_mismatch")
            if prepared.binding.verify_owner(timeout=1.0) is None:
                raise ServiceError("owner_mismatch")
        except (HostRegistryError, ServiceError) as exc:
            code = (
                _host_error_code(exc)
                if isinstance(exc, HostRegistryError)
                else _service_code(exc)
            )
            return _tracked_error(code, _service_message(code), record)

        try:
            _launch_supervisor(prepared, record, context=context)
        except (
            delegate.DelegateError,
            HostRegistryError,
            ServiceError,
            StoreError,
            OSError,
        ) as exc:
            code = getattr(exc, "code", None) or "client_start_failed"
            if isinstance(exc, ServiceError):
                code = _service_code(exc)
            pending = _pending(
                record,
                agent=prepared.agent,
                limitations=[str(code), "supervisor_start_uncertain"],
            )
            pending["code"] = str(code)
            return pending

        # Wait for result.json with bounded polling (original mechanism)
        return _wait_result(context, record, seconds, agent=prepared.agent)
    finally:
        prepared.binding.close()


def recover_local_result(context: HostContext, record: TaskRecord) -> dict[str, Any]:
    """Lee un resultado durable sin binding ni inferencia adicional."""

    return _recover(context, record, agent="build")


def load_local_record(project: Path, task_id: str) -> TaskRecord:
    """Atajo de lectura para consumidores que solo tienen la raíz y el ID."""

    return load_task(project, task_id)
