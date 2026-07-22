from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.routing import APIRoute

from apps.api.routers.auth import router as auth_router
from packages.contracts import identity as identity_contracts

OPENAPI = yaml.safe_load(
    Path("specs/001-daily-activity-plan/contracts/openapi.yaml").read_text(encoding="utf-8")
)

AUTH_PATHS = {
    "/api/v1/auth/csrf",
    "/api/v1/auth/bootstrap/registration/options",
    "/api/v1/auth/bootstrap/registration/verify",
    "/api/v1/auth/invitation/registration/options",
    "/api/v1/auth/invitation/registration/verify",
    "/api/v1/auth/authentication/options",
    "/api/v1/auth/authentication/verify",
    "/api/v1/auth/step-up/options",
    "/api/v1/auth/step-up/verify",
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",
    "/api/v1/auth/me",
    "/api/v1/auth/credentials",
    "/api/v1/auth/credentials/registration/options",
    "/api/v1/auth/credentials/registration/verify",
    "/api/v1/auth/credentials/{credential_id}",
    "/api/v1/auth/recovery/requests",
    "/api/v1/auth/recovery/registration/options",
    "/api/v1/auth/recovery/registration/verify",
    "/api/v1/auth/recovery-code/rotate",
    "/api/v1/auth/sessions",
    "/api/v1/auth/sessions/{session_id}",
}


def _resolve(reference_or_value: dict[str, Any]) -> dict[str, Any]:
    reference = reference_or_value.get("$ref")
    if reference is None:
        return reference_or_value
    current: Any = OPENAPI
    for part in str(reference).removeprefix("#/").split("/"):
        current = current[part]
    assert isinstance(current, dict)
    return current


def _runtime_routes() -> dict[tuple[str, str], APIRoute]:
    routes: dict[tuple[str, str], APIRoute] = {}
    for route in auth_router.routes:
        if not isinstance(route, APIRoute) or route.methods is None:
            continue
        for method in route.methods:
            routes[(route.path, method)] = route
    return routes


def test_auth_openapi_contains_complete_passkey_lifecycle_and_no_password_paths() -> None:
    paths = set(OPENAPI["paths"])

    assert paths >= AUTH_PATHS
    assert {
        "/api/v1/auth/login",
        "/api/v1/auth/change-password",
        "/api/v1/register",
    }.isdisjoint(paths)
    assert not any(path.endswith("/reset-password") for path in paths)
    assert not any("password" in name.lower() for name in OPENAPI["components"]["schemas"])


def test_registration_and_authentication_options_are_browser_ready() -> None:
    schemas = OPENAPI["components"]["schemas"]
    registration = schemas["WebAuthnRegistrationOptions"]["properties"]["publicKey"]
    authentication = schemas["WebAuthnAuthenticationOptions"]["properties"]["publicKey"]

    assert registration["required"] == [
        "challenge",
        "rp",
        "user",
        "pubKeyCredParams",
        "timeout",
        "excludeCredentials",
        "authenticatorSelection",
        "attestation",
    ]
    assert registration["properties"]["timeout"]["const"] == 300_000
    assert registration["properties"]["attestation"]["const"] == "none"
    assert registration["properties"]["authenticatorSelection"]["properties"] == {
        "residentKey": {"type": "string", "const": "required"},
        "requireResidentKey": {"type": "boolean", "const": True},
        "userVerification": {"type": "string", "const": "required"},
    }
    assert authentication["properties"]["allowCredentials"]["type"] == "array"
    assert authentication["properties"]["userVerification"]["const"] == "required"


def test_browser_credential_json_has_all_array_buffer_fields_as_base64url() -> None:
    schemas = OPENAPI["components"]["schemas"]
    registration_response = schemas["RegistrationCredential"]["properties"]["response"]
    authentication_response = schemas["AuthenticationCredential"]["properties"]["response"]

    assert registration_response["required"] == ["clientDataJSON", "attestationObject"]
    assert authentication_response["required"] == [
        "clientDataJSON",
        "authenticatorData",
        "signature",
        "userHandle",
    ]
    for schema_name in ("RegistrationCredential", "AuthenticationCredential"):
        assert schemas[schema_name]["required"] == [
            "id",
            "rawId",
            "type",
            "response",
            "clientExtensionResults",
        ]
        assert schemas[schema_name]["properties"]["rawId"] == {
            "$ref": "#/components/schemas/Base64Url"
        }


@pytest.mark.parametrize(
    ("path", "method", "status", "header_component"),
    [
        ("/api/v1/auth/authentication/verify", "post", "200", "AuthSetCookies"),
        ("/api/v1/auth/refresh", "post", "200", "AuthSetCookies"),
        ("/api/v1/auth/logout", "post", "204", "ClearAuthCookies"),
    ],
)
def test_auth_success_and_logout_lock_two_raw_cookie_headers(
    path: str, method: str, status: str, header_component: str
) -> None:
    response = _resolve(OPENAPI["paths"][path][method]["responses"][status])
    header = _resolve(response["headers"]["Set-Cookie"])

    assert header is OPENAPI["components"]["headers"][header_component]
    assert header["schema"]["type"] == "array"
    assert header["schema"]["minItems"] == 2
    assert header["schema"]["maxItems"] == 2
    assert "逗号折叠" in header["description"]


def test_identity_contract_models_match_frozen_passkey_names() -> None:
    required_models = {
        "WebAuthnRegistrationOptions",
        "WebAuthnAuthenticationOptions",
        "RegistrationCredential",
        "AuthenticationCredential",
        "RegistrationVerifyRequest",
        "AuthenticationVerifyRequest",
        "AuthenticationResult",
        "Credential",
        "Invitation",
        "RecoveryCompleted",
        "Session",
    }

    assert required_models <= set(dir(identity_contracts))
    assert {"LoginRequest", "ChangePasswordRequest", "PasswordResetRequest"}.isdisjoint(
        dir(identity_contracts)
    )


def test_runtime_auth_router_matches_frozen_passkey_paths() -> None:
    routes = _runtime_routes()
    runtime_paths = {path for path, _method in routes}

    assert runtime_paths >= AUTH_PATHS
    assert {
        "/api/v1/auth/login",
        "/api/v1/auth/change-password",
    }.isdisjoint(runtime_paths)
