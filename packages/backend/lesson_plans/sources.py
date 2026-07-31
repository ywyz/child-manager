"""集体活动来源的园所隔离持久化与服务边界。"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID, uuid7

import psycopg

from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.integrations.files.docx import DocxExtractionError, extract_docx_text
from packages.backend.lesson_plans.repository import LessonPlanRepository
from packages.backend.lesson_plans.service import LessonPlanService

_SOURCE_COLUMNS = """id, plan_id, source_type, original_filename, source_sha256,
    extracted_character_count, uploaded_by, created_at"""


@dataclass(frozen=True, slots=True)
class LessonPlanSourceRecord:
    id: UUID
    plan_id: UUID
    source_type: str
    original_filename: str | None
    source_sha256: str
    extracted_character_count: int
    uploaded_by: UUID
    created_at: datetime


@dataclass(frozen=True, slots=True)
class LessonPlanSourceDocxPreviewRecord:
    original_filename: str
    extracted_text: str


def _record(row: tuple[object, ...] | None) -> LessonPlanSourceRecord | None:
    if row is None:
        return None
    return LessonPlanSourceRecord(
        id=UUID(str(row[0])),
        plan_id=UUID(str(row[1])),
        source_type=str(row[2]),
        original_filename=str(row[3]) if row[3] is not None else None,
        source_sha256=str(row[4]),
        extracted_character_count=int(str(row[5])),
        uploaded_by=UUID(str(row[6])),
        created_at=row[7],  # type: ignore[arg-type]
    )


def sanitize_filename(filename: str) -> str:
    """保留可显示文件名，但绝不保存路径、控制字符或绝对位置。"""

    candidate = Path(filename.replace("\\", "/")).name
    candidate = re.sub(r"[^\w.-]+", "_", candidate, flags=re.UNICODE).strip("._")
    if not candidate.casefold().endswith(".docx"):
        candidate = f"{candidate or 'group-activity'}.docx"
    if len(candidate) > 255:
        candidate = f"{candidate[:250]}.docx"
    return candidate


class LessonPlanSourceRepository:
    """所有来源查询和写入均以 kindergarten_id 为首个范围条件。"""

    def __init__(self, connection: object) -> None:
        self._connection = connection

    def _require_plan_and_uploader(
        self,
        kindergarten_id: UUID,
        plan_id: UUID,
        uploaded_by: UUID,
    ) -> None:
        plan = self._connection.execute(  # type: ignore[attr-defined]
            "SELECT 1 FROM daily_activity_plans WHERE kindergarten_id=%s AND id=%s",
            (kindergarten_id, plan_id),
        ).fetchone()
        uploader = self._connection.execute(  # type: ignore[attr-defined]
            "SELECT 1 FROM users WHERE kindergarten_id=%s AND id=%s AND status='active'",
            (kindergarten_id, uploaded_by),
        ).fetchone()
        if plan is None or uploader is None:
            raise LookupError("园所范围内不存在教案或上传人")

    def confirm_text(
        self,
        *,
        kindergarten_id: UUID,
        plan_id: UUID,
        uploaded_by: UUID,
        text: str,
    ) -> LessonPlanSourceRecord:
        return self._confirm(
            kindergarten_id=kindergarten_id,
            plan_id=plan_id,
            uploaded_by=uploaded_by,
            source_type="pasted_text",
            original_filename=None,
            text=text,
        )

    def confirm_docx(
        self,
        *,
        kindergarten_id: UUID,
        plan_id: UUID,
        uploaded_by: UUID,
        original_filename: str,
        text: str,
    ) -> LessonPlanSourceRecord:
        return self._confirm(
            kindergarten_id=kindergarten_id,
            plan_id=plan_id,
            uploaded_by=uploaded_by,
            source_type="docx",
            original_filename=sanitize_filename(original_filename),
            text=text,
        )

    def _confirm(
        self,
        *,
        kindergarten_id: UUID,
        plan_id: UUID,
        uploaded_by: UUID,
        source_type: str,
        original_filename: str | None,
        text: str,
    ) -> LessonPlanSourceRecord:
        if not text or len(text) > 200_000:
            raise ValueError("集体活动来源文本长度无效")
        self._require_plan_and_uploader(kindergarten_id, plan_id, uploaded_by)
        row = self._connection.execute(  # type: ignore[attr-defined]
            f"""INSERT INTO lesson_plan_sources
            (id, kindergarten_id, plan_id, source_type, original_filename, source_sha256,
             extracted_character_count, extracted_text, uploaded_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING {_SOURCE_COLUMNS}""",
            (
                uuid7(),
                kindergarten_id,
                plan_id,
                source_type,
                original_filename,
                sha256(text.encode()).hexdigest(),
                len(text),
                text,
                uploaded_by,
            ),
        ).fetchone()
        record = _record(row)
        assert record is not None
        return record

    def list_history(
        self,
        kindergarten_id: UUID,
        plan_id: UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[LessonPlanSourceRecord], int]:
        rows = self._connection.execute(  # type: ignore[attr-defined]
            f"""SELECT {_SOURCE_COLUMNS}, count(*) OVER()
            FROM lesson_plan_sources
            WHERE kindergarten_id=%s AND plan_id=%s
            ORDER BY created_at DESC, id DESC
            LIMIT %s OFFSET %s""",
            (kindergarten_id, plan_id, page_size, (page - 1) * page_size),
        ).fetchall()
        return (
            [record for row in rows if (record := _record(row[:8])) is not None],
            int(rows[0][8]) if rows else 0,
        )

    def get_confirmed_text(
        self, *, kindergarten_id: UUID, source_id: UUID, plan_id: UUID | None = None
    ) -> str:
        if plan_id is None:
            query = (
                "SELECT extracted_text FROM lesson_plan_sources WHERE kindergarten_id=%s AND id=%s"
            )
            parameters = (kindergarten_id, source_id)
        else:
            query = (
                "SELECT extracted_text FROM lesson_plan_sources "
                "WHERE kindergarten_id=%s AND plan_id=%s AND id=%s"
            )
            parameters = (kindergarten_id, plan_id, source_id)
        row = self._connection.execute(query, parameters).fetchone()  # type: ignore[attr-defined]
        if row is None:
            raise LookupError("园所范围内不存在来源")
        return str(row[0])


class LessonPlanSourceService:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    @classmethod
    def from_environment(cls) -> LessonPlanSourceService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
        return cls(database_url)

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        native_url = self._database_url.replace("postgresql+psycopg://", "postgresql://", 1)
        return psycopg.connect(native_url)

    @staticmethod
    def _kindergarten_id(session: SessionUser) -> UUID:
        return LessonPlanService._kindergarten_id(session)

    @staticmethod
    def _require_edit(
        session: SessionUser,
        repository: LessonPlanRepository,
        kindergarten_id: UUID,
        plan_id: UUID,
    ) -> None:
        plan = repository.get_plan(kindergarten_id, plan_id)
        if plan is None:
            raise LessonPlanService._not_found()
        LessonPlanService._require_edit(session, repository, kindergarten_id, plan)

    @staticmethod
    def _require_view(
        session: SessionUser,
        repository: LessonPlanRepository,
        kindergarten_id: UUID,
        plan_id: UUID,
    ) -> None:
        plan = repository.get_plan(kindergarten_id, plan_id)
        if plan is None:
            raise LessonPlanService._not_found()
        LessonPlanService._require_view(session, repository, kindergarten_id, plan)

    @staticmethod
    def _require_valid_source_text(text: str) -> None:
        if not text or len(text) > 200_000:
            raise IdentityError(
                422, "group_activity.source_invalid", "来源文本长度必须在 1 到 200000 字符之间。"
            )

    def confirm_text(
        self,
        session: SessionUser,
        *,
        plan_id: UUID,
        text: str,
    ) -> LessonPlanSourceRecord:
        self._require_valid_source_text(text)
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            plans = LessonPlanRepository(connection)
            self._require_edit(session, plans, kindergarten_id, plan_id)
            return LessonPlanSourceRepository(connection).confirm_text(
                kindergarten_id=kindergarten_id,
                plan_id=plan_id,
                uploaded_by=session.user.id,
                text=text,
            )

    def preview_docx(
        self,
        session: SessionUser,
        *,
        plan_id: UUID,
        filename: str,
        content_type: str,
        payload: bytes,
    ) -> LessonPlanSourceDocxPreviewRecord:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            plans = LessonPlanRepository(connection)
            self._require_edit(session, plans, kindergarten_id, plan_id)
        try:
            with TemporaryDirectory(prefix="child-manager-docx-") as temporary_directory:
                extracted_text = extract_docx_text(
                    payload=payload,
                    filename=filename,
                    content_type=content_type,
                    temporary_directory=Path(temporary_directory),
                )
        except DocxExtractionError as error:
            raise IdentityError(
                422, "group_activity.source_invalid", "DOCX 文件无效或不安全。"
            ) from error
        return LessonPlanSourceDocxPreviewRecord(
            original_filename=sanitize_filename(filename),
            extracted_text=extracted_text,
        )

    def confirm_docx(
        self,
        session: SessionUser,
        *,
        plan_id: UUID,
        filename: str,
        text: str,
    ) -> LessonPlanSourceRecord:
        self._require_valid_source_text(text)
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            plans = LessonPlanRepository(connection)
            self._require_edit(session, plans, kindergarten_id, plan_id)
            return LessonPlanSourceRepository(connection).confirm_docx(
                kindergarten_id=kindergarten_id,
                plan_id=plan_id,
                uploaded_by=session.user.id,
                original_filename=filename,
                text=text,
            )

    def list_history(
        self,
        session: SessionUser,
        *,
        plan_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[LessonPlanSourceRecord], int]:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            plans = LessonPlanRepository(connection)
            self._require_view(session, plans, kindergarten_id, plan_id)
            return LessonPlanSourceRepository(connection).list_history(
                kindergarten_id,
                plan_id,
                page=page,
                page_size=page_size,
            )
