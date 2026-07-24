"""首期必要设置的稳定跨服务契约。"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, RootModel, model_validator

from packages.contracts.common import ContractModel

AgeGroupCode = Literal["toddler", "small", "middle", "large"]
AreaType = Literal["indoor", "outdoor"]

Name200 = Annotated[str, Field(min_length=1, max_length=200)]
Name160 = Annotated[str, Field(min_length=1, max_length=160)]
Name120 = Annotated[str, Field(min_length=1, max_length=120)]
PageNumber = Annotated[int, Field(ge=1)]
PageSize = Annotated[int, Field(ge=1, le=100)]
Total = Annotated[int, Field(ge=0)]
SortOrder = Annotated[int, Field(ge=0)]


class Kindergarten(ContractModel):
    id: UUID
    name: Annotated[str, Field(max_length=200)]
    timezone: Literal["Asia/Shanghai"]
    is_active: bool


class KindergartenPatch(ContractModel):
    name: Name200


class AgeGroup(ContractModel):
    id: UUID
    code: AgeGroupCode
    name: Annotated[str, Field(max_length=120)]
    sort_order: SortOrder
    is_active: bool


class AgeGroupList(RootModel[list[AgeGroup]]):
    root: Annotated[list[AgeGroup], Field(min_length=4, max_length=4)]

    @model_validator(mode="after")
    def require_frozen_order(self) -> AgeGroupList:
        expected: tuple[AgeGroupCode, ...] = ("toddler", "small", "middle", "large")
        if tuple(item.code for item in self.root) != expected:
            raise ValueError("年龄段必须按托班、小班、中班、大班的固定顺序返回")
        return self


class Semester(ContractModel):
    id: UUID
    name: Annotated[str, Field(max_length=160)]
    start_date: date
    end_date: date
    is_current: bool
    is_active: bool


class SemesterWrite(ContractModel):
    name: Name160
    start_date: date
    end_date: date
    is_active: bool


class SemesterPage(ContractModel):
    items: list[Semester] = Field(default_factory=list)
    page: PageNumber
    page_size: PageSize
    total: Total


class ClassTeacher(ContractModel):
    user_id: UUID
    display_name: Annotated[str, Field(max_length=120)]
    is_lead_teacher: bool


class ClassTeacherWrite(ContractModel):
    user_id: UUID
    is_lead_teacher: bool


class ClassTeachersWrite(ContractModel):
    teachers: list[ClassTeacherWrite] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_unique_teachers_and_lead(self) -> ClassTeachersWrite:
        user_ids = [teacher.user_id for teacher in self.teachers]
        if len(user_ids) != len(set(user_ids)):
            raise ValueError("同一教师不能重复关联到班级")
        if sum(teacher.is_lead_teacher for teacher in self.teachers) > 1:
            raise ValueError("同一班级只能有一位主班教师")
        return self


class Class(ContractModel):
    id: UUID
    name: Annotated[str, Field(max_length=120)]
    age_group_id: UUID
    age_group_name: Annotated[str, Field(max_length=120)]
    is_active: bool
    teachers: list[ClassTeacher] = Field(default_factory=list)
    indoor_areas_configured: bool
    outdoor_areas_configured: bool


class ClassWrite(ContractModel):
    name: Name120
    age_group_id: UUID
    is_active: bool


class ClassPage(ContractModel):
    items: list[Class] = Field(default_factory=list)
    page: PageNumber
    page_size: PageSize
    total: Total


class Area(ContractModel):
    id: UUID
    class_id: UUID
    area_type: AreaType
    name: Annotated[str, Field(max_length=120)]
    sort_order: SortOrder
    is_active: bool


class AreaWrite(ContractModel):
    id: UUID | None = None
    name: Name120
    sort_order: SortOrder
    is_active: bool


class AreaReplaceRequest(ContractModel):
    areas: list[AreaWrite] = Field(default_factory=list)


class AreaPage(ContractModel):
    items: list[Area] = Field(default_factory=list)
    page: PageNumber
    page_size: PageSize
    total: Total
