"""foundation

Revision ID: 0000_foundation
Revises:
Create Date: 2026-07-15 00:00:00.000000

"""

from collections.abc import Sequence

revision: str = "0000_foundation"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
