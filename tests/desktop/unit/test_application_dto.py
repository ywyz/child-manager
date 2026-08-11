from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from kindergarten_manager.application.dto import CommandResult, ErrorCode, TaskProgress
from kindergarten_manager.observability import REDACTED, redact_for_log, safe_exception_summary


def test_command_result_has_stable_success_and_failure_contract() -> None:
    success = CommandResult.success({"content": "仅在返回值中"}, message="保存成功")
    failure = CommandResult[None].failure(
        ErrorCode.OPERATION_FAILED,
        message="保存失败，请重试",
        retryable=True,
    )

    assert (success.ok, success.error_code, success.retryable) == (True, None, False)
    assert (failure.ok, failure.value, failure.error_code, failure.retryable) == (
        False,
        None,
        "operation.failed",
        True,
    )
    assert "仅在返回值中" not in repr(success)


def test_command_result_rejects_ambiguous_states() -> None:
    with pytest.raises(ValueError, match="成功结果不能包含错误码"):
        CommandResult(ok=True, message="完成", error_code="operation.failed")
    with pytest.raises(ValueError, match="失败结果必须包含错误码"):
        CommandResult(ok=False, message="失败")
    with pytest.raises(ValueError, match="失败结果不能包含返回值"):
        CommandResult(ok=False, message="失败", value=object(), error_code="operation.failed")


def test_task_progress_is_frozen_and_validated() -> None:
    progress = TaskProgress(
        operation_id=UUID("00000000-0000-0000-0000-000000000001"),
        phase="render",
        completed=1,
        total=2,
        message="正在生成 Word",
    )

    with pytest.raises(FrozenInstanceError):
        progress.completed = 2  # type: ignore[misc]
    with pytest.raises(ValueError, match="总数无效"):
        TaskProgress(progress.operation_id, "render", 3, 2, "进度错误")


def test_log_redaction_removes_content_and_credentials_recursively() -> None:
    payload = {
        "plan_id": 7,
        "content": "完整教案正文",
        "nested": {"api_key": "sk-synthetic-not-real", "status": "ready"},
    }

    redacted = redact_for_log(payload)

    assert redacted == {
        "plan_id": 7,
        "content": REDACTED,
        "nested": {"api_key": REDACTED, "status": "ready"},
    }
    assert safe_exception_summary(RuntimeError("含敏感正文")) == {
        "error_type": "RuntimeError",
        "message": "操作失败，请稍后重试",
    }
