"""NiceGUI 页面级冒烟测试。

使用 nicegui.testing.User 驱动真实页面，验证登录、改密、账号管理和导航
页面渲染及关键元素存在；页面内的 API 调用通过 JavaScript 规则拦截返回
mock 数据，真实端到端行为由 tests/web/test_auth_smoke.py 覆盖。
"""

import json
import re
from collections.abc import Callable
from typing import Any

import pytest
from nicegui.testing.user import User


def _add_js_rules(user: User, *, role_codes: list[str] | None = None) -> None:
    """为页面中 run_javascript 发起的 API 调用注入 mock 响应。"""

    def _result(value: Any) -> Callable[[re.Match], Any]:
        return lambda _: value

    user.javascript_rules[re.compile(r"/api/v1/auth/csrf")] = _result(None)
    user.javascript_rules[re.compile(r"/api/v1/auth/me")] = _result(
        json.dumps({"role_codes": role_codes or ["admin"]})
    )
    user.javascript_rules[re.compile(r"/api/v1/users")] = _result(
        json.dumps(
            {
                "items": [
                    {
                        "id": "u1",
                        "username": "teacher1",
                        "display_name": "教师一",
                        "role_codes": ["teacher"],
                        "is_active": True,
                    }
                ]
            }
        )
    )


@pytest.mark.asyncio
async def test_login_page_renders_form(user: User) -> None:
    _add_js_rules(user)
    await user.open("/login")
    await user.should_see("登录")
    await user.should_see("用户名")
    await user.should_see("密码")


@pytest.mark.asyncio
async def test_change_password_page_renders_form(user: User) -> None:
    _add_js_rules(user)
    await user.open("/change-password")
    await user.should_see("修改密码")
    await user.should_see("原密码")
    await user.should_see("新密码")
    await user.should_see("确认新密码")


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
