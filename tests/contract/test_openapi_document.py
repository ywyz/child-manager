from fastapi.testclient import TestClient

from apps.api.main import app


def test_openapi_schema_exists():
    """OpenAPI schema 应该存在"""
    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "openapi" in response.json()


def test_openapi_version_is_31():
    """OpenAPI 版本应该是 3.1"""
    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.json()["openapi"].startswith("3.1")


def test_openapi_has_health_endpoints():
    """OpenAPI 应该包含健康检查端点"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()

    paths = schema.get("paths", {})
    assert "/health/live" in paths
    assert "/health/ready" in paths


def test_openapi_has_components():
    """OpenAPI 应该包含 components 定义"""
    client = TestClient(app)
    response = client.get("/openapi.json")
    schema = response.json()

    assert "components" in schema
