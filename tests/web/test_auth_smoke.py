"""Web 认证流程 BFF 冒烟测试。"""

import json
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
def _set_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    from packages.backend.config import settings

    monkeypatch.setattr(
        settings,
        "jwt_signing_key",
        "test-jwt-signing-key-32bytes-long-12345",
        raising=False,
    )
    monkeypatch.setattr(
        settings,
        "csrf_signing_key",
        "test-csrf-signing-key-32bytes-long-1234",
        raising=False,
    )


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
        body=b'{"login":"admin","password":"ValidPassword2024!"}',
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


def test_navigation_shows_admin_entry_for_admin() -> None:
    from apps.web.components.navigation import _nav_html

    html = _nav_html(["admin"])
    assert "账号管理" in html
    assert "/users" in html


def test_navigation_hides_admin_entry_for_teacher() -> None:
    from apps.web.components.navigation import _nav_html

    html = _nav_html(["teacher"])
    assert "账号管理" not in html


@pytest.mark.asyncio
async def test_bff_full_auth_flow_against_real_api(migrated_database_url: str) -> None:
    """通过 BFF 代理访问真实 API，验证登录-刷新-改密-退出完整流程。"""
    from apps.api.app import create_app
    from apps.api.dependencies import HealthDependencies
    from packages.backend.database import session as session_module
    from packages.backend.identity.service import IdentityService

    async def _true() -> bool:
        return True

    api_app = create_app(
        dependencies=HealthDependencies(
            database=_true,
            redis=_true,
            ai=_true,
            calendar=_true,
            template=_true,
            export_storage=_true,
            security_ready=True,
        )
    )

    session = session_module.SessionLocal()
    try:
        service = IdentityService(session)
        service.init_admin(
            kg_name="BFF 测试园", admin_username="admin", password="ValidPassword2024!"
        )
        session.commit()
    finally:
        session.close()

    transport = httpx.ASGITransport(app=api_app)
    api_base_url = "http://testserver"
    peer_ip = "127.0.0.1"
    origin = "http://127.0.0.1:28080"

    csrf = await proxy_request(
        method="GET",
        path="/api/v1/auth/csrf",
        query=b"",
        headers=(),
        body=b"",
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert csrf.status_code == 200
    csrf_token = json.loads(csrf.body)["csrf_token"]

    common_headers = (
        (b"origin", origin.encode("ascii")),
        (b"x-csrf-token", csrf_token.encode("ascii")),
        (b"content-type", b"application/json"),
    )
    csrf_cookie = f"child_manager_csrf={csrf_token}".encode("ascii")

    login = await proxy_request(
        method="POST",
        path="/api/v1/auth/login",
        query=b"",
        headers=(*common_headers, (b"cookie", csrf_cookie)),
        body=json.dumps({"login": "admin", "password": "ValidPassword2024!"}).encode("utf-8"),
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert login.status_code == 200
    login_body = json.loads(login.body)
    assert login_body["id"]
    assert "admin" in login_body["role_codes"]
    set_cookies = [v for n, v in login.headers if n.lower() == b"set-cookie"]
    assert len(set_cookies) == 3
    cookie_header = b"; ".join(set_cookies)

    def _extract_cookie(cookies: bytes, name: bytes) -> bytes:
        for part in cookies.split(b"; "):
            if part.startswith(name + b"="):
                return part.split(b"=", 1)[1].split(b";", 1)[0]
        return b""

    csrf_after_login = _extract_cookie(cookie_header, b"child_manager_csrf").decode("ascii")
    refresh_headers = (
        (b"origin", origin.encode("ascii")),
        (b"x-csrf-token", csrf_after_login.encode("ascii")),
        (b"content-type", b"application/json"),
    )

    refresh = await proxy_request(
        method="POST",
        path="/api/v1/auth/refresh",
        query=b"",
        headers=(*refresh_headers, (b"cookie", cookie_header)),
        body=b"",
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert refresh.status_code == 200
    refresh_body = json.loads(refresh.body)
    assert refresh_body["id"] == login_body["id"]
    refresh_cookies = [v for n, v in refresh.headers if n.lower() == b"set-cookie"]
    assert len(refresh_cookies) == 3
    refresh_cookie_header = b"; ".join(refresh_cookies)
    csrf_after_refresh = _extract_cookie(refresh_cookie_header, b"child_manager_csrf").decode(
        "ascii"
    )
    state_headers = (
        (b"origin", origin.encode("ascii")),
        (b"x-csrf-token", csrf_after_refresh.encode("ascii")),
        (b"content-type", b"application/json"),
    )

    change_pw = await proxy_request(
        method="POST",
        path="/api/v1/auth/change-password",
        query=b"",
        headers=(*state_headers, (b"cookie", refresh_cookie_header)),
        body=json.dumps(
            {"current_password": "ValidPassword2024!", "new_password": "NewPassword2024!"}
        ).encode("utf-8"),
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert change_pw.status_code == 204

    # 改密后旧 Access Token 已失效，使用新密码重新登录以继续账号管理操作。
    re_login = await proxy_request(
        method="POST",
        path="/api/v1/auth/login",
        query=b"",
        headers=(*common_headers, (b"cookie", csrf_cookie)),
        body=json.dumps({"login": "admin", "password": "NewPassword2024!"}).encode("utf-8"),
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert re_login.status_code == 200
    re_login_cookies = [v for n, v in re_login.headers if n.lower() == b"set-cookie"]
    assert len(re_login_cookies) == 3
    re_login_cookie_header = b"; ".join(re_login_cookies)
    csrf_after_re_login = _extract_cookie(re_login_cookie_header, b"child_manager_csrf").decode(
        "ascii"
    )
    admin_headers = (
        (b"origin", origin.encode("ascii")),
        (b"x-csrf-token", csrf_after_re_login.encode("ascii")),
        (b"content-type", b"application/json"),
    )

    # 账号管理闭环：创建、列表、重置密码、调整角色、停用后失权、重新启用
    create_user = await proxy_request(
        method="POST",
        path="/api/v1/users",
        query=b"",
        headers=(*admin_headers, (b"cookie", re_login_cookie_header)),
        body=json.dumps(
            {
                "username": "teacher_smoke",
                "display_name": "冒烟教师",
                "phone_e164": None,
                "role_codes": ["teacher"],
                "password": "ValidPassword2024!",
            }
        ).encode("utf-8"),
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert create_user.status_code == 201
    teacher_id = json.loads(create_user.body)["id"]

    list_users = await proxy_request(
        method="GET",
        path="/api/v1/users",
        query=b"",
        headers=(*admin_headers, (b"cookie", re_login_cookie_header)),
        body=b"",
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert list_users.status_code == 200
    assert any(u["username"] == "teacher_smoke" for u in json.loads(list_users.body)["items"])

    reset_pw = await proxy_request(
        method="POST",
        path=f"/api/v1/users/{teacher_id}/reset-password",
        query=b"",
        headers=(*admin_headers, (b"cookie", re_login_cookie_header)),
        body=json.dumps({"new_password": "ResetPassword2024!"}).encode("utf-8"),
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert reset_pw.status_code == 204

    set_roles = await proxy_request(
        method="PUT",
        path=f"/api/v1/users/{teacher_id}/roles",
        query=b"",
        headers=(*admin_headers, (b"cookie", re_login_cookie_header)),
        body=json.dumps({"role_codes": ["teacher", "admin"]}).encode("utf-8"),
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert set_roles.status_code == 200
    assert set(json.loads(set_roles.body)["role_codes"]) == {"teacher", "admin"}

    deactivate = await proxy_request(
        method="POST",
        path=f"/api/v1/users/{teacher_id}/deactivate",
        query=b"",
        headers=(*admin_headers, (b"cookie", re_login_cookie_header)),
        body=b"",
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert deactivate.status_code == 200
    assert json.loads(deactivate.body)["is_active"] is False

    failed_login = await proxy_request(
        method="POST",
        path="/api/v1/auth/login",
        query=b"",
        headers=(*admin_headers, (b"cookie", re_login_cookie_header)),
        body=json.dumps({"login": "teacher_smoke", "password": "ResetPassword2024!"}).encode(
            "utf-8"
        ),
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert failed_login.status_code == 401
    assert json.loads(failed_login.body)["code"] == "auth.login_failed"

    activate = await proxy_request(
        method="POST",
        path=f"/api/v1/users/{teacher_id}/activate",
        query=b"",
        headers=(*admin_headers, (b"cookie", re_login_cookie_header)),
        body=b"",
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert activate.status_code == 200
    assert json.loads(activate.body)["is_active"] is True

    logout = await proxy_request(
        method="POST",
        path="/api/v1/auth/logout",
        query=b"",
        headers=(*admin_headers, (b"cookie", re_login_cookie_header)),
        body=b"",
        peer_ip=peer_ip,
        api_base_url=api_base_url,
        transport=transport,
    )
    assert logout.status_code == 204
    logout_cookies = [v for n, v in logout.headers if n.lower() == b"set-cookie"]
    assert len(logout_cookies) == 3
    assert all(b"Max-Age=0" in c for c in logout_cookies)
