from pathlib import Path

import yaml


def test_plan_and_snapshot_lists_use_bounded_page_parameters() -> None:
    document = yaml.safe_load(
        Path("specs/001-daily-activity-plan/contracts/openapi.yaml").read_text(encoding="utf-8")
    )
    parameters = document["components"]["parameters"]

    assert parameters["Page"]["schema"] == {"type": "integer", "minimum": 1, "default": 1}
    assert parameters["PageSize"]["schema"] == {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "default": 20,
    }
    assert {"$ref": "#/components/parameters/Page"} in document["paths"][
        "/api/v1/plans/{plan_id}/snapshots"
    ]["get"]["parameters"]
    assert {"$ref": "#/components/parameters/PageSize"} in document["paths"][
        "/api/v1/plans/{plan_id}/snapshots"
    ]["get"]["parameters"]
