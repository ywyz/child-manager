"""Word 导出公共 Schema 骨架。"""

from uuid import UUID

from packages.contracts.common import ContractModel


class ExportReference(ContractModel):
    export_id: UUID
    job_id: UUID
