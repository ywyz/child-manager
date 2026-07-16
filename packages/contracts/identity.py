"""身份与认证公共 Schema 骨架。"""

from pydantic import BaseModel, ConfigDict, Field


class CurrentUser(BaseModel):
    """当前登录用户的最小引用型骨架。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    display_name: str = Field(..., description="显示名称")
    roles: list[str] = Field(default_factory=list, description="角色代码列表")
