from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    phone: str | None = Field(None, description="手机号(E.164)")
    email: EmailStr | None = Field(None, description="邮箱")
    full_name: str | None = Field(None, description="全名")
    is_active: bool = Field(..., description="是否活跃")
    kindergarten_id: str = Field(..., description="园所ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class UserCreate(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    phone: str | None = Field(None, description="手机号")
    email: EmailStr | None = Field(None, description="邮箱")
    full_name: str | None = Field(None, description="全名")


class UserUpdate(BaseModel):
    phone: str | None = Field(None, description="手机号")
    email: EmailStr | None = Field(None, description="邮箱")
    full_name: str | None = Field(None, description="全名")
    is_active: bool | None = Field(None, description="是否活跃")


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名或手机号")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    user: User = Field(..., description="用户信息")
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field("bearer", description="令牌类型")


class TokenRefreshResponse(BaseModel):
    access_token: str = Field(..., description="新访问令牌")
    token_type: str = Field("bearer", description="令牌类型")


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码")


class Role(BaseModel):
    id: str = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")
    description: str | None = Field(None, description="角色描述")
    kindergarten_id: str = Field(..., description="园所ID")


class UserRole(BaseModel):
    user_id: str = Field(..., description="用户ID")
    role_id: str = Field(..., description="角色ID")
    assigned_at: datetime = Field(..., description="分配时间")
