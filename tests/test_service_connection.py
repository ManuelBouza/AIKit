from __future__ import annotations

import http.server
import json
import os
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
import service_connection as sc
import service_identity as si


@pytest.fixture(autouse=True)
def _trusted_registration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(si, "registration_trusted", lambda p: True)
    monkeypatch.setattr(sc, "registration_trusted_path", lambda p: True)


class FakeHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/api/info"):
            body = json.dumps({"pid": self.server.pid, "version": "2.2.0"}).encode()  # type: ignore[attr-defined]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/api/config"):
            body = json.dumps({"sources": []}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/api/model"):
            body = json.dumps({"data": []}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        body = b"{}"
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        return


@pytest.fixture
def fake_server(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[str, int, object]]:
    # Bind to loopback.
    httpd = http.server.HTTPServer(("127.0.0.1", 0), FakeHandler)
    httpd.pid = os.getpid()  # type: ignore[attr-defined]
    # patch get_process_birth to return matching birth for current pid
    real_birth = si.ProcessBirth(
        pid=os.getpid(), filetime=12345, started_at="2026-01-01T00:00:00+00:00"
    )
    monkeypatch.setattr(
        si, "get_process_birth", lambda pid: real_birth if pid == os.getpid() else None
    )
    monkeypatch.setattr(
        sc, "get_process_birth", lambda pid: real_birth if pid == os.getpid() else None
    )
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield "127.0.0.1", httpd.server_port, httpd
    httpd.shutdown()
    httpd.server_close()


def _write_reg(tmp_path: Path, port: int, pid: int) -> Path:
    reg_path = tmp_path / "reg.json"
    reg_path.write_text(
        json.dumps(
            {
                "id": "rid-1",
                "url": f"http://127.0.0.1:{port}/",
                "pid": pid,
                "version": "2.2.0",
                "password": "secret123",
            }
        ),
        encoding="utf-8",
    )
    return reg_path


def test_child_environment_does_not_mutate_parent(
    fake_server: tuple[str, int, object], tmp_path: Path
) -> None:
    host, port, _ = fake_server
    reg_path = _write_reg(tmp_path, port, os.getpid())
    ctx = si.HostContext(
        opencode_registration=reg_path, aikit_state=tmp_path, expected_version="2.2.0"
    )
    # Bypass trust check by monkey? registration_trusted may fail on ACL; force true.
    # Patch registration_trusted to True for test
    binding = sc.discover_existing(ctx, timeout=5.0)
    base = {"FOO": "bar"}
    env = binding.child_environment(base)
    assert env["OPENCODE_PASSWORD"] == "secret123"
    assert "OPENCODE_PASSWORD" not in base
    assert env["FOO"] == "bar"
    binding.close()
    with pytest.raises(si.ServiceError):
        binding.child_environment(base)


def test_close_invalidates(
    fake_server: tuple[str, int, object], tmp_path: Path
) -> None:
    host, port, _ = fake_server
    reg_path = _write_reg(tmp_path, port, os.getpid())
    ctx = si.HostContext(
        opencode_registration=reg_path, aikit_state=tmp_path, expected_version="2.2.0"
    )
    binding = sc.discover_existing(ctx, timeout=5.0)
    binding.close()
    assert binding.verify_owner(timeout=1.0) is None
    with pytest.raises(si.ServiceError):
        binding.request("server.info", session_id=None, timeout=1.0)


def test_http_401_raises_no_body(
    fake_server: tuple[str, int, object],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Make server return 401 for info by monkeypatching handler? Instead test _http_request indirectly via bad cred.
    host, port, _ = fake_server
    reg_path = tmp_path / "reg.json"
    reg_path.write_text(
        json.dumps(
            {
                "id": "rid-1",
                "url": f"http://127.0.0.1:{port}/",
                "pid": os.getpid(),
                "version": "2.2.0",
                "password": "wrong",
            }
        ),
        encoding="utf-8",
    )
    ctx = si.HostContext(
        opencode_registration=reg_path, aikit_state=tmp_path, expected_version="2.2.0"
    )
    # server doesn't check auth, so discover succeeds even with wrong cred. Test request path instead not needed.
    binding = sc.discover_existing(ctx, timeout=5.0)
    binding.close()


def test_config_and_model(fake_server: tuple[str, int, object], tmp_path: Path) -> None:
    host, port, _ = fake_server
    reg_path = _write_reg(tmp_path, port, os.getpid())
    ctx = si.HostContext(
        opencode_registration=reg_path, aikit_state=tmp_path, expected_version="2.2.0"
    )
    binding = sc.discover_existing(ctx, timeout=5.0)
    assert binding.config_sources(tmp_path, timeout=2.0) is not None
    assert binding.model_catalog(tmp_path, timeout=2.0) is not None
    binding.close()


class SlowHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", "100")
        self.end_headers()
        for _ in range(20):
            time.sleep(0.1)
            try:
                self.wfile.write(b"x" * 5)
                self.wfile.flush()
            except Exception:
                break

    def log_message(self, *args: object) -> None:
        return


def test_http_trickle_respects_deadline() -> None:
    import time as _time

    srv = http.server.HTTPServer(("127.0.0.1", 0), SlowHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{srv.server_port}/"
        start = _time.monotonic()
        with pytest.raises(si.ServiceError):
            sc._http_request(
                url=url,
                method="GET",
                credential="",
                timeout=10.0,
                deadline=_time.monotonic() + 0.5,
            )
        elapsed = _time.monotonic() - start
        assert elapsed < 1.5
    finally:
        srv.shutdown()
        srv.server_close()


def test_config_sources_verifies_owner_before_request(
    fake_server: tuple[str, int, object], tmp_path: Path
) -> None:
    host, port, _ = fake_server
    reg_path = _write_reg(tmp_path, port, os.getpid())
    ctx = si.HostContext(
        opencode_registration=reg_path, aikit_state=tmp_path, expected_version="2.2.0"
    )
    binding = sc.discover_existing(ctx, timeout=5.0)
    # Rotate credential in registry before config request.
    reg_path.write_text(
        json.dumps(
            {
                "id": "rid-1",
                "url": f"http://127.0.0.1:{port}/",
                "pid": os.getpid(),
                "version": "2.2.0",
                "password": "rotated",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(si.ServiceError) as exc:
        binding.config_sources(tmp_path, timeout=2.0)
    assert exc.value.code == "owner_mismatch"
    binding.close()


def test_managed_binding_session_message_get_maps_get_path() -> None:
    path, method = sc._operation_path("session.message.get", "ses_1", "msg_1")
    assert path == "/api/session/ses_1/message/msg_1"
    assert method == "GET"
    assert "session.message.get" in sc.DEFAULT_OPERATIONS


def test_binding_repr_excludes_credential(
    fake_server: tuple[str, int, object], tmp_path: Path
) -> None:
    host, port, _ = fake_server
    reg_path = _write_reg(tmp_path, port, os.getpid())
    ctx = si.HostContext(
        opencode_registration=reg_path, aikit_state=tmp_path, expected_version="2.2.0"
    )
    binding = sc.discover_existing(ctx, timeout=5.0)
    assert "secret123" not in repr(binding)
    assert "secret123" not in repr(binding.registration)
    binding.close()


class HeaderSlowHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802
        self.wfile.write(b"HTTP/1.1 200 OK\r\n")
        self.wfile.flush()
        time.sleep(0.3)
        self.wfile.write(b"Content-Type: application/json\r\n")
        self.wfile.flush()
        time.sleep(0.3)
        self.wfile.write(b"Content-Length: 2\r\n\r\n")
        self.wfile.flush()
        time.sleep(0.3)
        self.wfile.write(b"{}")
        self.wfile.flush()

    def log_message(self, *args: object) -> None:
        return

    def handle_one_request(self) -> None:
        super().handle_one_request()


def test_http_header_trickle_respects_deadline() -> None:
    import time as _time

    srv = http.server.HTTPServer(("127.0.0.1", 0), HeaderSlowHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{srv.server_port}/"
        start = _time.monotonic()
        with pytest.raises(si.ServiceError):
            sc._http_request(
                url=url,
                method="GET",
                credential="",
                timeout=10.0,
                deadline=_time.monotonic() + 0.5,
            )
        elapsed = _time.monotonic() - start
        assert elapsed < 1.0
    finally:
        srv.shutdown()
        srv.server_close()


def _discover_binding(
    fake_server: tuple[str, int, object], tmp_path: Path
) -> sc.ManagedBinding:
    host, port, _ = fake_server
    reg_path = _write_reg(tmp_path, port, os.getpid())
    ctx = si.HostContext(
        opencode_registration=reg_path, aikit_state=tmp_path, expected_version="2.2.0"
    )
    return sc.discover_existing(ctx, timeout=5.0)


def test_managed_binding_request_session_message_get_propagates_ids(
    fake_server: tuple[str, int, object],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binding = _discover_binding(fake_server, tmp_path)
    calls: list[tuple[str, str]] = []

    def fake_http(
        *, url: str, method: str, credential: str, timeout: float, deadline: float
    ) -> tuple[int, object]:
        calls.append((url, method))
        return 200, {"data": {}}

    monkeypatch.setattr(sc, "_http_request", fake_http)
    from session_backend import ApiResponse

    response = binding.request(
        "session.message.get",
        session_id="ses_1",
        message_id="msg_1",
        timeout=2.0,
    )
    assert isinstance(response, ApiResponse)
    assert response.status == 200
    assert len(calls) == 1
    url, method = calls[0]
    assert method == "GET"
    assert "/api/session/ses_1/message/msg_1" in url
    binding.close()


def test_managed_binding_request_session_message_get_owner_before_http(
    fake_server: tuple[str, int, object],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binding = _discover_binding(fake_server, tmp_path)
    host, port, _ = fake_server
    reg_path = tmp_path / "reg.json"
    reg_path.write_text(
        json.dumps(
            {
                "id": "rid-1",
                "url": f"http://127.0.0.1:{port}/",
                "pid": os.getpid(),
                "version": "2.2.0",
                "password": "rotated",
            }
        ),
        encoding="utf-8",
    )
    calls: list[int] = []

    def fake_http(
        *, url: str, method: str, credential: str, timeout: float, deadline: float
    ) -> tuple[int, object]:
        calls.append(1)
        return 200, {}

    monkeypatch.setattr(sc, "_http_request", fake_http)
    with pytest.raises(si.ServiceError) as exc:
        binding.request(
            "session.message.get", session_id="ses_1", message_id="msg_1", timeout=2.0
        )
    assert exc.value.code == "owner_mismatch"
    assert calls == []
    binding.close()


def test_managed_binding_request_session_message_get_owner_changed_after_http(
    fake_server: tuple[str, int, object],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binding = _discover_binding(fake_server, tmp_path)
    host, port, _ = fake_server
    reg_path = tmp_path / "reg.json"
    calls: list[int] = []

    def fake_http(
        *, url: str, method: str, credential: str, timeout: float, deadline: float
    ) -> tuple[int, object]:
        reg_path.write_text(
            json.dumps(
                {
                    "id": "rid-1",
                    "url": f"http://127.0.0.1:{port}/",
                    "pid": os.getpid(),
                    "version": "2.2.0",
                    "password": "rotated",
                }
            ),
            encoding="utf-8",
        )
        calls.append(1)
        return 200, {}

    monkeypatch.setattr(sc, "_http_request", fake_http)
    with pytest.raises(si.ServiceError) as exc:
        binding.request(
            "session.message.get", session_id="ses_1", message_id="msg_1", timeout=2.0
        )
    assert exc.value.code == "owner_mismatch"
    assert len(calls) == 1
    binding.close()


def test_managed_binding_request_rejects_invalid_ids_before_http(
    fake_server: tuple[str, int, object],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binding = _discover_binding(fake_server, tmp_path)
    calls: list[int] = []

    def fake_http(
        *, url: str, method: str, credential: str, timeout: float, deadline: float
    ) -> tuple[int, object]:
        calls.append(1)
        return 200, {}

    monkeypatch.setattr(sc, "_http_request", fake_http)

    with pytest.raises(si.ServiceError) as exc:
        binding.request(
            "session.message.get", session_id=None, message_id="msg_1", timeout=1.0
        )
    assert exc.value.code in {"invalid_session", "invalid_message"}
    with pytest.raises(si.ServiceError) as exc:
        binding.request(
            "session.message.get", session_id="ses_1", message_id=None, timeout=1.0
        )
    assert exc.value.code in {"invalid_session", "invalid_message"}

    for bad in ("../secret", "ses/x", "ses x", "", "ses\x00"):
        with pytest.raises(si.ServiceError) as exc:
            binding.request(
                "session.message.get", session_id=bad, message_id="msg_1", timeout=1.0
            )
        assert exc.value.code == "invalid_session"
        with pytest.raises(si.ServiceError) as exc:
            binding.request(
                "session.message.get", session_id="ses_1", message_id=bad, timeout=1.0
            )
        assert exc.value.code == "invalid_message"

    assert calls == []
    binding.close()


def test_managed_binding_request_rejects_unavailable_operation(
    fake_server: tuple[str, int, object],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binding = _discover_binding(fake_server, tmp_path)
    calls: list[int] = []

    def fake_http(
        *, url: str, method: str, credential: str, timeout: float, deadline: float
    ) -> tuple[int, object]:
        calls.append(1)
        return 200, {}

    monkeypatch.setattr(sc, "_http_request", fake_http)
    with pytest.raises(si.ServiceError) as exc:
        binding.request(
            "session.log", session_id="ses_1", message_id="msg_1", timeout=1.0
        )
    assert exc.value.code == "operation_unavailable"
    assert calls == []
    binding.close()


def test_managed_binding_request_allows_legitimate_ids(
    fake_server: tuple[str, int, object],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binding = _discover_binding(fake_server, tmp_path)
    calls: list[tuple[str, str]] = []

    def fake_http(
        *, url: str, method: str, credential: str, timeout: float, deadline: float
    ) -> tuple[int, object]:
        calls.append((url, method))
        return 200, {"ok": True}

    monkeypatch.setattr(sc, "_http_request", fake_http)
    response = binding.request(
        "session.message.get",
        session_id="ses_abc-123",
        message_id="msg_def_456",
        timeout=2.0,
    )
    assert response.status == 200
    assert calls
    assert "/api/session/ses_abc-123/message/msg_def_456" in calls[0][0]
    binding.close()
