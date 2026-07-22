"""WebAuthn ceremony challenge 的公共领域 seam。"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class ChallengePurpose(StrEnum):
    BOOTSTRAP_REGISTRATION = "bootstrap_registration"
    INVITATION_REGISTRATION = "invitation_registration"
    SELF_ADD_REGISTRATION = "self_add_registration"
    RECOVERY_REGISTRATION = "recovery_registration"
    AUTHENTICATION = "authentication"
    STEP_UP = "step_up"


@dataclass(frozen=True)
class ChallengeBinding:
    purpose: ChallengePurpose
    kindergarten_id: UUID | None
    user_id: UUID | None
    authorization_context: str | None
    rp_id: str
    origin: str
    requires_user_verification: bool


@dataclass
class ChallengeRecord:
    ceremony_id: UUID
    challenge_digest: str
    binding: ChallengeBinding
    expires_at: datetime
    consumed_at: datetime | None = None


@dataclass(frozen=True)
class IssuedChallenge:
    challenge: str
    record: ChallengeRecord


def issue_challenge(
    *,
    binding: ChallengeBinding,
    now: datetime,
    random_bytes: Callable[[int], bytes],
) -> IssuedChallenge:
    """T029 将用高熵随机值和摘要替换当前中性 skeleton。"""

    del random_bytes
    return IssuedChallenge(
        challenge="",
        record=ChallengeRecord(
            ceremony_id=UUID(int=0),
            challenge_digest="",
            binding=binding,
            expires_at=now,
        ),
    )


def consume_challenge(
    record: ChallengeRecord,
    *,
    challenge: str,
    binding: ChallengeBinding,
    now: datetime,
) -> bool:
    """T029 将实现绑定校验和单次消费。"""

    del record, challenge, binding, now
    return False
