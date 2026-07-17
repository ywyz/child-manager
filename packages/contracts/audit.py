"""审计事件公共 Schema 骨架。"""

from pydantic import BaseModel, ConfigDict, Field


class AuditEventReference(BaseModel):
    """审计事件的最小引用型骨架。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="事件ID")
    event_type: str = Field(..., description="事件类型")


# 身份审计事件类型常量
IDENTITY_INIT_ADMIN = "identity.init_admin"
IDENTITY_LOGIN = "identity.login"
IDENTITY_REFRESH = "identity.refresh"
IDENTITY_TOKEN_REPLAY = "identity.token_replay"
IDENTITY_LOGOUT = "identity.logout"
IDENTITY_CHANGE_PASSWORD = "identity.change_password"
IDENTITY_RESET_PASSWORD = "identity.reset_password"
IDENTITY_CREATE_USER = "identity.create_user"
IDENTITY_DEACTIVATE_USER = "identity.deactivate_user"

# 审计资源类型常量
RESOURCE_TYPE_USER = "user"
RESOURCE_TYPE_ACCOUNT = "account"
RESOURCE_TYPE_KINDERGARTEN = "kindergarten"

# 审计结果常量
RESULT_SUCCESS = "success"
RESULT_FAILURE = "failure"
