"""一日活动计划公共 Schema 骨架。"""

from datetime import date
from uuid import UUID

from packages.contracts.common import ContractModel


class LessonPlanReference(ContractModel):
    id: UUID
    class_id: UUID
    plan_date: date
    version: int
