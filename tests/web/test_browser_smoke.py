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
    """轮询等待服务器在回环地址上就绪。"""
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            response = httpx.get(url, timeout=1.0, follow_redirects=True)
            if response.status_code < 500:
                return
        except Exception as exc:
            last_error = exc
        time.sleep(0.2)
    raise RuntimeError(f"Server at {url} did not start within {timeout}s: {last_error}")


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
    """Playwright 真实浏览器测试：登录 → Cookie 设置 → 退出 → 导航闭环。

    T025 要求浏览器冒烟覆盖 Cookie 交换与导航闭环。本测试：
    1. 打开 /login，填写凭据并点击登录；
    2. 验证浏览器获得 access/refresh/csrf 三条 Cookie；
    3. 验证页面导航到首页（/）；
    4. 点击退出按钮；
    5. 验证页面导航到 /login。
    """
    from playwright.async_api import async_playwright

    _, web_url, password = browser_stack

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 1. 打开登录页
            await page.goto(f"{web_url}/login")
            await page.wait_for_selector("text=登录", timeout=10000)

            # 2. 填写凭据（NiceGUI ui.input 渲染为带 label 的 input）
            await page.locator("input").first.fill("admin")
            await page.locator("input[type='password']").first.fill(password)

            # 3. 点击登录（Playwright 自动等待按钮启用——CSRF 预取完成后启用）
            # 捕获网络请求便于诊断 CSRF 与登录 API 调用
            api_calls: list[dict[str, str]] = []

            def _on_request_finished(request: Any) -> None:
                if "/api/v1/" in request.url:
                    api_calls.append(
                        {
                            "url": request.url,
                            "method": request.method,
                            "post_data": request.post_data or "",
                        }
                    )

            page.on("requestfinished", _on_request_finished)
            await page.get_by_role("button", name="登录").click()

            # 4. 验证导航到首页；若失败，输出错误信息与页面状态便于诊断
            try:
                await page.wait_for_url(f"{web_url}/", timeout=15000)
            except Exception:
                error_text = await page.locator(".text-red-500").first.inner_text(timeout=2000)
                api_summary = "\n  ".join(
                    f"{c['method']} {c['url']} body={c['post_data'][:200]}" for c in api_calls
                )
                raise AssertionError(
                    f"登录后未导航到首页。URL: {page.url}, 错误: {error_text!r}\n"
                    f"API 调用:\n  {api_summary}"
                ) from None

            # 5. 验证 auth Cookie 已设置（浏览器真实 cookie jar）
            cookies = await context.cookies()
            cookie_names = {c.get("name", "") for c in cookies}
            assert "child_manager_access" in cookie_names, f"缺少 access cookie: {cookie_names}"
            assert "child_manager_refresh" in cookie_names, f"缺少 refresh cookie: {cookie_names}"
            assert "child_manager_csrf" in cookie_names, f"缺少 csrf cookie: {cookie_names}"

            # 6. 点击退出
            await page.get_by_role("button", name="退出").click()

            # 7. 验证导航到 /login
            await page.wait_for_url(f"{web_url}/login", timeout=15000)
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

    _, web_url, _ = browser_stack

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()

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
