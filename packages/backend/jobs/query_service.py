"""后台任务权威状态查询用例。"""

from __future__ import annotations

import os
from uuid import UUID

import psycopg

from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.jobs.repository import JobRecord, JobRepository


class JobQueryService:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    @classmethod
    def from_environment(cls) -> JobQueryService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
        return cls(database_url)

    def get(self, session: SessionUser, job_id: UUID) -> JobRecord:
        kindergarten_id = session.user.kindergarten_id
        if kindergarten_id is None:
            raise IdentityError(403, "auth.forbidden", "当前账号不属于可用园所。")
        native_url = self.database_url.replace(
            "postgresql+psycopg://",
            "postgresql://",
            1,
        )
        with psycopg.connect(native_url) as connection:
            record = JobRepository(connection).get(kindergarten_id, job_id)
        if record is None:
            raise IdentityError(404, "resource.not_found", "任务不存在。")
        return record
