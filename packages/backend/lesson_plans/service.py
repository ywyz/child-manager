"""教案权限、事务、乐观锁、快照与软提示用例。"""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from datetime import UTC, date, datetime
from hashlib import sha256
from typing import Any
from uuid import UUID

import psycopg

from packages.backend.audit.repository import AuditRepository
from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.integrations.calendar.service import WorkdayService
from packages.backend.lesson_plans.calendar import activity_date_text, season_for, teaching_week
from packages.backend.lesson_plans.repository import (
    AuthorRecord,
    LessonPlanRepository,
    PlanRecord,
    SnapshotRecord,
)
from packages.contracts.audit import IdentityAuditEventCode
from packages.contracts.lesson_plans import AuthorWrite, PlanContentV1, SoftWarning


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _canonical_sha256(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return sha256(payload).hexdigest()


class LessonPlanService:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    @classmethod
    def from_environment(cls) -> LessonPlanService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
        return cls(database_url)

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    @staticmethod
    def _kindergarten_id(session: SessionUser) -> UUID:
        kindergarten_id = session.user.kindergarten_id
        if kindergarten_id is None:
            raise IdentityError(403, "auth.forbidden", "当前账号不属于可用园所。")
        return kindergarten_id

    @staticmethod
    def _not_found() -> IdentityError:
        return IdentityError(404, "resource.not_found", "教案不存在。")

    @staticmethod
    def _conflict() -> IdentityError:
        return IdentityError(409, "plan.version_conflict", "教案已被修改，请刷新后重试。")

    @staticmethod
    def _require_view(
        session: SessionUser,
        repository: LessonPlanRepository,
        kindergarten_id: UUID,
        plan: PlanRecord,
    ) -> None:
        if "admin" in session.role_codes:
            return
        if "teacher" in session.role_codes and repository.is_class_teacher(
            kindergarten_id, plan.class_id, session.user.id
        ):
            return
        raise IdentityError(403, "class.not_associated", "只能访问本人关联班级的教案。")

    @staticmethod
    def _require_edit(
        session: SessionUser,
        repository: LessonPlanRepository,
        kindergarten_id: UUID,
        plan: PlanRecord,
    ) -> None:
        if not repository.is_class_teacher(kindergarten_id, plan.class_id, session.user.id):
            raise IdentityError(403, "class.not_associated", "只有关联教师可编辑本班教案。")
        if plan.archived_at is not None:
            raise IdentityError(409, "plan.archived_read_only", "教案已归档，请先恢复归档。")
        if plan.content_schema_version != 1:
            raise IdentityError(409, "plan.schema_read_only", "教案内容版本暂不支持编辑。")

    def open_plan(
        self,
        session: SessionUser,
        *,
        class_id: UUID,
        plan_date: date,
    ) -> PlanRecord:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection, connection.transaction():
            repository = LessonPlanRepository(connection)
            existing = repository.get_plan_by_class_date(kindergarten_id, class_id, plan_date)
            if existing is not None:
                self._require_view(session, repository, kindergarten_id, existing)
                return existing
            if not repository.class_exists(kindergarten_id, class_id):
                raise IdentityError(404, "resource.not_found", "班级不存在。")
            if not repository.is_class_teacher(kindergarten_id, class_id, session.user.id):
                raise IdentityError(403, "class.not_associated", "只有关联教师可创建本班教案。")
            context = repository.creation_context(kindergarten_id, class_id)
            if context is None:
                raise IdentityError(409, "semester.current_required", "请先配置并启用当前学期。")
            week_number, week_text = teaching_week(
                plan_date,
                context.semester_start_date,
                context.semester_end_date,
            )
            plan = repository.create_plan(
                kindergarten_id,
                class_id,
                plan_date,
                context=context,
                teaching_week_number=week_number,
                teaching_week_text=week_text,
                activity_date_text=activity_date_text(plan_date),
                season_code=season_for(plan_date),
                content=PlanContentV1.empty().model_dump(mode="json"),
                actor_id=session.user.id,
            )
            if not repository.list_authors(kindergarten_id, plan.id):
                repository.replace_authors(
                    kindergarten_id,
                    plan.id,
                    [(session.user.id, 0, session.user.display_name)],
                    actor_id=session.user.id,
                )
            return plan

    def get_plan(self, session: SessionUser, plan_id: UUID) -> PlanRecord:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            repository = LessonPlanRepository(connection)
            plan = repository.get_plan(kindergarten_id, plan_id)
            if plan is None:
                raise self._not_found()
            self._require_view(session, repository, kindergarten_id, plan)
            return plan

    def list_plans(
        self,
        session: SessionUser,
        *,
        class_id: UUID | None,
        date_from: date | None,
        date_to: date | None,
        author_id: UUID | None,
        archived: bool | None,
        page: int,
        page_size: int,
    ) -> tuple[list[PlanRecord], int]:
        kindergarten_id = self._kindergarten_id(session)
        if date_from is not None and date_to is not None and date_from > date_to:
            raise IdentityError(422, "plan.invalid_date_range", "开始日期不能晚于结束日期。")
        visible_to = None if "admin" in session.role_codes else session.user.id
        if visible_to is not None and "teacher" not in session.role_codes:
            raise IdentityError(403, "auth.forbidden", "当前账号没有访问教案的权限。")
        with self._connect() as connection:
            return LessonPlanRepository(connection).list_plans(
                kindergarten_id,
                class_id=class_id,
                date_from=date_from,
                date_to=date_to,
                author_id=author_id,
                archived=archived,
                visible_to_user_id=visible_to,
                page=page,
                page_size=page_size,
            )

    def authors_for(self, session: SessionUser, plan: PlanRecord) -> list[AuthorRecord]:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            return LessonPlanRepository(connection).list_authors(kindergarten_id, plan.id)

    @staticmethod
    def _author_tuples(
        repository: LessonPlanRepository,
        kindergarten_id: UUID,
        plan: PlanRecord,
        authors: Sequence[AuthorWrite],
    ) -> list[tuple[UUID, int, str]]:
        names = repository.resolve_author_names(
            kindergarten_id,
            plan.class_id,
            plan.id,
            [author.user_id for author in authors],
        )
        if len(names) != len(authors):
            raise IdentityError(
                422,
                "plan.author_not_associated",
                "编写教师必须属于当前园所并关联该班级。",
            )
        return [
            (author.user_id, author.sort_order, names[author.user_id])
            for author in sorted(authors, key=lambda value: value.sort_order)
        ]

    @staticmethod
    def _context_snapshot(
        plan: PlanRecord,
        authors: Sequence[AuthorRecord],
    ) -> dict[str, Any]:
        return {
            "kindergarten_name": plan.kindergarten_name_snapshot,
            "class_name": plan.class_name_snapshot,
            "age_group_name": plan.age_group_name_snapshot,
            "semester_name": plan.semester_name_snapshot,
            "semester_start_date": plan.semester_start_date_snapshot.isoformat(),
            "semester_end_date": plan.semester_end_date_snapshot.isoformat(),
            "teaching_week_number": plan.teaching_week_number,
            "teaching_week_text": plan.teaching_week_text,
            "activity_date_text": plan.activity_date_text,
            "season": plan.season_code,
            "authors": [
                {
                    "user_id": str(author.user_id),
                    "sort_order": author.sort_order,
                    "display_name_snapshot": author.display_name_snapshot,
                }
                for author in authors
            ],
        }

    @classmethod
    def _snapshot(
        cls,
        repository: LessonPlanRepository,
        kindergarten_id: UUID,
        plan: PlanRecord,
        *,
        reason: str,
        actor_id: UUID,
    ) -> SnapshotRecord:
        authors = repository.list_authors(kindergarten_id, plan.id)
        return repository.add_snapshot(
            kindergarten_id,
            plan.id,
            plan_version=plan.version,
            reason_code=reason,
            context_snapshot=cls._context_snapshot(plan, authors),
            content=plan.content,
            content_schema_version=plan.content_schema_version,
            content_sha256=_canonical_sha256(plan.content),
            created_by=actor_id,
        )

    def save(
        self,
        session: SessionUser,
        plan_id: UUID,
        *,
        expected_version: int,
        content: PlanContentV1,
        authors: Sequence[AuthorWrite],
        create_snapshot: bool,
    ) -> PlanRecord:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection, connection.transaction():
            repository = LessonPlanRepository(connection)
            current = repository.get_plan(kindergarten_id, plan_id)
            if current is None:
                raise self._not_found()
            self._require_edit(session, repository, kindergarten_id, current)
            author_tuples = self._author_tuples(repository, kindergarten_id, current, authors)
            existing = repository.list_authors(kindergarten_id, plan_id)
            requested_shape = [(user_id, order, name) for user_id, order, name in author_tuples]
            existing_shape = [
                (author.user_id, author.sort_order, author.display_name_snapshot)
                for author in existing
            ]
            if not create_snapshot and requested_shape != existing_shape:
                raise IdentityError(
                    409,
                    "plan.autosave_authors_immutable",
                    "编写教师变更必须使用显式保存。",
                )
            updated = repository.update_content(
                kindergarten_id,
                plan_id,
                expected_version=expected_version,
                content=content.model_dump(mode="json"),
                actor_id=session.user.id,
            )
            if updated is None:
                raise self._conflict()
            if create_snapshot:
                repository.replace_authors(
                    kindergarten_id,
                    plan_id,
                    author_tuples,
                    actor_id=session.user.id,
                )
                self._snapshot(
                    repository,
                    kindergarten_id,
                    updated,
                    reason="manual_save",
                    actor_id=session.user.id,
                )
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.PLAN_MANUALLY_SAVED,
                    actor_user_id=session.user.id,
                    actor_role_codes=list(session.role_codes),
                    resource_type="lesson_plan",
                    resource_id=plan_id,
                    outcome="success",
                )
            return updated

    def set_archived(
        self,
        session: SessionUser,
        plan_id: UUID,
        *,
        expected_version: int,
        archived: bool,
    ) -> PlanRecord:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection, connection.transaction():
            repository = LessonPlanRepository(connection)
            current = repository.get_plan(kindergarten_id, plan_id)
            if current is None:
                raise self._not_found()
            self._require_view(session, repository, kindergarten_id, current)
            updated = repository.set_archived(
                kindergarten_id,
                plan_id,
                expected_version=expected_version,
                archived=archived,
                actor_id=session.user.id,
            )
            if updated is None:
                raise self._conflict()
            reason = "archive" if archived else "unarchive"
            self._snapshot(
                repository,
                kindergarten_id,
                updated,
                reason=reason,
                actor_id=session.user.id,
            )
            AuditRepository(connection, kindergarten_id).append(
                event_code=(
                    IdentityAuditEventCode.PLAN_ARCHIVED
                    if archived
                    else IdentityAuditEventCode.PLAN_UNARCHIVED
                ),
                actor_user_id=session.user.id,
                actor_role_codes=list(session.role_codes),
                resource_type="lesson_plan",
                resource_id=plan_id,
                outcome="success",
            )
            return updated

    def list_snapshots(
        self,
        session: SessionUser,
        plan_id: UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[SnapshotRecord], int]:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            repository = LessonPlanRepository(connection)
            plan = repository.get_plan(kindergarten_id, plan_id)
            if plan is None:
                raise self._not_found()
            self._require_view(session, repository, kindergarten_id, plan)
            return repository.list_snapshots(
                kindergarten_id, plan_id, page=page, page_size=page_size
            )

    def restore_snapshot(
        self,
        session: SessionUser,
        plan_id: UUID,
        snapshot_id: UUID,
        *,
        expected_version: int,
    ) -> PlanRecord:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection, connection.transaction():
            repository = LessonPlanRepository(connection)
            current = repository.get_plan(kindergarten_id, plan_id)
            if current is None:
                raise self._not_found()
            self._require_edit(session, repository, kindergarten_id, current)
            target = repository.get_snapshot(kindergarten_id, plan_id, snapshot_id)
            if target is None:
                raise IdentityError(404, "resource.not_found", "历史版本不存在。")
            self._snapshot(
                repository,
                kindergarten_id,
                current,
                reason="before_restore",
                actor_id=session.user.id,
            )
            updated = repository.update_content(
                kindergarten_id,
                plan_id,
                expected_version=expected_version,
                content=target.content,
                actor_id=session.user.id,
            )
            if updated is None:
                raise self._conflict()
            target_authors = [
                AuthorWrite(
                    user_id=author["user_id"],
                    sort_order=author["sort_order"],
                )
                for author in target.context_snapshot.get("authors", [])
            ]
            author_tuples = self._author_tuples(
                repository, kindergarten_id, updated, target_authors
            )
            repository.replace_authors(
                kindergarten_id,
                plan_id,
                author_tuples,
                actor_id=session.user.id,
            )
            self._snapshot(
                repository,
                kindergarten_id,
                updated,
                reason="restored",
                actor_id=session.user.id,
            )
            AuditRepository(connection, kindergarten_id).append(
                event_code=IdentityAuditEventCode.PLAN_HISTORY_RESTORED,
                actor_user_id=session.user.id,
                actor_role_codes=list(session.role_codes),
                resource_type="lesson_plan",
                resource_id=plan_id,
                outcome="success",
            )
            return updated

    def warnings_for(self, session: SessionUser, plan: PlanRecord) -> list[SoftWarning]:
        warnings: list[SoftWarning] = []
        if plan.teaching_week_number is None:
            warnings.append(
                SoftWarning(
                    code="semester.out_of_range",
                    message="所选日期不在当前学期内，教学周次保持为空。",
                )
            )
        kindergarten_id = self._kindergarten_id(session)
        now = datetime.now(UTC)
        with self._connect() as connection, connection.transaction():
            result = WorkdayService(connection=connection).check(
                kindergarten_id,
                plan.plan_date,
                now=now,
            )
        detail = {
            "calendar_date": plan.plan_date.isoformat(),
            "source_code": result.source_code,
            **result.detail,
        }
        if result.source_code == "combined":
            warnings.append(
                SoftWarning(
                    code="calendar.source_conflict",
                    message="工作日来源结论不一致，已采用本地结论。",
                    detail=detail,
                )
            )
        elif result.result_code == "non_workday":
            warnings.append(
                SoftWarning(
                    code="calendar.non_workday",
                    message="所选日期可能不是工作日，但仍可继续填写。",
                    detail=detail,
                )
            )
        elif result.result_code == "unknown":
            warnings.append(
                SoftWarning(
                    code="calendar.unknown",
                    message="暂时无法确认所选日期是否为工作日。",
                    detail=detail,
                )
            )
        return warnings

    def capabilities_for(self, session: SessionUser, plan: PlanRecord) -> list[str]:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            associated = LessonPlanRepository(connection).is_class_teacher(
                kindergarten_id, plan.class_id, session.user.id
            )
        capabilities = {"plans:view", "plans:snapshots:view"}
        if associated and plan.archived_at is None and plan.content_schema_version == 1:
            capabilities.update({"plans:edit", "plans:archive"})
        elif "admin" in session.role_codes or associated:
            capabilities.add("plans:archive")
        return sorted(capabilities)
