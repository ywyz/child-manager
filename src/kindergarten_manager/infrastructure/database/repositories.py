"""Slice 1 具体 SQLite repositories。"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy.engine import Connection, CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from kindergarten_manager.application.ai_generation import AdoptionCandidate
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
from kindergarten_manager.domain.ai import canonical_json, validate_section_output
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


class AiRepositoryError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class AiConfigurationRecord:
    base_url: str | None
    model_name: str | None
    credential_configured: bool
    enabled: bool
    vision_base_url: str | None
    vision_model_name: str | None
    vision_credential_configured: bool
    vision_enabled: bool


@dataclass(frozen=True, slots=True)
class AiPreviewRecord:
    id: int
    lesson_plan_id: int
    operation_id: str
    section_code: str
    result: dict[str, Any]
    frozen_input_sha256: str
    target_section_sha256: str
    status: str


class AiRepository:
    """持久化非敏感 AI 配置和已校验预览；API Key 从不进入此接口。"""

    def __init__(self, database: DatabaseSource) -> None:
        self.session_factory = _session_factory(database)

    def get_configuration(self) -> AiConfigurationRecord | None:
        with self.session_factory() as session:
            row = (
                session.connection()
                .exec_driver_sql(
                    "SELECT base_url, model_name, credential_configured, enabled, "
                    "vision_base_url, vision_model_name, "
                    "vision_credential_configured, vision_enabled "
                    "FROM ai_configuration WHERE id = 1"
                )
                .mappings()
                .first()
            )
        return _configuration_record(row) if row is not None else None

    def content_for_plan(self, plan_id: int) -> dict[str, Any]:
        with self.session_factory() as session:
            row = (
                session.connection()
                .exec_driver_sql(
                    "SELECT content_json FROM lesson_plans WHERE id = ?",
                    (plan_id,),
                )
                .first()
            )
        if row is None:
            raise AiRepositoryError("plan.not_found", "教案不存在")
        return PlanContentV1.model_validate(json.loads(str(row[0]))).model_dump(mode="json")

    def save_configuration(
        self,
        *,
        base_url: str | None,
        model_name: str | None,
        credential_configured: bool,
        enabled: bool,
        now_utc_ms: int,
    ) -> AiConfigurationRecord:
        with self.session_factory.begin() as session:
            row = _write_ai_configuration(
                session.connection(),
                base_url=base_url,
                model_name=model_name,
                credential_configured=credential_configured,
                enabled=enabled,
                now_utc_ms=now_utc_ms,
            )
        return _configuration_record(row)

    @contextmanager
    def settings_transaction(
        self,
        now_utc_ms: int,
    ) -> Iterator[_SqliteAiSettingsTransaction]:
        with self.session_factory.begin() as session:
            yield _SqliteAiSettingsTransaction(
                session.connection(),
                now_utc_ms=now_utc_ms,
            )

    def get_prompt_override(self, prompt_code: str) -> str | None:
        with self.session_factory() as session:
            row = (
                session.connection()
                .exec_driver_sql(
                    "SELECT content FROM prompt_overrides WHERE prompt_code = ?",
                    (prompt_code,),
                )
                .first()
            )
        return str(row[0]) if row is not None else None

    def set_prompt_override(self, prompt_code: str, content: str, *, now_utc_ms: int) -> None:
        with self.session_factory.begin() as session:
            session.connection().exec_driver_sql(
                """
                INSERT INTO prompt_overrides(prompt_code, content, updated_at_utc_ms)
                VALUES (?, ?, ?)
                ON CONFLICT(prompt_code) DO UPDATE SET
                    content = excluded.content,
                    updated_at_utc_ms = excluded.updated_at_utc_ms
                """,
                (prompt_code, content, now_utc_ms),
            )

    def delete_prompt_override(self, prompt_code: str) -> None:
        with self.session_factory.begin() as session:
            session.connection().exec_driver_sql(
                "DELETE FROM prompt_overrides WHERE prompt_code = ?",
                (prompt_code,),
            )

    def create_preview(
        self,
        *,
        lesson_plan_id: int,
        operation_id: str,
        section_code: str,
        result: object,
        frozen_input_sha256: str,
        target_section_sha256: str,
        now_utc_ms: int,
    ) -> AiPreviewRecord:
        validated = validate_section_output(section_code, result)
        result_json = canonical_json(validated)
        with self.session_factory.begin() as session:
            row = (
                session.connection()
                .exec_driver_sql(
                    """
                    INSERT INTO ai_previews(
                        lesson_plan_id, operation_id, section_code, result_schema_code,
                        result_json, frozen_input_sha256, target_section_sha256,
                        state, created_at_utc_ms, decided_at_utc_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ready', ?, NULL)
                    RETURNING id, lesson_plan_id, operation_id, section_code, result_json,
                              frozen_input_sha256, target_section_sha256, state
                    """,
                    (
                        lesson_plan_id,
                        operation_id,
                        section_code,
                        section_code,
                        result_json,
                        frozen_input_sha256,
                        target_section_sha256,
                        now_utc_ms,
                    ),
                )
                .mappings()
                .one()
            )
        return _preview_record(row)

    def get_preview(self, preview_id: int) -> AiPreviewRecord | None:
        with self.session_factory() as session:
            row = (
                session.connection()
                .exec_driver_sql(
                    """
                    SELECT id, lesson_plan_id, operation_id, section_code, result_json,
                           frozen_input_sha256, target_section_sha256, state
                    FROM ai_previews WHERE id = ?
                    """,
                    (preview_id,),
                )
                .mappings()
                .first()
            )
        return _preview_record(row) if row is not None else None

    def reject_preview(self, preview_id: int, *, now_utc_ms: int) -> AiPreviewRecord:
        return self._decide_preview(preview_id, "rejected", now_utc_ms)

    @contextmanager
    def adoption_transaction(
        self,
        preview_id: int,
        *,
        now_utc_ms: int,
    ) -> Iterator[_SqliteAiAdoptionTransaction]:
        with self.session_factory.begin() as session:
            yield _SqliteAiAdoptionTransaction(
                session.connection(),
                preview_id=preview_id,
                now_utc_ms=now_utc_ms,
            )

    def _decide_preview(
        self,
        preview_id: int,
        state: str,
        now_utc_ms: int,
    ) -> AiPreviewRecord:
        with self.session_factory.begin() as session:
            row = (
                session.connection()
                .exec_driver_sql(
                    """
                    UPDATE ai_previews SET state = ?, decided_at_utc_ms = ?
                    WHERE id = ? AND state = 'ready'
                    RETURNING id, lesson_plan_id, operation_id, section_code, result_json,
                              frozen_input_sha256, target_section_sha256, state
                    """,
                    (state, now_utc_ms, preview_id),
                )
                .mappings()
                .first()
            )
        if row is None:
            raise AiRepositoryError("ai.preview_not_ready", "AI 预览不存在或已处理")
        return _preview_record(row)


class _SqliteAiSettingsTransaction:
    def __init__(self, connection: Connection, *, now_utc_ms: int) -> None:
        self._connection = connection
        self._now_utc_ms = now_utc_ms

    def save_configuration(
        self,
        *,
        base_url: str | None,
        model_name: str | None,
        credential_configured: bool,
        enabled: bool,
    ) -> None:
        _write_ai_configuration(
            self._connection,
            base_url=base_url,
            model_name=model_name,
            credential_configured=credential_configured,
            enabled=enabled,
            now_utc_ms=self._now_utc_ms,
        )

    def save_vision_configuration(
        self,
        *,
        base_url: str | None,
        model_name: str | None,
        credential_configured: bool,
        enabled: bool,
    ) -> None:
        self._connection.exec_driver_sql(
            """
            UPDATE ai_configuration SET
                vision_base_url = ?,
                vision_model_name = ?,
                vision_credential_configured = ?,
                vision_enabled = ?,
                updated_at_utc_ms = ?
            WHERE id = 1
            """,
            (
                base_url,
                model_name,
                int(credential_configured),
                int(enabled),
                self._now_utc_ms,
            ),
        )

    def set_prompt_override(self, prompt_code: str, content: str) -> None:
        self._connection.exec_driver_sql(
            """
            INSERT INTO prompt_overrides(prompt_code, content, updated_at_utc_ms)
            VALUES (?, ?, ?)
            ON CONFLICT(prompt_code) DO UPDATE SET
                content = excluded.content,
                updated_at_utc_ms = excluded.updated_at_utc_ms
            """,
            (prompt_code, content, self._now_utc_ms),
        )

    def delete_prompt_override(self, prompt_code: str) -> None:
        self._connection.exec_driver_sql(
            "DELETE FROM prompt_overrides WHERE prompt_code = ?",
            (prompt_code,),
        )


class _SqliteAiAdoptionTransaction:
    def __init__(self, connection: Connection, *, preview_id: int, now_utc_ms: int) -> None:
        self._connection = connection
        self._preview_id = preview_id
        self._now_utc_ms = now_utc_ms
        self._candidate: AdoptionCandidate | None = None

    def load_candidate(self) -> AdoptionCandidate:
        row = (
            self._connection.exec_driver_sql(
                """
                SELECT v.section_code, v.result_json, v.target_section_sha256,
                       v.state, p.id AS plan_id, p.author_name, p.content_schema_version,
                       p.content_json, p.content_revision, p.archived_at_utc_ms
                FROM ai_previews AS v
                JOIN lesson_plans AS p ON p.id = v.lesson_plan_id
                WHERE v.id = ?
                """,
                (self._preview_id,),
            )
            .mappings()
            .first()
        )
        if row is None:
            raise AiRepositoryError("ai.preview_not_found", "AI 预览不存在")
        if row["state"] != "ready":
            raise AiRepositoryError("ai.preview_not_ready", "AI 预览已处理")
        result = json.loads(str(row["result_json"]))
        if not isinstance(result, dict):
            raise AiRepositoryError("ai.preview_corrupt", "AI 预览数据已损坏")
        content = PlanContentV1.model_validate(json.loads(str(row["content_json"])))
        self._candidate = AdoptionCandidate(
            plan_id=int(row["plan_id"]),
            section_code=str(row["section_code"]),
            result=result,
            target_section_sha256=str(row["target_section_sha256"]),
            author_name=str(row["author_name"]),
            content_schema_version=int(row["content_schema_version"]),
            content=content.model_dump(mode="json"),
            content_revision=int(row["content_revision"]),
            archived=row["archived_at_utc_ms"] is not None,
        )
        return self._candidate

    def invalidate(self) -> None:
        self._connection.exec_driver_sql(
            "UPDATE ai_previews SET state = 'invalidated', decided_at_utc_ms = ? "
            "WHERE id = ? AND state = 'ready'",
            (self._now_utc_ms, self._preview_id),
        )

    def save_snapshot(self) -> None:
        candidate = self._require_candidate()
        self._connection.exec_driver_sql(
            """
            INSERT INTO lesson_plan_versions(
                lesson_plan_id, reason, description, author_name,
                content_schema_version, content_json, source_revision, created_at_utc_ms
            ) VALUES (?, 'pre_ai_adopt', NULL, ?, ?, ?, ?, ?)
            """,
            (
                candidate.plan_id,
                candidate.author_name,
                candidate.content_schema_version,
                canonical_json(candidate.content),
                candidate.content_revision,
                self._now_utc_ms,
            ),
        )

    def update_content(self, content: Mapping[str, object]) -> int:
        candidate = self._require_candidate()
        updated = PlanContentV1.model_validate(content)
        result = self._connection.exec_driver_sql(
            """
            UPDATE lesson_plans SET
                content_json = ?, content_revision = content_revision + 1,
                updated_at_utc_ms = ?
            WHERE id = ? AND content_revision = ? AND archived_at_utc_ms IS NULL
            """,
            (
                updated.canonical_json(),
                self._now_utc_ms,
                candidate.plan_id,
                candidate.content_revision,
            ),
        )
        if result.rowcount != 1:
            raise AiRepositoryError("ai.preview_stale", "教案已变化，预览不可采用")
        return candidate.content_revision + 1

    def mark_adopted(self) -> None:
        result = self._connection.exec_driver_sql(
            "UPDATE ai_previews SET state = 'adopted', decided_at_utc_ms = ? "
            "WHERE id = ? AND state = 'ready'",
            (self._now_utc_ms, self._preview_id),
        )
        if result.rowcount != 1:
            raise AiRepositoryError("ai.preview_not_ready", "AI 预览已处理")

    def _require_candidate(self) -> AdoptionCandidate:
        if self._candidate is None:
            raise RuntimeError("必须先读取采用候选")
        return self._candidate


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
                SELECT p.teacher_display_name, p.theme, k.name AS kindergarten_name,
                       s.id AS semester_id, s.name AS semester_name,
                       s.start_date, s.end_date
                FROM app_profile AS p
                CROSS JOIN kindergarten_settings AS k
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
                SELECT id, name, age_group FROM class_groups
                WHERE is_active = 1
                ORDER BY sort_order, id
                """
                )
                .mappings()
                .all()
            )
            areas = (
                connection.exec_driver_sql(
                    """
                SELECT class_id, area_type, name FROM class_areas
                ORDER BY class_id, area_type, sort_order, id
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
                ClassContext(
                    id=int(row["id"]),
                    name=str(row["name"]),
                    age_group=str(row["age_group"]),
                    indoor_areas=tuple(
                        str(area["name"])
                        for area in areas
                        if int(area["class_id"]) == int(row["id"]) and area["area_type"] == "indoor"
                    ),
                    outdoor_areas=tuple(
                        str(area["name"])
                        for area in areas
                        if int(area["class_id"]) == int(row["id"])
                        and area["area_type"] == "outdoor"
                    ),
                )
                for row in classes
            ),
            kindergarten_name=str(setup["kindergarten_name"]),
        )

    def get_author_name(self) -> str:
        with self.session_factory() as session:
            row = (
                session.connection()
                .exec_driver_sql("SELECT teacher_display_name FROM app_profile WHERE id = 1")
                .first()
            )
        return str(row[0]) if row is not None else ""

    def load_tool_plan(self, plan_id: int) -> dict[str, object] | None:
        with self.session_factory() as session:
            row = (
                session.connection()
                .exec_driver_sql(
                    "SELECT id, class_id, semester_id, plan_date, content_revision, content_json "
                    "FROM lesson_plans WHERE id = ?",
                    (plan_id,),
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        return {
            "plan_id": int(row["id"]),
            "class_id": int(row["class_id"]),
            "semester_id": int(row["semester_id"]),
            "plan_date": str(row["plan_date"]),
            "content_revision": int(row["content_revision"]),
            "content": json.loads(str(row["content_json"])),
        }

    def load_tool_context(self, plan_id: int) -> dict[str, object] | None:
        with self.session_factory() as session:
            row = (
                session.connection()
                .exec_driver_sql(
                    """
                SELECT p.id, p.plan_date, p.content_revision,
                       c.id AS class_id, c.name AS class_name, c.age_group,
                       s.id AS semester_id, s.name AS semester_name,
                       s.start_date, s.end_date
                FROM lesson_plans AS p
                JOIN class_groups AS c ON c.id = p.class_id
                JOIN semesters AS s ON s.id = p.semester_id
                WHERE p.id = ?
                """,
                    (plan_id,),
                )
                .mappings()
                .first()
            )
        if row is None:
            return None
        return {
            "plan_id": int(row["id"]),
            "plan_date": str(row["plan_date"]),
            "content_revision": int(row["content_revision"]),
            "class_id": int(row["class_id"]),
            "class_name": str(row["class_name"]),
            "age_group": str(row["age_group"]),
            "semester_id": int(row["semester_id"]),
            "semester_name": str(row["semester_name"]),
            "start_date": str(row["start_date"]),
            "end_date": str(row["end_date"]),
        }

    def load_tool_semester(self, semester_id: int) -> tuple[date, date] | None:
        with self.session_factory() as session:
            row = (
                session.connection()
                .exec_driver_sql(
                    "SELECT start_date, end_date FROM semesters WHERE id = ?",
                    (semester_id,),
                )
                .first()
            )
        if row is None:
            return None
        return date.fromisoformat(str(row[0])), date.fromisoformat(str(row[1]))

    def load_tool_class_areas(self, class_id: int) -> tuple[dict[str, object], ...]:
        with self.session_factory() as session:
            rows = (
                session.connection()
                .exec_driver_sql(
                    "SELECT area_type, name FROM class_areas "
                    "WHERE class_id = ? ORDER BY area_type, sort_order, id",
                    (class_id,),
                )
                .mappings()
                .all()
            )
        return tuple(dict(row) for row in rows)

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


def _configuration_record(row: Mapping[Any, object]) -> AiConfigurationRecord:
    return AiConfigurationRecord(
        base_url=str(row["base_url"]) if row["base_url"] is not None else None,
        model_name=str(row["model_name"]) if row["model_name"] is not None else None,
        credential_configured=bool(row["credential_configured"]),
        enabled=bool(row["enabled"]),
        vision_base_url=(
            str(row["vision_base_url"]) if row["vision_base_url"] is not None else None
        ),
        vision_model_name=(
            str(row["vision_model_name"]) if row["vision_model_name"] is not None else None
        ),
        vision_credential_configured=bool(row["vision_credential_configured"]),
        vision_enabled=bool(row["vision_enabled"]),
    )


def _write_ai_configuration(
    connection: Connection,
    *,
    base_url: str | None,
    model_name: str | None,
    credential_configured: bool,
    enabled: bool,
    now_utc_ms: int,
) -> Mapping[Any, object]:
    return (
        connection.exec_driver_sql(
            """
            INSERT INTO ai_configuration(
                id, base_url, model_name, credential_configured, enabled,
                created_at_utc_ms, updated_at_utc_ms
            ) VALUES (1, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                base_url = excluded.base_url,
                model_name = excluded.model_name,
                credential_configured = excluded.credential_configured,
                enabled = excluded.enabled,
                updated_at_utc_ms = excluded.updated_at_utc_ms
            RETURNING base_url, model_name, credential_configured, enabled,
                      vision_base_url, vision_model_name,
                      vision_credential_configured, vision_enabled
            """,
            (
                base_url,
                model_name,
                int(credential_configured),
                int(enabled),
                now_utc_ms,
                now_utc_ms,
            ),
        )
        .mappings()
        .one()
    )


def _preview_record(row: Mapping[Any, object]) -> AiPreviewRecord:
    result = json.loads(str(row["result_json"]))
    if not isinstance(result, dict):
        raise AiRepositoryError("ai.preview_corrupt", "AI 预览数据已损坏")
    return AiPreviewRecord(
        id=int(str(row["id"])),
        lesson_plan_id=int(str(row["lesson_plan_id"])),
        operation_id=str(row["operation_id"]),
        section_code=str(row["section_code"]),
        result=result,
        frozen_input_sha256=str(row["frozen_input_sha256"]),
        target_section_sha256=str(row["target_section_sha256"]),
        status=str(row["state"]),
    )


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
