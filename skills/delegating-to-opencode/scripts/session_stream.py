"""Captura JSONL incremental acotada; los artefactos pueden contener salida sensible."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import BinaryIO

from session_store import StoreError, _require_regular_file, _validate_session_id

MAX_LINE = 1024 * 1024
MAX_ARTIFACT = 1024 * 1024
MAX_DIAGNOSTIC = 64 * 1024


def open_artifact(path: Path) -> BinaryIO:
    """Nunca reutiliza archivos anteriores ni sigue enlaces preparados."""
    if path.exists() or path.is_symlink():
        _require_regular_file(path)
        raise StoreError("attempt_reserved", "El intento ya está reservado.")
    return path.open("xb", buffering=0)


class EventStream:
    """Retiene una sola línea y un resumen, nunca la transcripción completa."""

    def __init__(self, on_session: Callable[[str], None]) -> None:
        self.on_session = on_session
        self.buffer = bytearray()
        self.discarding = False
        self.line_truncated = False
        self.invalid_json = False
        self.session: str | None = None
        self.summary = ""
        self.activity = False
        self.terminal = False
        self.error = False
        self.session_mismatch = False
        self.assistant_message_id: str | None = None
        self.assistant_message_mismatch: bool = False

    def feed(self, chunk: bytes) -> None:
        for part in chunk.splitlines(keepends=True):
            # Solo LF termina un evento JSONL; CR y UTF8 fragmentado se conservan.
            ended = part.endswith(b"\n")
            if not self.discarding:
                if len(self.buffer) + len(part) > MAX_LINE:
                    self.line_truncated = True
                    self.terminal = False
                    self.buffer.clear()
                    self.discarding = True
                else:
                    self.buffer.extend(part)
            if ended:
                if not self.discarding:
                    self._line(bytes(self.buffer))
                self.buffer.clear()
                self.discarding = False

    def finish(self) -> None:
        if self.buffer and not self.discarding:
            self._line(bytes(self.buffer))
        self.buffer.clear()

    def _line(self, raw: bytes) -> None:
        if not raw.strip():
            return
        try:
            event = json.loads(raw)
        except (ValueError, UnicodeDecodeError, RecursionError):
            self.invalid_json = True
            self.terminal = False
            return
        if not isinstance(event, dict):
            self.invalid_json = True
            self.terminal = False
            return
        part = event.get("part")
        if not isinstance(part, dict):
            part = {}
        observed_message_ids: list[str] = []
        for source in (event, part):
            if not isinstance(source, dict):
                continue
            value = source.get("messageID")
            if isinstance(value, str):
                observed_message_ids.append(value)
        if observed_message_ids:
            candidate = observed_message_ids[0]
            if any(value != candidate for value in observed_message_ids):
                self.assistant_message_mismatch = True
                self.assistant_message_id = None
            elif self.assistant_message_id is None:
                self.assistant_message_id = candidate
            elif self.assistant_message_id != candidate:
                self.assistant_message_mismatch = True
                self.assistant_message_id = None
        if event.get("type") == "error" or event.get("error") or part.get("error"):
            self.error = True
        identities: list[str] = []
        for source in (event, part):
            for key in ("sessionID", "sessionId"):
                if key not in source:
                    continue
                value = source[key]
                try:
                    if not isinstance(value, str):
                        raise StoreError("invalid_session_id", "Identidad no válida.")
                    _validate_session_id(value)
                except StoreError:
                    self.invalid_json = True
                    self.session_mismatch = True
                    self.terminal = False
                    return
                identities.append(value)
        if not identities:
            self.terminal = False
            return
        candidate = identities[0]
        if any(value != candidate for value in identities):
            # No preferir un alias sobre evidencia contradictoria del mismo evento.
            # La incertidumbre persiste aunque después llegue otro terminal válido.
            self.session_mismatch = True
            self.terminal = False
            return
        if self.session is None:
            self.session = candidate
            self.on_session(candidate)
        elif candidate != self.session:
            self.session_mismatch = True
            self.terminal = False
            return
        kind = event.get("type")
        if kind == "error" or event.get("error") or part.get("error"):
            self.error = True
        terminal = (
            kind in ("step_finish", "step-finish") and part.get("reason") == "stop"
        )
        self.terminal = terminal and self.activity and not self.session_mismatch
        if kind in (
            "text",
            "message",
            "assistant",
            "step_start",
            "step-start",
            "tool_use",
            "tool_result",
        ):
            self.activity = True
        if kind == "text":
            text = part.get("text", event.get("text"))
            if isinstance(text, str) and text:
                self.summary = (self.summary + ("\n" if self.summary else "") + text)[
                    :4000
                ]


class Capture:
    """Un flujo: artefacto parcial, cola diagnóstica y parser opcional."""

    def __init__(self, artifact: BinaryIO, events: EventStream | None = None) -> None:
        self.artifact = artifact
        self.events = events
        self.written = 0
        self.truncated = False
        self.write_failed = False
        self.diagnostic = bytearray()

    def feed(self, chunk: bytes) -> None:
        remaining = MAX_ARTIFACT - self.written
        if len(chunk) > remaining:
            self.truncated = True
        if remaining and not self.write_failed:
            try:
                self.artifact.write(chunk[:remaining])
                self.written += min(len(chunk), remaining)
            except OSError:
                self.write_failed = True
        self.diagnostic.extend(chunk)
        del self.diagnostic[:-MAX_DIAGNOSTIC]
        if self.events:
            self.events.feed(chunk)
