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
        code="validation_error",
        message="请求参数验证失败",
        request_id="0198a7b0-1234-7890-abcd-ef0123456789",
    )
    assert response.code == "validation_error"
    assert response.message == "请求参数验证失败"
    assert response.field_errors == []


def test_error_response_missing_code() -> None:
    with pytest.raises(ValidationError):
        ErrorResponse(  # pyright: ignore[reportCallIssue]
            message="测试错误",
            request_id="0198a7b0-1234-7890-abcd-ef0123456789",
        )


def test_field_error_validation() -> None:
    error = FieldError(field="username", code="required", message="用户名不能为空")
    assert error.field == "username"
    assert error.code == "required"


def test_paginated_response_validation() -> None:
    response = PaginatedResponse[dict](
        items=[{"id": 1}, {"id": 2}],
        total=100,
        page=1,
        page_size=20,
    )
    assert response.total == 100
    assert response.page == 1


def test_paginated_response_page_minimum() -> None:
    with pytest.raises(ValidationError):
        PaginatedResponse[dict](items=[], total=0, page=0, page_size=20)


def test_paginated_response_page_size_range() -> None:
    with pytest.raises(ValidationError):
        PaginatedResponse[dict](items=[], total=0, page=1, page_size=0)
    with pytest.raises(ValidationError):
        PaginatedResponse[dict](items=[], total=0, page=1, page_size=101)


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
        code="resource.not_found",
        message="资源不存在",
        request_id="0198a7b0-1234-7890-abcd-ef0123456789",
    )
    json_str = response.model_dump_json()
    data = json.loads(json_str)
    assert data["code"] == "resource.not_found"
    assert data["message"] == "资源不存在"
    assert data["field_errors"] == []


def test_error_response_with_field_errors() -> None:
    response = ErrorResponse(
        code="request.validation_error",
        message="请求参数无效",
        request_id="0198a7b0-1234-7890-abcd-ef0123456789",
        field_errors=[
            FieldError(
                field="username",
                code="required",
                message="请填写用户名。",
            )
        ],
    )
    assert len(response.field_errors) == 1
    assert response.field_errors[0].code == "required"
