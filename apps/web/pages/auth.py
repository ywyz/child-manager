"""认证页面：登录与修改密码。"""

import json

from nicegui import ui


def _csrf_js() -> str:
    return """
    (document.cookie.split('; ').find(r => r.startsWith('child_manager_csrf=')) || '')
      .split('=')[1] || ''
    """.strip()


def _js_fetch(
    *,
    method: str,
    path: str,
    body: dict | None = None,
    redirect_on_ok: str | None = None,
) -> str:
    body_literal = "null" if body is None else json.dumps(body, ensure_ascii=False)
    redirect_literal = "null" if redirect_on_ok is None else json.dumps(redirect_on_ok)
    return f"""
    async function call() {{
        const csrf = {_csrf_js()};
        const resp = await fetch({json.dumps(path)}, {{
            method: {json.dumps(method)},
            headers: {{
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrf,
                'Origin': window.location.origin,
            }},
            body: {body_literal},
        }});
        if (resp.ok) {{
            const redirect = {redirect_literal};
            if (redirect) window.location.href = redirect;
            return null;
        }}
        const data = await resp.json().catch(() => ({{message: '请求失败'}}));
        return data.message || '请求失败';
    }}
    return await call();
    """


_JS_PREFETCH_CSRF = """
async function prefetchCsrf() {
    const resp = await fetch('/api/v1/auth/csrf', {
        method: 'GET',
        headers: {'Origin': window.location.origin},
    });
    if (!resp.ok) return 'CSRF 令牌获取失败';
    return null;
}
return await prefetchCsrf();
"""


async def login_page() -> None:
    """登录页面；加载时先预取 CSRF 令牌再启用登录按钮。"""
    with ui.card().classes("w-96 mx-auto"):
        ui.label("登录").classes("text-xl font-bold mb-4")
        login_input = ui.input("用户名").classes("mb-4 w-full")
        password = ui.input("密码", password=True).classes("mb-4 w-full")
        error = ui.label("").classes("text-red-500 mb-4")

        login_button = ui.button("登录", on_click=None).classes("w-full")
        login_button.set_enabled(False)

        async def handle_login() -> None:
            js = _js_fetch(
                method="POST",
                path="/api/v1/auth/login",
                body={"login": login_input.value, "password": password.value},
                redirect_on_ok="/",
            )
            result = await ui.run_javascript(js)
            if result:
                error.set_text(result)

        login_button.on_click(handle_login)

        prefetch_result = await ui.run_javascript(_JS_PREFETCH_CSRF)
        if prefetch_result:
            error.set_text(prefetch_result)
        else:
            login_button.set_enabled(True)


def change_password_page() -> None:
    """修改密码页面。"""
    with ui.card().classes("w-96 mx-auto"):
        ui.label("修改密码").classes("text-xl font-bold mb-4")
        old_password = ui.input("原密码", password=True).classes("mb-4 w-full")
        new_password = ui.input("新密码", password=True).classes("mb-4 w-full")
        confirm_password = ui.input("确认新密码", password=True).classes("mb-4 w-full")
        error = ui.label("").classes("text-red-500 mb-4")

        async def handle_change() -> None:
            if new_password.value != confirm_password.value:
                error.set_text("两次输入的新密码不一致")
                return
            js = _js_fetch(
                method="POST",
                path="/api/v1/auth/change-password",
                body={"current_password": old_password.value, "new_password": new_password.value},
                redirect_on_ok="/login",
            )
            result = await ui.run_javascript(js)
            if result:
                error.set_text(result)

        ui.button("确认修改", on_click=handle_change).classes("w-full")
