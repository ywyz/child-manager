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

    req_uuid = "0198a7b0-1234-7890-abcd-ef0123456789"
    trace_uuid = "0198a7b0-abcd-1234-7890-ef0123456789"
    response = client.get(
        "/test",
        headers={
            "X-Request-ID": req_uuid,
            "X-Trace-ID": trace_uuid,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == req_uuid
    assert data["trace_id"] == trace_uuid
    assert response.headers.get("X-Request-ID") == req_uuid


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


def test_middleware_binds_structlog_contextvars():
    import structlog.contextvars as ctxvars
    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient

    from apps.api.main import _request_context_middleware

    captured: dict[str, str] = {}

    app = FastAPI()

    @app.get("/ctx")
    async def ctx_endpoint(request: Request) -> dict[str, str]:
        bound = ctxvars.get_contextvars()
        captured.update(bound)
        return {"ok": "true"}

    app.middleware("http")(_request_context_middleware)
    client = TestClient(app)

    req_uuid = "0198a7b0-aaaa-bbbb-cccc-dddddddddddd"
    client.get("/ctx", headers={"X-Request-ID": req_uuid})

    assert captured.get("request_id") == req_uuid
    assert captured.get("trace_id") == req_uuid
