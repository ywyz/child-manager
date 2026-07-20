import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from packages.contracts.common import (
    ErrorField,
    ErrorResponse,
    HealthResponse,
    PaginatedResponse,
    RequestContext,
)


def test_error_response_validation() -> None:
    response = ErrorResponse.model_validate(
        {
            "code": "validation_error",
            "message": "请求参数验证失败",
            "request_id": "0198a7b0-1234-7890-abcd-ef0123456789",
            "field_errors": [],
        }
    )
    assert response.code == "validation_error"
    assert response.message == "请求参数验证失败"
    assert response.field_errors == []


def test_error_response_missing_code() -> None:
    with pytest.raises(ValidationError):
        ErrorResponse.model_validate(
            {
                "message": "测试错误",
                "request_id": "0198a7b0-1234-7890-abcd-ef0123456789",
                "field_errors": [],
            }
        )


def test_field_error_validation() -> None:
    error = ErrorField(field="username", code="required", message="用户名不能为空")
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
    ctx = RequestContext.model_validate(
        {
            "request_id": "0198a7b0-1234-7890-abcd-ef0123456789",
            "trace_id": "0198a7b0-5678-7890-abcd-ef0123456789",
            "kindergarten_id": "0198a7b0-9abc-7890-abcd-ef0123456789",
            "user_id": "0198a7b0-def0-7890-abcd-ef0123456789",
        }
    )
    assert str(ctx.request_id) == "0198a7b0-1234-7890-abcd-ef0123456789"


def test_health_response_status_enum() -> None:
    """HealthResponse.status 必须是 ok/degraded/unavailable 之一。"""
    HealthResponse(status="ok", checks={})
    HealthResponse(status="degraded", checks={"db": "unavailable"})
    with pytest.raises(ValidationError):
        HealthResponse(status="healthy", checks={})  # type: ignore[arg-type]


def test_health_response_checks_value_enum() -> None:
    """HealthResponse.checks 值必须是合法枚举。"""
    HealthResponse(status="ok", checks={"db": "ok", "redis": "not_required"})
    with pytest.raises(ValidationError):
        HealthResponse(
            status="ok",
            checks={"db": "healthy"},  # type: ignore[arg-type]
        )


def test_health_response_validation() -> None:
    response = HealthResponse(
        status="ok",
        checks={"database": "ok", "redis": "ok"},
    )
    assert len(response.checks) == 2


def test_error_response_json_serialization() -> None:
    response = ErrorResponse.model_validate(
        {
            "code": "resource.not_found",
            "message": "资源不存在",
            "request_id": "0198a7b0-1234-7890-abcd-ef0123456789",
            "field_errors": [],
        }
    )
    json_str = response.model_dump_json()
    data = json.loads(json_str)
    assert data["code"] == "resource.not_found"
    assert data["message"] == "资源不存在"
    assert data["field_errors"] == []


def test_error_response_with_field_errors() -> None:
    response = ErrorResponse.model_validate(
        {
            "code": "request.validation_error",
            "message": "请求参数无效",
            "request_id": "0198a7b0-1234-7890-abcd-ef0123456789",
            "field_errors": [
                {"field": "username", "code": "required", "message": "请填写用户名。"}
            ],
        }
    )
    assert len(response.field_errors) == 1
    assert response.field_errors[0].code == "required"


def test_error_response_rejects_non_uuid_request_id() -> None:
    """ErrorResponse 必须拒绝非 UUID 的 request_id。"""
    with pytest.raises(ValidationError, match="request_id"):
        ErrorResponse(
            code="server.internal_error",
            message="服务器内部错误",
            request_id="not-a-uuid",  # type: ignore[arg-type]
        )


def test_error_response_rejects_extra_fields() -> None:
    """ErrorResponse 不接受额外字段。"""
    with pytest.raises(ValidationError):
        ErrorResponse(
            code="server.internal_error",
            message="服务器内部错误",
            request_id="0198a7b0-1234-7890-abcd-ef0123456789",
            extra_field="should-fail",  # type: ignore[arg-type]
        )


def test_paginated_response_rejects_extra_fields() -> None:
    """PaginatedResponse 不接受额外字段。"""
    with pytest.raises(ValidationError):
        PaginatedResponse[dict](
            items=[],
            total=0,
            page=1,
            page_size=20,
            has_next=True,  # type: ignore[arg-type]
        )


def test_field_error_rejects_extra_fields() -> None:
    """ErrorField 不接受额外字段。"""
    with pytest.raises(ValidationError):
        ErrorField(
            field="name",
            code="required",
            message="必填",
            extra="bad",  # type: ignore[arg-type]
        )


def test_request_context_rejects_non_uuid_request_id() -> None:
    """RequestContext 必须拒绝非 UUID 的 request_id。"""
    with pytest.raises(ValidationError, match="request_id"):
        RequestContext(request_id="not-valid")  # type: ignore[arg-type]


def test_health_response_rejects_extra_fields() -> None:
    """HealthResponse 不接受额外字段。"""
    with pytest.raises(ValidationError):
        HealthResponse(
            status="ok",
            checks={},
            timestamp="2026-01-01T00:00:00Z",  # type: ignore[arg-type]
        )


def test_web_does_not_import_backend() -> None:
    """Web 不得导入 packages.backend（T019 依赖方向）。"""
    import re

    project_root = Path(__file__).resolve().parents[2]
    pattern = re.compile(r"^\s*(from|import)\s+packages\.backend", re.MULTILINE)
    web_dir = project_root / "apps" / "web"
    violations: list[str] = []
    if web_dir.is_dir():
        for py_file in web_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8", errors="replace")
            if pattern.search(content):
                violations.append(str(py_file.relative_to(project_root)))
    assert not violations, "Web 模块违规导入 packages.backend:\n" + "\n".join(violations)
