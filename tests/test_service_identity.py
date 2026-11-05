from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import service_identity as si


def test_resolve_host_context_requires_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AIKIT_OPENCODE_REGISTRATION", raising=False)
    monkeypatch.delenv("AIKIT_STATE", raising=False)
    with pytest.raises(si.ServiceError):
        si.resolve_host_context()


def test_canonical_url_valid() -> None:
    assert si.canonical_url("http://127.0.0.1:4096/") == "http://127.0.0.1:4096/"


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com:4096/",
        "http://127.0.0.1:4096/foo",
        "http://user:pass@127.0.0.1:4096/",
        "http://127.0.0.1:4096/?q=1",
        "http://127.0.0.1:4096/#frag",
        "ftp://127.0.0.1:4096/",
        "http://127.0.0.1/",
        "not-a-url",
    ],
)
def test_canonical_url_invalid(url: str) -> None:
    with pytest.raises(si.ServiceError):
        si.canonical_url(url)


def test_parse_registration_size_limit() -> None:
    big = b"{" + b'"a":1,' * 10000 + b'"b":2}'
    # ensure >64KiB
    big = big + b" " * (si.MAX_REGISTRATION_BYTES + 10)
    with pytest.raises(si.ServiceError):
        si.parse_registration_bytes(big)


def test_parse_registration_depth_limit() -> None:
    # depth 9
    value: object = 1
    for _ in range(10):
        value = {"a": value}
    raw = json.dumps(value).encode()
    with pytest.raises(si.ServiceError):
        si.parse_registration_bytes(raw)


def test_token_deterministic() -> None:
    reg = si.ServiceRegistration(
        registration_id="rid",
        url="http://127.0.0.1:4096/",
        pid=123,
        version="2.2.0",
        credential="secret",
    )
    birth = si.ProcessBirth(
        pid=123, filetime=999, started_at="2026-01-01T00:00:00+00:00"
    )
    t1 = si.token_for(reg, birth, "2.2.0")
    t2 = si.token_for(reg, birth, "2.2.0")
    assert t1 == t2
    assert t1.startswith("aikit-owner-v1-")
    assert "secret" not in t1


def test_registration_repr_redacts() -> None:
    reg = si.ServiceRegistration(
        registration_id="rid",
        url="http://127.0.0.1:4096/",
        pid=123,
        version="2.2.0",
        credential="secret",
    )
    assert "secret" not in repr(reg)
    assert "redacted" in repr(reg)


def test_registration_trusted_reparse(tmp_path: Path) -> None:
    p = tmp_path / "reg.json"
    p.write_text("{}", encoding="utf-8")
    # Normal file should be trusted on this platform at least structurally.
    # We don't assert True on windows security; just callable.
    assert isinstance(si.registration_trusted(p), bool)


def test_validate_registration_rejects_missing_id(tmp_path: Path) -> None:
    ctx = si.HostContext(
        opencode_registration=tmp_path / "r.json",
        aikit_state=tmp_path,
        expected_version="2.2.0",
    )
    with pytest.raises(si.ServiceError) as exc:
        si.validate_registration(
            {"url": "http://127.0.0.1:1/", "pid": 1, "version": "2.2.0"}, ctx
        )
    assert exc.value.code == "registration_invalid"


def test_validate_registration_accepts_different_version(tmp_path: Path) -> None:
    ctx = si.HostContext(
        opencode_registration=tmp_path / "r.json",
        aikit_state=tmp_path,
        expected_version="2.2.0",
    )
    registration = si.validate_registration(
        {"id": "r", "url": "http://127.0.0.1:1/", "pid": 1, "version": "2.3.0"}, ctx
    )
    assert registration.version == "2.3.0"


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL")
def test_registration_trusted_own_temp_file(tmp_path: Path) -> None:
    p = tmp_path / "reg.json"
    p.write_text("{}", encoding="utf-8")
    assert si.registration_trusted(p) is True


@pytest.mark.skipif(sys.platform != "win32", reason="Windows ACL")
def test_registration_trusted_rejects_foreign_write(tmp_path: Path) -> None:
    import subprocess

    p = tmp_path / "reg.json"
    p.write_text("{}", encoding="utf-8")
    assert si.registration_trusted(p) is True
    subprocess.run(
        ["icacls", str(p), "/grant", "*S-1-1-0:W"],
        capture_output=True,
        check=True,
    )
    assert si.registration_trusted(p) is False


@pytest.mark.skipif(sys.platform != "win32", reason="Windows process birth")
def test_get_process_birth_own_pid() -> None:
    import os

    birth = si.get_process_birth(os.getpid())
    assert birth is not None
    assert birth.pid == os.getpid()
    assert birth.filetime > 0


def test_read_registration_oversize(tmp_path: Path) -> None:
    reg_path = tmp_path / "reg.json"
    reg_path.write_bytes(b"{" + b" " * (si.MAX_REGISTRATION_BYTES + 100) + b"}")
    ctx = si.HostContext(
        opencode_registration=reg_path, aikit_state=tmp_path, expected_version="2.2.0"
    )
    # Bypass ACL for this size-focused test.
    original = si.registration_trusted
    si.registration_trusted = lambda p: True  # type: ignore[assignment]
    try:
        with pytest.raises(si.ServiceError) as exc:
            si.read_registration(ctx)
        assert exc.value.code == "registration_too_large"
    finally:
        si.registration_trusted = original


def test_canonical_url_uppercase_host() -> None:
    assert si.canonical_url("http://LOCALHOST:4096/") == "http://localhost:4096/"


@pytest.mark.parametrize(
    "url", ["http://127.0.0.1:4096//", "http://127.0.0.1:4096/foo/"]
)
def test_canonical_url_rejects_non_root_path(url: str) -> None:
    with pytest.raises(si.ServiceError):
        si.canonical_url(url)
