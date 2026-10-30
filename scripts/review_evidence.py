from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ReviewExpectation:
    snapshot: dict[str, str | None]
    implementer_session: str
    reviewer_session: str
    checks: dict[str, str]


def _reject_symlinks(*paths: Path) -> None:
    for p in paths:
        cur = p
        while True:
            if cur.is_symlink():
                raise ValueError(f"Ruta symlink no permitida: {cur}")
            if cur.parent == cur:
                break
            cur = cur.parent


def _validate_relative(rel: str) -> None:
    if not isinstance(rel, str) or rel == "":
        raise ValueError("Ruta relativa invalida")
    p = Path(rel)
    if p.is_absolute():
        raise ValueError("Ruta absoluta no permitida")
    for part in p.parts:
        if part == "..":
            raise ValueError("Escape de raiz no permitido")
        if part == "":
            raise ValueError("Ruta vacia no permitida")


def _safe_join(root: Path, rel: str) -> Path:
    _validate_relative(rel)
    _reject_symlinks(root)
    full = root / rel
    _reject_symlinks(full)
    return full


def capture_snapshot(root: Path, files: Sequence[str]) -> dict[str, str | None]:
    root = Path(root)
    _reject_symlinks(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Raiz invalida")
    result: dict[str, str | None] = {}
    for rel in files:
        _validate_relative(rel)
        full = _safe_join(root, rel)
        if not full.exists():
            result[rel] = None
            continue
        if full.is_symlink() or not full.is_file():
            raise ValueError(f"No es archivo regular: {rel}")
        data = full.read_bytes()
        result[rel] = hashlib.sha256(data).hexdigest()
    return result


def _is_str(value: Any) -> bool:
    return isinstance(value, str) and value != ""


def _validate_expected(expected: Any) -> str | None:
    if not isinstance(expected, ReviewExpectation):
        return "invalid_expectation"
    if not isinstance(expected.snapshot, dict):
        return "invalid_expectation"
    for key, value in expected.snapshot.items():
        if not isinstance(key, str) or key == "":
            return "invalid_expectation"
        if value is not None and not isinstance(value, str):
            return "invalid_expectation"
        try:
            _validate_relative(key)
        except ValueError:
            return "invalid_expectation"
    if not _is_str(expected.implementer_session):
        return "invalid_expectation"
    if not _is_str(expected.reviewer_session):
        return "invalid_expectation"
    if expected.implementer_session == expected.reviewer_session:
        return "invalid_expectation"
    if not isinstance(expected.checks, dict):
        return "invalid_expectation"
    for key, value in expected.checks.items():
        if not isinstance(key, str) or key == "":
            return "invalid_expectation"
        if not isinstance(value, str):
            return "invalid_expectation"
    return None


def _error(code: str) -> dict[str, Any]:
    return {"status": "error", "code": code}


def _rejected(code: str) -> dict[str, Any]:
    return {"status": "rejected", "code": code}


def validate_review(root: Path, report: Any, expected: Any) -> dict[str, Any]:
    root = Path(root)
    try:
        _reject_symlinks(root)
    except ValueError:
        return _error("invalid_root")
    if not isinstance(report, dict):
        return _error("invalid_report")
    exp_error = _validate_expected(expected)
    if exp_error is not None:
        return _error(exp_error)

    if report.get("role") != "reviewer":
        return _rejected("invalid_role")

    session = report.get("session")
    if not isinstance(session, str) or session == "":
        return _rejected("invalid_session")
    if session == expected.implementer_session:
        return _rejected("author_is_reviewer")
    if session != expected.reviewer_session:
        return _rejected("session_mismatch")

    report_snapshot = report.get("snapshot")
    if not isinstance(report_snapshot, dict):
        return _rejected("snapshot_mismatch")
    if report_snapshot != expected.snapshot:
        return _rejected("snapshot_mismatch")
    try:
        current = capture_snapshot(root, list(expected.snapshot.keys()))
    except (ValueError, OSError, UnicodeError):
        return _error("invalid_root")
    if current != expected.snapshot:
        return _rejected("snapshot_mismatch")

    verdict = report.get("verdict")
    if verdict not in ("accepted", "needs_corrections"):
        return _rejected("invalid_verdict")
    if verdict != "accepted":
        return _rejected("verdict_not_accepted")

    findings = report.get("findings")
    if not isinstance(findings, list):
        return _rejected("invalid_findings")
    for f in findings:
        if not isinstance(f, dict):
            return _rejected("invalid_findings")
        sev = f.get("severity")
        desc = f.get("description")
        if sev not in ("blocker", "warning", "info"):
            return _rejected("invalid_findings")
        if not isinstance(desc, str):
            return _rejected("invalid_findings")
    if any(f.get("severity") == "blocker" for f in findings):
        return _rejected("blocker_found")

    limitations = report.get("limitations")
    if not isinstance(limitations, list):
        return _rejected("invalid_limitations")
    if any(not isinstance(x, str) for x in limitations):
        return _rejected("invalid_limitations")

    checks = report.get("checks")
    if not isinstance(checks, list):
        return _rejected("invalid_checks")
    by_id: dict[str, list[dict[str, Any]]] = {}
    for c in checks:
        if not isinstance(c, dict):
            return _rejected("invalid_checks")
        cid = c.get("id")
        if not isinstance(cid, str) or cid == "":
            return _rejected("invalid_checks")
        by_id.setdefault(cid, []).append(c)

    missing = [cid for cid in expected.checks if cid not in by_id]
    if missing:
        return _rejected("checks_missing")
    for cid in expected.checks:
        if len(by_id.get(cid, [])) > 1:
            return _rejected("checks_ambiguous")

    root_resolved = root.resolve()
    for cid, required_cmd in expected.checks.items():
        c = by_id[cid][0]
        if c.get("command") != required_cmd:
            return _rejected("checks_failed")
        cwd = c.get("cwd")
        if not isinstance(cwd, str):
            return _rejected("checks_failed")
        try:
            cwd_path = Path(cwd)
        except (TypeError, ValueError):
            return _rejected("checks_failed")
        if not cwd_path.is_absolute():
            cwd_path = root / cwd_path
        if cwd_path.resolve() != root_resolved:
            return _rejected("checks_failed")
        exit_code = c.get("exit_code")
        if type(exit_code) is not int or isinstance(exit_code, bool):
            return _rejected("checks_failed")
        if exit_code != 0:
            return _rejected("checks_failed")
        summary = c.get("summary")
        if not isinstance(summary, str):
            return _rejected("checks_failed")

    return {"status": "accepted"}


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser(description="Evidencia de revision OpenCode")
    sub = parser.add_subparsers(dest="command", required=True)

    snap = sub.add_parser("snapshot")
    snap.add_argument("--root", required=True, type=Path)
    snap.add_argument("--files", required=True, type=Path)

    val = sub.add_parser("validate")
    val.add_argument("--root", required=True, type=Path)
    val.add_argument("--report", required=True, type=Path)
    val.add_argument("--expectation", required=True, type=Path)

    args = parser.parse_args()

    if args.command == "snapshot":
        try:
            files_data = json.loads(args.files.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeError):
            _print_json({"status": "error", "code": "invalid_input"})
            return 1
        if not isinstance(files_data, list) or not all(
            isinstance(x, str) for x in files_data
        ):
            _print_json({"status": "error", "code": "invalid_input"})
            return 1
        try:
            snapshot = capture_snapshot(args.root, files_data)
        except (ValueError, OSError, UnicodeError):
            _print_json({"status": "error", "code": "invalid_input"})
            return 1
        _print_json({"status": "captured", "snapshot": snapshot})
        return 0

    if args.command == "validate":
        try:
            report = json.loads(args.report.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeError):
            _print_json({"status": "error", "code": "invalid_report"})
            return 1
        try:
            exp_data = json.loads(args.expectation.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeError):
            _print_json({"status": "error", "code": "invalid_expectation"})
            return 1
        if not isinstance(exp_data, dict):
            _print_json({"status": "error", "code": "invalid_expectation"})
            return 1
        try:
            expected = ReviewExpectation(
                snapshot=exp_data["snapshot"],
                implementer_session=exp_data["implementer_session"],
                reviewer_session=exp_data["reviewer_session"],
                checks=exp_data["checks"],
            )
        except (KeyError, TypeError, ValueError):
            _print_json({"status": "error", "code": "invalid_expectation"})
            return 1
        result = validate_review(args.root, report, expected)
        _print_json(result)
        return 0 if result.get("status") == "accepted" else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
