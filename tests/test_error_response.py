import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from packages.contracts.common import ErrorResponse


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_openapi_schema_exists(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert schema["openapi"] >= "3.1.0"


def test_error_response_model_structure() -> None:
    error = ErrorResponse(
        code="TEST_ERROR",
        message="测试错误",
        detail="详细信息",
        request_id="req-123",
    )
    assert error.code == "TEST_ERROR"
    assert error.message == "测试错误"
    assert error.detail == "详细信息"
    assert error.request_id == "req-123"


def test_error_response_json() -> None:
    error = ErrorResponse(
        code="VALIDATION_ERROR",
        message="请求参数验证失败",
        detail=None,
        request_id=None,
    )
    data = error.model_dump()
    assert data["code"] == "VALIDATION_ERROR"
    assert data["message"] == "请求参数验证失败"
    assert data.get("detail") is None
    assert data.get("request_id") is None
