from pathlib import Path
from typing import Any

import yaml
from fastapi.routing import APIRoute

from apps.api.routers.auth import router as auth_router
from packages.contracts import identity as identity_contracts

OPENAPI = yaml.safe_load(
    Path("specs/002-password-totp-backup-login/contracts/openapi.yaml").read_text(encoding="utf-8")
)

BACKUP_PATH_METHODS = {
    ("/api/v1/auth/backup", "get"),
    ("/api/v1/auth/backup", "delete"),
    ("/api/v1/auth/backup/enrollment", "post"),
    ("/api/v1/auth/backup/enrollment/{enrollment_id}/verify", "post"),
    ("/api/v1/auth/backup/authentication", "post"),
    ("/api/v1/auth/backup/reauthentication", "post"),
    ("/api/v1/auth/security-events", "get"),
}


def _resolve(value: dict[str, Any]) -> dict[str, Any]:
    reference = value.get("$ref")
    if reference is None:
        return value
    current: Any = OPENAPI
    for part in str(reference).removeprefix("#/").split("/"):
        current = current[part]
    assert isinstance(current, dict)
    return current


def _runtime_routes() -> set[tuple[str, str]]:
    return {
        (route.path, method.lower())
        for route in auth_router.routes
        if isinstance(route, APIRoute) and route.methods is not None
        for method in route.methods
    }


def test_backup_contract_exposes_only_the_frozen_dual_factor_paths() -> None:
    operations = {
        (path, method)
        for path, path_item in OPENAPI["paths"].items()
        for method in path_item
        if method in {"get", "post", "put", "patch", "delete"}
    }

    assert operations == BACKUP_PATH_METHODS
    assert not any("sms" in path or "email" in path for path, _method in operations)
    assert not any(path.endswith("/password") or path.endswith("/totp") for path, _ in operations)


def test_backup_contract_marks_request_and_one_time_response_secrets() -> None:
    schemas = OPENAPI["components"]["schemas"]

    for schema_name in (
        "BackupEnrollmentVerifyRequest",
        "BackupAuthenticationRequest",
        "BackupReauthenticationRequest",
    ):
        schema = schemas[schema_name]
        password = schema["properties"]["password"]
        totp = _resolve(schema["properties"]["totp_code"])
        assert password["writeOnly"] is True
        assert totp["writeOnly"] is True

    enrollment = schemas["BackupEnrollment"]["properties"]
    for name in ("totp_secret", "otpauth_uri"):
        assert enrollment[name]["readOnly"] is True
        assert enrollment[name]["x-sensitive"] is True


def test_backup_authentication_failures_share_one_public_contract() -> None:
    generic_reference = "#/components/responses/GenericAuthenticationFailure"

    assert (
        OPENAPI["paths"]["/api/v1/auth/backup/authentication"]["post"]["responses"]["401"]["$ref"]
        == generic_reference
    )
    assert (
        OPENAPI["paths"]["/api/v1/auth/backup/reauthentication"]["post"]["responses"]["401"]["$ref"]
        == generic_reference
    )
    description = OPENAPI["components"]["responses"]["GenericAuthenticationFailure"]["description"]
    assert "未知账号" in description
    assert "任一因素错误" in description


def test_runtime_router_matches_the_frozen_backup_contract() -> None:
    assert _runtime_routes() >= BACKUP_PATH_METHODS


def test_runtime_identity_contract_models_match_the_frozen_names() -> None:
    required_models = {
        "BackupAuthenticationStatus",
        "BackupEnrollment",
        "BackupEnrollmentVerifyRequest",
        "BackupAuthenticationRequest",
        "BackupReauthenticationRequest",
        "SecurityEvent",
        "SecurityEventList",
    }

    assert required_models <= set(dir(identity_contracts))
