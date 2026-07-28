"""M6 教案 AI 公共契约的 RED 验收。"""

from datetime import UTC, datetime
from types import ModuleType
from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from packages.contracts import jobs as job_contracts
from packages.contracts import lesson_plans as plan_contracts
from packages.contracts.common import canonical_request_fingerprint


def _contract(module: ModuleType, name: str) -> Any:
    value = getattr(module, name, None)
    assert value is not None, f"M6 contract missing: {module.__name__}.{name}"
    return value


def _children(*statuses: str) -> list[object]:
    child_type = _contract(job_contracts, "JobChild")
    return [
        child_type(
            id=uuid4(),
            job_type=job_type,
            status=status,
            target_section=target_section,
        )
        for status, job_type, target_section in zip(
            statuses,
            (
                "ai.morning_activity",
                "ai.morning_talk",
                "ai.indoor_area_game",
                "ai.afternoon_outdoor_game",
            ),
            (
                "morning_activity",
                "morning_talk",
                "indoor_area_game",
                "afternoon_outdoor_game",
            ),
            strict=True,
        )
    ]


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        (
            ("pending_dispatch", "queued", "running", "retrying"),
            ("running", False),
        ),
        (
            (
                "awaiting_confirmation",
                "adopted",
                "rejected",
                "expired",
            ),
            ("succeeded", False),
        ),
        (
            ("awaiting_confirmation", "adopted", "rejected", "failed"),
            ("succeeded", True),
        ),
        (("failed", "failed", "failed", "failed"), ("failed", False)),
    ],
)
def test_batch_status_is_derived_only_from_exactly_four_children(
    statuses: tuple[str, str, str, str],
    expected: tuple[str, bool],
) -> None:
    derive = _contract(job_contracts, "derive_batch_projection")

    assert derive(_children(*statuses)) == expected


def test_ai_child_succeeded_is_not_a_valid_batch_completion_state() -> None:
    derive = _contract(job_contracts, "derive_batch_projection")

    with pytest.raises(ValueError, match="无法派生"):
        derive(
            _children(
                "succeeded",
                "awaiting_confirmation",
                "adopted",
                "rejected",
            )
        )


def test_batch_job_projects_zero_attempts_and_rejects_execution_shape() -> None:
    job_type = _contract(job_contracts, "Job")
    children = _children(
        "awaiting_confirmation",
        "awaiting_confirmation",
        "awaiting_confirmation",
        "awaiting_confirmation",
    )
    common = {
        "id": uuid4(),
        "job_type": "ai.batch",
        "status": "succeeded",
        "attempt_count": 0,
        "max_attempts": 0,
        "trace_id": uuid4(),
        "created_at": datetime.now(UTC),
        "children": children,
    }

    assert job_type(**common).attempt_count == 0
    with pytest.raises(ValidationError):
        job_type(**(common | {"attempt_count": 1, "max_attempts": 3}))
    with pytest.raises(ValidationError):
        job_type(**(common | {"children": children[:3]}))


def test_executable_job_rejects_batch_children_and_zero_attempt_limit() -> None:
    job_type = _contract(job_contracts, "Job")
    common = {
        "id": uuid4(),
        "job_type": "ai.morning_activity",
        "status": "failed",
        "attempt_count": 3,
        "max_attempts": 3,
        "trace_id": uuid4(),
        "created_at": datetime.now(UTC),
    }

    assert job_type(**common).max_attempts == 3
    with pytest.raises(ValidationError):
        job_type(**(common | {"attempt_count": 0, "max_attempts": 0}))
    with pytest.raises(ValidationError):
        job_type(**(common | {"children": _children("failed", "failed", "failed", "failed")}))


@pytest.mark.parametrize(
    ("job_type", "status", "has_result", "allowed"),
    [
        ("ai.morning_activity", "failed", True, True),
        ("ai.daily_reflection", "failed", True, True),
        ("ai.morning_activity", "running", True, False),
        ("ai.morning_activity", "failed", False, False),
        ("ai.batch", "failed", True, False),
        ("prompt.test", "failed", True, False),
        ("word.export", "failed", True, False),
    ],
)
def test_explicit_retry_matrix_is_failed_ai_result_only(
    job_type: str,
    status: str,
    has_result: bool,
    allowed: bool,
) -> None:
    predicate = _contract(job_contracts, "is_explicit_ai_retry_allowed")

    assert predicate(job_type=job_type, status=status, has_ai_result=has_result) is allowed
    assert _contract(job_contracts, "JOB_RETRY_NOT_ALLOWED") == "job.retry_not_allowed"


def test_retry_fingerprint_includes_actual_job_id() -> None:
    first = canonical_request_fingerprint(
        method="POST",
        route_template="/api/v1/jobs/{job_id}/retry",
        path_params={"job_id": "01900000-0000-7000-8000-000000000001"},
        query_params=[],
        body={},
    )
    second = canonical_request_fingerprint(
        method="POST",
        route_template="/api/v1/jobs/{job_id}/retry",
        path_params={"job_id": "01900000-0000-7000-8000-000000000002"},
        query_params=[],
        body={},
    )

    assert first != second


def test_adoption_body_accepts_only_expected_version() -> None:
    request = plan_contracts.VersionRequest(expected_version=3)

    assert request.model_dump() == {"expected_version": 3}
    with pytest.raises(ValidationError):
        plan_contracts.VersionRequest.model_validate(
            {"expected_version": 3, "teacher_context": "后来填写"}
        )


def test_generation_requests_are_closed_and_task_specific() -> None:
    batch_request = _contract(plan_contracts, "AiBatchRequest")
    generation_request = _contract(plan_contracts, "AiGenerationRequest")

    assert batch_request(expected_version=2, teacher_context="春天").expected_version == 2
    with pytest.raises(ValidationError):
        batch_request(expected_version=2, teacher_context="春天", content={})
    assert (
        generation_request(
            task_code="morning_talk",
            expected_version=2,
            teacher_context="围绕春天",
        ).task_code
        == "morning_talk"
    )
    with pytest.raises(ValidationError):
        generation_request(task_code="morning_talk", expected_version=2)
    with pytest.raises(ValidationError):
        generation_request(
            task_code="morning_talk",
            expected_version=2,
            teacher_context="围绕春天",
            content=plan_contracts.PlanContentV1.empty(),
        )
