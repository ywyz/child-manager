"""中文认证页面；业务调用始终经过同源 API。"""

import json

from nicegui import ui


def login_page_text() -> tuple[str, ...]:
    return ("用户名或手机号", "密码", "登录")


def change_password_page_text() -> tuple[str, ...]:
    return ("当前密码", "新密码", "修改密码")


async def post_same_origin(path: str, payload: dict[str, object]) -> dict[str, object]:
    script = f"""
    return await (async () => {{
      const csrfResponse = await fetch('/api/v1/auth/csrf', {{credentials: 'same-origin'}});
      const csrf = await csrfResponse.json();
      const request = () => fetch({json.dumps(path)}, {{
        method: 'POST', credentials: 'same-origin',
        headers: {{'Content-Type': 'application/json', 'X-CSRF-Token': csrf.csrf_token}},
        body: JSON.stringify({json.dumps(payload, ensure_ascii=False)})
      }});
      let response = await request();
      if (response.status === 401 && {json.dumps(path)} !== '/api/v1/auth/login') {{
        const refreshed = await fetch('/api/v1/auth/refresh', {{
          method: 'POST', credentials: 'same-origin',
          headers: {{'X-CSRF-Token': csrf.csrf_token}}
        }});
        if (refreshed.ok) response = await request();
      }}
      if (response.status === 204) return {{ok: true}};
      const body = await response.json();
      return {{ok: response.ok, body}};
    }})();
    """
    result = await ui.run_javascript(script, timeout=10.0)
    return result if isinstance(result, dict) else {"ok": False}


def register_auth_pages() -> None:
    @ui.page("/login")
    def login_page() -> None:
        ui.label("登录").classes("text-h5")
        login = ui.input("用户名或手机号")
        password = ui.input("密码", password=True, password_toggle_button=True)

        async def submit() -> None:
            result = await post_same_origin(
                "/api/v1/auth/login", {"login": login.value, "password": password.value}
            )
            if result.get("ok"):
                ui.navigate.to("/")
            else:
                body = result.get("body", {})
                message = (
                    body.get("message", "登录失败，请重试。") if isinstance(body, dict) else body
                )
                ui.notify(str(message), type="negative")

        ui.button("登录", on_click=submit)

    @ui.page("/change-password")
    def change_password_page() -> None:
        ui.label("修改密码").classes("text-h5")
        current = ui.input("当前密码", password=True, password_toggle_button=True)
        new = ui.input("新密码", password=True, password_toggle_button=True)

        async def submit() -> None:
            result = await post_same_origin(
                "/api/v1/auth/change-password",
                {"current_password": current.value, "new_password": new.value},
            )
            if result.get("ok"):
                ui.notify("密码已修改，请重新登录。", type="positive")
                ui.navigate.to("/login")
            else:
                body = result.get("body", {})
                message = body.get("message", "修改密码失败。") if isinstance(body, dict) else body
                ui.notify(str(message), type="negative")

        ui.button("修改密码", on_click=submit)
