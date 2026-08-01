"""T127 固定 Word 导出公共契约 RED。"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from packages.contracts import exports
from packages.contracts.common import canonical_request_fingerprint
from packages.contracts.lesson_plans import PlanContentV1

TEMPLATE_SHA256 = "72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043"
EXPECTED_SECTIONS = (
    "morning_activity",
    "morning_talk",
    "group_activity",
    "indoor_area_game",
    "afternoon_outdoor_game",
)


def _required(name: str) -> Any:
    candidate = getattr(exports, name, None)
    if candidate is None:
        pytest.fail(f"T127 Word 导出契约尚未实现：{name}")
    return candidate


def _job_payload(job_id: UUID, plan_id: UUID) -> dict[str, object]:
    return {
        "id": job_id,
        "job_type": "word.export",
        "status": "pending_dispatch",
        "plan_id": plan_id,
        "requested_resource_version": 2,
        "attempt_count": 0,
        "max_attempts": 3,
        "trace_id": uuid4(),
        "created_at": datetime(2026, 3, 2, tzinfo=UTC),
    }


def _export_payload(export_id: UUID, job_id: UUID, plan_id: UUID) -> dict[str, object]:
    return {
        "id": export_id,
        "plan_id": plan_id,
        "plan_version": 2,
        "content_schema_version": 1,
        "content_sha256": "1" * 64,
        "job_id": job_id,
        "status": "pending",
        "display_filename": "一日活动计划_向日葵班_2026-03-02.docx",
        "file_size": None,
        "file_sha256": None,
        "template_sha256": TEMPLATE_SHA256,
        "exported_at": None,
        "file_missing_at": None,
        "error_code": None,
        "error_summary": None,
        "created_at": datetime(2026, 3, 2, tzinfo=UTC),
    }


def test_export_section_contract_is_exactly_five_and_excludes_reflection() -> None:
    required_sections = _required("REQUIRED_EXPORT_SECTIONS")

    assert tuple(required_sections) == EXPECTED_SECTIONS
    assert "daily_reflection" not in required_sections


def test_confirmation_required_error_is_closed_and_carries_only_export_sections() -> None:
    error_type = _required("ExportConfirmationRequiredError")
    request_id = uuid4()

    error = error_type(
        code="export.confirmation_required",
        message="以下栏目内容不完整，确认后仍可导出。",
        request_id=request_id,
        missing_sections=["morning_talk"],
    )

    assert error.model_dump(mode="json") == {
        "code": "export.confirmation_required",
        "message": "以下栏目内容不完整，确认后仍可导出。",
        "request_id": str(request_id),
        "field_errors": [],
        "missing_sections": ["morning_talk"],
    }
    with pytest.raises(ValidationError):
        error_type(
            code="request.idempotency_conflict",
            message="错误类型不能复用。",
            request_id=request_id,
            missing_sections=["morning_talk"],
        )
    with pytest.raises(ValidationError):
        error_type(
            code="export.confirmation_required",
            message="栏目不能重复。",
            request_id=request_id,
            missing_sections=["morning_talk", "morning_talk"],
        )


def test_export_request_is_closed_and_requires_version_content_authors_and_confirmation() -> None:
    request_type = _required("ExportRequest")
    author_id = uuid4()
    request = request_type(
        expected_version=3,
        content=PlanContentV1.empty(),
        authors=[{"user_id": author_id, "sort_order": 0}],
        confirm_incomplete=False,
    )

    assert request.expected_version == 3
    assert request.confirm_incomplete is False
    with pytest.raises(ValidationError):
        request_type(
            expected_version=0,
            content=PlanContentV1.empty(),
            authors=[{"user_id": author_id, "sort_order": 0}],
            confirm_incomplete=False,
        )
    with pytest.raises(ValidationError):
        request_type(
            expected_version=3,
            content=PlanContentV1.empty(),
            authors=[{"user_id": author_id, "sort_order": 0}],
            confirm_incomplete=False,
            kindergarten_id=uuid4(),
        )


def test_export_response_page_and_download_metadata_are_closed_and_bounded() -> None:
    export_type = _required("Export")
    accepted_type = _required("ExportAccepted")
    page_type = _required("ExportPage")
    download_type = _required("ExportDownloadMetadata")
    export_id, job_id, plan_id = uuid4(), uuid4(), uuid4()
    export_payload = _export_payload(export_id, job_id, plan_id)

    record = export_type(**export_payload)
    accepted = accepted_type(job=_job_payload(job_id, plan_id), export=export_payload)
    page = page_type(items=[export_payload], page=1, page_size=20, total=1)
    download = download_type(
        display_filename=record.display_filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_size=1024,
        file_sha256="2" * 64,
    )

    assert accepted.export.id == export_id
    assert page.total == 1
    assert download.file_size == 1024
    with pytest.raises(ValidationError):
        export_type(**(export_payload | {"storage_key": "/private/export.docx"}))
    with pytest.raises(ValidationError):
        export_type(**(export_payload | {"content_schema_version": 2}))
    with pytest.raises(ValidationError):
        export_type(**(export_payload | {"template_sha256": "f" * 64}))
    with pytest.raises(ValidationError):
        page_type(items=[], page=1, page_size=101, total=0)


def test_export_fingerprint_includes_actual_plan_path() -> None:
    body = {
        "expected_version": 2,
        "content": PlanContentV1.empty().model_dump(mode="json"),
        "authors": [{"user_id": str(uuid4()), "sort_order": 0}],
        "confirm_incomplete": True,
    }
    first = canonical_request_fingerprint(
        method="POST",
        route_template="/api/v1/plans/{plan_id}/exports",
        path_params={"plan_id": uuid4()},
        query_params=[],
        body=body,
    )
    second = canonical_request_fingerprint(
        method="POST",
        route_template="/api/v1/plans/{plan_id}/exports",
        path_params={"plan_id": uuid4()},
        query_params=[],
        body=body,
    )

    assert first != second
