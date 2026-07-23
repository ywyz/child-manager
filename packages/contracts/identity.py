"""身份、通行密钥、邀请、恢复与会话公共契约。"""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from packages.contracts.common import ContractModel

RoleCode = Literal["admin", "teacher"]
UserText = Annotated[str, Field(min_length=1, max_length=120)]
Base64Url = Annotated[
    str,
    Field(
        min_length=1,
        max_length=4096,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="无填充 base64url；服务端解码后仍须执行各字段的字节长度限制",
    ),
]
SecretInput = Annotated[
    str,
    Field(
        min_length=22,
        max_length=512,
        description="只从受控入口输入；数据库只保存带服务端 pepper 的摘要",
        json_schema_extra={"writeOnly": True},
    ),
]
OneTimeSecret = Annotated[
    str,
    Field(
        min_length=22,
        max_length=512,
        description="只在本次成功响应展示一次；不得进入 URL、日志、审计或后续读取响应",
        json_schema_extra={"readOnly": True},
    ),
]
Transport = Literal["usb", "nfc", "ble", "internal", "hybrid"]
CredentialSource = Literal["bootstrap", "invitation", "self_add", "recovery", "migration"]
AccountStatus = Literal["pending_registration", "pending_verification", "active", "suspended"]


def _unique(value: list[str]) -> list[str]:
    if len(value) != len(set(value)):
        raise ValueError("列表项不能重复")
    return value


class CsrfResponse(ContractModel):
    csrf_token: Annotated[str, Field(min_length=32, max_length=512)]


class KindergartenSummary(ContractModel):
    id: UUID
    name: str
    timezone: Literal["Asia/Shanghai"]


class PublicKeyCredentialDescriptor(ContractModel):
    type: Literal["public-key"]
    id: Base64Url
    transports: list[Transport] = Field(
        default_factory=list,
        json_schema_extra={"uniqueItems": True},
    )

    _transports_are_unique = field_validator("transports")(_unique)


class RelyingParty(ContractModel):
    id: Annotated[str, Field(min_length=1, max_length=253)]
    name: Annotated[str, Field(min_length=1, max_length=120)]


class WebAuthnUser(ContractModel):
    id: Base64Url
    name: UserText
    displayName: UserText


class PublicKeyCredentialParameter(ContractModel):
    type: Literal["public-key"]
    alg: Literal[-7, -257]


class AuthenticatorSelection(ContractModel):
    residentKey: Literal["required"]
    requireResidentKey: Literal[True]
    userVerification: Literal["required"]


class RegistrationExtensions(ContractModel):
    credProps: Literal[True] = True


class RegistrationPublicKey(ContractModel):
    challenge: Base64Url
    rp: RelyingParty
    user: WebAuthnUser
    pubKeyCredParams: Annotated[list[PublicKeyCredentialParameter], Field(min_length=1)]
    timeout: Literal[300000]
    excludeCredentials: list[PublicKeyCredentialDescriptor]
    authenticatorSelection: AuthenticatorSelection
    attestation: Literal["none"]
    extensions: RegistrationExtensions | None = None


class WebAuthnRegistrationOptions(ContractModel):
    ceremony_id: UUID
    expires_at: datetime
    publicKey: RegistrationPublicKey


class AuthenticationPublicKey(ContractModel):
    challenge: Base64Url
    rpId: Annotated[str, Field(min_length=1, max_length=253)]
    timeout: Literal[300000]
    allowCredentials: list[PublicKeyCredentialDescriptor]
    userVerification: Literal["required"]


class WebAuthnAuthenticationOptions(ContractModel):
    ceremony_id: UUID
    expires_at: datetime
    publicKey: AuthenticationPublicKey


class RegistrationCredentialResponse(ContractModel):
    clientDataJSON: Base64Url
    attestationObject: Base64Url
    transports: list[Transport] = Field(
        default_factory=list,
        json_schema_extra={"uniqueItems": True},
    )

    _transports_are_unique = field_validator("transports")(_unique)


class AuthenticationCredentialResponse(ContractModel):
    clientDataJSON: Base64Url
    authenticatorData: Base64Url
    signature: Base64Url
    userHandle: Base64Url | None


class RegistrationCredential(ContractModel):
    id: Base64Url
    rawId: Base64Url
    type: Literal["public-key"]
    response: RegistrationCredentialResponse
    clientExtensionResults: dict[str, object]
    authenticatorAttachment: Literal["platform", "cross-platform"] | None = None


class AuthenticationCredential(ContractModel):
    id: Base64Url
    rawId: Base64Url
    type: Literal["public-key"]
    response: AuthenticationCredentialResponse
    clientExtensionResults: dict[str, object]
    authenticatorAttachment: Literal["platform", "cross-platform"] | None = None


class BootstrapRegistrationOptionsRequest(ContractModel):
    bootstrap_token: SecretInput


class InvitationRegistrationOptionsRequest(ContractModel):
    invitation_token: SecretInput


class RecoveryRegistrationOptionsRequest(ContractModel):
    enrollment_token: SecretInput


class RegistrationVerifyRequest(ContractModel):
    ceremony_id: UUID
    credential: RegistrationCredential
    label: Annotated[str, Field(min_length=1, max_length=120)] | None = None


class AuthenticationVerifyRequest(ContractModel):
    ceremony_id: UUID
    credential: AuthenticationCredential


class RegistrationPending(ContractModel):
    user_id: UUID
    status: Literal["pending_verification"]
    credential_id: UUID
    verification_required: Literal[True]


class StepUpResult(ContractModel):
    verified_at: datetime
    valid_until: datetime


class CurrentUser(ContractModel):
    id: UUID
    username: str
    display_name: str
    kindergarten: KindergartenSummary
    role_codes: list[RoleCode] = Field(json_schema_extra={"uniqueItems": True})
    capabilities: list[str] = Field(json_schema_extra={"uniqueItems": True})
    session_id: UUID
    last_reauthenticated_at: datetime | None

    _roles_are_unique = field_validator("role_codes")(_unique)
    _capabilities_are_unique = field_validator("capabilities")(_unique)


class AuthenticationResult(ContractModel):
    user: CurrentUser
    recovery_code: OneTimeSecret | None


class CreateUserRequest(ContractModel):
    username: UserText
    phone_e164: Annotated[str, Field(max_length=32)] | None = None
    display_name: UserText
    role_codes: Annotated[
        list[RoleCode],
        Field(min_length=1, json_schema_extra={"uniqueItems": True}),
    ]

    _roles_are_unique = field_validator("role_codes")(_unique)


class UserPatch(ContractModel):
    username: UserText | None = None
    phone_e164: Annotated[str, Field(max_length=32)] | None = None
    display_name: UserText | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> UserPatch:
        if not self.model_fields_set:
            raise ValueError("至少提供一个待修改字段")
        if any(
            field in self.model_fields_set and getattr(self, field) is None
            for field in ("username", "display_name")
        ):
            raise ValueError("用户名和显示名称不得为 null")
        return self


class RoleUpdate(ContractModel):
    role_codes: Annotated[
        list[RoleCode],
        Field(min_length=1, json_schema_extra={"uniqueItems": True}),
    ]

    _roles_are_unique = field_validator("role_codes")(_unique)


class User(ContractModel):
    id: UUID
    username: Annotated[str, Field(max_length=120)]
    phone_e164: Annotated[str, Field(max_length=32)] | None
    display_name: Annotated[str, Field(max_length=120)]
    role_codes: list[RoleCode] = Field(json_schema_extra={"uniqueItems": True})
    status: AccountStatus
    credential_count: Annotated[int, Field(ge=0)]
    activated_at: datetime | None
    created_at: datetime
    updated_at: datetime

    _roles_are_unique = field_validator("role_codes")(_unique)


UserResponse = User


class UserPage(ContractModel):
    items: list[User]
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1, le=100)]
    total: Annotated[int, Field(ge=0)]


class AccountActivationRequest(ContractModel):
    verification_confirmed: Literal[True]
    verification_note: Annotated[str, Field(max_length=500)] | None = None


class Credential(ContractModel):
    id: UUID
    label: UserText
    transports: list[Transport] = Field(json_schema_extra={"uniqueItems": True})
    backup_eligible: bool
    backup_state: bool
    created_via: CredentialSource
    created_at: datetime
    last_used_at: datetime | None
    revoked_at: datetime | None


class CredentialPatch(ContractModel):
    label: UserText


class CredentialList(ContractModel):
    items: list[Credential]


class InvitationCreateRequest(ContractModel):
    expires_in_hours: Annotated[int, Field(ge=1, le=24)] = 24


class Invitation(ContractModel):
    id: UUID
    user_id: UUID
    status: Literal["pending", "consumed", "expired", "revoked"]
    expires_at: datetime
    issued_at: datetime
    consumed_at: datetime | None
    revoked_at: datetime | None


class InvitationIssued(Invitation):
    invitation_token: OneTimeSecret


class InvitationList(ContractModel):
    items: list[Invitation]


class AdminCredentialRevocationResult(ContractModel):
    credential_id: UUID
    sessions_revoked: Annotated[int, Field(ge=0)]
    reinvitation: InvitationIssued | None


class RecoveryRequestCreate(ContractModel):
    login: UserText
    recovery_code: SecretInput


class RecoveryRequestAccepted(ContractModel):
    message: Literal["如果账号和恢复材料有效，我们会按既定带外方式继续核验。"]


class RecoveryRequest(ContractModel):
    id: UUID
    user_id: UUID
    status: Literal[
        "pending_verification",
        "approved",
        "registration_pending",
        "completed",
        "rejected",
        "expired",
    ]
    requested_at: datetime
    expires_at: datetime
    approved_at: datetime | None


class RecoveryRequestList(ContractModel):
    items: list[RecoveryRequest]


class RecoveryApprovalRequest(ContractModel):
    verification_confirmed: Literal[True]
    verification_note: Annotated[str, Field(max_length=500)] | None = None


class RecoveryEnrollmentIssued(ContractModel):
    recovery_request_id: UUID
    enrollment_token: OneTimeSecret
    expires_at: datetime


class RecoveryCodeIssued(ContractModel):
    recovery_code: OneTimeSecret
    issued_at: datetime


class RecoveryCompleted(ContractModel):
    credential: Credential
    recovery_code: OneTimeSecret
    sessions_revoked: Annotated[int, Field(ge=0)]


class Session(ContractModel):
    id: UUID
    is_current: bool
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    client_ip_hint: Annotated[str, Field(max_length=80)] | None
    user_agent_summary: Annotated[str, Field(max_length=200)] | None


class SessionList(ContractModel):
    items: list[Session]
