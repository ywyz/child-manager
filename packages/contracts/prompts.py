"""提示词管理公共 Schema 骨架。"""

from packages.contracts.common import ContractModel


class PromptReference(ContractModel):
    code: str
    required_capabilities: list[str]
