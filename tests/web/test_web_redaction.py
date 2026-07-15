"""Web 入口日志脱敏测试。

验证 Web 的 structlog 配置已接入共享脱敏处理器，
敏感字段在日志输出中被正确遮蔽。
"""

import io
import json

import structlog

from packages.security.redaction import redaction_processor


def _configure_web_style_logging(stream: io.StringIO) -> None:
    """模拟 Web 的 structlog 配置（JSONRenderer 便于断言）。"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            redaction_processor,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(file=stream),
        wrapper_class=structlog.make_filtering_bound_logger(10),
        cache_logger_on_first_use=True,
    )


def test_web_redacts_password_in_log_output() -> None:
    stream = io.StringIO()
    _configure_web_style_logging(stream)
    logger = structlog.get_logger()

    logger.info("bff_request", password="secret-value", path="/api/v1/auth/login")

    output = stream.getvalue()
    data = json.loads(output)
    assert data["password"] == "******"
    assert data["path"] == "/api/v1/auth/login"
    assert "secret-value" not in output


def test_web_redacts_api_key_in_log_output() -> None:
    stream = io.StringIO()
    _configure_web_style_logging(stream)
    logger = structlog.get_logger()

    logger.info("proxy_forward", api_key="sk-abc123", target="/api/v1/settings")

    output = stream.getvalue()
    data = json.loads(output)
    assert data["api_key"] == "******"
    assert "sk-abc123" not in output


def test_web_redacts_cookie_and_csrf_in_log_output() -> None:
    stream = io.StringIO()
    _configure_web_style_logging(stream)
    logger = structlog.get_logger()

    logger.info(
        "session_check",
        cookie="session=abc123",
        csrf="csrf-token-xyz",
        authorization="Bearer eyJhbGciOiJIUzI1NiJ9...",
    )

    output = stream.getvalue()
    data = json.loads(output)
    assert data["cookie"] == "******"
    assert data["csrf"] == "******"
    assert data["authorization"] == "******"
    assert "session=abc123" not in output
    assert "csrf-token-xyz" not in output
    assert "Bearer" not in output


def test_web_preserves_non_sensitive_data() -> None:
    stream = io.StringIO()
    _configure_web_style_logging(stream)
    logger = structlog.get_logger()

    logger.info(
        "page_render",
        user_id="user-123",
        page_name="index",
        version=3,
    )

    output = stream.getvalue()
    data = json.loads(output)
    assert data["user_id"] == "user-123"
    assert data["page_name"] == "index"
    assert data["version"] == 3
