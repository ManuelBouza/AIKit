#!/usr/bin/env python3
"""Adaptador mínimo para delegar una tarea acotada a OpenCode v2.

Este script no escribe transcripciones ni registros: OpenCode gestiona sus
propios registros y aquí solo se devuelve un resumen y el identificador de
sesión. Requiere Python 3.10+ y no usa dependencias externas.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from availability_state import AvailabilitySnapshot
from restrictions import configuration_is_restricted
from service_connection import BoundLaunch, ManagedBinding, discover_existing
from service_identity import HostContext, ServiceError, resolve_host_context
from session_store import Pricing, Role
from session_store import StoreError as AvailabilityStoreError

SKILL_DIR = Path(__file__).resolve().parent.parent
POLICY_PATH = SKILL_DIR / "policy.json"
MAX_TEXT = 4000
DEFAULT_TIMEOUT = 300.0
MAX_TIMEOUT = 3600.0
AGENTS = ("build", "plan")
TASK_PREFIX = "Tarea delegada (contenido literal):\n\n"
WINDOWS_SHIM_SUFFIXES = {".cmd", ".bat", ".ps1"}
VARIANT_SETTING_KEYS = ("reasoningEffort", "thinkingBudget")
POLICY_KEYS = ("prefer_free",)


class DelegateError(Exception):
    """Error controlado que se traduce a una salida JSON breve."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _is_openai_provider(provider: Any) -> bool:
    """El bloqueo depende solo del proveedor de conexión, no del modelo."""

    return isinstance(provider, str) and provider.strip().lower() == "openai"


def _reject_direct_openai(provider: str) -> None:
    if not _is_openai_provider(provider):
        return
    raise DelegateError(
        "provider_not_allowed",
        "El proveedor directo openai está bloqueado porque comparte la cuenta "
        "de Codex; usa un modelo GPT de otro proveedor conectado.",
    )


def _cap(text: Any, limit: int = MAX_TEXT) -> str:
    value = "" if text is None else str(text)
    return value[:limit]


def _error(code: str, message: str) -> dict[str, Any]:
    return {"status": "error", "code": code, "message": _cap(message)}


def load_policy(path: Path | str = POLICY_PATH) -> dict[str, bool]:
    """Carga la única preferencia admitida: preferir modelos gratuitos.

    Se rechazan las claves desconocidas para que la política no sugiera
    opciones que el adaptador no aplica. El motivo de selección es siempre
    obligatorio en `run` y no se configura aquí.
    """

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise DelegateError(
            "policy_unreadable", f"No se pudo leer la política {path}: {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DelegateError(
            "policy_invalid", f"La política {path} no es JSON válido: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise DelegateError("policy_invalid", "La política debe ser un objeto JSON.")

    unknown = sorted(str(key) for key in data if key not in POLICY_KEYS)
    if unknown:
        raise DelegateError(
            "policy_invalid",
            "policy.json admite solo prefer_free; claves desconocidas: "
            + ", ".join(unknown),
        )

    prefer_free = data.get("prefer_free")
    if not isinstance(prefer_free, bool):
        raise DelegateError(
            "policy_invalid",
            "policy.json requiere prefer_free booleano.",
        )
    return {"prefer_free": prefer_free}


def parse_model(model: str | None, variant: str | None) -> tuple[str, str | None]:
    """Separa el modelo base y una variante explícita, sin elegir un modelo."""

    if not isinstance(model, str) or not model.strip():
        raise DelegateError(
            "model_required", "Indica un modelo explícito con formato provider/model."
        )
    selected = model.strip()

    base, separator, embedded_variant = selected.partition("#")
    if separator and (
        not base
        or not embedded_variant
        or "#" in embedded_variant
        or not embedded_variant.strip()
    ):
        raise DelegateError(
            "invalid_model", f"Modelo con variante no válido: {selected}"
        )

    if variant is not None:
        if not isinstance(variant, str) or not variant.strip():
            raise DelegateError("invalid_variant", "La variante no puede estar vacía.")
        if separator:
            raise DelegateError(
                "variant_conflict",
                "Indica la variante en --model o con --variant, no en ambos.",
            )
        embedded_variant = variant.strip()

    if "/" not in base:
        raise DelegateError(
            "invalid_model", "El modelo debe tener el formato provider/model."
        )
    provider, name = base.split("/", 1)
    if not provider.strip() or not name.strip():
        raise DelegateError(
            "invalid_model", "El modelo debe tener el formato provider/model."
        )
    _reject_direct_openai(provider)

    clean_variant = embedded_variant.strip() if embedded_variant else None
    return base, clean_variant or None


def _validate_reason(reason: str | None) -> str:
    if not isinstance(reason, str) or not reason.strip():
        raise DelegateError(
            "reason_required",
            "Indica un motivo de selección no vacío para el modelo elegido.",
        )
    return reason.strip()


def resolve_opencode(which_result: str, is_windows: bool | None = None) -> str:
    """Resuelve el shim de npm en Windows al ejecutable real que lanza."""

    if is_windows is None:
        is_windows = os.name == "nt"
    if not is_windows:
        return which_result

    shim = Path(which_result)
    suffix = shim.suffix.lower()
    if suffix == ".exe":
        return which_result
    if suffix in WINDOWS_SHIM_SUFFIXES:
        candidate = (
            shim.parent / "node_modules" / "@opencode" / "cli" / "bin" / "opencode.exe"
        )
        if candidate.is_file():
            return str(candidate)
    raise DelegateError(
        "opencode_missing",
        "No se encontró opencode.exe nativo; en Windows solo se acepta un "
        "ejecutable .exe directo.",
    )


def find_opencode() -> str | None:
    found = shutil.which("opencode")
    if not found:
        return None
    return resolve_opencode(found)


def _kill_tree(process: subprocess.Popen[str]) -> None:
    """Mata el árbol del proceso propio; nunca procesos ajenos."""

    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/T", "/F", "/PID", str(process.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except Exception:
        try:
            process.kill()
        except Exception:
            pass


def run_process(
    argv: list[str], cwd: Path | str, timeout: float
) -> subprocess.CompletedProcess[str]:
    """Ejecuta sin shell y con grupo de procesos propio para poder cancelar."""

    kwargs: dict[str, Any] = {
        "cwd": str(cwd),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "shell": False,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        )
    else:
        kwargs["start_new_session"] = True

    try:
        process = subprocess.Popen(argv, **kwargs)
    except FileNotFoundError as exc:
        raise DelegateError(
            "opencode_missing", "No se encontró el ejecutable de OpenCode."
        ) from exc
    except OSError as exc:
        raise DelegateError(
            "opencode_failed", f"No se pudo iniciar OpenCode: {exc}"
        ) from exc

    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        _kill_tree(process)
        try:
            process.communicate(timeout=10)
        except Exception:
            pass
        raise DelegateError(
            "timeout",
            f"OpenCode excedió {timeout:g} s; se terminó su árbol de procesos.",
        ) from exc

    return subprocess.CompletedProcess(
        argv, process.returncode, stdout or "", stderr or ""
    )


def _validate_cwd(cwd: Path | str) -> Path:
    path = Path(cwd).expanduser()
    if not path.is_dir():
        raise DelegateError("invalid_cwd", f"El directorio no existe: {cwd}")
    return path.resolve()


def _read_task(task_file: Path | str) -> str:
    path = Path(task_file).expanduser()
    if not path.is_file():
        raise DelegateError(
            "task_not_found", f"No existe el archivo de tarea: {task_file}"
        )
    try:
        task = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise DelegateError(
            "task_unreadable", f"No se pudo leer la tarea: {exc}"
        ) from exc
    task = task.strip()
    if not task:
        raise DelegateError("empty_task", "El archivo de tarea está vacío.")
    return task


def _validate_task_text(task: str) -> str:
    """Acepta la tarea en memoria sin alterar su contenido literal."""

    if not isinstance(task, str) or not task.strip():
        raise DelegateError("empty_task", "La tarea está vacía.")
    return task


def _validate_timeout(timeout: float) -> float:
    try:
        value = float(timeout)
    except (TypeError, ValueError) as exc:
        raise DelegateError("invalid_timeout", "El timeout debe ser numérico.") from exc
    if not math.isfinite(value) or value <= 0:
        raise DelegateError(
            "invalid_timeout", "El timeout debe ser un número finito mayor que cero."
        )
    if value > MAX_TIMEOUT:
        raise DelegateError(
            "invalid_timeout", f"El timeout no puede superar {MAX_TIMEOUT:g} s."
        )
    return value


def _is_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _cost_rates(cost: Any) -> list[dict[str, Any]]:
    if isinstance(cost, dict):
        return [cost]
    if isinstance(cost, list):
        return [rate for rate in cost if isinstance(rate, dict)]
    return []


def _pricing_tier(rate: dict[str, Any]) -> dict[str, Any] | None:
    """Sanea una tarifa y su nivel; no expone campos ajenos al esquema."""

    pricing: dict[str, Any] = {}
    for key in ("input", "output"):
        value = rate.get(key)
        if _is_number(value):
            pricing[key] = value
    cache = rate.get("cache")
    if isinstance(cache, dict):
        clean_cache = {
            key: cache[key] for key in ("read", "write") if _is_number(cache.get(key))
        }
        if clean_cache:
            pricing["cache"] = clean_cache
    tier = rate.get("tier")
    if (
        isinstance(tier, dict)
        and tier.get("type") == "context"
        and _is_number(tier.get("size"))
    ):
        pricing["tier"] = {"type": "context", "size": tier["size"]}
    return pricing or None


def _pricing_tiers(cost: Any) -> list[dict[str, Any]] | None:
    """Devuelve todas las tarifas saneadas, en el orden del catálogo."""

    tiers: list[dict[str, Any]] = []
    for rate in _cost_rates(cost):
        clean = _pricing_tier(rate)
        if clean is not None:
            tiers.append(clean)
    return tiers or None


def _pricing(cost: Any) -> dict[str, Any] | None:
    """Mantiene la primera tarifa como precio base para compatibilidad."""

    tiers = _pricing_tiers(cost)
    return tiers[0] if tiers else None


def _free_candidate(provider: str, cost: Any) -> bool | None:
    """Solo es candidato si las tarifas conocidas son cero y no es OpenAI."""

    if _is_openai_provider(provider):
        return False
    rates = _cost_rates(cost)
    if not rates:
        return None
    unknown = False
    for rate in rates:
        input_price = rate.get("input")
        output_price = rate.get("output")
        if not _is_number(input_price) or not _is_number(output_price):
            unknown = True
            continue
        if input_price != 0 or output_price != 0:
            return False
        cache = rate.get("cache")
        if isinstance(cache, dict):
            for key in ("read", "write"):
                value = cache.get(key)
                if _is_number(value):
                    if value != 0:
                        return False
                elif value is not None:
                    unknown = True
    return None if unknown else True


def _variants(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        variant_id: object
        settings: dict[str, Any]
        if isinstance(item, str):
            variant_id = item.strip()
            settings = {}
        elif isinstance(item, dict):
            variant_id = item.get("id")
            raw_settings = item.get("settings")
            settings = raw_settings if isinstance(raw_settings, dict) else {}
        else:
            continue
        if not isinstance(variant_id, str) or not variant_id.strip():
            continue
        variant_id = variant_id.strip()
        if variant_id in seen:
            continue
        seen.add(variant_id)
        entry: dict[str, Any] = {"id": variant_id}
        for key in VARIANT_SETTING_KEYS:
            setting = settings.get(key)
            if isinstance(setting, str) and setting.strip():
                entry[key] = setting.strip()
            elif _is_number(setting):
                entry[key] = setting
        result.append(entry)
    return result


def _capabilities(value: Any) -> tuple[bool | None, list[str], list[str]]:
    capabilities = value if isinstance(value, dict) else {}
    tools = capabilities.get("tools")
    if not isinstance(tools, bool):
        tools = None
    modalities: list[list[str]] = []
    for key in ("input", "output"):
        raw = capabilities.get(key)
        modalities.append(
            [item for item in raw if isinstance(item, str)]
            if isinstance(raw, list)
            else []
        )
    return tools, modalities[0], modalities[1]


def _limits(value: Any) -> dict[str, int | float] | None:
    limits = value if isinstance(value, dict) else {}
    clean = {
        key: limits[key]
        for key in ("context", "input", "output")
        if _is_number(limits.get(key))
    }
    return clean or None


def _model_record(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, dict) or item.get("enabled") is not True:
        return None
    provider = item.get("providerID")
    model_id = item.get("id")
    if not isinstance(provider, str) or not provider.strip():
        return None
    if not isinstance(model_id, str) or not model_id.strip():
        return None
    provider = provider.strip()
    if _is_openai_provider(provider):
        return None
    model_id = model_id.strip()
    full = f"{provider}/{model_id}"
    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        name = full
    tools, input_modalities, output_modalities = _capabilities(item.get("capabilities"))
    variants = _variants(item.get("variants"))
    cost = item.get("cost")
    return {
        "model": full,
        "name": name.strip(),
        "pricing": _pricing(cost),
        "pricing_tiers": _pricing_tiers(cost),
        "variants": variants,
        "variant_ids": [variant["id"] for variant in variants],
        "tools": tools,
        "input": input_modalities,
        "output": output_modalities,
        "limits": _limits(item.get("limit")),
        "free_candidate": _free_candidate(provider, cost),
        "may_use_openai_quota": _is_openai_provider(provider),
    }


def _public_model(model: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "model",
        "name",
        "pricing",
        "pricing_tiers",
        "variants",
        "tools",
        "input",
        "output",
        "limits",
        "free_candidate",
        "may_use_openai_quota",
    )
    return {key: model[key] for key in keys}


def _project_key(path: Path) -> str:
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path.absolute()
    return os.path.normcase(os.path.normpath(str(resolved)))


def _catalog_from_payload(payload: object, project: Path) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise DelegateError(
            "catalog_unavailable",
            "El servicio OpenCode no devolvió un catálogo JSON válido.",
        )
    location = payload.get("location")
    directory = location.get("directory") if isinstance(location, dict) else None
    if not isinstance(directory, str) or not directory:
        raise DelegateError(
            "catalog_unavailable",
            "El catálogo no indicó la ubicación del proyecto consultado.",
        )
    location_path = Path(directory)
    if not location_path.is_absolute() or _project_key(location_path) != _project_key(
        project
    ):
        raise DelegateError(
            "project_mismatch",
            "El catálogo del servicio no corresponde al proyecto solicitado.",
        )

    data = payload.get("data")
    if not isinstance(data, list):
        raise DelegateError(
            "catalog_unavailable",
            "El catálogo no contiene la lista 'data' esperada.",
        )

    models: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in data:
        model = _model_record(item)
        if model is None or model["model"] in seen:
            continue
        seen.add(model["model"])
        models.append(model)
    return models


def _pricing_label(selected: dict[str, Any]) -> Pricing:
    free = selected.get("free_candidate")
    if free is True:
        return "free"
    if free is False:
        return "paid"
    return "unknown"


def _extract_error(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, dict):
        for key in ("message", "detail"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        data = value.get("data")
        if isinstance(data, dict):
            for key in ("message", "detail"):
                candidate = data.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    return candidate.strip()
        nested = value.get("error")
        if nested is not None and nested is not value:
            return _extract_error(nested)
        name = value.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return "OpenCode informó un error."


def parse_events(
    stdout: str,
) -> tuple[str, str | None, float | None, list[str]]:
    """Extrae resumen, sesión, coste informado y errores de eventos JSONL."""

    summary_parts: list[str] = []
    session: str | None = None
    costs: list[float] = []
    errors: list[str] = []

    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue

        raw_part = event.get("part")
        part = raw_part if isinstance(raw_part, dict) else {}
        candidate_session = (
            event.get("sessionID")
            or event.get("sessionId")
            or part.get("sessionID")
            or part.get("sessionId")
        )
        if isinstance(candidate_session, str) and candidate_session:
            session = candidate_session

        event_type = event.get("type")
        error_value = None
        if event_type == "error":
            error_value = event.get("error", event)
        elif isinstance(event.get("error"), (dict, str)):
            error_value = event.get("error")
        elif isinstance(part.get("error"), (dict, str)):
            error_value = part.get("error")
        if error_value is not None:
            errors.append(_extract_error(error_value))

        if event_type == "text":
            text = part.get("text")
            if text is None:
                text = event.get("text")
            if isinstance(text, str) and text:
                summary_parts.append(text)
        elif event_type in ("message", "assistant"):
            text = part.get("text") or event.get("text") or event.get("content")
            if isinstance(text, str) and text:
                summary_parts.append(text)

        if event_type in ("step_finish", "step-finish"):
            cost = part.get("cost", event.get("cost"))
            if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                costs.append(float(cost))

    summary = "\n".join(part for part in summary_parts if part).strip()
    cost = sum(costs) if costs else None
    return summary, session, cost, errors


def _free_limit_reached(stdout: str) -> bool:
    """Reconoce la señal estructurada de cuota sin confiar en texto del modelo."""
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or event.get("type") != "error":
            continue
        error = event.get("error")
        if isinstance(error, dict) and error.get("type") == "provider.free-limit":
            return True
    return False


def _build_bound_command(
    exe: str, url: str, model: str, agent: str, task: str
) -> list[str]:
    """Construye el envío explícito al servicio ya verificado."""

    return [
        exe,
        "run",
        "--model",
        model,
        "--agent",
        agent,
        "--server",
        url,
        "--format",
        "json",
        "--",
        TASK_PREFIX + task,
    ]


def _service_failure(exc: ServiceError) -> DelegateError:
    code = exc.code
    if code in {
        "transport_error",
        "network_error",
        "timeout",
        "invalid_response",
        "invalid_url",
        "redirect",
        "response_too_large",
        "response_too_deep",
        "binding_closed",
    } or code.startswith("http_"):
        code = "service_unavailable"
    messages = {
        "service_unavailable": (
            "El servicio OpenCode existente no está disponible; no se ha iniciado "
            "otro ni se ha enviado la tarea."
        ),
        "owner_mismatch": (
            "La identidad del servicio OpenCode cambió; no se reenvía la tarea."
        ),
        "version_mismatch": (
            "El servicio OpenCode existente no tiene la versión soportada."
        ),
        "host_context_unavailable": (
            "No hay un contexto de host OpenCode disponible para esta sesión."
        ),
        "registration_untrusted": (
            "El registro del servicio OpenCode no es confiable."
        ),
        "process_identity_unavailable": (
            "No se pudo acreditar la identidad del servicio OpenCode."
        ),
    }
    return DelegateError(
        code, messages.get(code, "No se pudo usar el servicio OpenCode existente.")
    )


def run_task(
    cwd: Path | str,
    task_file: Path | str,
    model: str | None = None,
    variant: str | None = None,
    reason: str | None = None,
    agent: str = "build",
    timeout: float = DEFAULT_TIMEOUT,
    *,
    role: Role = "implementer",
    _wait_seconds: float | None = None,
) -> dict[str, Any]:
    """Ejecuta un único intento leyendo la tarea de un archivo."""

    return _run_core(
        cwd=cwd,
        task_loader=lambda: _read_task(task_file),
        model=model,
        variant=variant,
        reason=reason,
        agent=agent,
        timeout=timeout,
        role=role,
        _wait_seconds=_wait_seconds,
    )


def run_text_task(
    cwd: Path | str,
    task: str,
    model: str | None = None,
    variant: str | None = None,
    reason: str | None = None,
    agent: str = "build",
    timeout: float = DEFAULT_TIMEOUT,
    *,
    role: Role = "implementer",
    _wait_seconds: float | None = None,
) -> dict[str, Any]:
    """Ejecuta un único intento con la tarea ya en memoria."""

    return _run_core(
        cwd=cwd,
        task_loader=lambda: _validate_task_text(task),
        model=model,
        variant=variant,
        reason=reason,
        agent=agent,
        timeout=timeout,
        role=role,
        _wait_seconds=_wait_seconds,
    )


def _preflight_remaining(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise ServiceError("timeout", "Preflight agotado.")
    return remaining


def _availability_snapshot(
    binding: ManagedBinding,
    host: HostContext,
    project: Path,
    config: object,
    deadline: float,
) -> AvailabilitySnapshot:
    from availability_refresh import coalesced_refresh
    from availability_state import configuration_signature, read_snapshot, state_path

    signature = configuration_signature(config)
    project_key = _project_key(project)

    def valid(snapshot: AvailabilitySnapshot | None) -> bool:
        return snapshot is not None and any(
            item.project_key == project_key
            and item.config_signature == signature
            and item.service_version == binding.registration.version
            and {"config.get", "model.catalog"}.issubset(item.capabilities)
            for item in snapshot.catalog_contexts
        )

    try:
        snapshot = read_snapshot(state_path(host.aikit_state))
        if not valid(snapshot):
            result = coalesced_refresh(
                state_path(host.aikit_state),
                binding,
                project,
                _preflight_remaining(deadline),
                force=True,
                context_signature=signature,
                service_version=binding.registration.version,
            )
            snapshot = result.snapshot
            if not valid(snapshot):
                code = (
                    "catalog_capability_unavailable"
                    if "catalog_unavailable" in result.errors
                    else "availability_context_unavailable"
                )
                raise DelegateError(
                    code,
                    "La tabla no acredita el contrato de catalogo requerido para este contexto.",
                )
        if snapshot is None:
            raise DelegateError(
                "availability_state_unavailable", "No hay tabla acreditada."
            )
        return snapshot
    except (AvailabilityStoreError, OSError, ValueError) as exc:
        raise DelegateError(
            "availability_state_unavailable",
            "No se pudo consultar o actualizar la tabla compartida.",
        ) from exc


def _prepare_run(
    cwd: Path | str,
    task_loader: Callable[[], str],
    model: str | None,
    variant: str | None,
    reason: str | None,
    agent: str,
    timeout: float,
    *,
    role: Role = "implementer",
    context: HostContext | None = None,
) -> BoundLaunch:
    """Prepara un envío validado contra el servicio existente."""

    base_model, selected_variant = parse_model(model, variant)
    clean_reason = _validate_reason(reason)
    project = _validate_cwd(cwd)
    task = _validate_task_text(task_loader())
    try:
        task_size = len(task.encode("utf-8"))
    except UnicodeError:
        raise DelegateError("invalid_task", "La tarea no es UTF8 valida.") from None
    if task_size > 1024 * 1024:
        raise DelegateError(
            "task_too_large", "La tarea excede el limite del supervisor."
        )
    load_policy()
    if agent not in AGENTS:
        raise DelegateError("invalid_agent", f"Agente no permitido: {agent}")
    if role not in ("implementer", "reviewer"):
        raise DelegateError("invalid_role", f"Rol no permitido: {role}")
    seconds = _validate_timeout(timeout)

    binding: ManagedBinding | None = None
    try:
        host = context if context is not None else resolve_host_context()
        deadline = time.monotonic() + min(10.0, seconds)
        binding = discover_existing(host, timeout=_preflight_remaining(deadline))
        config = binding.config_sources(project, timeout=_preflight_remaining(deadline))
        if not configuration_is_restricted(config):
            raise DelegateError(
                "unsafe_configuration",
                "La configuración efectiva no acredita el bloqueo del proveedor "
                "directo openai ni de la subdelegación interna de OpenCode.",
            )

        from availability_policy import eligible_for_attempt
        from availability_state import admission_for, model_entry

        snapshot = _availability_snapshot(binding, host, project, config, deadline)
        project_key = _project_key(project)
        entry = model_entry(snapshot, project_key, base_model)
        if entry is None or entry.context_key != project_key:
            raise DelegateError(
                "model_unavailable",
                f"El modelo no aparece disponible en la tabla actual: {base_model}",
            )
        if not eligible_for_attempt(entry):
            raise DelegateError(
                "model_unavailable",
                f"El modelo no está disponible actualmente: {base_model}",
            )
        if (
            selected_variant is not None
            and selected_variant not in entry.metadata.variants
        ):
            available = ", ".join(entry.metadata.variants) or "ninguna"
            raise DelegateError(
                "invalid_variant",
                f"La variante '{selected_variant}' no existe para {base_model}. "
                f"Variantes disponibles: {available}.",
            )

        selected = {"free_candidate": entry.metadata.free_candidate}

        exe = find_opencode()
        if not exe:
            raise DelegateError(
                "opencode_missing",
                "No se encontró 'opencode' en PATH. Instala la CLI v2 o revisa PATH.",
            )
        selected_model = base_model + (
            "#" + selected_variant if selected_variant else ""
        )
        return BoundLaunch(
            binding=binding,
            project=project,
            argv=_build_bound_command(
                exe, binding.registration.url, selected_model, agent, task
            ),
            model=base_model,
            variant=selected_variant,
            reason=clean_reason,
            agent=agent,
            timeout=seconds,
            role=role,
            task=task,
            pricing=_pricing_label(selected),
            admission=admission_for(
                snapshot, project_key, base_model, selected_variant
            ),
        )
    except ServiceError as exc:
        if binding is not None:
            binding.close()
        raise _service_failure(exc) from None
    except BaseException:
        if binding is not None:
            binding.close()
        raise


def _run_core(
    cwd: Path | str,
    task_loader: Callable[[], str],
    model: str | None,
    variant: str | None,
    reason: str | None,
    agent: str,
    timeout: float,
    *,
    role: Role = "implementer",
    _wait_seconds: float | None = None,
) -> dict[str, Any]:
    """Núcleo común de ejecución: valida antes de tocar procesos."""

    try:
        prepared = _prepare_run(
            cwd,
            task_loader,
            model,
            variant,
            reason,
            agent,
            timeout,
            role=role,
        )
        import bound_execution

        wait = prepared.timeout if _wait_seconds is None else _wait_seconds
        return bound_execution.execute_bound(
            prepared,
            context=prepared.binding.context,
            wait_seconds=wait,
        )
    except DelegateError as exc:
        return _error(exc.code, exc.message)
    except ServiceError as exc:
        failure = _service_failure(exc)
        return _error(failure.code, failure.message)
    except (AvailabilityStoreError, OSError):
        return _error(
            "availability_state_unavailable",
            "No se pudo consultar el estado compartido.",
        )


def doctor(
    cwd: Path | str,
    timeout: float = DEFAULT_TIMEOUT,
    model: str | None = None,
) -> dict[str, Any]:
    """Consulta el catálogo del servicio existente, sin exigir certificado."""

    binding: ManagedBinding | None = None
    try:
        project = _validate_cwd(cwd)
        seconds = _validate_timeout(timeout)
        filter_model: str | None = None
        if model is not None:
            if not isinstance(model, str) or not model.strip():
                raise DelegateError(
                    "invalid_model", "El filtro --model no puede estar vacío."
                )
            filter_model = model.strip().partition("#")[0].strip()
            if not filter_model:
                raise DelegateError(
                    "invalid_model", "El filtro --model no puede estar vacío."
                )
            if "/" in filter_model:
                _reject_direct_openai(filter_model.partition("/")[0])
        load_policy()

        host = resolve_host_context()
        deadline = time.monotonic() + min(10.0, seconds)
        binding = discover_existing(host, timeout=_preflight_remaining(deadline))
        config = binding.config_sources(project, timeout=_preflight_remaining(deadline))
        project_key = _project_key(project)
        snapshot = _availability_snapshot(binding, host, project, config, deadline)
        catalog: list[dict[str, Any]] = []
        if snapshot is not None:
            from availability_state import model_entry

            candidates = snapshot.project_models.get(project_key, snapshot.models)
            for model_name in candidates:
                entry = model_entry(snapshot, project_key, model_name)
                if entry is None:
                    continue
                if entry.context_key != project_key:
                    continue
                meta = entry.metadata
                tiers = [
                    {
                        "input": tier.input,
                        "output": tier.output,
                        "cache": {"read": tier.cache_read, "write": tier.cache_write},
                        "tier": (
                            {"type": "context", "size": tier.context_size}
                            if tier.context_size is not None
                            else None
                        ),
                    }
                    for tier in meta.pricing
                ]
                # Eliminar tiers sin tier para mantener la forma saneada.
                for tier in tiers:
                    if tier["tier"] is None:
                        del tier["tier"]
                catalog.append(
                    {
                        "model": meta.model,
                        "name": meta.name,
                        "pricing": tiers[0] if tiers else None,
                        "pricing_tiers": tiers or None,
                        "variants": [
                            {"id": variant_id} for variant_id in meta.variants
                        ],
                        "tools": meta.tools,
                        "input": list(meta.input_modalities),
                        "output": list(meta.output_modalities),
                        "limits": (
                            {
                                key: value
                                for key, value in {
                                    "context": meta.context_limit,
                                    "input": meta.input_limit,
                                    "output": meta.output_limit,
                                }.items()
                                if value is not None
                            }
                            or None
                        ),
                        "free_candidate": meta.free_candidate,
                        "may_use_openai_quota": meta.may_use_openai_quota,
                    }
                )
        total = len(catalog)

        def _priority_key(item: dict[str, Any]) -> tuple[int, str]:
            free = item.get("free_candidate")
            paid = free is False
            go = str(item.get("model", "")).startswith("opencode-go/")
            if paid and go:
                return (0, str(item.get("model", "")).lower())
            if paid:
                return (1, str(item.get("model", "")).lower())
            if free is True:
                return (2, str(item.get("model", "")).lower())
            return (3, str(item.get("model", "")).lower())

        policy = load_policy()
        if policy.get("prefer_free") is True:
            catalog.sort(
                key=lambda item: (
                    0
                    if item.get("free_candidate") is True
                    else 1
                    if str(item.get("model", "")).startswith("opencode-go/")
                    else 2
                    if item.get("free_candidate") is None
                    else 3,
                    str(item.get("model", "")).lower(),
                )
            )
        else:
            catalog.sort(key=_priority_key)

        if filter_model is not None:
            catalog = [item for item in catalog if item["model"] == filter_model]

        public_terms = snapshot.public_terms if snapshot is not None else ()
        return {
            "status": "ok",
            "version": binding.registration.version,
            "catalog_count": total,
            "catalog": catalog,
            "price_zero_count": sum(
                1 for item in catalog if item.get("free_candidate") is True
            ),
            "conditional_access_count": sum(
                1 for term in public_terms if term.access_kind == "conditional_access"
            ),
            "public_terms_count": len(public_terms),
            "listed_price_zero_count": sum(
                1 for item in catalog if item.get("free_candidate") is True
            ),
        }
    except ServiceError as exc:
        failure = _service_failure(exc)
        return _error(failure.code, failure.message)
    except AvailabilityStoreError:
        return _error(
            "availability_state_unavailable",
            "No se pudo consultar el estado compartido.",
        )
    except DelegateError as exc:
        return _error(exc.code, exc.message)
    finally:
        if binding is not None:
            binding.close()


def availability_status(cwd: Path | str) -> dict[str, Any]:
    """Solo estado del host configurado; nunca adivina una ruta de proyecto."""
    from availability_state import _snapshot_to_json, read_snapshot, state_path

    try:
        _validate_cwd(cwd)
        path = state_path(resolve_host_context().aikit_state)
        snapshot = read_snapshot(path)
        return {
            "status": "ok",
            "state_path": str(path),
            "exists": snapshot is not None,
            "snapshot": _snapshot_to_json(snapshot) if snapshot is not None else None,
        }
    except ServiceError as exc:
        return _error(exc.code, "No hay un contexto de host configurado.")
    except (AvailabilityStoreError, OSError, ValueError):
        return _error(
            "availability_state_unavailable", "No se pudo leer la tabla compartida."
        )
    except DelegateError as exc:
        return _error(exc.code, exc.message)


def availability_refresh_command(
    cwd: Path | str, timeout: float = DEFAULT_TIMEOUT
) -> dict[str, Any]:
    """Refresca la tabla usando solo un servicio ya registrado."""

    project = _validate_cwd(cwd)
    seconds = _validate_timeout(timeout)
    deadline = time.monotonic() + min(10.0, seconds)
    binding = None
    try:
        host = resolve_host_context()
        binding = discover_existing(host, timeout=_preflight_remaining(deadline))
        from availability_refresh import coalesced_refresh
        from availability_state import configuration_signature, state_path

        config = binding.config_sources(project, timeout=_preflight_remaining(deadline))
        result = coalesced_refresh(
            state_path(host.aikit_state),
            binding,
            project,
            _preflight_remaining(deadline),
            force=True,
            context_signature=configuration_signature(config),
            service_version=binding.registration.version,
        )
        return {
            "status": "ok",
            "refreshed": result.refreshed,
            "generation": result.generation,
            "errors": list(result.errors),
            "changes": result.changes,
            "added": list(result.added),
            "removed": list(result.removed),
            "changed": list(result.changed),
            "unchanged": list(result.unchanged),
        }
    except ServiceError as exc:
        failure = _service_failure(exc)
        return _error(failure.code, failure.message)
    except AvailabilityStoreError:
        return _error(
            "availability_state_unavailable",
            "No se pudo consultar el estado compartido.",
        )
    except DelegateError as exc:
        return _error(exc.code, exc.message)
    finally:
        if binding is not None:
            binding.close()


def availability_import_public_terms_command(
    cwd: Path | str,
    file: Path | str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    replace: bool = False,
) -> dict[str, Any]:
    """Incorpora hechos públicos validados al estado compartido."""
    try:
        _validate_cwd(cwd)
        state_path_value = resolve_host_context().aikit_state
    except ServiceError as exc:
        return _error(exc.code, "No hay un contexto de host configurado.")
    except DelegateError as exc:
        return _error(exc.code, exc.message)
    path = Path(file)
    try:
        from availability_public_terms import (
            import_public_terms_state,
            read_public_terms_file,
        )
        from availability_state import state_path

        terms = read_public_terms_file(path)
        snapshot = import_public_terms_state(
            state_path(state_path_value), terms, replace=replace
        )
        return {
            "status": "ok",
            "imported": len(terms),
            "generation": snapshot.generation,
            "state_path": str(state_path(state_path_value)),
        }
    except (OSError, ValueError) as exc:
        return _error("public_terms_invalid", str(exc))
    except AvailabilityStoreError:
        return _error(
            "availability_state_unavailable",
            "No se pudo actualizar el estado compartido.",
        )
    except ServiceError as exc:
        return _error(exc.code, exc.message)
    except DelegateError as exc:
        return _error(exc.code, exc.message)


def _positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("debe ser un número") from exc
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("debe ser un número finito mayor que cero")
    if number > MAX_TIMEOUT:
        raise argparse.ArgumentTypeError(f"no puede superar {MAX_TIMEOUT:g} segundos")
    return number


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Delega una tarea acotada a un modelo conectado de OpenCode v2."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser(
        "doctor", help="Muestra versión y catálogo compacto."
    )
    doctor_parser.add_argument("--cwd", required=True)
    doctor_parser.add_argument("--model", help="Filtra por modelo base provider/model.")
    doctor_parser.add_argument(
        "--timeout", type=_positive_float, default=DEFAULT_TIMEOUT
    )

    run_parser = subparsers.add_parser(
        "run", help="Ejecuta una tarea con un único intento."
    )
    run_parser.add_argument("--cwd", required=True)
    run_parser.add_argument("--task-file", required=True)
    run_parser.add_argument(
        "--model", help="Modelo explícito provider/model[#variant]."
    )
    run_parser.add_argument("--variant", help="Variante real del modelo, sin '#'.")
    run_parser.add_argument("--reason", help="Motivo de selección no vacío.")
    run_parser.add_argument("--agent", choices=AGENTS, default="build")
    run_parser.add_argument(
        "--role",
        choices=("implementer", "reviewer"),
        default="implementer",
        help="Rol explícito del intento; no se deduce de --agent.",
    )
    run_parser.add_argument("--timeout", type=_positive_float, default=DEFAULT_TIMEOUT)

    availability_parser = subparsers.add_parser(
        "availability", help="Inspecciona o refresca la tabla local de disponibilidad."
    )
    availability_subparsers = availability_parser.add_subparsers(
        dest="availability_command", required=True
    )
    status_parser = availability_subparsers.add_parser(
        "status", help="Lee la tabla local sin consultas externas."
    )
    status_parser.add_argument("--cwd", required=True)
    status_parser.add_argument("--json", action="store_true")
    refresh_parser = availability_subparsers.add_parser(
        "refresh", help="Refresca la tabla usando el servicio ya registrado."
    )
    refresh_parser.add_argument("--cwd", required=True)
    refresh_parser.add_argument("--json", action="store_true")
    refresh_parser.add_argument(
        "--timeout", type=_positive_float, default=DEFAULT_TIMEOUT
    )

    for command_name, help_text in (
        ("import", "Incorpora hechos públicos validados al estado compartido."),
        (
            "import-public-terms",
            "Incorpora hechos públicos validados al estado compartido.",
        ),
    ):
        sub = availability_subparsers.add_parser(command_name, help=help_text)
        sub.add_argument("--cwd", required=True)
        sub.add_argument("--file", required=True)
        sub.add_argument("--json", action="store_true")
        sub.add_argument("--replace", action="store_true")
        sub.add_argument("--timeout", type=_positive_float, default=DEFAULT_TIMEOUT)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "doctor":
            payload = doctor(cwd=args.cwd, timeout=args.timeout, model=args.model)
        elif args.command == "availability":
            if args.availability_command == "status":
                payload = availability_status(cwd=args.cwd)
            elif args.availability_command in {
                "import",
                "import-public-terms",
            }:
                payload = availability_import_public_terms_command(
                    cwd=args.cwd,
                    file=args.file,
                    timeout=args.timeout,
                    replace=getattr(args, "replace", False),
                )
            else:
                payload = availability_refresh_command(
                    cwd=args.cwd, timeout=args.timeout
                )
        else:
            payload = run_task(
                cwd=args.cwd,
                task_file=args.task_file,
                model=args.model,
                variant=args.variant,
                reason=args.reason,
                agent=args.agent,
                timeout=args.timeout,
                role=args.role,
            )
    except Exception as exc:  # noqa: BLE001 - la CLI siempre devuelve JSON breve
        payload = _error("internal_error", str(exc))

    sys.stdout.write(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":")) + "\n"
    )
    return 0 if payload.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
