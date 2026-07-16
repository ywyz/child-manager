"""审计事件公共 Schema 骨架。"""

from pydantic import BaseModel, ConfigDict, Field


class AuditEventReference(BaseModel):
    """审计事件的最小引用型骨架。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="事件ID")
    event_type: str = Field(..., description="事件类型")
