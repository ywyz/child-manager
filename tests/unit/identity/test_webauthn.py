from base64 import urlsafe_b64decode
from datetime import UTC, datetime, timedelta
from uuid import UUID

from packages.backend.identity.challenges import (
    ChallengeBinding,
    ChallengePurpose,
    consume_challenge,
    issue_challenge,
)
from packages.backend.identity.webauthn import authentication_options, registration_options

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)
KINDERGARTEN_ID = UUID("00000000-0000-7000-8000-000000000001")
USER_ID = UUID("00000000-0000-7000-8000-000000000002")


def _decode_base64url(value: str) -> bytes:
    return urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _binding(**overrides: object) -> ChallengeBinding:
    values: dict[str, object] = {
        "purpose": ChallengePurpose.INVITATION_REGISTRATION,
        "kindergarten_id": KINDERGARTEN_ID,
        "user_id": USER_ID,
        "authorization_context": "invitation:01900000-0000-7000-8000-000000000003",
        "rp_id": "localhost",
        "origin": "http://localhost:18080",
        "requires_user_verification": True,
    }
    values.update(overrides)
    return ChallengeBinding(**values)  # type: ignore[arg-type]


def test_challenge_is_32_bytes_hashed_and_expires_after_five_minutes() -> None:
    issued = issue_challenge(binding=_binding(), now=NOW, random_bytes=lambda size: b"c" * size)

    assert _decode_base64url(issued.challenge) == b"c" * 32
    assert issued.record.challenge_digest
    assert issued.record.challenge_digest != issued.challenge
    assert issued.record.expires_at == NOW + timedelta(minutes=5)


def test_challenge_is_bound_to_purpose_context_rp_origin_and_single_use() -> None:
    binding = _binding()
    issued = issue_challenge(binding=binding, now=NOW, random_bytes=lambda size: b"d" * size)

    for changed in (
        _binding(purpose=ChallengePurpose.AUTHENTICATION),
        _binding(authorization_context="invitation:other"),
        _binding(rp_id="example.test"),
        _binding(origin="https://example.test"),
        _binding(user_id=UUID("00000000-0000-7000-8000-000000000004")),
        _binding(requires_user_verification=False),
    ):
        assert not consume_challenge(
            issued.record,
            challenge=issued.challenge,
            binding=changed,
            now=NOW + timedelta(minutes=1),
        )
        assert issued.record.consumed_at is None

    assert consume_challenge(
        issued.record,
        challenge=issued.challenge,
        binding=binding,
        now=NOW + timedelta(minutes=1),
    )
    assert not consume_challenge(
        issued.record,
        challenge=issued.challenge,
        binding=binding,
        now=NOW + timedelta(minutes=2),
    )


def test_expired_challenge_cannot_be_consumed() -> None:
    binding = _binding()
    issued = issue_challenge(binding=binding, now=NOW, random_bytes=lambda size: b"e" * size)

    assert not consume_challenge(
        issued.record,
        challenge=issued.challenge,
        binding=binding,
        now=NOW + timedelta(minutes=5, microseconds=1),
    )


def test_registration_options_require_discoverable_credential_and_uv() -> None:
    options = registration_options(
        challenge="Y2hhbGxlbmdl",
        rp_id="localhost",
        rp_name="Child Manager",
        user_handle=b"u" * 32,
        username="teacher",
        display_name="测试教师",
    )

    public_key = options["publicKey"]
    assert isinstance(public_key, dict)
    assert public_key["challenge"] == "Y2hhbGxlbmdl"
    assert public_key["timeout"] == 300_000
    assert public_key["attestation"] == "none"
    assert public_key["authenticatorSelection"] == {
        "residentKey": "required",
        "requireResidentKey": True,
        "userVerification": "required",
    }


def test_username_less_authentication_uses_empty_allow_credentials_and_uv() -> None:
    options = authentication_options(
        challenge="Y2hhbGxlbmdl",
        rp_id="localhost",
    )

    assert options == {
        "publicKey": {
            "challenge": "Y2hhbGxlbmdl",
            "rpId": "localhost",
            "timeout": 300_000,
            "allowCredentials": [],
            "userVerification": "required",
        }
    }
