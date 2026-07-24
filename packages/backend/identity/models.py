"""最终通行密钥身份、邀请、恢复和会话 ORM 模型。"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.backend.database.base import Base


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Kindergarten(Timestamped, Base):
    __tablename__ = "kindergartens"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Shanghai")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint("timezone = 'Asia/Shanghai'", name="ck_kindergartens_timezone"),
    )


class User(Timestamped, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("kindergartens.id"), nullable=False
    )
    username: Mapped[str] = mapped_column(String(120))
    username_normalized: Mapped[str] = mapped_column(String(120))
    phone_e164: Mapped[str | None] = mapped_column(String(32))
    display_name: Mapped[str] = mapped_column(String(120))
    webauthn_user_handle: Mapped[bytes] = mapped_column(LargeBinary, unique=True)
    status: Mapped[str] = mapped_column(String(32), default="pending_registration")
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    updated_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    backup_auth_version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_users_kindergarten_id_id"),
        UniqueConstraint(
            "kindergarten_id", "username_normalized", name="uq_users_kindergarten_username"
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"], ["users.kindergarten_id", "users.id"]
        ),
        CheckConstraint(
            "status IN ('pending_registration','pending_verification','active','suspended')",
            name="ck_users_status",
        ),
        CheckConstraint("backup_auth_version >= 1", name="ck_users_backup_auth_version"),
        Index(
            "uq_users_kindergarten_phone",
            "kindergarten_id",
            "phone_e164",
            unique=True,
            postgresql_where=text("phone_e164 IS NOT NULL"),
        ),
        Index("ix_users_kindergarten_status", "kindergarten_id", "status"),
    )


class BackupAuthCredential(Timestamped, Base):
    __tablename__ = "backup_auth_credentials"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    status: Mapped[str] = mapped_column(String(16))
    password_hash: Mapped[str | None] = mapped_column(Text)
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    totp_ciphertext: Mapped[bytes | None] = mapped_column(LargeBinary)
    totp_nonce: Mapped[bytes | None] = mapped_column(LargeBinary)
    totp_key_id: Mapped[str | None] = mapped_column(String(64))
    totp_envelope_version: Mapped[int | None] = mapped_column(SmallInteger)
    totp_algorithm: Mapped[str] = mapped_column(String(16), default="SHA1", server_default="SHA1")
    totp_digits: Mapped[int] = mapped_column(SmallInteger, default=6, server_default="6")
    totp_period_seconds: Mapped[int] = mapped_column(
        SmallInteger,
        default=30,
        server_default="30",
    )
    last_accepted_counter: Mapped[int | None] = mapped_column(BigInteger)
    enabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint(
            "kindergarten_id",
            "id",
            name="uq_backup_auth_credentials_kindergarten_id_id",
        ),
        UniqueConstraint(
            "kindergarten_id",
            "user_id",
            name="uq_backup_auth_credentials_kindergarten_user",
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "user_id"],
            ["users.kindergarten_id", "users.id"],
        ),
        CheckConstraint(
            "status IN ('enabled','revoked')",
            name="ck_backup_auth_credentials_status",
        ),
        CheckConstraint(
            """(
                status = 'enabled'
                AND password_hash IS NOT NULL
                AND password_changed_at IS NOT NULL
                AND totp_ciphertext IS NOT NULL
                AND totp_nonce IS NOT NULL
                AND totp_key_id IS NOT NULL
                AND totp_envelope_version IS NOT NULL
                AND enabled_at IS NOT NULL
                AND revoked_at IS NULL
            ) OR (
                status = 'revoked'
                AND password_hash IS NULL
                AND totp_ciphertext IS NULL
                AND totp_nonce IS NULL
                AND totp_key_id IS NULL
                AND totp_envelope_version IS NULL
                AND revoked_at IS NOT NULL
            )""",
            name="ck_backup_auth_credentials_material",
        ),
        CheckConstraint(
            "totp_nonce IS NULL OR octet_length(totp_nonce) = 12",
            name="ck_backup_auth_credentials_nonce_length",
        ),
        CheckConstraint(
            "totp_envelope_version IS NULL OR totp_envelope_version >= 1",
            name="ck_backup_auth_credentials_envelope_version",
        ),
        CheckConstraint(
            "totp_algorithm = 'SHA1' AND totp_digits = 6 AND totp_period_seconds = 30",
            name="ck_backup_auth_credentials_totp_parameters",
        ),
        CheckConstraint(
            "last_accepted_counter IS NULL OR last_accepted_counter >= 0",
            name="ck_backup_auth_credentials_counter",
        ),
        Index(
            "ix_backup_auth_credentials_status",
            "kindergarten_id",
            "status",
            "updated_at",
        ),
    )


class BackupAuthEnrollment(Timestamped, Base):
    __tablename__ = "backup_auth_enrollments"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    session_token_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    totp_ciphertext: Mapped[bytes] = mapped_column(LargeBinary)
    totp_nonce: Mapped[bytes] = mapped_column(LargeBinary)
    totp_key_id: Mapped[str] = mapped_column(String(64))
    totp_envelope_version: Mapped[int] = mapped_column(SmallInteger)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    invalidation_reason: Mapped[str | None] = mapped_column(String(32))

    __table_args__ = (
        UniqueConstraint(
            "kindergarten_id",
            "id",
            name="uq_backup_auth_enrollments_kindergarten_id_id",
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "user_id"],
            ["users.kindergarten_id", "users.id"],
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "session_token_id"],
            ["refresh_tokens.kindergarten_id", "refresh_tokens.id"],
        ),
        CheckConstraint(
            "octet_length(totp_nonce) = 12",
            name="ck_backup_auth_enrollments_nonce_length",
        ),
        CheckConstraint(
            "totp_envelope_version >= 1",
            name="ck_backup_auth_enrollments_envelope_version",
        ),
        CheckConstraint(
            "consumed_at IS NULL OR invalidated_at IS NULL",
            name="ck_backup_auth_enrollments_terminal_state",
        ),
        CheckConstraint(
            """(invalidated_at IS NULL AND invalidation_reason IS NULL)
            OR (invalidated_at IS NOT NULL AND invalidation_reason IS NOT NULL)""",
            name="ck_backup_auth_enrollments_invalidation_reason",
        ),
        CheckConstraint(
            """invalidation_reason IS NULL
            OR invalidation_reason IN ('superseded','session_changed','factor_changed')""",
            name="ck_backup_auth_enrollments_invalidation_reason_value",
        ),
        Index(
            "uq_backup_auth_enrollments_active",
            "kindergarten_id",
            "user_id",
            unique=True,
            postgresql_where=text("consumed_at IS NULL AND invalidated_at IS NULL"),
        ),
        Index(
            "ix_backup_auth_enrollments_session",
            "kindergarten_id",
            "session_token_id",
        ),
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)


class UserRole(Timestamped, Base):
    __tablename__ = "user_roles"

    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    role_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True
    )
    assigned_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        ForeignKeyConstraint(["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]),
        ForeignKeyConstraint(
            ["kindergarten_id", "assigned_by"], ["users.kindergarten_id", "users.id"]
        ),
    )


class WebAuthnCredential(Timestamped, Base):
    __tablename__ = "webauthn_credentials"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    credential_id: Mapped[bytes] = mapped_column(LargeBinary, unique=True)
    public_key_cose: Mapped[bytes] = mapped_column(LargeBinary)
    sign_count: Mapped[int] = mapped_column(BigInteger, default=0)
    transports: Mapped[list[str]] = mapped_column(JSONB, default=list)
    aaguid: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    backup_eligible: Mapped[bool] = mapped_column(Boolean, default=False)
    backup_state: Mapped[bool] = mapped_column(Boolean, default=False)
    label: Mapped[str] = mapped_column(String(120))
    created_via: Mapped[str] = mapped_column(String(32))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoke_reason: Mapped[str | None] = mapped_column(String(64))

    __table_args__ = (
        UniqueConstraint(
            "kindergarten_id", "id", name="uq_webauthn_credentials_kindergarten_id_id"
        ),
        ForeignKeyConstraint(["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]),
    )


class WebAuthnChallenge(Timestamped, Base):
    __tablename__ = "webauthn_challenges"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("kindergartens.id")
    )
    user_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    purpose: Mapped[str] = mapped_column(String(48))
    challenge_hash: Mapped[str] = mapped_column(String(128), unique=True)
    authorization_context: Mapped[str | None] = mapped_column(String(200))
    expected_rp_id: Mapped[str] = mapped_column(String(253))
    expected_origin: Mapped[str] = mapped_column(String(512))
    requires_user_verification: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_webauthn_challenges_kindergarten_id_id"),
        ForeignKeyConstraint(["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]),
    )


class BootstrapInitialization(Timestamped, Base):
    __tablename__ = "bootstrap_initializations"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    token_digest: Mapped[str] = mapped_column(String(128), unique=True)
    owner_reference: Mapped[str] = mapped_column(String(160))
    operator_reference: Mapped[str] = mapped_column(String(160))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    registered_credential_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint(
            "kindergarten_id", "id", name="uq_bootstrap_initializations_kindergarten_id_id"
        ),
        ForeignKeyConstraint(["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]),
    )


class AccountInvitation(Timestamped, Base):
    __tablename__ = "account_invitations"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    issued_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    token_hash: Mapped[str] = mapped_column(String(128), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    registered_credential_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_account_invitations_kindergarten_id_id"),
        ForeignKeyConstraint(["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]),
        ForeignKeyConstraint(
            ["kindergarten_id", "issued_by"], ["users.kindergarten_id", "users.id"]
        ),
    )


class RecoveryCode(Timestamped, Base):
    __tablename__ = "recovery_codes"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    code_hash: Mapped[str] = mapped_column(String(128), unique=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_recovery_codes_kindergarten_id_id"),
        ForeignKeyConstraint(["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]),
    )


class AccountRecoveryRequest(Timestamped, Base):
    __tablename__ = "account_recovery_requests"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    recovery_code_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    status: Mapped[str] = mapped_column(String(32))
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    enrollment_token_hash: Mapped[str | None] = mapped_column(String(128), unique=True)
    enrollment_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    enrollment_consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint(
            "kindergarten_id", "id", name="uq_account_recovery_requests_kindergarten_id_id"
        ),
        ForeignKeyConstraint(["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]),
        ForeignKeyConstraint(
            ["kindergarten_id", "recovery_code_id"],
            ["recovery_codes.kindergarten_id", "recovery_codes.id"],
        ),
    )


class IdentityVerificationApproval(Timestamped, Base):
    __tablename__ = "identity_verification_approvals"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    context_type: Mapped[str] = mapped_column(String(32))
    context_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    approver_user_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    approver_kind: Mapped[str] = mapped_column(String(32))
    approver_reference: Mapped[str] = mapped_column(String(160))
    decision: Mapped[str] = mapped_column(String(16))
    note: Mapped[str | None] = mapped_column(String(500))
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class RefreshToken(Timestamped, Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    token_family_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True))
    token_hash: Mapped[str] = mapped_column(String(128), unique=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_reauthenticated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    authentication_method: Mapped[str] = mapped_column(
        String(24), default="webauthn", server_default="webauthn"
    )
    webauthn_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    backup_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    backup_reauthenticated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    backup_auth_version: Mapped[int | None] = mapped_column(Integer)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoke_reason: Mapped[str | None] = mapped_column(String(64))
    replaced_by_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    client_label: Mapped[str | None] = mapped_column(String(160))

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_refresh_tokens_kindergarten_id_id"),
        ForeignKeyConstraint(["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]),
        ForeignKeyConstraint(
            ["kindergarten_id", "replaced_by_id"],
            ["refresh_tokens.kindergarten_id", "refresh_tokens.id"],
        ),
        CheckConstraint(
            "authentication_method IN ('webauthn','password_totp','restricted_enrollment')",
            name="ck_refresh_tokens_authentication_method",
        ),
        CheckConstraint(
            "backup_auth_version IS NULL OR backup_auth_version >= 1",
            name="ck_refresh_tokens_backup_auth_version",
        ),
        CheckConstraint(
            """(
                authentication_method = 'webauthn'
                AND webauthn_verified_at IS NOT NULL
                AND backup_verified_at IS NULL
                AND backup_auth_version IS NULL
            ) OR (
                authentication_method = 'password_totp'
                AND backup_verified_at IS NOT NULL
                AND backup_auth_version IS NOT NULL
            ) OR (
                authentication_method = 'restricted_enrollment'
                AND webauthn_verified_at IS NOT NULL
                AND backup_verified_at IS NULL
                AND backup_auth_version IS NOT NULL
            )""",
            name="ck_refresh_tokens_authentication_assurance",
        ),
    )
