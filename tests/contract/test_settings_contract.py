from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
import yaml
from pydantic import ValidationError

from packages.contracts import settings as settings_contracts

OPENAPI = yaml.safe_load(
    Path("specs/001-daily-activity-plan/contracts/openapi.yaml").read_text(encoding="utf-8")
)

SETTINGS_PATHS = {
    "/api/v1/settings/kindergarten",
    "/api/v1/settings/age-groups",
    "/api/v1/settings/semesters",
    "/api/v1/settings/semesters/{semester_id}",
    "/api/v1/settings/semesters/{semester_id}/make-current",
    "/api/v1/settings/classes",
    "/api/v1/settings/classes/{class_id}",
    "/api/v1/settings/classes/{class_id}/teachers",
    "/api/v1/settings/classes/{class_id}/areas/{area_type}",
}
AGE_GROUPS = [
    {
        "id": f"00000000-0000-7000-8000-00000000000{index}",
        "code": code,
        "name": name,
        "sort_order": index - 1,
        "is_active": True,
    }
    for index, (code, name) in enumerate(
        [
            ("toddler", "托班"),
            ("small", "小班"),
            ("middle", "中班"),
            ("large", "大班"),
        ],
        start=1,
    )
]


def _resolve(value: dict[str, Any]) -> dict[str, Any]:
    reference = value.get("$ref")
    if reference is None:
        return value
    current: Any = OPENAPI
    for part in str(reference).removeprefix("#/").split("/"):
        current = current[part]
    assert isinstance(current, dict)
    return current


def _operation_parameters(path: str, method: str) -> list[dict[str, Any]]:
    path_item = OPENAPI["paths"][path]
    return [
        _resolve(parameter)
        for parameter in [
            *path_item.get("parameters", []),
            *path_item[method].get("parameters", []),
        ]
    ]


def test_settings_openapi_exposes_only_the_frozen_m3_paths() -> None:
    actual = {path for path in OPENAPI["paths"] if path.startswith("/api/v1/settings/")}

    assert actual >= SETTINGS_PATHS


def test_age_groups_are_a_fixed_four_item_non_paginated_collection() -> None:
    operation = OPENAPI["paths"]["/api/v1/settings/age-groups"]["get"]
    response = _resolve(operation["responses"]["200"])
    schema = _resolve(response["content"]["application/json"]["schema"])
    item_schema = _resolve(schema["items"])

    assert _operation_parameters("/api/v1/settings/age-groups", "get") == []
    assert schema["type"] == "array"
    assert schema["minItems"] == schema["maxItems"] == 4
    assert item_schema["properties"]["code"]["enum"] == [
        "toddler",
        "small",
        "middle",
        "large",
    ]


def test_area_get_uses_default_20_maximum_100_pagination() -> None:
    path = "/api/v1/settings/classes/{class_id}/areas/{area_type}"
    parameters = {
        (parameter["in"], parameter["name"]): parameter["schema"]
        for parameter in _operation_parameters(path, "get")
    }

    assert parameters[("query", "page")] == {
        "type": "integer",
        "minimum": 1,
        "default": 1,
    }
    assert parameters[("query", "page_size")] == {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "default": 20,
    }


def test_area_put_allows_empty_replacement_and_returns_only_204() -> None:
    operation = OPENAPI["paths"]["/api/v1/settings/classes/{class_id}/areas/{area_type}"]["put"]
    request_schema = operation["requestBody"]["content"]["application/json"]["schema"]

    assert request_schema["required"] == ["areas"]
    assert request_schema["properties"]["areas"]["type"] == "array"
    assert "200" not in operation["responses"]
    assert operation["responses"]["204"] == {
        "description": "目标类别区域已整体保存；客户端重新分页读取最新顺序"
    }


def test_shared_contract_exposes_all_m3_request_and_response_models() -> None:
    expected = {
        "Kindergarten",
        "KindergartenPatch",
        "AgeGroup",
        "AgeGroupList",
        "Semester",
        "SemesterWrite",
        "SemesterPage",
        "ClassTeacher",
        "ClassTeacherWrite",
        "ClassTeachersWrite",
        "Class",
        "ClassWrite",
        "ClassPage",
        "Area",
        "AreaWrite",
        "AreaReplaceRequest",
        "AreaPage",
    }

    assert expected <= settings_contracts.__dict__.keys()


def test_shared_age_group_contract_accepts_exactly_the_frozen_ordered_set() -> None:
    age_group_list = settings_contracts.__dict__["AgeGroupList"].model_validate(AGE_GROUPS)

    assert [item.code for item in age_group_list.root] == [
        "toddler",
        "small",
        "middle",
        "large",
    ]
    with pytest.raises(ValidationError):
        settings_contracts.__dict__["AgeGroupList"].model_validate(AGE_GROUPS[:3])
    with pytest.raises(ValidationError):
        settings_contracts.__dict__["AgeGroupList"].model_validate(
            [*AGE_GROUPS[:3], {**AGE_GROUPS[3], "code": "custom"}]
        )


def test_shared_area_contract_keeps_pagination_and_empty_put_semantics_distinct() -> None:
    area_page = settings_contracts.__dict__["AreaPage"].model_validate(
        {
            "items": [],
            "page": 1,
            "page_size": 20,
            "total": 0,
        }
    )
    replacement = settings_contracts.__dict__["AreaReplaceRequest"].model_validate({"areas": []})

    assert area_page.model_dump() == {
        "items": [],
        "page": 1,
        "page_size": 20,
        "total": 0,
    }
    assert replacement.areas == []
    with pytest.raises(ValidationError):
        settings_contracts.__dict__["AreaPage"].model_validate(
            {"items": [], "page": 1, "page_size": 101, "total": 0}
        )


def test_shared_kindergarten_contract_keeps_timezone_read_only_and_fixed() -> None:
    kindergarten = settings_contracts.__dict__["Kindergarten"].model_validate(
        {
            "id": UUID("00000000-0000-7000-8000-000000000001"),
            "name": "测试幼儿园",
            "timezone": "Asia/Shanghai",
            "is_active": True,
        }
    )

    assert kindergarten.timezone == "Asia/Shanghai"
    with pytest.raises(ValidationError):
        settings_contracts.__dict__["KindergartenPatch"].model_validate(
            {"name": "测试幼儿园", "timezone": "UTC"}
        )
