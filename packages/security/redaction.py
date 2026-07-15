"""共享脱敏模块。

提供敏感字段脱敏函数和 structlog 脱敏处理器，
供 API、Web、Worker 等所有运行单元使用。
"""

from typing import Any

from structlog.typing import EventDict

SENSITIVE_KEYS = {
    "password",
    "api_key",
    "secret",
    "token",
    "jwt",
    "csrf",
    "cookie",
    "authorization",
    "access_token",
    "refresh_token",
}


def redact_value(value: Any, key: str | None = None) -> Any:
    if key and _is_sensitive_key(key):
        if isinstance(value, list):
            return ["******" for _ in value]
        return "******"

    if isinstance(value, dict):
        return redact_dict(value)

    if isinstance(value, list):
        return [redact_value(item) for item in value]

    return value


def redact(data: dict[str, Any] | list[Any]) -> Any:
    if isinstance(data, dict):
        return redact_dict(data)
    if isinstance(data, list):
        return [redact_value(item) for item in data]
    return data


def redact_dict(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in data.items():
        result[key] = redact_value(value, key)
    return result


def redaction_processor(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """structlog 处理器：递归脱敏事件字典中的敏感字段。"""
    result: EventDict = {}
    for key, value in event_dict.items():
        result[key] = redact_value(value, key)
    return result


def _is_sensitive_key(key: str) -> bool:
    lower_key = key.lower()
    return any(sensitive in lower_key for sensitive in SENSITIVE_KEYS)
