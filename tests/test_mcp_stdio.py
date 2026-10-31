"""Transporte STDIO real: handshake, catálogo de herramientas y bloqueo directo."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import LATEST_PROTOCOL_VERSION, TextContent

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "skills" / "delegating-to-opencode" / "scripts" / "mcp_server.py"

pytestmark = pytest.mark.anyio


@pytest.fixture
def server_env(tmp_path: Path) -> dict[str, str]:
    """Entorno sin host ni OpenCode: el servidor no debe iniciar el backend."""

    empty_bin = tmp_path / "bin"
    empty_bin.mkdir()
    env = os.environ.copy()
    env["PATH"] = str(empty_bin)
    env["PATHEXT"] = os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD")
    env["PYTHONIOENCODING"] = "utf-8"
    for name in (
        "AIKIT_OPENCODE_REGISTRATION",
        "AIKIT_STATE",
        "AIKIT_EXPECTED_OPENCODE_VERSION",
    ):
        env.pop(name, None)
    return env


def _payload(result: Any) -> dict[str, Any]:
    block = result.content[0]
    assert isinstance(block, TextContent)
    data: dict[str, Any] = json.loads(block.text)
    return data


async def test_stdio_handshake_and_tool_list(server_env: dict[str, str]) -> None:
    params = StdioServerParameters(
        command=sys.executable, args=[str(SERVER)], env=server_env
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            initialization = await session.initialize()
            assert initialization.serverInfo.name == "aikit-opencode"
            tools = (await session.list_tools()).tools
    assert {tool.name for tool in tools} == {
        "opencode_catalog",
        "opencode_delegate",
    }
    catalog = next(tool for tool in tools if tool.name == "opencode_catalog")
    delegate = next(tool for tool in tools if tool.name == "opencode_delegate")
    assert catalog.annotations is not None
    assert catalog.annotations.readOnlyHint is True
    assert delegate.annotations is not None
    assert delegate.annotations.destructiveHint is True
    assert delegate.annotations.idempotentHint is False


async def test_stdio_rejects_the_direct_openai_provider(
    server_env: dict[str, str], tmp_path: Path
) -> None:
    params = StdioServerParameters(
        command=sys.executable, args=[str(SERVER)], env=server_env
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "opencode_delegate",
                {
                    "cwd": str(tmp_path),
                    "task": "Tarea",
                    "model": "openai/gpt-5",
                    "reason": "tarea mecánica",
                },
            )
    assert result.isError is True
    assert _payload(result)["code"] == "provider_not_allowed"


async def test_stdio_catalog_without_host_context_is_an_error(
    server_env: dict[str, str], tmp_path: Path
) -> None:
    params = StdioServerParameters(
        command=sys.executable, args=[str(SERVER)], env=server_env
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("opencode_catalog", {"cwd": str(tmp_path)})
    assert result.isError is True
    assert _payload(result)["code"] == "host_context_unavailable"


def test_stdout_carries_only_json_rpc_messages(
    server_env: dict[str, str], tmp_path: Path
) -> None:
    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": LATEST_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "prueba", "version": "1"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    ]
    request = "\n".join(json.dumps(message) for message in messages) + "\n"
    completed = subprocess.run(
        [sys.executable, str(SERVER)],
        input=request,
        capture_output=True,
        text=True,
        env=server_env,
        timeout=60,
        check=False,
        cwd=str(tmp_path),
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    assert lines, "el servidor debe responder al initialize"
    for line in lines:
        message = json.loads(line)
        assert message["jsonrpc"] == "2.0"
    identifiers = {json.loads(line).get("id") for line in lines}
    assert identifiers == {1, 2}
