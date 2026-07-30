"""集体活动两阶段生成的冻结输入与采用规则。"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any
from uuid import uuid7

from pydantic import ValidationError

from packages.contracts.lesson_plans import (
    AiGroupActivity,
    GroupActivity,
    GroupActivityAddStepResult,
    GroupActivityStep,
    validate_group_add_step_result,
)

_SPLIT_FIELDS = (
    "theme",
    "objectives",
    "preparation",
    "focus",
    "difficulty",
    "process",
)


class GroupActivityJobService:
    """保持拆分与新增环节相互独立，且只接受已确认、已保存的输入。"""

    @staticmethod
    def _preview(task_code: str, input_context: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "id": str(uuid7()),
            "task_code": task_code,
            "status": "pending",
            "input_context": deepcopy(dict(input_context)),
        }

    @staticmethod
    def _complete_group_activity(value: Mapping[str, Any]) -> dict[str, Any]:
        completed = deepcopy(dict(value))
        for field in ("focus", "difficulty"):
            if not str(completed.get(field, "")).strip():
                completed[field] = "待教师补充"
        try:
            parsed = AiGroupActivity.model_validate(completed)
        except ValidationError as exc:
            raise ValueError("集体活动拆分结果必须完整且不含 is_ai_added") from exc
        return parsed.model_dump(mode="json")

    @staticmethod
    def require_complete_saved_group_activity(value: Mapping[str, Any]) -> dict[str, Any]:
        """新增环节只基于教师已采用并保存的完整当前集体活动。"""

        try:
            activity = GroupActivity.model_validate(value)
        except ValidationError as exc:
            raise ValueError("集体活动必须已采用并保存") from exc
        dumped = activity.model_dump(mode="json")
        if any(not dumped[field] for field in _SPLIT_FIELDS):
            raise ValueError("集体活动必须已采用并保存")
        if any(not step.heading or not step.lines for step in activity.process):
            raise ValueError("集体活动必须已采用并保存")
        return dumped

    def create_split_preview(self, source: Mapping[str, Any]) -> dict[str, Any]:
        source_id = str(source.get("id", ""))
        confirmed_at = source.get("confirmed_at")
        source_text = str(source.get("extracted_text", ""))
        if not source_id or not confirmed_at or not source_text.strip():
            raise ValueError("必须先确认集体活动来源")
        return self._preview(
            "group_activity_split",
            {"source_id": source_id, "source_text": source_text},
        )

    def complete_split_result(
        self,
        preview: Mapping[str, Any],
        *,
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        if preview.get("task_code") != "group_activity_split":
            raise ValueError("拆分预览无效")
        return self._complete_group_activity(result)

    def adopt_and_save_split(
        self,
        preview: Mapping[str, Any],
        *,
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        split = self.complete_split_result(preview, result=result)
        return {
            "adopted_and_saved": True,
            "saved_split_preview_id": preview["id"],
            "group_activity": {
                **split,
                "process": [{**step, "is_ai_added": False} for step in split["process"]],
            },
        }

    def freeze_add_step_input(self, adopted: Mapping[str, Any]) -> dict[str, Any]:
        if adopted.get("adopted_and_saved") is not True or not adopted.get(
            "saved_split_preview_id"
        ):
            raise ValueError("必须先采用并保存集体活动拆分结果")
        activity = adopted.get("group_activity")
        if not isinstance(activity, Mapping):
            raise ValueError("必须先采用并保存集体活动拆分结果")
        return {"group_activity": self.require_complete_saved_group_activity(activity)}

    def create_add_step_preview(self, frozen: Mapping[str, Any]) -> dict[str, Any]:
        activity = frozen.get("group_activity")
        if not isinstance(activity, Mapping):
            raise ValueError("新增环节冻结输入无效")
        return self._preview(
            "group_activity_add_step",
            {"group_activity": self.require_complete_saved_group_activity(activity)},
        )

    def adopt_add_step(
        self,
        adopted: Mapping[str, Any],
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        frozen = self.freeze_add_step_input(adopted)
        try:
            candidate = GroupActivityAddStepResult.model_validate(result)
            validate_group_add_step_result(
                candidate,
                process_length=len(frozen["group_activity"]["process"]),
            )
        except (ValidationError, ValueError) as exc:
            raise ValueError("新增环节结果无效") from exc
        updated = deepcopy(dict(adopted))
        process = updated["group_activity"]["process"]
        process.insert(
            candidate.suggested_insert_index,
            GroupActivityStep(
                heading=candidate.step.heading,
                lines=list(candidate.step.lines),
                is_ai_added=True,
            ).model_dump(mode="json"),
        )
        return updated

    def record_add_step_failure(
        self,
        preview: Mapping[str, Any],
        *,
        error_code: str,
    ) -> dict[str, Any]:
        if preview.get("task_code") != "group_activity_add_step":
            raise ValueError("新增环节预览无效")
        return {
            "id": preview["id"],
            "task_code": "group_activity_add_step",
            "status": "failed",
            "input_context": deepcopy(preview["input_context"]),
            "error_code": error_code,
        }

    def retry_failed_add_step(self, failed: Mapping[str, Any]) -> dict[str, Any]:
        if failed.get("task_code") != "group_activity_add_step" or failed.get("status") != "failed":
            raise ValueError("只能重试失败的新增环节任务")
        input_context = failed.get("input_context")
        if not isinstance(input_context, Mapping):
            raise ValueError("新增环节冻结输入无效")
        return self.create_add_step_preview(input_context)
