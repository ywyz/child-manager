"""园所范围 Word 导出 PostgreSQL Repository。"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb


@dataclass(frozen=True, slots=True)
class ExportRecord:
    id: UUID
    kindergarten_id: UUID
    plan_id: UUID
    plan_version: int
    snapshot_id: UUID | None
    job_id: UUID
    status: str
    display_filename: str
    storage_key: str
    context_snapshot: dict[str, Any]
    content_snapshot: dict[str, Any]
    content_schema_version: int
    content_sha256: str
    file_size: int | None
    file_sha256: str | None
    template_code: str
    template_filename: str
    template_sha256: str
    exported_by: UUID
    exported_at: datetime | None
    error_code: str | None
    error_summary: str | None
    file_missing_at: datetime | None
    created_at: datetime
    updated_at: datetime


_COLUMNS = """id,kindergarten_id,plan_id,plan_version,snapshot_id,job_id,status,
display_filename,storage_key,context_snapshot,content_snapshot,content_schema_version,
content_sha256,file_size,file_sha256,template_code,template_filename,template_sha256,
exported_by,exported_at,error_code,error_summary,file_missing_at,created_at,updated_at"""


def _uuid(value: object | None) -> UUID | None:
    return UUID(str(value)) if value is not None else None


def _record(row: Sequence[object] | None) -> ExportRecord | None:
    if row is None:
        return None
    return ExportRecord(
        id=UUID(str(row[0])),
        kindergarten_id=UUID(str(row[1])),
        plan_id=UUID(str(row[2])),
        plan_version=int(str(row[3])),
        snapshot_id=_uuid(row[4]),
        job_id=UUID(str(row[5])),
        status=str(row[6]),
        display_filename=str(row[7]),
        storage_key=str(row[8]),
        context_snapshot=dict(row[9]),  # type: ignore[arg-type]
        content_snapshot=dict(row[10]),  # type: ignore[arg-type]
        content_schema_version=int(str(row[11])),
        content_sha256=str(row[12]),
        file_size=int(str(row[13])) if row[13] is not None else None,
        file_sha256=str(row[14]) if row[14] is not None else None,
        template_code=str(row[15]),
        template_filename=str(row[16]),
        template_sha256=str(row[17]),
        exported_by=UUID(str(row[18])),
        exported_at=row[19] if isinstance(row[19], datetime) else None,
        error_code=str(row[20]) if row[20] is not None else None,
        error_summary=str(row[21]) if row[21] is not None else None,
        file_missing_at=row[22] if isinstance(row[22], datetime) else None,
        created_at=row[23],  # type: ignore[arg-type]
        updated_at=row[24],  # type: ignore[arg-type]
    )


class ExportRepository:
    """所有查询和变更都同时约束 ``kindergarten_id``。"""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def create_pending(
        self,
        kindergarten_id: UUID,
        *,
        export_id: UUID,
        plan_id: UUID,
        plan_version: int,
        snapshot_id: UUID | None,
        job_id: UUID,
        display_filename: str,
        storage_key: str,
        context_snapshot: dict[str, Any],
        content_snapshot: dict[str, Any],
        content_schema_version: int,
        content_sha256: str,
        template_code: str,
        template_filename: str,
        template_sha256: str,
        exported_by: UUID,
    ) -> ExportRecord:
        row = self.connection.execute(
            f"""INSERT INTO daily_activity_plan_exports
            (id,kindergarten_id,plan_id,plan_version,snapshot_id,job_id,status,
             display_filename,storage_key,context_snapshot,content_snapshot,
             content_schema_version,content_sha256,template_code,template_filename,
             template_sha256,exported_by)
            VALUES (%s,%s,%s,%s,%s,%s,'pending',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING {_COLUMNS}""",
            (
                export_id,
                kindergarten_id,
                plan_id,
                plan_version,
                snapshot_id,
                job_id,
                display_filename,
                storage_key,
                Jsonb(context_snapshot),
                Jsonb(content_snapshot),
                content_schema_version,
                content_sha256,
                template_code,
                template_filename,
                template_sha256,
                exported_by,
            ),
        ).fetchone()
        record = _record(row)
        assert record is not None
        return record

    def get(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        for_update: bool = False,
    ) -> ExportRecord | None:
        suffix = " FOR UPDATE" if for_update else ""
        row = self.connection.execute(
            f"""SELECT {_COLUMNS} FROM daily_activity_plan_exports
            WHERE kindergarten_id=%s AND id=%s{suffix}""",
            (kindergarten_id, export_id),
        ).fetchone()
        return _record(row)

    def get_by_job(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        for_update: bool = False,
    ) -> ExportRecord | None:
        suffix = " FOR UPDATE" if for_update else ""
        row = self.connection.execute(
            f"""SELECT {_COLUMNS} FROM daily_activity_plan_exports
            WHERE kindergarten_id=%s AND job_id=%s{suffix}""",
            (kindergarten_id, job_id),
        ).fetchone()
        return _record(row)

    def list_for_plan(
        self,
        kindergarten_id: UUID,
        plan_id: UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[ExportRecord], int]:
        rows = self.connection.execute(
            f"""SELECT {_COLUMNS},count(*) OVER()
            FROM daily_activity_plan_exports
            WHERE kindergarten_id=%s AND plan_id=%s
            ORDER BY created_at DESC,id DESC LIMIT %s OFFSET %s""",
            (kindergarten_id, plan_id, page_size, (page - 1) * page_size),
        ).fetchall()
        records = [record for row in rows if (record := _record(row[:25])) is not None]
        return records, int(rows[0][25]) if rows else 0

    def mark_succeeded(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        file_size: int,
        file_sha256: str,
    ) -> ExportRecord | None:
        row = self.connection.execute(
            f"""UPDATE daily_activity_plan_exports
            SET status='succeeded',file_size=%s,file_sha256=%s,exported_at=now(),updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND status='pending'
            RETURNING {_COLUMNS}""",
            (file_size, file_sha256, kindergarten_id, export_id),
        ).fetchone()
        return _record(row)

    def mark_failed(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        error_code: str,
        error_summary: str,
    ) -> ExportRecord | None:
        row = self.connection.execute(
            f"""UPDATE daily_activity_plan_exports
            SET status='failed',error_code=%s,error_summary=%s,updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND status='pending'
            RETURNING {_COLUMNS}""",
            (error_code, error_summary, kindergarten_id, export_id),
        ).fetchone()
        return _record(row)

    def mark_file_missing(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
    ) -> ExportRecord | None:
        row = self.connection.execute(
            f"""UPDATE daily_activity_plan_exports
            SET file_missing_at=COALESCE(file_missing_at,now()),updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND status='succeeded'
            RETURNING {_COLUMNS}""",
            (kindergarten_id, export_id),
        ).fetchone()
        return _record(row)
