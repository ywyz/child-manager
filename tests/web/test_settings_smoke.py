import asyncio
import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import httpx
import psycopg
import pytest
from alembic import command
from alembic.config import Config
from playwright.sync_api import sync_playwright

from apps.web.components.navigation import navigation_for_capabilities
from apps.web.pages import class_areas as class_areas_page
from apps.web.pages.class_areas import class_areas_page_text
from apps.web.pages.settings import settings_page_text
from packages.backend.identity.tokens import create_access_token, hash_refresh_token

SIGNING_KEY = "m3-browser-jwt-signing-key-that-is-long"


@dataclass(frozen=True)
class BrowserActor:
    user_id: UUID
    access_token: str


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_http(url: str, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout is not None else ""
            raise AssertionError(f"服务启动失败: {url}\n{output}")
        try:
            with httpx.Client(trust_env=False, timeout=1) as client:
                if client.get(url).status_code == 200:
                    return
        except httpx.HTTPError:
            time.sleep(0.1)
    raise AssertionError(f"服务未就绪: {url}")


@contextmanager
def _m3_services(database_url: str) -> Iterator[str]:
    api_port = _free_port()
    web_port = _free_port()
    environment = {
        **os.environ,
        "CHILD_MANAGER_DATABASE_URL": database_url,
        "CHILD_MANAGER_AUTH_THROTTLE_BACKEND": "memory",
        "CHILD_MANAGER_JWT_SIGNING_KEY": SIGNING_KEY,
        "CHILD_MANAGER_CSRF_SIGNING_KEY": "m3-browser-csrf-signing-key-that-is-long",
        "CHILD_MANAGER_COOKIE_SECURE": "false",
        "CHILD_MANAGER_ENV": "development",
        "CHILD_MANAGER_WEB_PORT": str(web_port),
        "CHILD_MANAGER_ALLOWED_ORIGINS": f"http://localhost:{web_port}",
        "CHILD_MANAGER_TRUSTED_BFF_PEERS": "127.0.0.1",
        "CHILD_MANAGER_WEBAUTHN_RP_ID": "localhost",
        "CHILD_MANAGER_WEBAUTHN_RP_NAME": "Child Manager M3 Tests",
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
        yield f"http://localhost:{web_port}"
    finally:
        for process in (web, api):
            process.terminate()
        for process in (web, api):
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def _seed_browser_actors(database_url: str) -> tuple[BrowserActor, BrowserActor]:
    native_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    kindergarten_id = uuid4()
    admin_id = uuid4()
    teacher_id = uuid4()
    now = datetime.now(UTC)
    actors: list[BrowserActor] = []
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s, %s)",
            (kindergarten_id, "浏览器设置测试园"),
        )
        role_ids = {
            str(code): role_id
            for role_id, code in connection.execute(
                "SELECT id, code FROM roles WHERE code IN ('admin','teacher')"
            ).fetchall()
        }
        for index, (user_id, username, display_name, role_code) in enumerate(
            [
                (admin_id, "m3-admin", "M3 管理员", "admin"),
                (teacher_id, "m3-teacher", "M3 教师", "teacher"),
            ]
        ):
            family_id = uuid4()
            connection.execute(
                """INSERT INTO users
                (id, kindergarten_id, username, username_normalized, display_name,
                 webauthn_user_handle, status, activated_at)
                VALUES (%s,%s,%s,%s,%s,%s,'active',%s)""",
                (
                    user_id,
                    kindergarten_id,
                    username,
                    username,
                    display_name,
                    bytes([index + 1]) * 32,
                    now,
                ),
            )
            connection.execute(
                """INSERT INTO user_roles
                (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
                VALUES (%s,%s,%s,%s,%s)""",
                (kindergarten_id, user_id, role_ids[role_code], admin_id, now),
            )
            connection.execute(
                """INSERT INTO refresh_tokens
                (id, kindergarten_id, user_id, token_family_id, token_hash,
                 issued_at, expires_at, last_reauthenticated_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    uuid4(),
                    kindergarten_id,
                    user_id,
                    family_id,
                    hash_refresh_token(f"m3-browser-refresh-{index}"),
                    now,
                    now + timedelta(days=7),
                    now,
                ),
            )
            actors.append(
                BrowserActor(
                    user_id=user_id,
                    access_token=create_access_token(
                        user_id=str(user_id),
                        kindergarten_id=str(kindergarten_id),
                        token_family_id=str(family_id),
                        signing_key=SIGNING_KEY,
                        now=now,
                    ),
                )
            )
    return actors[0], actors[1]


def test_settings_pages_expose_the_complete_m3_admin_and_teacher_flows() -> None:
    settings_text = set(settings_page_text())
    areas_text = set(class_areas_page_text())

    assert {
        "系统设置",
        "幼儿园信息",
        "学期管理",
        "用户与班级",
        "保存园所名称",
        "创建学期",
        "设为当前学期",
        "创建班级",
        "保存教师关系",
        "主班教师",
        "区域尚未配置",
    } <= settings_text
    assert {
        "班级区域",
        "室内区域",
        "户外区域",
        "添加区域",
        "整体保存",
        "允许暂时留空",
        "没有维护该班区域的权限",
    } <= areas_text


def test_navigation_separates_admin_settings_from_teacher_class_areas() -> None:
    admin = navigation_for_capabilities(["settings:manage", "users:manage"])
    associated_teacher = navigation_for_capabilities(["class_areas:manage"])
    unrelated_teacher = navigation_for_capabilities([])

    assert "系统设置" in admin
    assert "系统设置" not in associated_teacher
    assert "班级区域" in associated_teacher
    assert "班级区域" not in unrelated_teacher


def test_class_area_page_loads_all_pages_before_editing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    async def fake_request(path: str, **_kwargs: object) -> dict[str, object]:
        calls.append(path)
        page = 1 if "page=1&" in path else 2
        if page == 1:
            items = [
                {
                    "id": str(uuid4()),
                    "name": f"历史区域 {index}",
                    "is_active": False,
                }
                for index in range(100)
            ]
        else:
            items = [{"id": str(uuid4()), "name": "仍在使用", "is_active": True}]
        return {
            "ok": True,
            "status": 200,
            "body": {"items": items, "page": page, "page_size": 100, "total": 101},
        }

    monkeypatch.setattr(class_areas_page, "same_origin_api_request", fake_request)

    items, error_status = asyncio.run(class_areas_page.load_all_class_areas("class-id", "indoor"))

    assert error_status is None
    assert len(items) == 101
    assert [item["name"] for item in items if item["is_active"]] == ["仍在使用"]
    assert len(calls) == 2


def test_settings_pages_use_only_same_origin_api_paths() -> None:
    source = (
        __import__("inspect").getsource(__import__("apps.web.pages.settings", fromlist=["*"]))
        + __import__("inspect").getsource(__import__("apps.web.pages.class_areas", fromlist=["*"]))
    ).lower()

    assert "/api/v1/settings/" in source
    assert "sqlalchemy" not in source
    assert "packages.backend" not in source
    assert "repository" not in source


def test_browser_completes_settings_empty_areas_and_immediate_unlink_flow(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    admin, teacher = _seed_browser_actors(isolated_database_url)

    with _m3_services(isolated_database_url) as base_url, sync_playwright() as manager:
        browser = manager.chromium.launch(headless=True)
        admin_context = browser.new_context()
        admin_context.add_cookies(
            [{"name": "child_manager_access", "value": admin.access_token, "url": base_url}]
        )
        admin_page = admin_context.new_page()
        admin_page.set_default_timeout(5_000)
        admin_page.goto(f"{base_url}/settings")
        admin_page.get_by_text("系统设置", exact=True).wait_for()

        admin_page.get_by_label("幼儿园名称").fill("更新后的浏览器测试园")
        admin_page.get_by_role("button", name="保存园所名称").click()
        admin_page.get_by_text("园所信息已保存").wait_for()

        admin_page.get_by_label("学期名称").fill("2026 春季学期")
        admin_page.get_by_label("开始日期").fill("2026-02-01")
        admin_page.get_by_label("结束日期").fill("2026-06-30")
        admin_page.get_by_role("button", name="创建学期").click()
        admin_page.get_by_role("button", name="设为当前学期").click()
        admin_page.get_by_text("当前学期已更新").wait_for()

        admin_page.get_by_label("班级名称").fill("浏览器空区域班")
        admin_page.get_by_label("年龄段").select_option("small")
        admin_page.get_by_label("任课教师 ID").fill(str(teacher.user_id))
        admin_page.get_by_label("主班教师").check()
        admin_page.get_by_role("button", name="创建班级").click()
        admin_page.get_by_text("班级已创建，区域尚未配置").wait_for()
        class_id = admin_page.get_by_test_id("created-class-id").text_content()
        assert class_id

        teacher_context = browser.new_context()
        teacher_context.add_cookies(
            [{"name": "child_manager_access", "value": teacher.access_token, "url": base_url}]
        )
        teacher_page = teacher_context.new_page()
        teacher_page.set_default_timeout(5_000)
        teacher_page.goto(f"{base_url}/class-areas")
        teacher_page.get_by_text("我的班级区域", exact=True).wait_for()
        teacher_page.get_by_role("link", name="浏览器空区域班").click()
        teacher_page.get_by_text("班级区域", exact=True).wait_for()
        teacher_page.get_by_label("室内区域").fill("阅读区\n建构区")
        teacher_page.get_by_role("button", name="整体保存室内区域").click()
        teacher_page.get_by_text("室内区域已保存").wait_for()
        teacher_page.get_by_role("button", name="整体保存户外区域").click()
        teacher_page.get_by_text("户外区域已保存").wait_for()

        admin_page.get_by_test_id(f"unlink-teachers-{class_id}").click()
        admin_page.get_by_text("教师关系已清空").wait_for()
        teacher_page.get_by_role("button", name="刷新区域").click()
        teacher_page.get_by_text("没有维护该班区域的权限").wait_for()

        assert all(
            "://127.0.0.1:" not in request.url
            for request in [*admin_page.context.pages, *teacher_page.context.pages]
        )
        teacher_context.close()
        admin_context.close()
        browser.close()
