# KMBACKUP1 备份包与恢复契约

## 1. 范围

本契约定义本地一致性备份包、可携带/远程加密信封和恢复事务。它不是同步协议，不支持增量、
冲突合并、自动选择最新版本或远端直接打开 SQLite。

## 2. 内部完整包

逻辑容器为 ZIP，固定条目：

```text
manifest.json
payload/application.sqlite3
```

首期没有附件或幼儿资源。ZIP 条目名必须来自白名单，恢复拒绝绝对路径、`..`、重复条目、
符号链接和超过上限的压缩比/解压大小。

`manifest.json` 使用 UTF-8 规范 JSON：

```text
format: "KMBACKUP"
format_version: 1
application_id: "cn.kindergartenmanager.desktop"
backup_id: UUID
kind: daily | manual | pre_migration | pre_restore
created_at_utc: RFC3339
application_version: semver
build_git_sha: full SHA
schema_revision: Alembic revision
sqlite_runtime_version: string
payloads:
  - path: "payload/application.sqlite3"
    length: integer
    sha256: lowercase hex
```

manifest 不包含教师、园所、班级名、正文、Endpoint、Key 或恢复口令。

### 本地安全备份

每日、迁移前和恢复前备份可以保存未加密完整包，因为其权限边界与明文本地数据库相同，且
秘密从未进入包。可携带手动备份和任何远程上传必须进入加密信封。

## 3. 一致性快照生成

1. 创建目标同目录临时 SQLite 文件。
2. 使用 `sqlite3.Connection.backup()` 从权威库复制，按页报告进度和检查取消。
3. 关闭目标连接后执行 `PRAGMA integrity_check` 与 `PRAGMA foreign_key_check`。
4. 记录 Alembic revision、关键实体计数、长度和 SHA-256。
5. 生成规范 manifest 和 ZIP 临时包，重新打开验证后原子发布。

禁止在数据库打开时直接复制主文件、`-wal` 或 `-shm`。

## 4. 加密信封

二进制布局：

```text
8 bytes   magic = "KMBACK1\0"
4 bytes   big-endian header JSON length
N bytes   canonical UTF-8 header JSON
remaining AES-256-GCM ciphertext || 16-byte tag
```

Header：

```text
envelope_version: 1
application_id: "cn.kindergartenmanager.desktop"
backup_id: UUID
schema_revision: string
kdf:
  name: "scrypt"
  salt_b64: 16 random bytes
  n: 131072
  r: 8
  p: 1
aead:
  name: "AES-256-GCM"
  nonce_b64: 12 random bytes
plaintext_length: integer
```

- 口令以 UTF-8 NFC 编码进入 scrypt，派生 32-byte key。
- AAD 是 magic、header 长度和完整 canonical header 的连接。
- 每份备份重新生成 salt 和 nonce；nonce 永不与同一派生 key 复用。
- 解密前先限制总文件/header 长度、salt/nonce 长度、plaintext 上限和 KDF 参数；不得执行攻击者
  指定的任意大成本。
- 只有 GCM tag 验证成功后才解压/解析载荷。`InvalidTag` 对外统一为“口令错误或备份已损坏”。
- 实现必须保留版本 1 黄金向量和篡改向量；未来参数变化新增可读版本，不原地重写旧文件。

## 5. 凭据存储

通过 keyring 的受支持操作系统 backend 保存：AI API Key、WebDAV secret、S3 Secret/Session
Token 和用户选择缓存的恢复口令。

- 稳定 service name 以应用 ID 开头，每类 secret 使用固定非 PII account key。
- Windows 必须是 `WinVaultKeyring` 并强制 `local-machine` persistence；Linux 必须是
  `keyring.backends.SecretService.Keyring` 并使用当前用户登录 keyring，记录为 `local-user`；
  Null、明文文件、未知或仅伪造显示名的 backend 必须 fail closed。
- 写入后立即读回等值验证；删除配置同时删除 credential。
- credential 丢失只禁用对应外部能力，本地编辑/Word/本地备份仍可用。
- 恢复口令是用户持有的跨设备秘密；凭据库只是自动备份所需缓存，不是唯一副本。

## 6. 远程对象

```text
kmb1/{UTC timestamp}-{backup UUID}.kmbak
```

对象名不得包含教师、园所、班级或正文。WebDAV/S3 接口仅允许：上传不可变对象、列举、下载、
删除。上传前必须完成本地加密；成功后核对长度/可用元数据。S3 multipart ETag 不作为 SHA-256，
最终完整性以 AEAD 和包内 hash 为准。

远程失败返回脱敏错误并允许重试，不得回滚或阻止任何本地数据库事务。

## 7. 轮换

- 每日本地日期首次成功打开数据库后创建一份 daily；成功后才更新 last backup date。
- daily 最多保留最近 30 份成功备份；失败/临时文件不计入配额并按清理策略删除。
- pre_migration 和 pre_restore 不受 daily 轮换立即删除，至少保留到对应升级/恢复已通过人工或
  自动稳定期检查。
- 删除远程备份必须由用户显式选择，不能以本地轮换自动删除远端。

## 8. 恢复事务

1. 教师显式选择一个具体本地/远程版本；应用不猜“最新”。
2. 远程对象下载到专用 staging；输入口令并验证 AEAD。
3. 安全解压，验证 manifest、应用 ID、格式、长度、SHA-256、SQLite integrity/FK。
4. 拒绝未来 Schema；旧 Schema 在 staging 副本上升级到当前 head 并再次完整验证。
5. 创建并验证当前数据库的 pre_restore 保护性备份；失败即停止。
6. 停止新任务，取消/等待后台任务，关闭全部 Session/engine 连接。
7. 确保候选库与当前库同卷，移走当前库为短期 rollback 副本，`os.replace()` 候选库；清理旧
   `-wal/-shm` 必须在确认连接已关闭后进行。
8. 重新打开，检查 revision、integrity/FK 和关键计数。失败则原子恢复 rollback 副本。
9. 成功后保留 pre_restore 备份并删除 staging/rollback 临时副本，重新进入 UI。

## 9. 稳定错误码

`backup.cancelled`、`backup.no_space`、`backup.snapshot_failed`、`backup.integrity_failed`、
`backup.credential_unavailable`、`backup.remote_unavailable`、`backup.remote_mismatch`、
`restore.bad_passphrase_or_tampered`、`restore.unsupported_format`、`restore.wrong_application`、
`restore.future_schema`、`restore.unsafe_archive`、`restore.protective_backup_failed`、
`restore.replace_failed`、`restore.rollback_failed`。

## 10. 验证矩阵

- WAL 中有提交且继续读取/写入时生成的一致快照。
- 空间不足、只读、取消、强制退出发生在 snapshot/zip/encrypt/upload/download/replace 各阶段。
- 错口令、AAD/header/密文/tag 篡改、截断、未知格式/KDF/AEAD、恶意 KDF 参数。
- ZIP 路径穿越、重复条目、压缩炸弹、payload hash/长度不符。
- Windows credential backend 缺失/拒绝/被用户删除；不得降级到 SQLite/文件/env。
- WebDAV/S3 超时、上传中断、远端长度不符；连续 100 次本地编辑仍成功。
- 新安装恢复、旧 Schema 升级恢复、未来 Schema 拒绝、替换后打开失败自动回滚。
