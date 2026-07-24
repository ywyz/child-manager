"""通行密钥登录、登记、恢复和个人安全页面。"""

import asyncio
import json

from nicegui import ui

from apps.web.api_client import same_origin_api_request


def login_page_text() -> tuple[str, ...]:
    return ("使用通行密钥登录", "邀请登记", "账号恢复")


def _javascript_helpers() -> str:
    return r"""
    const toBuffer = value => {
      const padded = value.replace(/-/g, '+').replace(/_/g, '/')
        + '='.repeat((4 - value.length % 4) % 4);
      return Uint8Array.from(atob(padded), c => c.charCodeAt(0)).buffer;
    };
    const toBase64url = value => {
      const bytes = new Uint8Array(value);
      let binary = '';
      bytes.forEach(byte => binary += String.fromCharCode(byte));
      return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    };
    const csrf = async () => {
      const response = await fetch('/api/v1/auth/csrf', {credentials: 'same-origin'});
      return (await response.json()).csrf_token;
    };
    const api = async (path, method, payload) => {
      const token = await csrf();
      const options = {
        method, credentials: 'same-origin',
        headers: {'X-CSRF-Token': token},
      };
      if (payload !== undefined) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(payload);
      }
      const response = await fetch(path, options);
      const body = response.status === 204 ? {} : await response.json();
      return {ok: response.ok, status: response.status, body};
    };
    """


async def api_request(
    path: str, *, method: str = "GET", payload: dict[str, object] | None = None
) -> dict[str, object]:
    return await same_origin_api_request(path, method=method, payload=payload)


async def post_same_origin(path: str, payload: dict[str, object]) -> dict[str, object]:
    return await api_request(path, method="POST", payload=payload)


async def perform_registration(
    *,
    options_path: str,
    options_payload: dict[str, object] | None,
    verify_path: str,
    label: str | None = None,
) -> dict[str, object]:
    serialized_options = (
        json.dumps(options_payload, ensure_ascii=False)
        if options_payload is not None
        else "undefined"
    )
    script = f"""
    return await (async () => {{
      {_javascript_helpers()}
      const optionsResult = await api(
        {json.dumps(options_path)}, 'POST',
        {serialized_options}
      );
      if (!optionsResult.ok) return optionsResult;
      const ceremony = optionsResult.body;
      const publicKey = ceremony.publicKey;
      publicKey.challenge = toBuffer(publicKey.challenge);
      publicKey.user.id = toBuffer(publicKey.user.id);
      publicKey.excludeCredentials = (publicKey.excludeCredentials || []).map(item => ({{
        ...item, id: toBuffer(item.id),
      }}));
      const created = await navigator.credentials.create({{publicKey}});
      const response = created.response;
      const credential = {{
        id: created.id,
        rawId: toBase64url(created.rawId),
        type: created.type,
        authenticatorAttachment: created.authenticatorAttachment,
        response: {{
          clientDataJSON: toBase64url(response.clientDataJSON),
          attestationObject: toBase64url(response.attestationObject),
          transports: response.getTransports ? response.getTransports() : [],
        }},
        clientExtensionResults: created.getClientExtensionResults(),
      }};
      return await api({json.dumps(verify_path)}, 'POST', {{
        ceremony_id: ceremony.ceremony_id,
        credential,
        label: {json.dumps(label, ensure_ascii=False)},
      }});
    }})();
    """
    result = await ui.run_javascript(script, timeout=30.0)
    return result if isinstance(result, dict) else {"ok": False, "body": {}}


async def perform_authentication(*, options_path: str, verify_path: str) -> dict[str, object]:
    script = f"""
    return await (async () => {{
      {_javascript_helpers()}
      const optionsResult = await api({json.dumps(options_path)}, 'POST', undefined);
      if (!optionsResult.ok) return optionsResult;
      const ceremony = optionsResult.body;
      const publicKey = ceremony.publicKey;
      publicKey.challenge = toBuffer(publicKey.challenge);
      publicKey.allowCredentials = (publicKey.allowCredentials || []).map(item => ({{
        ...item, id: toBuffer(item.id),
      }}));
      const assertion = await navigator.credentials.get({{publicKey}});
      const response = assertion.response;
      const credential = {{
        id: assertion.id,
        rawId: toBase64url(assertion.rawId),
        type: assertion.type,
        authenticatorAttachment: assertion.authenticatorAttachment,
        response: {{
          clientDataJSON: toBase64url(response.clientDataJSON),
          authenticatorData: toBase64url(response.authenticatorData),
          signature: toBase64url(response.signature),
          userHandle: response.userHandle ? toBase64url(response.userHandle) : null,
        }},
        clientExtensionResults: assertion.getClientExtensionResults(),
      }};
      return await api({json.dumps(verify_path)}, 'POST', {{
        ceremony_id: ceremony.ceremony_id, credential,
      }});
    }})();
    """
    result = await ui.run_javascript(script, timeout=30.0)
    return result if isinstance(result, dict) else {"ok": False, "body": {}}


def _message(result: dict[str, object], fallback: str) -> str:
    body = result.get("body")
    if isinstance(body, dict) and body.get("message"):
        return str(body["message"])
    return fallback


def register_auth_pages() -> None:
    @ui.page("/initialize")
    def initialize_page() -> None:
        ui.label("首位管理员初始化").classes("text-h5")
        secret = ui.input("初始化凭据")
        status = ui.label("")

        async def register() -> None:
            result = await perform_registration(
                options_path="/api/v1/auth/bootstrap/registration/options",
                options_payload={"bootstrap_token": secret.value or ""},
                verify_path="/api/v1/auth/bootstrap/registration/verify",
                label="首位管理员通行密钥",
            )
            status.set_text(
                "等待双人核验" if result.get("ok") else _message(result, "初始化登记失败")
            )

        ui.button("登记首位管理员通行密钥", on_click=register)

    @ui.page("/login")
    def login_page() -> None:
        title = ui.label("登录").classes("text-h5")
        status = ui.label("")
        recovery_container = ui.column()

        async def login() -> None:
            result = await perform_authentication(
                options_path="/api/v1/auth/authentication/options",
                verify_path="/api/v1/auth/authentication/verify",
            )
            if result.get("ok"):
                title.set_text("首页")
                body = result.get("body", {})
                code = body.get("recovery_code") if isinstance(body, dict) else None
                with recovery_container:
                    ui.label(str(code or "")).props('data-testid="recovery-code-once"')
                status.set_text("登录成功")
            else:
                status.set_text(_message(result, "通行密钥登录失败"))

        ui.button("使用通行密钥登录", on_click=login)
        ui.link("邀请登记", "/register")
        ui.link("账号恢复", "/recover")

    @ui.page("/register")
    def invitation_registration_page() -> None:
        ui.label("邀请登记").classes("text-h5")
        secret = ui.input("邀请凭据")
        status = ui.label("")

        async def register() -> None:
            result = await perform_registration(
                options_path="/api/v1/auth/invitation/registration/options",
                options_payload={"invitation_token": secret.value or ""},
                verify_path="/api/v1/auth/invitation/registration/verify",
                label="主通行密钥",
            )
            status.set_text(
                "等待管理员核验" if result.get("ok") else _message(result, "邀请登记失败")
            )

        ui.button("登记通行密钥", on_click=register)

    @ui.page("/recover")
    def recovery_page() -> None:
        ui.label("账号恢复").classes("text-h5")
        login = ui.input("用户名或手机号")
        recovery_code = ui.input("离线恢复码")
        status = ui.label("")

        async def submit() -> None:
            result = await post_same_origin(
                "/api/v1/auth/recovery/requests",
                {"login": login.value or "", "recovery_code": recovery_code.value or ""},
            )
            status.set_text("继续核验" if result.get("ok") else _message(result, "提交失败"))

        ui.button("提交恢复申请", on_click=submit)

    @ui.page("/recover/register")
    def recovery_registration_page() -> None:
        ui.label("恢复登记").classes("text-h5")
        enrollment = ui.input("恢复登记凭据")
        status = ui.label("")
        recovery_container = ui.column()

        async def register() -> None:
            result = await perform_registration(
                options_path="/api/v1/auth/recovery/registration/options",
                options_payload={"enrollment_token": enrollment.value or ""},
                verify_path="/api/v1/auth/recovery/registration/verify",
                label="恢复后的主通行密钥",
            )
            if result.get("ok"):
                body = result.get("body", {})
                code = body.get("recovery_code") if isinstance(body, dict) else None
                with recovery_container:
                    ui.label(str(code or "")).props('data-testid="recovery-code-once"')
                status.set_text("恢复登记完成")
            else:
                status.set_text(_message(result, "恢复登记失败"))

        ui.button("登记新通行密钥", on_click=register)

    @ui.page("/account/security")
    def security_page() -> None:
        ui.label("通行密钥与会话").classes("text-h5")
        status = ui.label("")
        label_input = ui.input("通行密钥名称")
        credential_ids: list[str] = []
        new_credential_id: list[str] = []
        current_session_id: list[str] = []
        operation_lock = asyncio.Lock()

        async def load() -> None:
            credential_result = await api_request("/api/v1/auth/credentials")
            session_result = await api_request("/api/v1/auth/sessions")
            if not credential_result.get("ok") or not session_result.get("ok"):
                status.set_text("登录状态已失效")
                return
            credential_body = credential_result.get("body", {})
            session_body = session_result.get("body", {})
            credential_ids[:] = (
                [
                    str(item["id"])
                    for item in credential_body.get("items", [])
                    if isinstance(item, dict)
                ]
                if isinstance(credential_body, dict)
                else []
            )
            current_session_id[:] = (
                [
                    str(item["id"])
                    for item in session_body.get("items", [])
                    if isinstance(item, dict) and item.get("is_current")
                ]
                if isinstance(session_body, dict)
                else []
            )

        async def step_up() -> None:
            async with operation_lock:
                result = await perform_authentication(
                    options_path="/api/v1/auth/step-up/options",
                    verify_path="/api/v1/auth/step-up/verify",
                )
                status.set_text(
                    "重新验证成功" if result.get("ok") else _message(result, "验证失败")
                )

        async def add_credential() -> None:
            async with operation_lock:
                result = await perform_registration(
                    options_path="/api/v1/auth/credentials/registration/options",
                    options_payload=None,
                    verify_path="/api/v1/auth/credentials/registration/verify",
                    label="备用通行密钥",
                )
                if result.get("ok"):
                    body = result.get("body", {})
                    if isinstance(body, dict) and body.get("id"):
                        new_credential_id[:] = [str(body["id"])]
                    status.set_text("通行密钥已新增")
                else:
                    status.set_text(_message(result, "新增失败"))

        async def save_name() -> None:
            async with operation_lock:
                if not new_credential_id:
                    status.set_text("请先新增通行密钥")
                    return
                result = await api_request(
                    f"/api/v1/auth/credentials/{new_credential_id[0]}",
                    method="PATCH",
                    payload={"label": label_input.value or "备用通行密钥"},
                )
                status.set_text("名称已保存" if result.get("ok") else _message(result, "保存失败"))

        async def revoke_primary() -> None:
            async with operation_lock:
                current = await api_request("/api/v1/auth/credentials")
                current_body = current.get("body", {})
                items = current_body.get("items", []) if isinstance(current_body, dict) else []
                if len(items) < 2:
                    status.set_text("撤销失败：必须先保留备用通行密钥")
                    return
                if not isinstance(items[0], dict):
                    return
                primary_id = str(items[0]["id"])
                result = await api_request(
                    f"/api/v1/auth/credentials/{primary_id}", method="DELETE"
                )
                status.set_text("凭据已撤销" if result.get("ok") else _message(result, "撤销失败"))

        async def revoke_current_session() -> None:
            if not current_session_id:
                await load()
            if current_session_id:
                await api_request(f"/api/v1/auth/sessions/{current_session_id[0]}", method="DELETE")
            ui.navigate.to("/login")

        ui.button("重新验证", on_click=step_up)
        ui.button("新增通行密钥", on_click=add_credential)
        ui.button("保存名称", on_click=save_name)
        ui.button("撤销主通行密钥", on_click=revoke_primary).props(
            'data-testid="revoke-primary-credential"'
        )
        ui.button("撤销当前会话", on_click=revoke_current_session)
        ui.timer(0.1, load, once=True)
