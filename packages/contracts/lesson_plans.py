"""一日活动计划稳定跨服务契约。"""

from __future__ import annotations

import unicodedata
from datetime import date, datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import AfterValidator, Field, ValidationInfo, field_validator, model_validator

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
TeacherContext = Annotated[str, Field(max_length=5000)]


def _require_nonblank(value: str) -> str:
    if not value.strip():
        raise ValueError("文本不能为空")
    return value


def _require_statement(value: str) -> str:
    _require_nonblank(value)
    if not value.endswith("。"):
        raise ValueError("陈述必须以中文句号结束")
    return value


def _require_question(value: str) -> str:
    _require_nonblank(value)
    if not value.endswith("？"):
        raise ValueError("问题必须以中文问号结束")
    return value


NonEmptyText500 = Annotated[
    str,
    Field(min_length=1, max_length=500),
    AfterValidator(_require_nonblank),
]
NonEmptyText1000 = Annotated[
    str,
    Field(min_length=1, max_length=1000),
    AfterValidator(_require_nonblank),
]
NonEmptyText5000 = Annotated[
    str,
    Field(min_length=1, max_length=5000),
    AfterValidator(_require_nonblank),
]
Statement = Annotated[
    str,
    Field(min_length=2, max_length=1000),
    AfterValidator(_require_statement),
]
Question = Annotated[
    str,
    Field(min_length=2, max_length=1000),
    AfterValidator(_require_question),
]
ExactlyThreeStatements = Annotated[list[Statement], Field(min_length=3, max_length=3)]
ExactlyThreeQuestions = Annotated[list[Question], Field(min_length=3, max_length=3)]
AiTaskCode = Literal[
    "morning_activity",
    "morning_talk",
    "group_activity_split",
    "group_activity_add_step",
    "indoor_area_game",
    "afternoon_outdoor_game",
    "daily_reflection",
]
LessonPlanSourceType = Literal["pasted_text", "docx"]


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


class AiMorningActivity(ContractModel):
    physical_cycle: Literal["体能大循环"]
    group_game: NonEmptyText500
    free_game: NonEmptyText500
    focus_guidance: NonEmptyText500
    objectives: ExactlyThreeStatements
    guidance_points: ExactlyThreeStatements


class AiMorningTalk(ContractModel):
    topic: NonEmptyText500
    questions: ExactlyThreeQuestions


class AiGroupActivityStep(ContractModel):
    heading: NonEmptyText1000
    lines: Annotated[list[NonEmptyText5000], Field(min_length=1)]


class AiGroupActivity(ContractModel):
    theme: NonEmptyText1000
    objectives: Annotated[list[NonEmptyText5000], Field(min_length=1)]
    preparation: Annotated[list[NonEmptyText5000], Field(min_length=1)]
    focus: NonEmptyText5000
    difficulty: NonEmptyText5000
    process: Annotated[list[AiGroupActivityStep], Field(min_length=1)]


class GroupActivityStepCandidate(AiGroupActivityStep):
    pass


def _validate_group_add_step_index(
    suggested_insert_index: int,
    *,
    process_length: int,
) -> None:
    if process_length < 0 or suggested_insert_index > process_length:
        raise ValueError("建议插入索引超出生成输入的过程范围")


class GroupActivityAddStepResult(ContractModel):
    step: GroupActivityStepCandidate
    suggested_insert_index: Annotated[int, Field(ge=0)]

    @model_validator(mode="after")
    def enforce_context_insert_index(
        self,
        info: ValidationInfo,
    ) -> GroupActivityAddStepResult:
        context = info.context
        maximum = context.get("max_insert_index") if isinstance(context, dict) else None
        if isinstance(maximum, int):
            _validate_group_add_step_index(
                self.suggested_insert_index,
                process_length=maximum,
            )
        return self


class AiAreaGame(ContractModel):
    focus_guidance: NonEmptyText500
    objectives: ExactlyThreeStatements
    guidance_points: ExactlyThreeStatements
    support_strategies: ExactlyThreeStatements


class AiDailyReflection(ContractModel):
    highlights: Annotated[str, Field(min_length=1, max_length=200)]
    issues: Annotated[str, Field(min_length=1, max_length=200)]
    adjustments: Annotated[str, Field(min_length=1, max_length=200)]

    @field_validator("highlights", "issues", "adjustments")
    @classmethod
    def normalize_nfkc(cls, value: str) -> str:
        return _require_nonblank(unicodedata.normalize("NFKC", value))

    @model_validator(mode="after")
    def enforce_combined_limit(self) -> AiDailyReflection:
        if len(self.highlights + self.issues + self.adjustments) > 200:
            raise ValueError("一日活动反思合计不能超过 200 个字符")
        return self


type AiPromptResult = (
    AiMorningActivity
    | AiMorningTalk
    | AiGroupActivity
    | GroupActivityAddStepResult
    | AiAreaGame
    | AiDailyReflection
)


def apply_ai_area_result(result: AiAreaGame, *, input_areas: list[str]) -> AreaGame:
    """区域名称属于冻结输入；模型只能选择重点指导区域，不能改写区域列表。"""

    if (
        not input_areas
        or len(input_areas) != len(set(input_areas))
        or any(not area.strip() for area in input_areas)
    ):
        raise ValueError("输入区域必须非空、有效且不重复")
    if result.focus_guidance not in input_areas:
        raise ValueError("重点指导必须等于一个输入区域")
    return AreaGame(
        areas=list(input_areas),
        focus_guidance=result.focus_guidance,
        objectives=list(result.objectives),
        guidance_points=list(result.guidance_points),
        support_strategies=list(result.support_strategies),
    )


def validate_group_add_step_result(
    result: GroupActivityAddStepResult,
    *,
    process_length: int,
) -> GroupActivityAddStepResult:
    """按任务冻结的过程长度校验索引；越界必须进入结构错误重试。"""

    _validate_group_add_step_index(
        result.suggested_insert_index,
        process_length=process_length,
    )
    return result


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


class AiBatchRequest(ContractModel):
    expected_version: Annotated[int, Field(ge=1)]
    teacher_context: TeacherContext


class AiGenerationRequest(ContractModel):
    task_code: AiTaskCode
    expected_version: Annotated[int, Field(ge=1)]
    teacher_context: TeacherContext | None = None
    source_id: UUID | None = None
    content: PlanContentV1 | None = None

    @model_validator(mode="after")
    def enforce_task_specific_input(self) -> AiGenerationRequest:
        is_reflection = self.task_code == "daily_reflection"
        if is_reflection:
            if self.content is None or self.teacher_context is not None:
                raise ValueError("反思生成只接受当前正文，不接受教师补充")
        elif self.teacher_context is None or self.content is not None:
            raise ValueError("非反思生成必须提供教师补充且不得携带当前正文")

        is_group_split = self.task_code == "group_activity_split"
        if is_group_split != (self.source_id is not None):
            raise ValueError("只有集体活动拆分必须提供来源 ID")
        return self


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


class LessonPlanSource(ContractModel):
    """已确认集体活动来源的脱敏元数据，正文和附件不得跨服务返回。"""

    id: UUID
    plan_id: UUID
    source_type: LessonPlanSourceType
    original_filename: Annotated[str | None, Field(max_length=255)]
    source_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    extracted_character_count: Annotated[int, Field(ge=1, le=200000)]
    uploaded_by: UUID
    created_at: datetime


class LessonPlanSourcePage(ContractModel):
    items: list[LessonPlanSource] = Field(default_factory=list)
    page: PageNumber
    page_size: PageSize
    total: Total


class LessonPlanSourceTextWrite(ContractModel):
    text: Annotated[str, Field(min_length=1, max_length=200_000)]


class LessonPlanSourceDocxPreview(ContractModel):
    """DOCX 提取的临时预览；教师确认前不得持久化。"""

    original_filename: Annotated[str, Field(min_length=1, max_length=255)]
    extracted_text: Annotated[str, Field(min_length=1, max_length=200_000)]


class LessonPlanReference(ContractModel):
    id: UUID
    class_id: UUID
    plan_date: date
    version: int
