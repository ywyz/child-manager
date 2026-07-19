"""refresh token family absolute expiration

Revision ID: 0003_refresh_family
Revises: 0002_updated_at
Create Date: 2026-07-17 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_refresh_family"
down_revision: str | None = "0002_updated_at"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "refresh_tokens",
        sa.Column("family_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE refresh_tokens
        SET family_expires_at = expires_at
        WHERE family_expires_at IS NULL
        """
    )
    op.alter_column(
        "refresh_tokens",
        "family_expires_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("refresh_tokens", "family_expires_at")
