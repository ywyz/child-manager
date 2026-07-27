"""只接收 job_id 的 Dramatiq actor 与 PostgreSQL 恢复扫描。"""

import logging
import os
import socket
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

import dramatiq
from dramatiq import Retry
from dramatiq.actor import Actor
from dramatiq.broker import Broker

from packages.backend.integrations.ai.client import ProviderNeutralAiClient
from packages.backend.integrations.ai.url_policy import validate_ai_base_url
from packages.backend.integrations.crypto.ai_keys import (
    AiKeyEnvelope,
    decrypt_api_key_with_provider,
)
from packages.backend.jobs.prompt_test_store import PostgresPromptTestStore
from packages.backend.jobs.service import (
    CurrentModelCallProfile,
    PromptTestExecutor,
    PromptTestRetry,
)
from packages.backend.prompts.catalog import validate_prompt_result_schema
from packages.backend.settings.ai_models import AiModelService

logger = logging.getLogger(__name__)


def _worker_id() -> str:
    return f"{socket.gethostname()}:{os.getpid()}"


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
        validate_result=validate_prompt_result_schema,
    )


class RecoveryStore(Protocol):
    def recoverable_job_ids(
        self,
        *,
        now: datetime,
        limit: int,
        include_expired: bool,
    ) -> list[UUID]: ...


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
    return dispatched


def register_actors(
    broker: Broker,
    *,
    executor: PromptTestExecutor | None = None,
) -> tuple[Actor[..., str], ...]:
    def run_prompt_test(job_id: str) -> str:
        parsed_job_id = UUID(job_id)
        if executor is not None:
            try:
                executor.execute_job(parsed_job_id, worker_id=_worker_id())
            except PromptTestRetry as exc:
                raise Retry(delay=exc.delay_seconds * 1000) from None
        return str(parsed_job_id)

    actor = dramatiq.actor(
        actor_name="prompt_test",
        broker=broker,
        max_retries=3,
        min_backoff=5000,
        max_backoff=30000,
    )(run_prompt_test)
    return (actor,)
