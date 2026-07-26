# ruff: noqa: F811

from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context


def test_unassociated_admin_can_view_and_archive_but_cannot_edit_body(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = admin_client
    class_id, plan_id = provision_editable_plan_context(client, actor)
    detached = client.put(
        f"/api/v1/settings/classes/{class_id}/teachers",
        json={"teachers": []},
        headers=csrf_headers(client),
    )
    assert detached.status_code == 200

    viewed = client.get(f"/api/v1/plans/{plan_id}")
    edited = client.put(
        f"/api/v1/plans/{plan_id}/save",
        json={
            "expected_version": viewed.json()["version"],
            "content": viewed.json()["content"],
            "authors": [{"user_id": str(actor.user_id), "sort_order": 0}],
        },
        headers=csrf_headers(client),
    )
    archived = client.post(
        f"/api/v1/plans/{plan_id}/archive",
        json={"expected_version": viewed.json()["version"]},
        headers=csrf_headers(client),
    )

    assert viewed.status_code == 200
    assert edited.status_code == 403
    assert archived.status_code == 200


def test_open_requires_current_semester(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = admin_client
    roles = client.put(
        f"/api/v1/users/{actor.user_id}/roles",
        json={"role_codes": ["admin", "teacher"]},
        headers=csrf_headers(client),
    )
    assert roles.status_code == 200
    age_groups = client.get("/api/v1/settings/age-groups").json()
    classroom = client.post(
        "/api/v1/settings/classes",
        json={"name": "无学期班", "age_group_id": age_groups[0]["id"], "is_active": True},
        headers=csrf_headers(client),
    )
    class_id = classroom.json()["id"]
    client.put(
        f"/api/v1/settings/classes/{class_id}/teachers",
        json={"teachers": [{"user_id": str(actor.user_id), "is_lead_teacher": True}]},
        headers=csrf_headers(client),
    )

    response = client.post(
        "/api/v1/plans/open",
        json={"class_id": class_id, "plan_date": "2026-03-02"},
        headers=csrf_headers(client),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "semester.current_required"
