"""身份与认证公共 Schema。"""

from pydantic import BaseModel, ConfigDict, Field


class CurrentUser(BaseModel):
    """当前登录用户的最小引用。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    display_name: str = Field(..., description="显示名称")
    roles: list[str] = Field(default_factory=list, description="角色代码列表")


class CsrfResponse(BaseModel):
    """CSRF 令牌响应。"""

    model_config = ConfigDict(extra="forbid")

    csrf_token: str = Field(..., description="CSRF 令牌")


class LoginRequest(BaseModel):
    """登录请求。"""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., description="用户名或手机号")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应。"""

    model_config = ConfigDict(extra="forbid")

    user: CurrentUser = Field(..., description="当前用户信息")


class RefreshRequest(BaseModel):
    """刷新请求。"""

    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(..., description="Refresh 令牌")


class ChangePasswordRequest(BaseModel):
    """修改密码请求。"""

    model_config = ConfigDict(extra="forbid")

    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., description="新密码")


class UserCreateRequest(BaseModel):
    """创建用户请求。"""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., description="用户名")
    display_name: str = Field(..., description="显示名称")
    phone: str | None = Field(None, description="手机号")
    roles: list[str] = Field(default_factory=list, description="角色代码列表")
    initial_password: str = Field(..., description="初始密码")


class UserResponse(BaseModel):
    """用户响应。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    display_name: str = Field(..., description="显示名称")
    phone: str | None = Field(None, description="手机号")
    roles: list[str] = Field(default_factory=list, description="角色代码列表")
    is_active: bool = Field(..., description="是否启用")


class ResetPasswordRequest(BaseModel):
    """重置密码请求。"""

    model_config = ConfigDict(extra="forbid")

    new_password: str = Field(..., description="新密码")
