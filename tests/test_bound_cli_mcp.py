"""CLI y MCP comparten preflight, rol, espera y estado incierto."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import bound_execution
import delegate
import mcp_server
import pytest
from mcp.client.session import ClientSession
from mcp.shared.memory import create_connected_server_and_client_session

from tests.conftest import Harness
from tests.fakes import DEFAULT_MODEL, api_model, variant


@asynccontextmanager
async def _client() -> AsyncIterator[ClientSession]:
    async with create_connected_server_and_client_session(
        mcp_server.create_server()
    ) as session:
        yield session


def _text(result: Any) -> str:
    assert result.content, "el resultado debe traer contenido"
    block = result.content[0]
    assert block.type == "text"
    return str(block.text)


def _ok(prepared: Any) -> dict[str, Any]:
    return {
        "status": "ok",
        "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "attempt_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
        "session": "ses_cli",
        "model": prepared.model,
        "variant": prepared.variant,
        "effort": prepared.variant or "provider_default",
        "reason": prepared.reason,
        "agent": prepared.agent,
        "summary": "listo",
        "cost": None,
        "delivery": "completed",
        "execution": "unknown",
        "limitations": [],
    }


def test_cli_uses_bound_execution_and_waits_the_existing_limit(
    harness: Harness,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness.fake()
    seen: dict[str, Any] = {}

    def execute(prepared: Any, *, context: Any, wait_seconds: float) -> dict[str, Any]:
        seen.update(prepared=prepared, context=context, wait_seconds=wait_seconds)
        return _ok(prepared)

    monkeypatch.setattr(bound_execution, "execute_bound", execute)

    code = delegate.main(
        [
            "run",
            "--cwd",
            str(harness.project),
            "--task-file",
            str(harness.task),
            "--model",
            DEFAULT_MODEL,
            "--reason",
            "motivo acotado",
            "--timeout",
            "12.5",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["status"] == "ok"
    assert seen["prepared"].project == harness.project.resolve()
    assert seen["prepared"].binding is not None
    assert seen["wait_seconds"] == 12.5
    assert seen["context"] is seen["prepared"].binding.context


def test_cli_role_is_explicit_and_agent_plan_is_not_a_reviewer(
    harness: Harness,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness.fake()
    seen: list[Any] = []

    def execute(prepared: Any, *, context: Any, wait_seconds: float) -> dict[str, Any]:
        seen.append(prepared)
        return _ok(prepared)

    monkeypatch.setattr(bound_execution, "execute_bound", execute)
    base = [
        "run",
        "--cwd",
        str(harness.project),
        "--task-file",
        str(harness.task),
        "--model",
        DEFAULT_MODEL,
        "--reason",
        "motivo acotado",
        "--agent",
        "plan",
    ]

    assert delegate.main(base) == 0
    assert delegate.main(base + ["--role", "reviewer"]) == 0
    capsys.readouterr()

    assert [item.agent for item in seen] == ["plan", "plan"]
    assert [item.role for item in seen] == ["implementer", "reviewer"]


@pytest.mark.anyio
async def test_mcp_caps_wait_at_45_seconds(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    harness.fake()
    seen: dict[str, Any] = {}

    def execute(prepared: Any, *, context: Any, wait_seconds: float) -> dict[str, Any]:
        seen["wait_seconds"] = wait_seconds
        return _ok(prepared)

    monkeypatch.setattr(bound_execution, "execute_bound", execute)

    async with _client() as session:
        result = await session.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea literal",
                "model": DEFAULT_MODEL,
                "reason": "motivo acotado",
                "timeout": 300,
            },
        )

    assert json.loads(_text(result))["status"] == "ok"
    assert seen["wait_seconds"] == 45.0


@pytest.mark.anyio
async def test_mcp_uses_the_requested_wait_when_below_the_cap(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    harness.fake()
    seen: dict[str, Any] = {}

    def execute(prepared: Any, *, context: Any, wait_seconds: float) -> dict[str, Any]:
        seen["wait_seconds"] = wait_seconds
        return _ok(prepared)

    monkeypatch.setattr(bound_execution, "execute_bound", execute)

    async with _client() as session:
        await session.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea literal",
                "model": DEFAULT_MODEL,
                "reason": "motivo acotado",
                "timeout": 7,
            },
        )

    assert seen["wait_seconds"] == 7.0


@pytest.mark.anyio
async def test_mcp_pending_is_tracked_without_error_or_second_send(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    harness.fake()
    launches: list[Any] = []
    monkeypatch.setattr(
        bound_execution,
        "_launch_supervisor",
        lambda prepared, record, *, context: launches.append(record),
    )

    async with _client() as session:
        result = await session.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "Tarea que no termina",
                "model": DEFAULT_MODEL,
                "reason": "motivo acotado",
                "timeout": 0.05,
            },
        )

    payload = json.loads(_text(result))
    assert result.isError is False
    assert payload["status"] == "pending"
    assert payload["task_id"]
    assert payload["attempt_id"]
    assert payload["uncertain"] is True
    assert "error" not in payload
    assert len(launches) == 1


@pytest.mark.anyio
async def test_mcp_schema_exposes_role_and_preserves_agent_and_variant(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    harness.fake(models=[api_model(variants=[variant("high")])])
    seen: list[Any] = []

    def execute(prepared: Any, *, context: Any, wait_seconds: float) -> dict[str, Any]:
        seen.append(prepared)
        return _ok(prepared)

    monkeypatch.setattr(bound_execution, "execute_bound", execute)

    async with _client() as session:
        tools = await session.list_tools()
        delegate_tool = next(
            tool for tool in tools.tools if tool.name == "opencode_delegate"
        )
        role = delegate_tool.inputSchema["properties"]["role"]
        assert role["enum"] == ["implementer", "reviewer"]

        result = await session.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": '--auto & "comillas" ñ',
                "model": DEFAULT_MODEL,
                "variant": "high",
                "reason": "motivo acotado",
                "agent": "plan",
                "role": "reviewer",
            },
        )

    assert json.loads(_text(result))["status"] == "ok"
    prepared = seen[0]
    assert prepared.agent == "plan"
    assert prepared.role == "reviewer"
    assert prepared.variant == "high"
    assert prepared.argv[-1] == delegate.TASK_PREFIX + '--auto & "comillas" ñ'
    assert prepared.argv[prepared.argv.index("--agent") + 1] == "plan"
    assert "--standalone" not in prepared.argv


@pytest.mark.anyio
async def test_mcp_real_wait_budget_returns_tracking_without_stopping_worker(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    from types import SimpleNamespace

    harness.fake()
    now = [0.0]
    launches = []

    def sleep(seconds: float) -> None:
        now[0] += seconds

    monkeypatch.setattr(
        bound_execution, "time", SimpleNamespace(monotonic=lambda: now[0], sleep=sleep)
    )
    monkeypatch.setattr(bound_execution, "POLL_SECONDS", 10.0)
    monkeypatch.setattr(
        bound_execution,
        "_launch_supervisor",
        lambda prepared, record, *, context: launches.append(record),
    )
    async with _client() as session:
        result = await session.call_tool(
            "opencode_delegate",
            {
                "cwd": str(harness.project),
                "task": "future-terminal",
                "model": DEFAULT_MODEL,
                "reason": "test",
                "timeout": 300,
            },
        )
    payload = json.loads(_text(result))
    assert now[0] == 45
    assert result.isError is False
    assert payload["status"] == "pending"
    assert payload["task_id"] == launches[0].task_id
    assert payload["attempt_id"] == launches[0].attempt_id
    assert len(launches) == 1
