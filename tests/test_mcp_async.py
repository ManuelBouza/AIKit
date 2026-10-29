"""Comportamiento asíncrono: el bucle no se bloquea y las delegaciones se serializan."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import anyio
import delegate
import mcp_server
import pytest
from mcp.client.session import ClientSession
from mcp.shared.memory import create_connected_server_and_client_session

from tests.conftest import Harness
from tests.fakes import DEFAULT_MODEL

pytestmark = pytest.mark.anyio

ARGUMENTS: dict[str, Any] = {
    "task": "Tarea en memoria",
    "model": DEFAULT_MODEL,
    "reason": "tarea mecánica",
}


@asynccontextmanager
async def _client() -> AsyncIterator[ClientSession]:
    async with create_connected_server_and_client_session(
        mcp_server.create_server()
    ) as session:
        yield session


@pytest.mark.anyio
async def test_event_loop_stays_responsive_during_a_delegation(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    def slow(**_kwargs: Any) -> dict[str, Any]:
        time.sleep(0.3)
        return {"status": "ok", "summary": "listo"}

    monkeypatch.setattr(delegate, "run_text_task", slow)
    ticks = 0

    async def heartbeat() -> None:
        nonlocal ticks
        while True:
            await anyio.sleep(0.01)
            ticks += 1

    async with anyio.create_task_group() as group:
        group.start_soon(heartbeat)
        async with _client() as client:
            result = await client.call_tool(
                "opencode_delegate", {"cwd": str(harness.project), **ARGUMENTS}
            )
        group.cancel_scope.cancel()

    assert result.isError is False
    assert ticks > 5


@pytest.mark.anyio
async def test_delegations_of_the_same_server_are_serialized(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = {"current": 0, "peak": 0}

    def slow(**_kwargs: Any) -> dict[str, Any]:
        state["current"] += 1
        state["peak"] = max(state["peak"], state["current"])
        time.sleep(0.1)
        state["current"] -= 1
        return {"status": "ok", "summary": "listo"}

    monkeypatch.setattr(delegate, "run_text_task", slow)
    async with _client() as client:
        async with anyio.create_task_group() as group:
            for _ in range(2):
                group.start_soon(
                    client.call_tool,
                    "opencode_delegate",
                    {"cwd": str(harness.project), **ARGUMENTS},
                )

    assert state["peak"] == 1
