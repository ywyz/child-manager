"""身份与认证公共 Schema 骨架。"""

from uuid import UUID

from packages.contracts.common import ContractModel


class CurrentUser(ContractModel):
    id: UUID
    username: str
    display_name: str
    roles: list[str]
