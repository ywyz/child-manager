"""只接收 job_id 的 Dramatiq actor 与 PostgreSQL 恢复扫描。"""

import os
import socket
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

import dramatiq
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
)
from packages.backend.prompts.catalog import validate_prompt_result_schema
from packages.backend.settings.ai_models import AiModelService


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
    def recoverable_job_ids(self, *, now: datetime, limit: int) -> list[UUID]: ...


def recover_prompt_test_jobs(
    store: RecoveryStore,
    *,
    dispatch: Callable[[UUID], None],
    now: datetime | None = None,
    limit: int = 100,
) -> int:
    """按 PostgreSQL 权威状态重投 pending/过期租约任务。"""

    job_ids = store.recoverable_job_ids(now=now or datetime.now(UTC), limit=limit)
    for job_id in job_ids:
        dispatch(job_id)
    return len(job_ids)


def register_actors(
    broker: Broker,
    *,
    executor: PromptTestExecutor | None = None,
) -> tuple[Actor[..., str], ...]:
    def run_prompt_test(job_id: str) -> str:
        parsed_job_id = UUID(job_id)
        if executor is not None:
            executor.execute_job(parsed_job_id, worker_id=_worker_id())
        return str(parsed_job_id)

    actor = dramatiq.actor(
        actor_name="prompt_test",
        broker=broker,
        max_retries=2,
        min_backoff=1000,
        max_backoff=2000,
    )(run_prompt_test)
    return (actor,)
