from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from review_evidence import (
    ReviewExpectation,
    capture_snapshot,
    validate_review,
)

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "review_evidence.py"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_root(tmp_path: Path, *, spaces: bool = False) -> Path:
    root = tmp_path / "root dir" if spaces else tmp_path / "root"
    root.mkdir()
    (root / "a.txt").write_text("hello", encoding="utf-8")
    (root / "b.txt").write_text("world", encoding="utf-8")
    return root


def base_expected(root: Path, snapshot: dict[str, str | None]) -> ReviewExpectation:
    return ReviewExpectation(
        snapshot=snapshot,
        implementer_session="impl-session",
        reviewer_session="review-session",
        checks={"t1": "pytest -q"},
    )


def base_report(root: Path, snapshot: dict[str, str | None]) -> dict[str, Any]:
    return {
        "role": "reviewer",
        "session": "review-session",
        "snapshot": snapshot,
        "verdict": "accepted",
        "checks": [
            {
                "id": "t1",
                "command": "pytest -q",
                "cwd": str(root.resolve()),
                "exit_code": 0,
                "summary": "ok",
            }
        ],
        "findings": [],
        "limitations": [],
    }


def test_capture_snapshot_hashes_files(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    assert snap["a.txt"] == sha256_bytes(b"hello")
    assert snap["b.txt"] == sha256_bytes(b"world")


def test_capture_snapshot_missing_is_none(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "missing.txt"])
    assert snap["missing.txt"] is None


def test_capture_snapshot_rejects_escape(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    with pytest.raises(ValueError, match="."):
        capture_snapshot(root, ["../x.txt"])


def test_capture_snapshot_rejects_absolute(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    with pytest.raises(ValueError, match="."):
        capture_snapshot(root, [str(root / "a.txt")])


def test_capture_snapshot_rejects_symlink(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    target = tmp_path / "target.txt"
    target.write_text("x", encoding="utf-8")
    link = root / "link.txt"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("no symlink support")
    with pytest.raises(ValueError, match="."):
        capture_snapshot(root, ["link.txt"])


def test_capture_snapshot_rejects_non_regular(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    (root / "dir").mkdir()
    with pytest.raises(ValueError, match="."):
        capture_snapshot(root, ["dir"])


def test_valid_accepted(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    result = validate_review(root, report, expected)
    assert result["status"] == "accepted"


def test_stale_snapshot(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    (root / "a.txt").write_text("changed", encoding="utf-8")
    report = base_report(root, snap)
    result = validate_review(root, report, expected)
    assert result["code"] == "snapshot_mismatch"


def test_failed_checks(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    report["checks"][0]["exit_code"] = 1
    result = validate_review(root, report, expected)
    assert result["code"] == "checks_failed"


def test_missing_checks(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    report["checks"] = []
    result = validate_review(root, report, expected)
    assert result["code"] == "checks_missing"


def test_changed_after_snapshot(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    (root / "b.txt").write_text("different", encoding="utf-8")
    report = base_report(root, snap)
    result = validate_review(root, report, expected)
    assert result["code"] == "snapshot_mismatch"


def test_deleted_file(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    (root / "b.txt").unlink()
    report = base_report(root, snap)
    result = validate_review(root, report, expected)
    assert result["code"] == "snapshot_mismatch"


def test_author_is_reviewer(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = ReviewExpectation(
        snapshot=snap,
        implementer_session="same",
        reviewer_session="same",
        checks={"t1": "pytest -q"},
    )
    report = base_report(root, snap)
    result = validate_review(root, report, expected)
    assert result["status"] in ("rejected", "error")


def test_session_mismatch(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    report["session"] = "other-session"
    result = validate_review(root, report, expected)
    assert result["status"] in ("rejected", "error")


def test_foreign_command(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    report["checks"][0]["command"] = "rm -rf /"
    result = validate_review(root, report, expected)
    assert result["code"] == "checks_failed"


def test_foreign_cwd(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    report["checks"][0]["cwd"] = str(tmp_path)
    result = validate_review(root, report, expected)
    assert result["code"] == "checks_failed"


def test_malformed_report(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    result = validate_review(root, "not-a-dict", expected)
    assert result["status"] == "error"


def test_malformed_report_missing_fields(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    result = validate_review(root, {"role": "reviewer"}, expected)
    assert result["status"] in ("rejected", "error")


def test_blocker(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    report["findings"] = [{"severity": "blocker", "description": "bad"}]
    result = validate_review(root, report, expected)
    assert result["status"] in ("rejected", "error")


def test_missing_check(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    del report["checks"][0]["id"]
    result = validate_review(root, report, expected)
    assert result["status"] in ("rejected", "error")


def test_nonzero_exit(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    report["checks"][0]["exit_code"] = 2
    result = validate_review(root, report, expected)
    assert result["code"] == "checks_failed"


def test_bool_exit_code_rejected(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    report["checks"][0]["exit_code"] = True
    result = validate_review(root, report, expected)
    assert result["code"] == "checks_failed"


def test_ambiguous_duplicates(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    report["checks"].append(
        {
            "id": "t1",
            "command": "pytest -q",
            "cwd": str(root.resolve()),
            "exit_code": 0,
            "summary": "dup",
        }
    )
    result = validate_review(root, report, expected)
    assert result["status"] in ("rejected", "error")


def test_verdict_false(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    report = base_report(root, snap)
    report["verdict"] = "needs_corrections"
    result = validate_review(root, report, expected)
    assert result["status"] in ("rejected", "error")


def test_expected_malformed_no_crash(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    report = base_report(root, snap)
    result = validate_review(root, report, None)
    assert result["status"] == "error"


def test_cli_snapshot_subprocess(tmp_path: Path) -> None:
    root = make_root(tmp_path, spaces=True)
    files = tmp_path / "files with space.json"
    files.write_text(json.dumps(["a.txt", "b.txt"]), encoding="utf-8")
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "snapshot",
            "--root",
            str(root),
            "--files",
            str(files),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "captured"
    assert "snapshot" in payload


def test_cli_validate_subprocess_accepted(tmp_path: Path) -> None:
    root = make_root(tmp_path, spaces=True)
    capture_snapshot(root, ["a.txt", "b.txt"])
    files = tmp_path / "files.json"
    files.write_text(json.dumps(["a.txt", "b.txt"]), encoding="utf-8")
    snap_proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "snapshot",
            "--root",
            str(root),
            "--files",
            str(files),
        ],
        capture_output=True,
        text=True,
    )
    assert snap_proc.returncode == 0
    snapshot = json.loads(snap_proc.stdout)["snapshot"]
    expected = base_expected(root, snapshot)
    exp_path = tmp_path / "expected.json"
    exp_path.write_text(
        json.dumps(
            {
                "snapshot": expected.snapshot,
                "implementer_session": expected.implementer_session,
                "reviewer_session": expected.reviewer_session,
                "checks": expected.checks,
            }
        ),
        encoding="utf-8",
    )
    report = base_report(root, snapshot)
    rep_path = tmp_path / "report.json"
    rep_path.write_text(json.dumps(report), encoding="utf-8")
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "validate",
            "--root",
            str(root),
            "--report",
            str(rep_path),
            "--expectation",
            str(exp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "accepted"


def test_cli_validate_rejected_exit1(tmp_path: Path) -> None:
    root = make_root(tmp_path)
    snap = capture_snapshot(root, ["a.txt", "b.txt"])
    expected = base_expected(root, snap)
    exp_path = tmp_path / "expected.json"
    exp_path.write_text(
        json.dumps(
            {
                "snapshot": expected.snapshot,
                "implementer_session": expected.implementer_session,
                "reviewer_session": expected.reviewer_session,
                "checks": expected.checks,
            }
        ),
        encoding="utf-8",
    )
    report = base_report(root, snap)
    report["checks"][0]["exit_code"] = 1
    rep_path = tmp_path / "report.json"
    rep_path.write_text(json.dumps(report), encoding="utf-8")
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "validate",
            "--root",
            str(root),
            "--report",
            str(rep_path),
            "--expectation",
            str(exp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    payload = json.loads(proc.stdout)
    assert payload["code"] == "checks_failed"
