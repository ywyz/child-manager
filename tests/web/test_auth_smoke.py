import os
import re
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

import httpx
import pytest
from alembic import command
from alembic.config import Config
from playwright.sync_api import BrowserContext, Page, sync_playwright

from apps.web.components.navigation import navigation_for_capabilities
from apps.web.pages.auth import login_page_text
from apps.web.pages.users import users_page_text


def test_auth_pages_expose_passkey_invitation_recovery_and_session_flows() -> None:
    auth_text = set(login_page_text())
    users_text = set(users_page_text())

    assert {"使用通行密钥登录", "邀请登记", "账号恢复"} <= auth_text
    assert {
        "账号管理",
        "签发邀请",
        "通行密钥",
        "新增通行密钥",
        "命名通行密钥",
        "撤销通行密钥",
        "重新邀请",
        "撤销会话",
        "恢复申请",
    } <= users_text
    rendered = " ".join(auth_text | users_text).lower()
    assert "密码" not in rendered
    assert "localstorage" not in rendered and "token" not in rendered


def test_navigation_is_derived_from_current_api_capabilities() -> None:
    admin = navigation_for_capabilities(["users:manage", "credentials:manage", "plans:view"])
    teacher = navigation_for_capabilities(["credentials:manage", "plans:view"])

    assert "账号管理" in admin
    assert "账号管理" not in teacher
    assert "通行密钥与会话" in admin and "通行密钥与会话" in teacher


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


@dataclass(frozen=True)
class BootstrapMaterial:
    bootstrap_id: str
    secret: str


def _bootstrap_start(database_url: str) -> BootstrapMaterial:
    environment = {**os.environ, "CHILD_MANAGER_DATABASE_URL": database_url}
    result = subprocess.run(
        [sys.executable, "-m", "packages.backend.bootstrap", "init-admin", "start"],
        input="测试幼儿园\nadmin\n测试管理员\nowner-ref-001\noperator-ref-002\n",
        text=True,
        capture_output=True,
        env=environment,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    output = result.stdout + result.stderr
    bootstrap_id = re.search(
        r"初始化(?:记录|ID)[：:]\s*([0-9a-f-]{36})",
        output,
        re.IGNORECASE,
    )
    secret = re.search(r"初始化凭据[：:]\s*([A-Za-z0-9_-]{22,})", output)
    assert bootstrap_id is not None
    assert secret is not None
    assert secret.group(1) not in re.sub(r"初始化凭据[^\n]*", "", output)
    assert "http://" not in output and "https://" not in output
    return BootstrapMaterial(bootstrap_id.group(1), secret.group(1))


def _bootstrap_activate(database_url: str, bootstrap_id: str) -> None:
    environment = {**os.environ, "CHILD_MANAGER_DATABASE_URL": database_url}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "packages.backend.bootstrap",
            "init-admin",
            "activate",
            "--bootstrap-id",
            bootstrap_id,
        ],
        input="owner-ref-001\noperator-ref-002\n",
        text=True,
        capture_output=True,
        env=environment,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "已激活" in result.stdout


@contextmanager
def _m2_services(database_url: str) -> Iterator[tuple[str, int]]:
    api_port = _free_port()
    web_port = _free_port()
    environment = {
        **os.environ,
        "CHILD_MANAGER_DATABASE_URL": database_url,
        "CHILD_MANAGER_AUTH_THROTTLE_BACKEND": "memory",
        "CHILD_MANAGER_JWT_SIGNING_KEY": "browser-jwt-signing-key-that-is-long",
        "CHILD_MANAGER_CSRF_SIGNING_KEY": "browser-csrf-signing-key-that-is-long",
        "CHILD_MANAGER_COOKIE_SECURE": "false",
        "CHILD_MANAGER_ENV": "development",
        "CHILD_MANAGER_WEB_PORT": str(web_port),
        "CHILD_MANAGER_ALLOWED_ORIGINS": f"http://127.0.0.1:{web_port}",
        "CHILD_MANAGER_TRUSTED_BFF_PEERS": "127.0.0.1",
        "CHILD_MANAGER_WEBAUTHN_RP_ID": "localhost",
        "CHILD_MANAGER_WEBAUTHN_RP_NAME": "Child Manager Tests",
        "CHILD_MANAGER_AUTH_THROTTLE_FAILURE_LIMIT": "2",
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
        yield f"http://localhost:{web_port}", api_port
    finally:
        for process in (web, api):
            process.terminate()
        for process in (web, api):
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def _add_virtual_authenticator(context: BrowserContext, page: Page) -> str:
    cdp = context.new_cdp_session(page)
    cdp.send("WebAuthn.enable")
    result = cdp.send(
        "WebAuthn.addVirtualAuthenticator",
        {
            "options": {
                "protocol": "ctap2",
                "transport": "internal",
                "hasResidentKey": True,
                "hasUserVerification": True,
                "isUserVerified": True,
                "automaticPresenceSimulation": True,
            }
        },
    )
    return str(result["authenticatorId"])


def _auth_cookie_names(context: BrowserContext) -> set[str]:
    return {
        str(cookie.get("name"))
        for cookie in context.cookies()
        if cookie.get("name") in {"child_manager_access", "child_manager_refresh"}
    }


def test_browser_completes_passkey_invitation_recovery_credential_and_session_journey(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    bootstrap = _bootstrap_start(isolated_database_url)

    with _m2_services(isolated_database_url) as (base_url, api_port), sync_playwright() as manager:
        browser = manager.chromium.launch(headless=True)
        admin_context = browser.new_context()
        admin_page = admin_context.new_page()
        admin_authenticator = _add_virtual_authenticator(admin_context, admin_page)
        requested_urls: list[str] = []
        admin_page.on("request", lambda request: requested_urls.append(request.url))

        admin_page.goto(f"{base_url}/initialize")
        admin_page.get_by_label("初始化凭据").fill(bootstrap.secret)
        admin_page.get_by_role("button", name="登记首位管理员通行密钥").click()
        admin_page.get_by_text("等待双人核验").wait_for()
        assert _auth_cookie_names(admin_context) == set()
        _bootstrap_activate(isolated_database_url, bootstrap.bootstrap_id)

        admin_page.goto(f"{base_url}/login")
        admin_page.get_by_role("button", name="使用通行密钥登录").click()
        admin_page.get_by_text("首页").wait_for()
        admin_recovery_code = admin_page.get_by_test_id("recovery-code-once").text_content()
        assert admin_recovery_code

        admin_page.goto(f"{base_url}/users")
        admin_page.get_by_label("用户名").fill("teacher")
        admin_page.get_by_label("姓名").fill("测试教师")
        admin_page.get_by_role("button", name="创建账号").click()
        teacher_id = admin_page.get_by_test_id("created-user-id").text_content()
        assert teacher_id
        admin_page.get_by_test_id(f"issue-invitation-{teacher_id}").click()
        invitation = admin_page.get_by_test_id("invitation-token-once").text_content()
        assert invitation

        teacher_context = browser.new_context()
        teacher_page = teacher_context.new_page()
        teacher_authenticator = _add_virtual_authenticator(teacher_context, teacher_page)
        teacher_page.on("request", lambda request: requested_urls.append(request.url))
        teacher_page.goto(f"{base_url}/register")
        teacher_page.get_by_label("邀请凭据").fill(invitation)
        teacher_page.get_by_role("button", name="登记通行密钥").click()
        teacher_page.get_by_text("等待管理员核验").wait_for()
        assert _auth_cookie_names(teacher_context) == set()

        admin_page.reload()
        admin_page.get_by_test_id(f"activate-user-{teacher_id}").click()
        admin_page.get_by_text("账号已激活").wait_for()
        teacher_page.goto(f"{base_url}/login")
        teacher_page.get_by_role("button", name="使用通行密钥登录").click()
        teacher_page.get_by_text("首页").wait_for()
        teacher_recovery_code = teacher_page.get_by_test_id("recovery-code-once").text_content()
        assert teacher_recovery_code

        teacher_page.goto(f"{base_url}/account/security")
        teacher_page.get_by_role("button", name="重新验证").click()
        teacher_page.get_by_role("button", name="新增通行密钥").click()
        teacher_page.get_by_label("通行密钥名称").fill("备用通行密钥")
        teacher_page.get_by_role("button", name="保存名称").click()
        teacher_page.get_by_test_id("revoke-primary-credential").click()
        teacher_page.get_by_text("凭据已撤销").wait_for()

        admin_page.goto(f"{base_url}/users/{teacher_id}/security")
        admin_page.get_by_role("button", name="撤销教师最后凭据并重新邀请").click()
        reinvitation = admin_page.get_by_test_id("invitation-token-once").text_content()
        assert reinvitation
        teacher_page.reload()
        teacher_page.get_by_text("登录状态已失效").wait_for()

        teacher_page.goto(f"{base_url}/recover")
        teacher_page.get_by_label("用户名或手机号").fill("teacher")
        teacher_page.get_by_label("离线恢复码").fill(teacher_recovery_code)
        teacher_page.get_by_role("button", name="提交恢复申请").click()
        teacher_page.get_by_text("继续核验").wait_for()
        assert _auth_cookie_names(teacher_context) == set()

        admin_page.goto(f"{base_url}/users/{teacher_id}/recovery")
        admin_page.get_by_role("button", name="批准恢复登记").click()
        enrollment = admin_page.get_by_test_id("recovery-enrollment-token-once").text_content()
        assert enrollment
        teacher_page.goto(f"{base_url}/recover/register")
        teacher_page.get_by_label("恢复登记凭据").fill(enrollment)
        teacher_page.get_by_role("button", name="登记新通行密钥").click()
        new_recovery_code = teacher_page.get_by_test_id("recovery-code-once").text_content()
        assert new_recovery_code and new_recovery_code != teacher_recovery_code
        assert _auth_cookie_names(teacher_context) == set()

        teacher_page.goto(f"{base_url}/login")
        teacher_page.get_by_role("button", name="使用通行密钥登录").click()
        teacher_page.get_by_text("首页").wait_for()
        teacher_page.goto(f"{base_url}/account/security")
        teacher_page.get_by_role("button", name="撤销当前会话").click()
        teacher_page.get_by_role("button", name="使用通行密钥登录").wait_for()

        options_statuses = teacher_page.evaluate(
            """async () => {
              const csrfResponse = await fetch('/api/v1/auth/csrf', {credentials: 'same-origin'});
              const csrf = await csrfResponse.json();
              const values = ['198.51.100.1', '203.0.113.2', '192.0.2.3'];
              const statuses = [];
              for (const value of values) {
                const response = await fetch('/api/v1/auth/authentication/options', {
                  method: 'POST', credentials: 'same-origin',
                  headers: {
                    'X-CSRF-Token': csrf.csrf_token,
                    'X-Child-Manager-Client-IP': value,
                    'X-Forwarded-For': value,
                  },
                });
                statuses.push(response.status);
              }
              return statuses;
            }"""
        )

        assert admin_authenticator
        assert teacher_authenticator
        assert options_statuses == [200, 200, 200]
        assert all(f":{api_port}/" not in url for url in requested_urls)
        browser.close()
