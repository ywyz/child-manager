from __future__ import annotations

import logging

import pytest

from kindergarten_manager.application.ai_generation import AiGenerationError
from kindergarten_manager.ui.errors import user_error_message


def test_user_error_message_preserves_application_error_code(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.ERROR)

    message = user_error_message(
        AiGenerationError("ai.operation_in_progress", "已有 AI 生成正在进行"),
        "集体活动原稿拆分启动失败",
    )

    assert message == ("集体活动原稿拆分启动失败：已有 AI 生成正在进行（ai.operation_in_progress）")
    assert "error_code=ai.operation_in_progress" in caplog.text


def test_user_error_message_rejects_untrusted_exception_code(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class ThirdPartyError(RuntimeError):
        code = "secret.api-key-value"

    caplog.set_level(logging.ERROR)

    message = user_error_message(ThirdPartyError("sensitive detail"), "操作失败")

    assert message == "操作失败（operation.failed）"
    assert "secret.api-key-value" not in caplog.text
