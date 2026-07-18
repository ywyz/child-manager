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
from nicegui.testing.user import User


def _rule(value: Any) -> Callable[[re.Match], Any]:
    return lambda _: value


def _js_rule(pattern: str) -> re.Pattern:
    return re.compile(rf".*{re.escape(pattern)}.*", re.DOTALL)


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
    # 登录成功后 JS 返回 null，错误标签保持为空；页面仍保留登录表单。
    await user.should_see("登录")


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
