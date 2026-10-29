"""Contrato MCP: herramientas, esquemas, errores y resultado estructurado."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import delegate
import mcp_server
import pytest
from mcp.client.session import ClientSession
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import TextContent, Tool

from tests.conftest import Harness
from tests.fakes import DEFAULT_MODEL, FakeTransport, api_model, variant

pytestmark = pytest.mark.anyio

INTERNAL_MESSAGE = "Fallo inesperado en el servidor MCP de AIKit."


@asynccontextmanager
async def _client() -> AsyncIterator[ClientSession]:
    async with create_connected_server_and_client_session(
        mcp_server.create_server()
    ) as session:
        yield session


def _text(result: Any) -> str:
    assert result.content, "el resultado debe traer contenido"
    block = result.content[0]
    assert isinstance(block, TextContent)
    return block.text


def _payload(result: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(_text(result))
    return data


def _tool(tools: list[Tool], name: str) -> Tool:
    return next(tool for tool in tools if tool.name == name)


async def test_server_publishes_exactly_the_two_agreed_tools() -> None:
    async with _client() as client:
        tools = (await client.list_tools()).tools
    assert {tool.name for tool in tools} == {
        "opencode_catalog",
        "opencode_delegate",
    }


async def test_catalog_is_annotated_as_read_only() -> None:
    async with _client() as client:
        tools = (await client.list_tools()).tools
    annotations = _tool(tools, "opencode_catalog").annotations
    assert annotations is not None
    assert annotations.readOnlyHint is True
    assert annotations.destructiveHint is False


async def test_delegate_is_annotated_as_destructive_and_not_idempotent() -> None:
    async with _client() as client:
        tools = (await client.list_tools()).tools
    annotations = _tool(tools, "opencode_delegate").annotations
    assert annotations is not None
    assert annotations.destructiveHint is True
    assert annotations.idempotentHint is False
    assert annotations.readOnlyHint is False


async def test_delegate_is_annotated_as_open_world_and_catalog_is_not() -> None:
    """La delegación puede ejecutar shell o red arbitraria: es mundo abierto."""

    async with _client() as client:
        tools = (await client.list_tools()).tools
    delegate_annotations = _tool(tools, "opencode_delegate").annotations
    catalog_annotations = _tool(tools, "opencode_catalog").annotations
    assert delegate_annotations is not None
    assert catalog_annotations is not None
    assert delegate_annotations.openWorldHint is True
    assert catalog_annotations.openWorldHint is False


async def test_catalog_schema_requires_cwd_and_defaults_timeout() -> None:
    async with _client() as client:
        tools = (await client.list_tools()).tools
    schema = _tool(tools, "opencode_catalog").inputSchema
    assert schema["required"] == ["cwd"]
    assert schema["properties"]["timeout"]["default"] == 300
    assert set(schema["properties"]) == {"cwd", "model", "timeout"}


async def test_delegate_schema_requires_selection_fields() -> None:
    async with _client() as client:
        tools = (await client.list_tools()).tools
    schema = _tool(tools, "opencode_delegate").inputSchema
    assert set(schema["required"]) == {"cwd", "task", "model", "reason"}
    properties = schema["properties"]
    assert properties["agent"]["enum"] == ["build", "plan"]
    assert properties["agent"]["default"] == "build"
    assert properties["timeout"]["default"] == 300
    assert "autoApprove" not in json.dumps(schema)


async def test_listing_tools_does_not_touch_the_backend(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode() -> str:
        raise AssertionError("el backend no debe ejecutarse al listar herramientas")

    monkeypatch.setattr(delegate, "find_opencode", explode)
    async with _client() as client:
        tools = (await client.list_tools()).tools
    assert len(tools) == 2


async def test_catalog_rejects_relative_cwd_without_any_process(
    harness: Harness,
) -> None:
    transport = harness.fake()
    async with _client() as client:
        result = await client.call_tool("opencode_catalog", {"cwd": "."})
    assert result.isError is True
    payload = _payload(result)
    assert payload["code"] == "invalid_cwd"
    assert "absoluta" in payload["message"]
    assert transport.calls == []


async def test_delegate_rejects_relative_cwd_without_any_process(
    harness: Harness,
) -> None:
    transport = harness.fake()
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": ".",
                "task": "Tarea",
                "model": DEFAULT_MODEL,
                "reason": "tarea mecánica",
            },
        )
    assert result.isError is True
    payload = _payload(result)
    assert payload["code"] == "invalid_cwd"
    assert "absoluta" in payload["message"]
    assert transport.calls == []


async def test_catalog_returns_the_version_and_catalog(
    harness: Harness,
) -> None:
    harness.fake(version="2.2.0", models=[api_model("uno"), api_model("dos")])
    async with _client() as client:
        result = await client.call_tool(
            "opencode_catalog", {"cwd": str(harness.project)}
        )
    assert result.isError is False
    payload = _payload(result)
    assert payload["status"] == "ok"
    assert payload["version"] == "2.2.0"
    assert payload["catalog_count"] == 2
    assert result.structuredContent == payload


async def test_delegate_runs_the_task_and_copies_the_payload(
    harness: Harness,
) -> None:
    harness.fake()
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea en memoria",
                "model": DEFAULT_MODEL,
                "reason": "tarea mecánica",
            },
        )
    assert result.isError is False
    payload = _payload(result)
    assert payload["status"] == "ok"
    assert payload["summary"] == "ok"
    assert result.structuredContent == payload
    assert _text(result) == json.dumps(
        payload, ensure_ascii=False, separators=(",", ":")
    )


async def test_delegate_forwards_variant_and_agent_to_the_backend(
    harness: Harness,
) -> None:
    transport = harness.fake(models=[api_model(variants=[variant("high")])])
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea en memoria",
                "model": DEFAULT_MODEL,
                "reason": "tarea mecánica",
                "variant": "high",
                "agent": "plan",
            },
        )
    assert result.isError is False
    argv = transport.run_calls[0].argv
    assert argv[3] == DEFAULT_MODEL + "#high"
    assert argv[5] == "plan"


async def test_delegate_rejects_the_blocked_provider_before_any_process(
    harness: Harness,
) -> None:
    transport = harness.fake()
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea",
                "model": "openai/gpt-5",
                "reason": "tarea mecánica",
            },
        )
    assert result.isError is True
    assert _payload(result)["code"] == "provider_not_allowed"
    assert transport.calls == []


async def test_delegate_reports_free_limit_with_reselect(harness: Harness) -> None:
    output = json.dumps(
        {"type": "error", "error": {"type": "provider.free-limit", "message": "x"}}
    )
    harness.fake(FakeTransport(run_stdout=output))
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea",
                "model": DEFAULT_MODEL,
                "reason": "tarea mecánica",
            },
        )
    assert result.isError is True
    payload = _payload(result)
    assert payload["code"] == "free_limit_reached"
    assert payload["fallback"] == "reselect"


async def test_delegate_rejects_an_unknown_variant(harness: Harness) -> None:
    harness.fake(models=[api_model(variants=[variant("high")])])
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea",
                "model": DEFAULT_MODEL,
                "reason": "tarea mecánica",
                "variant": "imaginaria",
            },
        )
    assert result.isError is True
    assert _payload(result)["code"] == "invalid_variant"


async def test_missing_required_field_is_reported_as_an_error(
    harness: Harness,
) -> None:
    harness.fake()
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {"cwd": str(harness.project), "task": "Tarea", "model": DEFAULT_MODEL},
        )
    assert result.isError is True
    assert "reason" in _text(result)


async def test_missing_required_field_is_rejected_by_the_sdk_without_structured(
    harness: Harness,
) -> None:
    """Falta el campo: lo rechaza el SDK antes del handler, sin JSON del núcleo."""

    harness.fake()
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {"cwd": str(harness.project), "task": "Tarea", "model": DEFAULT_MODEL},
        )
    assert result.isError is True
    assert result.structuredContent is None
    assert "reason" in _text(result)


@pytest.mark.parametrize("reason", ["", " \t "], ids=["vacio", "blancos"])
async def test_empty_reason_reaches_the_core_and_keeps_its_code(
    harness: Harness, reason: str
) -> None:
    """Un motivo vacío sí llega al núcleo: conserva JSON y `reason_required`."""

    harness.fake()
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea",
                "model": DEFAULT_MODEL,
                "reason": reason,
            },
        )
    assert result.isError is True
    payload = _payload(result)
    assert payload["code"] == "reason_required"
    assert result.structuredContent == payload


async def test_wrongly_typed_argument_is_rejected_by_the_sdk_without_structured(
    harness: Harness,
) -> None:
    """Un tipo incorrecto lo rechaza el SDK: texto y sin `structuredContent`."""

    harness.fake()
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea",
                "model": DEFAULT_MODEL,
                "reason": "tarea mecánica",
                "timeout": "mucho",
            },
        )
    assert result.isError is True
    assert result.structuredContent is None
    assert "timeout" in _text(result)


async def test_malformed_timeout_is_reported_as_an_error(harness: Harness) -> None:
    transport = harness.fake()
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea",
                "model": DEFAULT_MODEL,
                "reason": "tarea mecánica",
                "timeout": "mucho",
            },
        )
    assert result.isError is True
    assert transport.calls == []


@pytest.mark.parametrize("timeout", [0, 3601, -5], ids=["cero", "límite", "negativo"])
async def test_out_of_range_timeout_is_rejected_before_any_process(
    harness: Harness, timeout: int
) -> None:
    transport = harness.fake()
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea",
                "model": DEFAULT_MODEL,
                "reason": "tarea mecánica",
                "timeout": timeout,
            },
        )
    assert result.isError is True
    assert _payload(result)["code"] == "invalid_timeout"
    assert transport.calls == []


async def test_unexpected_failure_returns_a_fixed_message(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(**_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("TOKEN=secreto")

    monkeypatch.setattr(delegate, "run_text_task", explode)
    async with _client() as client:
        result = await client.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea",
                "model": DEFAULT_MODEL,
                "reason": "tarea mecánica",
            },
        )
    assert result.isError is True
    payload = _payload(result)
    assert payload["message"] == INTERNAL_MESSAGE
    assert "secreto" not in json.dumps(payload)
