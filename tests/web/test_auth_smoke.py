"""Web 认证流程 BFF 冒烟测试。"""

from collections.abc import Iterator
from typing import cast

import httpx
import pytest
from nicegui import app

from apps.web.api_client import proxy_request
from apps.web.app import register_web
from apps.web.components.navigation import render_navigation
from apps.web.pages.auth import change_password_page, login_page
from apps.web.pages.users import user_management_page


@pytest.fixture(autouse=True)
def _clear_routes() -> Iterator[None]:
    # NiceGUI 使用全局 app；测试前保留原始路由避免重复注册副作用
    original = list(app.routes)
    yield
    app.routes[:] = original


@pytest.mark.asyncio
async def test_bff_login_preserves_two_auth_cookies() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(
            200,
            headers=[
                (b"set-cookie", b"child_manager_access=token; Path=/; HttpOnly"),
                (b"set-cookie", b"child_manager_refresh=token; Path=/; HttpOnly"),
            ],
            content=b'{"user":{"id":"1","username":"admin"}}',
        )

    response = await proxy_request(
        method="POST",
        path="/api/v1/auth/login",
        query=b"",
        headers=(
            (b"content-type", b"application/json"),
            (b"origin", b"http://127.0.0.1:28080"),
            (b"x-csrf-token", b"csrf"),
        ),
        body=b'{"username":"admin","password":"ValidPassword2024!"}',
        peer_ip="127.0.0.1",
        api_base_url="http://127.0.0.1:28000",
        transport=httpx.MockTransport(handler),
    )
    cookies = [value for name, value in response.headers if name.lower() == b"set-cookie"]
    assert len(cookies) == 2
    assert all(b"HttpOnly" in c for c in cookies)


@pytest.mark.asyncio
async def test_bff_forwards_origin_and_csrf_cookie() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(204)

    await proxy_request(
        method="POST",
        path="/api/v1/auth/logout",
        query=b"",
        headers=(
            (b"origin", b"http://127.0.0.1:28080"),
            (b"x-csrf-token", b"signed"),
            (b"cookie", b"child_manager_csrf=signed"),
        ),
        body=b"",
        peer_ip="127.0.0.1",
        api_base_url="http://127.0.0.1:28000",
        transport=httpx.MockTransport(handler),
    )

    request = captured[0]
    assert request.headers["origin"] == "http://127.0.0.1:28080"
    assert request.headers["x-csrf-token"] == "signed"
    assert "child_manager_csrf=signed" in request.headers["cookie"]


@pytest.mark.asyncio
async def test_bff_replaces_forged_internal_ip_header() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(204)

    await proxy_request(
        method="POST",
        path="/api/v1/auth/login",
        query=b"",
        headers=(
            (b"origin", b"http://127.0.0.1:28080"),
            (b"x-child-manager-client-ip", b"1.2.3.4"),
        ),
        body=b"",
        peer_ip="127.0.0.1",
        api_base_url="http://127.0.0.1:28000",
        transport=httpx.MockTransport(handler),
    )

    request = captured[0]
    assert request.headers["x-child-manager-client-ip"] == "127.0.0.1"


def _route_paths() -> set[str]:
    return {
        cast(str, getattr(route, "path", None)) for route in app.routes if hasattr(route, "path")
    }


def test_web_registers_login_page(_clear_routes: None) -> None:
    register_web(api_base_url="http://127.0.0.1:28000")
    assert "/login" in _route_paths()


def test_web_registers_change_password_page(_clear_routes: None) -> None:
    register_web(api_base_url="http://127.0.0.1:28000")
    assert "/change-password" in _route_paths()


def test_web_registers_user_management_page(_clear_routes: None) -> None:
    register_web(api_base_url="http://127.0.0.1:28000")
    assert "/users" in _route_paths()


def test_login_page_is_defined() -> None:
    assert callable(login_page)


def test_change_password_page_is_defined() -> None:
    assert callable(change_password_page)


def test_user_management_page_is_defined() -> None:
    assert callable(user_management_page)


def test_navigation_component_is_defined() -> None:
    assert callable(render_navigation)
