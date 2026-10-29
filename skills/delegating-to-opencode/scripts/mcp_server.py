#!/usr/bin/env python3
"""Servidor MCP local que expone el adaptador de OpenCode como dos herramientas.

El servidor no implementa protocolo propio: usa el SDK oficial de MCP y
reutiliza el núcleo de `delegate.py` (catálogo, bloqueos, variantes y errores).
`stdout` queda reservado al protocolo MCP; cualquier diagnóstico va a stderr.
"""

from __future__ import annotations

import asyncio
import functools
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

import anyio
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent, ToolAnnotations

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import delegate  # noqa: E402  # se importa tras preparar la ruta de la skill

SERVER_NAME = "aikit-opencode"
DEFAULT_TIMEOUT = 300.0
INTERNAL_MESSAGE = "Fallo inesperado en el servidor MCP de AIKit."
INSTRUCTIONS = (
    "Puente de AIKit hacia OpenCode v2. Consulta el catálogo con "
    "opencode_catalog y ejecuta una tarea acotada con opencode_delegate, "
    "eligiendo siempre un modelo explícito y registrando el motivo."
)


def _absolute_cwd(cwd: str) -> str:
    """Exige una ruta absoluta para no depender del directorio del cliente."""

    if not Path(cwd).is_absolute():
        raise delegate.DelegateError(
            "invalid_cwd", "El directorio de trabajo debe ser una ruta absoluta."
        )
    return cwd


def _error_payload(code: str, message: str) -> dict[str, Any]:
    return {"status": "error", "code": code, "message": message}


def _internal_payload() -> dict[str, Any]:
    """Mensaje fijo: un fallo inesperado no expone detalles ni secretos."""

    return _error_payload("internal_error", INTERNAL_MESSAGE)


def _to_result(payload: dict[str, Any]) -> CallToolResult:
    """Compacta el resultado: JSON en el contenido y copia estructurada."""

    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        structuredContent=dict(payload),
        isError=payload.get("status") == "error",
    )


async def _call_in_thread(
    func: Callable[..., dict[str, Any]], **kwargs: Any
) -> dict[str, Any]:
    """Ejecuta el núcleo sin bloquear el bucle de eventos del servidor."""

    return await anyio.to_thread.run_sync(functools.partial(func, **kwargs))


def create_server() -> FastMCP:
    """Crea el servidor MCP con el catálogo y la delegación de AIKit."""

    server = FastMCP(SERVER_NAME, instructions=INSTRUCTIONS)
    delegation_lock = asyncio.Lock()

    @server.tool(
        name="opencode_catalog",
        annotations=ToolAnnotations(
            title="Catálogo de OpenCode",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def opencode_catalog(
        cwd: str,
        model: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> CallToolResult:
        """Consulta la versión y el catálogo de modelos habilitados de OpenCode.

        `cwd` es una ruta absoluta del proyecto. `model` filtra por modelo base
        `provider/model`. `timeout` es finito, mayor que cero y máximo 3600 s.
        Solo consulta: no infiere ni modifica nada.
        """

        try:
            project = _absolute_cwd(cwd)
            payload = await _call_in_thread(
                delegate.doctor, cwd=project, model=model, timeout=timeout
            )
        except delegate.DelegateError as exc:
            payload = _error_payload(exc.code, exc.message)
        except Exception:  # noqa: BLE001 - el cliente siempre recibe JSON breve
            payload = _internal_payload()
        return _to_result(payload)

    @server.tool(
        name="opencode_delegate",
        annotations=ToolAnnotations(
            title="Delegación acotada a OpenCode",
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=True,
        ),
    )
    async def opencode_delegate(
        cwd: str,
        task: str,
        model: str,
        reason: str,
        variant: str | None = None,
        agent: Literal["build", "plan"] = "build",
        timeout: float = DEFAULT_TIMEOUT,
    ) -> CallToolResult:
        """Ejecuta una tarea acotada en OpenCode con un modelo explícito.

        `cwd` es una ruta absoluta del proyecto, `task` el texto literal de la
        tarea, `model` el modelo `provider/model[#variante]` y `reason` el
        motivo de la selección. `variant` es opcional y `agent` admite `build`
        o `plan`. El timeout es finito, mayor que cero y máximo 3600 s.

        Es una ejecución con efectos: puede modificar archivos del proyecto y
        deja que OpenCode use shell o red arbitraria. No reintenta ni elige
        modelo por su cuenta.
        """

        try:
            project = _absolute_cwd(cwd)
            async with delegation_lock:
                payload = await _call_in_thread(
                    delegate.run_text_task,
                    cwd=project,
                    task=task,
                    model=model,
                    variant=variant,
                    reason=reason,
                    agent=agent,
                    timeout=timeout,
                )
        except delegate.DelegateError as exc:
            payload = _error_payload(exc.code, exc.message)
        except Exception:  # noqa: BLE001 - el cliente siempre recibe JSON breve
            payload = _internal_payload()
        return _to_result(payload)

    return server


def main() -> None:
    """Atiende el protocolo MCP por STDIO."""

    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
