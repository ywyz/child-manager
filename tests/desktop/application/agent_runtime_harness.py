"""Agent Runtime 的测试专用装配 seam；不属于冻结的 Runtime 公共接口。"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import ModuleType
from typing import Any

from pytestqt.qtbot import QtBot

from kindergarten_manager.ui.runtime import RuntimeBridge
from tests.desktop.helpers import pending_symbol


@dataclass(slots=True)
class AgentRuntimeHarness:
    runtime: Any
    bridge: RuntimeBridge
    emitted: list[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.bridge.succeeded.connect(self.emitted.append)
        self.bridge.failed.connect(self.emitted.append)

    def start_and_wait(
        self,
        qtbot: QtBot,
        intent: str,
        context_request: object,
    ) -> tuple[Any, tuple[Any, ...]]:
        with qtbot.waitSignal(self.bridge.finished, timeout=2_000) as finished:
            accepted = self.runtime.start_turn(intent, context_request)

        assert finished.args == [accepted.operation_id]
        return accepted, tuple(self.emitted)


def build_agent_runtime_harness(
    module: ModuleType,
    *,
    provider: object,
    registry: object,
    context_loader: object,
    monotonic_seconds: object,
    max_tool_calls: int,
    max_response_chars: int,
    max_turn_seconds: float,
) -> AgentRuntimeHarness:
    """集中隔离实现装配细节，行为测试只使用冻结方法和 Qt 信号。"""

    runtime_type = pending_symbol(module, "AgentRuntime", red_label="SLICE2B_RED")
    bridge = RuntimeBridge(max_workers=1)
    runtime = runtime_type(
        provider=provider,
        registry=registry,
        context_loader=context_loader,
        runtime_bridge=bridge,
        monotonic_seconds=monotonic_seconds,
        max_tool_calls=max_tool_calls,
        max_response_chars=max_response_chars,
        max_turn_seconds=max_turn_seconds,
    )
    return AgentRuntimeHarness(runtime=runtime, bridge=bridge)
