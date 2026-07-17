"""用户管理页面。"""

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
        const data = await resp.json().catch(() => ({{message: '请求失败'}}));
        return JSON.stringify({{error: data.message || '请求失败'}});
    }}
    return await call();
    """


def _js_fetch(
    *,
    method: str,
    path: str,
    body: dict | None = None,
) -> str:
    body_literal = "null" if body is None else json.dumps(body, ensure_ascii=False)
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
        if (resp.ok) return null;
        const data = await resp.json().catch(() => ({{message: '请求失败'}}));
        return data.message || '请求失败';
    }}
    return await call();
    """


def _render_user_table(users: list[dict]) -> str:
    rows = ""
    for user in users:
        roles = ", ".join(user.get("roles") or [])
        status = "启用" if user.get("is_active") else "停用"
        rows += (
            f"<tr><td>{user.get('username')}</td>"
            f"<td>{user.get('display_name')}</td>"
            f"<td>{roles}</td><td>{status}</td></tr>"
        )
    return (
        "<table class='w-full text-left border'>"
        "<tr><th>用户名</th><th>显示名称</th><th>角色</th><th>状态</th></tr>"
        f"{rows}</table>"
    )


def user_management_page() -> None:
    """账号管理页面。"""
    ui.label("账号管理").classes("text-xl font-bold mb-4")
    list_container = ui.html("").classes("w-full mb-4")
    message = ui.label("").classes("text-red-500 mb-4")

    async def load_users() -> None:
        result = await ui.run_javascript(_js_get("/api/v1/users"))
        if not result:
            list_container.set_content("<p>暂无账号</p>")
            return
        data = json.loads(result)
        if isinstance(data, dict) and "error" in data:
            message.set_text(data["error"])
            return
        if isinstance(data, list):
            list_container.set_content(_render_user_table(data))
        else:
            list_container.set_content("<p>加载失败</p>")

    with ui.card().classes("w-full mb-4"):
        ui.label("新建账号").classes("font-bold mb-2")
        username = ui.input("用户名").classes("mb-2 w-full")
        display_name = ui.input("显示名称").classes("mb-2 w-full")
        initial_password = ui.input("初始密码", password=True).classes("mb-2 w-full")
        roles = ui.select(["teacher", "admin"], multiple=True, label="角色").classes("mb-2 w-full")

        async def handle_create() -> None:
            selected = roles.value or []
            js = _js_fetch(
                method="POST",
                path="/api/v1/users",
                body={
                    "username": username.value,
                    "display_name": display_name.value,
                    "initial_password": initial_password.value,
                    "roles": selected if isinstance(selected, list) else [selected],
                },
            )
            result = await ui.run_javascript(js)
            if result:
                message.set_text(result)
            else:
                message.set_text("创建成功")
                message.classes("text-green-500")
                await load_users()

        ui.button("创建账号", on_click=handle_create)

    ui.button("刷新列表", on_click=load_users)
    ui.timer(0.1, load_users, once=True)
