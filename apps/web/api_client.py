"""NiceGUI 服务端 BFF 客户端的公开接缝。"""

import json
from dataclasses import dataclass

import httpx
from nicegui import ui

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


async def same_origin_api_request(
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    """从浏览器经同源 BFF 调用 API，并为写请求取得 CSRF token。"""

    script = f"""
    return await (async () => {{
      const csrfResponse = await fetch(
        '/api/v1/auth/csrf', {{credentials: 'same-origin'}}
      );
      const csrf = await csrfResponse.json();
      const options = {{
        method: {json.dumps(method)},
        credentials: 'same-origin',
        headers: {{'X-CSRF-Token': csrf.csrf_token}},
      }};
      const payload = {
        json.dumps(payload, ensure_ascii=False) if payload is not None else "undefined"
    };
      if (payload !== undefined) {{
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(payload);
      }}
      const response = await fetch({json.dumps(path)}, options);
      const body = response.status === 204 ? {{}} : await response.json();
      return {{ok: response.ok, status: response.status, body}};
    }})();
    """
    result = await ui.run_javascript(script, timeout=15.0)
    return result if isinstance(result, dict) else {"ok": False, "status": 0, "body": {}}


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
