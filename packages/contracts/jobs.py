"""后台任务公共 Schema 骨架。"""

from pydantic import BaseModel, ConfigDict, Field


class WorkerMessage(BaseModel):
    """Worker 消息信封：只传 job_id，不携带 API Key、token 或正文。"""

    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(..., description="任务 ID")
