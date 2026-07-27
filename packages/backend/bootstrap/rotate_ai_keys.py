"""AI Key 轮换维护命令入口。"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from uuid import UUID

from packages.backend.integrations.crypto.ai_keys import FileAiKeyProvider
from packages.backend.settings.ai_key_rotation import (
    PostgresAiKeyRotationStore,
    rotate_ai_key_batch,
)


def run_rotation(
    *,
    target_key_id: str,
    batch_size: int,
    after_profile_id: UUID | None,
    dry_run: bool,
) -> int:
    keyring_value = os.environ.get("CHILD_MANAGER_AI_KEYRING")
    if not keyring_value:
        print("未配置仓库外的外部 AI 主密钥 keyring。")
        return 2
    database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
    if not database_url:
        print("未配置当前档位数据库。")
        return 2
    try:
        raw_keyring = json.loads(keyring_value)
        keyring = {str(key_id): Path(str(path)) for key_id, path in raw_keyring.items()}
        provider = FileAiKeyProvider(
            keyring,
            active_key_id=target_key_id,
            repository_root=Path(__file__).resolve().parents[3],
        )
        report = rotate_ai_key_batch(
            PostgresAiKeyRotationStore(database_url),
            key_provider=provider,
            target_key_id=target_key_id,
            batch_size=batch_size,
            after_profile_id=after_profile_id,
            dry_run=dry_run,
        )
    except (AttributeError, LookupError, OSError, TypeError, ValueError) as exc:
        print(f"AI Key 轮换配置或文件不可用：{type(exc).__name__}。")
        return 2
    cursor = str(report.next_cursor) if report.next_cursor is not None else "无"
    print(
        f"扫描 {report.scanned}，重加密 {report.reencrypted}，"
        f"验证 {report.verified}，失败 {report.failed}；"
        f"下一游标 {cursor}；完成 {str(report.complete).lower()}；"
        f"dry-run {str(report.dry_run).lower()}。"
    )
    if report.failed or report.verified != report.reencrypted + (
        report.scanned - report.reencrypted - report.failed
    ):
        return 1
    return 0


def configure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target-key-id", required=True)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--after-profile-id", type=UUID)
    parser.add_argument("--dry-run", action="store_true")
