"""首期必要设置的 SQLAlchemy 模型。"""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from packages.backend.database.base import Base


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AgeGroup(Timestamped, Base):
    __tablename__ = "age_groups"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("kindergartens.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_age_groups_kindergarten_id_id"),
        UniqueConstraint("kindergarten_id", "code", name="uq_age_groups_kindergarten_code"),
        UniqueConstraint("kindergarten_id", "name", name="uq_age_groups_kindergarten_name"),
        CheckConstraint("sort_order >= 0", name="ck_age_groups_sort_order"),
    )


class ClassRoom(Timestamped, Base):
    __tablename__ = "classes"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    name_normalized: Mapped[str] = mapped_column(String(120), nullable=False)
    age_group_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    updated_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_classes_kindergarten_id_id"),
        UniqueConstraint("kindergarten_id", "name_normalized", name="uq_classes_kindergarten_name"),
        ForeignKeyConstraint(
            ["kindergarten_id", "age_group_id"],
            ["age_groups.kindergarten_id", "age_groups.id"],
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"], ["users.kindergarten_id", "users.id"]
        ),
        Index("ix_classes_active_name", "kindergarten_id", "is_active", "name_normalized"),
    )


class ClassTeacher(Timestamped, Base):
    __tablename__ = "class_teachers"

    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    class_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    is_lead_teacher: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    assigned_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["kindergarten_id", "class_id"], ["classes.kindergarten_id", "classes.id"]
        ),
        ForeignKeyConstraint(["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]),
        ForeignKeyConstraint(
            ["kindergarten_id", "assigned_by"], ["users.kindergarten_id", "users.id"]
        ),
        Index(
            "uq_class_teachers_lead",
            "kindergarten_id",
            "class_id",
            unique=True,
            postgresql_where=text("is_lead_teacher"),
        ),
        Index(
            "ix_class_teachers_user",
            "kindergarten_id",
            "user_id",
            "class_id",
        ),
    )


class Semester(Timestamped, Base):
    __tablename__ = "semesters"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    updated_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_semesters_kindergarten_id_id"),
        ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"], ["users.kindergarten_id", "users.id"]
        ),
        CheckConstraint("start_date <= end_date", name="ck_semesters_date_range"),
        CheckConstraint("NOT is_current OR is_active", name="ck_semesters_current_active"),
        ExcludeConstraint(
            ("kindergarten_id", "="),
            (func.daterange(start_date, end_date, "[]"), "&&"),
            where=text("is_active"),
            using="gist",
            name="ex_semesters_active_date_range",
        ),
        Index(
            "uq_semesters_current",
            "kindergarten_id",
            unique=True,
            postgresql_where=text("is_current"),
        ),
        Index("ix_semesters_dates", "kindergarten_id", "start_date", "end_date"),
    )


class ClassArea(Timestamped, Base):
    __tablename__ = "class_areas"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    class_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    area_type: Mapped[str] = mapped_column(String(16), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    name_normalized: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    updated_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_class_areas_kindergarten_id_id"),
        UniqueConstraint(
            "kindergarten_id",
            "class_id",
            "area_type",
            "name_normalized",
            name="uq_class_areas_kindergarten_class_type_name",
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "class_id"], ["classes.kindergarten_id", "classes.id"]
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"], ["users.kindergarten_id", "users.id"]
        ),
        CheckConstraint("area_type IN ('indoor','outdoor')", name="ck_class_areas_type"),
        CheckConstraint("sort_order >= 0", name="ck_class_areas_sort_order"),
        Index(
            "ix_class_areas_active_order",
            "kindergarten_id",
            "class_id",
            "area_type",
            "is_active",
            "sort_order",
        ),
    )
