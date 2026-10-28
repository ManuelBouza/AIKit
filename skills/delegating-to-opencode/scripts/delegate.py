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
import re
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent.parent
POLICY_PATH = SKILL_DIR / "policy.json"
MAX_TEXT = 4000
DEFAULT_TIMEOUT = 300.0
MAX_TIMEOUT = 3600.0
AGENTS = ("build", "plan")
TASK_PREFIX = "Tarea delegada (contenido literal):\n\n"
WINDOWS_SHIM_SUFFIXES = {".cmd", ".bat", ".ps1"}
CATALOG_LINE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.:/@+#-]+$")


class DelegateError(Exception):
    """Error controlado que se traduce a una salida JSON breve."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _cap(text: Any, limit: int = MAX_TEXT) -> str:
    value = "" if text is None else str(text)
    return value[:limit]


def _error(code: str, message: str) -> dict[str, Any]:
    return {"status": "error", "code": code, "message": _cap(message)}


def load_policy(path: Path | str = POLICY_PATH) -> dict[str, Any]:
    """Carga y valida la lista cerrada de modelos gratuitos permitidos."""

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

    default_model = data.get("default_model")
    allowed = data.get("allowed_models")
    if not isinstance(default_model, str) or not isinstance(allowed, list) or not allowed:
        raise DelegateError(
            "policy_invalid", "policy.json requiere default_model y allowed_models."
        )
    if len(set(allowed)) != len(allowed):
        raise DelegateError("policy_invalid", "allowed_models contiene duplicados.")

    for model in allowed:
        if not isinstance(model, str):
            raise DelegateError("policy_invalid", "Cada modelo permitido debe ser texto.")
        if not model.startswith("opencode/") or not model.endswith("-free"):
            raise DelegateError(
                "policy_invalid",
                f"Modelo no gratuito o proveedor no permitido en la política: {model}",
            )
        if "#" in model:
            raise DelegateError(
                "policy_invalid",
                f"La variante no forma parte de allowed_models: {model}",
            )

    if default_model not in allowed:
        raise DelegateError(
            "policy_invalid", "default_model debe pertenecer a allowed_models."
        )
    return data


def parse_model(
    model: str | None, variant: str | None, policy: dict[str, Any]
) -> tuple[str, str]:
    """Devuelve (modelo base, modelo con variante opcional)."""

    selected = (model or policy["default_model"]).strip()
    if not selected:
        raise DelegateError("invalid_model", "El modelo no puede estar vacío.")

    base, separator, embedded_variant = selected.partition("#")
    if separator and (not base or not embedded_variant or "#" in embedded_variant):
        raise DelegateError("invalid_model", f"Modelo con variante no válido: {selected}")

    if variant is not None:
        clean_variant = variant.strip()
        if not clean_variant:
            raise DelegateError("invalid_variant", "La variante no puede estar vacía.")
        if separator:
            raise DelegateError(
                "variant_conflict",
                "Indica la variante en --model o con --variant, no en ambos.",
            )
        embedded_variant = clean_variant

    if "/" not in base:
        raise DelegateError(
            "invalid_model", "El modelo debe tener el formato provider/model."
        )
    provider, _name = base.split("/", 1)
    if provider != "opencode":
        raise DelegateError(
            "provider_not_allowed",
            f"Solo se permite el proveedor opencode; recibido: {provider}",
        )
    if base not in policy["allowed_models"]:
        raise DelegateError(
            "model_not_allowed",
            f"El modelo no pertenece a allowed_models: {base}",
        )

    full = base + ("#" + embedded_variant if embedded_variant else "")
    return base, full


def validate_project_policy(cwd: Path | str) -> None:
    """Exige una política del proyecto que bloquee OpenAI y subagentes."""

    path = Path(cwd) / "opencode.json"
    if not path.is_file():
        raise DelegateError(
            "policy_missing",
            "Falta opencode.json en el directorio destino. Crea una política que "
            "deniegue provider.use '*' y tool.use 'subagent:*', y permita solo "
            "'opencode'. Consulta README.md y la skill.",
        )
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DelegateError(
            "policy_invalid", f"No se pudo leer la política del proyecto: {exc}"
        ) from exc

    policies = config.get("policies") if isinstance(config, dict) else None
    if not isinstance(policies, list):
        raise DelegateError(
            "policy_invalid", "opencode.json debe incluir una lista 'policies'."
        )

    def ordered(action: str, effect: str) -> list[tuple[int, str]]:
        found: list[tuple[int, str]] = []
        for index, entry in enumerate(policies):
            if not isinstance(entry, dict):
                continue
            if entry.get("action") != action or entry.get("effect") != effect:
                continue
            resource = entry.get("resource")
            if isinstance(resource, str):
                found.append((index, resource))
        return found

    deny_any_index = next(
        (index for index, resource in ordered("provider.use", "deny") if resource == "*"),
        None,
    )
    if deny_any_index is None:
        raise DelegateError(
            "policy_invalid",
            "La política debe incluir provider.use '*' con efecto deny antes de "
            "permitir 'opencode'. No se acepta 'openai' ni 'openai/*' como sustituto.",
        )

    allow_opencode_index: int | None = None
    for index, resource in ordered("provider.use", "allow"):
        if resource != "opencode":
            raise DelegateError(
                "policy_invalid",
                "La política solo puede permitir el proveedor 'opencode'; no se "
                "aceptan allow de otros proveedores ni comodines.",
            )
        if allow_opencode_index is None:
            allow_opencode_index = index

    if allow_opencode_index is None or allow_opencode_index < deny_any_index:
        raise DelegateError(
            "policy_invalid",
            "La regla provider.use '*' (deny) debe aparecer antes del allow de "
            "'opencode'.",
        )

    if ordered("tool.use", "allow"):
        raise DelegateError(
            "policy_invalid",
            "La política no puede permitir tool.use en este perfil porque podría "
            "habilitar 'subagent:*'.",
        )

    denies_subagents = any(
        resource == "subagent:*"
        for _index, resource in ordered("tool.use", "deny")
    )
    if not denies_subagents:
        raise DelegateError(
            "policy_invalid",
            "La política debe denegar tool.use 'subagent:*'.",
        )


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
            shim.parent
            / "node_modules"
            / "@opencode"
            / "cli"
            / "bin"
            / "opencode.exe"
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
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/T", "/F", "/PID", str(process.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
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
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    try:
        process = subprocess.Popen(argv, **kwargs)
    except FileNotFoundError as exc:
        raise DelegateError("opencode_missing", "No se encontró el ejecutable de OpenCode.") from exc
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
            "timeout", f"OpenCode excedió {timeout:g} s; se terminó su árbol de procesos."
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
        raise DelegateError("task_not_found", f"No existe el archivo de tarea: {task_file}")
    try:
        task = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise DelegateError("task_unreadable", f"No se pudo leer la tarea: {exc}") from exc
    task = task.strip()
    if not task:
        raise DelegateError("empty_task", "El archivo de tarea está vacío.")
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


def _validate_catalog_providers(catalog: list[str]) -> None:
    """Falla cerrado si la configuración externa expone otros proveedores."""

    unsafe = sorted({model.split("/", 1)[0] for model in catalog} - {"opencode"})
    if unsafe:
        shown = ", ".join(_cap(provider, 40) for provider in unsafe[:5])
        raise DelegateError(
            "unsafe_catalog",
            f"El catálogo incluye proveedores no permitidos: {shown}. Revisa la "
            "configuración externa de OpenCode y permite solo 'opencode'.",
        )


def _check_version(exe: str, cwd: Path, timeout: float) -> str:
    result = run_process([exe, "--version"], cwd, timeout)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        raise DelegateError(
            "version_check_failed",
            f"'opencode --version' falló con código {result.returncode}. Revisa "
            "los registros locales de OpenCode.",
        )
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", output)
    if not match:
        raise DelegateError(
            "invalid_version",
            "No se pudo interpretar la versión de OpenCode. Revisa la instalación "
            "y los registros locales.",
        )
    if int(match.group(1)) != 2:
        raise DelegateError(
            "unsupported_version",
            f"Se requiere OpenCode v2; versión detectada: {match.group(0)}",
        )
    return match.group(0)


def _catalog(exe: str, cwd: Path, timeout: float) -> list[str]:
    result = run_process([exe, "models", "--standalone"], cwd, timeout)
    if result.returncode != 0:
        raise DelegateError(
            "catalog_unavailable",
            f"No se pudo obtener el catálogo (código {result.returncode}). Revisa "
            "los registros locales de OpenCode.",
        )
    models: list[str] = []
    for line in (result.stdout or "").splitlines():
        token = line.strip().split()[0] if line.strip() else ""
        if token and CATALOG_LINE.match(token) and token not in models:
            models.append(token)
    if not models:
        raise DelegateError("catalog_unavailable", "El catálogo de modelos está vacío.")
    return models


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

        part = event.get("part") if isinstance(event.get("part"), dict) else {}
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


def build_command(exe: str, model: str, agent: str, task: str) -> list[str]:
    return [
        exe,
        "run",
        "--model",
        model,
        "--agent",
        agent,
        "--standalone",
        "--format",
        "json",
        "--",
        TASK_PREFIX + task,
    ]


def run_task(
    cwd: Path | str,
    task_file: Path | str,
    model: str | None = None,
    variant: str | None = None,
    agent: str = "build",
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Ejecuta un único intento, sin alternativas ni reintentos automáticos."""

    try:
        project = _validate_cwd(cwd)
        task = _read_task(task_file)
        policy = load_policy()
        if agent not in AGENTS:
            raise DelegateError("invalid_agent", f"Agente no permitido: {agent}")
        seconds = _validate_timeout(timeout)
        base_model, selected_model = parse_model(model, variant, policy)
        validate_project_policy(project)

        exe = find_opencode()
        if not exe:
            raise DelegateError(
                "opencode_missing",
                "No se encontró 'opencode' en PATH. Instala la CLI v2 o revisa PATH.",
            )
        _check_version(exe, project, seconds)
        catalog = _catalog(exe, project, seconds)
        _validate_catalog_providers(catalog)
        if base_model not in catalog:
            raise DelegateError(
                "model_unavailable",
                f"El modelo no aparece en el catálogo actual: {base_model}",
            )

        result = run_process(
            build_command(exe, selected_model, agent, task), project, seconds
        )
    except DelegateError as exc:
        return _error(exc.code, exc.message)

    stdout = result.stdout or ""
    if result.returncode != 0:
        return _error(
            "opencode_failed",
            f"OpenCode terminó con código {result.returncode}. Revisa los "
            "registros locales de OpenCode para el detalle.",
        )

    summary, session, cost, errors = parse_events(stdout)
    if errors:
        return _error("opencode_event_error", "; ".join(errors))
    if not summary:
        return _error("empty_output", "OpenCode no devolvió texto de resumen.")

    return {
        "status": "ok",
        "session": session,
        "model": selected_model,
        "agent": agent,
        "summary": _cap(summary),
        "cost": cost,
    }


def doctor(cwd: Path | str, timeout: float = DEFAULT_TIMEOUT) -> dict[str, Any]:
    """Comprueba versión v2, catálogo y disponibilidad de los modelos permitidos."""

    try:
        project = _validate_cwd(cwd)
        seconds = _validate_timeout(timeout)
        policy = load_policy()
        exe = find_opencode()
        if not exe:
            raise DelegateError(
                "opencode_missing",
                "No se encontró 'opencode' en PATH. Instala la CLI v2 o revisa PATH.",
            )
        version = _check_version(exe, project, seconds)
        catalog = _catalog(exe, project, seconds)
        _validate_catalog_providers(catalog)

        project_policy_ok = True
        project_policy_message: str | None = None
        try:
            validate_project_policy(project)
        except DelegateError as exc:
            project_policy_ok = False
            project_policy_message = _cap(exc.message)

        return {
            "status": "ok",
            "version": version,
            "catalog_count": len(catalog),
            "catalog": catalog,
            "allowed_models": [
                {"model": item, "available": item in catalog}
                for item in policy["allowed_models"]
            ],
            "project_policy_ok": project_policy_ok,
            "project_policy_message": project_policy_message,
        }
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
        description="Delega una tarea acotada a un modelo gratuito de OpenCode v2."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser(
        "doctor", help="Comprueba versión, catálogo y modelos permitidos."
    )
    doctor_parser.add_argument("--cwd", required=True)
    doctor_parser.add_argument("--timeout", type=_positive_float, default=DEFAULT_TIMEOUT)

    run_parser = subparsers.add_parser(
        "run", help="Ejecuta una tarea con un único intento."
    )
    run_parser.add_argument("--cwd", required=True)
    run_parser.add_argument("--task-file", required=True)
    run_parser.add_argument("--model")
    run_parser.add_argument("--variant")
    run_parser.add_argument("--agent", choices=AGENTS, default="build")
    run_parser.add_argument("--timeout", type=_positive_float, default=DEFAULT_TIMEOUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "doctor":
            payload = doctor(cwd=args.cwd, timeout=args.timeout)
        else:
            payload = run_task(
                cwd=args.cwd,
                task_file=args.task_file,
                model=args.model,
                variant=args.variant,
                agent=args.agent,
                timeout=args.timeout,
            )
    except Exception as exc:  # noqa: BLE001 - la CLI siempre devuelve JSON breve
        payload = _error("internal_error", str(exc))

    sys.stdout.write(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":")) + "\n"
    )
    return 0 if payload.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
