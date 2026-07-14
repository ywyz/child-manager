from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health_live_returns_healthy():
    """健康检查 live 端点应该返回 healthy"""
    response = client.get("/health/live")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["component"] == "api"


def test_health_ready_returns_healthy():
    """健康检查 ready 端点应该返回 healthy"""
    response = client.get("/health/ready")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["component"] == "api"


def test_health_live_has_request_id():
    """健康检查 live 端点应该返回 X-Request-ID 头部"""
    response = client.get("/health/live")
    
    assert "X-Request-ID" in response.headers


def test_health_ready_has_request_id():
    """健康检查 ready 端点应该返回 X-Request-ID 头部"""
    response = client.get("/health/ready")
    
    assert "X-Request-ID" in response.headers


def test_custom_request_id_propagated():
    """自定义请求 ID 应该被传播"""
    custom_id = "my-custom-request-id-123"
    response = client.get("/health/live", headers={"X-Request-ID": custom_id})
    
    assert response.headers["X-Request-ID"] == custom_id