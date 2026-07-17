from fastapi import Request, Response
from nicegui import app, ui

from apps.web.api_client import proxy_request
from apps.web.components.navigation import render_navigation
from apps.web.pages.auth import change_password_page, login_page
from apps.web.pages.users import user_management_page


def register_web(*, api_base_url: str) -> None:
    @app.api_route(
        "/api/v1/{api_path:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    # pyright: ignore[reportUnusedFunction]
    async def bff(request: Request, api_path: str) -> Response:
        client = request.client
        peer_ip = client.host if client is not None else "127.0.0.1"
        proxied = await proxy_request(
            method=request.method,
            path=f"/api/v1/{api_path}",
            query=request.url.query.encode("ascii"),
            headers=tuple(request.headers.raw),
            body=await request.body(),
            peer_ip=peer_ip,
            api_base_url=api_base_url,
        )
        response = Response(
            content=proxied.body,
            status_code=proxied.status_code,
        )
        response.raw_headers = list(proxied.headers)
        return response

    @ui.page("/")
    # pyright: ignore[reportUnusedFunction]
    async def index() -> None:
        render_navigation(current_user=None)
        with ui.card():
            ui.label("欢迎使用一日活动计划系统")

    @ui.page("/login")
    # pyright: ignore[reportUnusedFunction]
    async def login() -> None:
        await login_page()

    @ui.page("/change-password")
    # pyright: ignore[reportUnusedFunction]
    async def change_password() -> None:
        render_navigation(current_user=None)
        change_password_page()

    @ui.page("/users")
    # pyright: ignore[reportUnusedFunction]
    async def users() -> None:
        render_navigation(current_user=None)
        user_management_page()
