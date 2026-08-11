"""跨 UI 与应用服务边界的最小共享类型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from threading import Event
from uuid import UUID


class ErrorCode(StrEnum):
    OPERATION_CANCELLED = "operation.cancelled"
    OPERATION_FAILED = "operation.failed"
    VALIDATION_INVALID = "validation.invalid"


@dataclass(frozen=True, slots=True)
class CommandResult[T]:
    ok: bool
    message: str
    value: T | None = field(default=None, repr=False)
    error_code: str | None = None
    retryable: bool = False

    def __post_init__(self) -> None:
        if self.ok and self.error_code is not None:
            raise ValueError("成功结果不能包含错误码")
        if not self.ok and not self.error_code:
            raise ValueError("失败结果必须包含错误码")
        if not self.ok and self.value is not None:
            raise ValueError("失败结果不能包含返回值")

    @classmethod
    def success(cls, value: T, *, message: str) -> CommandResult[T]:
        return cls(ok=True, value=value, message=message)

    @classmethod
    def failure(
        cls,
        error_code: str | ErrorCode,
        *,
        message: str,
        retryable: bool = False,
    ) -> CommandResult[T]:
        return cls(
            ok=False,
            error_code=str(error_code),
            message=message,
            retryable=retryable,
        )


@dataclass(frozen=True, slots=True)
class TaskProgress:
    operation_id: UUID
    phase: str
    completed: int
    total: int | None
    message: str

    def __post_init__(self) -> None:
        if self.completed < 0:
            raise ValueError("进度不能为负数")
        if self.total is not None and (self.total < 0 or self.completed > self.total):
            raise ValueError("进度总数无效")


@dataclass(frozen=True, slots=True)
class OperationAccepted:
    operation_id: UUID


class CancellationToken:
    """只暴露单向取消请求的线程安全令牌。"""

    __slots__ = ("_event",)

    def __init__(self) -> None:
        self._event = Event()

    @property
    def cancel_requested(self) -> bool:
        return self._event.is_set()

    def request_cancel(self) -> None:
        self._event.set()
