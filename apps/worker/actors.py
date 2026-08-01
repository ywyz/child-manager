"""只接收 job_id 的 Dramatiq actor 与 PostgreSQL 恢复扫描。"""

import logging
import os
import socket
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from uuid import UUID, uuid7

import dramatiq
import psycopg
from dramatiq import Retry
from dramatiq.actor import Actor
from dramatiq.broker import Broker

from packages.backend.exports.rules import TEMPLATE_SHA256
from packages.backend.exports.runner import (
    PostgresWordExportStore,
    WordExportRetry,
    WordExportRunner,
)
from packages.backend.exports.service import ExportService
from packages.backend.integrations.ai.client import ProviderNeutralAiClient
from packages.backend.integrations.ai.url_policy import validate_ai_base_url
from packages.backend.integrations.crypto.ai_keys import (
    AiKeyEnvelope,
    decrypt_api_key_with_provider,
)
from packages.backend.integrations.files.teacherplan_renderer import TeacherplanRenderer
from packages.backend.jobs.ai_results import AiGenerationResultRepository
from packages.backend.jobs.ai_runner import AiJobRetry, AiJobRunner, AiJobStore
from packages.backend.jobs.prompt_test_store import PostgresPromptTestStore
from packages.backend.jobs.scope_resolver import WorkerScopeResolver
from packages.backend.jobs.service import (
    CurrentModelCallProfile,
    PromptTestExecutor,
    PromptTestRetry,
)
from packages.backend.prompts.catalog import validate_prompt_result_schema
from packages.backend.settings.ai_models import AiModelService

logger = logging.getLogger(__name__)


class AiJobScopeResolver(Protocol):
    def kindergarten_id_for_ai_job(self, job_id: UUID) -> UUID | None: ...


class AiRunner(Protocol):
    def execute(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> None: ...


class WordJobScopeResolver(Protocol):
    def kindergarten_id_for_word_job(self, job_id: UUID) -> UUID | None: ...


class WordRunner(Protocol):
    def execute(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> None: ...


def _worker_id() -> str:
    return f"{socket.gethostname()[:64]}:{os.getpid()}:{uuid7()}"


def build_prompt_test_executor() -> PromptTestExecutor:
    settings = AiModelService.from_environment()
    store = PostgresPromptTestStore(settings.database_url)
    client = ProviderNeutralAiClient(
        resolver=settings.resolver,
        allowed_hosts=settings.allowed_hosts,
    )

    def read_api_key(profile: CurrentModelCallProfile) -> str:
        if not isinstance(profile.key_envelope, AiKeyEnvelope):
            raise LookupError("模型密钥不可用")
        return decrypt_api_key_with_provider(
            profile.key_envelope,
            key_provider=settings.key_provider,
            kindergarten_id=profile.kindergarten_id,
            profile_id=profile.profile_id,
        )

    return PromptTestExecutor(
        store=store,
        client=client,
        authorizer=store,
        read_api_key=read_api_key,
        validate_url=lambda value: validate_ai_base_url(
            value,
            resolver=settings.resolver,
            allowed_hosts=settings.allowed_hosts,
        ),
        validate_result=lambda code, result, input_context: validate_prompt_result_schema(
            code,
            result,
            input_context=input_context,
        ),
    )


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def build_ai_job_runner() -> AiJobRunner:
    settings = AiModelService.from_environment()
    connection = psycopg.connect(_native_url(settings.database_url), autocommit=True)
    store = AiJobStore(connection)
    client = ProviderNeutralAiClient(
        resolver=settings.resolver,
        allowed_hosts=settings.allowed_hosts,
    )

    def read_api_key(profile: CurrentModelCallProfile) -> str:
        if not isinstance(profile.key_envelope, AiKeyEnvelope):
            raise LookupError("模型密钥不可用")
        return decrypt_api_key_with_provider(
            profile.key_envelope,
            key_provider=settings.key_provider,
            kindergarten_id=profile.kindergarten_id,
            profile_id=profile.profile_id,
        )

    return AiJobRunner(
        store=store,
        client=client,
        authorizer=store,
        read_api_key=read_api_key,
        validate_url=lambda value: validate_ai_base_url(
            value,
            resolver=settings.resolver,
            allowed_hosts=settings.allowed_hosts,
        ),
    )


def build_ai_result_repository() -> AiGenerationResultRepository:
    settings = AiModelService.from_environment()
    connection = psycopg.connect(_native_url(settings.database_url), autocommit=True)
    return AiGenerationResultRepository(connection)


def build_word_export_runner() -> WordExportRunner:
    service = ExportService.from_environment()
    connection = psycopg.connect(_native_url(service.database_url), autocommit=True)
    template_path = Path(__file__).resolve().parents[2] / "templates/teacherplan/teacherplan.docx"
    return WordExportRunner(
        store=PostgresWordExportStore(connection),
        renderer=TeacherplanRenderer(template_path, expected_sha256=TEMPLATE_SHA256),
        storage=service.storage,
    )


def build_worker_scope_resolver() -> WorkerScopeResolver:
    settings = AiModelService.from_environment()
    connection = psycopg.connect(_native_url(settings.database_url), autocommit=True)
    return WorkerScopeResolver(connection)


class RecoveryStore(Protocol):
    def kindergarten_id_for_job(self, job_id: UUID) -> UUID | None: ...

    def recoverable_job_ids(
        self,
        *,
        now: datetime,
        limit: int,
        include_expired: bool,
    ) -> list[UUID]: ...

    def mark_prompt_test_dispatched(self, kindergarten_id: UUID, job_id: UUID) -> None: ...


def recover_prompt_test_jobs(
    store: RecoveryStore,
    *,
    dispatch: Callable[[UUID], None],
    now: datetime | None = None,
    limit: int = 100,
    include_expired: bool = True,
) -> int:
    """按 PostgreSQL 权威状态重投 pending/过期租约任务。"""

    job_ids = store.recoverable_job_ids(
        now=now or datetime.now(UTC),
        limit=limit,
        include_expired=include_expired,
    )
    dispatched = 0
    for job_id in job_ids:
        try:
            dispatch(job_id)
        except Exception:
            logger.error("提示词测试恢复投递失败", extra={"job_id": str(job_id)})
            continue
        dispatched += 1
        kindergarten_id = store.kindergarten_id_for_job(job_id)
        if kindergarten_id is None:
            logger.error("提示词测试恢复状态缺少园所", extra={"job_id": str(job_id)})
            continue
        try:
            store.mark_prompt_test_dispatched(kindergarten_id, job_id)
        except Exception:
            logger.error("提示词测试恢复状态更新失败", extra={"job_id": str(job_id)})
    return dispatched


def register_actors(
    broker: Broker,
    *,
    executor: PromptTestExecutor | None = None,
    ai_runner: AiRunner | None = None,
    ai_job_scope_resolver: AiJobScopeResolver | None = None,
    word_runner: WordRunner | None = None,
    word_job_scope_resolver: WordJobScopeResolver | None = None,
) -> tuple[Actor[..., str], ...]:
    def run_prompt_test(job_id: str) -> str:
        parsed_job_id = UUID(job_id)
        if executor is not None:
            try:
                executor.execute_job(parsed_job_id, worker_id=_worker_id())
            except PromptTestRetry as exc:
                raise Retry(delay=exc.delay_seconds * 1000) from None
        return str(parsed_job_id)

    prompt_actor = dramatiq.actor(
        actor_name="prompt_test",
        broker=broker,
        max_retries=3,
        min_backoff=5000,
        max_backoff=30000,
    )(run_prompt_test)

    def run_ai_job(job_id: str) -> str:
        parsed_job_id = UUID(job_id)
        if ai_runner is not None and ai_job_scope_resolver is not None:
            kindergarten_id = ai_job_scope_resolver.kindergarten_id_for_ai_job(parsed_job_id)
            if kindergarten_id is not None:
                try:
                    ai_runner.execute(
                        kindergarten_id,
                        parsed_job_id,
                        worker_id=_worker_id(),
                    )
                except AiJobRetry as exc:
                    raise Retry(delay=exc.delay_seconds * 1000) from None
        return str(parsed_job_id)

    ai_actor = dramatiq.actor(
        actor_name="ai_job",
        broker=broker,
        max_retries=3,
        min_backoff=5000,
        max_backoff=30000,
    )(run_ai_job)
    actors: list[Actor[..., str]] = [prompt_actor, ai_actor]
    if word_runner is not None or word_job_scope_resolver is not None:

        def run_word_export(job_id: str) -> str:
            parsed_job_id = UUID(job_id)
            if word_runner is not None and word_job_scope_resolver is not None:
                kindergarten_id = word_job_scope_resolver.kindergarten_id_for_word_job(
                    parsed_job_id
                )
                if kindergarten_id is not None:
                    try:
                        word_runner.execute(
                            kindergarten_id,
                            parsed_job_id,
                            worker_id=_worker_id(),
                        )
                    except WordExportRetry as exc:
                        raise Retry(delay=exc.delay_seconds * 1000) from None
            return str(parsed_job_id)

        actors.append(
            dramatiq.actor(
                actor_name="word_export",
                broker=broker,
                max_retries=3,
                min_backoff=5000,
                max_backoff=30000,
            )(run_word_export)
        )
    return tuple(actors)
