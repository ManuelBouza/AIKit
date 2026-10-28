"""Política, resolución de binario y cancelación del proceso propio."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import Mock

import delegate
import pytest


def test_policy_only_contains_preferences() -> None:
    assert delegate.load_policy() == {
        "prefer_free": True,
        "require_selection_reason": True,
    }


def test_policy_rejects_invalid_shape(tmp_path: Path) -> None:
    path = tmp_path / "policy.json"
    path.write_text(json.dumps({"default_model": "x"}), encoding="utf-8")
    with pytest.raises(delegate.DelegateError) as error:
        delegate.load_policy(path)
    assert error.value.code == "policy_invalid"


def test_windows_npm_shim_resolves_to_sibling_exe(tmp_path: Path) -> None:
    shim = tmp_path / "opencode.ps1"
    shim.write_text("shim", encoding="utf-8")
    exe = tmp_path / "node_modules" / "@opencode" / "cli" / "bin" / "opencode.exe"
    exe.parent.mkdir(parents=True)
    exe.write_text("exe", encoding="utf-8")
    assert Path(delegate.resolve_opencode(str(shim), is_windows=True)) == exe


@pytest.mark.parametrize("suffix", [".cmd", ".bat", ".ps1"])
def test_windows_shim_without_native_exe_rejected(tmp_path: Path, suffix: str) -> None:
    shim = tmp_path / ("opencode" + suffix)
    shim.write_text("shim", encoding="utf-8")
    with pytest.raises(delegate.DelegateError) as error:
        delegate.resolve_opencode(str(shim), is_windows=True)
    assert error.value.code == "opencode_missing"


def test_unknown_windows_extension_rejected(tmp_path: Path) -> None:
    script = tmp_path / "opencode.py"
    script.write_text("script", encoding="utf-8")
    with pytest.raises(delegate.DelegateError) as error:
        delegate.resolve_opencode(str(script), is_windows=True)
    assert error.value.code == "opencode_missing"


def test_direct_windows_exe_accepted(tmp_path: Path) -> None:
    exe = tmp_path / "opencode.exe"
    exe.write_text("exe", encoding="utf-8")
    assert Path(delegate.resolve_opencode(str(exe), is_windows=True)) == exe


def test_unix_binary_used_as_found() -> None:
    assert (
        delegate.resolve_opencode("/usr/local/bin/opencode", is_windows=False)
        == "/usr/local/bin/opencode"
    )


def test_process_timeout_kills_only_own_tree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class FakeProcess:
        pid = 4321
        returncode = 0

        def __init__(self) -> None:
            self.calls = 0

        def communicate(self, timeout: float | None = None) -> tuple[str, str]:
            self.calls += 1
            if self.calls == 1:
                assert timeout is not None
                raise subprocess.TimeoutExpired(["opencode"], timeout)
            return "", ""

    process = FakeProcess()
    popen = Mock(return_value=process)
    kill = Mock()
    monkeypatch.setattr(subprocess, "Popen", popen)
    monkeypatch.setattr(delegate, "_kill_tree", kill)
    with pytest.raises(delegate.DelegateError) as error:
        delegate.run_process(["opencode"], cwd=tmp_path, timeout=1)
    assert error.value.code == "timeout"
    kill.assert_called_once_with(process)
    assert popen.call_args.kwargs["shell"] is False
    assert popen.call_args.kwargs["cwd"] == str(tmp_path)
