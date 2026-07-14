"""零外网 AI 客户端替身。"""

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(slots=True)
class FakeAiClient:
    responses: list[Mapping[str, object]] = field(default_factory=list)
    calls: list[Mapping[str, object]] = field(default_factory=list)

    async def generate(self, payload: Mapping[str, object]) -> Mapping[str, object]:
        self.calls.append(payload)
        if not self.responses:
            return {}
        return self.responses.pop(0)
