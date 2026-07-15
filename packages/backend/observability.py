"""结构化日志配置。

调用共享脱敏模块，确保日志中的敏感字段
（密钥、密码、令牌、Cookie 等）在输出前被脱敏。
"""

import structlog

from packages.security.redaction import redaction_processor


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
