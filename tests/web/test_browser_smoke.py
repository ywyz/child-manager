"""Playwright 真实浏览器冒烟测试。

T025/T034 要求浏览器冒烟覆盖 Cookie 交换、导航与失败反馈闭环。
现有 ``test_auth_smoke.py`` 通过 httpx ASGITransport 验证 BFF 与 API
契约，但无法覆盖浏览器执行 ``ui.run_javascript`` 的真实行为。本模块
使用 Playwright 启动真实 Chromium，验证以下闭环：

1. 登录成功后浏览器获得 access/refresh/csrf 三条 Cookie，并导航到首页；
2. 点击退出后浏览器导航到 /login；
3. 登录失败时页面显示中文错误信息（不导航到首页）。

环境要求：
- PostgreSQL 与 Redis 容器在 127.0.0.1 上可用；
- Playwright chromium 浏览器已安装（``uv run playwright install chromium``）。
"""

import os
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_url(url: str, timeout: float = 30.0) -> None:
    """轮询等待服务器在回环地址上就绪。

    使用 ``httpx.Client(trust_env=False)`` 显式忽略进程代理环境变量
    （``HTTP_PROXY``/``ALL_PROXY`` 等），避免在配置了 SOCKS/HTTP 代理的
    开发机上探针因代理解析错误而误报服务器未启动（Codex 第十六轮审阅）。
    """
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with httpx.Client(trust_env=False) as client:
                response = client.get(url, timeout=1.0, follow_redirects=True)
                if response.status_code < 500:
                    return
        except Exception as exc:
            last_error = exc
        time.sleep(0.2)
    raise RuntimeError(f"Server at {url} did not start within {timeout}s: {last_error}")


def _clean_proxy_env(env: dict[str, str]) -> dict[str, str]:
    """清理子进程代理变量并固定回环地址不走代理。

    Codex 第十六轮审阅发现：Web/Chromium 子进程继承进程代理变量后，回环
    就绪探针和浏览器请求会尝试经 SOCKS/HTTP 代理访问 127.0.0.1，导致连接
    失败。这里删除所有代理相关变量，并显式设置 ``NO_PROXY`` 覆盖回环地址，
    确保子进程不会把回环流量导向代理。
    """
    proxy_keys = (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "NO_PROXY",
        "no_proxy",
    )
    cleaned = {k: v for k, v in env.items() if k not in proxy_keys}
    # 显式让回环地址与常见本地主机名不走代理。
    cleaned["NO_PROXY"] = "127.0.0.1,localhost,::1"
    cleaned["no_proxy"] = "127.0.0.1,localhost,::1"
    return cleaned


async def _block_non_web_origins(
    context: Any,
    web_url: str,
    api_url: str,
) -> None:
    """注册 ``context.route`` 拒绝所有非 Web 同源请求。

    T025/T034 要求浏览器不直连 API 端口，所有 API 调用必须经 Web BFF
    同源代理。这里拦截所有请求，只放行目标为 Web 服务器（同源）的请求，
    其他请求（包括直连 API 端口）一律 abort，证明浏览器不绕过 BFF。
    """
    from urllib.parse import urlparse

    web_host = urlparse(web_url).netloc

    async def _route_handler(route: Any) -> None:
        target = urlparse(route.request.url).netloc
        if target == web_host:
            await route.continue_()
        else:
            await route.abort("blockedbyclient")

    await context.route("**/*", _route_handler)


async def _browser_login(
    page: Any,
    web_url: str,
    username: str,
    password: str,
) -> None:
    """通过浏览器 UI 执行登录并等待导航到首页。

    封装登录流程供多个冒烟测试复用：打开 /login -> 填写凭据 -> 点击登录 ->
    等待导航到首页。CSRF 预取完成后登录按钮才启用，Playwright 自动等待。
    """
    await page.goto(f"{web_url}/login")
    await page.wait_for_selector("text=登录", timeout=10000)
    await page.locator("input").first.fill(username)
    await page.locator("input[type='password']").first.fill(password)
    await page.get_by_role("button", name="登录").click()
    await page.wait_for_url(f"{web_url}/", timeout=15000)


def _fetch_csrf(api_url: str) -> str:
    """从 API 获取 CSRF 令牌（setup 辅助，非被测对象）。"""
    import httpx

    response = httpx.get(f"{api_url}/api/v1/auth/csrf", trust_env=False)
    assert response.status_code == 200
    return response.json()["csrf_token"]


async def _wait_for_success_message(page: Any) -> None:
    """等待账号管理页面的“操作成功”提示出现。

    NiceGUI 的 message label 初始为空且带 ``text-red-500``；成功时 ``set_text``
    写入“操作成功”并切到 ``text-green-500``。用 ``wait_for_function`` 轮询
    避免初始空文本导致 ``inner_text`` 立即返回空值。若出现红色错误信息则
    立即失败并报告错误内容，便于诊断。
    """
    import asyncio as _asyncio

    deadline = _asyncio.get_event_loop().time() + 15.0
    while _asyncio.get_event_loop().time() < deadline:
        error_text = await page.evaluate(
            """() => {
                const red = document.querySelector('.text-red-500');
                if (red && red.innerText && red.innerText.trim().length > 0
                    && !red.innerText.includes('操作成功')) {
                    return red.innerText.trim();
                }
                const green = document.querySelector('.text-green-500');
                if (green && green.innerText && green.innerText.includes('操作成功')) {
                    return '';
                }
                return null;
            }"""
        )
        if error_text == "":
            return  # 成功
        if error_text:
            raise AssertionError(f"账号操作失败: {error_text}")
        await page.wait_for_timeout(200)
    raise AssertionError("等待操作成功消息超时（15s 内未出现操作成功或错误提示）")


async def _fill_nicegui_input(page: Any, label: str, value: str) -> None:
    """按 label 文本定位 NiceGUI QInput 并填值。

    NiceGUI ``ui.input("label")`` 渲染为 Quasar QField，label 文本在
    ``.q-field__label`` 中。用 ``filter(has_text=)`` 定位包含该 label 的
    QField，再在其下找 ``input`` 填值。
    """
    field = page.locator(".q-field").filter(has_text=label)
    await field.locator("input").fill(value)


@pytest.fixture
def browser_stack(migrated_database_url: str) -> Iterator[tuple[str, str, str]]:
    """启动 API + Web 服务器供 Playwright 测试。

    API 服务器在进程内以 uvicorn 线程启动，共享 ``migrated_database_url``
    fixture 的隔离 schema。Web 服务器以子进程启动，避免 NiceGUI 全局
    ``app`` 对象与测试进程冲突。

    返回 ``(api_url, web_url, admin_password)``。
    """
    api_port = _find_free_port()
    web_port = _find_free_port()
    api_url = f"http://127.0.0.1:{api_port}"
    web_url = f"http://127.0.0.1:{web_port}"

    # 1. 启动 API 服务器（进程内 uvicorn 线程，共享隔离 schema）。
    # 同步把 ``settings.web_port`` 临时改为本测试 Web 服务器的随机端口，
    # 否则 CSRF Origin 校验会因 Origin 不在白名单内而失败。
    import uvicorn

    from apps.api.app import create_app
    from apps.api.dependencies import HealthDependencies
    from packages.backend.config import settings as settings_module
    from packages.backend.database import session as session_module
    from packages.backend.identity.service import IdentityService

    original_web_port = settings_module.web_port
    settings_module.web_port = web_port

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

    # 初始化管理员账号（使用 fixture 已 patch 的 SessionLocal）
    session = session_module.SessionLocal()
    try:
        service = IdentityService(session)
        service.init_admin(
            kg_name="浏览器测试园",
            admin_username="admin",
            password="ValidPassword2024!",
        )
        session.commit()
    finally:
        session.close()

    api_config = uvicorn.Config(
        app=api_app,
        host="127.0.0.1",
        port=api_port,
        log_level="error",
        loop="asyncio",
    )
    api_server = uvicorn.Server(api_config)
    api_thread = threading.Thread(target=api_server.run, daemon=True)
    api_thread.start()
    _wait_for_url(f"{api_url}/health")

    # 2. 启动 Web 服务器（子进程，避免 NiceGUI 全局状态冲突）。
    # 必须以 ``python -m tests.web.browser_test_server`` 模块方式运行，
    # 否则 ``apps`` 命名空间包在脚本直接执行模式下无法被解析。
    # 同时清除 ``PYTEST_CURRENT_TEST`` 等环境变量，避免 NiceGUI 误判
    # 子进程处于 pytest 测试模式而尝试使用 pytest 专用端口。
    repo_root = Path(__file__).resolve().parent.parent.parent
    env = os.environ.copy()
    env["CHILD_MANAGER_TEST_API_BASE_URL"] = api_url
    env["CHILD_MANAGER_TEST_WEB_PORT"] = str(web_port)
    env["PYTHONPATH"] = os.pathsep.join(
        str(repo_root / sub) for sub in ("apps", "packages", "tests")
    )
    for key in ("PYTEST_CURRENT_TEST", "NICEGUI_USER_SIMULATION"):
        env.pop(key, None)
    # 清理代理变量，避免 Web 子进程把回环请求导向 SOCKS/HTTP 代理。
    env = _clean_proxy_env(env)

    web_proc = subprocess.Popen(
        [sys.executable, "-m", "tests.web.browser_test_server"],
        env=env,
        cwd=str(repo_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        try:
            _wait_for_url(web_url)
        except RuntimeError:
            # 启动失败时打印子进程输出便于诊断
            web_proc.terminate()
            try:
                stdout, stderr = web_proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                web_proc.kill()
                stdout, stderr = web_proc.communicate(timeout=5)
            raise RuntimeError(
                f"Web 服务器启动失败。\nSTDOUT:\n{stdout.decode(errors='replace')}\n"
                f"STDERR:\n{stderr.decode(errors='replace')}"
            ) from None
        yield api_url, web_url, "ValidPassword2024!"
    finally:
        web_proc.terminate()
        try:
            # 读取 pipe 内容防止 ResourceWarning: unclosed file
            web_proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            web_proc.kill()
            web_proc.communicate(timeout=5)

        api_server.should_exit = True
        api_thread.join(timeout=5)

        # 恢复 settings.web_port 避免污染其他测试
        settings_module.web_port = original_web_port


@pytest.mark.asyncio
async def test_browser_login_logout_flow(browser_stack: tuple[str, str, str]) -> None:
    """Playwright 真实浏览器测试：登录 -> Cookie 设置 -> 退出 -> Cookie 清除 -> 导航闭环。

    T025 要求浏览器冒烟覆盖 Cookie 交换与导航闭环；Codex 第十六轮审阅要求
    断言退出后两条 auth Cookie 已清除。本测试还通过 ``context.route`` 拒绝
    所有非 Web 同源请求，证明浏览器不直连 API。
    """
    from playwright.async_api import async_playwright

    api_url, web_url, password = browser_stack

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()
        await _block_non_web_origins(context, web_url, api_url)
        page = await context.new_page()

        try:
            await _browser_login(page, web_url, "admin", password)

            # 验证 auth Cookie 已设置（浏览器真实 cookie jar）
            cookies = await context.cookies()
            cookie_names = {c.get("name", "") for c in cookies}
            assert "child_manager_access" in cookie_names, f"缺少 access cookie: {cookie_names}"
            assert "child_manager_refresh" in cookie_names, f"缺少 refresh cookie: {cookie_names}"
            assert "child_manager_csrf" in cookie_names, f"缺少 csrf cookie: {cookie_names}"

            # 点击退出
            await page.get_by_role("button", name="退出").click()
            await page.wait_for_url(f"{web_url}/login", timeout=15000)

            # 关键断言：退出后两条 auth Cookie 必须已被清除。
            # logout 响应通过 Max-Age=0 清除 Cookie，浏览器导航到 /login 后
            # cookie jar 中不应再保留 access/refresh（csrf 同样清除）。
            cookies_after = await context.cookies()
            names_after = {c.get("name", "") for c in cookies_after}
            assert "child_manager_access" not in names_after, (
                f"退出后 access cookie 仍存在: {names_after}"
            )
            assert "child_manager_refresh" not in names_after, (
                f"退出后 refresh cookie 仍存在: {names_after}"
            )
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_browser_failed_login_shows_error(
    browser_stack: tuple[str, str, str],
) -> None:
    """Playwright 真实浏览器测试：登录失败显示中文错误信息。

    T025/T034 要求失败反馈闭环。本测试验证：
    1. 填写错误密码并点击登录；
    2. 页面显示中文错误信息（不导航到首页）。

    NiceGUI 登录页的 error label 使用 ``text-red-500`` 类。登录失败时
    ``ui.run_javascript`` 返回 API 错误信息，Python 端设置 error label。
    """
    from playwright.async_api import async_playwright

    api_url, web_url, _ = browser_stack

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()
        await _block_non_web_origins(context, web_url, api_url)
        page = await context.new_page()

        try:
            await page.goto(f"{web_url}/login")
            await page.wait_for_selector("text=登录", timeout=10000)

            # 填写错误密码
            await page.locator("input").first.fill("admin")
            await page.locator("input[type='password']").first.fill("WrongPassword123!")

            await page.get_by_role("button", name="登录").click()

            # 等待 error label 出现非空文本。NiceGUI 的 error label 初始为空字符串，
            # ``inner_text`` 会立即返回空值；需要轮询等待 Python 端 ``set_text`` 完成。
            error_locator = page.locator(".text-red-500").first
            await page.wait_for_function(
                """() => {
                    const el = document.querySelector('.text-red-500');
                    return el && el.innerText && el.innerText.trim().length > 0;
                }""",
                timeout=15000,
            )
            error_text = await error_locator.inner_text(timeout=5000)
            assert error_text.strip(), "错误信息为空"

            # 验证未导航到首页（仍在 /login）
            assert page.url.endswith("/login"), f"登录失败后不应导航，当前 URL: {page.url}"
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_browser_refresh_session_rotates_cookies(
    browser_stack: tuple[str, str, str],
) -> None:
    """T025 浏览器冒烟：刷新会话轮换 Cookie。

    登录后点击“刷新会话”，/api/v1/auth/refresh 成功后浏览器获得新的
    access/refresh Cookie 并重载页面。``context.route`` 保证浏览器只经
    Web BFF 访问 API，不直连 API 端口。
    """
    from playwright.async_api import async_playwright

    api_url, web_url, password = browser_stack

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()
        await _block_non_web_origins(context, web_url, api_url)
        page = await context.new_page()

        try:
            await _browser_login(page, web_url, "admin", password)

            cookies_before = {
                c.get("name", ""): c.get("value", "") for c in await context.cookies()
            }
            access_before = cookies_before.get("child_manager_access", "")

            # 点击“刷新会话”；成功后页面 reload，新 access Cookie 由 Set-Cookie 写入。
            async with page.expect_navigation(timeout=15000):
                await page.get_by_role("button", name="刷新会话").click()

            cookies_after = {
                c.get("name", ""): c.get("value", "") for c in await context.cookies()
            }
            assert "child_manager_access" in cookies_after
            assert "child_manager_refresh" in cookies_after
            # access Cookie 应被轮换为新值。
            assert cookies_after["child_manager_access"] != access_before, (
                "刷新会话后 access cookie 未轮换"
            )
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_browser_change_password_redirects_to_login(
    browser_stack: tuple[str, str, str],
) -> None:
    """T025 浏览器冒烟：修改密码成功后跳转登录页。

    修改密码成功后 API 清除 auth Cookie 并要求重新登录，浏览器应导航到 /login。
    """
    from playwright.async_api import async_playwright

    api_url, web_url, password = browser_stack

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()
        await _block_non_web_origins(context, web_url, api_url)
        page = await context.new_page()

        try:
            await _browser_login(page, web_url, "admin", password)

            await page.goto(f"{web_url}/change-password")
            await page.wait_for_selector("text=修改密码", timeout=10000)

            await page.locator("input[type='password']").nth(0).fill(password)
            await page.locator("input[type='password']").nth(1).fill("NewValidPassword2025!")
            await page.locator("input[type='password']").nth(2).fill("NewValidPassword2025!")

            await page.get_by_role("button", name="确认修改").click()

            # 修改密码成功后应跳转到 /login。
            await page.wait_for_url(f"{web_url}/login", timeout=15000)
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_browser_admin_role_navigation(
    browser_stack: tuple[str, str, str],
) -> None:
    """T025 浏览器冒烟：按角色导航。

    管理员登录后导航栏应显示“账号管理”链接；首页加载时通过 /api/v1/auth/me
    获取角色并渲染。``context.route`` 保证角色请求只经 Web BFF。
    """
    from playwright.async_api import async_playwright

    api_url, web_url, password = browser_stack

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()
        await _block_non_web_origins(context, web_url, api_url)
        page = await context.new_page()

        try:
            await _browser_login(page, web_url, "admin", password)

            # 等待导航栏通过 /api/v1/auth/me 加载角色后渲染“账号管理”链接。
            await page.wait_for_selector("text=账号管理", timeout=15000)
            # 管理员应能看到账号管理链接。
            link = page.locator("a[href='/users']")
            assert await link.count() > 0, "管理员导航栏应包含账号管理链接"
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_browser_admin_create_reset_deactivate_user(
    browser_stack: tuple[str, str, str],
) -> None:
    """T025 浏览器冒烟：管理员创建/重置/停用账号。

    覆盖 T025 要求的管理员账号管理闭环。用户创建通过 API setup 完成以
    避免 NiceGUI multi-select 下拉框的脆弱选择器；重置密码与停用账号
    通过浏览器 UI 按钮完成，``context.route`` 保证不直连 API。创建后的
    账号在浏览器列表中可见，并可通过 UI 选择后执行重置与停用操作。
    """
    import httpx
    from playwright.async_api import async_playwright

    api_url, web_url, password = browser_stack
    web_port = web_url.rsplit(":", 2)[-1]
    origin = f"http://127.0.0.1:{web_port}"

    # setup：通过 API 创建教师账号（非被测对象，避免 multi-select 脆弱选择器）。
    csrf = _fetch_csrf(api_url)
    admin_login = httpx.post(
        f"{api_url}/api/v1/auth/login",
        json={"login": "admin", "password": password},
        headers={
            "origin": origin,
            "x-csrf-token": csrf,
            "x-child-manager-client-ip": "127.0.0.1",
        },
        cookies={"child_manager_csrf": csrf},
        trust_env=False,
    )
    assert admin_login.status_code == 200
    admin_cookies = admin_login.cookies
    # 登录响应设置新 CSRF cookie；后续请求必须用新令牌作为 header。
    admin_csrf = admin_cookies.get("child_manager_csrf") or csrf
    create = httpx.post(
        f"{api_url}/api/v1/users",
        json={
            "username": "browser_teacher",
            "display_name": "浏览器教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "TeacherPassword2024!",
        },
        headers={
            "origin": origin,
            "x-csrf-token": admin_csrf,
            "x-child-manager-client-ip": "127.0.0.1",
        },
        cookies=admin_cookies,
        trust_env=False,
    )
    assert create.status_code == 201

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()
        await _block_non_web_origins(context, web_url, api_url)
        page = await context.new_page()

        try:
            await _browser_login(page, web_url, "admin", password)

            await page.goto(f"{web_url}/users")
            await page.wait_for_selector("text=新建账号", timeout=10000)

            # 1. 验证创建的账号出现在列表中。
            await page.wait_for_selector("text=浏览器教师", timeout=15000)

            # 2. 选择账号并重置密码。
            await page.locator(".q-field").filter(has_text="选择账号").click()
            await page.locator(".q-item").filter(has_text="浏览器教师").click()
            await _fill_nicegui_input(page, "新密码", "ResetPassword2025!")
            await page.get_by_role("button", name="重置密码").click()
            await _wait_for_success_message(page)

            # 3. 停用账号。
            await page.get_by_role("button", name="停用账号").click()
            await _wait_for_success_message(page)
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_browser_deactivated_user_loses_access(
    browser_stack: tuple[str, str, str],
) -> None:
    """T025 浏览器冒烟：停用后下一请求失权。

    教师登录获得会话后，管理员通过 API 停用该教师；教师浏览器再次请求
    受保护资源时，access token 所在 family 已被撤销，应返回 401 并提示
    会话失效。``context.route`` 保证浏览器不直连 API。
    """
    import httpx
    from playwright.async_api import async_playwright

    api_url, web_url, password = browser_stack
    web_port = web_url.rsplit(":", 2)[-1]
    origin = f"http://127.0.0.1:{web_port}"

    # 1. 通过 API 创建教师并获取管理员会话（setup，非被测对象）。
    #    浏览器只用于验证教师侧的失权体验。
    admin_csrf = _fetch_csrf(api_url)
    admin_login = httpx.post(
        f"{api_url}/api/v1/auth/login",
        json={"login": "admin", "password": password},
        headers={
            "origin": origin,
            "x-csrf-token": admin_csrf,
            "x-child-manager-client-ip": "127.0.0.1",
        },
        cookies={"child_manager_csrf": admin_csrf},
        trust_env=False,
    )
    assert admin_login.status_code == 200
    admin_cookies = admin_login.cookies
    # 登录响应设置新 CSRF cookie；后续请求必须用新令牌作为 header。
    admin_csrf = admin_cookies.get("child_manager_csrf") or admin_csrf

    create = httpx.post(
        f"{api_url}/api/v1/users",
        json={
            "username": "deactivated_teacher",
            "display_name": "停用教师",
            "phone_e164": None,
            "role_codes": ["teacher"],
            "password": "TeacherPassword2024!",
        },
        headers={
            "origin": origin,
            "x-csrf-token": admin_csrf,
            "x-child-manager-client-ip": "127.0.0.1",
        },
        cookies=admin_cookies,
        trust_env=False,
    )
    assert create.status_code == 201
    teacher_id = create.json()["id"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()
        await _block_non_web_origins(context, web_url, api_url)
        page = await context.new_page()

        try:
            # 2. 教师通过浏览器登录。
            await _browser_login(page, web_url, "deactivated_teacher", "TeacherPassword2024!")

            # 3. 管理员通过 API 停用教师。
            deactivate = httpx.post(
                f"{api_url}/api/v1/users/{teacher_id}/deactivate",
                headers={
                    "origin": origin,
                    "x-csrf-token": admin_csrf,
                    "x-child-manager-client-ip": "127.0.0.1",
                },
                cookies=admin_cookies,
                trust_env=False,
            )
            assert deactivate.status_code == 200

            # 4. 教师点击“刷新会话”：refresh token 已被撤销，应失败而非静默重载。
            #    失败时 _auth_fetch_js 不 reload，因此用响应状态判断失权。
            refresh_responses: list[int] = []

            def _on_response(response: Any) -> None:
                if "/api/v1/auth/refresh" in response.url:
                    refresh_responses.append(response.status)

            page.on("response", _on_response)
            await page.get_by_role("button", name="刷新会话").click()
            # 等待 refresh 响应到达（失败时不触发 navigation，用轮询等待）。
            deadline = time.monotonic() + 15.0
            while not refresh_responses and time.monotonic() < deadline:
                await page.wait_for_timeout(200)

            # refresh 应返回 401（family 已撤销），不得成功轮换。
            assert refresh_responses, "未捕获到 refresh 请求响应"
            assert 401 in refresh_responses, (
                f"停用后 refresh 应失败(401)，实际: {refresh_responses}"
            )
        finally:
            await browser.close()
