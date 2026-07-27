"""提示词管理、固定输入和测试运行契约。"""

from __future__ import annotations

import unicodedata
from datetime import date, datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from packages.contracts.common import ContractModel
from packages.contracts.lesson_plans import (
    AreaGame,
    GroupActivity,
    MorningActivity,
    MorningTalk,
    SeasonCode,
)

PromptCode = Literal[
    "daily_activity_plan.morning_activity",
    "daily_activity_plan.morning_talk",
    "daily_activity_plan.group_activity_split",
    "daily_activity_plan.group_activity_add_step",
    "daily_activity_plan.indoor_area_game",
    "daily_activity_plan.afternoon_outdoor_game",
    "daily_activity_plan.daily_reflection",
]
AiCapability = Literal["text", "vision", "structured_output"]


class PromptReference(ContractModel):
    code: PromptCode
    required_capabilities: list[AiCapability]


class TeacherContext(ContractModel):
    notes: Annotated[str, Field(max_length=2000)] = ""


class CommonPlanPromptVariables(ContractModel):
    plan_date: date
    weekday_text: Annotated[str, Field(min_length=1, max_length=20)]
    teaching_week_text: Annotated[str, Field(max_length=40)] | None
    season: SeasonCode
    class_name: Annotated[str, Field(min_length=1, max_length=120)]
    age_group_name: Annotated[str, Field(min_length=1, max_length=120)]
    teacher_context: TeacherContext


class IndoorAreaPromptVariables(CommonPlanPromptVariables):
    indoor_areas: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=120)]], Field(min_length=1)
    ]


class OutdoorAreaPromptVariables(CommonPlanPromptVariables):
    outdoor_areas: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=120)]], Field(min_length=1)
    ]


class GroupSplitPromptVariables(ContractModel):
    source_text: Annotated[str, Field(min_length=1, max_length=200_000)]
    age_group_name: Annotated[str, Field(min_length=1, max_length=120)]
    teacher_context: TeacherContext


class GroupAddStepPromptVariables(ContractModel):
    group_activity: GroupActivity
    age_group_name: Annotated[str, Field(min_length=1, max_length=120)]
    teacher_context: TeacherContext


class ReflectionCurrentPlan(ContractModel):
    morning_activity: MorningActivity
    morning_talk: MorningTalk
    group_activity: GroupActivity
    indoor_area_game: AreaGame
    afternoon_outdoor_game: AreaGame


class ReflectionPromptVariables(ContractModel):
    plan_date: date
    class_name: Annotated[str, Field(min_length=1, max_length=120)]
    age_group_name: Annotated[str, Field(min_length=1, max_length=120)]
    current_plan: ReflectionCurrentPlan


ExactlyThreeStatements = Annotated[
    list[Annotated[str, Field(min_length=1, max_length=1000, pattern=r"。$")]],
    Field(min_length=3, max_length=3),
]
ExactlyThreeQuestions = Annotated[
    list[Annotated[str, Field(min_length=1, max_length=1000, pattern=r"？$")]],
    Field(min_length=3, max_length=3),
]


class AiMorningActivity(ContractModel):
    physical_cycle: Literal["体能大循环"]
    group_game: Annotated[str, Field(min_length=1, max_length=500)]
    free_game: Annotated[str, Field(min_length=1, max_length=500)]
    focus_guidance: Annotated[str, Field(min_length=1, max_length=500)]
    objectives: ExactlyThreeStatements
    guidance_points: ExactlyThreeStatements


class AiMorningTalk(ContractModel):
    topic: Annotated[str, Field(min_length=1, max_length=500)]
    questions: ExactlyThreeQuestions


class AiAreaGame(ContractModel):
    focus_guidance: Annotated[str, Field(min_length=1, max_length=500)]
    objectives: ExactlyThreeStatements
    guidance_points: ExactlyThreeStatements
    support_strategies: ExactlyThreeStatements


class AiGroupActivityStep(ContractModel):
    heading: Annotated[str, Field(min_length=1, max_length=1000)]
    lines: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=5000)]],
        Field(min_length=1),
    ]


class AiGroupActivity(ContractModel):
    theme: Annotated[str, Field(min_length=1, max_length=1000)]
    objectives: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=5000)]],
        Field(min_length=1),
    ]
    preparation: Annotated[
        list[Annotated[str, Field(min_length=1, max_length=5000)]],
        Field(min_length=1),
    ]
    focus: Annotated[str, Field(min_length=1, max_length=5000)]
    difficulty: Annotated[str, Field(min_length=1, max_length=5000)]
    process: Annotated[list[AiGroupActivityStep], Field(min_length=1)]


class GroupActivityAddStepResult(ContractModel):
    step: AiGroupActivityStep
    suggested_insert_index: Annotated[int, Field(ge=0)]


class AiDailyReflection(ContractModel):
    highlights: Annotated[str, Field(min_length=1, max_length=200)]
    issues: Annotated[str, Field(min_length=1, max_length=200)]
    adjustments: Annotated[str, Field(min_length=1, max_length=200)]

    @field_validator("highlights", "issues", "adjustments")
    @classmethod
    def normalize_nfkc(cls, value: str) -> str:
        return unicodedata.normalize("NFKC", value)

    @model_validator(mode="after")
    def enforce_combined_limit(self) -> AiDailyReflection:
        if len(self.highlights + self.issues + self.adjustments) > 200:
            raise ValueError("一日活动反思合计不能超过 200 个字符")
        return self


class PromptDefinition(ContractModel):
    id: UUID
    code: PromptCode
    name: Annotated[str, Field(max_length=160)]
    variable_whitelist: list[str]
    required_capabilities: list[AiCapability]
    result_schema_code: Annotated[str, Field(max_length=160)]
    result_schema_version: Literal[1]
    model_profile_id: UUID | None
    effective_version_id: UUID | None
    draft_version_id: UUID | None
    is_active: bool


class PromptDefinitionPage(ContractModel):
    items: Annotated[list[PromptDefinition], Field(max_length=7)] = Field(default_factory=list)
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1, le=100)]
    total: Annotated[int, Field(ge=0, le=7)]


class PromptVersion(ContractModel):
    id: UUID
    prompt_definition_id: UUID
    prompt_code: PromptCode
    version_number: Annotated[int, Field(ge=1)]
    source_type: Literal["system", "custom"]
    lifecycle_state: Literal["draft", "published"]
    content: Annotated[str, Field(min_length=1, max_length=50_000)]
    content_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    based_on_version_id: UUID | None
    created_by: UUID | None
    created_at: datetime
    published_by: UUID | None
    published_at: datetime | None


class PromptVersionPage(ContractModel):
    items: list[PromptVersion] = Field(default_factory=list)
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1, le=100)]
    total: Annotated[int, Field(ge=0)]


class PromptDraftWrite(ContractModel):
    content: Annotated[str, Field(min_length=1, max_length=50_000)]
    based_on_version_id: UUID | None = None


class PromptTestRequest(ContractModel):
    version_id: UUID
    model_profile_id: UUID
    variables: dict[str, Any]


class PromptTestInputSummary(ContractModel):
    provided_variable_names: list[Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]] = Field(
        description="按 ASCII 字典序排列的已提供变量名；不返回变量值。"
    )
    all_values_redacted: Literal[True]


class PromptTestRun(ContractModel):
    id: UUID
    job_id: UUID
    prompt_code: PromptCode
    input_summary: PromptTestInputSummary
    status: Literal["pending", "succeeded", "failed"]
    output_content: dict[str, Any] | None = None
    elapsed_ms: Annotated[int, Field(ge=0)] | None = None
    error_code: str | None = None
    error_summary: Annotated[str, Field(max_length=1000)] | None = None
    created_at: datetime


class PromptTestPage(ContractModel):
    items: Annotated[list[PromptTestRun], Field(max_length=20)] = Field(default_factory=list)
    page: Annotated[int, Field(ge=1)]
    page_size: Annotated[int, Field(ge=1, le=20)]
    total: Annotated[int, Field(ge=0, le=20)]
