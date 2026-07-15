"""公开 HTTP 异常接缝测试。

覆盖 404、405（含 OPTIONS）、主动 HTTP 异常、框架异常和未知 500，
验证中文 envelope、request_id 关联和 X-Request-ID header 一致性。
"""

from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.api.main import HealthDependencies, create_app

HEALTH_DEPENDENCIES = HealthDependencies(
    database=lambda: _true(),
    redis=lambda: _true(),
    ai=lambda: _true(),
    calendar=lambda: _true(),
    template=lambda: _true(),
    export_storage=lambda: _true(),
    security_ready=True,
)


async def _true() -> bool:
    return True


def _make_client() -> TestClient:
    return TestClient(create_app(dependencies=HEALTH_DEPENDENCIES))


def test_get_missing_path_returns_chinese_404() -> None:
    client = _make_client()
    response = client.get("/missing")

    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "resource.not_found"
    assert "不存在" in data["message"]
    assert "request_id" in data
    assert "field_errors" in data


def test_options_missing_path_returns_chinese_404() -> None:
    client = _make_client()
    response = client.options("/missing")

    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "resource.not_found"
    assert "不存在" in data["message"]


def test_post_health_live_returns_405_not_404() -> None:
    client = _make_client()
    response = client.post("/health/live")

    assert response.status_code == 405
    data = response.json()
    assert data["code"] == "request.method_not_allowed"


def test_delete_health_ready_returns_405() -> None:
    client = _make_client()
    response = client.delete("/health/ready")

    assert response.status_code == 405
    data = response.json()
    assert data["code"] == "request.method_not_allowed"


def test_404_response_includes_request_id_header() -> None:
    client = _make_client()
    response = client.get("/missing")

    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] == response.json()["request_id"]


def test_custom_request_id_propagated_to_error_response() -> None:
    client = _make_client()
    custom_id = "0198a7b0-1234-7890-abcd-ef0123456789"
    response = client.get("/missing", headers={"X-Request-ID": custom_id})

    assert response.headers["X-Request-ID"] == custom_id
    assert response.json()["request_id"] == custom_id


def test_500_returns_chinese_internal_error() -> None:
    from fastapi import FastAPI

    app = FastAPI()
    from apps.api.main import (
        _request_context_middleware,
        _unhandled_error_handler,
    )

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("unexpected failure")

    app.middleware("http")(_request_context_middleware)
    app.exception_handler(Exception)(_unhandled_error_handler)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/boom")
    assert response.status_code == 500
    data = response.json()
    assert data["code"] == "server.internal_error"
    assert "内部错误" in data["message"]
    assert "request_id" in data
    assert "X-Request-ID" in response.headers


def test_http_exception_400_returns_chinese_envelope() -> None:
    from fastapi import FastAPI

    app = FastAPI()
    from apps.api.main import (
        _http_exception_handler,
        _request_context_middleware,
    )

    @app.get("/bad")
    async def bad() -> None:
        raise HTTPException(status_code=400, detail="bad request")

    app.middleware("http")(_request_context_middleware)
    app.exception_handler(StarletteHTTPException)(_http_exception_handler)
    client = TestClient(app)

    response = client.get("/bad")
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "request.http_error"
    assert "request_id" in data


def test_contextvars_cleared_after_request() -> None:
    """请求完成后 contextvars 必须被清理。"""
    import structlog.contextvars as ctxvars

    client = _make_client()
    client.get("/health/live")
    bound = ctxvars.get_contextvars()
    assert "request_id" not in bound
    assert "trace_id" not in bound


def test_contextvars_cleared_after_error() -> None:
    """异常路径后 contextvars 也必须被清理。"""
    import structlog.contextvars as ctxvars

    client = _make_client()
    client.get("/missing")
    bound = ctxvars.get_contextvars()
    assert "request_id" not in bound
    assert "trace_id" not in bound
