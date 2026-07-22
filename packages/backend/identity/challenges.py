"""WebAuthn ceremony challenge 的公共领域 seam。"""

import base64
import hmac
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from hashlib import sha256
from uuid import UUID, uuid7


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
    random_bytes: Callable[[int], bytes] = secrets.token_bytes,
) -> IssuedChallenge:
    """签发绑定上下文、五分钟有效且只保存摘要的 challenge。"""

    raw = random_bytes(32)
    challenge = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    return IssuedChallenge(
        challenge=challenge,
        record=ChallengeRecord(
            ceremony_id=uuid7(),
            challenge_digest=sha256(raw).hexdigest(),
            binding=binding,
            expires_at=now + timedelta(minutes=5),
        ),
    )


def consume_challenge(
    record: ChallengeRecord,
    *,
    challenge: str,
    binding: ChallengeBinding,
    now: datetime,
) -> bool:
    """常量时间校验绑定并在成功时消费一次。"""

    if record.consumed_at is not None or now > record.expires_at or record.binding != binding:
        return False
    try:
        raw = base64.urlsafe_b64decode(challenge + "=" * (-len(challenge) % 4))
    except ValueError, TypeError:
        return False
    if not hmac.compare_digest(sha256(raw).hexdigest(), record.challenge_digest):
        return False
    record.consumed_at = now
    return True
