"""审计事件公共 Schema 骨架。"""

from packages.contracts.common import ContractModel, ResourceReference


class AuditEventReference(ContractModel):
    event_code: str
    resource: ResourceReference | None = None
