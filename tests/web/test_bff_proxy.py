import httpx
import pytest

from apps.web.api_client import proxy_request


@pytest.mark.asyncio
async def test_proxy_ignores_process_proxy_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    client_options: dict[str, object] = {}

    class RecordingClient:
        def __init__(self, **options: object) -> None:
            client_options.update(options)

        async def __aenter__(self) -> RecordingClient:
            return self

        async def __aexit__(self, *args: object) -> None:
            del args

        async def send(self, request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, request=request)

    monkeypatch.setattr(httpx, "AsyncClient", RecordingClient)

    await proxy_request(
        method="GET",
        path="/health/live",
        query=b"",
        headers=(),
        body=b"",
        peer_ip="127.0.0.1",
        api_base_url="http://127.0.0.1:8000",
    )

    assert client_options["trust_env"] is False


@pytest.mark.asyncio
async def test_proxy_preserves_request_and_rebuilds_client_ip() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            201,
            headers=[("Content-Type", "application/json"), ("X-Request-ID", "request-123")],
            content=b'{"ok":true}',
        )

    response = await proxy_request(
        method="POST",
        path="/api/v1/auth/login",
        query=b"next=%2Fplans",
        headers=(
            (b"cookie", b"child_manager_csrf=signed"),
            (b"origin", b"http://127.0.0.1:8080"),
            (b"referer", b"http://127.0.0.1:8080/login"),
            (b"x-csrf-token", b"signed"),
            (b"content-type", b"application/json"),
        ),
        body=b'{"username":"teacher"}',
        peer_ip="127.0.0.1",
        api_base_url="http://127.0.0.1:8000",
        transport=httpx.MockTransport(handler),
    )

    request = captured[0]
    assert request.method == "POST"
    assert request.url.path == "/api/v1/auth/login"
    assert request.url.query == b"next=%2Fplans"
    assert request.content == b'{"username":"teacher"}'
    assert request.headers["cookie"] == "child_manager_csrf=signed"
    assert request.headers["origin"] == "http://127.0.0.1:8080"
    assert request.headers["referer"] == "http://127.0.0.1:8080/login"
    assert request.headers["x-csrf-token"] == "signed"
    assert request.headers["x-child-manager-client-ip"] == "127.0.0.1"
    assert response.status_code == 201
    assert response.body == b'{"ok":true}'
    normalized_response_headers = [(name.lower(), value) for name, value in response.headers]
    assert (b"content-type", b"application/json") in normalized_response_headers
    assert (b"x-request-id", b"request-123") in normalized_response_headers


@pytest.mark.asyncio
async def test_proxy_strips_hop_by_hop_and_spoofed_source_headers() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(204, headers={"Connection": "close"})

    await proxy_request(
        method="POST",
        path="/api/v1/auth/logout",
        query=b"",
        headers=(
            (b"connection", b"keep-alive"),
            (b"forwarded", b"for=203.0.113.10"),
            (b"x-forwarded-for", b"203.0.113.11"),
            (b"x-child-manager-client-ip", b"203.0.113.12"),
        ),
        body=b"",
        peer_ip="127.0.0.2",
        api_base_url="http://127.0.0.1:8000",
        transport=httpx.MockTransport(handler),
    )

    request = captured[0]
    assert "connection" not in request.headers
    assert "forwarded" not in request.headers
    assert "x-forwarded-for" not in request.headers
    assert request.headers["x-child-manager-client-ip"] == "127.0.0.2"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "cookies"),
    [
        (
            "/api/v1/auth/login",
            (
                b"child_manager_access=login-access; Path=/; HttpOnly",
                b"child_manager_refresh=login-refresh; Path=/; HttpOnly",
            ),
        ),
        (
            "/api/v1/auth/refresh",
            (
                b"child_manager_access=refresh-access; Path=/; HttpOnly",
                b"child_manager_refresh=refresh-token; Path=/; HttpOnly",
            ),
        ),
        (
            "/api/v1/auth/logout",
            (
                b"child_manager_access=; Max-Age=0; Path=/; HttpOnly",
                b"child_manager_refresh=; Max-Age=0; Path=/; HttpOnly",
            ),
        ),
    ],
)
async def test_proxy_preserves_auth_set_cookie_as_raw_headers(
    path: str, cookies: tuple[bytes, bytes]
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(
            200,
            headers=[
                (b"set-cookie", cookies[0]),
                (b"set-cookie", cookies[1]),
                (b"content-type", b"application/json"),
            ],
            content=b"{}",
        )

    response = await proxy_request(
        method="POST",
        path=path,
        query=b"",
        headers=(),
        body=b"",
        peer_ip="127.0.0.1",
        api_base_url="http://127.0.0.1:8000",
        transport=httpx.MockTransport(handler),
    )

    raw_cookies = [value for name, value in response.headers if name.lower() == b"set-cookie"]
    assert raw_cookies == list(cookies)
