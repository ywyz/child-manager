"""Word 导出的业务完整性规则。"""

import json
from hashlib import sha256
from typing import Any

from packages.backend.lesson_plans.schemas import content_completeness
from packages.contracts.exports import REQUIRED_EXPORT_SECTIONS, ExportSection
from packages.contracts.lesson_plans import PlanContentV1

TEMPLATE_CODE = "daily_activity_plan.v1"
TEMPLATE_FILENAME = "teacherplan.docx"
TEMPLATE_SHA256 = "72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043"


def canonical_export_content_sha256(value: dict[str, Any]) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return sha256(serialized).hexdigest()


def missing_export_sections(content: PlanContentV1) -> tuple[ExportSection, ...]:
    """返回需要二次确认的五栏；反思永远不参与确认。"""

    completeness = content_completeness(content)
    return tuple(section for section in REQUIRED_EXPORT_SECTIONS if not completeness[section])
