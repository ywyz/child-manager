"""通行密钥登录、登记、恢复和个人安全页面。"""

import asyncio
import base64
import json

import qrcode
from nicegui import ui
from qrcode.image.svg import SvgPathImage

from apps.web.api_client import (
    backup_auth_api_request,
    backup_login_api_request,
    backup_reauthentication_api_request,
    same_origin_api_request,
)


def login_page_text() -> tuple[str, ...]:
    return (
        "使用通行密钥登录",
        "邀请登记",
        "账号恢复",
        "密码与 TOTP 备用登录",
        "使用密码与 TOTP 登录",
        "设置备用登录",
        "稍后设置",
        "重新验证后新增通行密钥",
        "获取五分钟专用授权",
        "为此设备新增通行密钥",
        "本人安全事件",
    )


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


def _qr_data_uri(value: str) -> str:
    image = qrcode.make(value, image_factory=SvgPathImage)
    encoded = base64.b64encode(image.to_string()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


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
        backup_prompt = ui.column()
        recovery_container = ui.column()
        backup_identifier = ui.input("用户名或手机号")
        backup_password = ui.input("备用登录密码", password=True)
        backup_totp = ui.input("动态验证码")

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
                backup = await api_request("/api/v1/auth/backup")
                backup_body = backup.get("body", {})
                enrollment_required = (
                    bool(backup_body.get("enrollment_required"))
                    if isinstance(backup_body, dict)
                    else False
                )
                enabled = (
                    bool(backup_body.get("enabled")) if isinstance(backup_body, dict) else False
                )
                if enrollment_required:
                    status.set_text("请先设置备用登录")
                    ui.navigate.to("/account/security")
                    return
                if backup.get("ok") and not enabled:
                    with backup_prompt:
                        ui.label("建议设置密码与 TOTP 备用登录")
                        ui.link("设置备用登录", "/account/security")
                        ui.button("稍后设置", on_click=lambda: backup_prompt.clear())
                status.set_text("登录成功")
            else:
                status.set_text(_message(result, "通行密钥登录失败"))

        async def backup_login() -> None:
            result = await backup_login_api_request(
                identifier=backup_identifier.value or "",
                password=backup_password.value or "",
                totp_code=backup_totp.value or "",
            )
            backup_password.value = ""
            backup_totp.value = ""
            if result.get("ok"):
                title.set_text("首页")
                status.set_text("备用登录成功，可进入业务或为此设备新增通行密钥")
                return
            status.set_text(_message(result, "账号、密码或动态验证码不正确"))

        ui.button("使用通行密钥登录", on_click=login)
        ui.button("使用密码与 TOTP 登录", on_click=backup_login)
        ui.link("为此设备新增通行密钥", "/account/security")
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
        ui.label("密码与 TOTP 备用登录").classes("text-h6")
        status = ui.label("")
        backup_status = ui.label("")
        backup_hint = ui.label("重新验证后新增通行密钥")
        security_events = ui.label("本人安全事件")
        del backup_hint, security_events
        label_input = ui.input("通行密钥名称")
        backup_password = ui.input("备用登录密码", password=True)
        backup_totp = ui.input("动态验证码")
        reauthentication_password = ui.input("重新验证密码", password=True)
        reauthentication_totp = ui.input("重新验证动态码")
        enrollment_material = ui.column()
        pending_enrollment_id: list[str] = []
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
            backup_result = await api_request("/api/v1/auth/backup")
            backup_body = backup_result.get("body", {})
            if backup_result.get("ok") and isinstance(backup_body, dict):
                if backup_body.get("enabled"):
                    backup_status.set_text("备用登录已启用")
                elif backup_body.get("required"):
                    backup_status.set_text("管理员必须完成备用登录设置")
                else:
                    backup_status.set_text("备用登录尚未启用，可稍后设置")

        async def start_backup_enrollment() -> None:
            async with operation_lock:
                result = await backup_auth_api_request("/enrollment", method="POST")
                body = result.get("body", {})
                if not result.get("ok") or not isinstance(body, dict):
                    status.set_text(_message(result, "开始设置失败"))
                    return
                enrollment_id = body.get("enrollment_id")
                secret = body.get("totp_secret")
                uri = body.get("otpauth_uri")
                if not all(isinstance(value, str) for value in (enrollment_id, secret, uri)):
                    status.set_text("绑定材料无效，请重新开始")
                    return
                pending_enrollment_id[:] = [str(enrollment_id)]
                enrollment_material.clear()
                with enrollment_material:
                    ui.label("请立即扫描二维码或复制人工输入值；离开后不会再次显示。")
                    ui.image(_qr_data_uri(str(uri))).props('alt="TOTP 认证器绑定二维码"')
                    ui.label(str(secret)).props('data-testid="totp-secret-once"')
                status.set_text("请输入密码和认证器显示的动态验证码")

        async def verify_backup_enrollment() -> None:
            async with operation_lock:
                if not pending_enrollment_id:
                    status.set_text("请先开始设置备用登录")
                    return
                result = await backup_auth_api_request(
                    f"/enrollment/{pending_enrollment_id[0]}/verify",
                    method="POST",
                    payload={
                        "password": backup_password.value or "",
                        "totp_code": backup_totp.value or "",
                    },
                )
                backup_password.value = ""
                backup_totp.value = ""
                if result.get("ok"):
                    pending_enrollment_id.clear()
                    enrollment_material.clear()
                    backup_status.set_text("备用登录已启用")
                    status.set_text("密码与 TOTP 已同时启用")
                    return
                status.set_text(_message(result, "验证失败"))

        async def step_up() -> None:
            async with operation_lock:
                result = await perform_authentication(
                    options_path="/api/v1/auth/step-up/options",
                    verify_path="/api/v1/auth/step-up/verify",
                )
                status.set_text(
                    "重新验证成功" if result.get("ok") else _message(result, "验证失败")
                )

        async def reauthenticate_backup() -> None:
            async with operation_lock:
                result = await backup_reauthentication_api_request(
                    password=reauthentication_password.value or "",
                    totp_code=reauthentication_totp.value or "",
                )
                reauthentication_password.value = ""
                reauthentication_totp.value = ""
                status.set_text(
                    "已取得五分钟新增通行密钥授权"
                    if result.get("ok")
                    else _message(result, "验证失败")
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

        ui.button("使用通行密钥重新验证", on_click=step_up)
        ui.button(
            "获取五分钟专用授权",
            on_click=reauthenticate_backup,
        )
        ui.button("设置备用登录", on_click=start_backup_enrollment)
        ui.button("确认密码与动态验证码", on_click=verify_backup_enrollment)
        ui.button("稍后设置", on_click=lambda: enrollment_material.clear())
        ui.button("新增通行密钥", on_click=add_credential)
        ui.button("保存名称", on_click=save_name)
        ui.button("撤销主通行密钥", on_click=revoke_primary).props(
            'data-testid="revoke-primary-credential"'
        )
        ui.button("撤销当前会话", on_click=revoke_current_session)
        ui.timer(0.1, load, once=True)
