"""Identidad confiable del servicio OpenCode existente.

No arranca ni descubre servicios. Solo valida registro, proceso y token opaco.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import stat
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ServiceError(Exception):
    """Error estable sin cuerpo remoto ni secretos."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code
        self.message = message or code


MAX_REGISTRATION_BYTES = 64 * 1024
MAX_JSON_DEPTH = 8
MAX_HTTP_BODY_BYTES = 8 * 1024 * 1024
MAX_JSON_RESPONSE_DEPTH = 128


@dataclass(frozen=True)
class HostContext:
    opencode_registration: Path
    aikit_state: Path
    expected_version: str


@dataclass
class ServiceRegistration:
    registration_id: str
    url: str
    pid: int
    version: str
    credential: str = field(repr=False, default="")

    def __repr__(self) -> str:
        return (
            "ServiceRegistration("
            f"registration_id={self.registration_id!r}, url={self.url!r}, "
            f"pid={self.pid!r}, version={self.version!r}, credential=<redacted>)"
        )

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class ProcessBirth:
    pid: int
    filetime: int
    started_at: str | None


@dataclass(frozen=True)
class CapabilitySnapshot:
    """Contrato mínimo que la fase de refresh validará contra OpenAPI.

    No autoriza envío por sí mismo: solo registra versión observada y las
    operaciones que el servicio deberá confirmar antes de usarse.
    """

    service_version: str
    operations: frozenset[str]
    schema_version: int | None = None
    source: str = "registration"


MAX_SERVICE_VERSION_CHARS = 64


def resolve_host_context() -> HostContext:
    registration = os.environ.get("AIKIT_OPENCODE_REGISTRATION")
    state = os.environ.get("AIKIT_STATE")
    version = os.environ.get("AIKIT_EXPECTED_OPENCODE_VERSION", "2.2.0")
    if not registration or not state:
        raise ServiceError(
            "host_context_unavailable",
            "Falta configuración confiable del host.",
        )
    return HostContext(
        opencode_registration=Path(registration),
        aikit_state=Path(state),
        expected_version=version,
    )


def _depth(value: Any, current: int = 0) -> int:
    if current > MAX_JSON_DEPTH:
        return current
    if isinstance(value, dict):
        if not value:
            return current + 1
        return max(_depth(v, current + 1) for v in value.values())
    if isinstance(value, list):
        if not value:
            return current + 1
        return max(_depth(v, current + 1) for v in value)
    return current


def parse_registration_bytes(raw: bytes) -> dict[str, Any]:
    if len(raw) > MAX_REGISTRATION_BYTES:
        raise ServiceError("registration_too_large", "Registro demasiado grande.")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ServiceError("registration_invalid", "Registro no UTF-8.") from exc
    try:
        data = json.loads(text, object_pairs_hook=_no_duplicate_keys)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise ServiceError("registration_invalid", "Registro JSON inválido.") from exc
    if not isinstance(data, dict):
        raise ServiceError("registration_invalid", "Registro no es objeto.")
    if _depth(data) > MAX_JSON_DEPTH:
        raise ServiceError("registration_too_deep", "Registro demasiado profundo.")
    return data


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def canonical_url(value: str) -> str:
    """Valida y normaliza URL base: solo loopback literal, puerto, ruta raíz."""
    if not isinstance(value, str) or not value:
        raise ServiceError("invalid_url", "URL inválida.")
    # Rechazar espacios y caracteres de control.
    if any(ch.isspace() or ord(ch) < 0x20 for ch in value):
        raise ServiceError("invalid_url", "URL inválida.")
    # Parseo manual estricto.
    if "://" not in value:
        raise ServiceError("invalid_url", "Falta esquema.")
    scheme, rest = value.split("://", 1)
    if scheme not in {"http", "https"}:
        raise ServiceError("invalid_url", "Esquema no permitido.")
    if "/" in rest:
        authority, path = rest.split("/", 1)
        path = "/" + path
    else:
        authority, path = rest, "/"
    if path not in ("", "/"):
        raise ServiceError("invalid_url", "Ruta no permitida.")
    path = "/"
    # userinfo
    if "@" in authority:
        raise ServiceError("invalid_url", "UserInfo no permitido.")
    # host/port
    if authority.startswith("["):
        # IPv6 literal
        if "]" not in authority:
            raise ServiceError("invalid_url", "Host inválido.")
        host, _, port_part = authority[1:].partition("]")
        host = "[" + host + "]"
        if port_part.startswith(":"):
            port_str = port_part[1:]
        elif port_part == "":
            port_str = ""
        else:
            raise ServiceError("invalid_url", "Puerto inválido.")
    else:
        if ":" in authority:
            host, port_str = authority.rsplit(":", 1)
        else:
            host, port_str = authority, ""
    host_lower = host.lower()
    if host_lower not in {"127.0.0.1", "localhost", "[::1]", "::1"}:
        # permitir solo loopback literal
        if host_lower not in {"127.0.0.1", "localhost", "[::1]"}:
            raise ServiceError("invalid_url", "Host no loopback.")
    if port_str == "":
        raise ServiceError("invalid_url", "Puerto requerido.")
    if not port_str.isdigit():
        raise ServiceError("invalid_url", "Puerto inválido.")
    port = int(port_str)
    if port < 1 or port > 65535:
        raise ServiceError("invalid_url", "Puerto inválido.")
    # query/fragment ya rechazados por ausencia de ? y #
    if "?" in value or "#" in value:
        raise ServiceError("invalid_url", "Query/fragmento no permitido.")
    if host.startswith("["):
        normalized_host = host
    else:
        normalized_host = host.lower()
    return f"{scheme}://{normalized_host}:{port}/"


def validate_registration(
    data: dict[str, Any], context: HostContext
) -> ServiceRegistration:
    # Campos esperados.
    required = {"id", "url", "pid", "version"}
    if not required.issubset(data):
        raise ServiceError("registration_invalid", "Registro incompleto.")
    registration_id = data.get("id")
    url_raw = data.get("url")
    pid = data.get("pid")
    version = data.get("version")
    credential = (
        data.get("password") or data.get("token") or data.get("credential") or ""
    )
    if not isinstance(registration_id, str) or not registration_id:
        raise ServiceError("registration_invalid", "ID inválido.")
    if not isinstance(url_raw, str):
        raise ServiceError("registration_invalid", "URL inválida.")
    if isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0:
        raise ServiceError("registration_invalid", "PID inválido.")
    if (
        not isinstance(version, str)
        or not version
        or len(version) > MAX_SERVICE_VERSION_CHARS
    ):
        raise ServiceError("version_invalid", "Versión observada inválida.")
    url = canonical_url(url_raw)
    if not isinstance(credential, str):
        raise ServiceError("registration_invalid", "Credencial inválida.")
    return ServiceRegistration(
        registration_id=registration_id,
        url=url,
        pid=pid,
        version=version,
        credential=credential,
    )


def is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError:
        return True
    attrs = getattr(info, "st_file_attributes", 0)
    return bool(attrs & 0x400)


def registration_trusted(path: Path) -> bool:
    """Comprobación básica de confianza del archivo de registro."""
    try:
        info = path.lstat()
    except OSError:
        return False
    if path.is_symlink() or is_reparse(path):
        return False
    if not stat.S_ISREG(info.st_mode):
        return False
    if sys.platform == "win32":
        return _windows_registration_trusted(path)
    # Fail closed fuera de Windows: no hay prueba equivalente acreditada.
    return False


def _windows_registration_trusted(path: Path) -> bool:
    try:
        advapi32 = ctypes.windll.advapi32
        kernel32 = ctypes.windll.kernel32
    except Exception:
        return False

    # Obtener DACL y propietario.
    ppsid_owner = ctypes.c_void_p()
    ppdacl = ctypes.c_void_p()
    ppsecurity = ctypes.c_void_p()
    res = advapi32.GetNamedSecurityInfoW(
        str(path),
        1,  # SE_FILE_OBJECT
        0x00000001 | 0x00000004,  # OWNER | DACL
        ctypes.byref(ppsid_owner),
        None,
        ctypes.byref(ppdacl),
        None,
        ctypes.byref(ppsecurity),
    )
    if res != 0 or ppsid_owner.value is None or ppdacl.value is None:
        return False

    # Propietario debe ser el usuario actual.
    token = ctypes.c_void_p()
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    advapi32.OpenProcessToken.argtypes = [
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    if not advapi32.OpenProcessToken(
        kernel32.GetCurrentProcess(), 0x0008, ctypes.byref(token)
    ):
        return False
    size = ctypes.c_ulong(0)
    advapi32.GetTokenInformation(token, 1, None, 0, ctypes.byref(size))
    buf = ctypes.create_string_buffer(size.value)
    if not advapi32.GetTokenInformation(token, 1, buf, size.value, ctypes.byref(size)):
        kernel32.CloseHandle(token)
        return False
    sid_ptr = ctypes.cast(buf, ctypes.POINTER(ctypes.c_void_p)).contents.value
    kernel32.CloseHandle(token)
    advapi32.EqualSid.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    advapi32.EqualSid.restype = ctypes.c_int
    if sid_ptr is None or not advapi32.EqualSid(sid_ptr, ppsid_owner.value):
        return False

    # Construir lista de SIDs autorizados (usuario, SYSTEM, Administradores).
    allowed_sids: list[ctypes.c_void_p] = [ctypes.c_void_p(sid_ptr)]
    for sid_str in ("S-1-5-18", "S-1-5-32-544", "S-1-3-4"):
        psid = ctypes.c_void_p()
        if advapi32.ConvertStringSidToSidW(sid_str, ctypes.byref(psid)):
            allowed_sids.append(psid)

    # Bits de modificacion/escritura.
    write_bits = (
        0x0002
        | 0x0004
        | 0x0010
        | 0x0100
        | 0x10000
        | 0x40000
        | 0x80000
        | 0x40000000
        | 0x10000000
    )

    # Inspeccionar ACEs.
    class ACL(ctypes.Structure):
        _fields_ = [
            ("AclRevision", ctypes.c_ubyte),
            ("Sbz1", ctypes.c_ubyte),
            ("AclSize", ctypes.c_ushort),
            ("AceCount", ctypes.c_ushort),
            ("Sbz2", ctypes.c_ushort),
        ]

    acl = ctypes.cast(ppdacl, ctypes.POINTER(ACL)).contents
    for i in range(acl.AceCount):
        pace = ctypes.c_void_p()
        if not advapi32.GetAce(ppdacl, i, ctypes.byref(pace)):
            return False
        if pace.value is None:
            return False
        # ACE_HEADER: AceType (1), AceFlags (1), AceSize (2)
        ace_type = ctypes.c_ubyte.from_address(pace.value).value
        ace_size = ctypes.c_ushort.from_address(pace.value + 2).value
        if ace_size < 8:
            return False
        # Solo ACCESS_ALLOWED_ACE (0) nos interesa para concesion.
        if ace_type == 0:
            # ACCESS_ALLOWED_ACE: Mask at offset 4, SidStart at offset 8.
            mask = ctypes.c_ulong.from_address(pace.value + 4).value
            sid_in_ace = pace.value + 8
            if mask & write_bits:
                # Verificar si el SID esta en la lista de autorizados.
                authorized = False
                for allowed in allowed_sids:
                    if allowed.value is not None and advapi32.EqualSid(
                        allowed.value, sid_in_ace
                    ):
                        authorized = True
                        break
                if not authorized:
                    return False
    return True


def get_process_birth(pid: int) -> ProcessBirth | None:
    if sys.platform != "win32":
        return None
    try:
        kernel32 = ctypes.windll.kernel32
    except Exception:
        return None
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return None
    try:
        creation = ctypes.c_ulonglong(0)
        exit_time = ctypes.c_ulonglong(0)
        kernel_time = ctypes.c_ulonglong(0)
        user_time = ctypes.c_ulonglong(0)
        ok = kernel32.GetProcessTimes(
            handle,
            ctypes.byref(creation),
            ctypes.byref(exit_time),
            ctypes.byref(kernel_time),
            ctypes.byref(user_time),
        )
        if not ok:
            return None
        filetime = int(creation.value)
        # FILETIME 100ns desde 1601-01-01 UTC -> datetime.
        # Convertir a unix microseconds.
        unix_us = (filetime - 116444736000000000) // 10
        try:
            started = datetime.fromtimestamp(
                unix_us / 1_000_000, tz=timezone.utc
            ).isoformat()
        except (ValueError, OSError, OverflowError):
            started = None
        return ProcessBirth(pid=pid, filetime=filetime, started_at=started)
    finally:
        kernel32.CloseHandle(handle)


def token_for(
    registration: ServiceRegistration, birth: ProcessBirth, version: str
) -> str:
    payload = [
        1,
        registration.registration_id,
        registration.url,
        birth.pid,
        str(birth.filetime),
        version,
    ]
    raw = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return "aikit-owner-v1-" + digest


def read_registration(context: HostContext) -> ServiceRegistration:
    path = context.opencode_registration
    if not registration_trusted(path):
        raise ServiceError("registration_untrusted", "Registro no confiable.")
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_REGISTRATION_BYTES + 1)
    except OSError as exc:
        raise ServiceError(
            "registration_unavailable", "No se pudo leer el registro."
        ) from exc
    if len(raw) > MAX_REGISTRATION_BYTES:
        raise ServiceError("registration_too_large", "Registro demasiado grande.")
    data = parse_registration_bytes(raw)
    return validate_registration(data, context)


def process_birth_or_raise(pid: int) -> ProcessBirth:
    birth = get_process_birth(pid)
    if birth is None:
        raise ServiceError("process_identity_unavailable", "Nacimiento no disponible.")
    return birth
