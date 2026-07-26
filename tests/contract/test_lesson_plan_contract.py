from datetime import date
from importlib import import_module
from uuid import uuid4

import pytest
from pydantic import ValidationError


def _contracts():
    return import_module("packages.contracts.lesson_plans")


def test_open_and_write_contracts_do_not_accept_tenant_or_ownership_mutation() -> None:
    contracts = _contracts()
    class_id = uuid4()
    opened = contracts.PlanOpenRequest(class_id=class_id, plan_date=date(2026, 3, 2))
    assert opened.class_id == class_id

    content = contracts.PlanContentV1.empty()
    with pytest.raises(ValidationError):
        contracts.PlanSaveRequest.model_validate(
            {
                "expected_version": 1,
                "content": content.model_dump(),
                "authors": [{"user_id": str(uuid4()), "sort_order": 0}],
                "kindergarten_id": str(uuid4()),
                "class_id": str(class_id),
                "plan_date": "2026-03-03",
            }
        )


def test_plan_snapshot_and_page_contracts_are_bounded_and_stable() -> None:
    contracts = _contracts()
    assert contracts.PlanPage(items=[], page=1, page_size=100, total=0).total == 0
    with pytest.raises(ValidationError):
        contracts.PlanPage(items=[], page=1, page_size=101, total=0)
    assert set(contracts.SnapshotReason.__args__) == {
        "manual_save",
        "ai_adopted",
        "archive",
        "unarchive",
        "before_restore",
        "restored",
    }
