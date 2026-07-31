"""`ai.batch` 父任务的只读状态投影。"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from packages.backend.jobs.repository import JobRepository
from packages.contracts.jobs import Job, JobChild, derive_batch_projection


class BatchJobAggregationRepository:
    """从恰好四个子任务派生父任务响应，不写入父任务执行字段。"""

    def __init__(self, connection: Any) -> None:
        self.jobs = JobRepository(connection)

    def get(self, kindergarten_id: UUID, parent_job_id: UUID) -> Job | None:
        parent = self.jobs.get_ai(kindergarten_id, parent_job_id)
        if parent is None or parent.job_type != "ai.batch":
            return None
        children = [
            JobChild.model_validate(
                {
                    "id": child.id,
                    "job_type": child.job_type,
                    "status": child.status,
                    "target_section": child.target_section,
                    "error_code": child.error_code,
                }
            )
            for child in self.jobs.list_ai_children(kindergarten_id, parent_job_id)
        ]
        status, has_partial_failure = derive_batch_projection(children)
        return Job.model_validate(
            {
                "id": parent.id,
                "job_type": parent.job_type,
                "status": status,
                "parent_job_id": parent.parent_job_id,
                "retry_of_job_id": parent.retry_of_job_id,
                "plan_id": parent.plan_id,
                "target_section": parent.target_section,
                "requested_resource_version": parent.requested_resource_version,
                "attempt_count": 0,
                "max_attempts": 0,
                "trace_id": parent.trace_id,
                "created_at": parent.created_at,
                "queued_at": None,
                "started_at": None,
                "finished_at": None,
                "error_code": None,
                "error_message": None,
                "has_partial_failure": has_partial_failure,
                "children": children,
            }
        )
