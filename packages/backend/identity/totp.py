"""RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。"""

import base64
import hashlib
import hmac
import secrets
import struct
import time

TOTP_DIGITS = 6
TOTP_PERIOD_SECONDS = 30
TOTP_SECRET_BYTES = 20


def generate_totp_secret() -> str:
    """生成认证器广泛兼容的 160 位无填充 Base32 种子。"""

    return base64.b32encode(secrets.token_bytes(TOTP_SECRET_BYTES)).decode("ascii")


def _counter(timestamp: float | int) -> int:
    if timestamp < 0:
        raise ValueError("TOTP 时间戳不能为负数")
    return int(timestamp) // TOTP_PERIOD_SECONDS


def candidate_totp_counters(*, timestamp: float | int | None = None) -> tuple[int, ...]:
    """返回当前时间步及相邻一个时间步，按 counter 递增排序。"""

    current = _counter(time.time() if timestamp is None else timestamp)
    return tuple(counter for counter in (current - 1, current, current + 1) if counter >= 0)


def _secret_bytes(secret: str) -> bytes:
    compact = "".join(secret.split()).upper()
    padding = "=" * (-len(compact) % 8)
    decoded = base64.b32decode(compact + padding, casefold=False)
    if len(decoded) < TOTP_SECRET_BYTES:
        raise ValueError("TOTP 种子熵不足")
    return decoded


def _hotp(secret: bytes, counter: int) -> str:
    digest = hmac.new(secret, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = int.from_bytes(digest[offset : offset + 4], "big") & 0x7FFF_FFFF
    return f"{binary % (10**TOTP_DIGITS):0{TOTP_DIGITS}d}"


def generate_totp(secret: str, *, timestamp: float | int | None = None) -> str:
    """按固定 SHA-1、6 位、30 秒参数生成 TOTP。"""

    counter = _counter(time.time() if timestamp is None else timestamp)
    return _hotp(_secret_bytes(secret), counter)


def verify_totp(
    secret: str,
    code: str,
    *,
    timestamp: float | int | None = None,
    last_accepted_counter: int | None,
) -> int | None:
    """返回匹配且尚未消费的 counter；失败或重放时返回 ``None``。"""

    if len(code) != TOTP_DIGITS or not code.isascii() or not code.isdigit():
        return None
    secret_bytes = _secret_bytes(secret)
    for counter in candidate_totp_counters(timestamp=timestamp):
        if last_accepted_counter is not None and counter <= last_accepted_counter:
            continue
        if hmac.compare_digest(_hotp(secret_bytes, counter), code):
            return counter
    return None
