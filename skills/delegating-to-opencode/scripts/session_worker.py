"""Supervisor independiente de una CLI; no acredita el estado del servidor.

La entrada privada solo recibe raíz e ID. Los seams keyword-only son para
transportes de pruebas desde código; no existen flags ni variables de bypass.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO

import delegate
from availability_policy import ResultCode, eligible_for_attempt, record_outcome
from availability_state import (
    AvailabilitySnapshot,
    admission_for,
    configuration_signature,
    model_entry,
    read_snapshot,
    state_path,
    update_snapshot,
)
from host_registry import (
    HostRegistryError,
    record_host_admission,
    record_host_observation,
    record_host_processes,
    record_host_session,
    reserve_host_attempt,
    verify_provenance,
)
from restrictions import configuration_is_restricted
from service_connection import ManagedBinding, discover_existing
from service_identity import (
    HostContext,
    ServiceError,
    get_process_birth,
    resolve_host_context,
)
from session_backend import interrupt_session, worker_interrupt
from session_store import (
    DeliveryObservation,
    DeliveryState,
    ExecutionObservation,
    ProcessIdentity,
    StoreError,
    TaskRecord,
    _managed_directory,
    _require_regular_file,
    _task_directory,
    load_task,
    lock_task,
    save_task,
)
from session_stream import MAX_ARTIFACT, Capture, EventStream, open_artifact

CommandFactory = Callable[[TaskRecord], list[str]]
Interrupt = Callable[[TaskRecord], bool | None]


def _now() -> str:
    # Hora de observación; nunca se usa como creación de un proceso del SO.
    return datetime.now(timezone.utc).isoformat()


def _attempt_directory(root: Path, record: TaskRecord) -> Path:
    return _managed_directory(
        root, (".aikit", "sessions", record.task_id, record.attempt_id), create=True
    )


def _input(root: Path, record: TaskRecord) -> str:
    directory = _task_directory(root, record.task_id, create=False)
    path = directory / "task.txt"
    _require_regular_file(path)
    with path.open("rb") as stream:
        raw = stream.read(MAX_ARTIFACT + 1)
    if len(raw) > MAX_ARTIFACT:
        raise StoreError("task_too_large", "La entrada de tarea excede el límite.")
    try:
        return delegate._validate_task_text(raw.decode("utf-8-sig"))
    except UnicodeDecodeError as exc:
        raise StoreError("invalid_task", "La entrada de tarea no es UTF8.") from exc


def _task_bytes(text: str) -> bytes:
    try:
        value = delegate._validate_task_text(text).encode("utf-8")
    except UnicodeError as exc:
        raise StoreError("invalid_task", "Entrada de tarea no valida.") from exc
    if len(value) > MAX_ARTIFACT:
        raise StoreError("task_too_large", "Entrada de tarea excede el limite.")
    return value


def _stdin_task() -> str:
    raw = sys.stdin.buffer.read(MAX_ARTIFACT + 1)
    if len(raw) > MAX_ARTIFACT:
        raise StoreError("task_too_large", "Entrada de tarea excede el limite.")
    try:
        return delegate._validate_task_text(raw.decode("utf-8"))
    except UnicodeError as exc:
        raise StoreError("invalid_task", "Entrada de tarea no valida.") from exc


def _identity(pid: int) -> ProcessIdentity | None:
    birth = get_process_birth(pid)
    return (
        ProcessIdentity(pid, birth.started_at)
        if birth is not None and birth.started_at is not None
        else None
    )


def _bound_command(
    record: TaskRecord, text: str, context: HostContext, binding: ManagedBinding
) -> list[str]:
    attempt = verify_provenance(context, record)
    if (
        binding.token != attempt.binding_token
        or binding.verify_owner(timeout=1) is None
    ):
        raise ServiceError("owner_mismatch")
    config = binding.config_sources(Path(record.cwd), timeout=10)
    if not configuration_is_restricted(config):
        raise delegate.DelegateError(
            "unsafe_configuration", "Configuracion efectiva no restringida."
        )
    model, variant = delegate.parse_model(record.model, record.variant)
    delegate._validate_reason(record.reason)
    delegate.load_policy()

    snapshot = read_snapshot(state_path(context.aikit_state))
    project_key = delegate._project_key(Path(record.cwd))
    signature = configuration_signature(config)
    if snapshot is None or not any(
        item.project_key == project_key
        and item.config_signature == signature
        and item.service_version == binding.registration.version
        and {"config.get", "model.catalog"}.issubset(item.capabilities)
        for item in snapshot.catalog_contexts
    ):
        raise delegate.DelegateError(
            "availability_context_unavailable",
            "Contrato del contexto ausente o cambiado; no se envia.",
        )
    admission = admission_for(snapshot, project_key, model, variant)
    if attempt.admission is None:
        record_host_admission(context, record, admission)
    elif (
        attempt.admission.project_key,
        attempt.admission.config_signature,
        attempt.admission.service_version,
        attempt.admission.model,
        attempt.admission.variant,
        attempt.admission.metadata_signature,
    ) != (
        admission.project_key,
        admission.config_signature,
        admission.service_version,
        admission.model,
        admission.variant,
        admission.metadata_signature,
    ):
        raise delegate.DelegateError(
            "availability_context_changed",
            "Seleccion del intento ya no acreditada; no se envia.",
        )
    entry = model_entry(snapshot, project_key, model)
    if entry is None or not eligible_for_attempt(entry, record.attempt_id):
        raise delegate.DelegateError(
            "model_unavailable", "Modelo no disponible para este intento."
        )
    if variant is not None and variant not in entry.metadata.variants:
        raise delegate.DelegateError("invalid_variant", "Variante no disponible.")
    exe = delegate.find_opencode()
    if exe is None:
        raise delegate.DelegateError("opencode_missing", "CLI no disponible.")
    selected = model + ("#" + variant if variant else "")
    return delegate._build_bound_command(
        exe, binding.registration.url, selected, attempt.agent, text
    )


def _deadline(record: TaskRecord) -> float:
    seconds = record.execution_timeout_seconds
    if seconds is None:
        raise StoreError("invalid_timeout", "Se requiere límite finito de ejecución.")
    return delegate._validate_timeout(seconds)


def _reserve_marker(directory: Path, name: str) -> None:
    with open_artifact(directory / name) as stream:
        stream.write(b"reserved\n")


def launch_worker(
    root: Path,
    task_id: str,
    *,
    worker_command: CommandFactory | None = None,
    context: HostContext | None = None,
    agent: str = "build",
    _host_reserved: bool = False,
    _task: str | None = None,
) -> tuple[TaskRecord, subprocess.Popen[bytes]]:
    """Reserva antes de lanzar. Una reserva incierta nunca se elimina ni repite.
    Returns (TaskRecord, supervisor_process_handle) for completion-aware waiting.
    """
    with lock_task(root, task_id):
        record = load_task(root, task_id)
        _deadline(record)
        if Path(record.cwd).resolve() != root.resolve():
            raise StoreError("cwd_mismatch", "La raíz no corresponde a la tarea.")
        if context is None and record.server_identity is not None:
            context = resolve_host_context()
        if context is not None and not _host_reserved:
            reserve_host_attempt(context, record, agent=agent)
        if context is not None:
            verify_provenance(context, record)
        directory = _attempt_directory(root, record)
        if (directory / "supervisor.claim").exists():
            raise StoreError("attempt_reserved", "El intento ya está reservado.")
        _reserve_marker(directory, "launch.reserved")
        record.execution = ExecutionObservation("unknown", "launch_reserved", _now())
        save_task(root, record)
    argv = (
        worker_command(record)
        if worker_command
        else [
            sys.executable,
            str(Path(__file__).resolve()),
            str(root.resolve()),
            task_id,
        ]
    )
    if context is not None and worker_command is None:
        argv.extend(
            [
                "--host-registration",
                str(context.opencode_registration),
                "--host-state",
                str(context.aikit_state),
                "--host-version",
                context.expected_version,
            ]
        )
    if _task is not None:
        _task_bytes(_task)
        if worker_command is None:
            argv.append("--task-stdin")
    with (
        open_artifact(directory / "supervisor.reply") as output,
        open_artifact(directory / "supervisor.errors") as errors,
    ):
        options: dict[str, Any] = (
            {"creationflags": subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS}
            if sys.platform == "win32"
            else {"start_new_session": True}
        )
        # Sin pipes dependientes del padre ni handles heredados innecesarios.
        process = subprocess.Popen(
            argv,
            cwd=record.cwd,
            stdin=subprocess.PIPE if _task is not None else subprocess.DEVNULL,
            stdout=output,
            stderr=errors,
            close_fds=True,
            **options,
        )
        # El prompt cruza solo un pipe anonimo, sin manifiesto ni entorno.
        if _task is not None:
            assert process.stdin is not None
            try:
                process.stdin.write(_task_bytes(_task))
                process.stdin.flush()
            finally:
                process.stdin.close()
        threading.Thread(target=process.wait, daemon=True).start()
    return record, process


def supervise(
    root: Path,
    task_id: str,
    *,
    interrupt: Interrupt | None = None,
    prepare_command: CommandFactory | None = None,
    grace_seconds: float = 1.0,
    context: HostContext | None = None,
    _task: str | None = None,
) -> int:
    """Drena hasta EOF aunque venza ejecución o desaparezca el cliente externo."""
    if not math.isfinite(grace_seconds) or not 0 <= grace_seconds <= 10:
        raise StoreError(
            "invalid_grace", "La gracia debe estar entre cero y diez segundos."
        )
    with lock_task(root, task_id):
        record = load_task(root, task_id)
        seconds = _deadline(record)
        if Path(record.cwd).resolve() != root.resolve():
            raise StoreError("cwd_mismatch", "La raíz no corresponde a la tarea.")
        text = (
            _input(root, record)
            if _task is None
            else delegate._validate_task_text(_task)
        )
        directory = _attempt_directory(root, record)
        if context is None and record.server_identity is not None:
            context = resolve_host_context()
        if context is not None:
            verify_provenance(context, record)
        _reserve_marker(directory, "supervisor.claim")
    # Validación y probes reutilizan exactamente el núcleo existente.
    binding: ManagedBinding | None = None
    child_env: dict[str, str] | None = None
    try:
        if context is not None:
            binding = discover_existing(context)
            try:
                argv = _bound_command(record, text, context, binding)
                child_env = binding.child_environment(os.environ)
            except BaseException:
                binding.close()
                raise
        if prepare_command is not None:
            argv = prepare_command(record)
        elif context is None:
            raise ServiceError(
                "service_unavailable",
                "El envío requiere el servicio OpenCode existente.",
            )
        state_lock = threading.RLock()
        limitations = ["process_identity_unknown", "server_state_unknown"]
        provenance_failed = False
        deadline_exceeded = False
        interrupt_confirmed: bool | None = None
        journal: BinaryIO

        def observe(event: str) -> None:
            try:
                journal.write(
                    json.dumps(
                        {
                            "event": event,
                            "observed_at": _now(),
                            "session": record.session,
                        }
                    ).encode("utf-8")
                    + b"\n"
                )
            except OSError:
                if "journal_save_failed" not in limitations:
                    limitations.append("journal_save_failed")

        def persist() -> None:
            nonlocal provenance_failed
            try:
                with lock_task(root, task_id):
                    save_task(root, record)
            except (StoreError, OSError):
                if context is not None:
                    provenance_failed = True
                if "record_save_failed" not in limitations:
                    limitations.append("record_save_failed")

        def session_seen(session: str) -> None:
            nonlocal provenance_failed
            with state_lock:
                if context is not None:
                    try:
                        record_host_session(context, record, session)
                    except (HostRegistryError, OSError, StoreError):
                        provenance_failed = True
                        limitations.append("provenance_unavailable")
                        observe("host_session_save_failed")
                        return
                record.session = session
                record.last_event_at = _now()
                record.delivery = DeliveryObservation("partial", "cli_event", _now())
                persist()
                observe("session_seen")

        events = EventStream(session_seen)
        with (
            open_artifact(directory / "stdout.partial") as out_file,
            open_artifact(directory / "stderr.partial") as err_file,
            open_artifact(directory / "observations.jsonl") as journal,
        ):
            stdout = Capture(out_file, events)
            stderr = Capture(err_file)
            task_started = time.monotonic()
            try:
                if binding is not None:
                    if context is None:
                        raise ServiceError("host_context_unavailable")
                    verify_provenance(context, record)
                    if binding.verify_owner(timeout=1) is None:
                        raise ServiceError("owner_mismatch")
                process = subprocess.Popen(
                    argv,
                    cwd=record.cwd,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    close_fds=True,
                    env=child_env,
                    creationflags=subprocess.CREATE_NO_WINDOW
                    if sys.platform == "win32"
                    else 0,
                )
            except OSError as exc:
                raise StoreError(
                    "client_start_failed", "No se pudo iniciar la CLI."
                ) from exc
            with state_lock:
                record.client = _identity(process.pid)
                record.supervisor = _identity(os.getpid())
                if record.client is not None and record.supervisor is not None:
                    limitations.remove("process_identity_unknown")
                if context is not None:
                    try:
                        record_host_processes(context, record)
                    except (HostRegistryError, StoreError, OSError):
                        provenance_failed = True
                        limitations.append("provenance_unavailable")
                record.execution = ExecutionObservation(
                    "active", "client_started", _now()
                )
                record.delivery = DeliveryObservation(
                    "pending", "client_started", _now()
                )
                persist()
                observe("client_started")

            def drain(pipe: BinaryIO, capture: Capture) -> None:
                try:
                    while True:
                        chunk = os.read(pipe.fileno(), 8192)
                        if not chunk:
                            break
                        with state_lock:
                            capture.feed(chunk)
                except OSError:
                    with state_lock:
                        limitations.append("stream_read_failed")
                finally:
                    pipe.close()

            assert process.stdout is not None
            assert process.stderr is not None
            readers = [
                threading.Thread(target=drain, args=(process.stdout, stdout)),
                threading.Thread(target=drain, args=(process.stderr, stderr)),
            ]
            for thread in readers:
                thread.start()
            end = time.monotonic() + seconds
            grace_end: float | None = None
            while process.poll() is None or any(
                thread.is_alive() for thread in readers
            ):
                now = time.monotonic()
                if not deadline_exceeded and now >= end:
                    with state_lock:
                        deadline_exceeded = True
                        record.execution = ExecutionObservation(
                            "unknown", "execution_deadline_exceeded", _now()
                        )
                        persist()
                        observe("execution_deadline_exceeded")
                    try:
                        if interrupt is not None:
                            interrupt_confirmed = interrupt(record)
                        elif binding is not None and context is not None:
                            verify_provenance(context, record)
                            interrupt_confirmed = interrupt_session(
                                record, binding=binding
                            ).confirmed
                        else:
                            interrupt_confirmed = worker_interrupt(record)
                    except Exception:
                        limitations.append("interrupt_failed")
                    grace_end = time.monotonic() + grace_seconds
                if grace_end is not None and now >= grace_end:
                    with state_lock:
                        limitations.append("deadline_exceeded")
                        if interrupt_confirmed is not True:
                            limitations.append("interrupt_unconfirmed")
                        persist()
                    grace_end = None
                for thread in readers:
                    thread.join(0.005)
            returncode = process.wait()
            events.finish()
            delivery: DeliveryState = "partial" if events.summary else "pending"
            if returncode != 0 or events.error:
                delivery = "failed"
            elif (
                events.terminal
                and not events.error
                and "stream_read_failed" not in limitations
            ):
                delivery = "completed"
            elif deadline_exceeded and interrupt_confirmed is True:
                delivery = "interrupted"
            if events.invalid_json:
                limitations.append("invalid_json")
            if events.session_mismatch:
                limitations.append("session_mismatch")
            if stdout.write_failed or stderr.write_failed:
                limitations.append("partial_save_failed")
                if context is not None:
                    provenance_failed = True
            if context is not None and "journal_save_failed" in limitations:
                provenance_failed = True
            if deadline_exceeded and "deadline_exceeded" not in limitations:
                limitations.append("deadline_exceeded")
            if (
                deadline_exceeded
                and interrupt_confirmed is not True
                and "interrupt_unconfirmed" not in limitations
            ):
                limitations.append("interrupt_unconfirmed")
            if binding is not None and binding.verify_owner(timeout=1) is None:
                provenance_failed = True
                limitations.append("owner_mismatch")
            if context is not None:
                try:
                    record_host_observation(
                        context,
                        record,
                        terminal=False,
                    )
                except (HostRegistryError, StoreError, OSError):
                    provenance_failed = True
                    limitations.append("provenance_unavailable")
            if provenance_failed:
                delivery = "pending"
            record.execution = ExecutionObservation(
                "unknown",
                "execution_deadline_exceeded" if deadline_exceeded else "client_exited",
                _now(),
            )
            record.delivery = DeliveryObservation(
                delivery,
                "cli_terminal" if delivery == "completed" else "client_observation",
                _now(),
            )
            record.last_event_at = _now()
            persist()
            if provenance_failed and context is not None:
                delivery = "pending"
                record.delivery = DeliveryObservation(
                    "pending", "provenance_unavailable", _now()
                )
                try:
                    record_host_observation(context, record, terminal=False)
                except (HostRegistryError, StoreError, OSError):
                    pass  # Existing reservation and artifacts still block another send.
            observe("client_exited")
            try:
                stdout_text = (directory / "stdout.partial").read_text(
                    encoding="utf-8", errors="replace"
                )
            except OSError:
                stdout_text = ""
            free_limit_reached = delegate._free_limit_reached(stdout_text)
            availability_errors = ["opencode_event_error"] if events.error else []
            outcome_code: ResultCode | None = None
            if context is not None and delivery in {"completed", "failed"}:
                try:
                    outcome_code = _record_availability_outcome(
                        context,
                        record,
                        stdout_text,
                        availability_errors,
                        delivery,
                        free_limit_reached,
                        task_seconds=time.monotonic() - task_started,
                    )
                except Exception:  # noqa: BLE001
                    if "availability_outcome_failed" not in limitations:
                        limitations.append("availability_outcome_failed")
            if (
                context is not None
                and outcome_code in {"quota_exhausted", "balance_exhausted"}
                and binding is not None
            ):
                try:
                    from availability_refresh import coalesced_refresh

                    current_admission = verify_provenance(context, record).admission
                    coalesced_refresh(
                        state_path(context.aikit_state),
                        binding,
                        Path(record.cwd),
                        10.0,
                        force=True,
                        context_signature=current_admission.config_signature
                        if current_admission is not None
                        else None,
                        service_version=binding.registration.version,
                    )
                except Exception:  # noqa: BLE001
                    if "availability_refresh_failed" not in limitations:
                        limitations.append("availability_refresh_failed")
            report: dict[str, Any] = {
                "status": "ok"
                if delivery == "completed"
                else "error"
                if delivery == "failed"
                else "pending",
                "task_id": task_id,
                "attempt_id": record.attempt_id,
                "session": record.session,
                "delivery": delivery,
                "execution": "unknown",
                "client_exit_code": returncode,
                "summary": events.summary,
                "deadline_exceeded": deadline_exceeded,
                "stdout_truncated": stdout.truncated,
                "stderr_truncated": stderr.truncated,
                "line_truncated": events.line_truncated,
                "limitations": limitations,
            }
        try:
            with open_artifact(directory / "result.json") as destination:
                destination.write(json.dumps(report, ensure_ascii=True).encode("utf-8"))
        except (OSError, StoreError):
            limitations.append("result_save_failed")
            if context is not None:
                provenance_failed = True
        if context is not None:
            if not provenance_failed and delivery == "completed":
                try:
                    record_host_observation(context, record, terminal=True)
                except (HostRegistryError, StoreError, OSError):
                    provenance_failed = True
                    limitations.append("provenance_unavailable")
            if provenance_failed:
                delivery = "pending"
                report["status"], report["delivery"] = "pending", "pending"
        try:
            print(json.dumps(report, ensure_ascii=True), flush=True)
        except (OSError, ValueError):
            # El resultado separado ya está persistido aunque el consumidor se fuera.
            pass
        return 0 if delivery == "completed" else 1
    finally:
        if binding is not None:
            binding.close()


def _result_code_for_outcome(
    stdout: str, errors: list[str], delivery: str, free_limit: bool
) -> ResultCode:
    if free_limit:
        return "quota_exhausted"
    if delivery == "completed" and not errors:
        return "success"
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except (ValueError, RecursionError):
            continue
        if not isinstance(event, dict) or event.get("type") != "error":
            continue
        error = event.get("error")
        if not isinstance(error, dict):
            continue
        code = str(error.get("type", error.get("code", ""))).lower().replace("_", "-")
        status = error.get("statusCode", error.get("status"))
        if code in {
            "provider.free-limit",
            "provider.quota-exhausted",
            "quota-exhausted",
        }:
            return "quota_exhausted"
        if code in {
            "provider.insufficient-credits",
            "provider.balance-exhausted",
            "insufficient-credits",
        }:
            return "balance_exhausted"
        if code in {"provider.rate-limit", "rate-limited"} or status == 429:
            return "rate_limited"
        if code in {"provider.auth", "authentication-error"} or status in (401, 403):
            return "auth_error"
        if code in {
            "provider.output-budget",
            "unaffordable-output",
            "max-output-unaffordable",
        }:
            return "unaffordable_output"
        if (
            code in {"provider.transport", "provider.timeout", "connection-error"}
            or type(status) is int
            and status >= 500
        ):
            return "service_error"
        if code in {"task.compilation", "task.tests", "task.failed", "tool.error"}:
            return "task_failed"
    return "unknown"


def _record_availability_outcome(
    context: HostContext,
    record: TaskRecord,
    stdout: str,
    errors: list[str],
    delivery: str,
    free_limit: bool,
    *,
    task_seconds: float | None = None,
) -> ResultCode | None:
    from dataclasses import replace

    from availability_performance import (
        PerformanceModelKey,
        PerformanceSample,
        PerformanceWindow,
        add_sample,
        extract_samples_from_events,
    )

    now = datetime.now(timezone.utc)
    code = _result_code_for_outcome(stdout, errors, delivery, free_limit)
    recorded = False

    def mutate(snapshot: AvailabilitySnapshot) -> AvailabilitySnapshot:
        nonlocal recorded
        project_key = delegate._project_key(Path(record.cwd))
        entry = model_entry(snapshot, project_key, record.model)
        models = dict(snapshot.models)
        projects = {
            project: dict(entries)
            for project, entries in snapshot.project_models.items()
        }
        if entry is not None:
            recorded = record.attempt_id not in entry.outcome_attempt_ids
            updated = record_outcome(entry, code, now, attempt_id=record.attempt_id)
            projects.setdefault(project_key, {})[record.model] = updated
            if (
                record.model in models
                and models[record.model].context_key == project_key
            ):
                models[record.model] = updated
        window = PerformanceWindow(max_samples=1000)
        for sample in snapshot.performance_samples:
            window = add_sample(window, sample)
        key = PerformanceModelKey(
            record.model.split("/")[0], record.model, record.variant
        )
        events = []
        for line in stdout.splitlines():
            try:
                events.append(json.loads(line))
            except (ValueError, RecursionError):
                continue
        samples = extract_samples_from_events(
            events,
            task_id=record.task_id,
            attempt_id=record.attempt_id,
            key=key,
            source="supervisor_stdout",
            role=record.role,
            observed_at=now,
            measurement_kind="model",
        )
        for sample in samples:
            window = add_sample(window, sample)
        if task_seconds is not None:
            sample = PerformanceSample(
                key,
                record.task_id,
                record.attempt_id,
                "supervisor_clock",
                "task",
                now,
                event_id="supervisor-task-total",
                role=record.role,
                task_seconds=task_seconds,
            )
            window = add_sample(window, sample)
        return replace(
            snapshot,
            models=models,
            project_models=projects,
            performance_samples=window.samples,
        )

    update_snapshot(state_path(context.aikit_state), mutate)
    return code if recorded else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("task_id")
    parser.add_argument("--host-registration", type=Path)
    parser.add_argument("--host-state", type=Path)
    parser.add_argument("--host-version")
    parser.add_argument("--task-stdin", action="store_true")
    args = parser.parse_args()
    context = None
    if any((args.host_registration, args.host_state, args.host_version)):
        if not all((args.host_registration, args.host_state, args.host_version)):
            parser.error("Contexto host incompleto")
        context = HostContext(
            args.host_registration, args.host_state, args.host_version
        )
    try:
        task = _stdin_task() if args.task_stdin else None
        return supervise(args.root, args.task_id, context=context, _task=task)
    except (
        StoreError,
        HostRegistryError,
        ServiceError,
        delegate.DelegateError,
        OSError,
    ):
        # No exponer mensajes que puedan contener entrada/configuración cruda.
        print(
            json.dumps(
                {
                    "status": "error",
                    "code": "worker_failed",
                    "message": "No se pudo supervisar el intento; requiere reconciliación.",
                }
            ),
            flush=True,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
