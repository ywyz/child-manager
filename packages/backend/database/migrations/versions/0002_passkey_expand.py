"""扩展通行密钥、邀请、恢复结构并停用旧会话。"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_passkey_expand"
down_revision: str | None = "0001_identity_and_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> tuple[sa.Column[Any], sa.Column[Any]]:
    return (
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )


def _tenant_identity_columns() -> tuple[sa.Column[Any], sa.Column[Any]]:
    return (
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
    )


def upgrade() -> None:
    op.add_column("users", sa.Column("webauthn_user_handle", sa.LargeBinary()))
    op.add_column("users", sa.Column("status", sa.String(32)))
    op.add_column("users", sa.Column("activated_at", sa.DateTime(timezone=True)))
    op.execute(
        """UPDATE users SET
        webauthn_user_handle=decode(
            md5(random()::text || id::text) || md5(id::text || random()::text), 'hex'
        ),
        status=CASE WHEN is_active THEN 'pending_registration' ELSE 'suspended' END"""
    )
    op.alter_column("users", "webauthn_user_handle", nullable=False)
    op.alter_column("users", "status", nullable=False, server_default="pending_registration")
    op.create_unique_constraint("uq_users_webauthn_user_handle", "users", ["webauthn_user_handle"])
    op.create_check_constraint(
        "ck_users_status",
        "users",
        "status IN ('pending_registration','pending_verification','active','suspended')",
    )
    op.execute(
        """UPDATE refresh_tokens SET revoked_at=COALESCE(revoked_at, now()),
        revoke_reason=COALESCE(revoke_reason, 'password_migration')"""
    )

    op.create_table(
        "webauthn_credentials",
        *_tenant_identity_columns(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("credential_id", sa.LargeBinary(), nullable=False, unique=True),
        sa.Column("public_key_cose", sa.LargeBinary(), nullable=False),
        sa.Column("sign_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column(
            "transports", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")
        ),
        sa.Column("aaguid", postgresql.UUID(as_uuid=True)),
        sa.Column("backup_eligible", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("backup_state", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("created_via", sa.String(32), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("revoke_reason", sa.String(64)),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id", "id", name="uq_webauthn_credentials_kindergarten_id_id"
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint(
            "created_via IN ('bootstrap','invitation','self_add','recovery','migration')",
            name="ck_webauthn_credentials_created_via",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(transports) = 'array'", name="ck_webauthn_credentials_transports"
        ),
    )
    op.create_index(
        "ix_webauthn_credentials_user_active",
        "webauthn_credentials",
        ["kindergarten_id", "user_id", "revoked_at"],
    )

    op.create_table(
        "webauthn_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True)),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("purpose", sa.String(48), nullable=False),
        sa.Column("challenge_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("authorization_context", sa.String(200)),
        sa.Column("expected_rp_id", sa.String(253), nullable=False),
        sa.Column("expected_origin", sa.String(512), nullable=False),
        sa.Column(
            "requires_user_verification", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id", "id", name="uq_webauthn_challenges_kindergarten_id_id"
        ),
        sa.ForeignKeyConstraint(["kindergarten_id"], ["kindergartens.id"]),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint(
            "purpose IN ('bootstrap_registration','invitation_registration',"
            "'self_add_registration','recovery_registration','authentication','step_up')",
            name="ck_webauthn_challenges_purpose",
        ),
    )

    op.create_table(
        "bootstrap_initializations",
        *_tenant_identity_columns(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_digest", sa.String(128), nullable=False, unique=True),
        sa.Column("owner_reference", sa.String(160), nullable=False),
        sa.Column("operator_reference", sa.String(160), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("registered_credential_id", postgresql.UUID(as_uuid=True)),
        sa.Column("activated_at", sa.DateTime(timezone=True)),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id", "id", name="uq_bootstrap_initializations_kindergarten_id_id"
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "registered_credential_id"],
            ["webauthn_credentials.kindergarten_id", "webauthn_credentials.id"],
        ),
    )

    op.create_table(
        "account_invitations",
        *_tenant_identity_columns(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issued_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("registered_credential_id", postgresql.UUID(as_uuid=True)),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id", "id", name="uq_account_invitations_kindergarten_id_id"
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "issued_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "registered_credential_id"],
            ["webauthn_credentials.kindergarten_id", "webauthn_credentials.id"],
        ),
    )
    op.create_index(
        "ix_account_invitations_user_active",
        "account_invitations",
        ["kindergarten_id", "user_id", "revoked_at", "consumed_at", "expires_at"],
    )

    op.create_table(
        "recovery_codes",
        *_tenant_identity_columns(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("replaced_by_id", postgresql.UUID(as_uuid=True)),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_recovery_codes_kindergarten_id_id"),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "replaced_by_id"],
            ["recovery_codes.kindergarten_id", "recovery_codes.id"],
        ),
    )
    op.create_index(
        "uq_recovery_codes_user_active",
        "recovery_codes",
        ["kindergarten_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("consumed_at IS NULL AND revoked_at IS NULL"),
    )

    op.create_table(
        "account_recovery_requests",
        *_tenant_identity_columns(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recovery_code_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("enrollment_token_hash", sa.String(128), unique=True),
        sa.Column("enrollment_expires_at", sa.DateTime(timezone=True)),
        sa.Column("enrollment_consumed_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id", "id", name="uq_account_recovery_requests_kindergarten_id_id"
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "recovery_code_id"],
            ["recovery_codes.kindergarten_id", "recovery_codes.id"],
        ),
        sa.CheckConstraint(
            "status IN ('pending_verification','approved','registration_pending',"
            "'completed','rejected','expired')",
            name="ck_account_recovery_requests_status",
        ),
    )

    op.create_table(
        "identity_verification_approvals",
        *_tenant_identity_columns(),
        sa.Column("context_type", sa.String(32), nullable=False),
        sa.Column("context_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approver_user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("approver_kind", sa.String(32), nullable=False),
        sa.Column("approver_reference", sa.String(160), nullable=False),
        sa.Column("decision", sa.String(16), nullable=False),
        sa.Column("note", sa.String(500)),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id", "id", name="uq_identity_approvals_kindergarten_id_id"
        ),
        sa.UniqueConstraint(
            "kindergarten_id",
            "context_type",
            "context_id",
            "approver_kind",
            "approver_reference",
            name="uq_identity_approval_natural_person",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "approver_user_id"], ["users.kindergarten_id", "users.id"]
        ),
    )


def downgrade() -> None:
    op.drop_table("identity_verification_approvals")
    op.drop_table("account_recovery_requests")
    op.drop_table("recovery_codes")
    op.drop_table("account_invitations")
    op.drop_table("bootstrap_initializations")
    op.drop_table("webauthn_challenges")
    op.drop_table("webauthn_credentials")
    op.drop_constraint("ck_users_status", "users", type_="check")
    op.drop_constraint("uq_users_webauthn_user_handle", "users", type_="unique")
    op.drop_column("users", "activated_at")
    op.drop_column("users", "status")
    op.drop_column("users", "webauthn_user_handle")
