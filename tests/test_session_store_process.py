"""Exclusión real entre procesos, sin inferencia ni acceso de red."""

from __future__ import annotations

import multiprocessing
from pathlib import Path
from typing import Any

from session_store import StoreError, lock_task

TASK_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


def hold_lock(
    root: str, task_id: str, acquired: Any, release: Any, result: Any
) -> None:
    try:
        with lock_task(Path(root), task_id):
            acquired.set()
            if not release.wait(10):
                result.put("owner_timeout")
                return
            result.put("owner_released")
    except StoreError as error:
        result.put(error.code)


def contend_lock(root: str, task_id: str, result: Any) -> None:
    try:
        with lock_task(Path(root), task_id):
            result.put("acquired")
    except StoreError as error:
        result.put(error.code)


def test_process_lock_excludes_contender_and_exit_releases_it(tmp_path: Path) -> None:
    context = multiprocessing.get_context("spawn")
    acquired = context.Event()
    release = context.Event()
    owner_result = context.Queue()
    contender_result = context.Queue()
    owner = context.Process(
        target=hold_lock,
        args=(str(tmp_path), TASK_ID, acquired, release, owner_result),
    )
    contender = context.Process(
        target=contend_lock,
        args=(str(tmp_path), TASK_ID, contender_result),
    )

    owner.start()
    try:
        assert acquired.wait(5), "el propietario no adquirió el bloqueo"
        contender.start()
        assert contender_result.get(timeout=5) == "lock_contended"
        contender.join(5)
        assert not contender.is_alive()
        assert contender.exitcode == 0
    finally:
        release.set()
        owner.join(5)
        if contender.is_alive():
            contender.terminate()
            contender.join(5)
        if owner.is_alive():
            owner.terminate()
            owner.join(5)

    assert not owner.is_alive()
    assert owner.exitcode == 0
    assert owner_result.get(timeout=1) == "owner_released"

    with lock_task(tmp_path, TASK_ID):
        pass
