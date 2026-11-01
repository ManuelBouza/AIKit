"""Pruebas de refresh read-only y coalescencia."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

import availability_refresh as ar
import availability_state as a
import pytest
from service_identity import HostContext

from tests.fakes import FakeBinding, api_model


def _utc(value: str) -> datetime:
    return datetime.fromisoformat(value)


def test_go_refresh_whitelist_and_aggregate(tmp_path: Path) -> None:
    context = HostContext(tmp_path / "reg.json", tmp_path / "state", "2.2.0")
    context.aikit_state.mkdir(parents=True, exist_ok=True)
    binding = FakeBinding(
        context=context,
        catalog=[api_model(provider="opencode-go", model_id="iceman-contributor-free")],
        usage_limits_data={
            "location": {"directory": str(tmp_path / "project")},
            "data": {
                "workspace": {
                    "id": "ws-ficticio",
                    "usageURL": "https://example.invalid/usage",
                },
                "go": {
                    "rolling": {
                        "percent": 0,
                        "limited": False,
                        "resetsAt": 1793476425740,
                    },
                    "weekly": {
                        "percent": 100,
                        "limited": True,
                        "resetsAt": 1793577600000,
                    },
                    "monthly": {
                        "percent": 50,
                        "limited": False,
                        "resetsAt": 1795887585000,
                    },
                },
                "budgets": [],
            },
        },
        openapi={"paths": {"/api/experimental/usage/limits": {"get": {}}}},
        integrations_data={
            "location": {"directory": str(tmp_path / "project")},
            "data": [{"id": "kilo", "name": "Kilo", "connections": 1}],
        },
    )
    project = tmp_path / "project"
    project.mkdir()
    context = HostContext(project / "reg.json", tmp_path / "state", "2.2.0")
    context.aikit_state.mkdir(parents=True, exist_ok=True)
    state = tmp_path / "state" / "availability-state.json"
    binding.context = context
    result = ar.coalesced_refresh(state, binding, project, 10.0, force=True)
    assert result.refreshed is True
    assert "opencode-go/iceman-contributor-free" in result.snapshot.models
    assert result.snapshot.aggregates
    assert result.snapshot.aggregates[0].observation.limited is True
    text = state.read_text(encoding="utf-8")
    assert "usageURL" not in text
    assert "workspace" not in text


def test_experimental_failure_keeps_last_valid(tmp_path: Path) -> None:
    state = tmp_path / "state" / "availability-state.json"
    state.parent.mkdir(parents=True)
    previous = a.empty_snapshot()
    a.write_snapshot(state, previous)
    context = HostContext(tmp_path / "reg.json", tmp_path / "state", "2.2.0")
    context.aikit_state.mkdir(parents=True, exist_ok=True)
    binding = FakeBinding(
        context=context,
        catalog=[api_model(provider="opencode-go", model_id="beam-free")],
        usage_limits_error="service_unavailable",
    )
    project = tmp_path / "project"
    project.mkdir()
    result = ar.coalesced_refresh(state, binding, project, 10.0, force=True)
    assert result.refreshed is True
    assert result.snapshot.models["opencode-go/beam-free"].quota is None
    assert any(source.status == "error" for source in result.snapshot.data_sources)


def test_two_processes_coalesce_refresh(tmp_path: Path) -> None:
    state = tmp_path / "state" / "availability-state.json"
    state.parent.mkdir(parents=True)
    context = HostContext(tmp_path / "reg.json", tmp_path / "state", "2.2.0")
    context.aikit_state.mkdir(parents=True, exist_ok=True)
    _ = FakeBinding(
        context=context,
        catalog=[api_model(provider="opencode", model_id="mimo-v2.6-flash-free")],
    )
    project = tmp_path / "project"
    project.mkdir()

    import os
    import subprocess
    import sys

    scripts = (
        Path(__file__).resolve().parents[1]
        / "skills"
        / "delegating-to-opencode"
        / "scripts"
    )
    code = (
        "import sys; from pathlib import Path; import availability_refresh as ar; import availability_state as a; "
        "from service_identity import HostContext; from tests.fakes import FakeBinding, api_model; "
        "p=Path(sys.argv[1]); proj=Path(sys.argv[2]); ctx=HostContext(proj/'reg.json', p, '2.2.0'); ctx.aikit_state.mkdir(parents=True, exist_ok=True); b=FakeBinding(context=ctx, catalog=[api_model()]); "
        "ar.coalesced_refresh(a.state_path(p), b, proj, 10.0, force=True)"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(scripts) + os.pathsep + env.get("PYTHONPATH", "")
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", code, str(state.parent), str(project)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            creationflags=__import__("subprocess").CREATE_NO_WINDOW
            if sys.platform == "win32"
            else 0,
        )
        for _ in range(2)
    ]
    for process in processes:
        out, err = process.communicate(timeout=30)
        assert process.returncode == 0, err.decode("utf-8", "replace")
    loaded = a.read_snapshot(state)
    assert loaded is not None
    assert loaded.generation >= 1


def healthy(tmp_path: Path) -> tuple[Path, FakeBinding, Path]:
    project = tmp_path / "project"
    project.mkdir(exist_ok=True)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    return (
        context.aikit_state / "availability-state.json",
        FakeBinding(context=context),
        project,
    )


def test_total_deadline_is_shared_between_sources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state, binding, project = healthy(tmp_path)

    def wait(*args: Any, timeout: float) -> object:
        time.sleep(min(0.04, timeout))
        return {"paths": {"/api/experimental/usage/limits": {"get": {}}}}

    monkeypatch.setattr(binding, "openapi_schema", wait)
    monkeypatch.setattr(binding, "integrations", wait)
    monkeypatch.setattr(binding, "model_catalog", wait)
    monkeypatch.setattr(binding, "usage_limits", wait)
    start = time.monotonic()
    ar.coalesced_refresh(state, binding, project, 0.1, force=True)
    assert time.monotonic() - start < 0.14


def test_failed_catalog_preserves_models_and_project_context(tmp_path: Path) -> None:
    state, binding, project = healthy(tmp_path)
    first = ar.coalesced_refresh(state, binding, project, 2, force=True)
    binding.catalog_returncode = 1
    failed = ar.coalesced_refresh(state, binding, project, 2, force=True)
    assert failed.snapshot.models == first.snapshot.models
    assert failed.snapshot.catalog_contexts == first.snapshot.catalog_contexts
    assert any(
        source.name == "catalog" and source.status == "error"
        for source in failed.snapshot.data_sources
    )


@pytest.mark.parametrize("limited", [None, 0, 1, "false", [], {}])
def test_usage_limited_requires_strict_bool(limited: object, tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    assert (
        ar._parse_usage_limits(
            {
                "location": {"directory": str(project)},
                "data": {"go": {"weekly": {"limited": limited, "percent": 0}}},
            },
            project,
        )
        is None
    )


def test_usage_endpoint_absent_is_not_an_ok_source(tmp_path: Path) -> None:
    state, binding, project = healthy(tmp_path)
    binding.openapi = {"paths": {}}
    result = ar.coalesced_refresh(state, binding, project, 2, force=True)
    assert (
        next(s for s in result.snapshot.data_sources if s.name == "usage_limits").status
        != "ok"
    )
    assert not any(kind == "usage" for kind, _ in binding.calls)


def test_pricing_tiers_preserve_every_rate_and_context_threshold(
    tmp_path: Path,
) -> None:
    state, binding, project = healthy(tmp_path)
    binding.catalog = [
        api_model(
            cost=[
                {"input": 1, "output": 2, "cache": {"read": 0.2, "write": 0.3}},
                {"input": 3, "output": 4, "tier": {"type": "context", "size": 200000}},
            ]
        )
    ]
    result = ar.coalesced_refresh(state, binding, project, 2, force=True)
    tiers = next(iter(result.snapshot.models.values())).metadata.pricing
    assert [(t.input, t.output) for t in tiers] == [(1, 2), (3, 4)]
    assert tiers[0].cache_read == 0.2
    assert tiers[1].context_size == 200000
    loaded = a.read_snapshot(state)
    assert loaded is not None
    assert next(iter(loaded.models.values())).metadata.pricing == tiers


@pytest.mark.parametrize("broken", [False, True])
def test_two_processes_count_real_source_reads_once_even_on_failure(
    tmp_path: Path, broken: bool
) -> None:
    import os
    import subprocess
    import sys

    state = tmp_path / "state" / "availability-state.json"
    state.parent.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    counter = tmp_path / "reads.log"
    scripts = str(Path(ar.__file__).parent)
    repo = str(Path.cwd())
    code = f"""
import sys,time
from pathlib import Path
sys.path[:0]=[{scripts!r},{repo!r}]
import availability_refresh as ar
from service_identity import HostContext
from tests.fakes import FakeBinding
root=Path({str(tmp_path)!r}); state=Path({str(state)!r}); project=Path({str(project)!r})
original=ar.read_snapshot
first=True
def initial(path):
 global first
 value=original(path)
 if first:
  first=False
  (root/('ready-'+sys.argv[1])).touch()
  end=time.monotonic()+5
  while len(list(root.glob('ready-*')))<2 and time.monotonic()<end: time.sleep(.005)
 return value
ar.read_snapshot=initial
class Counted(FakeBinding):
 def hit(self,name):
  with Path({str(counter)!r}).open('a') as out: out.write(name+'\\n')
 def openapi_schema(self,*,timeout):
  self.hit('openapi'); return super().openapi_schema(timeout=timeout)
 def integrations(self,*,timeout):
  self.hit('integrations'); return super().integrations(timeout=timeout)
 def model_catalog(self,project,*,timeout):
  self.hit('catalog')
  if {broken!r}: raise OSError('fake unavailable')
  return super().model_catalog(project,timeout=timeout)
 def usage_limits(self,project,*,timeout):
  self.hit('usage'); return super().usage_limits(project,timeout=timeout)
binding=Counted(context=HostContext(root/'registration',state.parent,'2.2.0'))
ar.coalesced_refresh(state,binding,project,3,force=True)
"""
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    workers = [
        subprocess.Popen(
            [sys.executable, "-c", code, str(i)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=flags,
        )
        for i in range(2)
    ]
    for worker in workers:
        stdout, stderr = worker.communicate(timeout=10)
        assert worker.returncode == 0, stderr.decode()
    assert sorted(counter.read_text().splitlines()) == [
        "catalog",
        "integrations",
        "openapi",
        "usage",
    ]
    loaded = a.read_snapshot(state)
    assert loaded is not None
    assert loaded.generation == 1
    assert next(
        source for source in loaded.data_sources if source.name == "catalog"
    ).status == ("error" if broken else "ok")


def test_real_http_respects_total_refresh_deadline(tmp_path: Path) -> None:
    import http.server
    import json
    import threading

    import service_connection as sc
    import service_identity as si
    from session_backend import OwnerIdentity

    requests = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            pass

        def do_GET(self) -> None:  # noqa: N802
            requests.append(self.path)
            time.sleep(0.08)
            if self.path == "/openapi.json":
                payload: Any = {
                    "paths": {"/api/experimental/usage/limits": {"get": {}}}
                }
            else:
                payload = []
            raw = json.dumps(payload).encode()
            try:
                self.send_response(200)
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
            except OSError:
                pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    state, _, project = healthy(tmp_path)
    context = HostContext(tmp_path / "registration", state.parent, "2.2.0")
    reg = si.ServiceRegistration(
        "fake", f"http://127.0.0.1:{server.server_port}/", 123, "2.2.0", "fictitious"
    )
    owner = OwnerIdentity("test", 123, "2026-10-31T00:00:00+00:00", "2.2.0")
    binding = sc.ManagedBinding(reg, context, owner, "test")
    binding.verify_owner = lambda **kwargs: owner  # type: ignore[method-assign]
    try:
        start = time.monotonic()
        result = ar.coalesced_refresh(state, binding, project, 0.12, force=True)
        elapsed = time.monotonic() - start
        assert elapsed < 0.20
        assert len(requests) == 2
        assert result.errors
    finally:
        binding.close()
        server.shutdown()
        server.server_close()
        thread.join(2)


def test_refresh_publication_lock_uses_remaining_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from types import SimpleNamespace

    from session_store import _lock_file

    state, binding, project = healthy(tmp_path)
    state.parent.mkdir(parents=True)
    clock = [0.0]

    def wait(seconds: float) -> None:
        clock[0] += seconds

    monkeypatch.setattr(
        a, "time", SimpleNamespace(monotonic=lambda: clock[0], sleep=wait)
    )
    with _lock_file(state.parent / (a.STATE_FILENAME + ".lock")):
        result = ar.coalesced_refresh(state, binding, project, 0.1, force=True)
    assert clock[0] <= 0.1
    assert not result.refreshed
    assert not state.exists()
    assert len(binding.catalog_calls) == 1


def test_usage_location_must_match_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    other = tmp_path / "other"
    other.mkdir()
    valid_payload = {
        "location": {"directory": str(project)},
        "data": {
            "go": {
                "rolling": {"percent": 0, "limited": False, "resetsAt": 1},
                "weekly": {"percent": 100, "limited": True, "resetsAt": 2},
            }
        },
    }
    assert ar._parse_usage_limits(valid_payload, project) is not None

    mismatched_payload = {
        "location": {"directory": str(other)},
        "data": valid_payload["data"],
    }
    assert ar._parse_usage_limits(mismatched_payload, project) is None

    missing_location = {"data": valid_payload["data"]}
    assert ar._parse_usage_limits(missing_location, project) is None

    invalid_location = {
        "location": {"directory": "relative/path"},
        "data": valid_payload["data"],
    }
    assert ar._parse_usage_limits(invalid_location, project) is None


def test_usage_location_mismatch_preserves_last_valid_aggregate(
    tmp_path: Path,
) -> None:
    state = tmp_path / "state" / "availability-state.json"
    state.parent.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    other = tmp_path / "other"
    other.mkdir()
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    context.aikit_state.mkdir(parents=True, exist_ok=True)
    valid_payload = {
        "location": {"directory": str(project)},
        "data": {
            "go": {
                "rolling": {"percent": 0, "limited": False, "resetsAt": 1},
                "weekly": {"percent": 100, "limited": True, "resetsAt": 2},
            }
        },
    }
    binding = FakeBinding(
        context=context,
        catalog=[api_model(provider="opencode-go", model_id="beam-free")],
        usage_limits_data=valid_payload,
        openapi={"paths": {"/api/experimental/usage/limits": {"get": {}}}},
    )
    first = ar.coalesced_refresh(state, binding, project, 2.0, force=True)
    assert first.errors == ()
    assert first.snapshot.aggregates
    previous = first.snapshot.aggregates

    binding.usage_limits_data = {
        "location": {"directory": str(other)},
        "data": valid_payload["data"],
    }
    second = ar.coalesced_refresh(state, binding, project, 2.0, force=True)
    assert "usage_limits_unavailable" in second.errors
    assert second.snapshot.aggregates == previous

    binding.usage_limits_data = valid_payload
    third = ar.coalesced_refresh(state, binding, project, 2.0, force=True)
    assert third.errors == ()
    assert third.snapshot.aggregates
