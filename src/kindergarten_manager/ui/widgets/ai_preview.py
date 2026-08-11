from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SectionPreview:
    section_code: str
    preview_id: object
    result: object
    status: str = "ready"

    @property
    def can_adopt(self) -> bool:
        return self.status == "ready"


@dataclass(frozen=True, slots=True)
class SectionFailure:
    section_code: str
    message: str
    can_retry: bool = True


class AiPreviewFlow:
    """不依赖 Qt 的预览状态机；所有正文变更必须由显式 intent 触发。"""

    def __init__(self) -> None:
        self.entry_visible = True
        self.generation_enabled = False
        self.status_text = "未配置 AI，可继续手工编辑和导出"
        self.notice_text = ""
        self.page_epoch = 0
        self._operation_id: UUID | None = None
        self._previews: dict[str, SectionPreview] = {}
        self._failures: dict[str, SectionFailure] = {}

    def configure(self, *, enabled: bool) -> None:
        self.generation_enabled = enabled
        self.status_text = "AI 已就绪" if enabled else "未配置 AI，可继续手工编辑和导出"
        self.notice_text = ""

    def mark_started(self, operation_id: UUID) -> None:
        self._operation_id = operation_id
        self.status_text = "AI 正在生成，请稍候"
        self.notice_text = ""

    def request_start(self, section_code: str) -> bool:
        del section_code
        if not self.generation_enabled:
            self.status_text = "未配置 AI，可继续手工编辑和导出"
            return False
        if self._operation_id is not None:
            self.status_text = "AI 正在生成，请稍候"
            self.notice_text = "已有 AI 任务正在运行"
            return False
        return True

    def show_preview(
        self,
        operation_id: UUID,
        section_code: str,
        preview_id: object,
        result: object,
        *,
        page_epoch: int | None = None,
    ) -> None:
        if not self._accepts_signal(operation_id, page_epoch):
            return
        self._previews[section_code] = SectionPreview(
            section_code=section_code,
            preview_id=preview_id,
            result=result,
        )
        self._failures.pop(section_code, None)
        self.status_text = "AI 预览已生成，请确认采用或拒绝"

    def show_failure(
        self,
        operation_id: UUID,
        section_code: str,
        message: str,
        *,
        page_epoch: int | None = None,
    ) -> None:
        if not self._accepts_signal(operation_id, page_epoch):
            return
        self._failures[section_code] = SectionFailure(section_code, message)
        self.status_text = "生成失败，可重试失败栏目"

    def preview_for(self, section_code: str) -> SectionPreview | None:
        return self._previews.get(section_code)

    def failure_for(self, section_code: str) -> SectionFailure | None:
        return self._failures.get(section_code)

    def request_retry(self, section_code: str) -> str | None:
        failure = self._failures.get(section_code)
        return section_code if failure is not None and failure.can_retry else None

    def request_adopt(self, preview_id: object) -> tuple[str, object] | None:
        return self._preview_intent("adopt", preview_id)

    def request_reject(self, preview_id: object) -> tuple[str, object] | None:
        return self._preview_intent("reject", preview_id)

    def mark_finished(self, operation_id: UUID) -> None:
        if self._operation_id == operation_id:
            self._operation_id = None

    def leave_page(self) -> None:
        self.page_epoch += 1
        self._operation_id = None
        self._previews.clear()
        self._failures.clear()
        self.notice_text = ""

    def _accepts_signal(self, operation_id: UUID, page_epoch: int | None) -> bool:
        signal_epoch = self.page_epoch if page_epoch is None else page_epoch
        return signal_epoch == self.page_epoch and operation_id == self._operation_id

    def _preview_intent(
        self,
        action: str,
        preview_id: object,
    ) -> tuple[str, object] | None:
        if any(
            preview.preview_id == preview_id and preview.status == "ready"
            for preview in self._previews.values()
        ):
            return action, preview_id
        return None
