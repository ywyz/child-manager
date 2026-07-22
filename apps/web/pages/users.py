"""管理员账号、邀请、凭据和恢复核验页面。"""

from nicegui import ui

from apps.web.pages.auth import api_request, post_same_origin


def users_page_text() -> tuple[str, ...]:
    return (
        "账号管理",
        "签发邀请",
        "通行密钥",
        "新增通行密钥",
        "命名通行密钥",
        "撤销通行密钥",
        "重新邀请",
        "撤销会话",
        "恢复申请",
    )


def register_users_page() -> None:
    @ui.page("/users")
    def users_page() -> None:
        ui.label("账号管理").classes("text-h5")
        username = ui.input("用户名")
        display_name = ui.input("姓名")
        status = ui.label("")
        one_time_values = ui.column()
        actions = ui.column()
        rendered: set[str] = set()

        def render_user(user_id: str) -> None:
            if user_id in rendered:
                return
            rendered.add(user_id)
            with actions:

                async def issue(target: str = user_id) -> None:
                    result = await post_same_origin(
                        f"/api/v1/users/{target}/invitations", {"expires_in_hours": 24}
                    )
                    body = result.get("body", {})
                    token = body.get("invitation_token") if isinstance(body, dict) else None
                    with one_time_values:
                        ui.label(str(token or "")).props('data-testid="invitation-token-once"')
                    status.set_text("邀请已签发" if result.get("ok") else "签发邀请失败")

                async def activate(target: str = user_id) -> None:
                    result = await post_same_origin(
                        f"/api/v1/users/{target}/activate",
                        {"verification_confirmed": True, "verification_note": "已带外核验"},
                    )
                    status.set_text("账号已激活" if result.get("ok") else "激活失败")

                ui.button("签发邀请", on_click=issue).props(
                    f'data-testid="issue-invitation-{user_id}"'
                )
                ui.button("激活账号", on_click=activate).props(
                    f'data-testid="activate-user-{user_id}"'
                )

        async def create() -> None:
            result = await post_same_origin(
                "/api/v1/users",
                {
                    "username": username.value or "",
                    "display_name": display_name.value or "",
                    "role_codes": ["teacher"],
                },
            )
            body = result.get("body", {})
            if result.get("ok") and isinstance(body, dict) and body.get("id"):
                user_id = str(body["id"])
                with one_time_values:
                    ui.label(user_id).props('data-testid="created-user-id"')
                render_user(user_id)
                status.set_text("账号已创建")
            else:
                status.set_text("创建账号失败")

        async def load() -> None:
            result = await api_request("/api/v1/users?page=1&page_size=100")
            body = result.get("body", {})
            if result.get("ok") and isinstance(body, dict):
                for item in body.get("items", []):
                    if isinstance(item, dict) and item.get("id"):
                        render_user(str(item["id"]))

        ui.button("创建账号", on_click=create)
        ui.timer(0.1, load, once=True)

    @ui.page("/users/{user_id}/security")
    def user_security_page(user_id: str) -> None:
        ui.label("通行密钥与会话").classes("text-h5")
        status = ui.label("")
        one_time_values = ui.column()
        credential_id: list[str] = []

        async def load() -> None:
            result = await api_request(f"/api/v1/users/{user_id}/credentials")
            body = result.get("body", {})
            if result.get("ok") and isinstance(body, dict):
                credential_id[:] = [
                    str(item["id"])
                    for item in body.get("items", [])
                    if isinstance(item, dict) and item.get("id")
                ]

        async def revoke_last() -> None:
            if not credential_id:
                await load()
            if not credential_id:
                status.set_text("没有可撤销的通行密钥")
                return
            result = await api_request(
                f"/api/v1/users/{user_id}/credentials/{credential_id[-1]}", method="DELETE"
            )
            body = result.get("body", {})
            reinvitation = body.get("reinvitation") if isinstance(body, dict) else None
            token = reinvitation.get("invitation_token") if isinstance(reinvitation, dict) else None
            with one_time_values:
                ui.label(str(token or "")).props('data-testid="invitation-token-once"')
            status.set_text("已撤销并重新邀请" if result.get("ok") else "撤销失败")

        ui.button("撤销教师最后凭据并重新邀请", on_click=revoke_last)
        ui.timer(0.1, load, once=True)

    @ui.page("/users/{user_id}/recovery")
    def user_recovery_page(user_id: str) -> None:
        ui.label("恢复申请").classes("text-h5")
        status = ui.label("")
        one_time_values = ui.column()
        request_id: list[str] = []

        async def load() -> None:
            result = await api_request(f"/api/v1/users/{user_id}/recovery-requests")
            body = result.get("body", {})
            if result.get("ok") and isinstance(body, dict):
                pending = [
                    item
                    for item in body.get("items", [])
                    if isinstance(item, dict) and item.get("status") == "pending_verification"
                ]
                if pending:
                    request_id[:] = [str(pending[-1]["id"])]

        async def approve() -> None:
            if not request_id:
                await load()
            if not request_id:
                status.set_text("没有待批准的恢复申请")
                return
            result = await post_same_origin(
                f"/api/v1/users/{user_id}/recovery-requests/{request_id[0]}/approve",
                {"verification_confirmed": True, "verification_note": "已带外核验"},
            )
            body = result.get("body", {})
            token = body.get("enrollment_token") if isinstance(body, dict) else None
            with one_time_values:
                ui.label(str(token or "")).props('data-testid="recovery-enrollment-token-once"')
            status.set_text("恢复登记已批准" if result.get("ok") else "批准失败")

        ui.button("批准恢复登记", on_click=approve)
        ui.timer(0.1, load, once=True)
