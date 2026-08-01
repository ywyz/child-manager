"""BFF 请求和原始多值响应头转发契约。"""

from typing import cast

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
            (b"idempotency-key", b"export-request-123"),
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
    assert request.headers["idempotency-key"] == "export-request-123"
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


@pytest.mark.asyncio
async def test_plan_docx_preview_request_forwards_csrf_cookie_and_multipart(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from importlib import import_module

    from nicegui import app, ui
    from nicegui.testing.user_interaction import UserInteraction
    from nicegui.testing.user_simulation import user_simulation

    client = import_module("apps.web.api_client")
    captured: list[dict[str, object]] = []

    async def fake_proxy(**kwargs: object) -> object:
        captured.append(kwargs)
        if kwargs["path"] == "/api/v1/auth/csrf":
            return client.BffResponse(200, (), b'{"csrf_token":"signed-token"}')
        return client.BffResponse(
            200,
            ((b"content-type", b"application/json"),),
            '{"original_filename":"教学.docx","extracted_text":"合成预览"}'.encode(),
        )

    monkeypatch.setattr(app.state, "child_manager_api_base_url", "http://api.test", raising=False)
    monkeypatch.setattr(client, "proxy_request", fake_proxy)

    def page() -> None:
        result_label = ui.label("")

        async def upload() -> None:
            result = await client.plan_docx_preview_request(
                "plan-1",
                filename="教学.docx",
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                payload=b"synthetic-docx",
            )
            result_label.set_text(str(result["body"].get("extracted_text", "")))

        ui.button("上传", on_click=upload)

    async with user_simulation(root=page) as user:
        await user.open("/")
        button = next(button for button in user.find(ui.button).elements if button.text == "上传")
        UserInteraction(user, {button}, "上传").click()
        await user.should_see("合成预览")
    assert [item["path"] for item in captured] == [
        "/api/v1/auth/csrf",
        "/api/v1/plans/plan-1/group-activity-sources/docx",
    ]
    post_headers = cast(tuple[tuple[bytes, bytes], ...], captured[1]["headers"])
    headers = {name.lower(): value for name, value in post_headers}
    post_body = cast(bytes, captured[1]["body"])
    assert headers[b"x-csrf-token"] == b"signed-token"
    assert b"child_manager_csrf=signed-token" in headers[b"cookie"]
    assert b"multipart/form-data" in headers[b"content-type"]
    assert "教学.docx".encode() in post_body
    assert b"synthetic-docx" in post_body
