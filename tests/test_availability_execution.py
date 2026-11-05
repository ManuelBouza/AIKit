"""Ejecución pública usando filas acreditadas del contexto exacto."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import bound_execution
import delegate
import mcp_server
import pytest
from availability_policy import record_outcome
from availability_state import AvailabilitySnapshot, state_path, update_snapshot
from mcp.shared.memory import create_connected_server_and_client_session

from tests.conftest import Harness
from tests.fakes import DEFAULT_MODEL, api_model, seed_availability


def seed_table(harness: Harness, models: list[dict[str, Any]] | None = None) -> None:
    assert harness.context is not None
    seed_availability(harness.context, harness.project, models or [api_model()])


def no_capacity_calls(harness: Harness) -> None:
    assert harness.bindings
    assert not [
        kind
        for binding in harness.bindings
        for kind, _ in binding.calls
        if kind in {"catalog", "usage", "openapi", "integrations"}
    ]


def test_two_successive_runs_use_table_without_remote_catalog(harness: Harness) -> None:
    transport = harness.fake()
    seed_table(harness)
    one = harness.run_text("authorized-one")
    two = harness.run_text("authorized-two")
    assert one["status"] == two["status"] == "ok"
    assert one["attempt_id"] != two["attempt_id"]
    assert len(transport.run_calls) == 2
    no_capacity_calls(harness)


def test_known_exhausted_rejects_without_inference(harness: Harness) -> None:
    transport = harness.fake()
    seed_table(harness)
    assert harness.context is not None
    from dataclasses import replace

    def exhausted(snapshot: AvailabilitySnapshot) -> AvailabilitySnapshot:
        project = delegate._project_key(harness.project)
        entries = dict(snapshot.project_models[project])
        entries[DEFAULT_MODEL] = record_outcome(
            entries[DEFAULT_MODEL],
            "quota_exhausted",
            datetime.now(timezone.utc),
            attempt_id="prior",
        )
        return replace(snapshot, models=entries, project_models={project: entries})

    update_snapshot(state_path(harness.context.aikit_state), exhausted)
    result = harness.run_text("not submitted")
    assert result["code"] == "model_unavailable"
    assert transport.run_calls == []
    no_capacity_calls(harness)


def test_unknown_quota_allows_one_real_attempt(harness: Harness) -> None:
    from session_store import load_task

    transport = harness.fake(run_stdout="")
    seed_table(harness)
    prepared = delegate._prepare_run(
        harness.project,
        lambda: "authorized",
        DEFAULT_MODEL,
        None,
        "reason",
        "build",
        30,
    )
    one = bound_execution.execute_bound(
        prepared, context=prepared.binding.context, wait_seconds=0
    )
    again = bound_execution.execute_bound(
        prepared, context=prepared.binding.context, wait_seconds=0
    )
    recovered = bound_execution.recover_local_result(
        prepared.binding.context, load_task(harness.project, one["task_id"])
    )
    assert uuid.UUID(one["attempt_id"])
    assert one["status"] == again["status"] == recovered["status"] == "pending"
    assert one["attempt_id"] == again["attempt_id"] == recovered["attempt_id"]
    assert len(transport.run_calls) == 1
    no_capacity_calls(harness)


@pytest.mark.anyio
async def test_mcp_two_successive_delegations_use_table(harness: Harness) -> None:
    transport = harness.fake()
    seed_table(harness)
    async with create_connected_server_and_client_session(
        mcp_server.create_server()
    ) as session:
        ids = []
        for task in ("one", "two"):
            result = await session.call_tool(
                "opencode_delegate",
                {
                    "cwd": str(harness.project),
                    "task": task,
                    "model": DEFAULT_MODEL,
                    "reason": "authorized",
                    "timeout": 7,
                },
            )
            assert result.structuredContent is not None
            assert result.structuredContent["status"] == "ok"
            ids.append(result.structuredContent["attempt_id"])
    assert ids[0] != ids[1]
    assert len(transport.run_calls) == 2
    no_capacity_calls(harness)
