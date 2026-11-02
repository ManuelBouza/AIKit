"""Regresión del precheck de propietario al finalizar la reconciliación."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from service_identity import HostContext, ServiceError
from session_store import load_task

from tests.fakes import FakeBinding
from tests.test_session_store import TASK_ID
from tests.test_session_worker import prepare, result, run_fake, worker
from tests.test_worker_reconciliation import _message_event, _seed


@pytest.mark.parametrize("precheck_failure", ["exception", "unverified"])
def test_owner_precheck_failure_persists_conservative_result_without_message_get(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    precheck_failure: str,
) -> None:
    directory = prepare(tmp_path)
    context = HostContext(tmp_path / "registration", tmp_path / "state", "2.2.0")
    binding = FakeBinding(context=context)
    _seed(tmp_path, context, binding)
    module = worker()
    monkeypatch.setattr(module, "discover_existing", lambda _context: binding)
    import delegate

    monkeypatch.setattr(delegate, "find_opencode", lambda: "C:/fake/opencode.exe")

    original_verify = binding.verify_owner
    checks = 0

    def verify(*, timeout: float = 1.0) -> Any:
        nonlocal checks
        checks += 1
        if checks == 4:
            if precheck_failure == "exception":
                raise ServiceError("owner_mismatch", "synthetic-private-detail")
            return None
        return original_verify(timeout=timeout)

    monkeypatch.setattr(binding, "verify_owner", verify)

    exit_code = run_fake(tmp_path, f"print({_message_event()!r})", context=context)

    assert exit_code == 1
    report = result(directory)
    record = load_task(tmp_path, TASK_ID)
    assert report["delivery"] == "pending"
    assert (
        "owner_verification_failed" in report["limitations"]
        or "owner_mismatch" in report["limitations"]
    )
    assert record.delivery is not None
    assert record.delivery.state == "pending"
    assert record.delivery.source != "durable_message"
    assert not any(call[0] == "session.message.get" for call in binding.request_calls)
    serialized = json.dumps(report)
    assert "synthetic-private-detail" not in serialized
    assert "fake-secret" not in serialized
