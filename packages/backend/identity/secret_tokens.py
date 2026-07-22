"""初始化、邀请与恢复秘密的公共 seam。"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum


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
    random_bytes: Callable[[int], bytes],
) -> IssuedSecret:
    """T029 将生成一次展示、只存摘要的高熵秘密。"""

    del random_bytes
    return IssuedSecret(secret="", record=SecretRecord(purpose=purpose, digest=""))


def verify_secret(purpose: SecretPurpose, *, secret: str, digest: str) -> bool:
    """T029 将实现 purpose 绑定的常量时间摘要校验。"""

    del purpose, secret, digest
    return False
