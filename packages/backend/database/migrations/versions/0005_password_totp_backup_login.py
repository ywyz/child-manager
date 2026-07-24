"""建立密码与 TOTP 双因素备用登录基础 Schema。"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_password_totp_backup_login"
down_revision: str | None = "0004_settings"
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


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "backup_auth_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )
    op.create_check_constraint(
        "ck_users_backup_auth_version",
        "users",
        "backup_auth_version >= 1",
    )

    op.add_column(
        "refresh_tokens",
        sa.Column(
            "authentication_method",
            sa.String(24),
            nullable=True,
        ),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column(
            "webauthn_verified_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("backup_verified_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("backup_reauthenticated_at", sa.DateTime(timezone=True)),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("backup_auth_version", sa.Integer()),
    )
    op.execute(
        """UPDATE refresh_tokens
        SET authentication_method='webauthn',
            webauthn_verified_at=COALESCE(last_reauthenticated_at, issued_at)"""
    )
    op.alter_column(
        "refresh_tokens",
        "authentication_method",
        nullable=False,
        server_default="webauthn",
    )
    op.create_check_constraint(
        "ck_refresh_tokens_authentication_method",
        "refresh_tokens",
        "authentication_method IN ('webauthn','password_totp','restricted_enrollment')",
    )
    op.create_check_constraint(
        "ck_refresh_tokens_backup_auth_version",
        "refresh_tokens",
        "backup_auth_version IS NULL OR backup_auth_version >= 1",
    )
    op.create_check_constraint(
        "ck_refresh_tokens_authentication_assurance",
        "refresh_tokens",
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
    )

    op.create_table(
        "backup_auth_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("password_hash", sa.Text()),
        sa.Column("password_changed_at", sa.DateTime(timezone=True)),
        sa.Column("totp_ciphertext", sa.LargeBinary()),
        sa.Column("totp_nonce", sa.LargeBinary()),
        sa.Column("totp_key_id", sa.String(64)),
        sa.Column("totp_envelope_version", sa.SmallInteger()),
        sa.Column(
            "totp_algorithm",
            sa.String(16),
            nullable=False,
            server_default="SHA1",
        ),
        sa.Column(
            "totp_digits",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("6"),
        ),
        sa.Column(
            "totp_period_seconds",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("30"),
        ),
        sa.Column("last_accepted_counter", sa.BigInteger()),
        sa.Column("enabled_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id",
            "id",
            name="uq_backup_auth_credentials_kindergarten_id_id",
        ),
        sa.UniqueConstraint(
            "kindergarten_id",
            "user_id",
            name="uq_backup_auth_credentials_kindergarten_user",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"],
            ["users.kindergarten_id", "users.id"],
        ),
        sa.CheckConstraint(
            "status IN ('enabled','revoked')",
            name="ck_backup_auth_credentials_status",
        ),
        sa.CheckConstraint(
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
        sa.CheckConstraint(
            "totp_nonce IS NULL OR octet_length(totp_nonce) = 12",
            name="ck_backup_auth_credentials_nonce_length",
        ),
        sa.CheckConstraint(
            "totp_envelope_version IS NULL OR totp_envelope_version >= 1",
            name="ck_backup_auth_credentials_envelope_version",
        ),
        sa.CheckConstraint(
            "totp_algorithm = 'SHA1' AND totp_digits = 6 AND totp_period_seconds = 30",
            name="ck_backup_auth_credentials_totp_parameters",
        ),
        sa.CheckConstraint(
            "last_accepted_counter IS NULL OR last_accepted_counter >= 0",
            name="ck_backup_auth_credentials_counter",
        ),
    )
    op.create_index(
        "ix_backup_auth_credentials_status",
        "backup_auth_credentials",
        ["kindergarten_id", "status", "updated_at"],
    )

    op.create_table(
        "backup_auth_enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_token_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("totp_ciphertext", sa.LargeBinary(), nullable=False),
        sa.Column("totp_nonce", sa.LargeBinary(), nullable=False),
        sa.Column("totp_key_id", sa.String(64), nullable=False),
        sa.Column(
            "totp_envelope_version",
            sa.SmallInteger(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("invalidated_at", sa.DateTime(timezone=True)),
        sa.Column("invalidation_reason", sa.String(32)),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id",
            "id",
            name="uq_backup_auth_enrollments_kindergarten_id_id",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"],
            ["users.kindergarten_id", "users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "session_token_id"],
            ["refresh_tokens.kindergarten_id", "refresh_tokens.id"],
        ),
        sa.CheckConstraint(
            "octet_length(totp_nonce) = 12",
            name="ck_backup_auth_enrollments_nonce_length",
        ),
        sa.CheckConstraint(
            "totp_envelope_version >= 1",
            name="ck_backup_auth_enrollments_envelope_version",
        ),
        sa.CheckConstraint(
            "consumed_at IS NULL OR invalidated_at IS NULL",
            name="ck_backup_auth_enrollments_terminal_state",
        ),
        sa.CheckConstraint(
            """(invalidated_at IS NULL AND invalidation_reason IS NULL)
            OR (invalidated_at IS NOT NULL AND invalidation_reason IS NOT NULL)""",
            name="ck_backup_auth_enrollments_invalidation_reason",
        ),
        sa.CheckConstraint(
            """invalidation_reason IS NULL
            OR invalidation_reason IN ('superseded','session_changed','factor_changed')""",
            name="ck_backup_auth_enrollments_invalidation_reason_value",
        ),
    )
    op.create_index(
        "uq_backup_auth_enrollments_active",
        "backup_auth_enrollments",
        ["kindergarten_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("consumed_at IS NULL AND invalidated_at IS NULL"),
    )
    op.create_index(
        "ix_backup_auth_enrollments_session",
        "backup_auth_enrollments",
        ["kindergarten_id", "session_token_id"],
    )


def downgrade() -> None:
    op.drop_table("backup_auth_enrollments")
    op.drop_table("backup_auth_credentials")

    op.drop_constraint(
        "ck_refresh_tokens_authentication_assurance",
        "refresh_tokens",
        type_="check",
    )
    op.drop_constraint(
        "ck_refresh_tokens_backup_auth_version",
        "refresh_tokens",
        type_="check",
    )
    op.drop_constraint(
        "ck_refresh_tokens_authentication_method",
        "refresh_tokens",
        type_="check",
    )
    op.drop_column("refresh_tokens", "backup_auth_version")
    op.drop_column("refresh_tokens", "backup_reauthenticated_at")
    op.drop_column("refresh_tokens", "backup_verified_at")
    op.drop_column("refresh_tokens", "webauthn_verified_at")
    op.drop_column("refresh_tokens", "authentication_method")

    op.drop_constraint("ck_users_backup_auth_version", "users", type_="check")
    op.drop_column("users", "backup_auth_version")
