"""初始化、邀请与恢复秘密的公共 seam。"""

import base64
import hmac
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class SecretPurpose(StrEnum):
    BOOTSTRAP = "bootstrap"
    INVITATION = "invitation"
    RECOVERY_CODE = "recovery_code"
    RECOVERY_ENROLLMENT = "recovery_enrollment"


@dataclass(frozen=True)
class SecretRecord:
    purpose: SecretPurpose
    digest: str


@dataclass(frozen=True)
class IssuedSecret:
    secret: str
    record: SecretRecord


def issue_secret(
    purpose: SecretPurpose,
    *,
    random_bytes: Callable[[int], bytes] = secrets.token_bytes,
) -> IssuedSecret:
    """生成 256 位一次性秘密，持久化对象中只保留 purpose 绑定摘要。"""

    secret = base64.urlsafe_b64encode(random_bytes(32)).rstrip(b"=").decode("ascii")
    digest = _digest(purpose, secret)
    return IssuedSecret(secret=secret, record=SecretRecord(purpose=purpose, digest=digest))


def verify_secret(purpose: SecretPurpose, *, secret: str, digest: str) -> bool:
    """以常量时间比较 purpose 绑定摘要。"""

    return bool(secret and digest) and hmac.compare_digest(_digest(purpose, secret), digest)


def _digest(purpose: SecretPurpose, secret: str) -> str:
    return sha256(f"child-manager:{purpose.value}:{secret}".encode()).hexdigest()
