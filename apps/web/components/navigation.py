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
    admin_link = '<a href="/users" class="mr-4">账号管理</a>' if "admin" in roles else ""
    return (
        '<nav class="flex items-center">'
        '<a href="/" class="mr-4">首页</a>'
        '<a href="/change-password" class="mr-4">修改密码</a>'
        f"{admin_link}"
        '<a href="#" onclick="logout(event)">退出</a>'
        "</nav>"
    )


_LOGOUT_SCRIPT = """
<script>
async function logout(e) {
  e.preventDefault();
  const csrf = (document.cookie.split('; ').find(r => r.startsWith('child_manager_csrf=')) || '').split('=')[1] || '';
  await fetch('/api/v1/auth/logout', {
    method: 'POST',
    headers: {'X-CSRF-Token': csrf, 'Origin': window.location.origin},
  });
  window.location.href = '/login';
}
</script>
"""


def render_navigation(*, current_user: object) -> None:
    """根据当前用户角色渲染导航。"""
    del current_user  # 导航通过 API 实时获取角色，不依赖传入对象
    ui.add_body_html(_LOGOUT_SCRIPT)
    with ui.header().classes("items-center justify-between"):
        ui.label("幼儿园教育管理系统").classes("text-xl font-bold")
        nav = ui.html(_nav_html([])).classes("ml-auto")

        async def load_roles() -> None:
            result = await ui.run_javascript(_js_get("/api/v1/auth/me"))
            user = json.loads(result) if result else {}
            nav.set_content(_nav_html(user.get("role_codes") or []))

        ui.timer(0.1, load_roles, once=True)
