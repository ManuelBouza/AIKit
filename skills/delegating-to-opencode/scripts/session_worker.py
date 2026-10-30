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
from session_store import (
    DeliveryObservation,
    DeliveryState,
    ExecutionObservation,
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


def _prepare_command(record: TaskRecord, text: str) -> list[str]:
    prepared = delegate._prepare_run(
        cwd=record.cwd,
        task_loader=lambda: text,
        model=record.model,
        variant=record.variant,
        reason=record.reason,
        agent="build",
        timeout=_deadline(record),
    )
    return prepared[0]


def _deadline(record: TaskRecord) -> float:
    seconds = record.execution_timeout_seconds
    if seconds is None:
        raise StoreError("invalid_timeout", "Se requiere límite finito de ejecución.")
    return delegate._validate_timeout(seconds)


def _reserve_marker(directory: Path, name: str) -> None:
    with open_artifact(directory / name) as stream:
        stream.write(b"reserved\n")


def launch_worker(
    root: Path, task_id: str, *, worker_command: CommandFactory | None = None
) -> TaskRecord:
    """Reserva antes de lanzar. Una reserva incierta nunca se elimina ni repite."""
    with lock_task(root, task_id):
        record = load_task(root, task_id)
        _deadline(record)
        if Path(record.cwd).resolve() != root.resolve():
            raise StoreError("cwd_mismatch", "La raíz no corresponde a la tarea.")
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
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=errors,
            close_fds=True,
            **options,
        )
        # No hay identidad SO acreditada: PID solo no se registra.
        threading.Thread(target=process.wait, daemon=True).start()
    return record


def supervise(
    root: Path,
    task_id: str,
    *,
    interrupt: Interrupt | None = None,
    prepare_command: CommandFactory | None = None,
    grace_seconds: float = 1.0,
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
        text = _input(root, record)
        directory = _attempt_directory(root, record)
        _reserve_marker(directory, "supervisor.claim")
    # Validación y probes reutilizan exactamente el núcleo existente.
    argv = (
        prepare_command(record) if prepare_command else _prepare_command(record, text)
    )
    state_lock = threading.RLock()
    limitations = ["process_identity_unknown", "server_state_unknown"]
    deadline_exceeded = False
    interrupt_confirmed: bool | None = None
    journal: BinaryIO

    def observe(event: str) -> None:
        try:
            journal.write(
                json.dumps(
                    {"event": event, "observed_at": _now(), "session": record.session}
                ).encode("utf-8")
                + b"\n"
            )
        except OSError:
            if "journal_save_failed" not in limitations:
                limitations.append("journal_save_failed")

    def persist() -> None:
        try:
            with lock_task(root, task_id):
                save_task(root, record)
        except (StoreError, OSError):
            if "record_save_failed" not in limitations:
                limitations.append("record_save_failed")

    def session_seen(session: str) -> None:
        with state_lock:
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
        try:
            process = subprocess.Popen(
                argv,
                cwd=record.cwd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True,
                creationflags=subprocess.CREATE_NO_WINDOW
                if sys.platform == "win32"
                else 0,
            )
        except OSError as exc:
            raise StoreError(
                "client_start_failed", "No se pudo iniciar la CLI."
            ) from exc
        with state_lock:
            record.execution = ExecutionObservation("active", "client_started", _now())
            record.delivery = DeliveryObservation("pending", "client_started", _now())
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
        while process.poll() is None or any(thread.is_alive() for thread in readers):
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
                    interrupt_confirmed = interrupt(record) if interrupt else None
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
        if deadline_exceeded and "deadline_exceeded" not in limitations:
            limitations.append("deadline_exceeded")
        if (
            deadline_exceeded
            and interrupt_confirmed is not True
            and "interrupt_unconfirmed" not in limitations
        ):
            limitations.append("interrupt_unconfirmed")
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
        observe("client_exited")
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
    try:
        print(json.dumps(report, ensure_ascii=True), flush=True)
    except (OSError, ValueError):
        # El resultado separado ya está persistido aunque el consumidor se fuera.
        pass
    return 0 if delivery == "completed" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("task_id")
    args = parser.parse_args()
    try:
        return supervise(args.root, args.task_id)
    except (StoreError, delegate.DelegateError, OSError):
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
