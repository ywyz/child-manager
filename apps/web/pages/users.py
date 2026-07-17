"""管理员账号管理页面；不导入后端模型或 Repository。"""

from nicegui import ui

from apps.web.pages.auth import post_same_origin


def users_page_text() -> tuple[str, ...]:
    return ("账号管理", "创建账号", "重置密码", "停用账号")


async def _get_users() -> dict[str, object]:
    result = await ui.run_javascript(
        """
        let response = await fetch(
          '/api/v1/users?page=1&page_size=100', {credentials: 'same-origin'}
        );
        if (response.status === 401) {
          const csrfResponse = await fetch('/api/v1/auth/csrf', {credentials: 'same-origin'});
          const csrf = await csrfResponse.json();
          const refreshed = await fetch('/api/v1/auth/refresh', {
            method: 'POST', credentials: 'same-origin',
            headers: {'X-CSRF-Token': csrf.csrf_token}
          });
          if (refreshed.ok) response = await fetch(
            '/api/v1/users?page=1&page_size=100', {credentials: 'same-origin'}
          );
        }
        const body = await response.json();
        return {ok: response.ok, body};
        """,
        timeout=10.0,
    )
    return result if isinstance(result, dict) else {"ok": False}


def register_users_page() -> None:
    @ui.page("/users")
    def users_page() -> None:
        ui.label("账号管理").classes("text-h5")
        username = ui.input("用户名")
        display_name = ui.input("姓名")
        password = ui.input("初始密码", password=True, password_toggle_button=True)

        async def create() -> None:
            result = await post_same_origin(
                "/api/v1/users",
                {
                    "username": username.value,
                    "display_name": display_name.value,
                    "password": password.value,
                    "role_codes": ["teacher"],
                },
            )
            ui.notify("账号已创建。" if result.get("ok") else "创建账号失败。")

        ui.button("创建账号", on_click=create)
        target_id = ui.input("账号 ID")
        reset_password = ui.input("重置后的密码", password=True, password_toggle_button=True)

        async def reset() -> None:
            result = await post_same_origin(
                f"/api/v1/users/{target_id.value}/reset-password",
                {"new_password": reset_password.value},
            )
            ui.notify("密码已重置。" if result.get("ok") else "重置密码失败。")

        async def deactivate() -> None:
            result = await post_same_origin(f"/api/v1/users/{target_id.value}/deactivate", {})
            ui.notify("账号已停用。" if result.get("ok") else "停用账号失败。")

        ui.button("重置密码", on_click=reset)
        ui.button("停用账号", on_click=deactivate)

        async def list_accounts() -> None:
            result = await _get_users()
            body = result.get("body", {})
            if result.get("ok"):
                total = body.get("total", 0) if isinstance(body, dict) else 0
                ui.notify(f"共 {total} 个账号")
            else:
                ui.notify("读取账号失败。", type="negative")

        ui.button("刷新账号列表", on_click=list_accounts)
