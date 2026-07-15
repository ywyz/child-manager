from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    PENDING_DISPATCH = "pending_dispatch"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class JobType(StrEnum):
    AI_GENERATION = "ai.generation"
    AI_BATCH = "ai.batch"
    PROMPT_TEST = "prompt.test"
    WORD_EXPORT = "word.export"


class Job(BaseModel):
    id: str = Field(..., description="任务ID")
    type: JobType = Field(..., description="任务类型")
    status: JobStatus = Field(..., description="任务状态")
    kindergarten_id: str = Field(..., description="园所ID")
    user_id: str = Field(..., description="用户ID")
    plan_id: str | None = Field(None, description="教案ID")
    prompt_code: str | None = Field(None, description="提示词代码")
    column_name: str | None = Field(None, description="栏目名称")
    retry_of_job_id: str | None = Field(None, description="重试来源任务ID")
    parent_job_id: str | None = Field(None, description="父任务ID")
    attempt_count: int = Field(0, description="尝试次数")
    max_attempts: int = Field(3, description="最大尝试次数")
    error_summary: str | None = Field(None, description="错误摘要")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    completed_at: datetime | None = Field(None, description="完成时间")


class JobCreateRequest(BaseModel):
    type: JobType = Field(..., description="任务类型")
    plan_id: str | None = Field(None, description="教案ID")
    prompt_code: str | None = Field(None, description="提示词代码")
    column_name: str | None = Field(None, description="栏目名称")


class JobBatchCreateRequest(BaseModel):
    plan_id: str = Field(..., description="教案ID")
    columns: list[str] = Field(..., description="栏目列表")


class JobRetryRequest(BaseModel):
    job_id: str = Field(..., description="任务ID")


class JobListResponse(BaseModel):
    jobs: list[Job] = Field(..., description="任务列表")
    total: int = Field(..., description="总数")


class AIResult(BaseModel):
    id: str = Field(..., description="结果ID")
    job_id: str = Field(..., description="任务ID")
    plan_id: str = Field(..., description="教案ID")
    column_name: str = Field(..., description="栏目名称")
    baseline_hash: str = Field(..., description="基线哈希")
    input_hash: str = Field(..., description="输入哈希")
    status: str = Field(..., description="状态")
    output: dict[str, object] | None = Field(None, description="输出结果")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class AIAdoptRequest(BaseModel):
    result_id: str = Field(..., description="结果ID")
    expected_version: int = Field(..., description="期望版本号")


class WorkerMessage(BaseModel):
    """Worker 消息信封：只传 job_id，不携带 API Key、token 或正文。"""

    model_config = {"extra": "forbid"}

    job_id: str = Field(..., description="任务 ID")
