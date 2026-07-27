"""提示词定义、版本和冻结测试运行 Repository。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from packages.backend.prompts.catalog import PROMPT_SPECS

FROZEN_PROMPT_RUN_FIELDS = frozenset(
    {
        "input_context",
        "input_sha256",
        "prompt_content",
        "prompt_content_sha256",
        "result_schema_code",
        "result_schema_version",
        "model_call_snapshot",
        "input_summary",
        "prompt_definition_id",
        "prompt_version_id",
        "model_profile_id",
        "job_id",
    }
)


def prompt_test_input_summary(variables: dict[str, object]) -> dict[str, object]:
    return {
        "provided_variable_names": sorted(variables),
        "all_values_redacted": True,
    }


@dataclass(frozen=True, slots=True)
class PromptDefinitionRecord:
    id: UUID
    code: str
    name: str
    variable_whitelist: tuple[str, ...]
    required_capabilities: tuple[str, ...]
    result_schema_code: str
    result_schema_version: int
    model_profile_id: UUID | None
    effective_version_id: UUID | None
    draft_version_id: UUID | None
    is_active: bool


@dataclass(frozen=True, slots=True)
class PromptVersionRecord:
    id: UUID
    prompt_definition_id: UUID
    prompt_code: str
    version_number: int
    source_type: str
    lifecycle_state: str
    content: str
    content_sha256: str
    based_on_version_id: UUID | None
    created_by: UUID | None
    created_at: datetime
    published_by: UUID | None
    published_at: datetime | None


@dataclass(frozen=True, slots=True)
class PromptTestRunRecord:
    id: UUID
    job_id: UUID
    prompt_code: str
    input_summary: dict[str, object]
    status: str
    output_content: dict[str, object] | None
    elapsed_ms: int | None
    error_code: str | None
    error_summary: str | None
    created_at: datetime


def _row(result: Any) -> tuple[Any, ...] | None:
    return result.fetchone() if result is not None else None


def _definition(row: tuple[Any, ...] | None) -> PromptDefinitionRecord | None:
    if row is None:
        return None
    return PromptDefinitionRecord(
        id=UUID(str(row[0])),
        code=str(row[1]),
        name=str(row[2]),
        variable_whitelist=tuple(str(value) for value in row[3]),
        required_capabilities=tuple(str(value) for value in row[4]),
        result_schema_code=str(row[5]),
        result_schema_version=int(row[6]),
        model_profile_id=UUID(str(row[7])) if row[7] is not None else None,
        effective_version_id=UUID(str(row[8])) if row[8] is not None else None,
        draft_version_id=UUID(str(row[9])) if row[9] is not None else None,
        is_active=bool(row[10]),
    )


def _version(row: tuple[Any, ...] | None) -> PromptVersionRecord | None:
    if row is None:
        return None
    return PromptVersionRecord(
        id=UUID(str(row[0])),
        prompt_definition_id=UUID(str(row[1])),
        prompt_code=str(row[2]),
        version_number=int(row[3]),
        source_type=str(row[4]),
        lifecycle_state=str(row[5]),
        content=str(row[6]),
        content_sha256=str(row[7]),
        based_on_version_id=UUID(str(row[8])) if row[8] is not None else None,
        created_by=UUID(str(row[9])) if row[9] is not None else None,
        created_at=row[10],  # type: ignore[arg-type]
        published_by=UUID(str(row[11])) if row[11] is not None else None,
        published_at=row[12] if isinstance(row[12], datetime) else None,
    )


_DEFINITION_SELECT = """
SELECT d.id,d.code,d.name,d.variable_whitelist,d.required_capabilities,
       d.result_schema_code,d.result_schema_version,d.model_profile_id,
       COALESCE(d.active_custom_version_id,system_version.id),
       draft.id,d.is_active
FROM prompt_definitions d
LEFT JOIN LATERAL (
  SELECT id FROM prompt_versions v
  WHERE v.kindergarten_id=d.kindergarten_id AND v.prompt_definition_id=d.id
    AND v.source_type='system' AND v.lifecycle_state='published'
  ORDER BY v.version_number DESC LIMIT 1
) system_version ON true
LEFT JOIN LATERAL (
  SELECT id FROM prompt_versions v
  WHERE v.kindergarten_id=d.kindergarten_id AND v.prompt_definition_id=d.id
    AND v.source_type='custom' AND v.lifecycle_state='draft'
  LIMIT 1
) draft ON true
"""

_VERSION_SELECT = """
SELECT v.id,v.prompt_definition_id,d.code,v.version_number,v.source_type,v.lifecycle_state,
       v.content,v.content_sha256,v.based_on_version_id,v.created_by,v.created_at,
       v.published_by,v.published_at
FROM prompt_versions v JOIN prompt_definitions d
  ON d.kindergarten_id=v.kindergarten_id AND d.id=v.prompt_definition_id
"""


class PromptRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def ensure_defaults(self, kindergarten_id: UUID) -> None:
        for spec in PROMPT_SPECS.values():
            definition_id = uuid5(
                NAMESPACE_URL,
                f"child-manager:{kindergarten_id}:prompt-definition:{spec.code}",
            )
            version_id = uuid5(
                NAMESPACE_URL,
                f"child-manager:{kindergarten_id}:prompt-version:{spec.code}:system-v1",
            )
            self.connection.execute(
                """INSERT INTO prompt_definitions
                (id,kindergarten_id,code,name,variable_whitelist,required_capabilities,
                 result_schema_code,result_schema_version,is_active)
                VALUES (%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,1,true)
                ON CONFLICT (kindergarten_id,code) DO NOTHING""",
                (
                    definition_id,
                    kindergarten_id,
                    spec.code,
                    spec.name,
                    json.dumps(sorted(spec.variable_whitelist), ensure_ascii=False),
                    json.dumps(sorted(spec.required_capabilities), ensure_ascii=False),
                    spec.result_schema_code,
                ),
            )
            self.connection.execute(
                """INSERT INTO prompt_versions
                (id,kindergarten_id,prompt_definition_id,version_number,source_type,
                 lifecycle_state,content,content_sha256,published_at)
                VALUES (%s,%s,%s,1,'system','published',%s,%s,now())
                ON CONFLICT (kindergarten_id,prompt_definition_id,version_number) DO NOTHING""",
                (
                    version_id,
                    kindergarten_id,
                    definition_id,
                    spec.content,
                    spec.content_sha256,
                ),
            )

    def list_definitions(
        self,
        kindergarten_id: UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[PromptDefinitionRecord], int]:
        count = _row(
            self.connection.execute(
                "SELECT count(*) FROM prompt_definitions WHERE kindergarten_id=%s",
                (kindergarten_id,),
            )
        )
        result = self.connection.execute(
            _DEFINITION_SELECT
            + """ WHERE d.kindergarten_id=%s ORDER BY d.code LIMIT %s OFFSET %s""",
            (kindergarten_id, page_size, (page - 1) * page_size),
        )
        return (
            [record for row in result.fetchall() if (record := _definition(row)) is not None],
            int(count[0]) if count else 0,
        )

    def get_definition(
        self,
        kindergarten_id: UUID,
        code: str,
        *,
        for_update: bool = False,
    ) -> PromptDefinitionRecord | None:
        suffix = " FOR UPDATE OF d" if for_update else ""
        return _definition(
            _row(
                self.connection.execute(
                    _DEFINITION_SELECT + " WHERE d.kindergarten_id=%s AND d.code=%s" + suffix,
                    (kindergarten_id, code),
                )
            )
        )

    def get_version(
        self,
        kindergarten_id: UUID,
        code: str,
        version_id: UUID,
    ) -> PromptVersionRecord | None:
        return _version(
            _row(
                self.connection.execute(
                    _VERSION_SELECT + """ WHERE v.kindergarten_id=%s AND d.code=%s AND v.id=%s""",
                    (kindergarten_id, code, version_id),
                )
            )
        )

    def list_versions(
        self,
        kindergarten_id: UUID,
        code: str,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[PromptVersionRecord], int]:
        count = _row(
            self.connection.execute(
                """SELECT count(*) FROM prompt_versions v JOIN prompt_definitions d
                ON d.kindergarten_id=v.kindergarten_id AND d.id=v.prompt_definition_id
                WHERE v.kindergarten_id=%s AND d.code=%s""",
                (kindergarten_id, code),
            )
        )
        result = self.connection.execute(
            _VERSION_SELECT
            + """ WHERE v.kindergarten_id=%s AND d.code=%s
                ORDER BY v.version_number DESC LIMIT %s OFFSET %s""",
            (kindergarten_id, code, page_size, (page - 1) * page_size),
        )
        return (
            [record for row in result.fetchall() if (record := _version(row)) is not None],
            int(count[0]) if count else 0,
        )

    def save_draft(
        self,
        kindergarten_id: UUID,
        definition_id: UUID,
        *,
        code: str,
        content: str,
        based_on_version_id: UUID | None,
        actor_id: UUID,
    ) -> PromptVersionRecord:
        existing = _row(
            self.connection.execute(
                """SELECT id FROM prompt_versions WHERE kindergarten_id=%s
                AND prompt_definition_id=%s AND source_type='custom'
                AND lifecycle_state='draft'""",
                (kindergarten_id, definition_id),
            )
        )
        digest = sha256(content.encode()).hexdigest()
        if existing:
            version_id = UUID(str(existing[0]))
            self.connection.execute(
                """UPDATE prompt_versions SET content=%s,content_sha256=%s,
                based_on_version_id=%s,created_by=%s,updated_at=now()
                WHERE kindergarten_id=%s AND prompt_definition_id=%s AND id=%s
                AND lifecycle_state='draft'""",
                (
                    content,
                    digest,
                    based_on_version_id,
                    actor_id,
                    kindergarten_id,
                    definition_id,
                    version_id,
                ),
            )
        else:
            version_id = uuid5(
                NAMESPACE_URL,
                f"child-manager:{kindergarten_id}:prompt-draft:{definition_id}",
            )
            next_number = _row(
                self.connection.execute(
                    """SELECT COALESCE(max(version_number),0)+1 FROM prompt_versions
                    WHERE kindergarten_id=%s AND prompt_definition_id=%s""",
                    (kindergarten_id, definition_id),
                )
            )
            self.connection.execute(
                """INSERT INTO prompt_versions
                (id,kindergarten_id,prompt_definition_id,version_number,source_type,
                 lifecycle_state,content,content_sha256,based_on_version_id,created_by)
                VALUES (%s,%s,%s,%s,'custom','draft',%s,%s,%s,%s)""",
                (
                    version_id,
                    kindergarten_id,
                    definition_id,
                    int(next_number[0]) if next_number else 2,
                    content,
                    digest,
                    based_on_version_id,
                    actor_id,
                ),
            )
        record = self.get_version(kindergarten_id, code, version_id)
        assert record is not None
        return record

    def publish_draft(
        self,
        kindergarten_id: UUID,
        definition_id: UUID,
        *,
        code: str,
        actor_id: UUID,
    ) -> PromptVersionRecord | None:
        row = _row(
            self.connection.execute(
                """UPDATE prompt_versions SET lifecycle_state='published',
                published_by=%s,published_at=now(),updated_at=now()
                WHERE kindergarten_id=%s AND prompt_definition_id=%s
                  AND source_type='custom' AND lifecycle_state='draft'
                RETURNING id""",
                (actor_id, kindergarten_id, definition_id),
            )
        )
        if row is None:
            return None
        version_id = UUID(str(row[0]))
        self.connection.execute(
            """UPDATE prompt_definitions SET active_custom_version_id=%s,updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (version_id, kindergarten_id, definition_id),
        )
        return self.get_version(kindergarten_id, code, version_id)

    def restore_version(
        self,
        kindergarten_id: UUID,
        definition_id: UUID,
        source_version_id: UUID,
        *,
        code: str,
        actor_id: UUID,
    ) -> PromptVersionRecord | None:
        source = self.get_version(kindergarten_id, code, source_version_id)
        if source is None:
            return None
        next_number = _row(
            self.connection.execute(
                """SELECT max(version_number)+1 FROM prompt_versions
                WHERE kindergarten_id=%s AND prompt_definition_id=%s""",
                (kindergarten_id, definition_id),
            )
        )
        assert next_number is not None
        version_id = uuid5(
            NAMESPACE_URL,
            f"child-manager:{kindergarten_id}:prompt-restore:{definition_id}:{next_number[0]}",
        )
        self.connection.execute(
            """INSERT INTO prompt_versions
            (id,kindergarten_id,prompt_definition_id,version_number,source_type,
             lifecycle_state,content,content_sha256,based_on_version_id,created_by,
             published_by,published_at)
            VALUES (%s,%s,%s,%s,'custom','published',%s,%s,%s,%s,%s,now())""",
            (
                version_id,
                kindergarten_id,
                definition_id,
                int(next_number[0]),
                source.content,
                source.content_sha256,
                source.id,
                actor_id,
                actor_id,
            ),
        )
        self.connection.execute(
            """UPDATE prompt_definitions SET active_custom_version_id=%s,updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (version_id, kindergarten_id, definition_id),
        )
        return self.get_version(kindergarten_id, code, version_id)

    def unfinished_count(self, kindergarten_id: UUID, definition_id: UUID) -> int:
        row = _row(
            self.connection.execute(
                """SELECT count(*) FROM prompt_test_runs WHERE kindergarten_id=%s
                AND prompt_definition_id=%s AND status='pending'""",
                (kindergarten_id, definition_id),
            )
        )
        return int(row[0]) if row else 0

    def prune_finished_prompt_test_runs(
        self,
        kindergarten_id: UUID,
        definition_id: UUID,
        *,
        keep: int,
    ) -> int:
        result = self.connection.execute(
            """DELETE FROM prompt_test_runs
            WHERE kindergarten_id=%s AND prompt_definition_id=%s
              AND status IN ('succeeded','failed')
              AND id NOT IN (
                SELECT id FROM prompt_test_runs
                WHERE kindergarten_id=%s AND prompt_definition_id=%s
                  AND status IN ('succeeded','failed')
                ORDER BY created_at DESC,id DESC LIMIT %s
              )""",
            (kindergarten_id, definition_id, kindergarten_id, definition_id, max(0, keep)),
        )
        return int(getattr(result, "rowcount", 0))

    def create_prompt_test_run(
        self,
        kindergarten_id: UUID,
        *,
        run_id: UUID,
        definition_id: UUID,
        version_id: UUID,
        profile_id: UUID,
        job_id: UUID,
        input_context: dict[str, object],
        prompt_content: str,
        result_schema_code: str,
        result_schema_version: int,
        model_call_snapshot: dict[str, object],
        actor_id: UUID,
    ) -> None:
        summary = prompt_test_input_summary(input_context)
        serialized = json.dumps(
            input_context, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        )
        self.connection.execute(
            """INSERT INTO prompt_test_runs
            (id,kindergarten_id,prompt_definition_id,prompt_version_id,model_profile_id,
             job_id,input_context,input_sha256,prompt_content,prompt_content_sha256,
             result_schema_code,result_schema_version,model_call_snapshot,input_summary,
             status,created_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,
                    'pending',%s)""",
            (
                run_id,
                kindergarten_id,
                definition_id,
                version_id,
                profile_id,
                job_id,
                json.dumps(input_context, ensure_ascii=False),
                sha256(serialized.encode()).hexdigest(),
                prompt_content,
                sha256(prompt_content.encode()).hexdigest(),
                result_schema_code,
                result_schema_version,
                json.dumps(model_call_snapshot, ensure_ascii=False),
                json.dumps(summary, ensure_ascii=False),
                actor_id,
            ),
        )

    def get_prompt_test_run(
        self,
        kindergarten_id: UUID,
        code: str,
        run_id: UUID,
    ) -> PromptTestRunRecord | None:
        row = _row(
            self.connection.execute(
                """SELECT r.id,r.job_id,d.code,r.input_summary,r.status,r.output_content,
                r.elapsed_ms,r.error_code,r.error_summary,r.created_at
                FROM prompt_test_runs r JOIN prompt_definitions d
                  ON d.kindergarten_id=r.kindergarten_id AND d.id=r.prompt_definition_id
                WHERE r.kindergarten_id=%s AND d.code=%s AND r.id=%s""",
                (kindergarten_id, code, run_id),
            )
        )
        if row is None:
            return None
        return PromptTestRunRecord(
            id=UUID(str(row[0])),
            job_id=UUID(str(row[1])),
            prompt_code=str(row[2]),
            input_summary=dict(row[3]),
            status=str(row[4]),
            output_content=dict(row[5]) if row[5] is not None else None,
            elapsed_ms=int(row[6]) if row[6] is not None else None,
            error_code=str(row[7]) if row[7] is not None else None,
            error_summary=str(row[8]) if row[8] is not None else None,
            created_at=row[9],  # type: ignore[arg-type]
        )

    def get_prompt_test_run_by_job(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
    ) -> PromptTestRunRecord | None:
        row = _row(
            self.connection.execute(
                """SELECT r.id,r.job_id,d.code,r.input_summary,r.status,r.output_content,
                r.elapsed_ms,r.error_code,r.error_summary,r.created_at
                FROM prompt_test_runs r JOIN prompt_definitions d
                  ON d.kindergarten_id=r.kindergarten_id AND d.id=r.prompt_definition_id
                WHERE r.kindergarten_id=%s AND r.job_id=%s""",
                (kindergarten_id, job_id),
            )
        )
        if row is None:
            return None
        return PromptTestRunRecord(
            id=UUID(str(row[0])),
            job_id=UUID(str(row[1])),
            prompt_code=str(row[2]),
            input_summary=dict(row[3]),
            status=str(row[4]),
            output_content=dict(row[5]) if row[5] is not None else None,
            elapsed_ms=int(row[6]) if row[6] is not None else None,
            error_code=str(row[7]) if row[7] is not None else None,
            error_summary=str(row[8]) if row[8] is not None else None,
            created_at=row[9],  # type: ignore[arg-type]
        )

    def list_prompt_test_runs(
        self,
        kindergarten_id: UUID,
        definition_id: UUID,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[PromptTestRunRecord], int]:
        count = _row(
            self.connection.execute(
                """SELECT count(*) FROM prompt_test_runs WHERE kindergarten_id=%s
                AND prompt_definition_id=%s""",
                (kindergarten_id, definition_id),
            )
        )
        result = self.connection.execute(
            """SELECT r.id,r.job_id,d.code,r.input_summary,r.status,r.output_content,
            r.elapsed_ms,r.error_code,r.error_summary,r.created_at
            FROM prompt_test_runs r JOIN prompt_definitions d
              ON d.kindergarten_id=r.kindergarten_id AND d.id=r.prompt_definition_id
            WHERE r.kindergarten_id=%s AND r.prompt_definition_id=%s
            ORDER BY r.created_at DESC,r.id DESC LIMIT %s OFFSET %s""",
            (kindergarten_id, definition_id, page_size, (page - 1) * page_size),
        )
        records = [
            PromptTestRunRecord(
                id=UUID(str(row[0])),
                job_id=UUID(str(row[1])),
                prompt_code=str(row[2]),
                input_summary=dict(row[3]),
                status=str(row[4]),
                output_content=dict(row[5]) if row[5] is not None else None,
                elapsed_ms=int(row[6]) if row[6] is not None else None,
                error_code=str(row[7]) if row[7] is not None else None,
                error_summary=str(row[8]) if row[8] is not None else None,
                created_at=row[9],  # type: ignore[arg-type]
            )
            for row in result.fetchall()
        ]
        return records, int(count[0]) if count else 0

    def clear_finished_prompt_test_runs(
        self,
        kindergarten_id: UUID,
        definition_id: UUID,
    ) -> int:
        result = self.connection.execute(
            """DELETE FROM prompt_test_runs WHERE kindergarten_id=%s
            AND prompt_definition_id=%s AND status IN ('succeeded','failed')""",
            (kindergarten_id, definition_id),
        )
        return int(getattr(result, "rowcount", 0))

    def update_prompt_test_run(
        self,
        kindergarten_id: UUID,
        run_id: UUID,
        *,
        changes: dict[str, object],
    ) -> None:
        if FROZEN_PROMPT_RUN_FIELDS.intersection(changes):
            raise ValueError("提示词测试冻结字段不可修改")
        if not changes:
            return
        allowed = {"status", "output_content", "elapsed_ms", "error_code", "error_summary"}
        if not set(changes) <= allowed:
            raise ValueError("提示词测试更新字段无效")
        assignments = ",".join(f"{name}=%s" for name in changes)
        self.connection.execute(
            f"""UPDATE prompt_test_runs SET {assignments},updated_at=now()
            WHERE kindergarten_id=%s AND id=%s""",
            (*changes.values(), kindergarten_id, run_id),
        )
