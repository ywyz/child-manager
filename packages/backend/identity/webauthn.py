"""WebAuthn 3.x options 生成与严格注册、认证验证。"""

import json
from collections.abc import Sequence
from typing import Any

from webauthn import (
    base64url_to_bytes,
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.authentication.verify_authentication_response import VerifiedAuthentication
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)
from webauthn.registration.verify_registration_response import VerifiedRegistration


class CredentialCounterAnomaly(Exception):
    """已通过其余认证校验的非备份凭据签名计数异常。"""


def registration_options(
    *,
    challenge: str,
    rp_id: str,
    rp_name: str,
    user_handle: bytes,
    username: str,
    display_name: str,
    exclude_credential_ids: Sequence[bytes] = (),
) -> dict[str, object]:
    """生成可直接传给 ``navigator.credentials.create`` 的 JSON。"""

    options = generate_registration_options(
        rp_id=rp_id,
        rp_name=rp_name,
        user_name=username,
        user_id=user_handle,
        user_display_name=display_name,
        challenge=base64url_to_bytes(challenge),
        timeout=300_000,
        attestation=AttestationConveyancePreference.NONE,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            require_resident_key=True,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
        exclude_credentials=[
            PublicKeyCredentialDescriptor(id=credential_id)
            for credential_id in exclude_credential_ids
        ],
        supported_pub_key_algs=[
            COSEAlgorithmIdentifier.ECDSA_SHA_256,
            COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
        ],
    )
    public_key = json.loads(options_to_json(options))
    public_key.setdefault("excludeCredentials", [])
    return {"publicKey": public_key}


def authentication_options(
    *,
    challenge: str,
    rp_id: str,
    allow_credential_ids: Sequence[bytes] = (),
) -> dict[str, object]:
    """生成无用户名或限定当前账号凭据的浏览器认证 JSON。"""

    options = generate_authentication_options(
        rp_id=rp_id,
        challenge=base64url_to_bytes(challenge),
        timeout=300_000,
        allow_credentials=[
            PublicKeyCredentialDescriptor(id=credential_id)
            for credential_id in allow_credential_ids
        ],
        user_verification=UserVerificationRequirement.REQUIRED,
    )
    public_key = json.loads(options_to_json(options))
    public_key.setdefault("allowCredentials", [])
    return {"publicKey": public_key}


def verify_registration(
    *,
    credential: dict[str, Any],
    expected_challenge: str,
    expected_rp_id: str,
    expected_origin: str,
) -> VerifiedRegistration:
    """校验注册 type、challenge、Origin、RP ID、UP/UV、签名和 attestation。"""

    return verify_registration_response(
        credential=credential,
        expected_challenge=base64url_to_bytes(expected_challenge),
        expected_rp_id=expected_rp_id,
        expected_origin=expected_origin,
        require_user_presence=True,
        require_user_verification=True,
        supported_pub_key_algs=[
            COSEAlgorithmIdentifier.ECDSA_SHA_256,
            COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
        ],
    )


def verify_authentication(
    *,
    credential: dict[str, Any],
    expected_challenge: str,
    expected_rp_id: str,
    expected_origin: str,
    credential_public_key: bytes,
    credential_current_sign_count: int,
    credential_backup_eligible: bool,
) -> VerifiedAuthentication:
    """校验 assertion、用户验证、签名和签名计数器。"""

    verified = verify_authentication_response(
        credential=credential,
        expected_challenge=base64url_to_bytes(expected_challenge),
        expected_rp_id=expected_rp_id,
        expected_origin=expected_origin,
        credential_public_key=credential_public_key,
        # 上游库在签名校验前检查计数器; 直接传当前值会允许伪造 assertion 触发风险处置。
        # 先完成签名校验; 再在下方对非备份凭据执行单调性判定。
        credential_current_sign_count=0,
        require_user_verification=True,
    )
    if (
        not credential_backup_eligible
        and (verified.new_sign_count > 0 or credential_current_sign_count > 0)
        and verified.new_sign_count <= credential_current_sign_count
    ):
        raise CredentialCounterAnomaly
    return verified
