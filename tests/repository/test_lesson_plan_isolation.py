# ruff: noqa: F811

from datetime import date
from importlib import import_module
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient

from tests.api.passkey_helpers import ActorFixture, admin_client, passkey_client  # noqa: F401
from tests.api.plan_helpers import provision_editable_plan_context


def test_repository_reads_and_cas_updates_are_tenant_scoped(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    repository_class = import_module(
        "packages.backend.lesson_plans.repository"
    ).LessonPlanRepository

    with psycopg.connect(native_url) as connection:
        repository = repository_class(connection)
        assert repository.get_plan(actor.kindergarten_id, plan_id) is not None
        assert repository.get_plan(uuid4(), plan_id) is None
        assert (
            repository.update_content(
                uuid4(),
                plan_id,
                expected_version=1,
                content={},
                actor_id=actor.user_id,
            )
            is None
        )
        unchanged = connection.execute(
            "SELECT plan_date, version FROM daily_activity_plans WHERE id=%s",
            (plan_id,),
        ).fetchone()
    assert unchanged == (date(2026, 3, 2), 1)
