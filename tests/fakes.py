"""Datos de la API v2 y transporte estricto para las pruebas."""

from __future__ import annotations

import copy
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import delegate

DEFAULT_MODEL = "opencode/mimo-v2.6-flash-free"
FREE_COST: dict[str, Any] = {
    "input": 0,
    "output": 0,
    "cache": {"read": 0, "write": 0},
}
DEFAULT_COST = [FREE_COST]


def api_model(
    model_id: str = "mimo-v2.6-flash-free",
    *,
    provider: str = "opencode",
    name: str | None = None,
    enabled: bool = True,
    variants: list[dict[str, Any]] | None = None,
    cost: dict[str, Any] | list[dict[str, Any]] | None = DEFAULT_COST,
    capabilities: dict[str, Any] | None = None,
    limit: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    model: dict[str, Any] = {
        "id": model_id,
        "providerID": provider,
        "name": name or model_id,
        "enabled": enabled,
        "type": "chat",
        "capabilities": capabilities
        if capabilities is not None
        else {"tools": True, "input": ["text"], "output": ["text"]},
        "variants": variants if variants is not None else [],
        "limit": limit if limit is not None else {"context": 100000, "output": 8000},
    }
    if cost is not None:
        model["cost"] = copy.deepcopy(cost)
    model.update(extra)
    return model


def variant(variant_id: str, **settings: Any) -> dict[str, Any]:
    return {"id": variant_id, "settings": settings}


def text_event(value: str, session: str = "ses_prueba") -> str:
    return json.dumps(
        {"type": "text", "sessionID": session, "part": {"type": "text", "text": value}},
        ensure_ascii=False,
    )


def finish_event(cost: float | None = None, session: str = "ses_prueba") -> str:
    part: dict[str, Any] = {"type": "step-finish", "reason": "stop"}
    if cost is not None:
        part["cost"] = cost
    return json.dumps({"type": "step_finish", "sessionID": session, "part": part})


def error_event(message: str = "fallo del proveedor") -> str:
    return json.dumps(
        {
            "type": "error",
            "sessionID": "ses_prueba",
            "error": {"name": "ProviderError", "data": {"message": message}},
        }
    )


def policy_rule(action: str, resource: str, effect: str) -> dict[str, Any]:
    """Construye una regla de política con las tres claves exactas."""

    return {"action": action, "resource": resource, "effect": effect}


def deny_provider() -> dict[str, Any]:
    return policy_rule("provider.use", "openai", "deny")


def deny_subagent() -> dict[str, Any]:
    return policy_rule("tool.use", "subagent:*", "deny")


def default_config_sources() -> list[dict[str, Any]]:
    """Fuentes seguras por defecto: los dos bloqueos exigidos."""

    return [
        {
            "type": "document",
            "path": "C:/cfg/opencode.json",
            "info": {"policies": [deny_provider(), deny_subagent()]},
        }
    ]


@dataclass(frozen=True)
class Call:
    argv: list[str]
    cwd: str
    timeout: float


@dataclass
class FakeTransport:
    version: str = "2.2.0"
    models: list[dict[str, Any]] = field(default_factory=lambda: [api_model()])
    run_stdout: str = field(
        default_factory=lambda: text_event("ok") + "\n" + finish_event(0)
    )
    run_returncode: int = 0
    run_stderr: str = ""
    fail_run: bool = False
    timeout_error: bool = False
    version_returncode: int = 0
    version_stderr: str = ""
    catalog_returncode: int = 0
    catalog_stderr: str = ""
    config_sources: list[dict[str, Any]] = field(default_factory=default_config_sources)
    config_returncode: int = 0
    config_stdout: str | None = None
    config_stderr: str = ""
    calls: list[Call] = field(default_factory=list)

    def __call__(
        self, argv: list[str], cwd: Path | str, timeout: float
    ) -> subprocess.CompletedProcess[str]:
        args = list(argv)
        self.calls.append(Call(args, str(cwd), timeout))
        assert args
        assert args[0] == "C:/fake/opencode.exe"
        if args[1:] == ["--version"]:
            return subprocess.CompletedProcess(
                args, self.version_returncode, self.version + "\n", self.version_stderr
            )
        if args[1:] == ["api", "--standalone", "GET", "/api/model"]:
            payload = {"location": {"directory": str(cwd)}, "data": self.models}
            return subprocess.CompletedProcess(
                args,
                self.catalog_returncode,
                json.dumps(payload, ensure_ascii=False),
                self.catalog_stderr,
            )
        if args[1:] == ["debug", "config", "--standalone"]:
            stdout = self.config_stdout
            if stdout is None:
                stdout = json.dumps(self.config_sources, ensure_ascii=False)
            return subprocess.CompletedProcess(
                args, self.config_returncode, stdout, self.config_stderr
            )
        if len(args) >= 2 and args[1] == "run":
            assert len(args) == 11
            assert args[2] == "--model"
            assert args[3]
            assert args[4] == "--agent"
            assert args[5] in ("build", "plan")
            assert args[6:10] == ["--standalone", "--format", "json", "--"]
            assert args[10].startswith(delegate.TASK_PREFIX)
            if self.timeout_error:
                raise delegate.DelegateError("timeout", "OpenCode excedió el tiempo")
            if self.fail_run:
                raise delegate.DelegateError(
                    "opencode_failed", "no se pudo iniciar OpenCode"
                )
            return subprocess.CompletedProcess(
                args, self.run_returncode, self.run_stdout, self.run_stderr
            )
        raise AssertionError(f"Llamada inesperada: {args!r}")

    @property
    def run_calls(self) -> list[Call]:
        return [call for call in self.calls if call.argv[1:2] == ["run"]]

    @property
    def config_calls(self) -> list[Call]:
        return [
            call
            for call in self.calls
            if call.argv[1:4] == ["debug", "config", "--standalone"]
        ]
