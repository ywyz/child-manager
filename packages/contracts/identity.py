"""身份与认证公共 Schema。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CurrentUser(BaseModel):
    """当前登录用户的最小引用。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    display_name: str = Field(..., description="显示名称")
    kindergarten_id: str = Field(..., description="所属园所ID")
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
    phone_e164: str | None = Field(None, description="手机号(E.164)")
    role_codes: list[str] = Field(default_factory=list, description="角色代码列表")
    password: str = Field(..., description="初始密码")


class UserPatch(BaseModel):
    """修改账号非凭证字段请求。"""

    model_config = ConfigDict(extra="forbid")

    username: str | None = Field(None, description="用户名")
    display_name: str | None = Field(None, description="显示名称")
    phone_e164: str | None = Field(None, description="手机号(E.164)")


class UserResponse(BaseModel):
    """用户响应。"""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    display_name: str = Field(..., description="显示名称")
    phone_e164: str | None = Field(None, description="手机号(E.164)")
    role_codes: list[str] = Field(default_factory=list, description="角色代码列表")
    is_active: bool = Field(..., description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class UserPage(BaseModel):
    """用户分页响应。"""

    model_config = ConfigDict(extra="forbid")

    items: list[UserResponse] = Field(default_factory=list, description="账号列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total: int = Field(..., description="总记录数")


class ResetPasswordRequest(BaseModel):
    """重置密码请求。"""

    model_config = ConfigDict(extra="forbid")

    new_password: str = Field(..., description="新密码")


class UserRolesUpdateRequest(BaseModel):
    """设置账号角色请求。"""

    model_config = ConfigDict(extra="forbid")

    role_codes: list[str] = Field(..., description="角色代码列表")
