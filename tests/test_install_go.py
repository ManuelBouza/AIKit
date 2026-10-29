import json
import subprocess
import sys
from pathlib import Path

import pytest
from install_go import BEGIN, END, install_go

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install_go.py"
TEMPLATE = Path(__file__).resolve().parents[1] / "config" / "codex" / "go.md"


def make_codex(tmp_path: Path) -> Path:
    d = tmp_path / "codex"
    d.mkdir()
    return d


def test_absent_profile(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    backup = install_go(ch, TEMPLATE)
    assert backup is not None
    assert (ch / "AGENTS.md").exists()
    assert BEGIN in (ch / "AGENTS.md").read_text()


def test_empty_profile(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.md").write_text("", encoding="utf-8")
    backup = install_go(ch, TEMPLATE)
    assert backup is not None


def test_idempotent_no_backup(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    install_go(ch, TEMPLATE)
    mtime = (ch / "AGENTS.md").stat().st_mtime
    res = install_go(ch, TEMPLATE)
    assert res is None
    assert (ch / "AGENTS.md").stat().st_mtime == mtime


def test_preserves_foreign_bytes(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    foreign = b"hello\r\nworld\r\n"
    (ch / "AGENTS.md").write_bytes(foreign)
    install_go(ch, TEMPLATE)
    data = (ch / "AGENTS.md").read_bytes()
    assert data.startswith(foreign) or foreign in data


def test_bom_crlf(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.md").write_bytes(b"\xef\xbb\xbf# hi\r\n")
    install_go(ch, TEMPLATE)
    data = (ch / "AGENTS.md").read_bytes()
    assert data.startswith(b"\xef\xbb\xbf")


def test_malformed_markers_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.md").write_text("<!-- AIKIT:GO:BEGIN -->\nno end", encoding="utf-8")
    with pytest.raises(ValueError, match="."):
        install_go(ch, TEMPLATE)


def test_duplicate_markers_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.md").write_text(f"{BEGIN}\n{END}\n{BEGIN}\n{END}", encoding="utf-8")
    with pytest.raises(ValueError, match="."):
        install_go(ch, TEMPLATE)


def test_override_nonempty_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.override.md").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="."):
        install_go(ch, TEMPLATE)


def test_symlink_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    target = tmp_path / "real.md"
    target.write_text("hi", encoding="utf-8")
    link = ch / "AGENTS.md"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("no symlink support")
    with pytest.raises(ValueError, match="."):
        install_go(ch, TEMPLATE)


def test_override_whitespace_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.override.md").write_bytes(b"   \n")
    with pytest.raises(ValueError, match="."):
        install_go(ch, TEMPLATE)


def test_backup_exact_bytes(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    foreign = b"hello\r\nworld\r\n"
    (ch / "AGENTS.md").write_bytes(foreign)
    backup = install_go(ch, TEMPLATE)
    assert backup is not None
    assert backup.read_bytes() == foreign


def test_absent_profile_state(tmp_path: Path) -> None:
    ch = tmp_path / "missing-profile"
    backup = install_go(ch, TEMPLATE)
    assert backup is not None
    assert backup.is_dir()
    assert (backup / "STATE.txt").read_text(
        encoding="utf-8"
    ) == "AGENTS.md no existía originalmente.\n"
    assert (ch / "AGENTS.md").exists()


def test_noop_no_new_backups_or_mtime(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    install_go(ch, TEMPLATE)
    mtime = (ch / "AGENTS.md").stat().st_mtime
    backups_before = (
        list((ch / "backups" / "aikit").iterdir())
        if (ch / "backups" / "aikit").exists()
        else []
    )
    res = install_go(ch, TEMPLATE)
    assert res is None
    assert (ch / "AGENTS.md").stat().st_mtime == mtime
    backups_after = (
        list((ch / "backups" / "aikit").iterdir())
        if (ch / "backups" / "aikit").exists()
        else []
    )
    assert backups_after == backups_before


def test_update_block_preserves_exterior(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    prefix = b"prefix-line\r\n"
    suffix = b"\r\nsuffix-line\r\n"
    (ch / "AGENTS.md").write_bytes(
        prefix + b"<!-- AIKIT:GO:BEGIN -->\nold\n<!-- AIKIT:GO:END -->" + suffix
    )
    install_go(ch, TEMPLATE)
    data = (ch / "AGENTS.md").read_bytes()
    assert data.startswith(prefix)
    assert data.endswith(suffix)
    assert b"old" not in data


def test_bom_crlf_preserved(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.md").write_bytes(b"\xef\xbb\xbf# hi\r\n")
    install_go(ch, TEMPLATE)
    data = (ch / "AGENTS.md").read_bytes()
    assert data.startswith(b"\xef\xbb\xbf")
    assert b"# hi\r\n" in data


def test_malformed_template_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    bad = tmp_path / "bad-template.md"
    bad.write_text("<!-- AIKIT:GO:BEGIN -->\nno end", encoding="utf-8")
    with pytest.raises(ValueError, match="."):
        install_go(ch, bad)


def test_duplicate_template_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    bad = tmp_path / "dup-template.md"
    bad.write_text(f"{BEGIN}\n{END}\n{BEGIN}\n{END}", encoding="utf-8")
    with pytest.raises(ValueError, match="."):
        install_go(ch, bad)


def test_symlink_no_writes(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    target = tmp_path / "real.md"
    target.write_text("hi", encoding="utf-8")
    link = ch / "AGENTS.md"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("no symlink support")
    before = target.read_bytes()
    with pytest.raises(ValueError, match="."):
        install_go(ch, TEMPLATE)
    assert target.read_bytes() == before


@pytest.mark.parametrize("mutation_point", ["temporary", "backup"])
def test_concurrent_mutation_not_overwritten(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation_point: str
) -> None:
    ch = make_codex(tmp_path)
    agents = ch / "AGENTS.md"
    agents.write_bytes(b"foreign\r\n")
    import install_go as module

    original_write = Path.write_bytes

    def patched(self: Path, data: bytes) -> int:
        result = original_write(self, data)
        is_temporary = self.name.startswith(".agents.md.tmp-")
        is_backup = self.parent.parent == ch / "backups" / "aikit"
        if (mutation_point == "temporary" and is_temporary) or (
            mutation_point == "backup" and is_backup
        ):
            agents.write_bytes(b"concurrent-edit")
        return result

    monkeypatch.setattr(Path, "write_bytes", patched)
    with pytest.raises(ValueError, match="."):
        module.install_go(ch, TEMPLATE)
    assert agents.read_bytes() == b"concurrent-edit"
    assert not list(ch.glob(".agents.md.tmp-*"))


def test_cli_subprocess_changed(tmp_path: Path) -> None:
    ch = tmp_path / "absent-profile"
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--codex-home",
            str(ch),
            "--template",
            str(TEMPLATE),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "changed"
    assert payload["backup"] is not None
    assert (ch / "AGENTS.md").exists()


def test_cli_subprocess_unchanged(tmp_path: Path) -> None:
    ch = tmp_path / "profile"
    ch.mkdir()
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--codex-home",
            str(ch),
            "--template",
            str(TEMPLATE),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--codex-home",
            str(ch),
            "--template",
            str(TEMPLATE),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "unchanged"
    assert payload["backup"] is None
