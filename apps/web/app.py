"""NiceGUI 页面与同源 API BFF 装配。"""

from fastapi import Request, Response
from nicegui import app, ui

from apps.web.api_client import proxy_request
from apps.web.components.navigation import navigation_for_capabilities
from apps.web.pages.auth import post_same_origin, register_auth_pages
from apps.web.pages.users import register_users_page


def register_web(*, api_base_url: str) -> None:
    register_auth_pages()
    register_users_page()

    @app.api_route(
        "/api/v1/{api_path:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    async def bff(request: Request, api_path: str) -> Response:
        peer_ip = request.client.host if request.client is not None else "127.0.0.1"
        proxied = await proxy_request(
            method=request.method,
            path=f"/api/v1/{api_path}",
            query=request.url.query.encode("ascii"),
            headers=tuple(request.headers.raw),
            body=await request.body(),
            peer_ip=peer_ip,
            api_base_url=api_base_url,
        )
        response = Response(content=proxied.body, status_code=proxied.status_code)
        response.raw_headers = list(proxied.headers)
        return response

    @ui.page("/")
    def index() -> None:
        ui.label("首页")
        navigation = ui.row()

        async def load_session() -> None:
            result = await ui.run_javascript(
                """
                let response = await fetch('/api/v1/auth/me', {credentials: 'same-origin'});
                if (response.status === 401) {
                  const csrfResponse = await fetch(
                    '/api/v1/auth/csrf', {credentials: 'same-origin'}
                  );
                  const csrf = await csrfResponse.json();
                  const refreshed = await fetch('/api/v1/auth/refresh', {
                    method: 'POST', credentials: 'same-origin',
                    headers: {'X-CSRF-Token': csrf.csrf_token}
                  });
                  if (refreshed.ok) response = await fetch(
                    '/api/v1/auth/me', {credentials: 'same-origin'}
                  );
                }
                const body = await response.json();
                return {ok: response.ok, body};
                """,
                timeout=10.0,
            )
            if not isinstance(result, dict) or not result.get("ok"):
                ui.navigate.to("/login")
                return
            body = result.get("body", {})
            capabilities = body.get("capabilities", []) if isinstance(body, dict) else []
            safe_capabilities = [str(value) for value in capabilities]
            with navigation:
                for label in navigation_for_capabilities(safe_capabilities):
                    target = {
                        "账号管理": "/users",
                        "通行密钥与会话": "/account/security",
                    }.get(label, "/")
                    ui.link(label, target)

                async def logout() -> None:
                    await post_same_origin("/api/v1/auth/logout", {})
                    ui.navigate.to("/login")

                ui.button("退出登录", on_click=logout)

        ui.timer(0.1, load_session, once=True)
