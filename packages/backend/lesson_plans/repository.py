"""园所范围教案 PostgreSQL Repository。"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid7

from psycopg.types.json import Jsonb


@dataclass(frozen=True, slots=True)
class PlanCreationContext:
    kindergarten_name: str
    class_name: str
    age_group_name: str
    semester_id: UUID
    semester_name: str
    semester_start_date: date
    semester_end_date: date


@dataclass(frozen=True, slots=True)
class AuthorRecord:
    user_id: UUID
    sort_order: int
    display_name_snapshot: str


@dataclass(frozen=True, slots=True)
class PlanRecord:
    id: UUID
    kindergarten_id: UUID
    class_id: UUID
    semester_id: UUID
    plan_date: date
    kindergarten_name_snapshot: str
    class_name_snapshot: str
    age_group_name_snapshot: str
    semester_name_snapshot: str
    semester_start_date_snapshot: date
    semester_end_date_snapshot: date
    teaching_week_number: int | None
    teaching_week_text: str | None
    activity_date_text: str
    season_code: str
    content: dict[str, Any]
    content_schema_version: int
    version: int
    archived_at: datetime | None


@dataclass(frozen=True, slots=True)
class SnapshotRecord:
    id: UUID
    plan_id: UUID
    plan_version: int
    reason_code: str
    context_snapshot: dict[str, Any]
    content: dict[str, Any]
    content_schema_version: int
    content_sha256: str
    created_by: UUID | None
    created_at: datetime


_PLAN_COLUMNS = """id, kindergarten_id, class_id, semester_id, plan_date,
    kindergarten_name_snapshot, class_name_snapshot, age_group_name_snapshot,
    semester_name_snapshot, semester_start_date_snapshot, semester_end_date_snapshot,
    teaching_week_number, teaching_week_text, activity_date_text, season_code,
    content, content_schema_version, version, archived_at"""


def _plan(row: Sequence[object] | None) -> PlanRecord | None:
    if row is None:
        return None
    return PlanRecord(
        id=UUID(str(row[0])),
        kindergarten_id=UUID(str(row[1])),
        class_id=UUID(str(row[2])),
        semester_id=UUID(str(row[3])),
        plan_date=row[4],  # type: ignore[arg-type]
        kindergarten_name_snapshot=str(row[5]),
        class_name_snapshot=str(row[6]),
        age_group_name_snapshot=str(row[7]),
        semester_name_snapshot=str(row[8]),
        semester_start_date_snapshot=row[9],  # type: ignore[arg-type]
        semester_end_date_snapshot=row[10],  # type: ignore[arg-type]
        teaching_week_number=int(str(row[11])) if row[11] is not None else None,
        teaching_week_text=str(row[12]) if row[12] is not None else None,
        activity_date_text=str(row[13]),
        season_code=str(row[14]),
        content=dict(row[15]),  # type: ignore[arg-type]
        content_schema_version=int(str(row[16])),
        version=int(str(row[17])),
        archived_at=row[18],  # type: ignore[arg-type]
    )


class LessonPlanRepository:
    """所有方法都显式接收并在 SQL 中使用 ``kindergarten_id``。"""

    def __init__(self, connection: object) -> None:
        self._connection = connection

    def creation_context(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
    ) -> PlanCreationContext | None:
        row = self._connection.execute(  # type: ignore[attr-defined]
            """SELECT k.name, c.name, age.name, s.id, s.name, s.start_date, s.end_date
            FROM kindergartens k
            JOIN classes c ON c.kindergarten_id=k.id AND c.id=%s AND c.is_active
            JOIN age_groups age
              ON age.kindergarten_id=c.kindergarten_id AND age.id=c.age_group_id
            JOIN semesters s ON s.kindergarten_id=k.id AND s.is_current AND s.is_active
            WHERE k.id=%s AND k.is_active""",
            (class_id, kindergarten_id),
        ).fetchone()
        if row is None:
            return None
        return PlanCreationContext(
            kindergarten_name=str(row[0]),
            class_name=str(row[1]),
            age_group_name=str(row[2]),
            semester_id=UUID(str(row[3])),
            semester_name=str(row[4]),
            semester_start_date=row[5],  # type: ignore[arg-type]
            semester_end_date=row[6],  # type: ignore[arg-type]
        )

    def class_exists(self, kindergarten_id: UUID, class_id: UUID) -> bool:
        return (
            self._connection.execute(  # type: ignore[attr-defined]
                "SELECT 1 FROM classes WHERE kindergarten_id=%s AND id=%s AND is_active",
                (kindergarten_id, class_id),
            ).fetchone()
            is not None
        )

    def is_class_teacher(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        user_id: UUID,
    ) -> bool:
        return (
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT 1 FROM class_teachers ct
                JOIN classes c
                  ON c.kindergarten_id=ct.kindergarten_id AND c.id=ct.class_id
                JOIN users u
                  ON u.kindergarten_id=ct.kindergarten_id AND u.id=ct.user_id
                JOIN user_roles ur
                  ON ur.kindergarten_id=u.kindergarten_id AND ur.user_id=u.id
                JOIN roles r ON r.id=ur.role_id AND r.code='teacher'
                WHERE ct.kindergarten_id=%s AND ct.class_id=%s AND ct.user_id=%s
                  AND c.is_active AND u.status='active'""",
                (kindergarten_id, class_id, user_id),
            ).fetchone()
            is not None
        )

    def create_plan(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        plan_date: date,
        *,
        context: PlanCreationContext,
        teaching_week_number: int | None,
        teaching_week_text: str | None,
        activity_date_text: str,
        season_code: str,
        content: dict[str, Any],
        actor_id: UUID,
    ) -> tuple[PlanRecord, bool]:
        row = self._connection.execute(  # type: ignore[attr-defined]
            f"""INSERT INTO daily_activity_plans
            (id, kindergarten_id, class_id, semester_id, plan_date,
             kindergarten_name_snapshot, class_name_snapshot, age_group_name_snapshot,
             semester_name_snapshot, semester_start_date_snapshot, semester_end_date_snapshot,
             teaching_week_number, teaching_week_text, activity_date_text, season_code,
             content, content_schema_version, version, created_by, updated_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,1,%s,%s)
            ON CONFLICT (kindergarten_id, class_id, plan_date) DO NOTHING
            RETURNING {_PLAN_COLUMNS}""",
            (
                uuid7(),
                kindergarten_id,
                class_id,
                context.semester_id,
                plan_date,
                context.kindergarten_name,
                context.class_name,
                context.age_group_name,
                context.semester_name,
                context.semester_start_date,
                context.semester_end_date,
                teaching_week_number,
                teaching_week_text,
                activity_date_text,
                season_code,
                Jsonb(content),
                actor_id,
                actor_id,
            ),
        ).fetchone()
        plan = _plan(row)
        if plan is None:
            plan = self.get_plan_by_class_date(kindergarten_id, class_id, plan_date)
            assert plan is not None
            return plan, False
        assert plan is not None
        return plan, True

    def get_plan(self, kindergarten_id: UUID, plan_id: UUID) -> PlanRecord | None:
        row = self._connection.execute(  # type: ignore[attr-defined]
            f"""SELECT {_PLAN_COLUMNS} FROM daily_activity_plans
            WHERE kindergarten_id=%s AND id=%s""",
            (kindergarten_id, plan_id),
        ).fetchone()
        return _plan(row)

    def get_plan_by_class_date(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        plan_date: date,
    ) -> PlanRecord | None:
        row = self._connection.execute(  # type: ignore[attr-defined]
            f"""SELECT {_PLAN_COLUMNS} FROM daily_activity_plans
            WHERE kindergarten_id=%s AND class_id=%s AND plan_date=%s""",
            (kindergarten_id, class_id, plan_date),
        ).fetchone()
        return _plan(row)

    def list_plans(
        self,
        kindergarten_id: UUID,
        *,
        class_id: UUID | None,
        date_from: date | None,
        date_to: date | None,
        author_id: UUID | None,
        archived: bool | None,
        visible_to_user_id: UUID | None,
        page: int,
        page_size: int,
    ) -> tuple[list[PlanRecord], int]:
        rows = self._connection.execute(  # type: ignore[attr-defined]
            f"""SELECT {_PLAN_COLUMNS}, count(*) OVER()
            FROM daily_activity_plans p
            WHERE p.kindergarten_id=%s
              AND (%s::uuid IS NULL OR p.class_id=%s)
              AND (%s::date IS NULL OR p.plan_date>=%s)
              AND (%s::date IS NULL OR p.plan_date<=%s)
              AND (%s::boolean IS NULL OR (p.archived_at IS NOT NULL)=%s)
              AND (
                %s::uuid IS NULL OR EXISTS (
                  SELECT 1 FROM daily_activity_plan_authors a
                  WHERE a.kindergarten_id=p.kindergarten_id AND a.plan_id=p.id
                    AND a.user_id=%s
                )
              )
              AND (
                %s::uuid IS NULL OR EXISTS (
                  SELECT 1 FROM class_teachers ct
                  JOIN classes c
                    ON c.kindergarten_id=ct.kindergarten_id AND c.id=ct.class_id
                  JOIN users u
                    ON u.kindergarten_id=ct.kindergarten_id AND u.id=ct.user_id
                  JOIN user_roles ur
                    ON ur.kindergarten_id=u.kindergarten_id AND ur.user_id=u.id
                  JOIN roles r ON r.id=ur.role_id AND r.code='teacher'
                  WHERE ct.kindergarten_id=p.kindergarten_id
                    AND ct.class_id=p.class_id AND ct.user_id=%s
                    AND c.is_active AND u.status='active'
                )
              )
            ORDER BY p.plan_date DESC, p.id
            LIMIT %s OFFSET %s""",
            (
                kindergarten_id,
                class_id,
                class_id,
                date_from,
                date_from,
                date_to,
                date_to,
                archived,
                archived,
                author_id,
                author_id,
                visible_to_user_id,
                visible_to_user_id,
                page_size,
                (page - 1) * page_size,
            ),
        ).fetchall()
        plans: list[PlanRecord] = []
        for row in rows:
            plan = _plan(row[:19])
            if plan is not None:
                plans.append(plan)
        return plans, int(rows[0][19]) if rows else 0

    def list_authors(self, kindergarten_id: UUID, plan_id: UUID) -> list[AuthorRecord]:
        rows = self._connection.execute(  # type: ignore[attr-defined]
            """SELECT user_id, sort_order, display_name_snapshot
            FROM daily_activity_plan_authors
            WHERE kindergarten_id=%s AND plan_id=%s
            ORDER BY sort_order, user_id""",
            (kindergarten_id, plan_id),
        ).fetchall()
        return [
            AuthorRecord(
                user_id=UUID(str(row[0])),
                sort_order=int(str(row[1])),
                display_name_snapshot=str(row[2]),
            )
            for row in rows
        ]

    def list_authors_for_plans(
        self,
        kindergarten_id: UUID,
        plan_ids: Sequence[UUID],
    ) -> dict[UUID, list[AuthorRecord]]:
        if not plan_ids:
            return {}
        rows = self._connection.execute(  # type: ignore[attr-defined]
            """SELECT plan_id, user_id, sort_order, display_name_snapshot
            FROM daily_activity_plan_authors
            WHERE kindergarten_id=%s AND plan_id=ANY(%s)
            ORDER BY plan_id, sort_order, user_id""",
            (kindergarten_id, list(plan_ids)),
        ).fetchall()
        result = {plan_id: [] for plan_id in plan_ids}
        for row in rows:
            result[UUID(str(row[0]))].append(
                AuthorRecord(
                    user_id=UUID(str(row[1])),
                    sort_order=int(str(row[2])),
                    display_name_snapshot=str(row[3]),
                )
            )
        return result

    def associated_class_ids(
        self,
        kindergarten_id: UUID,
        user_id: UUID,
        class_ids: Sequence[UUID],
    ) -> set[UUID]:
        if not class_ids:
            return set()
        rows = self._connection.execute(  # type: ignore[attr-defined]
            """SELECT DISTINCT ct.class_id
            FROM class_teachers ct
            JOIN classes c
              ON c.kindergarten_id=ct.kindergarten_id AND c.id=ct.class_id
            JOIN users u
              ON u.kindergarten_id=ct.kindergarten_id AND u.id=ct.user_id
            JOIN user_roles ur
              ON ur.kindergarten_id=u.kindergarten_id AND ur.user_id=u.id
            JOIN roles r ON r.id=ur.role_id AND r.code='teacher'
            WHERE ct.kindergarten_id=%s AND ct.user_id=%s
              AND ct.class_id=ANY(%s) AND c.is_active AND u.status='active'""",
            (kindergarten_id, user_id, list(class_ids)),
        ).fetchall()
        return {UUID(str(row[0])) for row in rows}

    def resolve_author_names(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        plan_id: UUID,
        user_ids: Sequence[UUID],
    ) -> dict[UUID, str]:
        if not user_ids:
            return {}
        rows = self._connection.execute(  # type: ignore[attr-defined]
            """SELECT u.id, COALESCE(existing.display_name_snapshot, u.display_name)
            FROM users u
            LEFT JOIN daily_activity_plan_authors existing
              ON existing.kindergarten_id=u.kindergarten_id
             AND existing.plan_id=%s AND existing.user_id=u.id
            WHERE u.kindergarten_id=%s AND u.id=ANY(%s)
              AND (
                existing.user_id IS NOT NULL OR (
                  u.status='active' AND EXISTS (
                    SELECT 1 FROM class_teachers ct
                    WHERE ct.kindergarten_id=u.kindergarten_id
                      AND ct.class_id=%s AND ct.user_id=u.id
                  )
                )
              )""",
            (plan_id, kindergarten_id, list(user_ids), class_id),
        ).fetchall()
        return {UUID(str(row[0])): str(row[1]) for row in rows}

    def replace_authors(
        self,
        kindergarten_id: UUID,
        plan_id: UUID,
        authors: Sequence[tuple[UUID, int, str]],
        *,
        actor_id: UUID,
    ) -> None:
        self._connection.execute(  # type: ignore[attr-defined]
            "DELETE FROM daily_activity_plan_authors WHERE kindergarten_id=%s AND plan_id=%s",
            (kindergarten_id, plan_id),
        )
        for user_id, sort_order, display_name in authors:
            self._connection.execute(  # type: ignore[attr-defined]
                """INSERT INTO daily_activity_plan_authors
                (kindergarten_id, plan_id, user_id, display_name_snapshot, sort_order, added_by)
                VALUES (%s,%s,%s,%s,%s,%s)""",
                (
                    kindergarten_id,
                    plan_id,
                    user_id,
                    display_name,
                    sort_order,
                    actor_id,
                ),
            )

    def update_content(
        self,
        kindergarten_id: UUID,
        plan_id: UUID,
        *,
        expected_version: int,
        content: dict[str, Any],
        actor_id: UUID,
    ) -> PlanRecord | None:
        row = self._connection.execute(  # type: ignore[attr-defined]
            f"""UPDATE daily_activity_plans
            SET content=%s, version=version+1, updated_by=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND version=%s AND archived_at IS NULL
            RETURNING {_PLAN_COLUMNS}""",
            (Jsonb(content), actor_id, kindergarten_id, plan_id, expected_version),
        ).fetchone()
        return _plan(row)

    def set_archived(
        self,
        kindergarten_id: UUID,
        plan_id: UUID,
        *,
        expected_version: int,
        archived: bool,
        actor_id: UUID,
    ) -> PlanRecord | None:
        if archived:
            assignment = "archived_at=now(), archived_by=%s"
        else:
            assignment = "archived_at=NULL, archived_by=NULL"
        params: list[object] = [actor_id] if archived else []
        params.extend([actor_id, kindergarten_id, plan_id, expected_version])
        expected_state = "archived_at IS NULL" if archived else "archived_at IS NOT NULL"
        row = self._connection.execute(  # type: ignore[attr-defined]
            f"""UPDATE daily_activity_plans
            SET {assignment}, version=version+1, updated_by=%s, updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND version=%s AND {expected_state}
            RETURNING {_PLAN_COLUMNS}""",
            params,
        ).fetchone()
        return _plan(row)

    def add_snapshot(
        self,
        kindergarten_id: UUID,
        plan_id: UUID,
        *,
        plan_version: int,
        reason_code: str,
        context_snapshot: dict[str, Any],
        content: dict[str, Any],
        content_schema_version: int,
        content_sha256: str,
        created_by: UUID | None,
    ) -> SnapshotRecord:
        row = self._connection.execute(  # type: ignore[attr-defined]
            """INSERT INTO daily_activity_plan_snapshots
            (id, kindergarten_id, plan_id, plan_version, reason_code, context_snapshot,
             content, content_schema_version, content_sha256, created_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id, plan_id, plan_version, reason_code, context_snapshot, content,
                      content_schema_version, content_sha256, created_by, created_at""",
            (
                uuid7(),
                kindergarten_id,
                plan_id,
                plan_version,
                reason_code,
                Jsonb(context_snapshot),
                Jsonb(content),
                content_schema_version,
                content_sha256,
                created_by,
            ),
        ).fetchone()
        assert row is not None
        return self._snapshot(row)

    def get_snapshot(
        self,
        kindergarten_id: UUID,
        plan_id: UUID,
        snapshot_id: UUID,
    ) -> SnapshotRecord | None:
        row = self._connection.execute(  # type: ignore[attr-defined]
            """SELECT id, plan_id, plan_version, reason_code, context_snapshot, content,
                      content_schema_version, content_sha256, created_by, created_at
            FROM daily_activity_plan_snapshots
            WHERE kindergarten_id=%s AND plan_id=%s AND id=%s""",
            (kindergarten_id, plan_id, snapshot_id),
        ).fetchone()
        return self._snapshot(row) if row is not None else None

    def list_snapshots(
        self,
        kindergarten_id: UUID,
        plan_id: UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[SnapshotRecord], int]:
        rows = self._connection.execute(  # type: ignore[attr-defined]
            """SELECT id, plan_id, plan_version, reason_code, context_snapshot, content,
                      content_schema_version, content_sha256, created_by, created_at,
                      count(*) OVER()
            FROM daily_activity_plan_snapshots
            WHERE kindergarten_id=%s AND plan_id=%s
            ORDER BY created_at DESC, id DESC
            LIMIT %s OFFSET %s""",
            (kindergarten_id, plan_id, page_size, (page - 1) * page_size),
        ).fetchall()
        return ([self._snapshot(row[:10]) for row in rows], int(rows[0][10]) if rows else 0)

    @staticmethod
    def _snapshot(row: Sequence[object]) -> SnapshotRecord:
        return SnapshotRecord(
            id=UUID(str(row[0])),
            plan_id=UUID(str(row[1])),
            plan_version=int(str(row[2])),
            reason_code=str(row[3]),
            context_snapshot=dict(row[4]),  # type: ignore[arg-type]
            content=dict(row[5]),  # type: ignore[arg-type]
            content_schema_version=int(str(row[6])),
            content_sha256=str(row[7]),
            created_by=UUID(str(row[8])) if row[8] is not None else None,
            created_at=row[9],  # type: ignore[arg-type]
        )
