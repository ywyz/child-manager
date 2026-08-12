"""Qt 线程池与应用服务之间的窄桥接。"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from kindergarten_manager.application.dto import (
    CancellationToken,
    CommandResult,
    ErrorCode,
    TaskProgress,
)
from kindergarten_manager.observability import safe_exception_summary

logger = logging.getLogger(__name__)

ProgressReporter = Callable[[str, int, int | None, str], None]
BackgroundTask = Callable[[object, CancellationToken, ProgressReporter], CommandResult[object]]


def _reject_thread_bound(value: object) -> None:
    if isinstance(value, QObject):
        raise TypeError("Qt 对象不能传入后台线程")
    module = type(value).__module__
    if module == "sqlalchemy.orm.session" or module.startswith("sqlalchemy.orm.session."):
        raise TypeError("数据库 Session 不能传入后台线程")
    if is_dataclass(value) and not isinstance(value, type):
        params = getattr(type(value), "__dataclass_params__", None)
        if params is None or not params.frozen:
            raise TypeError("后台输入 dataclass 必须冻结")
        for item in fields(value):
            _reject_thread_bound(getattr(value, item.name))
        return
    if isinstance(value, Mapping):
        raise TypeError("后台输入不能使用可变映射")
    if isinstance(value, list | set | bytearray):
        raise TypeError("后台输入必须是不可变值")
    if isinstance(value, Sequence | frozenset) and not isinstance(value, str | bytes):
        for item in value:
            _reject_thread_bound(item)
        return
    if isinstance(
        value,
        Path | str | bytes | int | float | bool | UUID | date | datetime | Enum | type(None),
    ):
        return
    raise TypeError("后台输入必须是冻结 DTO 或不可变基础值")


class _WorkerSignals(QObject):
    progressed = Signal(object, object)
    completed = Signal(object, object)
    crashed = Signal(object)
    finished = Signal(object)


class _Worker(QRunnable):
    def __init__(
        self,
        operation_id: UUID,
        task: BackgroundTask,
        frozen_input: object,
        token: CancellationToken,
    ) -> None:
        super().__init__()
        self.setAutoDelete(False)
        self.operation_id = operation_id
        self.task = task
        self.frozen_input = frozen_input
        self.token = token
        self.signals = _WorkerSignals()

    @Slot()
    def run(self) -> None:
        def report(phase: str, completed: int, total: int | None, message: str) -> None:
            progress = TaskProgress(
                operation_id=self.operation_id,
                phase=phase,
                completed=completed,
                total=total,
                message=message,
            )
            self.signals.progressed.emit(self.operation_id, progress)

        try:
            result = self.task(self.frozen_input, self.token, report)
        except Exception as error:
            self.frozen_input = None
            summary = safe_exception_summary(error)
            logger.disabled = False
            logger.error(
                "desktop_runtime_task_failed error_code=%s error_type=%s",
                ErrorCode.OPERATION_FAILED,
                summary["error_type"],
                extra={
                    "error_code": str(ErrorCode.OPERATION_FAILED),
                    "error_type": summary["error_type"],
                    "safe_message": summary["message"],
                },
            )
            self.signals.crashed.emit(self.operation_id)
        else:
            self.frozen_input = None
            self.signals.completed.emit(self.operation_id, result)
        finally:
            self.frozen_input = None
            self.signals.finished.emit(self.operation_id)


class RuntimeBridge(QObject):
    progress = Signal(object)
    succeeded = Signal(object)
    failed = Signal(object)
    finished = Signal(object)

    def __init__(self, *, max_workers: int = 2, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(max_workers)
        self._tokens: dict[UUID, CancellationToken] = {}
        self._workers: dict[UUID, _Worker] = {}
        self._accepting = True

    @property
    def active_operation_ids(self) -> tuple[UUID, ...]:
        return tuple(self._tokens)

    @property
    def retained_worker_ids(self) -> tuple[UUID, ...]:
        """仍由 bridge 持有、等待线程池安全释放的 operation。"""

        return tuple(self._workers)

    def submit(
        self,
        operation_id: UUID,
        task: BackgroundTask,
        frozen_input: object,
        cancellation_token: CancellationToken | None = None,
    ) -> CancellationToken:
        self._discard_finished_workers_if_idle()
        if not self._accepting:
            raise RuntimeError("应用正在退出，不能启动新任务")
        if operation_id in self._tokens:
            raise ValueError("operation_id 已在运行")
        _reject_thread_bound(frozen_input)
        token = cancellation_token or CancellationToken()
        worker = _Worker(operation_id, task, frozen_input, token)
        worker.signals.progressed.connect(self._on_progress)
        worker.signals.completed.connect(self._on_completed)
        worker.signals.crashed.connect(self._on_crashed)
        worker.signals.finished.connect(self._on_finished)
        self._tokens[operation_id] = token
        self._workers[operation_id] = worker
        self._pool.start(worker)
        return token

    def cancel(self, operation_id: UUID) -> bool:
        token = self._tokens.get(operation_id)
        if token is None:
            return False
        token.request_cancel()
        return True

    def shutdown(self, timeout_ms: int) -> bool:
        self._accepting = False
        for token in self._tokens.values():
            token.request_cancel()
        finished = self._pool.waitForDone(timeout_ms)
        if finished:
            self._tokens.clear()
            self._workers.clear()
        return finished

    @Slot(object, object)
    def _on_progress(self, operation_id: UUID, progress: TaskProgress) -> None:
        token = self._tokens.get(operation_id)
        if token is not None and not token.cancel_requested:
            self.progress.emit(progress)

    @Slot(object, object)
    def _on_completed(self, operation_id: UUID, result: CommandResult[object]) -> None:
        token = self._tokens.get(operation_id)
        if token is None or token.cancel_requested:
            return
        if result.ok:
            self.succeeded.emit(result)
        else:
            self.failed.emit(result)

    @Slot(object)
    def _on_crashed(self, operation_id: UUID) -> None:
        token = self._tokens.get(operation_id)
        if token is None or token.cancel_requested:
            return
        self.failed.emit(
            CommandResult[None].failure(
                ErrorCode.OPERATION_FAILED,
                message="后台操作失败，请重试",
            )
        )

    @Slot(object)
    def _on_finished(self, operation_id: UUID) -> None:
        if operation_id not in self._tokens:
            return
        self._tokens.pop(operation_id, None)
        self.finished.emit(operation_id)

    def _discard_finished_workers_if_idle(self) -> None:
        if self._pool.activeThreadCount() != 0 or not self._pool.waitForDone(0):
            return
        for operation_id in tuple(self._workers):
            if operation_id not in self._tokens:
                self._workers.pop(operation_id, None)
