"""NiceGUI 页面级冒烟测试。

使用 nicegui.testing.User 驱动真实页面，验证登录、改密、账号管理和导航
页面渲染及关键交互；通过拦截 run_javascript 精确记录并断言每个页面
请求的 method/path/body。
"""

import asyncio
import json
import re
from dataclasses import dataclass
from typing import Any

import pytest
from nicegui import ui
from nicegui.testing.user import User


@dataclass
class CapturedRequest:
    """页面 run_javascript 发起的一次 fetch 请求记录。"""

    method: str
    path: str
    body: dict[str, Any] | None = None
    raw_code: str = ""


class JsRequestRecorder:
    """拦截并解析页面 run_javascript 发起的 fetch 请求。

    通过 NiceGUI `User.javascript_rules` 的单一通配规则捕获所有 JS 执行，
    解析其中的 method/path/body，同时返回与请求匹配的 mock 响应。
    """

    def __init__(self) -> None:
        self.requests: list[CapturedRequest] = []
        self._responses: dict[str, Any] = {}

    def add_response(self, method: str, path: str, response: Any) -> None:
        """注册指定 method+path 的 mock 响应。"""
        self._responses[f"{method}:{path}"] = response

    def add_prefix_response(self, method: str, path_prefix: str, response: Any) -> None:
        """注册按路径前缀匹配的 mock 响应（最后注册优先）。"""
        self._responses[f"{method}:prefix:{path_prefix}"] = response

    @staticmethod
    def _extract_method(code: str) -> str:
        match = re.search(r"method:\s*['\"]([A-Z]+)['\"],?", code)
        return match.group(1) if match else "GET"

    @staticmethod
    def _extract_path(code: str) -> str:
        match = re.search(r"fetch\(['\"]([^'\"]+)['\"]", code)
        return match.group(1) if match else ""

    @staticmethod
    def _extract_body(code: str) -> dict[str, Any] | None:
        start = code.find("body:")
        if start == -1:
            return None
        start += len("body:")
        while start < len(code) and code[start].isspace():
            start += 1
        if code.startswith("null", start):
            return None
        if code[start] != "{":
            return None
        depth = 0
        end = start
        for i in range(start, len(code)):
            if code[i] == "{":
                depth += 1
            elif code[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        try:
            return json.loads(code[start:end])
        except json.JSONDecodeError:
            return None

    def _match_response(self, req: CapturedRequest) -> Any:
        """按精确 method:path 或前缀匹配返回 mock 响应。"""
        exact_key = f"{req.method}:{req.path}"
        if exact_key in self._responses:
            return self._responses[exact_key]
        for key, response in self._responses.items():
            if not key.startswith(f"{req.method}:prefix:"):
                continue
            prefix = key.split(":prefix:", 1)[1]
            if req.path.startswith(prefix):
                return response
        return None

    def __call__(self, match: re.Match) -> Any:
        code = match.string
        req = CapturedRequest(
            method=self._extract_method(code),
            path=self._extract_path(code),
            body=self._extract_body(code),
            raw_code=code,
        )
        self.requests.append(req)
        return self._match_response(req)

    def find(
        self,
        *,
        method: str | None = None,
        path: str | None = None,
        path_suffix: str | None = None,
    ) -> list[CapturedRequest]:
        results = self.requests
        if method is not None:
            results = [r for r in results if r.method == method]
        if path is not None:
            results = [r for r in results if r.path == path]
        if path_suffix is not None:
            results = [r for r in results if r.path.endswith(path_suffix)]
        return results

    def assert_request(
        self,
        *,
        method: str,
        path: str | None = None,
        path_suffix: str | None = None,
        body: dict[str, Any] | None = None,
    ) -> CapturedRequest:
        """断言存在指定请求，并可选校验请求体。"""
        reqs = self.find(method=method, path=path, path_suffix=path_suffix)
        assert reqs, f"未找到 {method} 请求（path={path}, suffix={path_suffix}）"
        req = reqs[0]
        if body is not None:
            assert req.body == body, f"请求体不匹配：期望 {body}，实际 {req.body}"
        return req


async def _wait_for_request(
    recorder: JsRequestRecorder,
    *,
    method: str,
    path: str | None = None,
    path_suffix: str | None = None,
    timeout: float = 1.0,
) -> CapturedRequest:
    """轮询等待指定请求被记录。"""
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        reqs = recorder.find(method=method, path=path, path_suffix=path_suffix)
        if reqs:
            return reqs[0]
        await asyncio.sleep(0.05)
    raise AssertionError(f"超时未找到 {method} 请求（path={path}, suffix={path_suffix}）")


async def _wait_for_request_count(
    recorder: JsRequestRecorder,
    *,
    method: str,
    path: str | None = None,
    path_suffix: str | None = None,
    min_count: int = 1,
    timeout: float = 1.0,
) -> list[CapturedRequest]:
    """轮询等待指定请求被记录至少 min_count 次。"""
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        reqs = recorder.find(method=method, path=path, path_suffix=path_suffix)
        if len(reqs) >= min_count:
            return reqs
        await asyncio.sleep(0.05)
    raise AssertionError(f"超时未找到足够 {method} 请求（path={path}, suffix={path_suffix}）")


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


def _set_multi_select(user: User, label: str, values: list[str]) -> None:
    """直接设置多选选择器的值。

    NiceGUI 多选下拉在测试环境中无法通过点击选项稳定选择，因此直接设置
    元素 value 属性，同时保留页面级交互意图。
    """
    assert user.client is not None
    with user:
        for element in user.client.elements.values():
            if isinstance(element, ui.select) and element.props.get("label") == label:
                element.value = values
                return
    raise AssertionError(f"未找到选择器: {label}")


def _set_input(user: User, label: str, value: str) -> None:
    """直接设置输入框的值。

    NiceGUI testing 的 `type()` 在多个输入框场景下对最后一个输入框存在副作用，
    会导致后续按钮点击无法触发预期的 run_javascript。直接设置 value 可绕过该问题，
    同时仍验证页面在输入值后的行为。
    """
    assert user.client is not None
    with user:
        for element in user.client.elements.values():
            if isinstance(element, ui.input) and element.props.get("label") == label:
                element.value = value
                return
    raise AssertionError(f"未找到输入框: {label}")


async def _click_button(user: User, label: str) -> None:
    """直接触发按钮的 on_click handler。

    NiceGUI testing.User 的 click 在异步 handler 场景下受内部事件循环限制，
    因此通过页面元素定位按钮后，使用与框架相同的 `handle_event` 路径调用
    handler，保留页面级交互验证。
    """
    from nicegui import events as nicegui_events

    assert user.client is not None
    with user:
        for element in user.client.elements.values():
            if isinstance(element, ui.button) and element.props.get("label") == label:
                for listener in element._event_listeners.values():
                    if listener.element_id == element.id and listener.type == "click":
                        event_args = nicegui_events.GenericEventArguments(
                            sender=element, client=user.client, args=None
                        )
                        nicegui_events.handle_event(listener.handler, event_args)
                        return
    raise AssertionError(f"未找到按钮: {label}")


def _user_payload(user_id: str = "u1", username: str = "teacher1") -> dict[str, Any]:
    return {
        "items": [
            {
                "id": user_id,
                "username": username,
                "display_name": "教师一",
                "role_codes": ["teacher"],
                "is_active": True,
            }
        ]
    }


def _wire_recorder(user: User, *, role_codes: list[str] | None = None) -> JsRequestRecorder:
    """将 recorder 注册到 User 并配置默认 mock 响应。"""
    recorder = JsRequestRecorder()
    recorder.add_response("GET", "/api/v1/auth/csrf", None)
    recorder.add_response(
        "GET", "/api/v1/auth/me", json.dumps({"role_codes": role_codes or ["admin"]})
    )
    recorder.add_response("POST", "/api/v1/auth/login", None)
    recorder.add_response("POST", "/api/v1/auth/change-password", None)
    recorder.add_response("POST", "/api/v1/auth/logout", None)
    recorder.add_response("POST", "/api/v1/auth/refresh", None)
    recorder.add_prefix_response("GET", "/api/v1/users", json.dumps({"items": []}))
    recorder.add_prefix_response("POST", "/api/v1/users", None)
    recorder.add_prefix_response("POST", "/api/v1/users/", None)
    recorder.add_prefix_response("PUT", "/api/v1/users/", None)
    user.javascript_rules[re.compile(r".*", re.DOTALL)] = recorder
    return recorder


@pytest.mark.asyncio
async def test_login_page_renders_form(user: User) -> None:
    recorder = _wire_recorder(user)
    await user.open("/login")
    await user.should_see("登录")
    await user.should_see("用户名")
    await user.should_see("密码")
    # 登录页加载时会预取 CSRF 令牌
    await _wait_for_request(recorder, method="GET", path="/api/v1/auth/csrf")


@pytest.mark.asyncio
async def test_login_page_sends_expected_request(user: User) -> None:
    recorder = _wire_recorder(user)
    await user.open("/login")
    # 等待 CSRF 预取完成、登录按钮启用后再点击
    await _wait_for_request(recorder, method="GET", path="/api/v1/auth/csrf")
    user.find("用户名").type("admin")
    user.find("密码").type("ValidPassword2024!")
    await _click_button(user, "登录")
    req = await _wait_for_request(recorder, method="POST", path="/api/v1/auth/login")
    assert req.body == {"login": "admin", "password": "ValidPassword2024!"}


@pytest.mark.asyncio
async def test_change_password_page_renders_form(user: User) -> None:
    _wire_recorder(user)
    await user.open("/change-password")
    await user.should_see("修改密码")
    await user.should_see("原密码")
    await user.should_see("新密码")
    await user.should_see("确认新密码")


@pytest.mark.asyncio
async def test_change_password_page_sends_expected_request(user: User) -> None:
    recorder = _wire_recorder(user)
    await user.open("/change-password")
    # 等待导航组件的 auth/me 请求完成，避免异步事件冲突
    await _wait_for_request(recorder, method="GET", path="/api/v1/auth/me")
    _set_input(user, "原密码", "OldPassword2024!")
    _set_input(user, "新密码", "NewPassword2024!")
    _set_input(user, "确认新密码", "NewPassword2024!")
    user.find("确认修改").click()
    req = await _wait_for_request(recorder, method="POST", path="/api/v1/auth/change-password")
    assert req.body == {
        "current_password": "OldPassword2024!",
        "new_password": "NewPassword2024!",
    }


@pytest.mark.asyncio
async def test_navigation_renders_header_and_links(user: User) -> None:
    recorder = _wire_recorder(user)
    await user.open("/")
    await user.should_see("幼儿园教育管理系统")
    await user.should_see("首页")
    await user.should_see("修改密码")
    await user.should_see("退出")
    await _wait_for_request(recorder, method="GET", path="/api/v1/auth/me")


@pytest.mark.asyncio
async def test_navigation_renders_admin_link_for_admin(user: User) -> None:
    recorder = _wire_recorder(user, role_codes=["admin"])
    await user.open("/")
    await user.should_see("账号管理")
    await _wait_for_request(recorder, method="GET", path="/api/v1/auth/me")


@pytest.mark.asyncio
async def test_navigation_hides_admin_link_for_teacher(user: User) -> None:
    recorder = _wire_recorder(user, role_codes=["teacher"])
    await user.open("/")
    await user.should_not_see("账号管理")
    await _wait_for_request(recorder, method="GET", path="/api/v1/auth/me")


@pytest.mark.asyncio
async def test_login_success_redirects_to_home(user: User) -> None:
    """登录成功后页面 JS 必须把 window.location.href 跳转到首页 "/"。"""
    recorder = _wire_recorder(user)
    await user.open("/login")
    await _wait_for_request(recorder, method="GET", path="/api/v1/auth/csrf")
    user.find("用户名").type("admin")
    user.find("密码").type("ValidPassword2024!")
    await _click_button(user, "登录")
    req = await _wait_for_request(recorder, method="POST", path="/api/v1/auth/login")
    # 登录请求的 JS 源码必须包含跳转到首页的指令。
    assert "window.location.href" in req.raw_code
    assert '"/"' in req.raw_code


@pytest.mark.asyncio
async def test_change_password_success_redirects_to_login(user: User) -> None:
    """改密成功后页面 JS 必须把 window.location.href 跳转到登录页 "/login"。"""
    recorder = _wire_recorder(user)
    await user.open("/change-password")
    await _wait_for_request(recorder, method="GET", path="/api/v1/auth/me")
    _set_input(user, "原密码", "OldPassword2024!")
    _set_input(user, "新密码", "NewPassword2024!")
    _set_input(user, "确认新密码", "NewPassword2024!")
    user.find("确认修改").click()
    req = await _wait_for_request(recorder, method="POST", path="/api/v1/auth/change-password")
    assert "window.location.href" in req.raw_code
    assert '"/login"' in req.raw_code


@pytest.mark.asyncio
async def test_logout_button_invokes_logout_endpoint(user: User) -> None:
    """NiceGUI User 驱动的退出：导航渲染退出入口并绑定 logout 处理函数。

    退出入口通过内联 onclick="logout(event)" 绑定，logout 函数由
    ui.add_body_html 注入；这里断言导航渲染退出入口且绑定 logout 处理函数。
    logout 端点与跳转目标已由 API 层与页面 JS 源码覆盖。
    """
    _wire_recorder(user)
    await user.open("/")
    await user.should_see("退出")
    # 导航 HTML 必须包含退出入口并绑定 logout 处理函数。
    assert user.client is not None
    from nicegui import ui

    nav_html = ""
    with user:
        for element in user.client.elements.values():
            if isinstance(element, ui.html):
                content = str(getattr(element, "content", ""))
                if "退出" in content:
                    nav_html = content
                    break
    assert 'onclick="logout(event)"' in nav_html


@pytest.mark.asyncio
async def test_user_management_page_renders(user: User) -> None:
    recorder = _wire_recorder(user)
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
    await _wait_for_request(recorder, method="GET", path="/api/v1/users")


@pytest.mark.asyncio
async def test_user_management_page_create_user_closes_loop(user: User) -> None:
    recorder = _wire_recorder(user)
    recorder.add_prefix_response("GET", "/api/v1/users", json.dumps(_user_payload()))
    await user.open("/users")
    user.find("用户名").type("newteacher")
    user.find("显示名称").type("新教师")
    user.find("初始密码").type("ValidPassword2024!")
    _set_multi_select(user, "角色", ["teacher"])
    await _click_button(user, "创建账号")
    await user.should_see("创建成功", retries=10)
    await user.should_see("教师一", retries=10)

    req = await _wait_for_request(recorder, method="POST", path="/api/v1/users")
    assert req.body == {
        "username": "newteacher",
        "display_name": "新教师",
        "password": "ValidPassword2024!",
        "role_codes": ["teacher"],
    }
    # 创建成功后刷新列表
    get_requests = await _wait_for_request_count(
        recorder, method="GET", path="/api/v1/users", min_count=2
    )
    assert len(get_requests) >= 2


@pytest.mark.asyncio
async def test_user_management_page_refresh_list(user: User) -> None:
    recorder = _wire_recorder(user)
    recorder.add_prefix_response("GET", "/api/v1/users", json.dumps(_user_payload()))
    await user.open("/users")
    await _click_button(user, "刷新列表")
    await user.should_see("教师一", retries=10)
    await user.should_see("teacher1", retries=10)
    await _wait_for_request(recorder, method="GET", path="/api/v1/users")


@pytest.mark.asyncio
async def test_user_management_page_reset_password(user: User) -> None:
    recorder = _wire_recorder(user)
    recorder.add_prefix_response("GET", "/api/v1/users", json.dumps(_user_payload()))
    await user.open("/users")
    await user.should_see("teacher1", retries=10)
    _select_user(user, "u1")
    user.find("新密码").type("NewPassword2024!")
    await _click_button(user, "重置密码")
    await user.should_see("操作成功", retries=10)
    req = await _wait_for_request(recorder, method="POST", path_suffix="/reset-password")
    assert req.body == {"new_password": "NewPassword2024!"}


@pytest.mark.asyncio
async def test_user_management_page_deactivate_and_activate(user: User) -> None:
    recorder = _wire_recorder(user)
    recorder.add_prefix_response("GET", "/api/v1/users", json.dumps(_user_payload()))
    await user.open("/users")
    await user.should_see("teacher1", retries=10)
    _select_user(user, "u1")
    await _click_button(user, "停用账号")
    await user.should_see("操作成功", retries=10)
    await _wait_for_request(recorder, method="POST", path_suffix="/deactivate")

    _select_user(user, "u1")
    await _click_button(user, "启用账号")
    await user.should_see("操作成功", retries=10)
    await _wait_for_request(recorder, method="POST", path_suffix="/activate")


@pytest.mark.asyncio
async def test_user_management_page_set_roles(user: User) -> None:
    recorder = _wire_recorder(user)
    recorder.add_prefix_response("GET", "/api/v1/users", json.dumps(_user_payload()))
    await user.open("/users")
    await user.should_see("teacher1", retries=10)
    _select_user(user, "u1")
    _set_multi_select(user, "调整角色", ["teacher", "admin"])
    await _click_button(user, "保存角色")
    await user.should_see("操作成功", retries=10)
    req = await _wait_for_request(recorder, method="PUT", path_suffix="/roles")
    assert req.body == {"role_codes": ["teacher", "admin"]}
