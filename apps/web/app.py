from ipaddress import ip_address

from fastapi import Request, Response
from nicegui import app, ui

from apps.web.api_client import proxy_request


def _require_loopback(value: str, label: str) -> None:
    try:
        allowed = ip_address(value).is_loopback
    except ValueError:
        allowed = False
    if not allowed:
        raise ValueError(f"{label}必须使用回环地址")


def register_web(*, api_base_url: str) -> None:
    @app.api_route(
        "/api/v1/{api_path:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    # pyright: ignore[reportUnusedFunction]
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
    # pyright: ignore[reportUnusedFunction]
    async def index() -> None:
        with ui.header():
            ui.label("幼儿园教育管理系统").classes("text-xl font-bold")

        with ui.card():
            ui.label("欢迎使用一日活动计划系统")
