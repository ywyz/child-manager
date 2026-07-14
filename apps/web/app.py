"""NiceGUI 页面与同源 API BFF 装配。"""

from fastapi import Request, Response
from nicegui import app, ui

from apps.web.api_client import proxy_request


def register_web(*, api_base_url: str) -> None:
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
        ui.label("Child Manager")
        ui.label("请登录后使用幼儿园一日活动计划。")
