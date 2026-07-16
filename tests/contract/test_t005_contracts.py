"""T005 契约骨架回归测试：确保后续阶段接口不提前固化到 contracts 包。"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from packages.contracts import identity, jobs, settings
from packages.contracts.audit import AuditEventReference
from packages.contracts.exports import ExportReference
from packages.contracts.lesson_plans import LessonPlanReference
from packages.contracts.prompts import PromptReference


class TestIdentitySkeleton:
    """identity.py 只允许 CurrentUser 最小引用骨架。"""

    def test_current_user_valid(self) -> None:
        user = identity.CurrentUser(
            id="u1",
            username="teacher-a",
            display_name="王老师",
            roles=["teacher"],
        )
        assert user.id == "u1"
        assert user.roles == ["teacher"]

    def test_current_user_rejects_extra_fields(self) -> None:
        with pytest.raises(ValidationError):
            identity.CurrentUser(
                id="u1",
                username="teacher-a",
                display_name="王老师",
                password="secret",  # type: ignore[call-arg]
            )

    def test_no_login_response_in_identity_module(self) -> None:
        assert not hasattr(identity, "LoginResponse")
        assert not hasattr(identity, "TokenRefreshResponse")


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


class TestModelsFileRemoved:
    """models.py（T029+ AI 模型档案完整契约）不应存在。"""

    def test_models_file_removed(self) -> None:
        contracts_dir = Path(__file__).resolve().parents[2] / "packages" / "contracts"
        models_file = contracts_dir / "models.py"
        assert not models_file.exists(), "T005 不应包含 models.py"
