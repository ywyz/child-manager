"""双实现本地开发档位的 Compose 合同。"""

import json
import os
import secrets
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.database_config import require_test_database_url

PROFILES = {
    "codex": {
        "COMPOSE_PROJECT_NAME": "child_manager_codex",
        "CHILD_MANAGER_PROFILE": "codex",
        "CHILD_MANAGER_POSTGRES_PORT": "15432",
        "CHILD_MANAGER_REDIS_PORT": "16379",
        "CHILD_MANAGER_DATABASE_NAME": "child_manager_codex",
        "CHILD_MANAGER_TEST_DATABASE_NAME": "child_manager_codex_test",
    },
    "trae": {
        "COMPOSE_PROJECT_NAME": "child_manager_trae",
        "CHILD_MANAGER_PROFILE": "trae",
        "CHILD_MANAGER_POSTGRES_PORT": "25432",
        "CHILD_MANAGER_REDIS_PORT": "26379",
        "CHILD_MANAGER_DATABASE_NAME": "child_manager_trae",
        "CHILD_MANAGER_TEST_DATABASE_NAME": "child_manager_trae_test",
    },
}
POSTGRES_IMAGE = (
    "postgres:18-alpine@sha256:9a8afca54e7861fd90fab5fdf4c42477a6b1cb7d293595148e674e0a3181de15"
)
REDIS_IMAGE = (
    "redis:8-alpine@sha256:9d317178eceac8454a2284a9e6df2466b93c745529947f0cd42a0fa9609d7005"
)


def _compose_config(profile: dict[str, str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["docker", "compose", "-f", "compose.dev.yaml", "config", "--format", "json"],
        check=True,
        capture_output=True,
        env=os.environ | {"CHILD_MANAGER_POSTGRES_PASSWORD": secrets.token_hex(32)} | profile,
        text=True,
    )
    loaded = json.loads(completed.stdout)
    assert isinstance(loaded, dict)
    return loaded


@pytest.mark.parametrize(("profile_name", "profile"), PROFILES.items())
def test_compose_uses_selected_local_profile(profile_name: str, profile: dict[str, str]) -> None:
    config = _compose_config(profile)
    services = config["services"]

    assert config["name"] == f"child_manager_{profile_name}"
    assert (
        services["postgres"]["environment"]["POSTGRES_DB"] == profile["CHILD_MANAGER_DATABASE_NAME"]
    )
    assert services["postgres"]["ports"][0]["host_ip"] == "127.0.0.1"
    assert services["postgres"]["ports"][0]["published"] == profile["CHILD_MANAGER_POSTGRES_PORT"]
    assert services["redis"]["ports"][0]["host_ip"] == "127.0.0.1"
    assert services["redis"]["ports"][0]["published"] == profile["CHILD_MANAGER_REDIS_PORT"]
    assert services["postgres"]["image"] == POSTGRES_IMAGE
    assert services["redis"]["image"] == REDIS_IMAGE


def test_compose_rejects_missing_profile_variables() -> None:
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("CHILD_MANAGER_") and key != "COMPOSE_PROJECT_NAME"
    }
    completed = subprocess.run(
        ["docker", "compose", "-f", "compose.dev.yaml", "config"],
        check=False,
        capture_output=True,
        env=environment,
        text=True,
    )

    assert completed.returncode != 0
    assert "COMPOSE_PROJECT_NAME" in completed.stderr


def test_compose_accepts_temporary_image_overrides() -> None:
    profile = PROFILES["codex"] | {
        "CHILD_MANAGER_POSTGRES_IMAGE": POSTGRES_IMAGE.replace(
            "postgres:", "mirror.example/postgres:"
        ),
        "CHILD_MANAGER_REDIS_IMAGE": REDIS_IMAGE.replace("redis:", "mirror.example/redis:"),
    }

    services = _compose_config(profile)["services"]

    assert services["postgres"]["image"] == POSTGRES_IMAGE.replace(
        "postgres:", "mirror.example/postgres:"
    )
    assert services["redis"]["image"] == REDIS_IMAGE.replace("redis:", "mirror.example/redis:")


def test_test_database_url_requires_an_explicit_profile(monkeypatch) -> None:
    monkeypatch.delenv("CHILD_MANAGER_TEST_DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="CHILD_MANAGER_TEST_DATABASE_URL"):
        require_test_database_url()


def test_quality_workflow_provides_an_isolated_postgresql_database() -> None:
    workflow = yaml.safe_load(Path(".github/workflows/quality.yml").read_text(encoding="utf-8"))
    job = workflow["jobs"]["python"]

    assert job["services"]["postgres"]["env"]["POSTGRES_DB"] == "child_manager_ci"
    assert job["env"]["CHILD_MANAGER_TEST_DATABASE_URL"].endswith(
        "@127.0.0.1:5432/child_manager_ci"
    )
