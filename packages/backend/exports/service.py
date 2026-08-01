"""Word 导出创建、历史、详情与实时授权下载用例。"""

from __future__ import annotations

import logging
import os
from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid7

import psycopg

from packages.backend.audit.repository import AuditRepository
from packages.backend.exports.repository import ExportRecord, ExportRepository
from packages.backend.exports.rules import (
    TEMPLATE_CODE,
    TEMPLATE_FILENAME,
    TEMPLATE_SHA256,
    canonical_export_content_sha256,
    missing_export_sections,
)
from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.integrations.files.export_storage import (
    ExportStorage,
    build_display_filename,
    new_storage_key,
)
from packages.backend.jobs.dispatcher import RedisJobDispatcher
from packages.backend.jobs.repository import JobRecord, JobRepository
from packages.backend.lesson_plans.ai_generation import dispatch_after_commit
from packages.backend.lesson_plans.repository import (
    AuthorRecord,
    LessonPlanRepository,
    PlanRecord,
)
from packages.backend.lesson_plans.service import LessonPlanService
from packages.contracts.audit import IdentityAuditEventCode
from packages.contracts.common import canonical_request_fingerprint
from packages.contracts.exports import ExportRequest

logger = logging.getLogger(__name__)

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


@dataclass(frozen=True, slots=True)
class ExportAcceptance:
    job: JobRecord
    export: ExportRecord
    replayed: bool = False


@dataclass(frozen=True, slots=True)
class ExportDownload:
    record: ExportRecord
    path: Path


class ExportService:
    def __init__(
        self,
        *,
        database_url: str,
        storage: ExportStorage,
        dispatcher: RedisJobDispatcher | None = None,
    ) -> None:
        self.database_url = database_url
        self.storage = storage
        self.dispatcher = dispatcher

    @classmethod
    def from_environment(cls) -> ExportService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        runtime_root_value = os.environ.get("CHILD_MANAGER_RUNTIME_ROOT")
        if not database_url or not runtime_root_value:
            raise IdentityError(503, "configuration.unavailable", "Word 导出配置不可用。")
        repository_root = Path(__file__).resolve().parents[3]
        template_path = repository_root / "templates/teacherplan/teacherplan.docx"
        try:
            if not template_path.is_file():
                raise OSError("template missing")
            if sha256(template_path.read_bytes()).hexdigest() != TEMPLATE_SHA256:
                raise OSError("template hash mismatch")
            runtime_root = Path(runtime_root_value)
            storage = ExportStorage(
                runtime_root / "exports",
                temporary_root=runtime_root / "temporary",
            )
        except OSError as exc:
            raise IdentityError(
                503,
                "configuration.unavailable",
                "Word 导出配置不可用。",
            ) from exc
        redis_url = os.environ.get("CHILD_MANAGER_REDIS_URL")
        dispatcher = (
            RedisJobDispatcher.from_url(redis_url, actor_name="word_export") if redis_url else None
        )
        return cls(database_url=database_url, storage=storage, dispatcher=dispatcher)

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    @staticmethod
    def _kindergarten_id(session: SessionUser) -> UUID:
        kindergarten_id = session.user.kindergarten_id
        if kindergarten_id is None:
            raise IdentityError(403, "auth.forbidden", "当前账号不属于可用园所。")
        return kindergarten_id

    @staticmethod
    def _validate_idempotency_key(value: str) -> None:
        if not value or len(value) > 200:
            raise IdentityError(
                422,
                "request.invalid_idempotency_key",
                "Idempotency-Key 长度必须为 1 到 200 个字符。",
            )

    @staticmethod
    def _plan(
        session: SessionUser,
        repository: LessonPlanRepository,
        kindergarten_id: UUID,
        plan_id: UUID,
        *,
        for_update: bool,
    ) -> PlanRecord:
        plan = repository.get_plan(kindergarten_id, plan_id, for_update=for_update)
        if plan is None:
            raise IdentityError(404, "resource.not_found", "教案不存在。")
        LessonPlanService._require_view(session, repository, kindergarten_id, plan)
        if plan.content_schema_version != 1:
            raise IdentityError(409, "plan.schema_read_only", "教案内容版本暂不支持导出。")
        return plan

    @staticmethod
    def _requested_authors(
        repository: LessonPlanRepository,
        kindergarten_id: UUID,
        plan_id: UUID,
        body: ExportRequest,
    ) -> list[AuthorRecord]:
        existing = repository.list_authors(kindergarten_id, plan_id)
        existing_shape = [(author.user_id, author.sort_order) for author in existing]
        requested_shape = sorted(
            ((author.user_id, author.sort_order) for author in body.authors),
            key=lambda value: value[1],
        )
        if requested_shape != existing_shape:
            raise IdentityError(
                409,
                "plan.autosave_authors_immutable",
                "导出前无快照保存不能修改编写教师。",
            )
        return existing

    @staticmethod
    def _context_snapshot(
        plan: PlanRecord,
        authors: Sequence[AuthorRecord],
    ) -> dict[str, object]:
        return LessonPlanService._context_snapshot(plan, authors)

    @staticmethod
    def _check_existing(
        jobs: JobRepository,
        exports: ExportRepository,
        kindergarten_id: UUID,
        *,
        requested_by: UUID,
        scope: str,
        key: str,
        fingerprint: str,
    ) -> ExportAcceptance | None:
        existing_job = jobs.find_idempotent(
            kindergarten_id,
            requested_by=requested_by,
            scope=scope,
            key=key,
        )
        if existing_job is None:
            return None
        if existing_job.request_fingerprint_sha256 != fingerprint:
            raise IdentityError(
                409,
                "request.idempotency_conflict",
                "幂等键已用于不同的导出请求。",
            )
        export = exports.get_by_job(kindergarten_id, existing_job.id)
        if export is None:
            raise IdentityError(409, "export.state_conflict", "导出受理记录不完整。")
        return ExportAcceptance(existing_job, export, replayed=True)

    def create(
        self,
        session: SessionUser,
        plan_id: UUID,
        body: ExportRequest,
        *,
        idempotency_key: str,
        request_id: UUID | None,
    ) -> ExportAcceptance:
        self._validate_idempotency_key(idempotency_key)
        kindergarten_id = self._kindergarten_id(session)
        content = body.content.model_dump(mode="json")
        missing = missing_export_sections(body.content)
        scope = "POST /api/v1/plans/{plan_id}/exports"
        fingerprint = canonical_request_fingerprint(
            method="POST",
            route_template="/api/v1/plans/{plan_id}/exports",
            path_params={"plan_id": plan_id},
            query_params=[],
            body=body.model_dump(mode="json"),
        )
        try:
            if missing and not body.confirm_incomplete:
                with self._connect() as connection, connection.transaction():
                    repository = LessonPlanRepository(connection)
                    plan = self._plan(
                        session,
                        repository,
                        kindergarten_id,
                        plan_id,
                        for_update=False,
                    )
                    if plan.version != body.expected_version:
                        raise IdentityError(
                            409,
                            "lesson_plan.version_conflict",
                            "教案已被修改，请刷新后重试。",
                        )
                    self._requested_authors(
                        repository,
                        kindergarten_id,
                        plan_id,
                        body,
                    )
                raise IdentityError(
                    409,
                    "export.confirmation_required",
                    "以下栏目内容不完整，确认后仍可导出。",
                    details={"missing_sections": list(missing)},
                )

            with self._connect() as connection, connection.transaction():
                jobs = JobRepository(connection)
                exports = ExportRepository(connection)
                jobs.lock_idempotency(
                    kindergarten_id,
                    requested_by=session.user.id,
                    scope=scope,
                    key=idempotency_key,
                )
                repository = LessonPlanRepository(connection)
                current = self._plan(
                    session,
                    repository,
                    kindergarten_id,
                    plan_id,
                    for_update=True,
                )
                replay = self._check_existing(
                    jobs,
                    exports,
                    kindergarten_id,
                    requested_by=session.user.id,
                    scope=scope,
                    key=idempotency_key,
                    fingerprint=fingerprint,
                )
                if replay is not None:
                    return replay
                if current.version != body.expected_version:
                    raise IdentityError(
                        409,
                        "lesson_plan.version_conflict",
                        "教案已被修改，请刷新后重试。",
                    )
                authors = self._requested_authors(
                    repository,
                    kindergarten_id,
                    plan_id,
                    body,
                )
                associated_teacher = repository.is_class_teacher(
                    kindergarten_id,
                    current.class_id,
                    session.user.id,
                )
                if not associated_teacher and content != current.content:
                    raise IdentityError(
                        403,
                        "class.not_associated",
                        "管理员可导出教案，但不能修改非关联班级正文。",
                    )
                if current.archived_at is not None:
                    if content != current.content:
                        raise IdentityError(
                            409,
                            "plan.archived_read_only",
                            "归档教案只能导出已保存内容。",
                        )
                    saved = current
                else:
                    saved = repository.update_content(
                        kindergarten_id,
                        plan_id,
                        expected_version=body.expected_version,
                        content=content,
                        actor_id=session.user.id,
                    )
                    if saved is None:
                        raise IdentityError(
                            409,
                            "lesson_plan.version_conflict",
                            "教案已被修改，请刷新后重试。",
                        )

                trace_id = uuid7()
                job_id = uuid7()
                export_id = uuid7()
                job = jobs.create_word_export(
                    kindergarten_id,
                    job_id=job_id,
                    plan_id=plan_id,
                    requested_resource_version=saved.version,
                    requested_by=session.user.id,
                    request_id=request_id,
                    trace_id=trace_id,
                    scope=scope,
                    key=idempotency_key,
                    fingerprint=fingerprint,
                )
                export = exports.create_pending(
                    kindergarten_id,
                    export_id=export_id,
                    plan_id=plan_id,
                    plan_version=saved.version,
                    snapshot_id=None,
                    job_id=job.id,
                    display_filename=build_display_filename(
                        saved.class_name_snapshot,
                        saved.plan_date.isoformat(),
                    ),
                    storage_key=new_storage_key(export_id),
                    context_snapshot=self._context_snapshot(saved, authors),
                    content_snapshot=content,
                    content_schema_version=saved.content_schema_version,
                    content_sha256=canonical_export_content_sha256(content),
                    template_code=TEMPLATE_CODE,
                    template_filename=TEMPLATE_FILENAME,
                    template_sha256=TEMPLATE_SHA256,
                    exported_by=session.user.id,
                )
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.PLAN_EXPORT_REQUESTED,
                    actor_user_id=session.user.id,
                    actor_role_codes=list(session.role_codes),
                    resource_type="lesson_plan_export",
                    resource_id=export.id,
                    outcome="success",
                    request_id=request_id,
                    trace_id=job.trace_id,
                    job_id=job.id,
                )
                acceptance = ExportAcceptance(job, export)
        except psycopg.OperationalError as exc:
            raise IdentityError(503, "database.unavailable", "数据库暂不可用。") from exc
        self._dispatch(kindergarten_id, acceptance.job.id)
        return acceptance

    def list_for_plan(
        self,
        session: SessionUser,
        plan_id: UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[ExportRecord], int]:
        kindergarten_id = self._kindergarten_id(session)
        try:
            with self._connect() as connection:
                plans = LessonPlanRepository(connection)
                self._plan(session, plans, kindergarten_id, plan_id, for_update=False)
                return ExportRepository(connection).list_for_plan(
                    kindergarten_id,
                    plan_id,
                    page=page,
                    page_size=page_size,
                )
        except psycopg.OperationalError as exc:
            raise IdentityError(503, "database.unavailable", "数据库暂不可用。") from exc

    def get(self, session: SessionUser, export_id: UUID) -> ExportRecord:
        kindergarten_id = self._kindergarten_id(session)
        try:
            with self._connect() as connection:
                export = ExportRepository(connection).get(kindergarten_id, export_id)
                if export is None:
                    raise IdentityError(404, "resource.not_found", "导出记录不存在。")
                self._plan(
                    session,
                    LessonPlanRepository(connection),
                    kindergarten_id,
                    export.plan_id,
                    for_update=False,
                )
                return export
        except psycopg.OperationalError as exc:
            raise IdentityError(503, "database.unavailable", "数据库暂不可用。") from exc

    def download(self, session: SessionUser, export_id: UUID) -> ExportDownload:
        kindergarten_id = self._kindergarten_id(session)
        try:
            with self._connect() as connection, connection.transaction():
                exports = ExportRepository(connection)
                export = exports.get(kindergarten_id, export_id, for_update=True)
                if export is None:
                    raise IdentityError(404, "resource.not_found", "导出记录不存在。")
                self._plan(
                    session,
                    LessonPlanRepository(connection),
                    kindergarten_id,
                    export.plan_id,
                    for_update=False,
                )
                if export.status != "succeeded":
                    raise IdentityError(409, "export.not_ready", "导出文件尚不可下载。")
                try:
                    path = self.storage.open_for_read(export.storage_key)
                except FileNotFoundError as exc:
                    exports.mark_file_missing(kindergarten_id, export.id)
                    AuditRepository(connection, kindergarten_id).append(
                        event_code=IdentityAuditEventCode.PLAN_EXPORT_DOWNLOAD_FAILED,
                        actor_user_id=session.user.id,
                        actor_role_codes=list(session.role_codes),
                        resource_type="lesson_plan_export",
                        resource_id=export.id,
                        outcome="failure",
                        metadata={"reason": "file_missing"},
                    )
                    raise IdentityError(
                        410,
                        "export.file_missing",
                        "历史导出文件已缺失，无法重新下载。",
                    ) from exc
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.PLAN_EXPORT_DOWNLOADED,
                    actor_user_id=session.user.id,
                    actor_role_codes=list(session.role_codes),
                    resource_type="lesson_plan_export",
                    resource_id=export.id,
                    outcome="success",
                )
                return ExportDownload(export, path)
        except psycopg.OperationalError as exc:
            raise IdentityError(503, "database.unavailable", "数据库暂不可用。") from exc

    def _dispatch(self, kindergarten_id: UUID, job_id: UUID) -> None:
        try:
            dispatched = dispatch_after_commit(self.dispatcher, (job_id,))
        except Exception:
            logger.error("Word 导出任务提交后投递失败", extra={"job_id": str(job_id)})
            return
        if job_id not in dispatched:
            return
        try:
            with self._connect() as connection, connection.transaction():
                JobRepository(connection).mark_queued(kindergarten_id, job_id)
        except Exception:
            logger.error("Word 导出任务 queued 状态回写失败", extra={"job_id": str(job_id)})
