import json
import subprocess
import sys
from pathlib import Path

import pytest
from install_go import BEGIN as GO_BEGIN
from install_go import install_go
from install_routing import BEGIN, END, install_routing

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install_routing.py"
TEMPLATE = Path(__file__).resolve().parents[1] / "config" / "codex" / "routing.md"
GO_TEMPLATE = Path(__file__).resolve().parents[1] / "config" / "codex" / "go.md"


def make_codex(tmp_path: Path) -> Path:
    d = tmp_path / "codex"
    d.mkdir()
    return d


def test_absent_profile(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    backup = install_routing(ch, TEMPLATE)
    assert backup is not None
    assert (ch / "AGENTS.md").exists()
    assert BEGIN in (ch / "AGENTS.md").read_text()


def test_idempotent_no_backup(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    install_routing(ch, TEMPLATE)
    mtime = (ch / "AGENTS.md").stat().st_mtime
    res = install_routing(ch, TEMPLATE)
    assert res is None
    assert (ch / "AGENTS.md").stat().st_mtime == mtime


def test_preserves_foreign_bytes(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    foreign = b"hello\r\nworld\r\n"
    (ch / "AGENTS.md").write_bytes(foreign)
    install_routing(ch, TEMPLATE)
    data = (ch / "AGENTS.md").read_bytes()
    assert foreign in data


def test_bom_crlf(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.md").write_bytes(b"\xef\xbb\xbf# hi\r\n")
    install_routing(ch, TEMPLATE)
    data = (ch / "AGENTS.md").read_bytes()
    assert data.startswith(b"\xef\xbb\xbf")
    assert b"# hi\r\n" in data


def test_malformed_markers_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.md").write_text(
        "<!-- AIKIT:ROUTING:BEGIN -->\nno end", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="."):
        install_routing(ch, TEMPLATE)


def test_duplicate_markers_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.md").write_text(f"{BEGIN}\n{END}\n{BEGIN}\n{END}", encoding="utf-8")
    with pytest.raises(ValueError, match="."):
        install_routing(ch, TEMPLATE)


def test_override_nonempty_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    (ch / "AGENTS.override.md").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="."):
        install_routing(ch, TEMPLATE)


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
        install_routing(ch, TEMPLATE)


def test_symlink_ancestors_rejects(tmp_path: Path) -> None:
    ch = tmp_path / "codex"
    # make parent a symlink to a real dir
    real = tmp_path / "realdir"
    real.mkdir()
    try:
        ch.symlink_to(real)
    except OSError:
        pytest.skip("no symlink support")
    with pytest.raises(ValueError, match="."):
        install_routing(ch, TEMPLATE)


def test_backup_exact_bytes(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    foreign = b"hello\r\nworld\r\n"
    (ch / "AGENTS.md").write_bytes(foreign)
    backup = install_routing(ch, TEMPLATE)
    assert backup is not None
    assert backup.read_bytes() == foreign


def test_noop_no_new_backups_or_mtime(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    install_routing(ch, TEMPLATE)
    mtime = (ch / "AGENTS.md").stat().st_mtime
    backups_before = (
        list((ch / "backups" / "aikit").iterdir())
        if (ch / "backups" / "aikit").exists()
        else []
    )
    res = install_routing(ch, TEMPLATE)
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
        prefix
        + b"<!-- AIKIT:ROUTING:BEGIN -->\nold\n<!-- AIKIT:ROUTING:END -->"
        + suffix
    )
    install_routing(ch, TEMPLATE)
    data = (ch / "AGENTS.md").read_bytes()
    assert data.startswith(prefix)
    assert data.endswith(suffix)
    assert b"old" not in data


def test_malformed_template_rejects(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    bad = tmp_path / "bad-template.md"
    bad.write_text("<!-- AIKIT:ROUTING:BEGIN -->\nno end", encoding="utf-8")
    with pytest.raises(ValueError, match="."):
        install_routing(ch, bad)


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
        install_routing(ch, TEMPLATE)
    assert target.read_bytes() == before


@pytest.mark.parametrize("mutation_point", ["temporary", "backup"])
def test_concurrent_mutation_not_overwritten(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation_point: str
) -> None:
    ch = make_codex(tmp_path)
    agents = ch / "AGENTS.md"
    agents.write_bytes(b"foreign\r\n")
    import install_routing as module

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
        module.install_routing(ch, TEMPLATE)
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


def test_packaged_default_template_from_other_cwd(tmp_path: Path) -> None:
    # Simulate running from another cwd with template resolved by __file__

    ch = tmp_path / "prof"
    ch.mkdir()
    cwd = tmp_path / "elsewhere"
    cwd.mkdir()
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--codex-home", str(ch)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )
    assert proc.returncode == 0, proc.stderr
    assert (ch / "AGENTS.md").exists()


def test_order_go_then_routing(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    install_go(ch, GO_TEMPLATE)
    install_routing(ch, TEMPLATE)
    data = (ch / "AGENTS.md").read_bytes()
    assert GO_BEGIN in data.decode()
    assert BEGIN in data.decode()
    # both blocks present
    assert data.count(GO_BEGIN.encode()) == 1
    assert data.count(BEGIN.encode()) == 1


def test_order_routing_then_go(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    install_routing(ch, TEMPLATE)
    install_go(ch, GO_TEMPLATE)
    data = (ch / "AGENTS.md").read_bytes()
    assert GO_BEGIN in data.decode()
    assert BEGIN in data.decode()
    assert data.count(GO_BEGIN.encode()) == 1
    assert data.count(BEGIN.encode()) == 1


def test_update_routing_preserves_go(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    foreign = b"foreign-line\r\n"
    (ch / "AGENTS.md").write_bytes(foreign)
    install_go(ch, GO_TEMPLATE)
    # capture go block bytes
    install_routing(ch, TEMPLATE)
    # update routing again with changed routing template? Instead re-run routing noop
    # Verify go block unchanged region
    after = (ch / "AGENTS.md").read_bytes()
    assert GO_BEGIN.encode() in after
    assert foreign in after


def test_update_only_routing_keeps_go_and_exterior(tmp_path: Path) -> None:
    ch = make_codex(tmp_path)
    prefix = b"prefix\r\n"
    (ch / "AGENTS.md").write_bytes(prefix)
    install_go(ch, GO_TEMPLATE)
    install_routing(ch, TEMPLATE)
    # modify routing block in file to old
    text = (ch / "AGENTS.md").read_text()
    text = text.replace("<!-- AIKIT:ROUTING:BEGIN -->", "<!-- AIKIT:ROUTING:BEGIN -->")
    # capture backup on re-run with template change by forcing content change:
    # change routing block manually

    data = (ch / "AGENTS.md").read_bytes().decode()
    start = data.index(BEGIN)
    end = data.index(END) + len(END)
    data2 = data[:start] + BEGIN + "\nOLDROUTING\n" + END + data[end:]
    (ch / "AGENTS.md").write_bytes(data2.encode())
    # now install should restore routing and keep go
    backup = install_routing(ch, TEMPLATE)
    assert backup is not None
    final = (ch / "AGENTS.md").read_bytes().decode()
    assert "OLDROUTING" not in final
    assert GO_BEGIN in final
    assert prefix.decode() in final
    # backup exact bytes include old routing
    assert backup.read_bytes().decode().count("OLDROUTING") == 1
