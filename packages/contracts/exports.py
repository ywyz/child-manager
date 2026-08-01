"""Word 导出跨 API、Web 与 Worker 使用的稳定契约。"""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, field_validator

from packages.contracts.common import ContractModel, FieldError
from packages.contracts.jobs import Job
from packages.contracts.lesson_plans import PlanSaveRequest

ExportStatus = Literal["pending", "succeeded", "failed"]
ExportContentSchemaVersion = Literal[1]
ExportTemplateSha256 = Literal["72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043"]
ExportSection = Literal[
    "morning_activity",
    "morning_talk",
    "group_activity",
    "indoor_area_game",
    "afternoon_outdoor_game",
]
REQUIRED_EXPORT_SECTIONS: tuple[ExportSection, ...] = (
    "morning_activity",
    "morning_talk",
    "group_activity",
    "indoor_area_game",
    "afternoon_outdoor_game",
)


class ExportReference(ContractModel):
    export_id: UUID
    job_id: UUID


class ExportRequest(PlanSaveRequest):
    confirm_incomplete: bool


class ExportConfirmationRequiredError(ContractModel):
    code: Literal["export.confirmation_required"]
    message: str
    request_id: UUID
    field_errors: list[FieldError] = Field(default_factory=list)
    missing_sections: Annotated[list[ExportSection], Field(min_length=1, max_length=5)]

    @field_validator("missing_sections")
    @classmethod
    def unique_sections(cls, value: list[ExportSection]) -> list[ExportSection]:
        if len(value) != len(set(value)):
            raise ValueError("缺失栏目不能重复")
        return value


class Export(ContractModel):
    id: UUID
    plan_id: UUID
    plan_version: Annotated[int, Field(ge=1)]
    content_schema_version: ExportContentSchemaVersion
    content_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    job_id: UUID
    status: ExportStatus
    display_filename: Annotated[str, Field(max_length=255)]
    file_size: Annotated[int, Field(ge=0)] | None = None
    file_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None = None
    template_sha256: ExportTemplateSha256
    exported_at: datetime | None = None
    file_missing_at: datetime | None = None
    error_code: str | None = None
    error_summary: Annotated[str, Field(max_length=1000)] | None = None
    created_at: datetime


class ExportAccepted(ContractModel):
    job: Job
    export: Export


class ExportPage(ContractModel):
    items: list[Export]
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1, le=100)]
    total: Annotated[int, Field(ge=0)]


class ExportDownloadMetadata(ContractModel):
    display_filename: Annotated[str, Field(min_length=1, max_length=255)]
    media_type: Literal["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    file_size: Annotated[int, Field(ge=0)]
    file_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
