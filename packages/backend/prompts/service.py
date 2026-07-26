"""提示词生命周期与冻结异步测试事务编排。"""

from __future__ import annotations

import os
from contextlib import suppress
from typing import Any, Protocol
from uuid import UUID, uuid7

import psycopg
from pydantic import ValidationError

from packages.backend.audit.repository import AuditRepository
from packages.backend.identity.service import IdentityError, IdentityService, SessionUser
from packages.backend.jobs.repository import JobRecord, JobRepository
from packages.backend.prompts.catalog import validate_prompt_variables
from packages.backend.prompts.renderer import (
    PromptTemplateError,
    render_prompt,
    validate_prompt_template,
)
from packages.backend.prompts.repository import (
    PromptDefinitionRecord,
    PromptRepository,
    PromptTestRunRecord,
    PromptVersionRecord,
)
from packages.contracts.audit import IdentityAuditEventCode
from packages.contracts.common import canonical_request_fingerprint
from packages.contracts.prompts import PromptTestRequest


class Dispatcher(Protocol):
    def dispatch(self, job_id: UUID) -> None: ...


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


class PromptService:
    def __init__(self, *, database_url: str, dispatcher: Dispatcher | None = None) -> None:
        self.database_url = database_url
        self.dispatcher = dispatcher

    @classmethod
    def from_environment(cls) -> PromptService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
        return cls(database_url=database_url)

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    @staticmethod
    def _scope(session: SessionUser) -> UUID:
        IdentityService.require_admin(session)
        if session.user.kindergarten_id is None:
            raise IdentityError(403, "auth.forbidden", "当前账号不属于可用园所。")
        return session.user.kindergarten_id

    @staticmethod
    def _missing(resource: str) -> IdentityError:
        return IdentityError(404, "resource.not_found", f"{resource}不存在。")

    def list_definitions(
        self, session: SessionUser, *, page: int, page_size: int
    ) -> tuple[list[PromptDefinitionRecord], int]:
        kindergarten_id = self._scope(session)
        with self._connect() as connection, connection.transaction():
            repository = PromptRepository(connection)
            repository.ensure_defaults(kindergarten_id)
            return repository.list_definitions(kindergarten_id, page=page, page_size=page_size)

    def get_definition(self, session: SessionUser, code: str) -> PromptDefinitionRecord:
        kindergarten_id = self._scope(session)
        with self._connect() as connection, connection.transaction():
            repository = PromptRepository(connection)
            repository.ensure_defaults(kindergarten_id)
            record = repository.get_definition(kindergarten_id, code)
        if record is None:
            raise self._missing("提示词")
        return record

    def save_draft(
        self,
        session: SessionUser,
        code: str,
        *,
        content: str,
        based_on_version_id: UUID | None,
    ) -> PromptVersionRecord:
        kindergarten_id = self._scope(session)
        try:
            with self._connect() as connection, connection.transaction():
                repository = PromptRepository(connection)
                repository.ensure_defaults(kindergarten_id)
                definition = repository.get_definition(kindergarten_id, code, for_update=True)
                if definition is None:
                    raise self._missing("提示词")
                validate_prompt_template(content, set(definition.variable_whitelist))
                if (
                    based_on_version_id is not None
                    and repository.get_version(kindergarten_id, code, based_on_version_id) is None
                ):
                    raise self._missing("提示词版本")
                return repository.save_draft(
                    kindergarten_id,
                    definition.id,
                    code=code,
                    content=content,
                    based_on_version_id=based_on_version_id,
                    actor_id=session.user.id,
                )
        except PromptTemplateError as exc:
            raise IdentityError(422, exc.code, str(exc)) from exc

    def publish(self, session: SessionUser, code: str) -> PromptVersionRecord:
        kindergarten_id = self._scope(session)
        try:
            with self._connect() as connection, connection.transaction():
                repository = PromptRepository(connection)
                definition = repository.get_definition(kindergarten_id, code, for_update=True)
                if definition is None:
                    raise self._missing("提示词")
                if definition.draft_version_id is None:
                    raise IdentityError(409, "prompt.no_draft", "当前没有可发布的草稿。")
                draft = repository.get_version(kindergarten_id, code, definition.draft_version_id)
                assert draft is not None
                validate_prompt_template(draft.content, set(definition.variable_whitelist))
                record = repository.publish_draft(
                    kindergarten_id,
                    definition.id,
                    code=code,
                    actor_id=session.user.id,
                )
                assert record is not None
                AuditRepository(connection, kindergarten_id).append(
                    event_code=IdentityAuditEventCode.PROMPT_PUBLISHED,
                    actor_user_id=session.user.id,
                    actor_role_codes=list(session.role_codes),
                    resource_type="prompt_version",
                    resource_id=record.id,
                    outcome="success",
                )
                return record
        except PromptTemplateError as exc:
            raise IdentityError(422, exc.code, str(exc)) from exc

    def list_versions(
        self,
        session: SessionUser,
        code: str,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[PromptVersionRecord], int]:
        kindergarten_id = self._scope(session)
        with self._connect() as connection:
            repository = PromptRepository(connection)
            if repository.get_definition(kindergarten_id, code) is None:
                raise self._missing("提示词")
            return repository.list_versions(kindergarten_id, code, page=page, page_size=page_size)

    def get_version(self, session: SessionUser, code: str, version_id: UUID) -> PromptVersionRecord:
        kindergarten_id = self._scope(session)
        with self._connect() as connection:
            record = PromptRepository(connection).get_version(kindergarten_id, code, version_id)
        if record is None:
            raise self._missing("提示词版本")
        return record

    def restore(self, session: SessionUser, code: str, version_id: UUID) -> PromptVersionRecord:
        kindergarten_id = self._scope(session)
        with self._connect() as connection, connection.transaction():
            repository = PromptRepository(connection)
            definition = repository.get_definition(kindergarten_id, code, for_update=True)
            if definition is None:
                raise self._missing("提示词")
            record = repository.restore_version(
                kindergarten_id,
                definition.id,
                version_id,
                code=code,
                actor_id=session.user.id,
            )
            if record is None:
                raise self._missing("提示词版本")
            AuditRepository(connection, kindergarten_id).append(
                event_code=IdentityAuditEventCode.PROMPT_RESTORED,
                actor_user_id=session.user.id,
                actor_role_codes=list(session.role_codes),
                resource_type="prompt_version",
                resource_id=record.id,
                outcome="success",
            )
            return record

    def create_test(
        self,
        session: SessionUser,
        code: str,
        body: PromptTestRequest,
        *,
        idempotency_key: str,
        request_id: UUID | None,
    ) -> tuple[JobRecord, PromptTestRunRecord]:
        kindergarten_id = self._scope(session)
        scope = "POST /api/v1/prompts/{code}/tests"
        fingerprint = canonical_request_fingerprint(
            method="POST",
            route_template="/api/v1/prompts/{code}/tests",
            path_params={"code": code},
            query_params=[],
            body=body.model_dump(mode="json"),
        )
        job_id: UUID | None = None
        try:
            with self._connect() as connection, connection.transaction():
                jobs = JobRepository(connection)
                prompts = PromptRepository(connection)
                existing = jobs.find_idempotent(
                    kindergarten_id,
                    requested_by=session.user.id,
                    scope=scope,
                    key=idempotency_key,
                )
                if existing is not None:
                    if existing.request_fingerprint_sha256 != fingerprint:
                        raise IdentityError(
                            409,
                            "job.idempotency_conflict",
                            "幂等键已用于不同请求。",
                        )
                    run = prompts.get_prompt_test_run_by_job(kindergarten_id, existing.id)
                    assert run is not None
                    return existing, run
                prompts.ensure_defaults(kindergarten_id)
                definition = prompts.get_definition(kindergarten_id, code, for_update=True)
                if definition is None:
                    raise self._missing("提示词")
                if prompts.unfinished_count(kindergarten_id, definition.id) >= 20:
                    raise IdentityError(
                        409,
                        "prompt.too_many_active_tests",
                        "当前提示词已有过多未完成测试。",
                    )
                version = prompts.get_version(kindergarten_id, code, body.version_id)
                if version is None or version.lifecycle_state != "published":
                    raise IdentityError(
                        422,
                        "prompt.version_unavailable",
                        "只能测试已发布提示词版本。",
                    )
                try:
                    input_context = validate_prompt_variables(code, body.variables)
                    render_prompt(
                        version.content,
                        input_context,
                        set(definition.variable_whitelist),
                    )
                except (ValidationError, PromptTemplateError) as exc:
                    raise IdentityError(
                        422, "prompt.invalid_input", "提示词测试输入无效。"
                    ) from exc
                profile_row: Any = connection.execute(
                    """SELECT p.api_base_url,p.model_name,p.call_config_revision,p.is_active,
                    COALESCE(array_agg(c.capability_code ORDER BY c.capability_code)
                      FILTER (WHERE c.capability_code IS NOT NULL),ARRAY[]::varchar[])
                    FROM ai_model_profiles p LEFT JOIN ai_model_profile_capabilities c
                      ON c.kindergarten_id=p.kindergarten_id AND c.model_profile_id=p.id
                    WHERE p.kindergarten_id=%s AND p.id=%s GROUP BY p.id""",
                    (kindergarten_id, body.model_profile_id),
                ).fetchone()
                if profile_row is None or not bool(profile_row[3]):
                    raise IdentityError(422, "prompt.model_unavailable", "模型档案当前不可用。")
                if not set(definition.required_capabilities) <= set(profile_row[4]):
                    raise IdentityError(
                        422, "prompt.model_capability_missing", "模型能力不满足提示词要求。"
                    )
                job_id = uuid7()
                run_id = uuid7()
                trace_id = uuid7()
                job = jobs.create_prompt_test(
                    kindergarten_id,
                    job_id=job_id,
                    requested_by=session.user.id,
                    request_id=request_id,
                    trace_id=trace_id,
                    scope=scope,
                    key=idempotency_key,
                    fingerprint=fingerprint,
                )
                prompts.create_prompt_test_run(
                    kindergarten_id,
                    run_id=run_id,
                    definition_id=definition.id,
                    version_id=version.id,
                    profile_id=body.model_profile_id,
                    job_id=job_id,
                    input_context=input_context,
                    prompt_content=version.content,
                    result_schema_code=definition.result_schema_code,
                    result_schema_version=definition.result_schema_version,
                    model_call_snapshot={
                        "profile_id": str(body.model_profile_id),
                        "base_url": str(profile_row[0]),
                        "model_name": str(profile_row[1]),
                        "capabilities": list(profile_row[4]),
                        "call_config_revision": int(profile_row[2]),
                    },
                    actor_id=session.user.id,
                )
                run = prompts.get_prompt_test_run(kindergarten_id, code, run_id)
                assert run is not None
        except psycopg.OperationalError as exc:
            raise IdentityError(503, "database.unavailable", "数据库暂不可用。") from exc
        assert job_id is not None
        if self.dispatcher is not None:
            with suppress(Exception):
                self.dispatcher.dispatch(job_id)
        return job, run

    def get_test(self, session: SessionUser, code: str, run_id: UUID) -> PromptTestRunRecord:
        kindergarten_id = self._scope(session)
        with self._connect() as connection:
            record = PromptRepository(connection).get_prompt_test_run(kindergarten_id, code, run_id)
        if record is None:
            raise self._missing("提示词测试")
        return record

    def list_tests(
        self,
        session: SessionUser,
        code: str,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[PromptTestRunRecord], int]:
        kindergarten_id = self._scope(session)
        with self._connect() as connection:
            repository = PromptRepository(connection)
            definition = repository.get_definition(kindergarten_id, code)
            if definition is None:
                raise self._missing("提示词")
            return repository.list_prompt_test_runs(
                kindergarten_id, definition.id, page=page, page_size=page_size
            )

    def clear_tests(self, session: SessionUser, code: str) -> int:
        kindergarten_id = self._scope(session)
        with self._connect() as connection, connection.transaction():
            repository = PromptRepository(connection)
            definition = repository.get_definition(kindergarten_id, code)
            if definition is None:
                raise self._missing("提示词")
            deleted = repository.clear_finished_prompt_test_runs(kindergarten_id, definition.id)
            AuditRepository(connection, kindergarten_id).append(
                event_code=IdentityAuditEventCode.PROMPT_TESTS_CLEARED,
                actor_user_id=session.user.id,
                actor_role_codes=list(session.role_codes),
                resource_type="prompt_definition",
                resource_id=definition.id,
                outcome="success",
            )
            return deleted
