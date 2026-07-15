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


def test_error_response_validation():
    """ErrorResponse 应该正确验证字段"""
    data = {
        "code": "VALIDATION_ERROR",
        "message": "请求参数验证失败",
        "detail": None,
        "request_id": "abc-123",
    }
    response = ErrorResponse(**data)
    assert response.code == "VALIDATION_ERROR"
    assert response.message == "请求参数验证失败"


def test_error_response_missing_code():
    """ErrorResponse 缺少 code 字段应该失败"""
    with pytest.raises(ValidationError):
        ErrorResponse(
            message="测试错误",
        )


def test_field_error_validation():
    """FieldError 应该正确验证字段"""
    data = {
        "field": "username",
        "message": "用户名不能为空",
    }
    error = FieldError(**data)
    assert error.field == "username"


def test_paginated_response_validation():
    """PaginatedResponse 应该正确验证字段"""
    data = {
        "items": [{"id": 1}, {"id": 2}],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "has_next": True,
        "has_prev": False,
    }
    response = PaginatedResponse[dict](**data)
    assert response.total == 100
    assert response.page == 1


def test_request_context_validation():
    """RequestContext 应该正确验证字段"""
    data = {
        "request_id": "req-001",
        "trace_id": "trace-001",
        "kindergarten_id": "kg-001",
        "user_id": "user-001",
    }
    ctx = RequestContext(**data)
    assert ctx.request_id == "req-001"


def test_health_check_result_validation():
    """HealthCheckResult 应该正确验证字段"""
    data = {
        "name": "database",
        "status": "healthy",
        "message": "连接正常",
    }
    result = HealthCheckResult(**data)
    assert result.status in ["healthy", "degraded", "unhealthy"]


def test_health_response_validation():
    """HealthResponse 应该正确验证字段"""
    data = {
        "status": "healthy",
        "checks": [
            {"name": "database", "status": "healthy"},
            {"name": "redis", "status": "healthy"},
        ],
        "timestamp": datetime.now(UTC).isoformat(),
    }
    response = HealthResponse(**data)
    assert len(response.checks) == 2


def test_error_response_json_serialization():
    """ErrorResponse 应该正确序列化 JSON"""
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
