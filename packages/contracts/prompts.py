from datetime import datetime

from pydantic import BaseModel, Field


class PromptVariable(BaseModel):
    name: str = Field(..., description="变量名")
    type: str = Field(..., description="变量类型")
    description: str | None = Field(None, description="变量描述")


class PromptCapability(BaseModel):
    name: str = Field(..., description="能力名称")
    required: bool = Field(True, description="是否必需")


class PromptResultSchema(BaseModel):
    name: str = Field(..., description="Schema名称")
    json_schema: dict[str, object] = Field(..., description="JSON Schema")


class PromptVersion(BaseModel):
    id: str = Field(..., description="版本ID")
    prompt_id: str = Field(..., description="提示词ID")
    content: str = Field(..., description="提示词内容")
    variables: list[PromptVariable] = Field(..., description="变量列表")
    capabilities: list[PromptCapability] = Field(..., description="能力要求")
    result_schema: PromptResultSchema = Field(..., description="结果Schema")
    is_published: bool = Field(False, description="是否已发布")
    created_at: datetime = Field(..., description="创建时间")
    created_by: str = Field(..., description="创建者")


class Prompt(BaseModel):
    id: str = Field(..., description="提示词ID")
    code: str = Field(..., description="稳定标识")
    name: str = Field(..., description="显示名称")
    description: str | None = Field(None, description="描述")
    current_version_id: str | None = Field(None, description="当前版本ID")
    published_version_id: str | None = Field(None, description="已发布版本ID")
    is_system_default: bool = Field(False, description="是否系统默认")
    kindergarten_id: str = Field(..., description="园所ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class PromptCreateRequest(BaseModel):
    code: str = Field(..., description="稳定标识")
    name: str = Field(..., description="显示名称")
    description: str | None = Field(None, description="描述")
    content: str = Field(..., description="提示词内容")
    variables: list[PromptVariable] = Field(..., description="变量列表")
    capabilities: list[PromptCapability] = Field(..., description="能力要求")
    result_schema: PromptResultSchema = Field(..., description="结果Schema")


class PromptUpdateRequest(BaseModel):
    name: str | None = Field(None, description="显示名称")
    description: str | None = Field(None, description="描述")
    content: str | None = Field(None, description="提示词内容")
    variables: list[PromptVariable] | None = Field(None, description="变量列表")
    capabilities: list[PromptCapability] | None = Field(None, description="能力要求")
    result_schema: PromptResultSchema | None = Field(None, description="结果Schema")


class PromptPublishRequest(BaseModel):
    version_id: str = Field(..., description="版本ID")


class PromptTestRun(BaseModel):
    id: str = Field(..., description="测试运行ID")
    prompt_id: str = Field(..., description="提示词ID")
    version_id: str = Field(..., description="版本ID")
    job_id: str = Field(..., description="任务ID")
    input_summary: dict[str, object] = Field(..., description="输入摘要(脱敏)")
    status: str = Field(..., description="状态")
    result: dict[str, object] | None = Field(None, description="结果")
    error_summary: str | None = Field(None, description="错误摘要")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: datetime | None = Field(None, description="完成时间")


class PromptTestRequest(BaseModel):
    version_id: str = Field(..., description="版本ID")
    variables: dict[str, object] = Field(..., description="测试变量")
