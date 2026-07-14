from datetime import datetime

from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    plan_id: str = Field(..., description="教案ID")
    expected_version: int = Field(..., description="期望版本号")


class ExportRecord(BaseModel):
    id: str = Field(..., description="导出记录ID")
    plan_id: str = Field(..., description="教案ID")
    plan_version: int = Field(..., description="教案版本")
    template_hash: str = Field(..., description="模板哈希")
    file_hash: str = Field(..., description="文件哈希")
    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    status: str = Field(..., description="状态")
    user_id: str = Field(..., description="用户ID")
    kindergarten_id: str = Field(..., description="园所ID")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: datetime | None = Field(None, description="完成时间")


class ExportListResponse(BaseModel):
    exports: list[ExportRecord] = Field(..., description="导出记录列表")
    total: int = Field(..., description="总数")


class MissingColumnWarning(BaseModel):
    column_name: str = Field(..., description="栏目名称")
    column_label: str = Field(..., description="栏目显示名")


class ExportConfirmRequest(BaseModel):
    plan_id: str = Field(..., description="教案ID")
    expected_version: int = Field(..., description="期望版本号")
    confirmed_missing_columns: list[str] = Field(..., description="已确认的缺失栏目")
