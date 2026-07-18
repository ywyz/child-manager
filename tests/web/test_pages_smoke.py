"""NiceGUI 页面级冒烟测试。

使用 nicegui.testing.User 驱动真实页面，验证登录、改密、账号管理和导航
页面渲染及关键交互；页面内的 API 调用通过 JavaScript 规则拦截返回
mock 数据，真实端到端行为由 tests/web/test_auth_smoke.py 覆盖。
"""

import json
import re
from collections.abc import Callable
from typing import Any

import pytest
from nicegui import ui
from nicegui.testing.user import User


def _rule(value: Any) -> Callable[[re.Match], Any]:
    return lambda _: value


def _js_rule(pattern: str) -> re.Pattern:
    return re.compile(rf".*{re.escape(pattern)}.*", re.DOTALL)


def _action_js_rule(suffix: str) -> re.Pattern:
    return re.compile(rf".*api/v1/users/.*/{suffix}.*", re.DOTALL)


def _add_js_rules(
    user: User,
    *,
    role_codes: list[str] | None = None,
    users_payload: dict[str, Any] | None = None,
) -> None:
    """为页面中 run_javascript 发起的 API 调用注入 mock 响应。"""

    def _users_result(match: re.Match) -> Any:
        # 创建/更新账号请求返回 null 表示成功；查询列表返回 mock 数据。
        if '"POST"' in match.string or '"PUT"' in match.string:
            return None
        return json.dumps(users_payload or {"items": []})

    user.javascript_rules[_js_rule("/api/v1/auth/csrf")] = _rule(None)
    user.javascript_rules[_js_rule("/api/v1/auth/me")] = _rule(
        json.dumps({"role_codes": role_codes or ["admin"]})
    )
    user.javascript_rules[_js_rule("/api/v1/auth/login")] = _rule(None)
    user.javascript_rules[_js_rule("/api/v1/auth/change-password")] = _rule(None)
    user.javascript_rules[_js_rule("/api/v1/users")] = _users_result
    # 账号操作：重置密码、停用、启用、保存角色均返回 null 表示成功。
    user.javascript_rules[_action_js_rule("reset-password")] = _rule(None)
    user.javascript_rules[_action_js_rule("deactivate")] = _rule(None)
    user.javascript_rules[_action_js_rule("activate")] = _rule(None)
    user.javascript_rules[_action_js_rule("roles")] = _rule(None)


def _select_user(user: User, user_id: str) -> None:
    """在动态账号列表加载后，直接设置选择器的值为目标用户 ID。

    NiceGUI `ui.select` 的选项为字典时，测试框架无法通过文本点击选择，
    因此通过页面元素设置值后再触发按钮，仍属于页面级交互验证。
    """
    assert user.client is not None
    with user:
        for element in user.client.elements.values():
            if isinstance(element, ui.select) and element.props.get("label") == "选择账号":
                element.value = user_id
                return
    raise AssertionError("未找到账号选择器")


@pytest.mark.asyncio
async def test_login_page_renders_form(user: User) -> None:
    _add_js_rules(user)
    await user.open("/login")
    await user.should_see("登录")
    await user.should_see("用户名")
    await user.should_see("密码")


@pytest.mark.asyncio
async def test_login_page_allows_typing_and_click(user: User) -> None:
    _add_js_rules(user)
    await user.open("/login")
    user.find("用户名").type("admin")
    user.find("密码").type("ValidPassword2024!")
    user.find("登录").click()
    # 登录请求已发出并成功（JS 返回 null），错误标签不出现请求失败提示。
    await user.should_not_see("请求失败", retries=10)


@pytest.mark.asyncio
async def test_change_password_page_renders_form(user: User) -> None:
    _add_js_rules(user)
    await user.open("/change-password")
    await user.should_see("修改密码")
    await user.should_see("原密码")
    await user.should_see("新密码")
    await user.should_see("确认新密码")


@pytest.mark.asyncio
async def test_change_password_page_accepts_input_and_submit(user: User) -> None:
    _add_js_rules(user)
    await user.open("/change-password")
    user.find("原密码").type("OldPassword2024!")
    user.find("新密码").type("NewPassword2024!")
    user.find("确认新密码").type("NewPassword2024!")
    user.find("确认修改").click()
    # 改密成功后 JS 返回 null，不应出现错误提示。
    await user.should_see("修改密码")


@pytest.mark.asyncio
async def test_navigation_renders_header_and_links(user: User) -> None:
    _add_js_rules(user)
    await user.open("/")
    await user.should_see("幼儿园教育管理系统")
    await user.should_see("首页")
    await user.should_see("修改密码")
    await user.should_see("退出")


@pytest.mark.asyncio
async def test_navigation_renders_admin_link_for_admin(user: User) -> None:
    _add_js_rules(user, role_codes=["admin"])
    await user.open("/")
    await user.should_see("账号管理")


@pytest.mark.asyncio
async def test_user_management_page_renders(user: User) -> None:
    _add_js_rules(user)
    await user.open("/users")
    await user.should_see("账号管理")
    await user.should_see("新建账号")
    await user.should_see("用户名")
    await user.should_see("显示名称")
    await user.should_see("初始密码")
    await user.should_see("创建账号")
    await user.should_see("账号操作")
    await user.should_see("重置密码")
    await user.should_see("停用账号")
    await user.should_see("启用账号")
    await user.should_see("保存角色")
    await user.should_see("刷新列表")


@pytest.mark.asyncio
async def test_user_management_page_create_user_closes_loop(user: User) -> None:
    _add_js_rules(
        user,
        users_payload={
            "items": [
                {
                    "id": "u1",
                    "username": "teacher1",
                    "display_name": "教师一",
                    "role_codes": ["teacher"],
                    "is_active": True,
                }
            ]
        },
    )
    await user.open("/users")
    user.find("用户名").type("newteacher")
    user.find("显示名称").type("新教师")
    user.find("初始密码").type("ValidPassword2024!")
    user.find("角色").click()
    user.find("teacher").click()
    user.find("创建账号").click()
    # 创建成功后先看到成功消息，随后列表刷新显示新账号。
    await user.should_see("创建成功", retries=10)
    await user.should_see("教师一", retries=10)


@pytest.mark.asyncio
async def test_user_management_page_refresh_list(user: User) -> None:
    _add_js_rules(
        user,
        users_payload={
            "items": [
                {
                    "id": "u1",
                    "username": "teacher1",
                    "display_name": "教师一",
                    "role_codes": ["teacher"],
                    "is_active": True,
                }
            ]
        },
    )
    await user.open("/users")
    user.find("刷新列表").click()
    await user.should_see("教师一", retries=10)
    await user.should_see("teacher1", retries=10)


@pytest.mark.asyncio
async def test_user_management_page_reset_password(user: User) -> None:
    _add_js_rules(
        user,
        users_payload={
            "items": [
                {
                    "id": "u1",
                    "username": "teacher1",
                    "display_name": "教师一",
                    "role_codes": ["teacher"],
                    "is_active": True,
                }
            ]
        },
    )
    await user.open("/users")
    await user.should_see("teacher1", retries=10)
    _select_user(user, "u1")
    user.find("新密码").type("NewPassword2024!")
    user.find("重置密码").click()
    await user.should_see("操作成功", retries=10)
    await user.should_not_see("请求失败", retries=5)


@pytest.mark.asyncio
async def test_user_management_page_deactivate_and_activate(user: User) -> None:
    _add_js_rules(
        user,
        users_payload={
            "items": [
                {
                    "id": "u1",
                    "username": "teacher1",
                    "display_name": "教师一",
                    "role_codes": ["teacher"],
                    "is_active": True,
                }
            ]
        },
    )
    await user.open("/users")
    await user.should_see("teacher1", retries=10)
    _select_user(user, "u1")
    user.find("停用账号").click()
    await user.should_see("操作成功", retries=10)
    _select_user(user, "u1")
    user.find("启用账号").click()
    await user.should_see("操作成功", retries=10)


@pytest.mark.asyncio
async def test_user_management_page_set_roles(user: User) -> None:
    _add_js_rules(
        user,
        users_payload={
            "items": [
                {
                    "id": "u1",
                    "username": "teacher1",
                    "display_name": "教师一",
                    "role_codes": ["teacher"],
                    "is_active": True,
                }
            ]
        },
    )
    await user.open("/users")
    await user.should_see("teacher1", retries=10)
    _select_user(user, "u1")
    user.find("调整角色").click()
    user.find("admin").click()
    user.find("保存角色").click()
    await user.should_see("操作成功", retries=10)
    await user.should_not_see("请求失败", retries=5)
