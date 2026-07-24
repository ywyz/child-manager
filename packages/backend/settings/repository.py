"""园所范围设置的 PostgreSQL Repository。"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5, uuid7


@dataclass(frozen=True, slots=True)
class KindergartenRecord:
    id: UUID
    name: str
    timezone: str
    is_active: bool


@dataclass(frozen=True, slots=True)
class AgeGroupRecord:
    id: UUID
    code: str
    name: str
    sort_order: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class SemesterRecord:
    id: UUID
    name: str
    start_date: date
    end_date: date
    is_current: bool
    is_active: bool


@dataclass(frozen=True, slots=True)
class TeacherRecord:
    user_id: UUID
    display_name: str
    is_lead_teacher: bool


@dataclass(frozen=True, slots=True)
class ClassRecord:
    id: UUID
    name: str
    age_group_id: UUID
    age_group_name: str
    is_active: bool
    teachers: tuple[TeacherRecord, ...]
    indoor_areas_configured: bool
    outdoor_areas_configured: bool


@dataclass(frozen=True, slots=True)
class AreaRecord:
    id: UUID
    class_id: UUID
    area_type: str
    name: str
    sort_order: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class AreaInput:
    id: UUID | None
    name: str
    name_normalized: str
    sort_order: int
    is_active: bool


@dataclass(frozen=True, slots=True)
class TeacherInput:
    user_id: UUID
    is_lead_teacher: bool


AGE_GROUPS = (
    ("toddler", "托班", 0),
    ("small", "小班", 1),
    ("middle", "中班", 2),
    ("large", "大班", 3),
)


def _rows(result: Any) -> list[tuple[object, ...]]:
    return list(result.fetchall()) if result is not None else []


def _row(result: Any) -> tuple[object, ...] | None:
    return result.fetchone() if result is not None else None


class SettingsRepository:
    """所有读写都在 SQL 中显式携带 ``kindergarten_id``。"""

    def __init__(self, connection: object) -> None:
        self._connection = connection

    def ensure_age_groups(self, kindergarten_id: UUID) -> None:
        for code, name, sort_order in AGE_GROUPS:
            self._connection.execute(  # type: ignore[attr-defined]
                """INSERT INTO age_groups
                (id, kindergarten_id, code, name, sort_order, is_active)
                VALUES (%s,%s,%s,%s,%s,true)
                ON CONFLICT (kindergarten_id, code) DO NOTHING""",
                (
                    uuid5(NAMESPACE_URL, f"child-manager:{kindergarten_id}:age-group:{code}"),
                    kindergarten_id,
                    code,
                    name,
                    sort_order,
                ),
            )

    def get_kindergarten(self, kindergarten_id: UUID) -> KindergartenRecord | None:
        row = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT id, name, timezone, is_active
                FROM kindergartens WHERE id=%s AND id=%s""",
                (kindergarten_id, kindergarten_id),
            )
        )
        if row is None:
            return None
        return KindergartenRecord(
            id=UUID(str(row[0])),
            name=str(row[1]),
            timezone=str(row[2]),
            is_active=bool(row[3]),
        )

    def update_kindergarten(
        self,
        kindergarten_id: UUID,
        *,
        name: str,
    ) -> KindergartenRecord | None:
        row = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """UPDATE kindergartens
                SET name=%s, updated_at=now()
                WHERE id=%s
                RETURNING id, name, timezone, is_active""",
                (name, kindergarten_id),
            )
        )
        if row is None:
            return None
        return KindergartenRecord(
            id=UUID(str(row[0])),
            name=str(row[1]),
            timezone=str(row[2]),
            is_active=bool(row[3]),
        )

    def list_age_groups(self, kindergarten_id: UUID) -> list[AgeGroupRecord]:
        rows = _rows(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT id, code, name, sort_order, is_active
                FROM age_groups
                WHERE kindergarten_id=%s
                ORDER BY sort_order""",
                (kindergarten_id,),
            )
        )
        return [
            AgeGroupRecord(
                id=UUID(str(row[0])),
                code=str(row[1]),
                name=str(row[2]),
                sort_order=int(str(row[3])),
                is_active=bool(row[4]),
            )
            for row in rows
        ]

    def list_semesters(
        self,
        kindergarten_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[SemesterRecord], int]:
        rows = _rows(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT id, name, start_date, end_date, is_current, is_active,
                          count(*) OVER()
                FROM semesters
                WHERE kindergarten_id=%s
                ORDER BY start_date DESC, id
                LIMIT %s OFFSET %s""",
                (kindergarten_id, page_size, (page - 1) * page_size),
            )
        )
        return (
            [
                SemesterRecord(
                    id=UUID(str(row[0])),
                    name=str(row[1]),
                    start_date=row[2],  # type: ignore[arg-type]
                    end_date=row[3],  # type: ignore[arg-type]
                    is_current=bool(row[4]),
                    is_active=bool(row[5]),
                )
                for row in rows
            ],
            int(str(rows[0][6])) if rows else 0,
        )

    def get_semester(
        self,
        kindergarten_id: UUID,
        semester_id: UUID,
    ) -> SemesterRecord | None:
        row = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT id, name, start_date, end_date, is_current, is_active
                FROM semesters
                WHERE kindergarten_id=%s AND id=%s""",
                (kindergarten_id, semester_id),
            )
        )
        return self._semester(row)

    def create_semester(
        self,
        kindergarten_id: UUID,
        *,
        name: str,
        start_date: date,
        end_date: date,
        is_active: bool,
        actor_id: UUID,
    ) -> SemesterRecord:
        row = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """INSERT INTO semesters
                (id, kindergarten_id, name, start_date, end_date, is_current, is_active,
                 created_by, updated_by)
                VALUES (%s,%s,%s,%s,%s,false,%s,%s,%s)
                RETURNING id, name, start_date, end_date, is_current, is_active""",
                (
                    uuid7(),
                    kindergarten_id,
                    name,
                    start_date,
                    end_date,
                    is_active,
                    actor_id,
                    actor_id,
                ),
            )
        )
        assert row is not None
        semester = self._semester(row)
        assert semester is not None
        return semester

    def update_semester(
        self,
        kindergarten_id: UUID,
        semester_id: UUID,
        *,
        name: str,
        start_date: date,
        end_date: date,
        is_active: bool,
        actor_id: UUID,
    ) -> SemesterRecord | None:
        row = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """UPDATE semesters
                SET name=%s, start_date=%s, end_date=%s, is_active=%s,
                    updated_by=%s, updated_at=now()
                WHERE kindergarten_id=%s AND id=%s
                RETURNING id, name, start_date, end_date, is_current, is_active""",
                (
                    name,
                    start_date,
                    end_date,
                    is_active,
                    actor_id,
                    kindergarten_id,
                    semester_id,
                ),
            )
        )
        return self._semester(row)

    def make_current_semester(
        self,
        kindergarten_id: UUID,
        semester_id: UUID,
        *,
        actor_id: UUID,
    ) -> SemesterRecord | None:
        target = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT id FROM semesters
                WHERE kindergarten_id=%s AND id=%s AND is_active
                FOR UPDATE""",
                (kindergarten_id, semester_id),
            )
        )
        if target is None:
            return None
        self._connection.execute(  # type: ignore[attr-defined]
            """UPDATE semesters
            SET is_current=false, updated_by=%s, updated_at=now()
            WHERE kindergarten_id=%s AND is_current AND id<>%s""",
            (actor_id, kindergarten_id, semester_id),
        )
        row = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """UPDATE semesters
                SET is_current=true, updated_by=%s, updated_at=now()
                WHERE kindergarten_id=%s AND id=%s
                RETURNING id, name, start_date, end_date, is_current, is_active""",
                (actor_id, kindergarten_id, semester_id),
            )
        )
        return self._semester(row)

    def list_classes(
        self,
        kindergarten_id: UUID,
        *,
        user_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ClassRecord], int]:
        rows = _rows(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT c.id, c.name, c.age_group_id, age.name, c.is_active,
                          EXISTS (
                              SELECT 1 FROM class_areas indoor
                              WHERE indoor.kindergarten_id=c.kindergarten_id
                                AND indoor.class_id=c.id
                                AND indoor.area_type='indoor'
                                AND indoor.is_active
                          ),
                          EXISTS (
                              SELECT 1 FROM class_areas outdoor
                              WHERE outdoor.kindergarten_id=c.kindergarten_id
                                AND outdoor.class_id=c.id
                                AND outdoor.area_type='outdoor'
                                AND outdoor.is_active
                          ),
                          count(*) OVER()
                FROM classes c
                JOIN age_groups age
                  ON age.kindergarten_id=c.kindergarten_id AND age.id=c.age_group_id
                WHERE c.kindergarten_id=%s
                  AND (
                    %s::uuid IS NULL
                    OR (
                      c.is_active
                      AND EXISTS (
                        SELECT 1 FROM class_teachers relation
                        WHERE relation.kindergarten_id=c.kindergarten_id
                          AND relation.class_id=c.id
                          AND relation.user_id=%s
                      )
                    )
                  )
                ORDER BY c.name_normalized, c.id
                LIMIT %s OFFSET %s""",
                (
                    kindergarten_id,
                    user_id,
                    user_id,
                    page_size,
                    (page - 1) * page_size,
                ),
            )
        )
        records = [self._class(kindergarten_id, row) for row in rows]
        return records, int(str(rows[0][7])) if rows else 0

    def get_class(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        *,
        user_id: UUID | None = None,
    ) -> ClassRecord | None:
        row = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT c.id, c.name, c.age_group_id, age.name, c.is_active,
                          EXISTS (
                              SELECT 1 FROM class_areas indoor
                              WHERE indoor.kindergarten_id=c.kindergarten_id
                                AND indoor.class_id=c.id
                                AND indoor.area_type='indoor'
                                AND indoor.is_active
                          ),
                          EXISTS (
                              SELECT 1 FROM class_areas outdoor
                              WHERE outdoor.kindergarten_id=c.kindergarten_id
                                AND outdoor.class_id=c.id
                                AND outdoor.area_type='outdoor'
                                AND outdoor.is_active
                          )
                FROM classes c
                JOIN age_groups age
                  ON age.kindergarten_id=c.kindergarten_id AND age.id=c.age_group_id
                WHERE c.kindergarten_id=%s AND c.id=%s
                  AND (
                    %s::uuid IS NULL
                    OR (
                      c.is_active
                      AND EXISTS (
                        SELECT 1 FROM class_teachers relation
                        WHERE relation.kindergarten_id=c.kindergarten_id
                          AND relation.class_id=c.id
                          AND relation.user_id=%s
                      )
                    )
                  )""",
                (kindergarten_id, class_id, user_id, user_id),
            )
        )
        return self._class(kindergarten_id, row) if row is not None else None

    def create_class(
        self,
        kindergarten_id: UUID,
        *,
        name: str,
        name_normalized: str,
        age_group_id: UUID,
        is_active: bool,
        actor_id: UUID,
    ) -> ClassRecord:
        class_id = uuid7()
        self._connection.execute(  # type: ignore[attr-defined]
            """INSERT INTO classes
            (id, kindergarten_id, name, name_normalized, age_group_id, is_active,
             created_by, updated_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                class_id,
                kindergarten_id,
                name,
                name_normalized,
                age_group_id,
                is_active,
                actor_id,
                actor_id,
            ),
        )
        record = self.get_class(kindergarten_id, class_id)
        assert record is not None
        return record

    def update_class(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        *,
        name: str,
        name_normalized: str,
        age_group_id: UUID,
        is_active: bool,
        actor_id: UUID,
    ) -> ClassRecord | None:
        row = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """UPDATE classes
                SET name=%s, name_normalized=%s, age_group_id=%s, is_active=%s,
                    updated_by=%s, updated_at=now()
                WHERE kindergarten_id=%s AND id=%s
                RETURNING id""",
                (
                    name,
                    name_normalized,
                    age_group_id,
                    is_active,
                    actor_id,
                    kindergarten_id,
                    class_id,
                ),
            )
        )
        return self.get_class(kindergarten_id, class_id) if row is not None else None

    def replace_class_teachers(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        teachers: Sequence[TeacherInput],
        actor_id: UUID,
    ) -> ClassRecord | None:
        existing = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT id FROM classes
                WHERE kindergarten_id=%s AND id=%s FOR UPDATE""",
                (kindergarten_id, class_id),
            )
        )
        if existing is None:
            return None
        self._connection.execute(  # type: ignore[attr-defined]
            """DELETE FROM class_teachers
            WHERE kindergarten_id=%s AND class_id=%s""",
            (kindergarten_id, class_id),
        )
        for teacher in teachers:
            self._connection.execute(  # type: ignore[attr-defined]
                """INSERT INTO class_teachers
                (kindergarten_id, class_id, user_id, is_lead_teacher, assigned_by, assigned_at)
                VALUES (%s,%s,%s,%s,%s,now())""",
                (
                    kindergarten_id,
                    class_id,
                    teacher.user_id,
                    teacher.is_lead_teacher,
                    actor_id,
                ),
            )
        return self.get_class(kindergarten_id, class_id)

    def teacher_role_user_ids(
        self,
        kindergarten_id: UUID,
        user_ids: Sequence[UUID],
    ) -> set[UUID]:
        if not user_ids:
            return set()
        ordered_user_ids = sorted(set(user_ids), key=str)
        self._connection.execute(  # type: ignore[attr-defined]
            """SELECT id FROM users
            WHERE kindergarten_id=%s AND id=ANY(%s::uuid[])
            ORDER BY id FOR UPDATE""",
            (kindergarten_id, ordered_user_ids),
        )
        rows = _rows(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT DISTINCT users.id
                FROM users
                JOIN user_roles
                  ON user_roles.kindergarten_id=users.kindergarten_id
                 AND user_roles.user_id=users.id
                JOIN roles
                  ON roles.id=user_roles.role_id
                 AND roles.code='teacher'
                WHERE users.kindergarten_id=%s
                  AND users.id=ANY(%s::uuid[])""",
                (kindergarten_id, ordered_user_ids),
            )
        )
        return {UUID(str(row[0])) for row in rows}

    def is_class_teacher(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        user_id: UUID,
    ) -> bool:
        row = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT EXISTS (
                    SELECT 1 FROM class_teachers relation
                    JOIN classes class_record
                      ON class_record.kindergarten_id=relation.kindergarten_id
                     AND class_record.id=relation.class_id
                    WHERE relation.kindergarten_id=%s
                      AND relation.class_id=%s
                      AND relation.user_id=%s
                      AND class_record.is_active
                )""",
                (kindergarten_id, class_id, user_id),
            )
        )
        return bool(row and row[0])

    def has_class_assignments(
        self,
        kindergarten_id: UUID,
        user_id: UUID,
    ) -> bool:
        row = _row(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT EXISTS (
                    SELECT 1 FROM class_teachers relation
                    JOIN classes class_record
                      ON class_record.kindergarten_id=relation.kindergarten_id
                     AND class_record.id=relation.class_id
                    WHERE relation.kindergarten_id=%s
                      AND relation.user_id=%s
                      AND class_record.is_active
                )""",
                (kindergarten_id, user_id),
            )
        )
        return bool(row and row[0])

    def list_class_areas(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        area_type: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AreaRecord], int]:
        rows = _rows(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT id, class_id, area_type, name, sort_order, is_active,
                          count(*) OVER()
                FROM class_areas
                WHERE kindergarten_id=%s AND class_id=%s AND area_type=%s
                ORDER BY sort_order, id
                LIMIT %s OFFSET %s""",
                (
                    kindergarten_id,
                    class_id,
                    area_type,
                    page_size,
                    (page - 1) * page_size,
                ),
            )
        )
        return (
            [
                AreaRecord(
                    id=UUID(str(row[0])),
                    class_id=UUID(str(row[1])),
                    area_type=str(row[2]),
                    name=str(row[3]),
                    sort_order=int(str(row[4])),
                    is_active=bool(row[5]),
                )
                for row in rows
            ],
            int(str(rows[0][6])) if rows else 0,
        )

    def replace_class_areas(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        area_type: str,
        names: Sequence[str | AreaInput],
        actor_id: UUID,
    ) -> None:
        existing = _rows(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT id, name_normalized
                FROM class_areas
                WHERE kindergarten_id=%s AND class_id=%s AND area_type=%s
                FOR UPDATE""",
                (kindergarten_id, class_id, area_type),
            )
        )
        existing_by_id = {UUID(str(row[0])): str(row[1]) for row in existing}
        existing_by_name = {str(row[1]): UUID(str(row[0])) for row in existing}
        retained_ids: list[UUID] = []

        for sort_order, value in enumerate(names):
            area = (
                AreaInput(
                    id=None,
                    name=value,
                    name_normalized=value.casefold(),
                    sort_order=sort_order,
                    is_active=True,
                )
                if isinstance(value, str)
                else value
            )
            if area.id is not None and area.id not in existing_by_id:
                raise ValueError("区域标识不属于当前班级和类别")
            area_id = area.id or existing_by_name.get(area.name_normalized)
            if area_id is None:
                area_id = uuid7()
                self._connection.execute(  # type: ignore[attr-defined]
                    """INSERT INTO class_areas
                    (id, kindergarten_id, class_id, area_type, name, name_normalized,
                     sort_order, is_active, created_by, updated_by)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        area_id,
                        kindergarten_id,
                        class_id,
                        area_type,
                        area.name,
                        area.name_normalized,
                        area.sort_order,
                        area.is_active,
                        actor_id,
                        actor_id,
                    ),
                )
            else:
                self._connection.execute(  # type: ignore[attr-defined]
                    """UPDATE class_areas
                    SET name=%s, name_normalized=%s, sort_order=%s, is_active=%s,
                        updated_by=%s, updated_at=now()
                    WHERE kindergarten_id=%s AND class_id=%s AND area_type=%s AND id=%s""",
                    (
                        area.name,
                        area.name_normalized,
                        area.sort_order,
                        area.is_active,
                        actor_id,
                        kindergarten_id,
                        class_id,
                        area_type,
                        area_id,
                    ),
                )
            retained_ids.append(area_id)

        self._connection.execute(  # type: ignore[attr-defined]
            """UPDATE class_areas
            SET is_active=false, updated_by=%s, updated_at=now()
            WHERE kindergarten_id=%s AND class_id=%s AND area_type=%s
              AND NOT (id=ANY(%s::uuid[]))""",
            (actor_id, kindergarten_id, class_id, area_type, retained_ids),
        )

    @staticmethod
    def _semester(row: tuple[object, ...] | None) -> SemesterRecord | None:
        if row is None:
            return None
        return SemesterRecord(
            id=UUID(str(row[0])),
            name=str(row[1]),
            start_date=row[2],  # type: ignore[arg-type]
            end_date=row[3],  # type: ignore[arg-type]
            is_current=bool(row[4]),
            is_active=bool(row[5]),
        )

    def _class(self, kindergarten_id: UUID, row: tuple[object, ...]) -> ClassRecord:
        class_id = UUID(str(row[0]))
        teachers = _rows(
            self._connection.execute(  # type: ignore[attr-defined]
                """SELECT relation.user_id, users.display_name, relation.is_lead_teacher
                FROM class_teachers relation
                JOIN users
                  ON users.kindergarten_id=relation.kindergarten_id
                 AND users.id=relation.user_id
                WHERE relation.kindergarten_id=%s AND relation.class_id=%s
                ORDER BY relation.is_lead_teacher DESC, users.display_name, relation.user_id""",
                (kindergarten_id, class_id),
            )
        )
        return ClassRecord(
            id=class_id,
            name=str(row[1]),
            age_group_id=UUID(str(row[2])),
            age_group_name=str(row[3]),
            is_active=bool(row[4]),
            teachers=tuple(
                TeacherRecord(
                    user_id=UUID(str(teacher[0])),
                    display_name=str(teacher[1]),
                    is_lead_teacher=bool(teacher[2]),
                )
                for teacher in teachers
            ),
            indoor_areas_configured=bool(row[5]),
            outdoor_areas_configured=bool(row[6]),
        )
