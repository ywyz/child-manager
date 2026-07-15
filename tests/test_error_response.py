import pytest
from fastapi.testclient import TestClient

from apps.api.app import create_app
from packages.contracts.common import ErrorResponse

app = create_app()


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
    error = ErrorResponse.model_validate(
        {
            "code": "resource.not_found",
            "message": "资源不存在",
            "request_id": "0198a7b0-1234-7890-abcd-ef0123456789",
            "field_errors": [],
        }
    )
    assert error.code == "resource.not_found"
    assert error.message == "资源不存在"
    assert str(error.request_id) == "0198a7b0-1234-7890-abcd-ef0123456789"
    assert error.field_errors == []


def test_error_response_defaults() -> None:
    error = ErrorResponse.model_validate(
        {
            "code": "server.internal_error",
            "message": "服务器内部错误",
            "request_id": "0198a7b0-1234-7890-abcd-ef0123456789",
            "field_errors": [],
        }
    )
    data = error.model_dump()
    assert data["code"] == "server.internal_error"
    assert data["message"] == "服务器内部错误"
    assert data["field_errors"] == []
