"""refresh token composite foreign key

Revision ID: 0004_refresh_token_fk
Revises: 0003_refresh_family
Create Date: 2026-07-18 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "0004_refresh_token_fk"
down_revision: str | None = "0003_refresh_family"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_refresh_tokens_user",
        "refresh_tokens",
        "users",
        ["kindergarten_id", "user_id"],
        ["kindergarten_id", "id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_refresh_tokens_user", "refresh_tokens", type_="foreignkey")
