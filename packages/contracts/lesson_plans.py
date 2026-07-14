from datetime import datetime

from pydantic import BaseModel, Field


class PlanContentV1(BaseModel):
    morning_activity: str = Field("", description="晨间活动")
    morning_talk: str = Field("", description="晨间谈话")
    group_activity: str = Field("", description="集体活动")
    indoor_area_game: str = Field("", description="室内区域游戏")
    afternoon_outdoor_game: str = Field("", description="下午户外游戏")
    daily_reflection: str = Field("", description="一日活动反思")


class DailyReflection(BaseModel):
    highlights: str = Field("", description="活动亮点")
    issues: str = Field("", description="存在问题")
    adjustments: str = Field("", description="调整策略")


class PlanAuthor(BaseModel):
    user_id: str = Field(..., description="用户ID")
    full_name: str = Field(..., description="姓名")
    sort_order: int = Field(..., description="排序顺序")


class PlanSnapshot(BaseModel):
    id: str = Field(..., description="快照ID")
    plan_id: str = Field(..., description="教案ID")
    content: PlanContentV1 = Field(..., description="内容")
    authors: list[PlanAuthor] = Field(..., description="作者")
    reason: str = Field(..., description="快照原因")
    version: int = Field(..., description="版本号")
    created_at: datetime = Field(..., description="创建时间")


class LessonPlan(BaseModel):
    id: str = Field(..., description="教案ID")
    kindergarten_id: str = Field(..., description="园所ID")
    class_id: str = Field(..., description="班级ID")
    plan_date: str = Field(..., description="活动日期")
    semester_id: str = Field(..., description="学期ID")
    age_group_id: str = Field(..., description="年龄段ID")
    age_group_name: str = Field(..., description="年龄段名称")
    class_name: str = Field(..., description="班级名称")
    content: PlanContentV1 = Field(..., description="内容")
    authors: list[PlanAuthor] = Field(..., description="作者")
    version: int = Field(..., description="版本号")
    archived_at: datetime | None = Field(None, description="归档时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class PlanCreateRequest(BaseModel):
    class_id: str = Field(..., description="班级ID")
    plan_date: str = Field(..., description="活动日期")


class PlanOpenRequest(BaseModel):
    class_id: str = Field(..., description="班级ID")
    plan_date: str = Field(..., description="活动日期")


class PlanSaveRequest(BaseModel):
    content: PlanContentV1 = Field(..., description="内容")
    expected_version: int = Field(..., description="期望版本号")


class PlanAutoSaveRequest(BaseModel):
    content: PlanContentV1 = Field(..., description="内容")
    expected_version: int = Field(..., description="期望版本号")


class PlanArchiveRequest(BaseModel):
    expected_version: int = Field(..., description="期望版本号")


class PlanUnarchiveRequest(BaseModel):
    expected_version: int = Field(..., description="期望版本号")


class PlanRestoreRequest(BaseModel):
    snapshot_id: str = Field(..., description="快照ID")
    expected_version: int = Field(..., description="期望版本号")


class PlanSoftWarning(BaseModel):
    code: str = Field(..., description="警告代码")
    message: str = Field(..., description="警告消息")


class PlanResponse(BaseModel):
    plan: LessonPlan = Field(..., description="教案")
    warnings: list[PlanSoftWarning] = Field([], description="软提示")


class PlanListResponse(BaseModel):
    plans: list[LessonPlan] = Field(..., description="教案列表")
    total: int = Field(..., description="总数")


class SnapshotListResponse(BaseModel):
    snapshots: list[PlanSnapshot] = Field(..., description="快照列表")
    total: int = Field(..., description="总数")
