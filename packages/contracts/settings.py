from datetime import datetime

from pydantic import BaseModel, Field


class Kindergarten(BaseModel):
    id: str = Field(..., description="园所ID")
    name: str = Field(..., description="园所名称")
    timezone: str = Field("Asia/Shanghai", description="时区")
    is_active: bool = Field(True, description="是否活跃")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class KindergartenUpdate(BaseModel):
    name: str = Field(..., description="园所名称")


class Semester(BaseModel):
    id: str = Field(..., description="学期ID")
    name: str = Field(..., description="学期名称")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    is_current: bool = Field(False, description="是否当前学期")
    is_active: bool = Field(True, description="是否活跃")
    kindergarten_id: str = Field(..., description="园所ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class SemesterCreate(BaseModel):
    name: str = Field(..., description="学期名称")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    is_current: bool = Field(False, description="是否当前学期")


class SemesterUpdate(BaseModel):
    name: str | None = Field(None, description="学期名称")
    start_date: str | None = Field(None, description="开始日期")
    end_date: str | None = Field(None, description="结束日期")
    is_current: bool | None = Field(None, description="是否当前学期")
    is_active: bool | None = Field(None, description="是否活跃")


class AgeGroup(BaseModel):
    id: str = Field(..., description="年龄段ID")
    name: str = Field(..., description="年龄段名称")
    sort_order: int = Field(..., description="排序顺序")
    kindergarten_id: str = Field(..., description="园所ID")


class Class(BaseModel):
    id: str = Field(..., description="班级ID")
    name: str = Field(..., description="班级名称")
    age_group_id: str = Field(..., description="年龄段ID")
    kindergarten_id: str = Field(..., description="园所ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ClassCreate(BaseModel):
    name: str = Field(..., description="班级名称")
    age_group_id: str = Field(..., description="年龄段ID")


class ClassUpdate(BaseModel):
    name: str | None = Field(None, description="班级名称")
    age_group_id: str | None = Field(None, description="年龄段ID")


class ClassTeacher(BaseModel):
    class_id: str = Field(..., description="班级ID")
    teacher_id: str = Field(..., description="教师ID")
    is_main: bool = Field(False, description="是否主班教师")
    assigned_at: datetime = Field(..., description="分配时间")


class Area(BaseModel):
    id: str = Field(..., description="区域ID")
    name: str = Field(..., description="区域名称")
    category: str = Field(..., description="类别: indoor/outdoor")
    sort_order: int = Field(..., description="排序顺序")
    is_active: bool = Field(True, description="是否活跃")
    class_id: str = Field(..., description="班级ID")
    kindergarten_id: str = Field(..., description="园所ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class AreaCreate(BaseModel):
    name: str = Field(..., description="区域名称")
    category: str = Field(..., description="类别")
    sort_order: int = Field(..., description="排序顺序")


class AreaUpdate(BaseModel):
    name: str | None = Field(None, description="区域名称")
    sort_order: int | None = Field(None, description="排序顺序")
    is_active: bool | None = Field(None, description="是否活跃")
