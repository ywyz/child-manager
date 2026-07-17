import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager

import httpx
import psycopg
import pytest
from alembic import command
from alembic.config import Config
from playwright.sync_api import Page, sync_playwright

from apps.web.components.navigation import navigation_for_capabilities
from apps.web.pages.auth import change_password_page_text, login_page_text
from apps.web.pages.users import users_page_text
from packages.backend.bootstrap.init_admin import initialize_admin


def test_login_and_change_password_pages_are_chinese_and_do_not_persist_tokens() -> None:
    assert {"用户名或手机号", "密码", "登录"} <= set(login_page_text())
    assert {"当前密码", "新密码", "修改密码"} <= set(change_password_page_text())
    rendered = " ".join(login_page_text() + change_password_page_text()).lower()
    assert "localstorage" not in rendered and "token" not in rendered and "cookie" not in rendered


def test_admin_account_page_exposes_create_reset_and_deactivate_flows() -> None:
    assert {"账号管理", "创建账号", "重置密码", "停用账号"} <= set(users_page_text())


def test_navigation_is_derived_from_current_api_capabilities() -> None:
    admin = navigation_for_capabilities(["users:manage", "plans:view"])
    teacher = navigation_for_capabilities(["plans:view"])
    assert "账号管理" in admin
    assert "账号管理" not in teacher
    assert "教案" in admin and "教案" in teacher


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_http(url: str, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 15
    last_status: int | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout is not None else ""
            raise AssertionError(f"服务启动失败: {url}\n{output}")
        try:
            with httpx.Client(trust_env=False, timeout=1) as client:
                last_status = client.get(url).status_code
                if last_status == 200:
                    return
        except httpx.HTTPError:
            time.sleep(0.1)
    raise AssertionError(f"服务未就绪: {url}, last_status={last_status}")


@contextmanager
def _m2_services(database_url: str) -> Iterator[tuple[str, int]]:
    api_port = _free_port()
    web_port = _free_port()
    redis_url = os.environ.get("CHILD_MANAGER_TEST_REDIS_URL")
    if not redis_url:
        raise AssertionError("必须设置 CHILD_MANAGER_TEST_REDIS_URL")
    environment = {
        **os.environ,
        "CHILD_MANAGER_DATABASE_URL": database_url,
        "CHILD_MANAGER_REDIS_URL": redis_url,
        "CHILD_MANAGER_LOGIN_THROTTLE_BACKEND": "redis",
        "CHILD_MANAGER_JWT_SIGNING_KEY": "browser-jwt-signing-key-that-is-long",
        "CHILD_MANAGER_CSRF_SIGNING_KEY": "browser-csrf-signing-key-that-is-long",
        "CHILD_MANAGER_COOKIE_SECURE": "false",
        "CHILD_MANAGER_ENV": "development",
        "CHILD_MANAGER_WEB_PORT": str(web_port),
        "CHILD_MANAGER_ALLOWED_ORIGINS": f"http://127.0.0.1:{web_port}",
        "CHILD_MANAGER_TRUSTED_BFF_PEERS": "127.0.0.1",
        "NICEGUI_SCREEN_TEST_PORT": str(web_port),
    }
    api = subprocess.Popen(
        [sys.executable, "-m", "apps.api", "--host", "127.0.0.1", "--port", str(api_port)],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    web = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "apps.web",
            "--host",
            "127.0.0.1",
            "--port",
            str(web_port),
            "--api-base-url",
            f"http://127.0.0.1:{api_port}",
        ],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_http(f"http://127.0.0.1:{api_port}/health/live", api)
        _wait_http(f"http://127.0.0.1:{web_port}/login", web)
        yield f"http://127.0.0.1:{web_port}", api_port
    finally:
        for process in (web, api):
            process.terminate()
        for process in (web, api):
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def _login(page: Page, base_url: str, username: str, password: str) -> None:
    page.goto(f"{base_url}/login")
    page.get_by_label("用户名或手机号").fill(username)
    page.get_by_label("密码").fill(password)
    page.get_by_role("button", name="登录").click()
    page.wait_for_url(f"{base_url}/")


def test_browser_auth_and_account_management_flow(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    initialize_admin(
        database_url=isolated_database_url,
        kindergarten_name="浏览器验收幼儿园",
        username="admin",
        display_name="浏览器管理员",
        password="管理员足够长的安全测试密码 2026",
    )
    with _m2_services(isolated_database_url) as (base_url, api_port), sync_playwright() as manager:
        browser = manager.chromium.launch(headless=True)
        admin_context = browser.new_context()
        admin_page = admin_context.new_page()
        requested_urls: list[str] = []
        admin_page.on("request", lambda request: requested_urls.append(request.url))

        _login(admin_page, base_url, "admin", "管理员足够长的安全测试密码 2026")
        admin_page.get_by_text("账号管理", exact=True).wait_for()
        cookies = {str(cookie.get("name")): cookie for cookie in admin_context.cookies()}
        access_cookie = cookies["child_manager_access"]
        refresh_cookie = cookies["child_manager_refresh"]
        assert access_cookie.get("httpOnly") is True
        assert refresh_cookie.get("httpOnly") is True
        assert access_cookie.get("sameSite") == "Lax"
        old_refresh = str(refresh_cookie.get("value"))

        refresh_status = admin_page.evaluate(
            """async () => {
              const csrf = await (await fetch('/api/v1/auth/csrf')).json();
              return (await fetch('/api/v1/auth/refresh', {
                method: 'POST', headers: {'X-CSRF-Token': csrf.csrf_token}
              })).status;
            }"""
        )
        assert refresh_status == 200
        assert {str(cookie.get("name")): cookie for cookie in admin_context.cookies()}[
            "child_manager_refresh"
        ].get("value") != old_refresh

        admin_page.get_by_text("账号管理", exact=True).click()
        admin_page.wait_for_url(f"{base_url}/users")
        admin_page.get_by_label("用户名").fill("browser-teacher")
        admin_page.get_by_label("姓名").fill("浏览器教师")
        admin_page.get_by_label("初始密码").fill("教师足够长的安全测试密码 2026")
        admin_page.get_by_role("button", name="创建账号").click()
        admin_page.get_by_text("账号已创建。").wait_for()
        teacher_id = admin_page.evaluate(
            """async () => {
              const body = await (await fetch('/api/v1/users?page=1&page_size=100')).json();
              return body.items.find(item => item.username === 'browser-teacher').id;
            }"""
        )
        admin_page.get_by_label("账号 ID").fill(teacher_id)
        admin_page.get_by_label("重置后的密码").fill("教师重置后的足够长安全密码 2026")
        admin_page.get_by_role("button", name="重置密码").click()
        admin_page.get_by_text("密码已重置。").wait_for()

        teacher_context = browser.new_context()
        teacher_page = teacher_context.new_page()
        _login(teacher_page, base_url, "browser-teacher", "教师重置后的足够长安全密码 2026")
        teacher_page.get_by_text("账号管理", exact=True).wait_for(state="detached")

        admin_page.get_by_role("button", name="停用账号").click()
        admin_page.get_by_text("账号已停用。").wait_for()
        assert teacher_page.evaluate("async () => (await fetch('/api/v1/auth/me')).status") == 401

        admin_page.goto(f"{base_url}/change-password")
        admin_page.get_by_label("当前密码").fill("管理员足够长的安全测试密码 2026")
        admin_page.get_by_label("新密码").fill("管理员修改后的足够长安全密码 2026")
        admin_page.get_by_role("button", name="修改密码").click()
        admin_page.wait_for_url(f"{base_url}/login")
        _login(admin_page, base_url, "admin", "管理员修改后的足够长安全密码 2026")

        forged_status = admin_page.evaluate(
            """async () => {
              const csrf = await (await fetch('/api/v1/auth/csrf')).json();
              return (await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRF-Token': csrf.csrf_token,
                  'X-Child-Manager-Client-IP': '203.0.113.99'
                },
                body: JSON.stringify({
                  login: 'missing-browser-user', password: '错误但足够长密码 2026'
                })
              })).status;
            }"""
        )
        assert forged_status == 401
        admin_page.get_by_role("button", name="退出登录").click()
        admin_page.wait_for_url(f"{base_url}/login")
        auth_cookie_names = {
            str(cookie.get("name"))
            for cookie in admin_context.cookies()
            if cookie.get("name") in {"child_manager_access", "child_manager_refresh"}
        }
        assert auth_cookie_names == set()
        assert all(f":{api_port}/" not in url for url in requested_urls)
        browser.close()

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        source = connection.execute(
            """SELECT metadata->>'source' FROM audit_events
            WHERE event_code='identity.login_failed' ORDER BY occurred_at DESC LIMIT 1"""
        ).fetchone()
    assert source is not None and source[0] == "127.0.0.1"
