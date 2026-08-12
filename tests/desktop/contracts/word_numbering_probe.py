from __future__ import annotations

import sys
from datetime import date
from hashlib import sha256
from pathlib import Path

from kindergarten_manager.application.exports import DailyPlanExportSnapshot
from kindergarten_manager.domain.content import PlanContentV1
from kindergarten_manager.infrastructure.exports.teacherplan_renderer import TeacherplanRenderer

TEMPLATE_SHA256 = "72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043"


def _snapshot(content: PlanContentV1) -> DailyPlanExportSnapshot:
    return DailyPlanExportSnapshot(
        plan_id=7,
        content_revision=3,
        plan_date=date(2026, 3, 2),
        teaching_week_text="第（四）周",
        activity_date_text="周（一）3月2日",
        semester_name="2026 春季学期",
        semester_start_date=date(2026, 2, 4),
        semester_end_date=date(2026, 6, 30),
        kindergarten_name="星河幼儿园",
        class_name="向日葵班",
        age_group="middle",
        author_name="测试教师",
        content=content,
        content_sha256=sha256(content.canonical_json().encode()).hexdigest(),
    )


def main(output_path: Path) -> None:
    payload = PlanContentV1.empty().model_dump()
    payload["morning_talk"] = {
        "topic": "春天的发现",
        "questions": ["1、你看到了什么？", "2. 你听到了什么？"],
    }
    payload["group_activity"] = {
        "theme": "寻找春天",
        "objectives": ["1．观察季节变化。", "2、尝试完整表达。"],
        "preparation": ["1.春景图片。", "2、记录纸。"],
        "focus": "表达观察结果。",
        "difficulty": "连续描述变化。",
        "process": [
            {
                "heading": "一、观察图片",
                "lines": ["1.师：请看看图片里有什么。", "2、幼：我看到了花。"],
                "is_ai_added": False,
            }
        ],
    }
    payload["indoor_area_game"] = {
        "areas": ["建构区", "阅读区"],
        "focus_guidance": "建构区",
        "objectives": ["1.尝试合作搭建。", "2、发展空间想象。"],
        "guidance_points": ["1．先商量再搭建。", "2.按标记取放材料。"],
        "support_strategies": ["1、提供结构图片。", "2.补充连接材料。"],
    }
    renderer = TeacherplanRenderer(
        Path("templates/teacherplan/teacherplan.docx"),
        expected_sha256=TEMPLATE_SHA256,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(renderer.render_day(_snapshot(PlanContentV1.model_validate(payload))))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: word_numbering_probe.py OUTPUT.docx")
    main(Path(sys.argv[1]))
