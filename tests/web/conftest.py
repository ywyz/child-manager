"""Web 测试共享 fixture。"""

from collections.abc import Iterator

import pytest
from nicegui.outbox import Message
from nicegui.testing.user import User


@pytest.fixture(autouse=True)
def patch_nicegui_simulated_emit() -> Iterator[None]:
    """修复 NiceGUI 3.14 testing user 对无 request_id JS 消息的崩溃。

    页面内部更新（如导航 set_content）可能发出不带 request_id 的 run_javascript
    消息，导致 simulated_emit 抛出 KeyError 并阻塞后续事件。此处将
    `_patch_outbox_emit_function` 替换为安全版本，无 request_id 时跳过响应回调。
    """
    original_patch = User._patch_outbox_emit_function

    def safe_patch(self: User) -> None:
        original_emit = self._client.outbox._emit

        async def safe_simulated_emit(message: Message) -> None:
            await original_emit(message)
            _, type_, data = message  # type: ignore[misc]
            if type_ == "run_javascript" and "request_id" in data:
                for rule, result in self.javascript_rules.items():
                    match = rule.match(data["code"])
                    if match:
                        self._client.handle_javascript_response(
                            {
                                "request_id": data["request_id"],
                                "result": result(match),
                            }
                        )

        self._client.outbox._emit = safe_simulated_emit

    User._patch_outbox_emit_function = safe_patch
    yield
    User._patch_outbox_emit_function = original_patch
