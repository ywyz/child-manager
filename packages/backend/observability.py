"""结构化日志配置与脱敏处理器。

将 redaction 模块接入 structlog 处理链，确保日志中的敏感字段
（密钥、密码、令牌、Cookie 等）在输出前被脱敏。
"""

from typing import Any

import structlog
from structlog.typing import EventDict

from packages.backend.security.redaction import redact_value


def redaction_processor(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """structlog 处理器：递归脱敏事件字典中的敏感字段。"""
    result: EventDict = {}
    for key, value in event_dict.items():
        result[key] = redact_value(value, key)
    return result


def configure_logging() -> None:
    """配置 structlog 处理链，包含脱敏处理器。"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            redaction_processor,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),
        cache_logger_on_first_use=True,
    )
