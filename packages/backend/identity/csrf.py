"""签名双提交 CSRF 保护。"""

import hmac
import secrets
from urllib.parse import urlparse

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


def _normalize_origin(origin: str) -> str | None:
    """把 Origin/Referer 规范化为 scheme://host:port 形式，比较完整同源。"""
    try:
        parsed = urlparse(origin)
        if not parsed.scheme or not parsed.hostname:
            return None
        port = parsed.port
        if port is None:
            default_ports = {"http": 80, "https": 443}
            port = default_ports.get(parsed.scheme, 0)
        return f"{parsed.scheme.lower()}://{parsed.hostname.lower()}:{port}"
    except ValueError:
        return None


def _build_allowed_origins() -> set[str]:
    """根据配置生成允许的完整 Origin 集合（scheme + host + effective port）。"""
    origins: set[str] = set()
    web_port = settings.web_port
    scheme = "https" if settings.environment == "production" else "http"
    for host in settings.allowed_hosts:
        origins.add(f"{scheme}://{host}:{web_port}")
    # 保留标准端口的 localhost / 127.0.0.1，便于本地调试
    for host in ("localhost", "127.0.0.1"):
        origins.add(f"{scheme}://{host}")
    return origins


def _is_allowed_origin(origin: str | None) -> bool:
    if origin is None:
        return False
    return origin in _build_allowed_origins()


def validate_csrf_request(
    *, cookie_value: str | None, header_value: str | None, origin: str | None, referer: str | None
) -> bool:
    """校验签名双提交 CSRF：Cookie 与 Header 必须同时存在、均有效且值相同。"""
    if not cookie_value or not header_value:
        return False

    source = origin or referer
    if not source:
        return False

    if not _is_allowed_origin(_normalize_origin(source)):
        return False

    # 签名双提交：分别验证 Cookie 与 Header 的签名，再比较二者是否完全一致。
    if not verify_csrf_token(cookie_value, settings.csrf_signing_key):
        return False
    if not verify_csrf_token(header_value, settings.csrf_signing_key):
        return False
    return cookie_value == header_value


class CsrfError(Exception):
    """CSRF 校验失败的专用异常，错误码为 auth.csrf_invalid。"""

    def __init__(self) -> None:
        self.status_code = 403
        self.detail = "CSRF 校验失败"
        self.code = "auth.csrf_invalid"
        super().__init__(self.detail)


def require_csrf(
    *,
    cookie_value: str | None,
    header_value: str | None,
    origin: str | None,
    referer: str | None,
) -> None:
    """校验 CSRF Cookie 与 Header，失败时抛 CsrfError。

    本函数不依赖 FastAPI/Starlette 的 Request 类型，由 API 层提取原始值后传入。
    """
    if not validate_csrf_request(
        cookie_value=cookie_value,
        header_value=header_value,
        origin=origin,
        referer=referer,
    ):
        raise CsrfError()
