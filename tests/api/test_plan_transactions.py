# ruff: noqa: F811

from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context


def test_autosave_creates_no_snapshot_and_stale_version_never_overwrites(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = admin_client
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    content = plan["content"]
    content["daily_reflection"] = {
        "highlights": "幼儿主动合作",
        "issues": "",
        "adjustments": "",
    }
    body = {
        "expected_version": plan["version"],
        "content": content,
        "authors": [{"user_id": str(actor.user_id), "sort_order": 0}],
    }

    first = client.put(
        f"/api/v1/plans/{plan_id}/autosave",
        json=body,
        headers=csrf_headers(client),
    )
    stale = client.put(
        f"/api/v1/plans/{plan_id}/autosave",
        json=body,
        headers=csrf_headers(client),
    )

    assert first.status_code == 200
    assert stale.status_code == 409
    assert client.get(f"/api/v1/plans/{plan_id}/snapshots").json()["total"] == 0
    assert client.get(f"/api/v1/plans/{plan_id}").json()["content"] == content
