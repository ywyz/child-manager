from datetime import date

from fastapi.testclient import TestClient

from tests.api.passkey_helpers import ActorFixture, csrf_headers


def provision_editable_plan_context(
    client: TestClient,
    actor: ActorFixture,
    *,
    plan_date: date = date(2026, 3, 2),
) -> tuple[str, str]:
    headers = csrf_headers(client)
    roles = client.put(
        f"/api/v1/users/{actor.user_id}/roles",
        json={"role_codes": ["admin", "teacher"]},
        headers=headers,
    )
    assert roles.status_code == 200
    age_groups = client.get("/api/v1/settings/age-groups")
    assert age_groups.status_code == 200
    semester = client.post(
        "/api/v1/settings/semesters",
        json={
            "name": "2026 春季学期",
            "start_date": "2026-02-04",
            "end_date": "2026-06-30",
            "is_active": True,
        },
        headers=csrf_headers(client),
    )
    assert semester.status_code == 201
    current = client.post(
        f"/api/v1/settings/semesters/{semester.json()['id']}/make-current",
        headers=csrf_headers(client),
    )
    assert current.status_code == 200
    classroom = client.post(
        "/api/v1/settings/classes",
        json={
            "name": "向日葵班",
            "age_group_id": age_groups.json()[2]["id"],
            "is_active": True,
        },
        headers=csrf_headers(client),
    )
    assert classroom.status_code == 201
    class_id = classroom.json()["id"]
    association = client.put(
        f"/api/v1/settings/classes/{class_id}/teachers",
        json={"teachers": [{"user_id": str(actor.user_id), "is_lead_teacher": True}]},
        headers=csrf_headers(client),
    )
    assert association.status_code == 200
    opened = client.post(
        "/api/v1/plans/open",
        json={"class_id": class_id, "plan_date": plan_date.isoformat()},
        headers=csrf_headers(client),
    )
    assert opened.status_code == 200
    return class_id, opened.json()["id"]
