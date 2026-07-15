"""structlog 脱敏集成测试。

验证 redaction_processor 已接入 structlog 处理链，
日志中的密钥、密码、Cookie、token 和嵌套数据被脱敏，
敏感明文在输出中命中数为 0。
"""

import io
import json

import structlog

from packages.backend.observability import redaction_processor


def _capture_structlog_output() -> io.StringIO:
    stream = io.StringIO()
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
    return stream


def test_password_is_redacted_in_log_output() -> None:
    stream = _capture_structlog_output()
    logger = structlog.get_logger()

    logger.info("user_login", password="my-secret-password", username="alice")

    output = stream.getvalue()
    data = json.loads(output)
    assert data["password"] == "******"
    assert data["username"] == "alice"
    assert "my-secret-password" not in output


def test_api_key_is_redacted_in_log_output() -> None:
    stream = _capture_structlog_output()
    logger = structlog.get_logger()

    logger.info("ai_call", api_key="sk-abc123def456", model="gpt-4")

    output = stream.getvalue()
    data = json.loads(output)
    assert data["api_key"] == "******"
    assert data["model"] == "gpt-4"
    assert "sk-abc123def456" not in output


def test_token_and_cookie_are_redacted() -> None:
    stream = _capture_structlog_output()
    logger = structlog.get_logger()

    logger.info(
        "request",
        token="jwt-token-value",
        cookie="session=abc123",
        csrf="csrf-token-xyz",
        path="/api/v1/plans",
    )

    output = stream.getvalue()
    data = json.loads(output)
    assert data["token"] == "******"
    assert data["cookie"] == "******"
    assert data["csrf"] == "******"
    assert data["path"] == "/api/v1/plans"
    assert "jwt-token-value" not in output
    assert "session=abc123" not in output


def test_nested_dict_with_sensitive_keys_is_redacted() -> None:
    stream = _capture_structlog_output()
    logger = structlog.get_logger()

    logger.info(
        "config_loaded",
        database={
            "host": "localhost",
            "password": "db-password-123",
            "port": 5432,
        },
        ai={
            "api_key": "sk-real-key",
            "model_name": "gpt-4",
        },
    )

    output = stream.getvalue()
    data = json.loads(output)
    assert data["database"]["host"] == "localhost"
    assert data["database"]["password"] == "******"
    assert data["database"]["port"] == 5432
    assert data["ai"]["api_key"] == "******"
    assert data["ai"]["model_name"] == "gpt-4"
    assert "db-password-123" not in output
    assert "sk-real-key" not in output


def test_list_of_sensitive_values_is_redacted() -> None:
    stream = _capture_structlog_output()
    logger = structlog.get_logger()

    logger.info(
        "batch",
        tokens=["token1", "token2", "token3"],
        ids=[1, 2, 3],
    )

    output = stream.getvalue()
    data = json.loads(output)
    assert data["tokens"] == ["******", "******", "******"]
    assert data["ids"] == [1, 2, 3]
    assert "token1" not in output


def test_non_sensitive_data_passes_through_unchanged() -> None:
    stream = _capture_structlog_output()
    logger = structlog.get_logger()

    logger.info(
        "plan_saved",
        plan_id="abc-123",
        version=5,
        class_name="中一班",
        archived=False,
    )

    output = stream.getvalue()
    data = json.loads(output)
    assert data["plan_id"] == "abc-123"
    assert data["version"] == 5
    assert data["class_name"] == "中一班"
    assert data["archived"] is False


def test_authorization_header_is_redacted() -> None:
    stream = _capture_structlog_output()
    logger = structlog.get_logger()

    logger.info(
        "auth_check",
        authorization="Bearer eyJhbGciOiJIUzI1NiJ9...",
        access_token="access-abc",
        refresh_token="refresh-xyz",
    )

    output = stream.getvalue()
    data = json.loads(output)
    assert data["authorization"] == "******"
    assert data["access_token"] == "******"
    assert data["refresh_token"] == "******"
    assert "Bearer" not in output
    assert "access-abc" not in output
