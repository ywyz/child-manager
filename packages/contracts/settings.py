"""首期必要设置公共 Schema 骨架。"""

from uuid import UUID

from packages.contracts.common import ContractModel


class KindergartenSummary(ContractModel):
    id: UUID
    name: str
    timezone: str = "Asia/Shanghai"
