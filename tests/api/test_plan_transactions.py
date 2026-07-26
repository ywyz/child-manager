# ruff: noqa: F811

from importlib import import_module

import psycopg
import pytest
from fastapi.testclient import TestClient

from packages.backend.audit.repository import AuditRepository
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
    assert stale.json()["code"] == "lesson_plan.version_conflict"
    assert client.get(f"/api/v1/plans/{plan_id}/snapshots").json()["total"] == 0
    assert client.get(f"/api/v1/plans/{plan_id}").json()["content"] == content


def test_manual_save_rolls_back_content_version_snapshot_and_audit_together(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, actor = admin_client
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id}").json()
    content = before["content"]
    content["daily_reflection"] = {
        "highlights": "这次写入必须回滚",
        "issues": "",
        "adjustments": "",
    }

    def fail_audit(self: AuditRepository, **_kwargs: object) -> None:
        del self
        raise RuntimeError("test plan transaction rollback")

    monkeypatch.setattr(AuditRepository, "append", fail_audit)
    with pytest.raises(RuntimeError, match="test plan transaction rollback"):
        client.put(
            f"/api/v1/plans/{plan_id}/save",
            json={
                "expected_version": before["version"],
                "content": content,
                "authors": [{"user_id": str(actor.user_id), "sort_order": 0}],
            },
            headers=csrf_headers(client),
        )

    after = client.get(f"/api/v1/plans/{plan_id}").json()
    assert after["content"] == before["content"]
    assert after["version"] == before["version"]
    assert client.get(f"/api/v1/plans/{plan_id}/snapshots").json()["total"] == 0

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    event_code = import_module("packages.contracts.audit").IdentityAuditEventCode
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT count(*) FROM audit_events
            WHERE kindergarten_id=%s AND resource_id=%s AND event_code=%s""",
            (
                actor.kindergarten_id,
                plan_id,
                event_code.PLAN_MANUALLY_SAVED.value,
            ),
        ).fetchone() == (0,)
