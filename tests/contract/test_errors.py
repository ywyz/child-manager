from pathlib import Path

import yaml


def test_plan_conflicts_use_the_shared_error_envelope() -> None:
    document = yaml.safe_load(
        Path("specs/001-daily-activity-plan/contracts/openapi.yaml").read_text(encoding="utf-8")
    )
    for path, method in [
        ("/api/v1/plans/{plan_id}/autosave", "put"),
        ("/api/v1/plans/{plan_id}/save", "put"),
        ("/api/v1/plans/{plan_id}/archive", "post"),
        ("/api/v1/plans/{plan_id}/unarchive", "post"),
        ("/api/v1/plans/{plan_id}/snapshots/{snapshot_id}/restore", "post"),
    ]:
        assert document["paths"][path][method]["responses"]["409"] == {
            "$ref": "#/components/responses/Conflict"
        }
