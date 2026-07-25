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


BACKUP_AUTH_API_PATH = "/api/v1/auth/backup"
BACKUP_AUTHENTICATION_API_PATH = f"{BACKUP_AUTH_API_PATH}/authentication"
BACKUP_REAUTHENTICATION_API_PATH = f"{BACKUP_AUTH_API_PATH}/reauthentication"
SECURITY_EVENTS_API_PATH = "/api/v1/auth/security-events"


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


async def backup_auth_api_request(
    suffix: str = "",
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    """只通过同源 BFF 访问本人备用登录端点。"""

    return await same_origin_api_request(
        f"{BACKUP_AUTH_API_PATH}{suffix}",
        method=method,
        payload=payload,
    )


async def backup_login_api_request(
    *,
    identifier: str,
    password: str,
    totp_code: str,
) -> dict[str, object]:
    """以请求正文提交两项备用因素，不把秘密放入 URL。"""

    return await same_origin_api_request(
        BACKUP_AUTHENTICATION_API_PATH,
        method="POST",
        payload={
            "identifier": identifier,
            "password": password,
            "totp_code": totp_code,
        },
    )


async def backup_reauthentication_api_request(
    *,
    password: str,
    totp_code: str,
) -> dict[str, object]:
    """为当前备用会话取得仅可新增通行密钥的短时证明。"""

    return await same_origin_api_request(
        BACKUP_REAUTHENTICATION_API_PATH,
        method="POST",
        payload={"password": password, "totp_code": totp_code},
    )


async def security_events_api_request() -> dict[str, object]:
    """读取本人最近 20 条内建安全事件，不产生已读状态。"""

    return await same_origin_api_request(SECURITY_EVENTS_API_PATH)


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
