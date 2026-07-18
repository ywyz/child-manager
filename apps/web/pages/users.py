"""用户管理页面。"""

import json
from collections.abc import Awaitable, Callable

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
        roles = ", ".join(user.get("role_codes") or [])
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


async def _load_users(
    list_container: ui.html,
    user_selector: ui.select,
    show_error: Callable[[str], None],
) -> None:
    result = await ui.run_javascript(_js_get("/api/v1/users"))
    if not result:
        list_container.set_content("<p>暂无账号</p>")
        user_selector.set_options([])
        return
    data = json.loads(result)
    if isinstance(data, dict) and "error" in data:
        show_error(data["error"])
        return
    if isinstance(data, dict) and "items" in data:
        list_container.set_content(_render_user_table(data["items"]))
        options = {
            u.get("id"): f"{u.get('username')} ({u.get('display_name')})" for u in data["items"]
        }
        user_selector.set_options(options)
    else:
        list_container.set_content("<p>加载失败</p>")


async def _do_action(
    user_selector: ui.select,
    path: str,
    body: dict | None,
    method: str,
    show_success: Callable[[str], None],
    show_error: Callable[[str], None],
    load_users: Callable[[], Awaitable[None]],
) -> bool:
    user_id = user_selector.value
    if not user_id:
        show_error("请先选择账号")
        return False
    result = await ui.run_javascript(
        _js_fetch(method=method, path=f"/api/v1/users/{user_id}{path}", body=body)
    )
    if result:
        show_error(result)
        return False
    show_success("操作成功")
    await load_users()
    return True


def _render_create_form(
    *,
    on_success: Callable[[str], Awaitable[None]],
    show_error: Callable[[str], None],
) -> None:
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
                "password": initial_password.value,
                "role_codes": selected if isinstance(selected, list) else [selected],
            },
        )
        result = await ui.run_javascript(js)
        if result:
            show_error(result)
        else:
            await on_success("创建成功")

    ui.button("创建账号", on_click=handle_create)


def _render_action_panel(
    *,
    do_action: Callable[..., Awaitable[bool]],
    load_users: Callable[[], Awaitable[None]],
    show_success: Callable[[str], None],
    show_error: Callable[[str], None],
) -> None:
    reset_password = ui.input("新密码", password=True).classes("mb-2 w-full")

    async def handle_reset_password() -> None:
        await do_action("/reset-password", {"new_password": reset_password.value})

    async def handle_deactivate() -> None:
        await do_action("/deactivate")

    async def handle_activate() -> None:
        await do_action("/activate")

    with ui.row():
        ui.button("重置密码", on_click=handle_reset_password)
        ui.button("停用账号", on_click=handle_deactivate)
        ui.button("启用账号", on_click=handle_activate)

    ui.separator().classes("my-2")
    set_roles = ui.select(["teacher", "admin"], multiple=True, label="调整角色").classes(
        "mb-2 w-full"
    )

    async def handle_set_roles() -> None:
        selected = set_roles.value or []
        role_codes = selected if isinstance(selected, list) else [selected]
        await do_action("/roles", {"role_codes": role_codes}, method="PUT")

    ui.button("保存角色", on_click=handle_set_roles)


def user_management_page() -> None:
    """账号管理页面。"""
    ui.label("账号管理").classes("text-xl font-bold mb-4")
    list_container = ui.html("").classes("w-full mb-4")
    message = ui.label("").classes("text-red-500 mb-4")
    user_selector = ui.select([], label="选择账号", with_input=True).classes("w-full mb-2")

    def show_success(text: str) -> None:
        message.set_text(text)
        message.classes("text-green-500")

    def show_error(text: str) -> None:
        message.set_text(text)
        message.classes("text-red-500")

    async def load_users() -> None:
        await _load_users(list_container, user_selector, show_error)

    async def do_action(path: str, body: dict | None = None, method: str = "POST") -> bool:
        return await _do_action(
            user_selector, path, body, method, show_success, show_error, load_users
        )

    with ui.card().classes("w-full mb-4"):
        ui.label("新建账号").classes("font-bold mb-2")

        async def _on_create_success(text: str) -> None:
            show_success(text)
            await load_users()

        _render_create_form(
            on_success=_on_create_success,
            show_error=show_error,
        )

    with ui.card().classes("w-full mb-4"):
        ui.label("账号操作").classes("font-bold mb-2")
        _render_action_panel(
            do_action=do_action,
            load_users=load_users,
            show_success=show_success,
            show_error=show_error,
        )

    ui.button("刷新列表", on_click=load_users)
    ui.timer(0.1, load_users, once=True)
