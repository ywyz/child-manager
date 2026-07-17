"""签名双提交 CSRF 保护。"""

import hmac
import secrets
from urllib.parse import urlparse

from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

from packages.backend.config import settings

_MIN_KEY_LENGTH = 32


def _require_signing_key(signing_key: str) -> None:
    if len(signing_key) < _MIN_KEY_LENGTH:
        msg = "CSRF 签名密钥长度必须至少 256 bits"
        raise ValueError(msg)


def generate_csrf_token(signing_key: str) -> str:
    """生成签名 CSRF 令牌。"""
    _require_signing_key(signing_key)
    nonce = secrets.token_urlsafe(16)
    signature = hmac.new(signing_key.encode("utf-8"), nonce.encode("utf-8"), "sha256").hexdigest()
    return f"{nonce}.{signature}"


def verify_csrf_token(token: str, signing_key: str) -> bool:
    """验证签名 CSRF 令牌。"""
    _require_signing_key(signing_key)
    if "." not in token:
        return False
    nonce, signature = token.split(".", 1)
    expected = hmac.new(signing_key.encode("utf-8"), nonce.encode("utf-8"), "sha256").hexdigest()
    return hmac.compare_digest(signature, expected)


def _origin_host(origin: str) -> str | None:
    try:
        parsed = urlparse(origin)
        return parsed.hostname
    except ValueError:
        return None


def _is_allowed_host(host: str | None) -> bool:
    if host is None:
        return False
    allowed = set(settings.allowed_hosts)
    allowed.add("localhost")
    allowed.add("127.0.0.1")
    return host in allowed


def validate_csrf_request(
    *, cookie_value: str | None, header_value: str | None, origin: str | None, referer: str | None
) -> bool:
    """校验签名双提交 CSRF：Cookie 与 Header 必须同时存在、均有效且值相同。"""
    if not cookie_value or not header_value:
        return False

    source = origin or referer
    if not source:
        return False

    if not _is_allowed_host(_origin_host(source)):
        return False

    # 签名双提交：分别验证 Cookie 与 Header 的签名，再比较二者是否完全一致。
    if not verify_csrf_token(cookie_value, settings.csrf_signing_key):
        return False
    if not verify_csrf_token(header_value, settings.csrf_signing_key):
        return False
    return cookie_value == header_value


class CsrfError(StarletteHTTPException):
    """CSRF 校验失败的专用异常，错误码为 auth.csrf_invalid。"""

    def __init__(self) -> None:
        super().__init__(status_code=403, detail="CSRF 校验失败")
        self.code = "auth.csrf_invalid"


def require_csrf(request: Request) -> None:
    """从请求中读取 CSRF Cookie 与 Header，校验失败时抛 CsrfError。"""
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    cookie = request.cookies.get("child_manager_csrf")
    header = request.headers.get("x-csrf-token")
    if not validate_csrf_request(
        cookie_value=cookie,
        header_value=header,
        origin=origin,
        referer=referer,
    ):
        raise CsrfError()
