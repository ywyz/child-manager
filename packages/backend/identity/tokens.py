"""Access JWT 与 opaque Refresh token 接缝。"""

import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any

import jwt


def create_access_token(
    *,
    user_id: str,
    kindergarten_id: str,
    token_family_id: str,
    signing_key: str,
    now: datetime,
    session_version: str | None = None,
) -> str:
    issued_at = now.astimezone(UTC)
    claims = {
        "sub": user_id,
        "kid": kindergarten_id,
        "fid": token_family_id,
        "iat": int(issued_at.timestamp()),
        "exp": int((issued_at + timedelta(minutes=15)).timestamp()),
        "jti": secrets.token_hex(16),
    }
    if session_version is not None:
        claims["sv"] = session_version
    return str(jwt.encode(claims, signing_key, algorithm="HS256"))


def decode_access_token(token: str, *, signing_key: str, now: datetime) -> dict[str, Any]:
    try:
        claims = dict(
            jwt.decode(
                token,
                signing_key,
                algorithms=["HS256"],
                options={
                    "verify_exp": False,
                    "require": ["sub", "kid", "fid", "iat", "exp", "jti"],
                },
            )
        )
    except jwt.PyJWTError as exc:
        raise ValueError("访问令牌无效") from exc
    if int(claims["exp"]) <= int(now.astimezone(UTC).timestamp()):
        raise ValueError("访问令牌已过期")
    return claims


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return sha256(token.encode()).hexdigest()
