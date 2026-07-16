"""一日活动计划公共 Schema 骨架。"""

from pydantic import BaseModel, ConfigDict, Field


class LessonPlanReference(BaseModel):
    """教案的最小引用型骨架。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="教案ID")
    class_id: str = Field(..., description="班级ID")
    plan_date: str = Field(..., description="活动日期")
