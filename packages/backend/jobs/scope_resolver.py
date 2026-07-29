"""Worker 最小消息进入逐园业务操作前的受控园所解析边界。"""

from __future__ import annotations

from typing import Any
from uuid import UUID


class WorkerScopeResolver:
    """只返回园所 ID，不读取或返回跨园业务正文。"""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def kindergarten_id_for_ai_job(self, job_id: UUID) -> UUID | None:
        row = self.connection.execute(
            """SELECT kindergarten_id FROM background_jobs
            WHERE id=%s AND job_type LIKE 'ai.%%' AND job_type<>'ai.batch'""",
            (job_id,),
        ).fetchone()
        return UUID(str(row[0])) if row is not None else None

    def active_kindergarten_ids(self) -> list[UUID]:
        result = self.connection.execute(
            """SELECT id FROM kindergartens
            WHERE is_active
            ORDER BY id"""
        )
        return [UUID(str(row[0])) for row in result.fetchall()]
