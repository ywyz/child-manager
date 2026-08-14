"""Qt 页面稳定错误反馈与脱敏诊断。"""

from __future__ import annotations

import logging
import re

from kindergarten_manager.application.agent_runtime import AgentRuntimeError
from kindergarten_manager.application.ai_generation import AiGenerationError
from kindergarten_manager.application.ai_settings import AiSettingsError
from kindergarten_manager.application.bootstrap import StartupError
from kindergarten_manager.application.exports import ExportError
from kindergarten_manager.application.lesson_plans import LessonPlanError
from kindergarten_manager.application.settings import SettingsError
from kindergarten_manager.application.workspace import WorkspaceError
from kindergarten_manager.observability import safe_exception_summary

logger = logging.getLogger(__name__)

_TRUSTED_CODE_ERRORS = (
    AgentRuntimeError,
    AiGenerationError,
    AiSettingsError,
    ExportError,
    LessonPlanError,
    SettingsError,
    StartupError,
    WorkspaceError,
)
_ERROR_CODE_PATTERN = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+")
_USER_ERROR_REASONS = {
    "ai.operation_in_progress": "已有 AI 生成正在进行",
}


def _safe_error_code(error: BaseException) -> str:
    if not isinstance(error, _TRUSTED_CODE_ERRORS):
        return "operation.failed"
    error_code = getattr(error, "error_code", None) or getattr(error, "code", None)
    if (
        not isinstance(error_code, str)
        or len(error_code) > 80
        or _ERROR_CODE_PATTERN.fullmatch(error_code) is None
    ):
        return "operation.failed"
    return error_code


def user_error_message(error: BaseException, fallback: str) -> str:
    # Alembic fileConfig 可能在应用启动期重配 root. 此错误边界必须保持可记录.
    logger.disabled = False
    error_code = _safe_error_code(error)
    summary = safe_exception_summary(error)
    logger.error(
        "desktop_ui_operation_failed error_code=%s error_type=%s",
        error_code,
        summary["error_type"],
        extra={
            "error_code": error_code,
            "error_type": summary["error_type"],
            "safe_message": summary["message"],
        },
    )
    reason = _USER_ERROR_REASONS.get(error_code)
    detail = f"：{reason}" if reason else ""
    return f"{fallback}{detail}（{error_code}）"
