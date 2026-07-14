"""NiceGUI 服务端 BFF 客户端的公开接缝。"""

from dataclasses import dataclass

import httpx

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
    """按固定 allowlist 转发请求，并保留响应原始多值头。"""

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
