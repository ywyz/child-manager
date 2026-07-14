from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ModelCapability(StrEnum):
    TEXT = "text"
    VISION = "vision"
    STRUCTURED_OUTPUT = "structured_output"


class ModelProfile(BaseModel):
    id: str = Field(..., description="模型档案ID")
    name: str = Field(..., description="模型名称")
    base_url: str = Field(..., description="API基础URL")
    api_key_id: str = Field(..., description="密钥ID")
    model_name: str = Field(..., description="模型名称")
    capabilities: list[ModelCapability] = Field(..., description="能力列表")
    is_active: bool = Field(False, description="是否启用")
    kindergarten_id: str = Field(..., description="园所ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    enabled_at: datetime | None = Field(None, description="启用时间")
    enabled_by: str | None = Field(None, description="启用人")


class ModelProfileCreateRequest(BaseModel):
    name: str = Field(..., description="模型名称")
    base_url: str = Field(..., description="API基础URL")
    api_key: str = Field(..., description="API密钥")
    model_name: str = Field(..., description="模型名称")
    capabilities: list[ModelCapability] = Field(..., description="能力列表")


class ModelProfileUpdateRequest(BaseModel):
    name: str | None = Field(None, description="模型名称")
    base_url: str | None = Field(None, description="API基础URL")
    api_key: str | None = Field(None, description="API密钥")
    model_name: str | None = Field(None, description="模型名称")
    capabilities: list[ModelCapability] | None = Field(None, description="能力列表")


class ModelProfileEnableRequest(BaseModel):
    enabled: bool = Field(..., description="是否启用")


class ModelProfileListResponse(BaseModel):
    profiles: list[ModelProfile] = Field(..., description="模型档案列表")
    total: int = Field(..., description="总数")
