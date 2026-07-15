def test_request_context_middleware_generates_ids():
    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient

    from apps.api.main import _request_context_middleware

    app = FastAPI()

    @app.get("/test")
    async def test_endpoint(request: Request) -> dict[str, str]:
        return {
            "request_id": str(request.state.request_id),
            "trace_id": str(request.state.trace_id),
        }

    app.middleware("http")(_request_context_middleware)
    client = TestClient(app)

    response = client.get("/test")
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "trace_id" in data
    assert data["request_id"] == data["trace_id"]


def test_request_context_middleware_accepts_supplied_ids():
    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient

    from apps.api.main import _request_context_middleware

    app = FastAPI()

    @app.get("/test")
    async def test_endpoint(request: Request) -> dict[str, str]:
        return {
            "request_id": str(request.state.request_id),
            "trace_id": str(request.state.trace_id),
        }

    app.middleware("http")(_request_context_middleware)
    client = TestClient(app)

    response = client.get(
        "/test",
        headers={
            "X-Request-ID": "test-request-123",
            "X-Trace-ID": "test-trace-456",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "test-request-123"
    assert data["trace_id"] == "test-trace-456"
    assert response.headers.get("X-Request-ID") == "test-request-123"


def test_error_responses_include_request_id():
    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient

    from apps.api.main import (
        _http_exception_handler,
        _request_context_middleware,
    )

    app = FastAPI()

    @app.get("/error")
    async def error_endpoint() -> None:
        raise HTTPException(status_code=400, detail="Bad request")

    app.middleware("http")(_request_context_middleware)
    app.exception_handler(HTTPException)(_http_exception_handler)
    client = TestClient(app)

    response = client.get("/error")
    assert response.status_code == 400
    assert "X-Request-ID" in response.headers
    data = response.json()
    assert "request_id" in data
