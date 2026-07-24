# Data Model: 密码与 TOTP 备用登录

## 1. 设计原则

- `users` 继续只表示账号身份，不增加 `password_hash`、TOTP 种子或恢复秘密字段。
- 每个账号最多一套当前备用认证材料；密码与 TOTP 必须一起启用、一起撤销。
- 所有持久表带 `kindergarten_id`，Repository 查询、写入和唯一约束均显式园所隔离。
- TOTP 原始种子只在绑定开始响应中出现一次；数据库只保存 AES-256-GCM 密文。
- 会话明确记录认证方式和最近重新验证时间，普通业务授权与高风险身份授权分离。

## 2. 枚举

### `authentication_method`

- `webauthn`
- `password_totp`
- `restricted_enrollment`：管理员首次绑定备用因素前的受限会话，不可访问业务资源

### `backup_auth_status`

- `enabled`：密码与 TOTP 均已验证并可共同登录
- `revoked`：教师关闭或恢复流程撤销

待确认状态只存在于 `backup_auth_enrollments`，不得在当前凭据表中建立第二个 pending
事实来源。

### `reauthentication_purpose`

- `add_passkey`：唯一允许的备用重新验证用途

## 3. 表

### 3.1 `backup_auth_credentials`

一个账号最多一行当前备用认证材料。

| 字段 | 类型 | 约束/说明 |
|---|---|---|
| `id` | UUID | 主键 |
| `kindergarten_id` | UUID | 非空，园所隔离 |
| `user_id` | UUID | 非空，外键 `users.id` |
| `status` | VARCHAR(16) | `enabled/revoked` |
| `password_hash` | TEXT | Argon2id PHC 字符串；仅 `enabled` 时非空 |
| `password_changed_at` | TIMESTAMPTZ | 密码最近生效时间 |
| `totp_ciphertext` | BYTEA | AES-256-GCM 密文；仅 `enabled` 时非空 |
| `totp_nonce` | BYTEA | 12 字节随机 nonce |
| `totp_key_id` | VARCHAR(64) | 数据库外主密钥标识 |
| `totp_envelope_version` | SMALLINT | AAD/信封格式版本 |
| `totp_algorithm` | VARCHAR(16) | 固定 `SHA1` |
| `totp_digits` | SMALLINT | 固定 `6` |
| `totp_period_seconds` | SMALLINT | 固定 `30` |
| `last_accepted_counter` | BIGINT | 可空；原子重放保护 |
| `enabled_at` | TIMESTAMPTZ | 首次完整启用时间 |
| `revoked_at` | TIMESTAMPTZ | 当前材料撤销时间 |
| `created_at` | TIMESTAMPTZ | 非空 |
| `updated_at` | TIMESTAMPTZ | 非空 |

约束：

- `UNIQUE (kindergarten_id, user_id)`。
- 复合外键 `(kindergarten_id, user_id)` 指向同园所用户。
- `status = 'enabled'` 时密码、TOTP 信封和 `enabled_at` 全部非空且 `revoked_at` 为空。
- `status = 'revoked'` 时 `revoked_at` 非空；密码摘要与 TOTP 信封必须清除。
- `totp_nonce` 长度固定 12；digits/period/algorithm 使用检查约束固定。
- Repository 更新 `last_accepted_counter` 时执行
  `UPDATE ... WHERE last_accepted_counter IS NULL OR last_accepted_counter < :counter`，
  只有更新一行才表示 TOTP 可接受。

### 3.2 `backup_auth_enrollments`

保存尚未确认的短时绑定，不创建半启用凭据。

| 字段 | 类型 | 约束/说明 |
|---|---|---|
| `id` | UUID | 主键，也是公开 opaque enrollment ID |
| `kindergarten_id` | UUID | 非空 |
| `user_id` | UUID | 非空 |
| `session_token_id` | UUID | 非空，绑定发起时的当前 `refresh_tokens.id` |
| `totp_ciphertext` | BYTEA | 待确认种子密文 |
| `totp_nonce` | BYTEA | 12 字节 |
| `totp_key_id` | VARCHAR(64) | 主密钥标识 |
| `totp_envelope_version` | SMALLINT | 信封版本 |
| `expires_at` | TIMESTAMPTZ | 发起后 10 分钟 |
| `consumed_at` | TIMESTAMPTZ | 成功后非空 |
| `invalidated_at` | TIMESTAMPTZ | 被新绑定或会话变化作废时非空 |
| `invalidation_reason` | VARCHAR(32) | 可空，`superseded/session_changed` |
| `created_at` | TIMESTAMPTZ | 非空 |
| `updated_at` | TIMESTAMPTZ | 非空 |

约束与清理：

- `consumed_at` 与 `invalidated_at` 互斥；原因与 `invalidated_at` 必须同时为空或同时非空。
- 部分唯一约束
  `(kindergarten_id, user_id) WHERE consumed_at IS NULL AND invalidated_at IS NULL`
  保证只有一个未终结绑定；新绑定先原子作废旧行再插入，不在索引谓词中使用 `now()`。
- 验证请求必须同时匹配用户、当前未撤销且未被替换的 refresh token、未过期、未消费且未作废。
- refresh token 轮换、撤销或过期会令绑定失效；用户须重新开始绑定，避免 enrollment
  跨会话或跨 token family 漂移。
- enrollment 信封的 AAD 绑定园所、用户、enrollment ID 和版本；验证成功后使用新 nonce
  重新加密，凭据信封的 AAD 改绑园所、用户、credential ID 和版本。
- 密码只在验证请求中出现，不持久化到 enrollment。
- 成功事务中同时写入/替换 `backup_auth_credentials`、消费 enrollment、撤销旧备用会话和证明。

### 3.3 `refresh_tokens` 扩展

| 新字段 | 类型 | 说明 |
|---|---|---|
| `authentication_method` | VARCHAR(24) | 会话建立方式 |
| `webauthn_verified_at` | TIMESTAMPTZ | 最近 WebAuthn 认证/重新验证 |
| `backup_verified_at` | TIMESTAMPTZ | 备用登录建立时间 |
| `backup_reauthenticated_at` | TIMESTAMPTZ | 最近密码+TOTP 再验证 |
| `backup_auth_version` | INTEGER | 备用会话创建时的备用因素版本 |

规则：

- WebAuthn 会话写 `authentication_method = 'webauthn'` 和 `webauthn_verified_at`。
- 备用会话写 `authentication_method = 'password_totp'` 和 `backup_verified_at`。
- 管理员首次登录而未绑定时写 `restricted_enrollment`，只允许本人备用绑定、注销和健康检查。
- 新增通行密钥检查当前会话为 `password_totp` 且
  `backup_reauthenticated_at >= now() - 5 minutes`，或沿用现有 WebAuthn 重新验证规则。
- `password_totp` 与 `restricted_enrollment` 会话必须匹配用户当前 `backup_auth_version`；
  WebAuthn 会话不因备用因素版本变化而失效。
- 密码/TOTP 变化、关闭与恢复增加 `backup_auth_version` 并撤销备用会话和专用证明。
- 管理员首次绑定成功后，将当前 `restricted_enrollment` 原子转换或重新签发为普通
  WebAuthn 会话；不得把它转换为 `password_totp` 会话。

### 3.4 `users` 扩展

| 新字段 | 类型 | 说明 |
|---|---|---|
| `backup_auth_version` | INTEGER | 非空，默认 1；只撤销旧备用认证状态 |

不增加备用因素明细。API 的“是否启用”通过同园所关联 `backup_auth_credentials` 投影。

## 4. 状态转换

```text
无配置
  └─ WebAuthn 重新验证/管理员受限会话 ─> enrollment pending
       ├─ 过期/新绑定 ─> 作废
       └─ 密码合格 + 首个 TOTP 成功 ─> enabled

enabled
  ├─ WebAuthn 重新验证 + 新绑定成功 ─> enabled（旧材料、备用会话和证明失效）
  ├─ 教师 + WebAuthn 重新验证 ─> revoked
  └─ 紧急恢复完成 ─> revoked（全部认证材料和会话失效）

revoked
  └─ WebAuthn 重新验证/管理员受限会话 ─> enrollment pending
```

## 5. 登录与升级事务

### 5.1 备用登录

1. 规范化账号标识，在同园所候选范围读取用户和备用材料；未知账号走等价虚拟摘要验证。
2. 在同一服务调用中验证 Argon2id 和候选 TOTP，不暴露中间结果。
3. TOTP 正确时原子推进 `last_accepted_counter`；推进失败视为通用认证失败。
4. 校验账号状态与 `backup_auth_version`，创建 `password_totp` 会话。
5. 写最小化审计与通知事件，提交后返回 Cookie；任一步失败均不建立会话。

### 5.2 备用重新验证

1. 必须已有 `password_totp` 会话且备用因素版本仍有效。
2. 再次同时验证密码与未重放 TOTP。
3. 只更新当前会话的 `backup_reauthenticated_at`，不创建通用 bearer token。
4. WebAuthn 注册 verify 成功后清除该时间；失败或过期不改变凭据。

### 5.3 因素轮换与恢复

- WebAuthn 重新验证后才能开始 enrollment。
- 新因素生效与旧因素撤销必须在同一事务中完成。
- 紧急恢复批准并绑定新通行密钥后，清除密码/TOTP 密文和摘要、增加备用因素版本、撤销全部
  会话、邀请、旧通行密钥与旧恢复码；管理员进入新的受限 enrollment 会话。

## 6. Alembic

- 文件：`0005_password_totp_backup_login.py`
- `revision = "0005_password_totp_backup_login"`
- `down_revision = "0004_settings"`
- upgrade：创建两张备用认证表，扩展 `users` 和 `refresh_tokens`，回填既有 refresh token
  的认证方式为
  `webauthn`（无法安全证明时撤销而不是猜测）。
- downgrade：先删除 enrollment/credential 表，再删除新增会话与用户字段；不得恢复 M2
  已移除的旧密码列或旧密码登录端点。
- 测试必须从 `0004_settings` 升级到 `0005`，并验证降级回 `0004_settings`。

## 7. 本人安全事件投影

不新增通知表。`GET /auth/security-events` 从现有 `audit_events` 按服务端会话中的
`kindergarten_id` 与当前用户过滤，只返回最近 20 条备用认证相关事件：稳定事件代码、
`occurred_at`、认证方式和脱敏设备提示。不得返回 actor/subject 的其他身份信息、IP 原文、
密码、摘要、TOTP、种子、二维码或完整请求；没有“已读”写入，也不依赖邮件/短信服务。
