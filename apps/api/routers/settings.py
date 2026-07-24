"""园所、学期、班级、教师关系和班级区域设置端点。"""

from typing import Annotated, Literal, cast
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response

from apps.api.dependencies import (
    AdminSessionDependency,
    CurrentSessionDependency,
    SettingsServiceDependency,
)
from apps.api.routers.auth import require_csrf
from packages.backend.settings.repository import (
    AgeGroupRecord,
    AreaRecord,
    ClassRecord,
    KindergartenRecord,
    SemesterRecord,
)
from packages.contracts.settings import (
    AgeGroup,
    AgeGroupList,
    Area,
    AreaPage,
    AreaReplaceRequest,
    AreaType,
    Class,
    ClassPage,
    ClassTeacher,
    ClassTeachersWrite,
    ClassWrite,
    Kindergarten,
    KindergartenPatch,
    Semester,
    SemesterPage,
    SemesterWrite,
)

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


def _kindergarten(record: KindergartenRecord) -> Kindergarten:
    return Kindergarten(
        id=record.id,
        name=record.name,
        timezone=cast(Literal["Asia/Shanghai"], record.timezone),
        is_active=record.is_active,
    )


def _age_group(record: AgeGroupRecord) -> AgeGroup:
    return AgeGroup(
        id=record.id,
        code=record.code,  # type: ignore[arg-type]
        name=record.name,
        sort_order=record.sort_order,
        is_active=record.is_active,
    )


def _semester(record: SemesterRecord) -> Semester:
    return Semester(
        id=record.id,
        name=record.name,
        start_date=record.start_date,
        end_date=record.end_date,
        is_current=record.is_current,
        is_active=record.is_active,
    )


def _class(record: ClassRecord) -> Class:
    return Class(
        id=record.id,
        name=record.name,
        age_group_id=record.age_group_id,
        age_group_name=record.age_group_name,
        is_active=record.is_active,
        teachers=[
            ClassTeacher(
                user_id=teacher.user_id,
                display_name=teacher.display_name,
                is_lead_teacher=teacher.is_lead_teacher,
            )
            for teacher in record.teachers
        ],
        indoor_areas_configured=record.indoor_areas_configured,
        outdoor_areas_configured=record.outdoor_areas_configured,
    )


def _area(record: AreaRecord) -> Area:
    return Area(
        id=record.id,
        class_id=record.class_id,
        area_type=record.area_type,  # type: ignore[arg-type]
        name=record.name,
        sort_order=record.sort_order,
        is_active=record.is_active,
    )


@router.get("/kindergarten", response_model=Kindergarten)
def get_kindergarten(
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
) -> Kindergarten:
    return _kindergarten(service.get_kindergarten(session))


@router.patch("/kindergarten", response_model=Kindergarten)
def patch_kindergarten(
    body: KindergartenPatch,
    request: Request,
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
) -> Kindergarten:
    require_csrf(request)
    return _kindergarten(service.update_kindergarten(session, name=body.name))


@router.get("/age-groups", response_model=AgeGroupList)
def list_age_groups(
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
) -> list[AgeGroup]:
    return [_age_group(record) for record in service.list_age_groups(session)]


@router.get("/semesters", response_model=SemesterPage)
def list_semesters(
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> SemesterPage:
    records, total = service.list_semesters(session, page=page, page_size=page_size)
    return SemesterPage(
        items=[_semester(record) for record in records],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("/semesters", response_model=Semester, status_code=201)
def create_semester(
    body: SemesterWrite,
    request: Request,
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
) -> Semester:
    require_csrf(request)
    return _semester(
        service.create_semester(
            session,
            name=body.name,
            start_date=body.start_date,
            end_date=body.end_date,
            is_active=body.is_active,
        )
    )


@router.get("/semesters/{semester_id}", response_model=Semester)
def get_semester(
    semester_id: UUID,
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
) -> Semester:
    return _semester(service.get_semester(session, semester_id))


@router.patch("/semesters/{semester_id}", response_model=Semester)
def patch_semester(
    semester_id: UUID,
    body: SemesterWrite,
    request: Request,
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
) -> Semester:
    require_csrf(request)
    return _semester(
        service.update_semester(
            session,
            semester_id,
            name=body.name,
            start_date=body.start_date,
            end_date=body.end_date,
            is_active=body.is_active,
        )
    )


@router.post("/semesters/{semester_id}/make-current", response_model=Semester)
def make_current_semester(
    semester_id: UUID,
    request: Request,
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
) -> Semester:
    require_csrf(request)
    return _semester(service.make_current_semester(session, semester_id))


@router.get("/classes", response_model=ClassPage)
def list_classes(
    session: CurrentSessionDependency,
    service: SettingsServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ClassPage:
    records, total = service.list_classes(session, page=page, page_size=page_size)
    return ClassPage(
        items=[_class(record) for record in records],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("/classes", response_model=Class, status_code=201)
def create_class(
    body: ClassWrite,
    request: Request,
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
) -> Class:
    require_csrf(request)
    return _class(
        service.create_class(
            session,
            name=body.name,
            age_group_id=body.age_group_id,
            is_active=body.is_active,
        )
    )


@router.get("/classes/{class_id}", response_model=Class)
def get_class(
    class_id: UUID,
    session: CurrentSessionDependency,
    service: SettingsServiceDependency,
) -> Class:
    return _class(service.get_class(session, class_id))


@router.patch("/classes/{class_id}", response_model=Class)
def patch_class(
    class_id: UUID,
    body: ClassWrite,
    request: Request,
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
) -> Class:
    require_csrf(request)
    return _class(
        service.update_class(
            session,
            class_id,
            name=body.name,
            age_group_id=body.age_group_id,
            is_active=body.is_active,
        )
    )


@router.put("/classes/{class_id}/teachers", response_model=Class)
def replace_class_teachers(
    class_id: UUID,
    body: ClassTeachersWrite,
    request: Request,
    session: AdminSessionDependency,
    service: SettingsServiceDependency,
) -> Class:
    require_csrf(request)
    return _class(service.replace_class_teachers(session, class_id, body.teachers))


@router.get("/classes/{class_id}/areas/{area_type}", response_model=AreaPage)
def list_class_areas(
    class_id: UUID,
    area_type: AreaType,
    session: CurrentSessionDependency,
    service: SettingsServiceDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> AreaPage:
    records, total = service.list_class_areas(
        session,
        class_id,
        area_type,
        page=page,
        page_size=page_size,
    )
    return AreaPage(
        items=[_area(record) for record in records],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.put("/classes/{class_id}/areas/{area_type}", status_code=204)
def replace_class_areas(
    class_id: UUID,
    area_type: AreaType,
    body: AreaReplaceRequest,
    request: Request,
    session: CurrentSessionDependency,
    service: SettingsServiceDependency,
) -> Response:
    require_csrf(request)
    service.replace_class_areas(session, class_id, area_type, body.areas)
    return Response(status_code=204)
