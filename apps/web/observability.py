"""Web 进程自己的结构化日志装配。"""

from collections.abc import Mapping

import structlog
from structlog.typing import EventDict

_SENSITIVE_KEY_PARTS = (
    "api_key",
    "authorization",
    "cookie",
    "password",
    "secret",
    "token",
)


def _redact(key: str, value: object) -> object:
    lowered = key.lower()
    if (
        any(part in lowered for part in _SENSITIVE_KEY_PARTS)
        or lowered == "key"
        or lowered.endswith("_key")
        or lowered.endswith(("_url", "_urls"))
    ):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {
            str(child_key): _redact(str(child_key), child) for child_key, child in value.items()
        }
    if isinstance(value, list):
        return [_redact("", item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact("", item) for item in value)
    return value


def redact_mapping(event: Mapping[str, object]) -> dict[str, object]:
    """递归清除 Web 日志中的凭证和内部 URL。"""

    return {str(key): _redact(str(key), value) for key, value in event.items()}


def _redact_event(_logger: object, _method: str, event: EventDict) -> EventDict:
    return redact_mapping(event)


def configure_logging() -> None:
    """配置不依赖后端包的 JSON 日志输出。"""

    structlog.configure(
        processors=[
            _redact_event,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
