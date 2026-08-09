from __future__ import annotations

import logging
from dataclasses import dataclass
from threading import Event
from uuid import UUID

import pytest
from PySide6.QtWidgets import QWidget
from pytestqt.qtbot import QtBot
from sqlalchemy.orm import Session

from kindergarten_manager.application.dto import CancellationToken, CommandResult, TaskProgress
from kindergarten_manager.ui.runtime import ProgressReporter, RuntimeBridge


@dataclass(frozen=True, slots=True)
class FrozenWork:
    label: str


def test_runtime_emits_progress_success_and_operation_id(qtbot: QtBot) -> None:
    bridge = RuntimeBridge(max_workers=1)
    operation_id = UUID("00000000-0000-0000-0000-000000000007")
    progress: list[TaskProgress] = []
    successes: list[CommandResult[object]] = []
    bridge.progress.connect(progress.append)
    bridge.succeeded.connect(successes.append)

    def task(
        work: object,
        _token: CancellationToken,
        report: ProgressReporter,
    ) -> CommandResult[object]:
        assert work == FrozenWork("导出")
        report("render", 1, 1, "生成完成")
        return CommandResult.success("完成", message="后台操作完成")

    with qtbot.waitSignal(bridge.finished, timeout=2_000) as finished:
        bridge.submit(operation_id, task, FrozenWork("导出"))

    assert finished.args == [operation_id]
    assert progress == [TaskProgress(operation_id, "render", 1, 1, "生成完成")]
    assert len(successes) == 1
    assert successes[0].value == "完成"


def test_finished_worker_is_retained_until_thread_pool_confirms_return(qtbot: QtBot) -> None:
    bridge = RuntimeBridge(max_workers=1)
    operation_id = UUID("00000000-0000-0000-0000-000000000017")

    def task(
        _work: object,
        _token: CancellationToken,
        _report: ProgressReporter,
    ) -> CommandResult[object]:
        return CommandResult.success(None, message="完成")

    bridge.submit(operation_id, task, FrozenWork("生命周期"))
    with qtbot.waitSignal(bridge.finished, timeout=2_000):
        pass

    assert operation_id in bridge.retained_worker_ids
    assert bridge.shutdown(1_000)
    assert operation_id not in bridge.retained_worker_ids


def test_cancelled_operation_discards_late_progress_and_result(qtbot: QtBot) -> None:
    bridge = RuntimeBridge(max_workers=1)
    operation_id = UUID("00000000-0000-0000-0000-000000000008")
    started = Event()
    release = Event()
    progress: list[object] = []
    completed: list[object] = []
    bridge.progress.connect(progress.append)
    bridge.succeeded.connect(completed.append)
    bridge.failed.connect(completed.append)

    def task(
        _work: object,
        _token: CancellationToken,
        report: ProgressReporter,
    ) -> CommandResult[object]:
        started.set()
        release.wait(timeout=2)
        report("late", 1, 1, "迟到结果")
        return CommandResult.success("迟到", message="迟到完成")

    bridge.submit(operation_id, task, FrozenWork("取消"))
    qtbot.waitUntil(started.is_set, timeout=1_000)
    assert bridge.cancel(operation_id)
    release.set()
    with qtbot.waitSignal(bridge.finished, timeout=2_000):
        pass

    assert progress == []
    assert completed == []


def test_runtime_rejects_widget_session_and_mutable_input(qtbot: QtBot) -> None:
    bridge = RuntimeBridge(max_workers=1)

    def task(
        _work: object,
        _token: CancellationToken,
        _report: ProgressReporter,
    ) -> CommandResult[object]:
        return CommandResult.success(None, message="完成")

    widget = QWidget()
    qtbot.addWidget(widget)
    with pytest.raises(TypeError, match="Qt 对象"):
        bridge.submit(UUID(int=9), task, widget)
    with Session() as session, pytest.raises(TypeError, match="Session"):
        bridge.submit(UUID(int=10), task, session)
    with pytest.raises(TypeError, match="不可变"):
        bridge.submit(UUID(int=11), task, ["mutable"])
    with pytest.raises(TypeError, match="冻结 DTO"):
        bridge.submit(UUID(int=12), task, object())


def test_shutdown_requests_cancel_and_waits_for_cooperative_task(qtbot: QtBot) -> None:
    bridge = RuntimeBridge(max_workers=1)
    operation_id = UUID("00000000-0000-0000-0000-000000000014")
    started = Event()
    tick = Event()

    def task(
        _work: object,
        token: CancellationToken,
        _report: ProgressReporter,
    ) -> CommandResult[object]:
        started.set()
        while not token.cancel_requested:
            tick.wait(0.01)
        return CommandResult.failure("operation.cancelled", message="操作已取消")

    bridge.submit(operation_id, task, FrozenWork("退出"))
    qtbot.waitUntil(started.is_set, timeout=1_000)

    assert bridge.shutdown(1_000)
    qtbot.waitUntil(lambda: operation_id not in bridge.active_operation_ids, timeout=1_000)
    with pytest.raises(RuntimeError, match="正在退出"):
        bridge.submit(UUID(int=15), task, FrozenWork("新任务"))


def test_runtime_crash_returns_stable_code_and_logs_only_safe_summary(
    qtbot: QtBot,
    caplog: pytest.LogCaptureFixture,
) -> None:
    bridge = RuntimeBridge(max_workers=1)
    failures: list[CommandResult[object]] = []
    bridge.failed.connect(failures.append)
    caplog.set_level(logging.ERROR)

    def task(
        _work: object,
        _token: CancellationToken,
        _report: ProgressReporter,
    ) -> CommandResult[object]:
        raise RuntimeError("秘密教案正文")

    with qtbot.waitSignal(bridge.finished, timeout=2_000):
        bridge.submit(UUID(int=18), task, FrozenWork("异常"))

    assert len(failures) == 1
    assert failures[0].error_code == "operation.failed"
    assert "operation.failed" in caplog.text
    assert "RuntimeError" in caplog.text
    assert "秘密教案正文" not in caplog.text
