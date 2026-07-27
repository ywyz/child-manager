"""后台任务公共 Schema。"""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field

from packages.contracts.common import ContractModel


class JobMessage(ContractModel):
    """Redis 中唯一允许传递的最小任务消息。"""

    job_id: UUID


JobType = Literal[
    "ai.batch",
    "ai.morning_activity",
    "ai.morning_talk",
    "ai.group_activity_split",
    "ai.group_activity_add_step",
    "ai.indoor_area_game",
    "ai.afternoon_outdoor_game",
    "ai.daily_reflection",
    "prompt.test",
    "word.export",
]
JobStatus = Literal[
    "pending_dispatch",
    "queued",
    "running",
    "retrying",
    "awaiting_confirmation",
    "succeeded",
    "failed",
    "adopted",
    "rejected",
    "expired",
]


class Job(ContractModel):
    id: UUID
    job_type: JobType
    status: JobStatus
    parent_job_id: UUID | None = None
    retry_of_job_id: UUID | None = None
    plan_id: UUID | None = None
    target_section: str | None = None
    requested_resource_version: int | None = None
    attempt_count: Annotated[int, Field(ge=0, le=3)]
    max_attempts: Annotated[int, Field(ge=0, le=3)]
    trace_id: UUID
    created_at: datetime
    queued_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_code: str | None = None
    error_message: Annotated[str, Field(max_length=1000)] | None = None
    has_partial_failure: bool = False
    poll_after_ms: Annotated[int, Field(ge=1000, le=2000)] = 1500
    children: list[dict[str, object]] = Field(default_factory=list)


class JobAccepted(ContractModel):
    job: Job
    related_resource_id: UUID | None = None
