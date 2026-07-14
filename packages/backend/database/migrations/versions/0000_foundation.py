"""建立 M1 迁移基线，不创建业务表。"""

from collections.abc import Sequence

revision: str = "0000_foundation"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """记录空的工程基础 revision。"""


def downgrade() -> None:
    """移除空的工程基础 revision。"""
