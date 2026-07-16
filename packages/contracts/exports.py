"""Word 导出公共 Schema 骨架。"""

from pydantic import BaseModel, ConfigDict, Field


class ExportReference(BaseModel):
    """导出记录的最小引用型骨架。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="导出记录ID")
    plan_id: str = Field(..., description="教案ID")
