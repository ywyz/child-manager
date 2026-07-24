from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import cast
from uuid import UUID, uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from psycopg import sql

from apps.api.app import create_app
from apps.api.dependencies import admin_session, current_session
from packages.backend.identity.tokens import hash_refresh_token


@dataclass(frozen=True)
class ActorFixture:
    kindergarten_id: UUID
    user_id: UUID
    session_id: UUID


@pytest.fixture
def passkey_client(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    monkeypatch.setenv("CHILD_MANAGER_JWT_SIGNING_KEY", "test-jwt-signing-key-that-is-long")
    monkeypatch.setenv("CHILD_MANAGER_CSRF_SIGNING_KEY", "test-csrf-signing-key-that-is-long")
    monkeypatch.setenv("CHILD_MANAGER_COOKIE_SECURE", "false")
    monkeypatch.setenv("CHILD_MANAGER_ENV", "development")
    monkeypatch.setenv("CHILD_MANAGER_BIND_HOST", "127.0.0.1")
    monkeypatch.setenv("CHILD_MANAGER_AUTH_THROTTLE_BACKEND", "memory")
    monkeypatch.setenv("CHILD_MANAGER_AUTH_THROTTLE_FAILURE_LIMIT", "2")
    monkeypatch.setenv("CHILD_MANAGER_AUTH_THROTTLE_SUBJECT_FAILURE_LIMIT", "2")
    monkeypatch.setenv("CHILD_MANAGER_AUTH_THROTTLE_GLOBAL_FAILURE_LIMIT", "2")
    monkeypatch.setenv("CHILD_MANAGER_ALLOWED_ORIGINS", "http://testserver")
    monkeypatch.setenv("CHILD_MANAGER_WEBAUTHN_RP_ID", "testserver")
    monkeypatch.setenv("CHILD_MANAGER_WEBAUTHN_RP_NAME", "Child Manager Tests")
    command.upgrade(Config("alembic.ini"), "head")
    with TestClient(create_app()) as client:
        yield client


def csrf_headers(client: TestClient) -> dict[str, str]:
    response = client.get("/api/v1/auth/csrf")
    assert response.status_code == 200
    return {
        "Origin": "http://testserver",
        "X-CSRF-Token": response.json()["csrf_token"],
    }


@pytest.fixture
def admin_client(
    passkey_client: TestClient,
    isolated_database_url: str,
) -> Iterator[tuple[TestClient, ActorFixture]]:
    """通过 FastAPI 身份依赖注入建立已 step-up 管理员，不借用密码登录。"""

    actor = ActorFixture(kindergarten_id=uuid4(), user_id=uuid4(), session_id=uuid4())
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    now = datetime.now(UTC)
    with psycopg.connect(native_url) as connection:
        user_columns = {
            str(row[0])
            for row in connection.execute(
                """SELECT column_name FROM information_schema.columns
                WHERE table_schema=current_schema() AND table_name='users'"""
            ).fetchall()
        }
        columns = [
            "id",
            "kindergarten_id",
            "username",
            "username_normalized",
            "display_name",
        ]
        values: list[object] = [
            actor.user_id,
            actor.kindergarten_id,
            "admin",
            "admin",
            "测试管理员",
        ]
        if "webauthn_user_handle" in user_columns:
            columns.extend(["webauthn_user_handle", "status", "activated_at"])
            values.extend([b"a" * 32, "active", now])
        if "password_hash" in user_columns:
            columns.extend(["password_hash", "password_changed_at"])
            values.extend(["$argon2id$test-only", now])
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s, %s)",
            (actor.kindergarten_id, "API 测试园"),
        )
        user_insert = sql.SQL("INSERT INTO users ({}) VALUES ({})").format(
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() for _value in values),
        )
        connection.execute(user_insert, values)
        admin_role = connection.execute("SELECT id FROM roles WHERE code='admin'").fetchone()
        assert admin_role is not None
        connection.execute(
            """INSERT INTO user_roles
            (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (%s,%s,%s,%s,%s)""",
            (
                actor.kindergarten_id,
                actor.user_id,
                admin_role[0],
                actor.user_id,
                now,
            ),
        )
        refresh_columns = {
            str(row[0])
            for row in connection.execute(
                """SELECT column_name FROM information_schema.columns
                WHERE table_schema=current_schema() AND table_name='refresh_tokens'"""
            ).fetchall()
        }
        refresh_names = [
            "id",
            "kindergarten_id",
            "user_id",
            "token_family_id",
            "token_hash",
            "issued_at",
            "expires_at",
        ]
        refresh_values: list[object] = [
            uuid4(),
            actor.kindergarten_id,
            actor.user_id,
            actor.session_id,
            hash_refresh_token("admin-test-refresh"),
            now,
            now + timedelta(days=7),
        ]
        if "last_reauthenticated_at" in refresh_columns:
            refresh_names.append("last_reauthenticated_at")
            refresh_values.append(now)
        refresh_insert = sql.SQL("INSERT INTO refresh_tokens ({}) VALUES ({})").format(
            sql.SQL(", ").join(map(sql.Identifier, refresh_names)),
            sql.SQL(", ").join(sql.Placeholder() for _value in refresh_values),
        )
        connection.execute(refresh_insert, refresh_values)

    session = SimpleNamespace(
        user=SimpleNamespace(
            id=actor.user_id,
            kindergarten_id=actor.kindergarten_id,
            username="admin",
            display_name="测试管理员",
            status="active",
            is_active=True,
        ),
        role_codes=["admin"],
        token_family_id=actor.session_id,
        session_id=actor.session_id,
        last_reauthenticated_at=now,
    )
    app = cast(FastAPI, passkey_client.app)
    app.dependency_overrides[current_session] = lambda: session
    app.dependency_overrides[admin_session] = lambda: session
    try:
        yield passkey_client, actor
    finally:
        app.dependency_overrides.clear()
