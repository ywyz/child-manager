"""后台任务公共 Schema 骨架。"""

from uuid import UUID

from packages.contracts.common import ContractModel


class JobMessage(ContractModel):
    """Redis 中唯一允许传递的最小任务消息。"""

    job_id: UUID
