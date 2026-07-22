from base64 import urlsafe_b64decode
from dataclasses import asdict

import pytest

from packages.backend.identity.secret_tokens import SecretPurpose, issue_secret, verify_secret


def _decode_base64url(value: str) -> bytes:
    return urlsafe_b64decode(value + "=" * (-len(value) % 4))


@pytest.mark.parametrize(
    "purpose",
    [
        SecretPurpose.BOOTSTRAP,
        SecretPurpose.INVITATION,
        SecretPurpose.RECOVERY_CODE,
        SecretPurpose.RECOVERY_ENROLLMENT,
    ],
)
def test_identity_secret_has_128_bits_and_only_digest_is_persistable(
    purpose: SecretPurpose,
) -> None:
    issued = issue_secret(purpose, random_bytes=lambda size: b"s" * size)

    assert len(_decode_base64url(issued.secret)) >= 16
    assert issued.record.purpose == purpose
    assert issued.record.digest
    assert issued.secret not in str(asdict(issued.record))
    assert set(asdict(issued.record)) == {"purpose", "digest"}
    assert verify_secret(purpose, secret=issued.secret, digest=issued.record.digest)


def test_secret_digest_is_bound_to_purpose() -> None:
    issued = issue_secret(SecretPurpose.INVITATION, random_bytes=lambda size: b"i" * size)

    assert verify_secret(
        SecretPurpose.INVITATION,
        secret=issued.secret,
        digest=issued.record.digest,
    )
    assert not verify_secret(
        SecretPurpose.BOOTSTRAP,
        secret=issued.secret,
        digest=issued.record.digest,
    )
    assert not verify_secret(
        SecretPurpose.INVITATION,
        secret=f"{issued.secret}tampered",
        digest=issued.record.digest,
    )
