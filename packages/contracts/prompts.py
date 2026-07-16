"""提示词管理公共 Schema 骨架。"""

from pydantic import BaseModel, ConfigDict, Field


class PromptReference(BaseModel):
    """提示词定义的最小引用型骨架。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="提示词ID")
    code: str = Field(..., description="稳定标识")
