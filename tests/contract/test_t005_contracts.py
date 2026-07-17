"""T005 契约骨架回归测试：确保后续阶段接口不提前固化到 contracts 包。"""

import inspect
from pathlib import Path
from types import ModuleType

import pytest
from pydantic import BaseModel, ValidationError

from packages.contracts import (
    audit,
    exports,
    identity,
    jobs,
    lesson_plans,
    prompts,
    settings,
)
from packages.contracts.audit import AuditEventReference
from packages.contracts.exports import ExportReference
from packages.contracts.lesson_plans import LessonPlanReference
from packages.contracts.prompts import PromptReference


def _public_base_model_names(module: ModuleType) -> set[str]:
    """返回模块中所有公开 BaseModel 子类的名称集合（含导入的类，不含 BaseModel 本身）。"""
    return {
        name
        for name, obj in inspect.getmembers(module)
        if inspect.isclass(obj)
        and issubclass(obj, BaseModel)
        and obj is not BaseModel
        and not name.startswith("_")
    }


class TestIdentitySkeleton:
    """identity.py 在 M2 扩展为 Auth/Users 公共契约。"""

    def test_current_user_valid(self) -> None:
        user = identity.CurrentUser(
            id="u1",
            username="teacher-a",
            display_name="王老师",
            kindergarten=identity.KindergartenSnapshot(
                id="k1", name="实验幼儿园", timezone="Asia/Shanghai"
            ),
            role_codes=["teacher"],
        )
        assert user.id == "u1"
        assert user.role_codes == ["teacher"]
        assert user.kindergarten_id == "k1"
        assert user.roles == ["teacher"]

    def test_current_user_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            identity.CurrentUser(
                id="u1",
                username="teacher-a",
                display_name="王老师",
                password="secret",  # type: ignore[call-arg]
            )

    def test_identity_has_auth_contracts(self) -> None:
        assert hasattr(identity, "LoginRequest")
        assert hasattr(identity, "CurrentUser")
        assert hasattr(identity, "CsrfResponse")


class TestSettingsSkeleton:
    """settings.py 只允许 KindergartenSummary 最小引用骨架。"""

    def test_kindergarten_summary_valid(self) -> None:
        ks = settings.KindergartenSummary(
            id="k1",
            name="实验幼儿园",
            timezone="Asia/Shanghai",
        )
        assert ks.name == "实验幼儿园"

    def test_kindergarten_summary_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            settings.KindergartenSummary(
                id="k1",
                name="实验幼儿园",
                address=" somewhere",  # type: ignore[call-arg]
            )


class TestJobsSkeleton:
    """jobs.py 只允许 WorkerMessage 最小引用骨架，且只传 job_id。"""

    def test_worker_message_valid(self) -> None:
        msg = jobs.WorkerMessage(job_id="job-123")
        assert msg.job_id == "job-123"

    def test_worker_message_rejects_sensitive_payload(self) -> None:
        with pytest.raises(ValidationError):
            jobs.WorkerMessage(
                job_id="job-123",
                api_key="sk-secret",  # type: ignore[call-arg]
            )

    def test_worker_message_rejects_result_body(self) -> None:
        with pytest.raises(ValidationError):
            jobs.WorkerMessage(
                job_id="job-123",
                result={"content": "ai-generated"},  # type: ignore[call-arg]
            )


class TestOtherSkeletons:
    """audit/exports/lesson_plans/prompts 只保留最小引用型骨架。"""

    def test_audit_event_reference(self) -> None:
        ref = AuditEventReference(id="e1", event_type="login")
        assert ref.event_type == "login"

    def test_export_reference(self) -> None:
        ref = ExportReference(id="x1", plan_id="p1")
        assert ref.plan_id == "p1"

    def test_lesson_plan_reference(self) -> None:
        ref = LessonPlanReference(id="p1", class_id="c1", plan_date="2026-07-16")
        assert ref.plan_date == "2026-07-16"

    def test_prompt_reference(self) -> None:
        ref = PromptReference(id="prompt-1", code="daily_plan")
        assert ref.code == "daily_plan"


class TestPublicClassScope:
    """各契约模块的公开 BaseModel 类集合必须精确等于最小骨架范围。"""

    @pytest.mark.parametrize(
        ("module", "expected"),
        [
            pytest.param(
                identity,
                {
                    "CurrentUser",
                    "KindergartenSnapshot",
                    "CsrfResponse",
                    "LoginRequest",
                    "RefreshRequest",
                    "ChangePasswordRequest",
                    "UserCreateRequest",
                    "UserPatch",
                    "UserResponse",
                    "UserPage",
                    "ResetPasswordRequest",
                    "UserRolesUpdateRequest",
                },
                id="identity",
            ),
            pytest.param(settings, {"KindergartenSummary"}, id="settings"),
            pytest.param(jobs, {"WorkerMessage"}, id="jobs"),
            pytest.param(audit, {"AuditEventReference"}, id="audit"),
            pytest.param(exports, {"ExportReference"}, id="exports"),
            pytest.param(
                lesson_plans,
                {"LessonPlanReference"},
                id="lesson_plans",
            ),
            pytest.param(prompts, {"PromptReference"}, id="prompts"),
        ],
    )
    def test_module_public_base_model_classes(
        self,
        module: ModuleType,
        expected: set[str],
    ) -> None:
        assert _public_base_model_names(module) == expected


class TestModelsFileRemoved:
    """models.py（T029+ AI 模型档案完整契约）不应存在。"""

    def test_models_file_removed(self) -> None:
        contracts_dir = Path(__file__).resolve().parents[2] / "packages" / "contracts"
        models_file = contracts_dir / "models.py"
        assert not models_file.exists(), "T005 不应包含 models.py"
