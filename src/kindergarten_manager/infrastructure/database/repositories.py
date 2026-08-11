"""Slice 1 具体 SQLite repositories。"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from kindergarten_manager.application.lesson_plans import (
    LessonPlanEditorState,
    LessonPlanError,
    SaveResult,
)
from kindergarten_manager.application.settings import SettingsError
from kindergarten_manager.application.workspace import (
    ClassContext,
    PlanExportRecord,
    SetupContextRecord,
)
from kindergarten_manager.domain.calendar import evaluate_calendar
from kindergarten_manager.domain.content import PlanContentV1
from kindergarten_manager.infrastructure.database.engine import create_session_factory

DatabaseSource = Path | sessionmaker[Session]


class SettingsRepository:
    def __init__(self, database: DatabaseSource) -> None:
        self.session_factory = _session_factory(database)
        self._session: Session | None = None

    @contextmanager
    def transaction(self) -> Iterator[None]:
        if self._session is not None:
            yield
            return
        with self.session_factory.begin() as session:
            self._session = session
            try:
                yield
            finally:
                self._session = None

    def upsert_profile(self, teacher_name: str, theme: str, now_utc_ms: int) -> dict[str, object]:
        row = (
            self._execute(
                """
            INSERT INTO app_profile(
                id, application_id, teacher_display_name, theme,
                last_daily_backup_date, created_at_utc_ms, updated_at_utc_ms
            ) VALUES (1, 'cn.kindergartenmanager.desktop', ?, ?, NULL, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                teacher_display_name = excluded.teacher_display_name,
                theme = excluded.theme,
                updated_at_utc_ms = excluded.updated_at_utc_ms
            RETURNING teacher_display_name, theme
            """,
                (teacher_name, theme, now_utc_ms, now_utc_ms),
            )
            .mappings()
            .one()
        )
        return dict(row)

    def upsert_kindergarten(self, name: str, now_utc_ms: int) -> dict[str, object]:
        row = (
            self._execute(
                """
            INSERT INTO kindergarten_settings(
                id, name, timezone, created_at_utc_ms, updated_at_utc_ms
            ) VALUES (1, ?, 'Asia/Shanghai', ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                updated_at_utc_ms = excluded.updated_at_utc_ms
            RETURNING name, timezone
            """,
                (name, now_utc_ms, now_utc_ms),
            )
            .mappings()
            .one()
        )
        return dict(row)

    def upsert_semester(self, values: dict[str, object]) -> dict[str, object]:
        if values["is_current"]:
            self._execute("UPDATE semesters SET is_current = 0 WHERE is_current = 1")
        semester_id = values.get("id")
        now_utc_ms = int(str(values["now_utc_ms"]))
        parameters = (
            str(values["name"]),
            str(values["start_date"]),
            str(values["end_date"]),
            int(bool(values["is_current"])),
            now_utc_ms,
        )
        if semester_id is None:
            row = (
                self._execute(
                    """
                INSERT INTO semesters(
                    name, start_date, end_date, is_current,
                    created_at_utc_ms, updated_at_utc_ms
                ) VALUES (?, ?, ?, ?, ?, ?)
                RETURNING id, name, start_date, end_date, is_current
                """,
                    (*parameters, now_utc_ms),
                )
                .mappings()
                .first()
            )
        else:
            row = (
                self._execute(
                    """
                UPDATE semesters SET
                    name = ?, start_date = ?, end_date = ?, is_current = ?, updated_at_utc_ms = ?
                WHERE id = ?
                RETURNING id, name, start_date, end_date, is_current
                """,
                    (*parameters, int(str(semester_id))),
                )
                .mappings()
                .first()
            )
        if row is None:
            raise SettingsError("settings.semester_not_found", "学期不存在")
        return dict(row)

    def upsert_class(self, values: dict[str, object]) -> dict[str, object]:
        class_id = values.get("id")
        now_utc_ms = int(str(values["now_utc_ms"]))
        try:
            if class_id is None:
                row = (
                    self._execute(
                        """
                    INSERT INTO class_groups(
                        name, age_group, sort_order, is_active,
                        created_at_utc_ms, updated_at_utc_ms
                    ) VALUES (?, ?, 0, 1, ?, ?)
                    RETURNING id, name, age_group
                    """,
                        (str(values["name"]), str(values["age_group"]), now_utc_ms, now_utc_ms),
                    )
                    .mappings()
                    .first()
                )
            else:
                row = (
                    self._execute(
                        """
                    UPDATE class_groups SET name = ?, age_group = ?, updated_at_utc_ms = ?
                    WHERE id = ?
                    RETURNING id, name, age_group
                    """,
                        (
                            str(values["name"]),
                            str(values["age_group"]),
                            now_utc_ms,
                            int(str(class_id)),
                        ),
                    )
                    .mappings()
                    .first()
                )
        except IntegrityError as error:
            raise SettingsError("settings.class_name_conflict", "班级名称已存在") from error
        if row is None:
            raise SettingsError("settings.class_not_found", "班级不存在")
        saved = dict(row)
        saved.update(indoor_areas=(), outdoor_areas=())
        return saved

    def replace_class_areas(
        self,
        class_id: int,
        indoor: tuple[str, ...],
        outdoor: tuple[str, ...],
        now_utc_ms: int,
    ) -> dict[str, object]:
        connection = self._require_session().connection()
        row = (
            connection.exec_driver_sql(
                "SELECT id, name, age_group FROM class_groups WHERE id = ?", (class_id,)
            )
            .mappings()
            .first()
        )
        if row is None:
            raise SettingsError("settings.class_not_found", "班级不存在")
        connection.exec_driver_sql("DELETE FROM class_areas WHERE class_id = ?", (class_id,))
        try:
            for area_type, names in (("indoor", indoor), ("outdoor", outdoor)):
                if names:
                    connection.exec_driver_sql(
                        """
                        INSERT INTO class_areas(
                            class_id, area_type, name, sort_order,
                            created_at_utc_ms, updated_at_utc_ms
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        [
                            (class_id, area_type, name, index, now_utc_ms, now_utc_ms)
                            for index, name in enumerate(names)
                        ],
                    )
        except IntegrityError as error:
            raise SettingsError("settings.area_name_conflict", "班级区域名称重复") from error
        saved = dict(row)
        saved.update(indoor_areas=indoor, outdoor_areas=outdoor)
        return saved

    def _execute(
        self,
        sql: str,
        parameters: tuple[object, ...] = (),
    ) -> CursorResult[Any]:
        return self._require_session().connection().exec_driver_sql(sql, parameters)

    def _require_session(self) -> Session:
        if self._session is None:
            raise RuntimeError("SQLite 设置写入必须位于事务中")
        return self._session


class LessonPlanRepository:
    def __init__(self, database: DatabaseSource) -> None:
        self.session_factory = _session_factory(database)

    def open_or_create(
        self,
        *,
        class_id: int,
        semester_id: int,
        plan_date: date,
        author_name: str,
        now_utc_ms: int,
    ) -> LessonPlanEditorState:
        empty = PlanContentV1.empty()
        try:
            with self.session_factory.begin() as session:
                connection = session.connection()
                connection.exec_driver_sql(
                    """
                    INSERT INTO lesson_plans(
                        class_id, semester_id, plan_date, author_name,
                        content_schema_version, content_json, content_revision,
                        created_at_utc_ms, updated_at_utc_ms
                    ) VALUES (?, ?, ?, ?, 1, ?, 1, ?, ?)
                    ON CONFLICT(class_id, plan_date) DO NOTHING
                    """,
                    (
                        class_id,
                        semester_id,
                        plan_date.isoformat(),
                        author_name,
                        empty.canonical_json(),
                        now_utc_ms,
                        now_utc_ms,
                    ),
                )
                row = (
                    connection.exec_driver_sql(
                        """
                    SELECT id, class_id, semester_id, plan_date, author_name,
                           content_revision, content_json
                    FROM lesson_plans WHERE class_id = ? AND plan_date = ?
                    """,
                        (class_id, plan_date.isoformat()),
                    )
                    .mappings()
                    .first()
                )
                warnings = _calendar_warnings(connection, plan_date, semester_id)
        except IntegrityError as error:
            raise LessonPlanError("plan.invalid_context", "班级或学期不存在") from error
        if row is None:
            raise LessonPlanError("plan.not_found", "教案不存在")
        return _lesson_plan_state(row, warnings)

    def save_content(
        self,
        *,
        plan_id: int,
        base_revision: int,
        content: PlanContentV1,
        now_utc_ms: int,
    ) -> SaveResult:
        with self.session_factory.begin() as session:
            result = session.connection().exec_driver_sql(
                """
                UPDATE lesson_plans SET
                    content_schema_version = 1,
                    content_json = ?,
                    content_revision = content_revision + 1,
                    updated_at_utc_ms = ?
                WHERE id = ? AND content_revision = ? AND archived_at_utc_ms IS NULL
                """,
                (content.canonical_json(), now_utc_ms, plan_id, base_revision),
            )
            if result.rowcount != 1:
                raise LessonPlanError("plan.stale_editor_state", "教案已发生变化，请重新加载")
        return SaveResult(
            plan_id=plan_id,
            content_revision=base_revision + 1,
            saved_at_utc_ms=now_utc_ms,
        )


class WorkspaceRepository:
    """为 Application workspace 提供冻结的 SQLite 读取记录。"""

    def __init__(self, database: DatabaseSource) -> None:
        self.session_factory = _session_factory(database)

    def load_setup_context(self) -> SetupContextRecord | None:
        with self.session_factory() as session:
            connection = session.connection()
            setup = (
                connection.exec_driver_sql(
                    """
                SELECT p.teacher_display_name, p.theme,
                       s.id AS semester_id, s.name AS semester_name,
                       s.start_date, s.end_date
                FROM app_profile AS p
                CROSS JOIN semesters AS s
                WHERE s.is_current = 1
                LIMIT 1
                """
                )
                .mappings()
                .first()
            )
            classes = (
                connection.exec_driver_sql(
                    """
                SELECT id, name FROM class_groups
                WHERE is_active = 1
                ORDER BY sort_order, id
                """
                )
                .mappings()
                .all()
            )
        if setup is None or not classes:
            return None
        return SetupContextRecord(
            teacher_name=str(setup["teacher_display_name"]),
            theme=str(setup["theme"]),
            semester_id=int(setup["semester_id"]),
            semester_name=str(setup["semester_name"]),
            semester_start_date=date.fromisoformat(str(setup["start_date"])),
            semester_end_date=date.fromisoformat(str(setup["end_date"])),
            classes=tuple(
                ClassContext(id=int(row["id"]), name=str(row["name"])) for row in classes
            ),
        )

    def get_author_name(self) -> str:
        with self.session_factory() as session:
            row = (
                session.connection()
                .exec_driver_sql("SELECT teacher_display_name FROM app_profile WHERE id = 1")
                .first()
            )
        return str(row[0]) if row is not None else ""

    def load_export_record(self, plan_id: int) -> PlanExportRecord | None:
        with self.session_factory() as session:
            row = (
                session.connection()
                .exec_driver_sql(
                    """
                SELECT p.id, p.content_revision, p.plan_date, p.author_name, p.content_json,
                       c.name AS class_name, c.age_group,
                       s.name AS semester_name, s.start_date, s.end_date,
                       k.name AS kindergarten_name
                FROM lesson_plans AS p
                JOIN class_groups AS c ON c.id = p.class_id
                JOIN semesters AS s ON s.id = p.semester_id
                CROSS JOIN kindergarten_settings AS k
                WHERE p.id = ?
                """,
                    (plan_id,),
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        return PlanExportRecord(
            plan_id=int(row["id"]),
            content_revision=int(row["content_revision"]),
            plan_date=date.fromisoformat(str(row["plan_date"])),
            author_name=str(row["author_name"]),
            content_json=str(row["content_json"]),
            class_name=str(row["class_name"]),
            age_group=str(row["age_group"]),
            semester_name=str(row["semester_name"]),
            semester_start_date=date.fromisoformat(str(row["start_date"])),
            semester_end_date=date.fromisoformat(str(row["end_date"])),
            kindergarten_name=str(row["kindergarten_name"]),
        )


def _session_factory(database: DatabaseSource) -> sessionmaker[Session]:
    return create_session_factory(database) if isinstance(database, Path) else database


def _lesson_plan_state(
    row: Mapping[Any, object],
    warnings: tuple[str, ...] = (),
) -> LessonPlanEditorState:
    return LessonPlanEditorState(
        id=int(str(row["id"])),
        class_id=int(str(row["class_id"])),
        semester_id=int(str(row["semester_id"])),
        plan_date=date.fromisoformat(str(row["plan_date"])),
        author_name=str(row["author_name"]),
        content_revision=int(str(row["content_revision"])),
        content=PlanContentV1.model_validate(json.loads(str(row["content_json"]))),
        warnings=warnings,
    )


def _calendar_warnings(
    connection: Connection,
    plan_date: date,
    semester_id: int,
) -> tuple[str, ...]:
    columns = {
        str(row[1]) for row in connection.exec_driver_sql("PRAGMA table_info(semesters)").fetchall()
    }
    if not {"start_date", "end_date"} <= columns:
        return ()
    semester = (
        connection.exec_driver_sql(
            "SELECT start_date, end_date FROM semesters WHERE id = ?",
            (semester_id,),
        )
        .mappings()
        .first()
    )
    if semester is None:
        return ()
    evaluation = evaluate_calendar(
        plan_date,
        semester_start=date.fromisoformat(str(semester["start_date"])),
        semester_end=date.fromisoformat(str(semester["end_date"])),
    )
    return evaluation.warnings
