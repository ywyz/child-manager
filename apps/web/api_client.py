"""NiceGUI 服务端 BFF 客户端的公开接缝。"""

import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import cast

import httpx
from nicegui import app, ui

logger = logging.getLogger(__name__)

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
PLANS_API_PATH = "/api/v1/plans"


async def same_origin_api_request(
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    request_headers: dict[str, str] | None = None,
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
        headers: {{
          'X-CSRF-Token': csrf.csrf_token,
          ...{json.dumps(request_headers or {})},
        }},
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


async def export_file_download(path: str) -> dict[str, object]:
    """通过同源 fetch 下载受保护文件，并保留 API 错误反馈。"""

    script = """
    return await (async () => {
      const response = await fetch(__PATH__, {credentials: 'same-origin'});
      if (!response.ok) {
        let body = {};
        try { body = await response.json(); } catch (_error) {}
        return {ok: false, status: response.status, body};
      }
      const blob = await response.blob();
      const disposition = response.headers.get('Content-Disposition') || '';
      const encoded = disposition.match(/filename\\*=UTF-8''([^;]+)/i);
      let filename = 'daily_activity_plan.docx';
      if (encoded) {
        try { filename = decodeURIComponent(encoded[1]); } catch (_error) {}
      }
      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = objectUrl;
      anchor.download = filename;
      anchor.style.display = 'none';
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(objectUrl);
      return {ok: true, status: response.status, body: {}};
    })();
    """.replace("__PATH__", json.dumps(path))
    try:
        result = await ui.run_javascript(script, timeout=30.0)
    except Exception as exc:
        logger.error(
            "Word 导出浏览器下载失败",
            extra={"exception_type": type(exc).__name__},
        )
        return {
            "ok": False,
            "status": 0,
            "body": {"message": "下载失败，请稍后重试。"},
        }
    return (
        result
        if isinstance(result, dict)
        else {
            "ok": False,
            "status": 0,
            "body": {"message": "下载失败，请稍后重试。"},
        }
    )


async def plan_docx_preview_request(
    plan_id: str,
    *,
    filename: str,
    content_type: str,
    payload: bytes,
) -> dict[str, object]:
    """通过同源 BFF 提取 DOCX，返回待教师确认的临时文本。"""

    api_base_url = getattr(app.state, "child_manager_api_base_url", None)
    if not isinstance(api_base_url, str) or not api_base_url:
        return {"ok": False, "status": 0, "body": {}}
    browser_request = ui.context.client.request
    peer_ip = browser_request.client.host if browser_request.client is not None else "127.0.0.1"
    csrf_response = await proxy_request(
        method="GET",
        path="/api/v1/auth/csrf",
        query=b"",
        headers=tuple(browser_request.headers.raw),
        body=b"",
        peer_ip=peer_ip,
        api_base_url=api_base_url,
    )
    try:
        csrf_body = json.loads(csrf_response.body)
    except json.JSONDecodeError:
        return {"ok": False, "status": csrf_response.status_code, "body": {}}
    csrf_token = csrf_body.get("csrf_token") if isinstance(csrf_body, dict) else None
    if csrf_response.status_code != 200 or not isinstance(csrf_token, str):
        return {"ok": False, "status": csrf_response.status_code, "body": csrf_body}

    multipart = httpx.Request(
        "POST",
        "http://same-origin.invalid",
        files={"file": (filename, payload, content_type)},
    )
    headers = [
        (name, value)
        for name, value in browser_request.headers.raw
        if name.lower() not in {b"content-type", b"cookie", b"x-csrf-token"}
    ]
    existing_cookie = browser_request.headers.get("cookie", "")
    csrf_cookie = f"child_manager_csrf={csrf_token}"
    cookie = f"{existing_cookie}; {csrf_cookie}" if existing_cookie else csrf_cookie
    headers.extend(
        (name, value) for name, value in multipart.headers.raw if name.lower() == b"content-type"
    )
    headers.extend(
        ((b"cookie", cookie.encode("ascii")), (b"x-csrf-token", csrf_token.encode("ascii")))
    )
    response = await proxy_request(
        method="POST",
        path=f"{PLANS_API_PATH}/{plan_id}/group-activity-sources/docx",
        query=b"",
        headers=tuple(headers),
        body=b"".join(cast(Iterable[bytes], multipart.stream)),
        peer_ip=peer_ip,
        api_base_url=api_base_url,
    )
    try:
        body = json.loads(response.body) if response.body else {}
    except json.JSONDecodeError:
        body = {}
    return {
        "ok": 200 <= response.status_code < 300,
        "status": response.status_code,
        "body": body,
    }


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


async def plan_api_request(
    suffix: str = "",
    *,
    method: str = "GET",
    payload: dict[str, object] | None = None,
    request_headers: dict[str, str] | None = None,
) -> dict[str, object]:
    """只通过同源 BFF 访问教案及其任务端点。"""

    is_top_level = suffix.startswith(("/jobs/", "/exports/"))
    return await same_origin_api_request(
        f"/api/v1{suffix}" if is_top_level else f"{PLANS_API_PATH}{suffix}",
        method=method,
        payload=payload,
        request_headers=request_headers,
    )


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
