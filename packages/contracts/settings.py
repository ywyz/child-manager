"""首期必要设置公共 Schema 骨架。"""

from pydantic import BaseModel, ConfigDict, Field


class KindergartenSummary(BaseModel):
    """园所设置的最小引用型骨架。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="园所ID")
    name: str = Field(..., description="园所名称")
    timezone: str = Field("Asia/Shanghai", description="时区")
