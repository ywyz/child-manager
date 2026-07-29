"""后台任务公共 Schema。"""

from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import Field, model_validator

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

EXECUTABLE_AI_JOB_TYPES = frozenset(
    {
        "ai.morning_activity",
        "ai.morning_talk",
        "ai.group_activity_split",
        "ai.group_activity_add_step",
        "ai.indoor_area_game",
        "ai.afternoon_outdoor_game",
        "ai.daily_reflection",
    }
)
JOB_RETRY_NOT_ALLOWED = "job.retry_not_allowed"


class JobChild(ContractModel):
    id: UUID
    job_type: JobType
    status: JobStatus
    target_section: str | None = None
    error_code: str | None = None


def derive_batch_projection(children: Sequence[JobChild]) -> tuple[JobStatus, bool]:
    """从四个子任务实时派生 batch 展示状态，不保存第二套执行状态。"""

    if len(children) != 4:
        raise ValueError("ai.batch 必须恰好包含四个子任务")
    expected_types = {
        "ai.morning_activity",
        "ai.morning_talk",
        "ai.indoor_area_game",
        "ai.afternoon_outdoor_game",
    }
    if {child.job_type for child in children} != expected_types:
        raise ValueError("ai.batch 子任务必须是固定四栏且各不重复")

    statuses = {child.status for child in children}
    has_failure = "failed" in statuses
    has_partial_failure = has_failure and statuses != {"failed"}
    for active_status in ("running", "retrying", "queued", "pending_dispatch"):
        if active_status in statuses:
            return active_status, has_partial_failure  # type: ignore[return-value]
    if statuses == {"failed"}:
        return "failed", False
    completed = {
        "awaiting_confirmation",
        "adopted",
        "rejected",
        "expired",
        "failed",
    }
    if statuses <= completed:
        return "succeeded", has_partial_failure
    raise ValueError("ai.batch 子任务状态无法派生")


def is_explicit_ai_retry_allowed(
    *,
    job_type: str,
    status: str,
    has_ai_result: bool,
) -> bool:
    return job_type in EXECUTABLE_AI_JOB_TYPES and status == "failed" and has_ai_result


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
    children: Annotated[list[JobChild], Field(max_length=4)] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_job_shape(self) -> Job:
        if self.job_type == "ai.batch":
            if self.attempt_count != 0 or self.max_attempts != 0:
                raise ValueError("ai.batch API attempt 必须固定投影为 0/0")
            status, has_partial_failure = derive_batch_projection(self.children)
            if self.status != status or self.has_partial_failure != has_partial_failure:
                raise ValueError("ai.batch 状态必须由四个子任务派生")
            return self

        if self.children:
            raise ValueError("只有 ai.batch 可以包含子任务")
        if not 1 <= self.max_attempts <= 3:
            raise ValueError("可执行任务 max_attempts 必须在 1 到 3 之间")
        if not 0 <= self.attempt_count <= self.max_attempts:
            raise ValueError("attempt_count 不能超过 max_attempts")
        if self.job_type in EXECUTABLE_AI_JOB_TYPES and self.max_attempts != 3:
            raise ValueError("执行型 AI 任务 max_attempts 必须为 3")
        return self


class JobAccepted(ContractModel):
    job: Job
    related_resource_id: UUID | None = None


class JobPage(ContractModel):
    items: list[Job] = Field(default_factory=list)
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1, le=100)]
    total: Annotated[int, Field(ge=0)]


class JobPreview(ContractModel):
    job_id: UUID
    target_section: str
    result_schema_code: str
    result_schema_version: Annotated[int, Field(ge=1)]
    output_content: dict[str, Any]
    expires_at: datetime
    warnings: list[dict[str, Any]] = Field(default_factory=list)
