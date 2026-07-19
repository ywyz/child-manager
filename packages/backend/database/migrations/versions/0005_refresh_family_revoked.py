"""add family_revoked_at to refresh_tokens

Revision ID: 0005_refresh_family_revoked
Revises: 0004_refresh_token_fk
Create Date: 2026-07-18 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_refresh_family_revoked"
down_revision: str | None = "0004_refresh_token_fk"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "refresh_tokens",
        sa.Column("family_revoked_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("refresh_tokens", "family_revoked_at")
