import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from packages.contracts.common import (
    ErrorResponse,
    FieldError,
    HealthCheckResult,
    HealthResponse,
    PaginatedResponse,
    RequestContext,
)


def test_error_response_validation() -> None:
    response = ErrorResponse(
        code="VALIDATION_ERROR",
        message="请求参数验证失败",
        detail=None,
        request_id="abc-123",
    )
    assert response.code == "VALIDATION_ERROR"
    assert response.message == "请求参数验证失败"


def test_error_response_missing_code() -> None:
    with pytest.raises(ValidationError):
        ErrorResponse(  # pyright: ignore[reportCallIssue]
            message="测试错误",
            detail=None,
            request_id=None,
        )


def test_field_error_validation() -> None:
    error = FieldError(field="username", message="用户名不能为空")
    assert error.field == "username"


def test_paginated_response_validation() -> None:
    response = PaginatedResponse[dict](
        items=[{"id": 1}, {"id": 2}],
        total=100,
        page=1,
        page_size=20,
        has_next=True,
        has_prev=False,
    )
    assert response.total == 100
    assert response.page == 1


def test_request_context_validation() -> None:
    ctx = RequestContext(
        request_id="req-001",
        trace_id="trace-001",
        kindergarten_id="kg-001",
        user_id="user-001",
    )
    assert ctx.request_id == "req-001"


def test_health_check_result_validation() -> None:
    result = HealthCheckResult(name="database", status="healthy", message="连接正常")
    assert result.status in ["healthy", "degraded", "unhealthy"]


def test_health_response_validation() -> None:
    checks = [
        HealthCheckResult(name="database", status="healthy", message=None),
        HealthCheckResult(name="redis", status="healthy", message=None),
    ]
    response = HealthResponse(
        status="healthy",
        checks=checks,
        timestamp=datetime.now(UTC).isoformat(),
    )
    assert len(response.checks) == 2


def test_error_response_json_serialization() -> None:
    response = ErrorResponse(
        code="NOT_FOUND",
        message="资源不存在",
        detail="ID 为 1 的资源不存在",
        request_id="req-001",
    )
    json_str = response.model_dump_json()
    data = json.loads(json_str)
    assert data["code"] == "NOT_FOUND"
    assert data["message"] == "资源不存在"
