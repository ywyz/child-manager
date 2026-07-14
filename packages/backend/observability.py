"""结构化日志、追踪上下文与脱敏接缝。"""

from collections.abc import Mapping
from contextvars import ContextVar
from urllib.parse import urlsplit, urlunsplit

import structlog
from structlog.typing import EventDict

REQUEST_ID: ContextVar[str | None] = ContextVar("request_id", default=None)
TRACE_ID: ContextVar[str | None] = ContextVar("trace_id", default=None)

_SENSITIVE_KEY_PARTS = ("api_key", "authorization", "cookie", "password", "secret", "token")


def _redact_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return "[REDACTED]"
    try:
        password = parsed.password
        port = parsed.port
    except ValueError:
        return "[REDACTED]"
    netloc = parsed.netloc
    if password is not None:
        host = parsed.hostname or ""
        if ":" in host:
            host = f"[{host}]"
        if port is not None:
            host = f"{host}:{port}"
        username = parsed.username or ""
        netloc = f"{username}:[REDACTED]@{host}"
    query = "[REDACTED]" if parsed.query else ""
    fragment = "[REDACTED]" if parsed.fragment else ""
    return urlunsplit((parsed.scheme, netloc, parsed.path, query, fragment))


def _redact(key: str, value: object) -> object:
    lowered = key.lower()
    if (
        any(part in lowered for part in _SENSITIVE_KEY_PARTS)
        or lowered == "key"
        or lowered.endswith("_key")
    ):
        return "[REDACTED]"
    if lowered.endswith(("_url", "_urls")):
        if isinstance(value, str):
            return _redact_url(value)
        if isinstance(value, list):
            return [
                _redact_url(item) if isinstance(item, str) else _redact("", item) for item in value
            ]
        if isinstance(value, tuple):
            return tuple(
                _redact_url(item) if isinstance(item, str) else _redact("", item) for item in value
            )
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
    """递归清除日志中的密钥、令牌、密码与 URL 凭证。"""

    return {str(key): _redact(str(key), value) for key, value in event.items()}


def request_context(*, request_id: str, trace_id: str | None = None) -> dict[str, str]:
    """构造每条结构化日志都应携带的关联字段。"""

    return {"request_id": request_id, "trace_id": trace_id or request_id}


def merge_request_context(_logger: object, _method: str, event: EventDict) -> EventDict:
    """将当前请求关联字段合并到真实 structlog 事件。"""

    request_id = REQUEST_ID.get()
    trace_id = TRACE_ID.get()
    if request_id is not None:
        event.setdefault("request_id", request_id)
    if trace_id is not None:
        event.setdefault("trace_id", trace_id)
    return event


def configure_logging() -> None:
    """配置 JSON 结构化日志和最终脱敏处理器。"""

    structlog.configure(
        processors=[
            merge_request_context,
            lambda _logger, _method, event: redact_mapping(event),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
