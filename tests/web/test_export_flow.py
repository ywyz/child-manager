"""T132 Word 导出保存、确认、轮询、历史与下载 RED 冒烟。"""

import asyncio
import json
from copy import deepcopy
from datetime import UTC, datetime
from importlib import import_module
from pathlib import Path
from uuid import uuid4

import pytest
from nicegui import ui
from nicegui.client import Client
from nicegui.element import Element
from nicegui.testing.user import User
from nicegui.testing.user_interaction import UserInteraction
from nicegui.testing.user_simulation import user_simulation

from tests.web.test_plan_ai_smoke import PLAN_ID, _plan

FIXTURE = Path("tests/fixtures/word/daily_activity_plan_v1.json")
EXPORT_ID_1 = "00000000-0000-0000-0000-000000000201"
EXPORT_ID_2 = "00000000-0000-0000-0000-000000000202"
JOB_ID_1 = "00000000-0000-0000-0000-000000000211"
JOB_ID_2 = "00000000-0000-0000-0000-000000000212"
DISPLAY_FILENAME = "一日活动计划_向日葵班_2026-03-02.docx"


def _complete_plan() -> dict[str, object]:
    plan = _plan()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    plan["content"] = deepcopy(fixture["content_snapshot"])
    return plan


def _job(job_id: str, *, plan_version: int = 2) -> dict[str, object]:
    return {
        "id": job_id,
        "job_type": "word.export",
        "status": "pending_dispatch",
        "plan_id": PLAN_ID,
        "requested_resource_version": plan_version,
        "attempt_count": 0,
        "max_attempts": 3,
        "trace_id": str(uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "poll_after_ms": 1000,
    }


def _export(
    export_id: str,
    job_id: str,
    *,
    status: str,
    created_at: str,
    plan_version: int = 2,
) -> dict[str, object]:
    succeeded = status == "succeeded"
    return {
        "id": export_id,
        "plan_id": PLAN_ID,
        "plan_version": plan_version,
        "content_schema_version": 1,
        "content_sha256": "1" * 64,
        "job_id": job_id,
        "status": status,
        "display_filename": DISPLAY_FILENAME,
        "file_size": 2048 if succeeded else None,
        "file_sha256": "2" * 64 if succeeded else None,
        "template_sha256": "3" * 64,
        "exported_at": created_at if succeeded else None,
        "file_missing_at": None,
        "error_code": None,
        "error_summary": None,
        "created_at": created_at,
    }


def _page(items: list[dict[str, object]]) -> dict[str, object]:
    return {"items": items, "page": 1, "page_size": 20, "total": len(items)}


def _trigger_enter(user: User, button: Element, label: str) -> None:
    UserInteraction(user, {button}, label).trigger(
        "keydown.enter",
        {"key": "Enter"},
    )


@pytest.mark.asyncio
async def test_empty_reflection_exports_current_editor_content_polls_and_keeps_two_histories(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = _complete_plan()
    plan["content"]["daily_reflection"] = {  # type: ignore[index]
        "highlights": "",
        "issues": "",
        "adjustments": "",
    }
    histories: list[dict[str, object]] = []
    calls: list[tuple[str, str, dict[str, object] | None, dict[str, str] | None]] = []

    async def fake_request(
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
        request_headers: dict[str, str] | None = None,
        **_kwargs: object,
    ) -> dict[str, object]:
        calls.append((path, method, payload, request_headers))
        if path.endswith("/jobs"):
            return {"ok": True, "status": 200, "body": _page([])}
        if "/exports?" in path:
            return {"ok": True, "status": 200, "body": _page(histories)}
        if method == "POST" and path.endswith("/exports"):
            assert payload is not None
            current_version = int(str(plan["version"]))
            assert payload["expected_version"] == current_version
            assert payload["content"] == plan["content"]
            assert payload["confirm_incomplete"] is False
            assert request_headers is not None and request_headers.get("Idempotency-Key")
            plan["version"] = current_version + 1
            index = len(histories)
            export_id = (EXPORT_ID_1, EXPORT_ID_2)[index]
            job_id = (JOB_ID_1, JOB_ID_2)[index]
            accepted = _export(
                export_id,
                job_id,
                status="pending",
                created_at=f"2026-03-02T0{index + 8}:00:00Z",
                plan_version=int(plan["version"]),
            )
            histories.insert(0, accepted)
            return {
                "ok": True,
                "status": 202,
                "body": {
                    "job": _job(job_id, plan_version=int(plan["version"])),
                    "export": accepted,
                },
            }
        if any(path.endswith(f"/exports/{export_id}") for export_id in (EXPORT_ID_1, EXPORT_ID_2)):
            # NiceGUI background tasks have no implicit slot; production polling needs
            # an explicit container context before browser-side API requests can run.
            assert ui.context.client is not None
            export_id = path.rsplit("/", 1)[-1]
            record = next(item for item in histories if item["id"] == export_id)
            record.update(
                status="succeeded",
                file_size=2048,
                file_sha256="2" * 64,
                exported_at="2026-03-02T08:00:01Z",
            )
            return {"ok": True, "status": 200, "body": record}
        return {"ok": True, "status": 200, "body": dict(plan)}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)
    monkeypatch.setattr(pages, "EXPORT_POLL_INTERVAL_SECONDS", 0.01, raising=False)

    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        await user.should_see("导出历史")
        export_button = next(
            button for button in user.find(ui.button).elements if "导出 Word" in str(button.text)
        )
        _trigger_enter(user, export_button, "导出 Word")
        await user.should_see("导出成功")
        _trigger_enter(user, export_button, "导出 Word")
        await user.should_see("共 2 次导出")

        export_posts = [
            call for call in calls if call[0] == f"/{PLAN_ID}/exports" and call[1] == "POST"
        ]
        assert len(export_posts) == 2
        assert export_posts[0][3] != export_posts[1][3]
        assert not any(path.endswith("/autosave") for path, *_rest in calls)
        assert (
            sum(str(label.text) == DISPLAY_FILENAME for label in user.find(ui.label).elements) == 2
        )
        download_buttons = [
            button for button in user.find(ui.button).elements if "下载" in str(button.text)
        ]
        assert len(download_buttons) == 2
        assert export_button.props.get("aria-label") == "导出 Word"
        assert "min-h-[44px]" in export_button.classes


@pytest.mark.asyncio
async def test_reload_resumes_pending_export_poll(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = _complete_plan()
    pending = _export(
        EXPORT_ID_1,
        JOB_ID_1,
        status="pending",
        created_at="2026-03-02T08:00:00Z",
    )
    detail_calls = 0

    async def fake_request(path: str, **_kwargs: object) -> dict[str, object]:
        nonlocal detail_calls
        if path.endswith("/jobs"):
            return {"ok": True, "status": 200, "body": _page([])}
        if "/exports?" in path:
            return {"ok": True, "status": 200, "body": _page([pending])}
        if path.endswith(f"/exports/{EXPORT_ID_1}"):
            detail_calls += 1
            return {
                "ok": True,
                "status": 200,
                "body": _export(
                    EXPORT_ID_1,
                    JOB_ID_1,
                    status="succeeded",
                    created_at="2026-03-02T08:00:00Z",
                ),
            }
        return {"ok": True, "status": 200, "body": dict(plan)}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)
    monkeypatch.setattr(pages, "EXPORT_POLL_INTERVAL_SECONDS", 0.01, raising=False)

    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        await user.should_see("导出成功")

    assert detail_calls >= 1


@pytest.mark.asyncio
async def test_leaving_editor_stops_pending_export_poll(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = _complete_plan()
    pending = _export(
        EXPORT_ID_1,
        JOB_ID_1,
        status="pending",
        created_at="2026-03-02T08:00:00Z",
    )
    detail_calls = 0
    disconnect_handlers: list[object] = []

    def capture_disconnect(_client: Client, handler: object) -> None:
        disconnect_handlers.append(handler)

    async def fake_request(path: str, **_kwargs: object) -> dict[str, object]:
        nonlocal detail_calls
        if path.endswith("/jobs"):
            return {"ok": True, "status": 200, "body": _page([])}
        if "/exports?" in path:
            return {"ok": True, "status": 200, "body": _page([pending])}
        if path.endswith(f"/exports/{EXPORT_ID_1}"):
            detail_calls += 1
            return {"ok": True, "status": 200, "body": pending}
        return {"ok": True, "status": 200, "body": dict(plan)}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)
    monkeypatch.setattr(pages, "EXPORT_POLL_INTERVAL_SECONDS", 0.01, raising=False)
    monkeypatch.setattr(Client, "on_disconnect", capture_disconnect)

    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        while detail_calls == 0:
            await asyncio.sleep(0.01)
        assert disconnect_handlers
        disconnect_handler = disconnect_handlers[0]
        assert callable(disconnect_handler)
        disconnect_handler()
        calls_after_leave = detail_calls
        await asyncio.sleep(0.05)
        assert detail_calls == calls_after_leave


@pytest.mark.asyncio
async def test_download_javascript_failure_logs_only_sanitized_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    api_client = import_module("apps.web.api_client")
    logged: dict[str, object] = {}

    async def fail_javascript(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("sensitive browser detail")

    def capture_error(message: str, *, extra: dict[str, object]) -> None:
        logged.update(message=message, extra=extra)

    monkeypatch.setattr(api_client.ui, "run_javascript", fail_javascript)
    monkeypatch.setattr(api_client.logger, "error", capture_error)
    result = await api_client.export_file_download("/api/v1/exports/safe-id/download")

    assert result["ok"] is False
    assert "sensitive browser detail" not in str(logged)
    assert logged == {
        "message": "Word 导出浏览器下载失败",
        "extra": {"exception_type": "RuntimeError"},
    }


@pytest.mark.asyncio
async def test_export_history_load_failure_uses_chinese_feedback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = _complete_plan()

    async def fake_request(path: str, **_kwargs: object) -> dict[str, object]:
        if path.endswith("/jobs"):
            return {"ok": True, "status": 200, "body": _page([])}
        if "/exports?" in path:
            return {
                "ok": False,
                "status": 503,
                "body": {"message": "导出历史暂不可用"},
            }
        return {"ok": True, "status": 200, "body": dict(plan)}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)

    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        await user.should_see("导出历史暂不可用")


@pytest.mark.asyncio
async def test_download_failure_uses_server_chinese_feedback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = _complete_plan()
    succeeded = _export(
        EXPORT_ID_1,
        JOB_ID_1,
        status="succeeded",
        created_at="2026-03-02T08:00:00Z",
    )
    download_paths: list[str] = []

    async def fake_request(path: str, **_kwargs: object) -> dict[str, object]:
        if path.endswith("/jobs"):
            return {"ok": True, "status": 200, "body": _page([])}
        if "/exports?" in path:
            return {"ok": True, "status": 200, "body": _page([succeeded])}
        return {"ok": True, "status": 200, "body": dict(plan)}

    async def fake_download(path: str) -> dict[str, object]:
        download_paths.append(path)
        return {
            "ok": False,
            "status": 410,
            "body": {"message": "历史导出文件已缺失，无法重新下载。"},
        }

    monkeypatch.setattr(pages, "plan_api_request", fake_request)
    monkeypatch.setattr(pages, "export_file_download", fake_download, raising=False)

    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        await user.should_see(DISPLAY_FILENAME)
        download_button = next(
            button for button in user.find(ui.button).elements if "下载" in str(button.text)
        )
        _trigger_enter(user, download_button, "下载 Word")
        await user.should_see("历史导出文件已缺失，无法重新下载。")

    assert download_paths == [f"/api/v1/exports/{EXPORT_ID_1}/download"]


@pytest.mark.asyncio
async def test_pending_export_poll_timeout_uses_chinese_feedback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = _complete_plan()
    pending = _export(
        EXPORT_ID_1,
        JOB_ID_1,
        status="pending",
        created_at="2026-03-02T08:00:00Z",
    )

    async def fake_request(path: str, **_kwargs: object) -> dict[str, object]:
        if path.endswith("/jobs"):
            return {"ok": True, "status": 200, "body": _page([])}
        if "/exports?" in path:
            return {"ok": True, "status": 200, "body": _page([pending])}
        if path.endswith(f"/exports/{EXPORT_ID_1}"):
            return {"ok": True, "status": 200, "body": pending}
        return {"ok": True, "status": 200, "body": dict(plan)}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)
    monkeypatch.setattr(pages, "EXPORT_POLL_INTERVAL_SECONDS", 0.01, raising=False)
    monkeypatch.setattr(pages, "EXPORT_POLL_MAX_ATTEMPTS", 1, raising=False)

    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        await user.should_see("导出状态查询超时，请稍后重试")


@pytest.mark.asyncio
async def test_only_missing_required_columns_prompt_and_confirm_with_keyboard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = _complete_plan()
    plan["content"]["morning_talk"] = {"topic": "", "questions": []}  # type: ignore[index]
    plan["content"]["daily_reflection"] = {  # type: ignore[index]
        "highlights": "",
        "issues": "",
        "adjustments": "",
    }
    confirmations: list[bool] = []

    async def fake_request(
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
        **_kwargs: object,
    ) -> dict[str, object]:
        if path.endswith("/jobs"):
            return {"ok": True, "status": 200, "body": _page([])}
        if "/exports?" in path:
            return {"ok": True, "status": 200, "body": _page([])}
        if method == "POST" and path.endswith("/exports"):
            assert payload is not None
            confirmed = bool(payload["confirm_incomplete"])
            confirmations.append(confirmed)
            if not confirmed:
                return {
                    "ok": False,
                    "status": 409,
                    "body": {
                        "code": "export.confirmation_required",
                        "message": "以下栏目内容不完整，确认后仍可导出",
                        "missing_sections": ["morning_talk"],
                    },
                }
            accepted = _export(
                EXPORT_ID_1,
                JOB_ID_1,
                status="pending",
                created_at="2026-03-02T08:00:00Z",
            )
            return {
                "ok": True,
                "status": 202,
                "body": {"job": _job(JOB_ID_1), "export": accepted},
            }
        if path.endswith(f"/exports/{EXPORT_ID_1}"):
            return {
                "ok": True,
                "status": 200,
                "body": _export(
                    EXPORT_ID_1,
                    JOB_ID_1,
                    status="succeeded",
                    created_at="2026-03-02T08:00:00Z",
                ),
            }
        return {"ok": True, "status": 200, "body": dict(plan)}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)
    monkeypatch.setattr(pages, "EXPORT_POLL_INTERVAL_SECONDS", 0.01, raising=False)

    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        export_button = next(
            button for button in user.find(ui.button).elements if "导出 Word" in str(button.text)
        )
        _trigger_enter(user, export_button, "导出 Word")
        await user.should_see("晨间谈话")
        await user.should_see("确认并导出")
        assert all("一日活动反思" not in str(label.text) for label in user.find(ui.label).elements)
        confirm_button = next(
            button for button in user.find(ui.button).elements if "确认并导出" in str(button.text)
        )
        _trigger_enter(user, confirm_button, "确认并导出")
        await user.should_see("导出成功")

        assert confirmations == [False, True]
        assert confirm_button.props.get("aria-label") == "确认并导出"
        assert "min-h-[44px]" in confirm_button.classes


@pytest.mark.asyncio
async def test_export_failure_uses_safe_chinese_feedback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = _complete_plan()

    async def fake_request(
        path: str,
        *,
        method: str = "GET",
        **_kwargs: object,
    ) -> dict[str, object]:
        if path.endswith("/jobs"):
            return {"ok": True, "status": 200, "body": _page([])}
        if "/exports?" in path:
            return {"ok": True, "status": 200, "body": _page([])}
        if method == "POST" and path.endswith("/exports"):
            return {
                "ok": False,
                "status": 503,
                "body": {"code": "configuration.unavailable", "message": "导出服务暂不可用"},
            }
        return {"ok": True, "status": 200, "body": dict(plan)}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)

    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        export_button = next(
            button for button in user.find(ui.button).elements if "导出 Word" in str(button.text)
        )
        _trigger_enter(user, export_button, "导出 Word")
        await user.should_see("导出服务暂不可用")
        alert = next(
            label
            for label in user.find(ui.label).elements
            if label.props.get("role") == "alert" and "导出服务暂不可用" in str(label.text)
        )
        assert "路径" not in str(alert.text)
