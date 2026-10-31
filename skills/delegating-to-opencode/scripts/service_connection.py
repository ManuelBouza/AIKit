"""Conexión autenticada al servicio OpenCode existente, sin autoarranque."""

from __future__ import annotations

import base64
import json
import select
import socket
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from service_identity import (
    HostContext,
    ServiceError,
    ServiceRegistration,
    get_process_birth,
    process_birth_or_raise,
    read_registration,
    token_for,
)
from session_backend import OwnerIdentity
from session_store import Pricing, Role

MAX_HTTP_BODY_BYTES = 8 * 1024 * 1024
DEFAULT_OPERATIONS = frozenset(
    {
        "server.info",
        "session.get",
        "session.active",
        "session.inbox.list",
        "session.permission.list",
        "session.interrupt",
    }
)


@dataclass
class ManagedBinding:
    registration: ServiceRegistration
    context: HostContext
    owner: OwnerIdentity
    token: str
    operations: frozenset[str] = field(default_factory=lambda: DEFAULT_OPERATIONS)
    _closed: bool = field(default=False, repr=False)
    _credential: str = field(default="", repr=False)
    _birth_filetime: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        self._credential = self.registration.credential

    @property
    def expected_owner(self) -> OwnerIdentity:
        return self.owner

    def verify_owner(self, *, timeout: float) -> OwnerIdentity | None:
        if self._closed:
            return None
        deadline = time.monotonic() + max(0.0, timeout)
        try:
            reg = read_registration(self.context)
        except ServiceError:
            return None
        if reg.registration_id != self.registration.registration_id:
            return None
        if reg.url != self.registration.url:
            return None
        if reg.pid != self.registration.pid:
            return None
        if reg.version != self.registration.version:
            return None
        if reg.credential != self._credential:
            return None
        birth = get_process_birth(reg.pid)
        if birth is None or birth.filetime != self._birth_filetime:
            return None
        if time.monotonic() > deadline:
            return None
        # Revalidar token.
        if token_for(reg, birth, reg.version) != self.token:
            return None
        return self.owner

    pass

    def request(
        self,
        operation: str,
        *,
        session_id: str | None = None,
        timeout: float = 10.0,
        resume: bool | None = None,
    ) -> Any:
        from session_backend import ApiResponse

        if self._closed:
            raise ServiceError("binding_closed", "Binding cerrado.")
        # Revalidar propietario antes.
        owner = self.verify_owner(timeout=min(timeout, 1.0))
        if owner is None:
            raise ServiceError("owner_mismatch", "Propietario no verificado.")
        if operation not in self.operations:
            raise ServiceError("operation_unavailable", "Operación no disponible.")
        if (
            operation == "session.interrupt"
            and resume is not False
            and resume is not None
        ):
            # solo resume=False permitido
            pass
        if operation == "session.interrupt":
            if resume is not False:
                raise ServiceError("invalid_resume", "resume debe ser false.")
        path, method = _operation_path(operation, session_id)
        url = self.registration.url.rstrip("/") + path
        # location[directory] para config/model se añade por caller en path?
        deadline = time.monotonic() + max(0.0, timeout)
        data = _http_request(
            url=url,
            method=method,
            credential=self._credential,
            timeout=timeout,
            deadline=deadline,
        )
        # Revalidar después.
        if self.verify_owner(timeout=0.5) is None:
            raise ServiceError("owner_mismatch", "Propietario cambió.")
        return ApiResponse(status=data[0], body=data[1])

    def config_sources(self, project: Path, *, timeout: float) -> object:
        if self._closed:
            raise ServiceError("binding_closed", "Binding cerrado.")
        if self.verify_owner(timeout=min(timeout, 1.0)) is None:
            raise ServiceError("owner_mismatch", "Propietario no verificado.")
        url = self.registration.url.rstrip("/") + "/api/config"
        params = f"?directory={_quote(str(project))}"
        deadline = time.monotonic() + max(0.0, timeout)
        status, body = _http_request(
            url=url + params,
            method="GET",
            credential=self._credential,
            timeout=timeout,
            deadline=deadline,
        )
        if self.verify_owner(timeout=0.5) is None:
            raise ServiceError("owner_mismatch", "Propietario cambió.")
        if status != 200:
            raise ServiceError("http_error", "Error HTTP.")
        return body

    def model_catalog(self, project: Path, *, timeout: float) -> object:
        if self._closed:
            raise ServiceError("binding_closed", "Binding cerrado.")
        if self.verify_owner(timeout=min(timeout, 1.0)) is None:
            raise ServiceError("owner_mismatch", "Propietario no verificado.")
        url = self.registration.url.rstrip("/") + "/api/model"
        params = f"?directory={_quote(str(project))}"
        deadline = time.monotonic() + max(0.0, timeout)
        status, body = _http_request(
            url=url + params,
            method="GET",
            credential=self._credential,
            timeout=timeout,
            deadline=deadline,
        )
        if self.verify_owner(timeout=0.5) is None:
            raise ServiceError("owner_mismatch", "Propietario cambió.")
        if status != 200:
            raise ServiceError("http_error", "Error HTTP.")
        return body

    def child_environment(self, base: Mapping[str, str]) -> dict[str, str]:
        if self._closed:
            raise ServiceError("binding_closed", "Binding cerrado.")
        result = dict(base)
        result["OPENCODE_PASSWORD"] = self._credential
        return result

    def close(self) -> None:
        self._closed = True
        self._credential = ""

    def __repr__(self) -> str:
        return (
            f"ManagedBinding(registration_id={self.registration.registration_id!r}, "
            f"url={self.registration.url!r}, closed={self._closed})"
        )


@dataclass
class BoundLaunch:
    """Envío ya validado; no expone prompt, motivo, argv ni credencial."""

    binding: ManagedBinding = field(repr=False)
    project: Path
    argv: list[str] = field(repr=False)
    model: str
    variant: str | None
    reason: str = field(repr=False)
    agent: str
    timeout: float
    role: Role = "implementer"
    task: str = field(default="", repr=False)
    pricing: Pricing = "unknown"
    _attempt_ids: tuple[str, str] | None = field(default=None, init=False, repr=False)
    _claim_lock: Any = field(default_factory=threading.Lock, init=False, repr=False)

    def metadata(self) -> dict[str, Any]:
        """Solo seleccion/ubicacion; nunca binding, prompt, argv ni motivo."""
        return {
            "project": str(self.project),
            "model": self.model,
            "variant": self.variant,
            "agent": self.agent,
            "timeout": self.timeout,
            "role": self.role,
            "pricing": self.pricing,
        }


def _quote(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")


def _operation_path(operation: str, session_id: str | None) -> tuple[str, str]:
    if operation == "server.info":
        return "/api/info", "GET"
    if operation == "session.get":
        if not session_id:
            raise ServiceError("invalid_session", "Sesión requerida.")
        return f"/api/session/{session_id}", "GET"
    if operation == "session.active":
        return "/api/session/status", "GET"
    if operation == "session.inbox.list":
        if not session_id:
            raise ServiceError("invalid_session", "Sesión requerida.")
        return f"/api/session/{session_id}/message", "GET"
    if operation == "session.permission.list":
        return "/api/permission", "GET"
    if operation == "session.interrupt":
        if not session_id:
            raise ServiceError("invalid_session", "Sesión requerida.")
        return f"/api/session/{session_id}/abort", "POST"
    raise ServiceError("operation_unavailable", "Operación no soportada.")


def _send_all(sock: Any, data: bytes, deadline: float) -> None:
    view = memoryview(data)
    sent = 0
    while sent < len(data):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ServiceError("timeout", "Presupuesto agotado.")
        r, w, _ = select.select([], [sock], [], remaining)
        if not w:
            raise ServiceError("timeout", "Presupuesto agotado.")
        try:
            n = sock.send(view[sent:])
        except (TimeoutError, BlockingIOError):
            continue
        except OSError:
            raise ServiceError("transport_error", "Error de transporte.") from None
        if n <= 0:
            raise ServiceError("transport_error", "Error de transporte.") from None
        sent += n


def _http_request(
    *,
    url: str,
    method: str,
    credential: str,
    timeout: float,
    deadline: float,
) -> tuple[int, Any]:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ServiceError("invalid_url", "URL invalida.")
    host = parsed.hostname
    if not host:
        raise ServiceError("invalid_url", "Host invalido.")
    port = parsed.port
    if port is None:
        port = 443 if parsed.scheme == "https" else 80
    path = parsed.path or "/"
    if parsed.query:
        path = path + "?" + parsed.query

    sock: Any = None
    try:
        addrinfos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise ServiceError("network_error", "Error de red.") from None
    if not addrinfos:
        raise ServiceError("network_error", "Error de red.") from None
    family, socktype, proto, _, sockaddr = addrinfos[0]
    sock = socket.socket(family, socktype, proto)
    sock.setblocking(False)
    try:
        sock.connect(sockaddr)
    except BlockingIOError:
        pass
    except OSError:
        sock.close()
        raise ServiceError("transport_error", "Error de transporte.") from None

    remaining = deadline - time.monotonic()
    if remaining <= 0:
        sock.close()
        raise ServiceError("timeout", "Presupuesto agotado.")
    _, wlist, _ = select.select([], [sock], [], remaining)
    if not wlist:
        sock.close()
        raise ServiceError("timeout", "Presupuesto agotado.")
    err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
    if err != 0:
        sock.close()
        raise ServiceError("transport_error", "Error de transporte.") from None

    if parsed.scheme == "https":
        ctx = ssl.create_default_context()
        try:
            ssl_sock = ctx.wrap_socket(
                sock, server_hostname=host, do_handshake_on_connect=False
            )
        except Exception:
            sock.close()
            raise ServiceError("transport_error", "Error de transporte.") from None
        sock = ssl_sock
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                sock.close()
                raise ServiceError("timeout", "Presupuesto agotado.")
            try:
                sock.do_handshake()
                break
            except ssl.SSLWantReadError:
                rlist, _, _ = select.select([sock], [], [], remaining)
                if not rlist:
                    sock.close()
                    raise ServiceError("timeout", "Presupuesto agotado.") from None
            except ssl.SSLWantWriteError:
                _, wlist, _ = select.select([], [sock], [], remaining)
                if not wlist:
                    sock.close()
                    raise ServiceError("timeout", "Presupuesto agotado.") from None
            except Exception:
                sock.close()
                raise ServiceError("transport_error", "Error de transporte.") from None

    request_bytes = (
        f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n"
    ).encode("ascii")
    if credential:
        token = base64.b64encode(f"opencode:{credential}".encode()).decode("ascii")
        request_bytes += f"Authorization: Basic {token}\r\n".encode("ascii")
    request_bytes += b"\r\n"
    try:
        _send_all(sock, request_bytes, deadline)
    except ServiceError:
        sock.close()
        raise

    # Leer cabeceras hasta linea vacia.
    buffer = b""
    while b"\r\n\r\n" not in buffer:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            sock.close()
            raise ServiceError("timeout", "Presupuesto agotado.")
        rlist, _, _ = select.select([sock], [], [], remaining)
        if not rlist:
            sock.close()
            raise ServiceError("timeout", "Presupuesto agotado.")
        try:
            chunk = sock.recv(4096)
        except (TimeoutError, BlockingIOError):
            continue
        except OSError:
            sock.close()
            raise ServiceError("transport_error", "Error de transporte.") from None
        if not chunk:
            break
        buffer += chunk
        if len(buffer) > MAX_HTTP_BODY_BYTES + 8192:
            sock.close()
            raise ServiceError("response_too_large", "Respuesta demasiado grande.")

    if b"\r\n\r\n" not in buffer:
        sock.close()
        raise ServiceError("invalid_response", "Respuesta invalida.")
    header_bytes, rest = buffer.split(b"\r\n\r\n", 1)
    try:
        header_text = header_bytes.decode("iso-8859-1")
    except Exception:
        sock.close()
        raise ServiceError("invalid_response", "Respuesta invalida.") from None
    lines = header_text.split("\r\n")
    status_parts = lines[0].split(" ", 2)
    if len(status_parts) < 2 or not status_parts[1].isdigit():
        sock.close()
        raise ServiceError("invalid_response", "Respuesta invalida.")
    status = int(status_parts[1])
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()

    body_bytes = rest
    content_length = headers.get("content-length")
    transfer_encoding = headers.get("transfer-encoding", "")
    if content_length is not None:
        try:
            total_len = int(content_length)
        except ValueError:
            sock.close()
            raise ServiceError("invalid_response", "Respuesta invalida.") from None
        while len(body_bytes) < total_len:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                sock.close()
                raise ServiceError("timeout", "Presupuesto agotado.")
            rlist, _, _ = select.select([sock], [], [], remaining)
            if not rlist:
                sock.close()
                raise ServiceError("timeout", "Presupuesto agotado.")
            try:
                chunk = sock.recv(65536)
            except (TimeoutError, BlockingIOError):
                continue
            except OSError:
                sock.close()
                raise ServiceError("transport_error", "Error de transporte.") from None
            if not chunk:
                break
            body_bytes += chunk
            if len(body_bytes) > MAX_HTTP_BODY_BYTES:
                sock.close()
                raise ServiceError("response_too_large", "Respuesta demasiado grande.")
    elif "chunked" in transfer_encoding:
        buf = body_bytes
        decoded = b""
        while True:
            while b"\r\n" not in buf:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    sock.close()
                    raise ServiceError("timeout", "Presupuesto agotado.")
                rlist, _, _ = select.select([sock], [], [], remaining)
                if not rlist:
                    sock.close()
                    raise ServiceError("timeout", "Presupuesto agotado.")
                try:
                    chunk = sock.recv(65536)
                except (TimeoutError, BlockingIOError):
                    continue
                except OSError:
                    sock.close()
                    raise ServiceError(
                        "transport_error", "Error de transporte."
                    ) from None
                if not chunk:
                    break
                buf += chunk
            if b"\r\n" not in buf:
                break
            size_hex, _, rest = buf.partition(b"\r\n")
            try:
                size = int(size_hex.strip(), 16)
            except ValueError:
                sock.close()
                raise ServiceError("invalid_response", "Respuesta invalida.") from None
            buf = rest
            if size == 0:
                break
            while len(buf) < size + 2:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    sock.close()
                    raise ServiceError("timeout", "Presupuesto agotado.")
                rlist, _, _ = select.select([sock], [], [], remaining)
                if not rlist:
                    sock.close()
                    raise ServiceError("timeout", "Presupuesto agotado.")
                try:
                    chunk = sock.recv(65536)
                except (TimeoutError, BlockingIOError):
                    continue
                except OSError:
                    sock.close()
                    raise ServiceError(
                        "transport_error", "Error de transporte."
                    ) from None
                if not chunk:
                    break
                buf += chunk
            decoded += buf[:size]
            buf = buf[size + 2 :]
            if len(decoded) > MAX_HTTP_BODY_BYTES:
                sock.close()
                raise ServiceError("response_too_large", "Respuesta demasiado grande.")
        body_bytes = decoded
    else:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                sock.close()
                raise ServiceError("timeout", "Presupuesto agotado.")
            rlist, _, _ = select.select([sock], [], [], remaining)
            if not rlist:
                break
            try:
                chunk = sock.recv(65536)
            except (TimeoutError, BlockingIOError):
                continue
            except OSError:
                sock.close()
                raise ServiceError("transport_error", "Error de transporte.") from None
            if not chunk:
                break
            body_bytes += chunk
            if len(body_bytes) > MAX_HTTP_BODY_BYTES:
                sock.close()
                raise ServiceError("response_too_large", "Respuesta demasiado grande.")

    try:
        sock.close()
    except Exception:
        pass

    if status >= 300 and status < 400:
        raise ServiceError("redirect", "Redireccion no permitida.")
    try:
        body = json.loads(body_bytes.decode("utf-8")) if body_bytes else None
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError):
        raise ServiceError("invalid_response", "Respuesta invalida.") from None
    if _json_depth(body) > 128:
        raise ServiceError("response_too_deep", "Respuesta demasiado profunda.")
    if status != 200:
        raise ServiceError(f"http_{status}", "Error HTTP.")
    return status, body


def _json_depth(value: Any, current: int = 0) -> int:
    if isinstance(value, dict):
        if not value:
            return current + 1
        return max(_json_depth(v, current + 1) for v in value.values())
    if isinstance(value, list):
        if not value:
            return current + 1
        return max(_json_depth(v, current + 1) for v in value)
    return current


def discover_existing(context: HostContext, *, timeout: float = 10.0) -> ManagedBinding:
    deadline = time.monotonic() + max(0.0, timeout)
    reg = read_registration(context)
    # Validar ACL/trust ya en read_registration? read_registration checks registration_trusted.
    if not registration_trusted_path(context.opencode_registration):
        raise ServiceError("registration_untrusted", "Registro no confiable.")
    if time.monotonic() > deadline:
        raise ServiceError("timeout", "Presupuesto agotado.")
    birth = process_birth_or_raise(reg.pid)
    if birth.filetime <= 0:
        raise ServiceError("process_identity_unavailable", "Nacimiento inválido.")
    # HTTP info
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise ServiceError("timeout", "Presupuesto agotado.")
    url = reg.url.rstrip("/") + "/api/info"
    status, body = _http_request(
        url=url,
        method="GET",
        credential=reg.credential,
        timeout=min(timeout, remaining),
        deadline=deadline,
    )
    if status != 200:
        raise ServiceError("service_unavailable", "Servicio no disponible.")
    if not isinstance(body, dict):
        raise ServiceError("invalid_response", "Respuesta inválida.")
    info_pid = body.get("pid")
    info_version = body.get("version")
    if type(info_pid) is not int or isinstance(info_pid, bool):
        raise ServiceError("invalid_response", "Respuesta invalida.")
    if not isinstance(info_version, str):
        raise ServiceError("invalid_response", "Respuesta invalida.")
    if info_pid != reg.pid or info_version != reg.version:
        raise ServiceError("owner_mismatch", "Identidad no coincide.")
    # token
    tok = token_for(reg, birth, reg.version)
    started_at = birth.started_at
    owner = OwnerIdentity(
        identity=tok, pid=reg.pid, started_at=started_at, version=reg.version
    )
    binding = ManagedBinding(
        registration=reg,
        context=context,
        owner=owner,
        token=tok,
        operations=DEFAULT_OPERATIONS,
    )
    # Guardar filetime para revalidación.
    binding._birth_filetime = birth.filetime
    # cerrar handle? process_birth ya cerró.
    if time.monotonic() > deadline:
        raise ServiceError("timeout", "Presupuesto agotado.")
    return binding


def registration_trusted_path(path: Path) -> bool:
    from service_identity import registration_trusted

    return registration_trusted(path)
