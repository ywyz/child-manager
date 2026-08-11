"""Qt 页面稳定错误反馈与脱敏诊断。"""

from __future__ import annotations

import logging

from kindergarten_manager.observability import safe_exception_summary

logger = logging.getLogger(__name__)


def user_error_message(error: BaseException, fallback: str) -> str:
    # Alembic fileConfig 可能在应用启动期重配 root. 此错误边界必须保持可记录.
    logger.disabled = False
    error_code = getattr(error, "error_code", "operation.failed")
    if not isinstance(error_code, str) or not error_code:
        error_code = "operation.failed"
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
    return f"{fallback}（{error_code}）"
