"""一日活动计划稳定跨服务契约。"""

from __future__ import annotations

import unicodedata
from datetime import date, datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from packages.contracts.common import ContractModel

SeasonCode = Literal["spring", "summer", "autumn", "winter"]
SnapshotReason = Literal[
    "manual_save",
    "ai_adopted",
    "archive",
    "unarchive",
    "before_restore",
    "restored",
]
PageNumber = Annotated[int, Field(ge=1)]
PageSize = Annotated[int, Field(ge=1, le=100)]
Total = Annotated[int, Field(ge=0)]
SortOrder = Annotated[int, Field(ge=0)]
Text500 = Annotated[str, Field(max_length=500)]
Text1000 = Annotated[str, Field(max_length=1000)]
Text5000 = Annotated[str, Field(max_length=5000)]
SentenceList = Annotated[list[Annotated[str, Field(max_length=1000)]], Field(max_length=3)]


class MorningActivity(ContractModel):
    physical_cycle: Literal["体能大循环"] = "体能大循环"
    group_game: Text500 = ""
    free_game: Text500 = ""
    focus_guidance: Text500 = ""
    objectives: SentenceList = Field(default_factory=list)
    guidance_points: SentenceList = Field(default_factory=list)


class MorningTalk(ContractModel):
    topic: Text500 = ""
    questions: SentenceList = Field(default_factory=list)


class GroupActivityStep(ContractModel):
    heading: Text1000 = ""
    lines: list[Text5000] = Field(default_factory=list)
    is_ai_added: bool = False


class GroupActivity(ContractModel):
    theme: Text1000 = ""
    objectives: list[Text5000] = Field(default_factory=list)
    preparation: list[Text5000] = Field(default_factory=list)
    focus: Text5000 = ""
    difficulty: Text5000 = ""
    process: list[GroupActivityStep] = Field(default_factory=list)


class AreaGame(ContractModel):
    areas: list[Annotated[str, Field(max_length=120)]] = Field(default_factory=list)
    focus_guidance: Text500 = ""
    objectives: SentenceList = Field(default_factory=list)
    guidance_points: SentenceList = Field(default_factory=list)
    support_strategies: SentenceList = Field(default_factory=list)

    @field_validator("areas")
    @classmethod
    def unique_areas(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("区域名称不能重复")
        return value


class DailyReflection(ContractModel):
    highlights: Annotated[str, Field(max_length=200)] = ""
    issues: Annotated[str, Field(max_length=200)] = ""
    adjustments: Annotated[str, Field(max_length=200)] = ""

    @field_validator("highlights", "issues", "adjustments")
    @classmethod
    def normalize_nfkc(cls, value: str) -> str:
        return unicodedata.normalize("NFKC", value)

    @model_validator(mode="after")
    def enforce_combined_limit(self) -> DailyReflection:
        if len(self.highlights + self.issues + self.adjustments) > 200:
            raise ValueError("一日活动反思合计不能超过 200 个字符")
        return self


class PlanContentV1(ContractModel):
    morning_activity: MorningActivity = Field(default_factory=MorningActivity)
    morning_talk: MorningTalk = Field(default_factory=MorningTalk)
    group_activity: GroupActivity = Field(default_factory=GroupActivity)
    indoor_area_game: AreaGame = Field(default_factory=AreaGame)
    afternoon_outdoor_game: AreaGame = Field(default_factory=AreaGame)
    daily_reflection: DailyReflection = Field(default_factory=DailyReflection)

    @classmethod
    def empty(cls) -> PlanContentV1:
        return cls()


class AuthorWrite(ContractModel):
    user_id: UUID
    sort_order: SortOrder


class Author(AuthorWrite):
    display_name_snapshot: Annotated[str, Field(max_length=120)]


class SoftWarning(ContractModel):
    code: Literal[
        "semester.out_of_range",
        "calendar.non_workday",
        "calendar.unknown",
        "calendar.source_conflict",
        "group_activity.ai_step_missing",
    ]
    message: str
    detail: dict[str, Any] | None = None


class Plan(ContractModel):
    id: UUID
    class_id: UUID
    semester_id: UUID
    plan_date: date
    kindergarten_name_snapshot: str
    class_name_snapshot: str
    age_group_name_snapshot: str
    semester_name_snapshot: str
    semester_start_date_snapshot: date
    semester_end_date_snapshot: date
    teaching_week_number: int | None
    teaching_week_text: str | None
    activity_date_text: str
    season: SeasonCode
    content: PlanContentV1 | dict[str, Any]
    content_schema_version: int
    version: Annotated[int, Field(ge=1)]
    authors: Annotated[list[Author], Field(min_length=1)]
    soft_warnings: list[SoftWarning] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    archived_at: datetime | None


class PlanOpenRequest(ContractModel):
    class_id: UUID
    plan_date: date


class PlanSaveRequest(ContractModel):
    expected_version: Annotated[int, Field(ge=1)]
    content: PlanContentV1
    authors: Annotated[list[AuthorWrite], Field(min_length=1)]

    @model_validator(mode="after")
    def unique_authors_and_order(self) -> PlanSaveRequest:
        user_ids = [author.user_id for author in self.authors]
        sort_orders = [author.sort_order for author in self.authors]
        if len(user_ids) != len(set(user_ids)) or len(sort_orders) != len(set(sort_orders)):
            raise ValueError("编写教师和排序不能重复")
        return self


class VersionRequest(ContractModel):
    expected_version: Annotated[int, Field(ge=1)]


class PlanPage(ContractModel):
    items: list[Plan] = Field(default_factory=list)
    page: PageNumber
    page_size: PageSize
    total: Total


class PlanSnapshotContext(ContractModel):
    kindergarten_name: str
    class_name: str
    age_group_name: str
    semester_name: str
    semester_start_date: date
    semester_end_date: date
    teaching_week_number: int | None
    teaching_week_text: str | None
    activity_date_text: str
    season: SeasonCode
    authors: Annotated[list[Author], Field(min_length=1)]


class PlanSnapshot(ContractModel):
    id: UUID
    plan_id: UUID
    plan_version: Annotated[int, Field(ge=1)]
    reason_code: SnapshotReason
    context_snapshot: PlanSnapshotContext
    content: PlanContentV1 | dict[str, Any]
    content_schema_version: int
    content_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    created_by: UUID | None
    created_at: datetime


class PlanSnapshotPage(ContractModel):
    items: list[PlanSnapshot] = Field(default_factory=list)
    page: PageNumber
    page_size: PageSize
    total: Total


class LessonPlanReference(ContractModel):
    id: UUID
    class_id: UUID
    plan_date: date
    version: int
