"""顶部导航组件：按角色渲染链接。"""

import json

from nicegui import ui


def _csrf_js() -> str:
    return """
    (document.cookie.split('; ').find(r => r.startsWith('child_manager_csrf=')) || '')
      .split('=')[1] || ''
    """.strip()


def _js_get(path: str) -> str:
    return f"""
    async function call() {{
        const csrf = {_csrf_js()};
        const resp = await fetch({json.dumps(path)}, {{
            method: 'GET',
            headers: {{
                'X-CSRF-Token': csrf,
                'Origin': window.location.origin,
            }},
        }});
        if (resp.ok) return JSON.stringify(await resp.json());
        return JSON.stringify({{}});
    }}
    return await call();
    """


def _nav_html(roles: list[str]) -> str:
    """渲染导航链接；退出与刷新会话由独立 NiceGUI 按钮触发以支持页面级交互。"""
    admin_link = '<a href="/users" class="mr-4">账号管理</a>' if "admin" in roles else ""
    return (
        '<nav class="flex items-center">'
        '<a href="/" class="mr-4">首页</a>'
        '<a href="/change-password" class="mr-4">修改密码</a>'
        f"{admin_link}"
        "</nav>"
    )


def _auth_fetch_js(path: str, success_js: str) -> str:
    """构造 POST 认证 fetch；仅 resp.ok 时执行 success_js，否则弹中文错误。

    AGENTS.md 要求异常不得静默吞掉，用户获得中文可理解的错误信息。原来
    refresh/logout 不检查 resp.ok，失败仍 reload/跳转，造成“看似已退出但
    服务端 family 与 Cookie 仍有效”的不一致。这里仅在成功时执行副作用，
    失败保留当前页面并通过 alert 显示中文错误。
    """
    return f"""
    async function call() {{
      const csrf = {_csrf_js()};
      try {{
        const resp = await fetch({json.dumps(path)}, {{
          method: 'POST',
          headers: {{'X-CSRF-Token': csrf, 'Origin': window.location.origin}},
        }});
        if (resp.ok) {{
          {success_js}
          return 'ok';
        }}
        alert('操作失败，请稍后重试。');
        return 'error';
      }} catch (e) {{
        alert('网络错误，请检查连接后重试。');
        return 'error';
      }}
    }}
    return await call();
    """


_REFRESH_JS = _auth_fetch_js(
    "/api/v1/auth/refresh",
    "window.location.reload();",
)

_LOGOUT_JS = _auth_fetch_js(
    "/api/v1/auth/logout",
    "window.location.href = '/login';",
)


async def _handle_refresh() -> None:
    """刷新会话按钮 on_click：调用 /api/v1/auth/refresh 并重载页面。

    失败时不重载，由浏览器 alert 显示中文错误，避免静默吞掉失败。
    """
    await ui.run_javascript(_REFRESH_JS)


async def _handle_logout() -> None:
    """退出按钮 on_click：调用 /api/v1/auth/logout 并跳转到 /login。

    Cookie 清除由浏览器根据 logout 响应的 Set-Cookie: Max-Age=0 自动处理；
    仅当服务端确认退出成功后才跳转，避免“以为已退出但服务端仍有效”。
    """
    await ui.run_javascript(_LOGOUT_JS)


def render_navigation(*, current_user: object) -> None:
    """根据当前用户角色渲染导航。"""
    del current_user  # 导航通过 API 实时获取角色，不依赖传入对象
    with ui.header().classes("items-center justify-between"):
        ui.label("幼儿园教育管理系统").classes("text-xl font-bold")
        nav = ui.html(_nav_html([])).classes("ml-auto")
        ui.button("刷新会话", on_click=_handle_refresh).classes("ml-2")
        ui.button("退出", on_click=_handle_logout).classes("ml-2")

        async def load_roles() -> None:
            result = await ui.run_javascript(_js_get("/api/v1/auth/me"))
            user = json.loads(result) if result else {}
            nav.set_content(_nav_html(user.get("role_codes") or []))

        ui.timer(0.1, load_roles, once=True)
