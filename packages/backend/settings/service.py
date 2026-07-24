"""首期必要设置的领域规则与事务边界。"""

from __future__ import annotations

import os
import unicodedata
from collections.abc import Sequence
from datetime import date
from typing import NoReturn
from uuid import UUID

import psycopg

from packages.backend.identity.service import IdentityError, IdentityService, SessionUser
from packages.backend.settings.repository import (
    AgeGroupRecord,
    AreaInput,
    AreaRecord,
    ClassRecord,
    KindergartenRecord,
    SemesterRecord,
    SettingsRepository,
    TeacherInput,
)
from packages.contracts.settings import AreaWrite, ClassTeacherWrite


def semester_ranges_overlap(
    start_date: date,
    end_date: date,
    other_start_date: date,
    other_end_date: date,
) -> bool:
    """按闭区间判断两个学期日期范围是否重叠。"""

    return start_date <= other_end_date and other_start_date <= end_date


def current_semester_selection_is_valid(states: Sequence[tuple[bool, bool]]) -> bool:
    """当前学期最多一个，且当前学期必须有效。"""

    current = [is_active for is_current, is_active in states if is_current]
    return len(current) <= 1 and all(current)


def lead_teacher_selection_is_valid(teacher_ids: Sequence[UUID]) -> bool:
    """同一班级最多一名主班教师。"""

    return len(teacher_ids) <= 1


def _normalize_display_name(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def _normalize_key(value: str) -> str:
    return _normalize_display_name(value).casefold()


def _required_display_name(value: str, *, code: str, resource: str) -> str:
    normalized = _normalize_display_name(value)
    if not normalized:
        raise IdentityError(422, code, f"{resource}名称不能为空。")
    return normalized


def normalize_class_areas(names: Sequence[str]) -> tuple[str, ...]:
    """规范化区域显示名，保留顺序并拒绝同类别重名。"""

    normalized = tuple(_normalize_display_name(name) for name in names)
    keys = tuple(_normalize_key(name) for name in normalized)
    if any(not name for name in normalized):
        raise ValueError("区域名称不能为空")
    if len(keys) != len(set(keys)):
        raise ValueError("同一类别的区域名称不能重复")
    return normalized


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


class SettingsService:
    """在当前会话园所内执行设置用例。"""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    @classmethod
    def from_environment(cls) -> SettingsService:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            raise IdentityError(503, "configuration.unavailable", "数据库配置不可用。")
        return cls(database_url)

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    @staticmethod
    def _kindergarten_id(session: SessionUser) -> UUID:
        kindergarten_id = session.user.kindergarten_id
        if kindergarten_id is None:
            raise IdentityError(403, "auth.forbidden", "当前账号不属于可用园所。")
        return kindergarten_id

    @staticmethod
    def _require_admin(session: SessionUser) -> None:
        IdentityService.require_admin(session)

    @staticmethod
    def _not_found(resource: str) -> IdentityError:
        return IdentityError(404, "resource.not_found", f"{resource}不存在。")

    @staticmethod
    def _raise_write_error(exc: psycopg.IntegrityError) -> NoReturn:
        constraint = getattr(exc.diag, "constraint_name", None)
        if constraint == "ck_semesters_date_range":
            raise IdentityError(
                422, "semester.invalid_date_range", "学期开始日期不能晚于结束日期。"
            )
        if constraint == "ck_semesters_current_active":
            raise IdentityError(409, "semester.current_inactive", "当前学期必须处于启用状态。")
        if constraint == "ex_semesters_active_date_range":
            raise IdentityError(409, "semester.overlap", "有效学期的日期范围不能重叠。")
        if constraint == "uq_class_teachers_lead":
            raise IdentityError(409, "class.multiple_lead_teachers", "同一班级只能有一位主班教师。")
        if constraint == "uq_class_areas_kindergarten_class_type_name":
            raise IdentityError(409, "area.duplicate_name", "同一类别的区域名称不能重复。")
        raise IdentityError(409, "settings.conflict", "设置数据与现有记录冲突。")

    def get_kindergarten(self, session: SessionUser) -> KindergartenRecord:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            record = SettingsRepository(connection).get_kindergarten(kindergarten_id)
        if record is None:
            raise self._not_found("园所")
        return record

    def capabilities_for(self, session: SessionUser) -> list[str]:
        """合并身份能力与基于当前班级关系实时计算的设置能力。"""

        capabilities = {"plans:view", "credentials:manage"}
        if "admin" in session.role_codes:
            capabilities.update({"users:manage", "settings:manage"})
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            if SettingsRepository(connection).has_class_assignments(
                kindergarten_id,
                session.user.id,
            ):
                capabilities.add("class_areas:manage")
        return sorted(capabilities)

    def update_kindergarten(self, session: SessionUser, *, name: str) -> KindergartenRecord:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        normalized_name = _normalize_display_name(name)
        if not normalized_name:
            raise IdentityError(422, "kindergarten.invalid_name", "园所名称不能为空。")
        with self._connect() as connection, connection.transaction():
            record = SettingsRepository(connection).update_kindergarten(
                kindergarten_id,
                name=normalized_name,
            )
        if record is None:
            raise self._not_found("园所")
        return record

    def list_age_groups(self, session: SessionUser) -> list[AgeGroupRecord]:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection, connection.transaction():
            repository = SettingsRepository(connection)
            repository.ensure_age_groups(kindergarten_id)
            records = repository.list_age_groups(kindergarten_id)
        if len(records) != 4:
            raise IdentityError(503, "settings.age_groups_unavailable", "系统年龄段配置不可用。")
        return records

    def list_semesters(
        self,
        session: SessionUser,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[SemesterRecord], int]:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            return SettingsRepository(connection).list_semesters(
                kindergarten_id,
                page=page,
                page_size=page_size,
            )

    def get_semester(self, session: SessionUser, semester_id: UUID) -> SemesterRecord:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            record = SettingsRepository(connection).get_semester(kindergarten_id, semester_id)
        if record is None:
            raise self._not_found("学期")
        return record

    def create_semester(
        self,
        session: SessionUser,
        *,
        name: str,
        start_date: date,
        end_date: date,
        is_active: bool,
    ) -> SemesterRecord:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        if start_date > end_date:
            raise IdentityError(
                422, "semester.invalid_date_range", "学期开始日期不能晚于结束日期。"
            )
        display_name = _required_display_name(
            name,
            code="semester.invalid_name",
            resource="学期",
        )
        try:
            with self._connect() as connection, connection.transaction():
                return SettingsRepository(connection).create_semester(
                    kindergarten_id,
                    name=display_name,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=is_active,
                    actor_id=session.user.id,
                )
        except psycopg.IntegrityError as exc:
            self._raise_write_error(exc)

    def update_semester(
        self,
        session: SessionUser,
        semester_id: UUID,
        *,
        name: str,
        start_date: date,
        end_date: date,
        is_active: bool,
    ) -> SemesterRecord:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        if start_date > end_date:
            raise IdentityError(
                422, "semester.invalid_date_range", "学期开始日期不能晚于结束日期。"
            )
        display_name = _required_display_name(
            name,
            code="semester.invalid_name",
            resource="学期",
        )
        try:
            with self._connect() as connection, connection.transaction():
                record = SettingsRepository(connection).update_semester(
                    kindergarten_id,
                    semester_id,
                    name=display_name,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=is_active,
                    actor_id=session.user.id,
                )
        except psycopg.IntegrityError as exc:
            self._raise_write_error(exc)
        if record is None:
            raise self._not_found("学期")
        return record

    def make_current_semester(
        self,
        session: SessionUser,
        semester_id: UUID,
    ) -> SemesterRecord:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        current = self.get_semester(session, semester_id)
        if not current.is_active:
            raise IdentityError(409, "semester.current_inactive", "停用学期不能设为当前学期。")
        with self._connect() as connection, connection.transaction():
            record = SettingsRepository(connection).make_current_semester(
                kindergarten_id,
                semester_id,
                actor_id=session.user.id,
            )
        if record is None:
            raise self._not_found("学期")
        return record

    def list_classes(
        self,
        session: SessionUser,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[ClassRecord], int]:
        kindergarten_id = self._kindergarten_id(session)
        user_id: UUID | None = None
        if "admin" not in session.role_codes:
            if "teacher" not in session.role_codes:
                raise IdentityError(403, "auth.forbidden", "当前账号没有访问班级的权限。")
            user_id = session.user.id
            with self._connect() as connection:
                if not SettingsRepository(connection).has_class_assignments(
                    kindergarten_id,
                    user_id,
                ):
                    raise IdentityError(403, "class.not_associated", "当前账号未关联任何班级。")
        with self._connect() as connection:
            return SettingsRepository(connection).list_classes(
                kindergarten_id,
                user_id=user_id,
                page=page,
                page_size=page_size,
            )

    def get_class(self, session: SessionUser, class_id: UUID) -> ClassRecord:
        kindergarten_id = self._kindergarten_id(session)
        user_id: UUID | None = None
        if "admin" not in session.role_codes:
            if "teacher" not in session.role_codes:
                raise IdentityError(403, "auth.forbidden", "当前账号没有访问班级的权限。")
            user_id = session.user.id
        with self._connect() as connection:
            record = SettingsRepository(connection).get_class(
                kindergarten_id,
                class_id,
                user_id=user_id,
            )
        if record is None:
            if user_id is not None:
                raise IdentityError(403, "class.not_associated", "只能访问本人关联班级。")
            raise self._not_found("班级")
        return record

    def create_class(
        self,
        session: SessionUser,
        *,
        name: str,
        age_group_id: UUID,
        is_active: bool,
    ) -> ClassRecord:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        display_name = _required_display_name(
            name,
            code="class.invalid_name",
            resource="班级",
        )
        try:
            with self._connect() as connection, connection.transaction():
                repository = SettingsRepository(connection)
                repository.ensure_age_groups(kindergarten_id)
                return repository.create_class(
                    kindergarten_id,
                    name=display_name,
                    name_normalized=_normalize_key(display_name),
                    age_group_id=age_group_id,
                    is_active=is_active,
                    actor_id=session.user.id,
                )
        except psycopg.IntegrityError as exc:
            self._raise_write_error(exc)

    def update_class(
        self,
        session: SessionUser,
        class_id: UUID,
        *,
        name: str,
        age_group_id: UUID,
        is_active: bool,
    ) -> ClassRecord:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        display_name = _required_display_name(
            name,
            code="class.invalid_name",
            resource="班级",
        )
        try:
            with self._connect() as connection, connection.transaction():
                record = SettingsRepository(connection).update_class(
                    kindergarten_id,
                    class_id,
                    name=display_name,
                    name_normalized=_normalize_key(display_name),
                    age_group_id=age_group_id,
                    is_active=is_active,
                    actor_id=session.user.id,
                )
        except psycopg.IntegrityError as exc:
            self._raise_write_error(exc)
        if record is None:
            raise self._not_found("班级")
        return record

    def replace_class_teachers(
        self,
        session: SessionUser,
        class_id: UUID,
        teachers: Sequence[ClassTeacherWrite],
    ) -> ClassRecord:
        self._require_admin(session)
        kindergarten_id = self._kindergarten_id(session)
        lead_ids = [teacher.user_id for teacher in teachers if teacher.is_lead_teacher]
        if not lead_teacher_selection_is_valid(lead_ids):
            raise IdentityError(422, "class.multiple_lead_teachers", "同一班级只能有一位主班教师。")
        try:
            with self._connect() as connection, connection.transaction():
                repository = SettingsRepository(connection)
                requested_user_ids = [teacher.user_id for teacher in teachers]
                if repository.teacher_role_user_ids(
                    kindergarten_id,
                    requested_user_ids,
                ) != set(requested_user_ids):
                    raise IdentityError(
                        422,
                        "class.teacher_role_required",
                        "班级只能关联具有教师角色的账号。",
                    )
                record = repository.replace_class_teachers(
                    kindergarten_id,
                    class_id,
                    [
                        TeacherInput(
                            user_id=teacher.user_id,
                            is_lead_teacher=teacher.is_lead_teacher,
                        )
                        for teacher in teachers
                    ],
                    session.user.id,
                )
        except psycopg.IntegrityError as exc:
            self._raise_write_error(exc)
        if record is None:
            raise self._not_found("班级")
        return record

    def list_class_areas(
        self,
        session: SessionUser,
        class_id: UUID,
        area_type: str,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[AreaRecord], int]:
        kindergarten_id = self._kindergarten_id(session)
        with self._connect() as connection:
            repository = SettingsRepository(connection)
            class_record = repository.get_class(kindergarten_id, class_id)
            if class_record is None:
                raise self._not_found("班级")
            if not repository.is_class_teacher(kindergarten_id, class_id, session.user.id):
                raise IdentityError(403, "class.not_associated", "只有关联教师可维护本班区域。")
            return repository.list_class_areas(
                kindergarten_id,
                class_id,
                area_type,
                page=page,
                page_size=page_size,
            )

    def replace_class_areas(
        self,
        session: SessionUser,
        class_id: UUID,
        area_type: str,
        areas: Sequence[AreaWrite],
    ) -> None:
        kindergarten_id = self._kindergarten_id(session)
        try:
            normalized_names = normalize_class_areas([area.name for area in areas])
        except ValueError as exc:
            code = "area.duplicate_name" if "重复" in str(exc) else "area.invalid_name"
            raise IdentityError(422, code, str(exc)) from None
        normalized = [
            AreaInput(
                id=area.id,
                name=name,
                name_normalized=_normalize_key(name),
                sort_order=area.sort_order,
                is_active=area.is_active,
            )
            for area, name in zip(areas, normalized_names, strict=True)
        ]
        try:
            with self._connect() as connection, connection.transaction():
                repository = SettingsRepository(connection)
                class_record = repository.get_class(kindergarten_id, class_id)
                if class_record is None:
                    raise self._not_found("班级")
                if not repository.is_class_teacher(
                    kindergarten_id,
                    class_id,
                    session.user.id,
                ):
                    raise IdentityError(403, "class.not_associated", "只有关联教师可维护本班区域。")
                try:
                    repository.replace_class_areas(
                        kindergarten_id,
                        class_id,
                        area_type,
                        normalized,
                        session.user.id,
                    )
                except ValueError as exc:
                    raise IdentityError(422, "area.invalid_reference", str(exc)) from None
        except psycopg.IntegrityError as exc:
            self._raise_write_error(exc)
