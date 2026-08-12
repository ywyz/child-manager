from __future__ import annotations

import tomllib
from pathlib import Path


def _dependency_name(requirement: str) -> str:
    return requirement.partition("[")[0].partition("=")[0].partition("<")[0].partition(">")[0]


def test_default_quality_gate_is_desktop_only_and_service_free() -> None:
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert project["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests/desktop"]
    assert (
        "--confcutdir=tests/desktop" in project["tool"]["pytest"]["ini_options"]["addopts"].split()
    )
    assert project["tool"]["pyright"]["include"] == [
        "src/kindergarten_manager",
        "tests/desktop",
    ]

    retired_runtime_dependencies = {
        "argon2-cffi",
        "dramatiq",
        "fastapi",
        "nicegui",
        "psycopg",
        "pydantic-settings",
        "pyjwt",
        "qrcode",
        "structlog",
        "uvicorn",
        "webauthn",
    }
    retired_test_dependencies = {
        "httpx2",
        "openapi-spec-validator",
        "playwright",
        "pytest-asyncio",
        "respx",
    }
    assert retired_runtime_dependencies.isdisjoint(
        {_dependency_name(item) for item in project["project"]["dependencies"]}
    )
    assert retired_test_dependencies.isdisjoint(
        {_dependency_name(item) for item in project["dependency-groups"]["dev"]}
    )

    workflow = Path(".github/workflows/quality.yml").read_text(encoding="utf-8")
    assert "uv run pytest" in workflow
    for retired_entry in (
        "CHILD_MANAGER_TEST_DATABASE_URL",
        "CHILD_MANAGER_TEST_REDIS_URL",
        "postgres:",
        "redis:",
        "playwright install",
        "openapi-spec-validator",
    ):
        assert retired_entry not in workflow
