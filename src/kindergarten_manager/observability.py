"""桌面日志边界的确定性脱敏工具。"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

REDACTED = "<redacted>"
_SENSITIVE_PARTS = (
    "api_key",
    "authorization",
    "content",
    "credential",
    "password",
    "prompt",
    "secret",
    "token",
)


def _is_sensitive_key(key: object) -> bool:
    normalized = str(key).casefold()
    return any(part in normalized for part in _SENSITIVE_PARTS)


def redact_for_log(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: REDACTED if _is_sensitive_key(key) else redact_for_log(item)
            for key, item in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(redact_for_log(item) for item in value)
    return value


def safe_exception_summary(error: BaseException) -> dict[str, str]:
    return {"error_type": type(error).__name__, "message": "操作失败，请稍后重试"}
