"""只读取冻结 export row 的 Word Worker 执行器。"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable, Mapping
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol
from uuid import UUID

from packages.backend.exports.repository import ExportRecord, ExportRepository
from packages.backend.exports.rules import (
    TEMPLATE_CODE,
    TEMPLATE_FILENAME,
    TEMPLATE_SHA256,
    canonical_export_content_sha256,
)
from packages.backend.jobs.retry_policy import retry_delay_seconds
from packages.contracts.lesson_plans import PlanContentV1

logger = logging.getLogger(__name__)
LEASE_SECONDS = 120


class WordExportStore(Protocol):
    def claim(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> bool: ...

    def load_for_job(self, kindergarten_id: UUID, job_id: UUID) -> Any: ...

    def publish_succeeded(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        worker_id: str,
        publish: Callable[[], Any],
        cleanup: Callable[[], None],
    ) -> object | None: ...

    def mark_failed(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        worker_id: str,
        error_code: str,
        error_summary: str,
    ) -> object | None: ...

    def handle_error(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        worker_id: str,
        error_code: str,
        error_summary: str,
        retryable: bool,
    ) -> int | None: ...


class WordRenderer(Protocol):
    def render(
        self,
        *,
        context_snapshot: Mapping[str, Any],
        content_snapshot: Mapping[str, Any],
    ) -> bytes: ...


class WordStorage(Protocol):
    def write_atomic(self, storage_key: str, chunks: Iterable[bytes]) -> Any: ...

    def delete(self, storage_key: str) -> None: ...


class WordExportRetry(RuntimeError):
    """通知消息代理按 PostgreSQL 权威状态给出的延迟重投。"""

    def __init__(self, delay_seconds: int) -> None:
        super().__init__("Word 导出任务将按固定策略重试")
        self.delay_seconds = delay_seconds


_REQUIRED_CONTEXT_FIELDS = frozenset(
    {
        "kindergarten_name",
        "class_name",
        "age_group_name",
        "semester_name",
        "semester_start_date",
        "semester_end_date",
        "activity_date_text",
        "season",
        "authors",
    }
)


def _has_valid_frozen_input(export: Any) -> bool:
    context = export.context_snapshot
    content = export.content_snapshot
    if not isinstance(context, dict) or not isinstance(content, dict):
        return False
    if not _REQUIRED_CONTEXT_FIELDS.issubset(context) or not context or not content:
        return False
    if not isinstance(context.get("authors"), list) or not context["authors"]:
        return False
    try:
        validated = PlanContentV1.model_validate(content).model_dump(mode="json")
    except ValueError:
        return False
    return (
        validated == content
        and export.content_schema_version == 1
        and canonical_export_content_sha256(content) == export.content_sha256
        and export.template_code == TEMPLATE_CODE
        and export.template_filename == TEMPLATE_FILENAME
        and export.template_sha256 == TEMPLATE_SHA256
    )


class WordExportRunner:
    def __init__(
        self, *, store: WordExportStore, renderer: WordRenderer, storage: WordStorage
    ) -> None:
        self.store = store
        self.renderer = renderer
        self.storage = storage

    def execute(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> None:
        if not self.store.claim(kindergarten_id, job_id, worker_id=worker_id):
            return
        export = self.store.load_for_job(kindergarten_id, job_id)
        if not _has_valid_frozen_input(export):
            logger.error(
                "Word 导出冻结输入完整性校验失败",
                extra={"job_id": str(job_id)},
            )
            self.store.mark_failed(
                kindergarten_id,
                export.id,
                worker_id=worker_id,
                error_code="export.frozen_input_invalid",
                error_summary="Word 导出冻结输入无效。",
            )
            return
        try:
            payload = self.renderer.render(
                context_snapshot=export.context_snapshot,
                content_snapshot=export.content_snapshot,
            )

            def publish() -> Any:
                self.storage.delete(export.storage_key)
                return self.storage.write_atomic(export.storage_key, (payload,))

            completed = self.store.publish_succeeded(
                kindergarten_id,
                export.id,
                worker_id=worker_id,
                publish=publish,
                cleanup=lambda: self.storage.delete(export.storage_key),
            )
            if completed is None or completed is False:
                return
        except Exception as exc:
            logger.error(
                "Word 导出执行失败",
                extra={"job_id": str(job_id), "exception_type": type(exc).__name__},
            )
            retry_delay = self.store.handle_error(
                kindergarten_id,
                export.id,
                worker_id=worker_id,
                error_code="export.generation_failed",
                error_summary="Word 导出生成失败。",
                retryable=True,
            )
            if retry_delay is not None:
                raise WordExportRetry(retry_delay) from None


class PostgresWordExportStore:
    """用同一事务落位 export 与 background_job 终态。"""

    def __init__(self, connection: Any) -> None:
        if not bool(getattr(connection, "autocommit", False)):
            raise ValueError("PostgresWordExportStore requires an autocommit connection")
        self.connection = connection

    def claim(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> bool:
        lease_expires_at = datetime.now(UTC) + timedelta(seconds=LEASE_SECONDS)
        result = self.connection.execute(
            """UPDATE background_jobs AS job
            SET execution_status='running',attempt_count=attempt_count+1,lease_owner=%s,
                lease_expires_at=%s,last_heartbeat_at=now(),
                started_at=COALESCE(started_at,now()),updated_at=now()
            WHERE job.kindergarten_id=%s AND job.id=%s AND job.job_type='word.export'
              AND job.attempt_count<job.max_attempts
              AND (job.execution_status IN ('pending_dispatch','queued')
                   OR (job.execution_status='retrying' AND job.queued_at<=now())
                   OR (job.execution_status='running' AND job.lease_expires_at<now()))
              AND EXISTS (
                SELECT 1 FROM daily_activity_plan_exports AS export
                WHERE export.kindergarten_id=job.kindergarten_id
                  AND export.job_id=job.id AND export.status='pending'
              )""",
            (worker_id, lease_expires_at, kindergarten_id, job_id),
        )
        return bool(getattr(result, "rowcount", 0))

    def load_for_job(self, kindergarten_id: UUID, job_id: UUID) -> ExportRecord:
        record = ExportRepository(self.connection).get_by_job(kindergarten_id, job_id)
        if record is None:
            raise LookupError("Word 导出冻结记录不存在")
        return record

    def publish_succeeded(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        worker_id: str,
        publish: Callable[[], Any],
        cleanup: Callable[[], None],
    ) -> ExportRecord | None:
        with self.connection.transaction():
            owned = self.connection.execute(
                """SELECT 1 FROM background_jobs AS job
                JOIN daily_activity_plan_exports AS export
                  ON export.kindergarten_id=job.kindergarten_id AND export.job_id=job.id
                WHERE job.kindergarten_id=%s AND export.id=%s
                  AND job.job_type='word.export' AND job.execution_status='running'
                  AND job.lease_owner=%s AND export.status='pending'
                FOR UPDATE OF job,export""",
                (kindergarten_id, export_id, worker_id),
            ).fetchone()
            if owned is None:
                return None
            try:
                stored = publish()
                file_size = int(stored.file_size)
                file_sha256 = str(stored.file_sha256)
                exports = ExportRepository(self.connection)
                record = exports.mark_succeeded(
                    kindergarten_id,
                    export_id,
                    file_size=file_size,
                    file_sha256=file_sha256,
                )
                if record is None:
                    raise RuntimeError("Word 导出记录成功状态落位失败")
                updated = self.connection.execute(
                    """UPDATE background_jobs
                    SET execution_status='succeeded',finished_at=now(),lease_owner=NULL,
                        lease_expires_at=NULL,last_heartbeat_at=NULL,updated_at=now()
                    WHERE kindergarten_id=%s AND id=%s AND job_type='word.export'
                      AND execution_status='running' AND lease_owner=%s""",
                    (kindergarten_id, record.job_id, worker_id),
                )
                if not getattr(updated, "rowcount", 0):
                    raise RuntimeError("Word 导出任务成功状态落位失败")
            except Exception:
                try:
                    cleanup()
                except Exception as cleanup_exc:
                    logger.error(
                        "Word 导出失败补偿清理失败",
                        extra={
                            "export_id": str(export_id),
                            "exception_type": type(cleanup_exc).__name__,
                        },
                    )
                raise
            return record

    def mark_failed(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        worker_id: str,
        error_code: str,
        error_summary: str,
    ) -> ExportRecord | None:
        with self.connection.transaction():
            owned = self.connection.execute(
                """SELECT 1 FROM background_jobs AS job
                JOIN daily_activity_plan_exports AS export
                  ON export.kindergarten_id=job.kindergarten_id AND export.job_id=job.id
                WHERE job.kindergarten_id=%s AND export.id=%s
                  AND job.job_type='word.export' AND job.execution_status='running'
                  AND job.lease_owner=%s AND export.status='pending'
                FOR UPDATE OF job,export""",
                (kindergarten_id, export_id, worker_id),
            ).fetchone()
            if owned is None:
                return None
            exports = ExportRepository(self.connection)
            record = exports.mark_failed(
                kindergarten_id,
                export_id,
                error_code=error_code,
                error_summary=error_summary,
            )
            if record is None:
                return None
            updated = self.connection.execute(
                """UPDATE background_jobs
                SET execution_status='failed',finished_at=now(),error_code=%s,error_summary=%s,
                    lease_owner=NULL,lease_expires_at=NULL,last_heartbeat_at=NULL,updated_at=now()
                WHERE kindergarten_id=%s AND id=%s AND job_type='word.export'
                  AND execution_status='running' AND lease_owner=%s""",
                (
                    error_code,
                    error_summary,
                    kindergarten_id,
                    record.job_id,
                    worker_id,
                ),
            )
            if not getattr(updated, "rowcount", 0):
                raise RuntimeError("Word 导出任务失败状态落位失败")
            return record

    def handle_error(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        worker_id: str,
        error_code: str,
        error_summary: str,
        retryable: bool,
    ) -> int | None:
        with self.connection.transaction():
            row = self.connection.execute(
                """SELECT job.id,job.attempt_count,job.max_attempts
                FROM background_jobs AS job
                JOIN daily_activity_plan_exports AS export
                  ON export.kindergarten_id=job.kindergarten_id AND export.job_id=job.id
                WHERE job.kindergarten_id=%s AND export.id=%s
                  AND job.job_type='word.export' AND job.execution_status='running'
                  AND job.lease_owner=%s AND export.status='pending'
                FOR UPDATE OF job,export""",
                (kindergarten_id, export_id, worker_id),
            ).fetchone()
            if row is None:
                return None
            job_id = UUID(str(row[0]))
            attempt_count = int(str(row[1]))
            max_attempts = int(str(row[2]))
            if retryable and attempt_count < max_attempts:
                delay = retry_delay_seconds(job_id, attempt_count=attempt_count)
                updated = self.connection.execute(
                    """UPDATE background_jobs
                    SET execution_status='retrying',queued_at=now()+(%s * interval '1 second'),
                        lease_owner=NULL,lease_expires_at=NULL,last_heartbeat_at=NULL,
                        error_code=NULL,error_summary=NULL,updated_at=now()
                    WHERE kindergarten_id=%s AND id=%s AND job_type='word.export'
                      AND execution_status='running' AND lease_owner=%s""",
                    (delay, kindergarten_id, job_id, worker_id),
                )
                return delay if getattr(updated, "rowcount", 0) else None
            export_updated = self.connection.execute(
                """UPDATE daily_activity_plan_exports
                SET status='failed',error_code=%s,error_summary=%s,updated_at=now()
                WHERE kindergarten_id=%s AND id=%s AND status='pending'""",
                (error_code, error_summary, kindergarten_id, export_id),
            )
            job_updated = self.connection.execute(
                """UPDATE background_jobs
                SET execution_status='failed',finished_at=now(),error_code=%s,error_summary=%s,
                    lease_owner=NULL,lease_expires_at=NULL,last_heartbeat_at=NULL,updated_at=now()
                WHERE kindergarten_id=%s AND id=%s AND job_type='word.export'
                  AND execution_status='running' AND lease_owner=%s""",
                (error_code, error_summary, kindergarten_id, job_id, worker_id),
            )
            if not getattr(export_updated, "rowcount", 0) or not getattr(
                job_updated, "rowcount", 0
            ):
                raise RuntimeError("Word 导出失败状态落位失败")
            return None

    def reserve_recoverable_jobs(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
        include_expired: bool,
    ) -> list[UUID]:
        rows = self.connection.execute(
            """SELECT job.id FROM background_jobs AS job
            JOIN daily_activity_plan_exports AS export
              ON export.kindergarten_id=job.kindergarten_id AND export.job_id=job.id
            WHERE job.kindergarten_id=%s AND job.job_type='word.export'
              AND export.status='pending' AND job.attempt_count<job.max_attempts
              AND (job.execution_status='pending_dispatch'
                   OR (job.execution_status='retrying' AND job.queued_at<=%s)
                   OR (%s AND job.execution_status='running' AND job.lease_expires_at<%s))
            ORDER BY job.created_at,job.id LIMIT %s""",
            (kindergarten_id, now, include_expired, now, limit),
        ).fetchall()
        return [UUID(str(row[0])) for row in rows]
