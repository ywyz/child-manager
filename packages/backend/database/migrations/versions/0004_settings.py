"""建立 M3 首期必要设置 Schema。"""

from collections.abc import Sequence
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_settings"
down_revision: str | None = "0003_passkey_contract"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

AGE_GROUPS = (
    ("toddler", "托班", 0),
    ("small", "小班", 1),
    ("middle", "中班", 2),
    ("large", "大班", 3),
)


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
    age_groups = op.create_table(
        "age_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "kindergarten_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("kindergartens.id"),
            nullable=False,
        ),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_age_groups_kindergarten_id_id"),
        sa.UniqueConstraint("kindergarten_id", "code", name="uq_age_groups_kindergarten_code"),
        sa.UniqueConstraint("kindergarten_id", "name", name="uq_age_groups_kindergarten_name"),
        sa.CheckConstraint("sort_order >= 0", name="ck_age_groups_sort_order"),
    )

    op.create_table(
        "classes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("name_normalized", sa.String(120), nullable=False),
        sa.Column("age_group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_classes_kindergarten_id_id"),
        sa.UniqueConstraint(
            "kindergarten_id", "name_normalized", name="uq_classes_kindergarten_name"
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "age_group_id"],
            ["age_groups.kindergarten_id", "age_groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"], ["users.kindergarten_id", "users.id"]
        ),
    )
    op.create_index(
        "ix_classes_active_name",
        "classes",
        ["kindergarten_id", "is_active", "name_normalized"],
    )

    op.create_table(
        "class_teachers",
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("is_lead_teacher", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "class_id"], ["classes.kindergarten_id", "classes.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "assigned_by"], ["users.kindergarten_id", "users.id"]
        ),
    )
    op.create_index(
        "uq_class_teachers_lead",
        "class_teachers",
        ["kindergarten_id", "class_id"],
        unique=True,
        postgresql_where=sa.text("is_lead_teacher"),
    )
    op.create_index(
        "ix_class_teachers_user",
        "class_teachers",
        ["kindergarten_id", "user_id", "class_id"],
    )

    op.create_table(
        "semesters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "kindergarten_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("kindergartens.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_semesters_kindergarten_id_id"),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint("start_date <= end_date", name="ck_semesters_date_range"),
        sa.CheckConstraint("NOT is_current OR is_active", name="ck_semesters_current_active"),
    )
    op.create_index(
        "uq_semesters_current",
        "semesters",
        ["kindergarten_id"],
        unique=True,
        postgresql_where=sa.text("is_current"),
    )
    op.create_index(
        "ix_semesters_dates",
        "semesters",
        ["kindergarten_id", "start_date", "end_date"],
    )
    op.execute(
        """ALTER TABLE semesters
        ADD CONSTRAINT ex_semesters_active_date_range
        EXCLUDE USING gist (
            kindergarten_id WITH =,
            daterange(start_date, end_date, '[]') WITH &&
        ) WHERE (is_active)"""
    )

    op.create_table(
        "class_areas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("area_type", sa.String(16), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("name_normalized", sa.String(120), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_class_areas_kindergarten_id_id"),
        sa.UniqueConstraint(
            "kindergarten_id",
            "class_id",
            "area_type",
            "name_normalized",
            name="uq_class_areas_kindergarten_class_type_name",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "class_id"], ["classes.kindergarten_id", "classes.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint("area_type IN ('indoor','outdoor')", name="ck_class_areas_type"),
        sa.CheckConstraint("sort_order >= 0", name="ck_class_areas_sort_order"),
    )
    op.create_index(
        "ix_class_areas_active_order",
        "class_areas",
        ["kindergarten_id", "class_id", "area_type", "is_active", "sort_order"],
    )

    kindergarten_ids = op.get_bind().execute(sa.text("SELECT id FROM kindergartens")).scalars()
    op.bulk_insert(
        age_groups,
        [
            {
                "id": uuid5(NAMESPACE_URL, f"child-manager:{kindergarten_id}:age-group:{code}"),
                "kindergarten_id": kindergarten_id,
                "code": code,
                "name": name,
                "sort_order": sort_order,
                "is_active": True,
            }
            for kindergarten_id in kindergarten_ids
            for code, name, sort_order in AGE_GROUPS
        ],
    )


def downgrade() -> None:
    op.drop_table("class_areas")
    op.drop_table("semesters")
    op.drop_table("class_teachers")
    op.drop_table("classes")
    op.drop_table("age_groups")
