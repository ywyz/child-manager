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
    """校验 CSRF 双提交与来源头。"""
    if not cookie_value or not header_value:
        return False

    source = origin or referer
    if not source:
        return False

    if not _is_allowed_host(_origin_host(source)):
        return False

    if settings.environment == "test":
        return cookie_value == header_value

    return verify_csrf_token(header_value, settings.csrf_signing_key)
