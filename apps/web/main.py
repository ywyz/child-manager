import argparse
from dataclasses import dataclass
from ipaddress import ip_address
from typing import Any
from urllib.parse import urlsplit

import httpx
from fastapi import Request, Response
from nicegui import app, ui

_REQUEST_HEADER_ALLOWLIST = {
    b"accept",
    b"content-type",
    b"cookie",
    b"origin",
    b"referer",
    b"x-csrf-token",
    b"x-request-id",
}
_HOP_BY_HOP_HEADERS = {
    b"connection",
    b"keep-alive",
    b"proxy-authenticate",
    b"proxy-authorization",
    b"te",
    b"trailer",
    b"transfer-encoding",
    b"upgrade",
}
_SPOOFED_SOURCE_HEADERS = {
    b"forwarded",
    b"x-forwarded-for",
    b"x-child-manager-client-ip",
}


@dataclass(frozen=True, slots=True)
class BffResponse:
    status_code: int
    headers: tuple[tuple[bytes, bytes], ...]
    body: bytes


async def proxy_request(
    *,
    method: str,
    path: str,
    query: bytes,
    headers: tuple[tuple[bytes, bytes], ...],
    body: bytes,
    peer_ip: str,
    api_base_url: str,
    transport: httpx.AsyncBaseTransport | None = None,
) -> BffResponse:
    forwarded_headers = [
        (name, value)
        for name, value in headers
        if name.lower() in _REQUEST_HEADER_ALLOWLIST
        and name.lower() not in _HOP_BY_HOP_HEADERS
        and name.lower() not in _SPOOFED_SOURCE_HEADERS
    ]
    forwarded_headers.append((b"x-child-manager-client-ip", peer_ip.encode("ascii")))
    base_url = httpx.URL(api_base_url)
    url = base_url.join(path).copy_with(query=query)
    async with httpx.AsyncClient(
        transport=transport, follow_redirects=False, trust_env=False
    ) as client:
        response = await client.send(
            httpx.Request(
                method=method,
                url=url,
                headers=forwarded_headers,
                content=body,
            )
        )
    response_headers = tuple(
        (name, value)
        for name, value in response.headers.raw
        if name.lower() not in _HOP_BY_HOP_HEADERS
    )
    return BffResponse(
        status_code=response.status_code,
        headers=response_headers,
        body=response.content,
    )


def _require_loopback(value: str, label: str) -> None:
    try:
        allowed = ip_address(value).is_loopback
    except ValueError:
        allowed = False
    if not allowed:
        raise ValueError(f"{label}必须使用回环地址")


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def request(self, endpoint: str, method: str = "GET", **kwargs: Any) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url, follow_redirects=False, trust_env=False
        ) as client:
            response = await client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()


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
    async def index() -> None:
        with ui.header():
            ui.label("幼儿园教育管理系统").classes("text-xl font-bold")

        with ui.card():
            ui.label("欢迎使用一日活动计划系统")


def main() -> None:
    parser = argparse.ArgumentParser(description="启动 Child Manager Web BFF")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=28080, type=int)
    parser.add_argument("--api-base-url", default="http://127.0.0.1:28000")
    args = parser.parse_args()

    _require_loopback(args.host, "Web 绑定地址")
    api_host = urlsplit(args.api_base_url).hostname or ""
    _require_loopback(api_host, "API 地址")

    register_web(api_base_url=args.api_base_url)
    ui.run(
        title="幼儿园教育管理系统",
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
