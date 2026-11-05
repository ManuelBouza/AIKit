"""Pruebas de estado tipado y persistencia segura de disponibilidad."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import availability_state as a
import pytest
from session_store import StoreError


def _utc(text: str) -> datetime:
    return datetime.fromisoformat(text)


def _record() -> a.AvailabilityRecord:
    return a.AvailabilityRecord(
        provider="opencode-go",
        account_alias=a.AccountAlias("acct-local"),
        model="opencode-go/iceman-contributor-free",
        limit_scope="model",
        status="exhausted",
        observed_at=_utc("2026-10-31T14:53:45.967746+00:00"),
        last_valid_observation=a.QuotaObservation(
            status="exhausted",
            source="experimental.usage.limits",
            asof=_utc("2026-10-31T14:53:45.967746+00:00"),
            limit_scope="model",
            reset_at=_utc("2026-11-02T00:00:00+00:00"),
            precision="confirmed",
            percent=100,
            limited=True,
        ),
        last_query_attempt=a.QueryAttempt(
            at=_utc("2026-10-31T14:53:46+00:00"),
            result="ok",
            error_code=None,
        ),
        reset_at=_utc("2026-11-02T00:00:00+00:00"),
        precision="confirmed",
        next_check_at=_utc("2026-10-31T15:08:45+00:00"),
        shared_scope_known=False,
    )


def _snapshot(record: a.AvailabilityRecord) -> a.AvailabilitySnapshot:
    return a.AvailabilitySnapshot(
        schema_version=a.STATE_SCHEMA_VERSION,
        generation=1,
        published_at=_utc("2026-10-31T14:53:46+00:00"),
        catalog_contexts=(
            a.CatalogContext(
                project_key="abc123", config_sources=("global", "project")
            ),
        ),
        models={
            "opencode-go/iceman-contributor-free": a.ModelEntry(
                metadata=a.ModelMetadata(
                    model="opencode-go/iceman-contributor-free",
                    name="Iceman Contributor Free",
                    pricing=(a.PricingTier(input=0.0, output=0.0),),
                    variants=("high",),
                    tools=True,
                    input_modalities=("text",),
                    output_modalities=("text",),
                    context_limit=200000,
                    output_limit=32000,
                    free_candidate=True,
                    may_use_openai_quota=False,
                ),
                quota=record.last_valid_observation,
                context_key="abc123",
            )
        },
        data_sources=(a.DataSourceStatus(name="go", status="ok", error_code=None),),
    )


def test_state_roundtrip_and_completeness(tmp_path: Path) -> None:
    path = tmp_path / "state" / "availability-state.json"
    snapshot = _snapshot(_record())
    a.write_snapshot(path, snapshot)
    loaded = a.read_snapshot(path)
    assert loaded == snapshot


def test_missing_state_is_none(tmp_path: Path) -> None:
    assert a.read_snapshot(tmp_path / "state" / "availability-state.json") is None


def test_unknown_account_alias_is_not_available() -> None:
    record = a.record_with_unknown_alias(
        provider="opencode-go", model="opencode-go/iceman-contributor-free"
    )
    assert record.status == "unknown"
    assert record.account_alias == a.AccountAlias("")


def test_corrupt_json_is_rejected_without_partial_state(tmp_path: Path) -> None:
    path = tmp_path / "state" / "availability-state.json"
    path.parent.mkdir(parents=True)
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(StoreError) as exc:
        a.read_snapshot(path)
    assert exc.value.code == "availability_corrupt"


def test_future_schema_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "state" / "availability-state.json"
    path.parent.mkdir(parents=True)
    payload = {
        "schema_version": a.STATE_SCHEMA_VERSION + 1,
        "generation": 1,
        "published_at": "2026-10-31T14:53:46+00:00",
        "catalog_contexts": [],
        "models": {},
        "data_sources": [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(StoreError) as exc:
        a.read_snapshot(path)
    assert exc.value.code == "availability_schema_future"


def test_bool_is_not_int_in_json(tmp_path: Path) -> None:
    path = tmp_path / "state" / "availability-state.json"
    path.parent.mkdir(parents=True)
    payload = {
        "schema_version": a.STATE_SCHEMA_VERSION,
        "generation": True,
        "published_at": "2026-10-31T14:53:46+00:00",
        "catalog_contexts": [],
        "models": {},
        "data_sources": [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(StoreError) as exc:
        a.read_snapshot(path)
    assert exc.value.code == "availability_corrupt"


def test_naive_timestamp_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "state" / "availability-state.json"
    path.parent.mkdir(parents=True)
    payload = {
        "schema_version": a.STATE_SCHEMA_VERSION,
        "generation": 1,
        "published_at": "2026-10-31T14:53:46",
        "catalog_contexts": [],
        "models": {},
        "data_sources": [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(StoreError) as exc:
        a.read_snapshot(path)
    assert exc.value.code == "availability_corrupt"


def test_failed_write_preserves_previous_bytes(tmp_path: Path) -> None:
    path = tmp_path / "state" / "availability-state.json"
    original = _snapshot(_record())
    a.write_snapshot(path, original)
    before = path.read_bytes()
    broken = a.AvailabilitySnapshot(
        schema_version=a.STATE_SCHEMA_VERSION,
        generation=2,
        published_at=_utc("2026-10-31T15:00:00+00:00"),
        catalog_contexts=(),
        models={},
        data_sources=(),
    )
    with pytest.raises(StoreError):
        a.write_snapshot(path, broken, fail_before_replace=True)
    assert path.read_bytes() == before


def test_two_processes_do_not_lose_updates(tmp_path: Path) -> None:
    state_dir = tmp_path / "state"
    code = (
        "import sys; import dataclasses; import availability_state as a;"
        "from pathlib import Path;"
        "p=Path(sys.argv[1]);"
        "s=a.read_snapshot(a.state_path(p)) or a.empty_snapshot();"
        "s=dataclasses.replace(s, generation=s.generation+1);"
        "a.write_snapshot(a.state_path(p), s)"
    )
    import os

    scripts = (
        Path(__file__).resolve().parents[1]
        / "skills"
        / "delegating-to-opencode"
        / "scripts"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(scripts) + os.pathsep + env.get("PYTHONPATH", "")
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", code, str(state_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        for _ in range(2)
    ]
    for index, process in enumerate(processes):
        _stdout, stderr = process.communicate(timeout=30)
        if process.returncode != 0:
            Path(f".aikit/pytest-tmp/proc-{index}.stderr").write_bytes(stderr)
        assert process.returncode == 0
    loaded = a.read_snapshot(a.state_path(state_dir))
    assert loaded is not None
    assert loaded.generation >= 1


def test_catalog_contexts_do_not_merge_quota_across_projects() -> None:
    snapshot = a.AvailabilitySnapshot(
        schema_version=a.STATE_SCHEMA_VERSION,
        generation=1,
        published_at=datetime.fromisoformat("2026-10-31T14:53:46+00:00"),
        catalog_contexts=(
            a.CatalogContext(
                project_key="project-a", config_sources=("global", "project")
            ),
            a.CatalogContext(project_key="project-b", config_sources=("global",)),
        ),
        models={
            "opencode-go/iceman-contributor-free": a.ModelEntry(
                metadata=a.ModelMetadata(
                    model="opencode-go/iceman-contributor-free",
                    name="Iceman Contributor Free",
                    pricing=(a.PricingTier(input=0.0, output=0.0),),
                    variants=("high",),
                    tools=True,
                    input_modalities=("text",),
                    output_modalities=("text",),
                    context_limit=200000,
                    output_limit=32000,
                    free_candidate=True,
                    may_use_openai_quota=False,
                ),
                quota=None,
                context_key="project-a",
            )
        },
        data_sources=(a.DataSourceStatus(name="go", status="ok", error_code=None),),
    )
    assert {entry.context_key for entry in snapshot.models.values()} == {"project-a"}


def test_serialized_state_excludes_workspace_and_credentials(tmp_path: Path) -> None:
    path = tmp_path / "state" / "availability-state.json"
    a.write_snapshot(path, _snapshot(_record()))
    text = path.read_text(encoding="utf-8")
    for forbidden in ("workspace", "usageURL", "password", "token", "credential"):
        assert forbidden not in text
