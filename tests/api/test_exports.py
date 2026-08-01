# ruff: noqa: F811

"""T128/T137/T139 Word 导出事务、幂等、权限与下载 RED。"""

import json
from copy import deepcopy
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.dependencies import current_session
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context

FIXTURE = Path("tests/fixtures/word/daily_activity_plan_v1.json")


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _complete_content() -> dict[str, object]:
    return deepcopy(json.loads(FIXTURE.read_text(encoding="utf-8"))["content_snapshot"])


def _runtime(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    (tmp_path / "exports").mkdir()
    (tmp_path / "temporary").mkdir()
    monkeypatch.setenv("CHILD_MANAGER_RUNTIME_ROOT", str(tmp_path))


def _headers(client: TestClient, key: str | None = None) -> dict[str, str]:
    return csrf_headers(client) | {"Idempotency-Key": key or str(uuid4())}


def _request_body(
    plan: dict[str, object],
    *,
    content: dict[str, object] | None = None,
    confirm_incomplete: bool,
) -> dict[str, object]:
    return {
        "expected_version": plan["version"],
        "content": content if content is not None else _complete_content(),
        "authors": [
            {"user_id": author["user_id"], "sort_order": author["sort_order"]}
            for author in plan["authors"]  # type: ignore[union-attr]
        ],
        "confirm_incomplete": confirm_incomplete,
    }


def test_missing_five_columns_requires_confirmation_with_zero_side_effects_and_key_reuse(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id}").json()
    incomplete = _complete_content()
    incomplete["morning_talk"] = {"topic": "", "questions": []}
    incomplete["daily_reflection"] = {"highlights": "", "issues": "", "adjustments": ""}
    key = str(uuid4())

    rejected = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(before, content=incomplete, confirm_incomplete=False),
        headers=_headers(client, key),
    )

    assert rejected.status_code == 409
    rejected_body = rejected.json()
    assert rejected_body["code"] == "export.confirmation_required"
    assert rejected_body["missing_sections"] == ["morning_talk"]
    assert set(rejected_body) == {
        "code",
        "message",
        "request_id",
        "field_errors",
        "missing_sections",
    }
    assert client.get(f"/api/v1/plans/{plan_id}").json()["version"] == before["version"]
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            "SELECT count(*) FROM daily_activity_plan_exports WHERE kindergarten_id=%s",
            (actor.kindergarten_id,),
        ).fetchone() == (0,)
        assert connection.execute(
            """SELECT count(*) FROM background_jobs
            WHERE kindergarten_id=%s AND job_type='word.export'""",
            (actor.kindergarten_id,),
        ).fetchone() == (0,)

    accepted = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(before, content=incomplete, confirm_incomplete=True),
        headers=_headers(client, key),
    )
    assert accepted.status_code == 202


@pytest.mark.parametrize(
    ("section", "field", "invalid_value"),
    [
        ("morning_activity", "objectives", ["只有一项。"]),
        ("morning_talk", "questions", ["只有一个问题？"]),
        ("indoor_area_game", "guidance_points", ["缺少句号", "第二项。", "第三项。"]),
        ("afternoon_outdoor_game", "support_strategies", ["只有一项。"]),
    ],
)
def test_fixed_section_schema_incompleteness_requires_confirmation(
    admin_client: tuple[TestClient, ActorFixture],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    section: str,
    field: str,
    invalid_value: list[str],
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    content = _complete_content()
    content_section = cast(dict[str, object], content[section])
    content_section[field] = invalid_value

    response = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(plan, content=content, confirm_incomplete=False),
        headers=_headers(client),
    )

    assert response.status_code == 409
    assert response.json()["missing_sections"] == [section]


def test_empty_reflection_is_accepted_and_freezes_save_export_and_job_atomically(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id}").json()
    content = _complete_content()
    content["daily_reflection"] = {"highlights": "", "issues": "", "adjustments": ""}

    response = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(before, content=content, confirm_incomplete=False),
        headers=_headers(client),
    )

    assert response.status_code == 202
    body = response.json()
    assert body["job"]["job_type"] == "word.export"
    assert body["job"]["status"] == "pending_dispatch"
    assert body["export"]["status"] == "pending"
    after = client.get(f"/api/v1/plans/{plan_id}").json()
    assert after["version"] == before["version"] + 1
    assert after["content"] == content
    assert client.get(f"/api/v1/plans/{plan_id}/snapshots").json()["total"] == 0
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        row = connection.execute(
            """SELECT context_snapshot,content_snapshot,content_schema_version,content_sha256,
                      plan_version,job_id,storage_key
            FROM daily_activity_plan_exports
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, body["export"]["id"]),
        ).fetchone()
    assert row is not None
    assert row[0]["class_name"] == before["class_name_snapshot"]
    assert row[1] == content
    assert row[2] == 1 and len(row[3]) == 64
    assert row[4] == after["version"]
    assert str(row[5]) == body["job"]["id"]
    assert not str(row[6]).startswith("/")


def test_worker_completion_fences_expired_lease_owner(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    accepted = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(plan, confirm_incomplete=False),
        headers=_headers(client),
    )
    assert accepted.status_code == 202
    export_id = UUID(accepted.json()["export"]["id"])
    job_id = UUID(accepted.json()["job"]["id"])
    runner_module = import_module("packages.backend.exports.runner")

    with psycopg.connect(_native_url(isolated_database_url), autocommit=True) as connection:
        store = runner_module.PostgresWordExportStore(connection)
        assert store.claim(actor.kindergarten_id, job_id, worker_id="worker-a")
        connection.execute(
            """UPDATE background_jobs SET lease_expires_at=now()-interval '1 second'
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, job_id),
        )
        assert store.claim(actor.kindergarten_id, job_id, worker_id="worker-b")
        stale_publish_called = False

        def stale_publish() -> object:
            nonlocal stale_publish_called
            stale_publish_called = True
            return SimpleNamespace(file_size=1, file_sha256="1" * 64)

        stale = store.publish_succeeded(
            actor.kindergarten_id,
            export_id,
            worker_id="worker-a",
            publish=stale_publish,
            cleanup=lambda: None,
        )
        winner = store.publish_succeeded(
            actor.kindergarten_id,
            export_id,
            worker_id="worker-b",
            publish=lambda: SimpleNamespace(file_size=2, file_sha256="2" * 64),
            cleanup=lambda: None,
        )
        row = connection.execute(
            """SELECT export.status,export.file_size,export.file_sha256,job.execution_status
            FROM daily_activity_plan_exports AS export
            JOIN background_jobs AS job
              ON job.kindergarten_id=export.kindergarten_id AND job.id=export.job_id
            WHERE export.kindergarten_id=%s AND export.id=%s""",
            (actor.kindergarten_id, export_id),
        ).fetchone()

    assert stale is None
    assert stale_publish_called is False
    assert winner is not None
    assert row == ("succeeded", 2, "2" * 64, "succeeded")


def test_idempotency_replays_same_export_and_conflicts_across_actual_plan_path(
    admin_client: tuple[TestClient, ActorFixture],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    class_id, first_plan_id = provision_editable_plan_context(client, actor)
    first_plan = client.get(f"/api/v1/plans/{first_plan_id}").json()
    key = str(uuid4())
    request = _request_body(first_plan, confirm_incomplete=False)

    first = client.post(
        f"/api/v1/plans/{first_plan_id}/exports",
        json=request,
        headers=_headers(client, key),
    )
    replay = client.post(
        f"/api/v1/plans/{first_plan_id}/exports",
        json=request,
        headers=_headers(client, key),
    )
    opened = client.post(
        "/api/v1/plans/open",
        json={"class_id": class_id, "plan_date": "2026-03-03"},
        headers=csrf_headers(client),
    )
    assert opened.status_code == 201
    other_plan = opened.json()
    conflict = client.post(
        f"/api/v1/plans/{other_plan['id']}/exports",
        json=_request_body(other_plan, confirm_incomplete=False),
        headers=_headers(client, key),
    )

    assert first.status_code == replay.status_code == 202
    assert first.json()["job"]["id"] == replay.json()["job"]["id"]
    assert first.json()["export"]["id"] == replay.json()["export"]["id"]
    assert conflict.status_code == 409
    assert conflict.json()["code"] == "request.idempotency_conflict"


def test_idempotency_replay_reauthorizes_live_class_relationship(
    admin_client: tuple[TestClient, ActorFixture],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    key = str(uuid4())
    request = _request_body(plan, confirm_incomplete=False)

    accepted = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=request,
        headers=_headers(client, key),
    )
    assert accepted.status_code == 202
    detached = client.put(
        f"/api/v1/settings/classes/{class_id}/teachers",
        json={"teachers": []},
        headers=csrf_headers(client),
    )
    assert detached.status_code == 200
    teacher_session = SimpleNamespace(
        user=SimpleNamespace(
            id=actor.user_id,
            kindergarten_id=actor.kindergarten_id,
            username="admin",
            display_name="测试管理员",
            status="active",
            is_active=True,
        ),
        role_codes=["teacher"],
        token_family_id=actor.session_id,
        session_id=actor.session_id,
        last_reauthenticated_at=None,
    )
    app = cast(FastAPI, client.app)
    app.dependency_overrides[current_session] = lambda: teacher_session

    replay = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=request,
        headers=_headers(client, key),
    )

    assert replay.status_code == 403
    assert replay.json()["code"] == "class.not_associated"


def test_history_and_detail_reauthorize_live_relationship_and_hide_cross_tenant(
    admin_client: tuple[TestClient, ActorFixture],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    accepted = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(plan, confirm_incomplete=False),
        headers=_headers(client),
    )
    assert accepted.status_code == 202
    export_id = accepted.json()["export"]["id"]
    detached = client.put(
        f"/api/v1/settings/classes/{class_id}/teachers",
        json={"teachers": []},
        headers=csrf_headers(client),
    )
    assert detached.status_code == 200
    app = cast(FastAPI, client.app)
    app.dependency_overrides[current_session] = lambda: SimpleNamespace(
        user=SimpleNamespace(
            id=actor.user_id,
            kindergarten_id=actor.kindergarten_id,
            username="admin",
            display_name="测试管理员",
            status="active",
            is_active=True,
        ),
        role_codes=["teacher"],
        token_family_id=actor.session_id,
        session_id=actor.session_id,
        last_reauthenticated_at=None,
    )

    assert client.get(f"/api/v1/plans/{plan_id}/exports").status_code == 403
    assert client.get(f"/api/v1/exports/{export_id}").status_code == 403

    app.dependency_overrides[current_session] = lambda: SimpleNamespace(
        user=SimpleNamespace(
            id=actor.user_id,
            kindergarten_id=uuid4(),
            username="other-admin",
            display_name="其他园管理员",
            status="active",
            is_active=True,
        ),
        role_codes=["admin"],
        token_family_id=actor.session_id,
        session_id=actor.session_id,
        last_reauthenticated_at=None,
    )

    assert client.get(f"/api/v1/plans/{plan_id}/exports").status_code == 404
    assert client.get(f"/api/v1/exports/{export_id}").status_code == 404


def test_missing_storage_configuration_creates_nothing(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, actor = admin_client
    monkeypatch.delenv("CHILD_MANAGER_RUNTIME_ROOT", raising=False)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    missing_config = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(plan, confirm_incomplete=False),
        headers=_headers(client),
    )
    assert missing_config.status_code == 503
    assert missing_config.json()["code"] == "configuration.unavailable"

    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            """SELECT count(*) FROM background_jobs
            WHERE kindergarten_id=%s AND job_type='word.export'""",
            (actor.kindergarten_id,),
        ).fetchone() == (0,)


def test_stale_version_creates_nothing(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    request = _request_body(plan, confirm_incomplete=False)
    request["expected_version"] = cast(int, plan["version"]) + 1

    response = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=request,
        headers=_headers(client),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "lesson_plan.version_conflict"
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            "SELECT count(*) FROM daily_activity_plan_exports WHERE kindergarten_id=%s",
            (actor.kindergarten_id,),
        ).fetchone() == (0,)


def test_database_failure_rolls_back_plan_export_job_and_audit(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id}").json()
    repository_type = import_module("packages.backend.exports.repository").ExportRepository

    def fail_create(*_args: object, **_kwargs: object) -> None:
        raise psycopg.OperationalError("test export transaction rollback")

    monkeypatch.setattr(repository_type, "create_pending", fail_create)
    response = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(before, confirm_incomplete=False),
        headers=_headers(client),
    )

    assert response.status_code == 503
    assert response.json()["code"] == "database.unavailable"
    after = client.get(f"/api/v1/plans/{plan_id}").json()
    assert after["version"] == before["version"]
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            "SELECT count(*) FROM daily_activity_plan_exports WHERE kindergarten_id=%s",
            (actor.kindergarten_id,),
        ).fetchone() == (0,)
        assert connection.execute(
            """SELECT count(*) FROM background_jobs
            WHERE kindergarten_id=%s AND job_type='word.export'""",
            (actor.kindergarten_id,),
        ).fetchone() == (0,)
        assert connection.execute(
            "SELECT count(*) FROM audit_events WHERE kindergarten_id=%s AND resource_id=%s",
            (actor.kindergarten_id, plan_id),
        ).fetchone() == (0,)


def test_new_idempotency_key_creates_an_independent_export(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    first_plan = client.get(f"/api/v1/plans/{plan_id}").json()

    first = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(first_plan, confirm_incomplete=False),
        headers=_headers(client),
    )
    second_plan = client.get(f"/api/v1/plans/{plan_id}").json()
    second = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(second_plan, confirm_incomplete=False),
        headers=_headers(client),
    )

    assert first.status_code == second.status_code == 202
    assert first.json()["export"]["id"] != second.json()["export"]["id"]
    assert first.json()["job"]["id"] != second.json()["job"]["id"]
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        rows = connection.execute(
            """SELECT storage_key FROM daily_activity_plan_exports
            WHERE kindergarten_id=%s ORDER BY created_at""",
            (actor.kindergarten_id,),
        ).fetchall()
    assert len(rows) == 2
    assert rows[0][0] != rows[1][0]


def test_cross_tenant_plan_is_hidden_before_export_creation(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    app = cast(FastAPI, client.app)
    other_tenant = uuid4()
    app.dependency_overrides[current_session] = lambda: SimpleNamespace(
        user=SimpleNamespace(
            id=actor.user_id,
            kindergarten_id=other_tenant,
            username="other-admin",
            display_name="其他园管理员",
            status="active",
            is_active=True,
        ),
        role_codes=["admin"],
        token_family_id=actor.session_id,
        session_id=actor.session_id,
        last_reauthenticated_at=None,
    )

    response = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(plan, confirm_incomplete=False),
        headers=_headers(client),
    )

    assert response.status_code == 404
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            "SELECT count(*) FROM daily_activity_plan_exports",
        ).fetchone() == (0,)


def test_dispatch_failure_after_commit_keeps_original_202_pending_dispatch(
    admin_client: tuple[TestClient, ActorFixture],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    try:
        service_module = import_module("packages.backend.exports.service")
    except ModuleNotFoundError:
        service_module = SimpleNamespace()

    def fail_dispatch(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("Redis unavailable after commit")

    monkeypatch.setattr(service_module, "dispatch_after_commit", fail_dispatch, raising=False)
    response = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(plan, confirm_incomplete=False),
        headers=_headers(client),
    )

    assert response.status_code == 202
    assert response.json()["job"]["status"] == "pending_dispatch"


def test_download_reauthorizes_live_class_relationship_and_missing_file_is_410(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client, actor = admin_client
    _runtime(monkeypatch, tmp_path)
    class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()
    accepted = client.post(
        f"/api/v1/plans/{plan_id}/exports",
        json=_request_body(plan, confirm_incomplete=False),
        headers=_headers(client),
    )
    assert accepted.status_code == 202
    export_id = accepted.json()["export"]["id"]
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """UPDATE daily_activity_plan_exports
            SET status='succeeded',file_size=123,file_sha256=%s,exported_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            ("2" * 64, actor.kindergarten_id, export_id),
        )

    missing = client.get(f"/api/v1/exports/{export_id}/download")
    assert missing.status_code == 410
    assert missing.json()["code"] == "export.file_missing"
    assert "路径" not in missing.text

    detached = client.put(
        f"/api/v1/settings/classes/{class_id}/teachers",
        json={"teachers": []},
        headers=csrf_headers(client),
    )
    assert detached.status_code == 200
    teacher_session = SimpleNamespace(
        user=SimpleNamespace(
            id=actor.user_id,
            kindergarten_id=actor.kindergarten_id,
            username="admin",
            display_name="测试管理员",
            status="active",
            is_active=True,
        ),
        role_codes=["teacher"],
        token_family_id=actor.session_id,
        session_id=actor.session_id,
        last_reauthenticated_at=None,
    )
    app = cast(FastAPI, client.app)
    app.dependency_overrides[current_session] = lambda: teacher_session

    forbidden = client.get(f"/api/v1/exports/{export_id}/download")

    assert forbidden.status_code == 403
    assert "路径" not in forbidden.text
