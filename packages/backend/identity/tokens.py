"""Access JWT 与 opaque Refresh 令牌。"""

import hashlib
import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt

_MIN_KEY_LENGTH = 32

# UUIDv4/UUIDv7 等标准 UUID 字符串；parse_refresh_kindergarten_id 用它稳定拒绝
# 非 UUID 园所前缀，避免将非法值下发到 PostgreSQL UUID 列引发 DataError。
_UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def _require_signing_key(signing_key: str) -> None:
    if len(signing_key) < _MIN_KEY_LENGTH:
        msg = "JWT/CSRF 签名密钥长度必须至少 256 bits"
        raise ValueError(msg)


def create_access_token(
    *,
    user_id: str,
    kindergarten_id: str,
    roles: list[str],
    family_id: str,
    signing_key: str,
    expire_minutes: int = 15,
) -> str:
    """签发 Access JWT。

    family_id 与 Refresh Token family 绑定，用于在退出、改密、重置、停用或
    Refresh 重放后使相应旧 Access Token 立即失效。
    """
    _require_signing_key(signing_key)
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "kindergarten_id": kindergarten_id,
        "roles": roles,
        "family_id": family_id,
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + timedelta(minutes=expire_minutes),
    }
    return jwt.encode(payload, signing_key, algorithm="HS256")


def decode_access_token(token: str, signing_key: str) -> dict[str, Any] | None:
    """解码并验证 Access JWT。"""
    try:
        _require_signing_key(signing_key)
        return jwt.decode(token, signing_key, algorithms=["HS256"])
    except jwt.PyJWTError, ValueError:
        return None


def generate_refresh_value(*, kindergarten_id: str) -> str:
    """生成 opaque Refresh 明文；前缀编码园所 ID 以便 Repository 显式隔离。"""
    return f"kg:{kindergarten_id}:{secrets.token_urlsafe(32)}"


def parse_refresh_kindergarten_id(value: str) -> str | None:
    """从 Refresh 明文中解析园所 ID；失败返回 None。

    父 Issue #4 要求对无效 Refresh 稳定拒绝为未认证结果，不得进入数据库
    类型错误。因此除前缀与分段外，还必须校验园所 ID 是合法 UUID，避免
    `kg:not-a-uuid:*` 形态把 `InvalidTextRepresentation` 暴露为 500。
    """
    prefix = "kg:"
    if not value.startswith(prefix):
        return None
    rest = value[len(prefix) :]
    parts = rest.split(":", 1)
    if len(parts) != 2:
        return None
    kindergarten_id = parts[0]
    if not _UUID_PATTERN.fullmatch(kindergarten_id):
        return None
    return kindergarten_id


def hash_refresh_value(value: str) -> str:
    """返回 Refresh 明文 SHA-256 哈希。"""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
