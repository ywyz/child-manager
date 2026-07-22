# Child Manager PostgreSQL 数据库 Schema

文档版本：v1.1

状态：已确认，待 Alembic 实现

日期：2026-07-22

适用范围：Cloud 首期单园功能数据库

## 1. 文档目的

本文将 [`data-model.md`](data-model.md) 的领域模型落为 PostgreSQL 物理 Schema，冻结首期的表、列类型、空值、主键、外键、组合园所隔离、检查约束、部分索引、JSONB 版本和 Alembic 实现顺序。

本文是 SQLAlchemy 模型、Alembic 迁移、Repository 和 PostgreSQL 集成测试的物理契约。它不替代：

- [`lesson-management.md`](../PRD/lesson-management.md) 定义的用户行为与验收标准。
- [`data-model.md`](data-model.md) 定义的领域语义、生命周期与数据保留。
- [`system-architecture.md`](system-architecture.md) 定义的服务、事务、队列、文件和安全缝隙。

本文描述目标 Schema，不表示当前 `main` 已存在数据库或迁移链。真正实现后，Alembic 迁移必须与本文同步，不得以 `create_all()` 替代。

## 2. 事实来源与旧仓库取舍

### 2.1 事实来源

- [`AGENTS.md`](../../AGENTS.md)：园所隔离、迁移、安全和验证硬性规则。
- [`CONTEXT.md`](../../CONTEXT.md)：当前阶段、实施顺序与部署延后边界。
- [`data-model.md`](data-model.md)：首期实体、关系、字段职责、不变量与保留策略。
- [`system-architecture.md`](system-architecture.md)：应用用例拥有事务、PostgreSQL 是权威状态、跨系统操作采用补偿。
- [`lesson-management.md`](../PRD/lesson-management.md)：账号、设置、教案、AI、导出与审计的业务规则。

### 2.2 旧仓库经验

本次复查的旧仓库 `ywyz/kindergartenManager` 版本为提交 `225fe139d5541539f2be4d0d41ef00061989533d`。旧迁移和模型验证了 Repository 集中查询、明确租户过滤、Alembic 修改 Schema 以及 AI Key 密文存储的价值，但下列物理设计不继承：

- `BIGINT` 自增主键与本地 SQLite 变体。
- MySQL Enum 和 SQLite/MySQL 双生产语义。
- 将班级区域保存为逗号字符串。
- 以 `(tenant_id, user_id, plan_date)` 查询后 upsert 的教案唯一性。
- Repository 内部自行 `commit()` 或物理删除教案。
- 将所有业务表机械增加含义不明的通用 `user_id`。
- 将照片 BLOB、本地绝对文件路径或运行时配置写入业务 Schema。

## 3. PostgreSQL 物理约定

### 3.1 Schema、扩展与命名

- 首期使用 PostgreSQL 默认 `public` Schema，不提前拆分多 Schema。
- 首个 Alembic 迁移显式创建 `btree_gist` 扩展，仅用于学期日期范围排他约束。
- 不依赖 `uuid-ossp`、`pgcrypto` UUID 默认函数或 `citext`。
- 表、列、约束和索引使用英文 `snake_case`。
- 约束命名使用 `pk_<table>`、`fk_<table>_<columns>_<target>`、`uq_<table>_<columns>`、`ck_<table>_<rule>`；索引使用 `ix_<table>_<columns>`。

### 3.2 通用类型与默认值

- UUIDv7 由 Python 应用或迁移脚本显式生成；`UUID` 主键不声明数据库 `DEFAULT`。
- 时间点使用 `TIMESTAMPTZ`，`created_at` 使用 `server_default=now()`；`updated_at` 在应用写入时更新，不依赖数据库 `ON UPDATE` 或触发器。
- 业务日期使用 `DATE`，不使用带时区时间替代。
- 结构化正文、上下文与元数据使用 `JSONB`；可运营正文使用 `TEXT`。
- 哈希使用小写十六进制 `CHAR(64)`；安全令牌哈希使用最多 `VARCHAR(128)`。
- 布尔状态列非空并声明服务端默认值。
- 所有正整数、非负整数、结束日期和成对空值规则都使用命名 `CHECK` 约束。

### 3.3 园所隔离与组合外键

`kindergartens` 是园所根表，`roles` 是全局参考表，两者不含 `kindergarten_id`。除这两表和 Alembic 元数据外，所有表都含 `kindergarten_id`。

每个拥有 UUID 主键的园所表同时声明 `UNIQUE (kindergarten_id, id)`，供子表使用组合外键：

```sql
FOREIGN KEY (kindergarten_id, parent_id)
REFERENCES parent_table (kindergarten_id, id)
ON DELETE RESTRICT
```

这一冗余唯一键用于在数据库层阻止跨园关联，不代替 Repository 的 `kindergarten_id` 过滤和 API 班级授权。

- 园所表到 `kindergartens(id)` 使用单列外键。
- 操作人、创建人、更新人和业务父子关系使用组合外键。
- `roles` 的 `role_id` 使用单列外键。
- 历史、审计、任务和导出关系默认 `ON DELETE RESTRICT`，不使用业务级联删除。

### 3.4 规范化列与状态代码

- `username_normalized`、`name_normalized` 由应用使用固定纯函数生成，并对纯函数编写固定样例测试。
- 数据库唯一约束使用规范化列，不依赖当前数据库 locale 的大小写排序。
- 业务可扩展代码使用 `VARCHAR` + `CHECK` 或参考表，不使用 PostgreSQL Enum。
- 任务、导出等基础设施状态首期也使用有限 `VARCHAR` + `CHECK`，避免 Alembic 修改 Enum 的额外风险。

### 3.5 不可变与不使用触发器

首期不使用数据库触发器复制应用业务规则。已发布提示词、教案快照和审计事件的不可变性通过下列方式叠加保证：

1. 应用用例不提供更新或删除接口。
2. Repository 只提供插入与查询方法。
3. 集成测试证明已发布或历史记录不会被应用路径改写。
4. 未来生产数据库角色权限在 ADR-0009 复审时再冻结，但必须保留审计表禁止应用账号 `UPDATE/DELETE` 的安全结果。

## 4. Schema 总览

| 领域 | 表 | 数量 |
| --- | --- | ---: |
| 园所与身份 | `kindergartens`、`users`、`webauthn_credentials`、`webauthn_challenges`、`bootstrap_initializations`、`account_invitations`、`recovery_codes`、`account_recovery_requests`、`identity_verification_approvals`、`roles`、`user_roles`、`refresh_tokens` | 12 |
| 教学设置 | `age_groups`、`classes`、`class_teachers`、`semesters`、`class_areas` | 5 |
| AI 模型 | `ai_model_profiles`、`ai_model_profile_capabilities` | 2 |
| 提示词 | `prompt_definitions`、`prompt_versions`、`prompt_test_runs` | 3 |
| 教案 | `daily_activity_plans`、`daily_activity_plan_authors`、`daily_activity_plan_snapshots`、`lesson_plan_sources` | 4 |
| 任务与 AI 结果 | `background_jobs`、`ai_generation_results` | 2 |
| 导出 | `daily_activity_plan_exports` | 1 |
| 系统支撑 | `workday_cache`、`audit_events` | 2 |
| **合计** |  | **31** |

首期不创建幼儿、年级组、审批、批注、照片、对象存储、平台租户或生产部署元数据表。

## 5. 园所与身份 Schema

### 5.1 `kindergartens`

```text
id UUID PK
name VARCHAR(200) NOT NULL
timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Shanghai'
is_active BOOLEAN NOT NULL DEFAULT true
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

约束：首期使用 `CHECK (timezone = 'Asia/Shanghai')`；未来开放其他园所时通过迁移扩展。不使用数据库单例约束限制只有一条园所。

### 5.2 `users`

```text
id UUID PK
kindergarten_id UUID NOT NULL FK -> kindergartens.id
username VARCHAR(120) NOT NULL
username_normalized VARCHAR(120) NOT NULL
phone_e164 VARCHAR(32) NULL
display_name VARCHAR(120) NOT NULL
webauthn_user_handle BYTEA NOT NULL
status VARCHAR(32) NOT NULL DEFAULT 'pending_registration'
activated_at TIMESTAMPTZ NULL
last_login_at TIMESTAMPTZ NULL
created_by UUID NULL
updated_by UUID NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

约束与索引：

- `UNIQUE (kindergarten_id, id)`。
- `UNIQUE (kindergarten_id, username_normalized)`。
- `UNIQUE (webauthn_user_handle)` 与 `CHECK (octet_length(webauthn_user_handle) = 32)`。
- 部分唯一索引 `(kindergarten_id, phone_e164) WHERE phone_e164 IS NOT NULL`。
- `CHECK (status IN ('pending_registration','pending_verification','active','suspended'))`。
- 索引 `(kindergarten_id, status)`。
- `(kindergarten_id, created_by)` 和 `(kindergarten_id, updated_by)` 组合自外键，首位管理员初始化时允许空。
- 停用账号仍占用用户名与手机号。

本表不包含密码字段。`active` 账号必须至少存在一个未撤销 WebAuthn 凭据由应用锁事务校验；
注册成功只进入 `pending_verification`，带外核验完成后才进入 `active`。

### 5.3 `webauthn_credentials`

```text
id UUID PK
kindergarten_id UUID NOT NULL
user_id UUID NOT NULL
credential_id BYTEA NOT NULL
public_key_cose BYTEA NOT NULL
sign_count BIGINT NOT NULL DEFAULT 0
transports JSONB NOT NULL DEFAULT '[]'::jsonb
aaguid UUID NULL
backup_eligible BOOLEAN NOT NULL
backup_state BOOLEAN NOT NULL
attestation_format VARCHAR(32) NULL
label VARCHAR(120) NOT NULL
created_via VARCHAR(32) NOT NULL
last_used_at TIMESTAMPTZ NULL
revoked_at TIMESTAMPTZ NULL
revoke_reason VARCHAR(64) NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

约束：`UNIQUE (kindergarten_id, id)`、`UNIQUE (kindergarten_id, credential_id)`、同园用户组合
外键、`sign_count >= 0`、`label = btrim(label)` 且非空、`created_via` 枚举 CHECK。`transports`
只允许字符串数组由应用 Schema 校验；撤销记录不删除。

### 5.4 `webauthn_challenges`

```text
id UUID PK
kindergarten_id UUID NOT NULL FK -> kindergartens.id
user_id UUID NULL
purpose VARCHAR(40) NOT NULL
challenge_hash VARCHAR(128) NOT NULL UNIQUE
authorization_context_id UUID NULL
expected_rp_id VARCHAR(253) NOT NULL
expected_origin VARCHAR(2048) NOT NULL
expires_at TIMESTAMPTZ NOT NULL
consumed_at TIMESTAMPTZ NULL
failed_attempts SMALLINT NOT NULL DEFAULT 0
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

`purpose` 只允许 `bootstrap_registration/invitation_registration/self_add/recovery_registration/
authentication/step_up`；`CHECK (expires_at > created_at)`、`failed_attempts >= 0`，索引
`(kindergarten_id, purpose, expires_at, consumed_at)`。`user_id` 非空时使用同园组合外键；
`authorization_context_id` 的目标由 purpose 决定并由应用锁事务验证。

### 5.5 `bootstrap_initializations`

```text
id UUID PK
kindergarten_id UUID NOT NULL
user_id UUID NOT NULL
token_hash VARCHAR(128) NOT NULL UNIQUE
purpose VARCHAR(24) NOT NULL
expires_at TIMESTAMPTZ NOT NULL
consumed_at TIMESTAMPTZ NULL
credential_id UUID NULL
activated_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

同园组合外键分别指向 `users` 与 `webauthn_credentials`；`purpose` 只允许
`empty_system/migration_admin`。空系统通过部分唯一索引或串行化事务保证只创建一条链路；
`migration_admin` 还需迁移窗口和零 WebAuthn active 管理员应用门禁。

### 5.6 `account_invitations`

```text
id UUID PK
kindergarten_id UUID NOT NULL
user_id UUID NOT NULL
issued_by UUID NOT NULL
token_hash VARCHAR(128) NOT NULL UNIQUE
expires_at TIMESTAMPTZ NOT NULL
consumed_at TIMESTAMPTZ NULL
revoked_at TIMESTAMPTZ NULL
revoke_reason VARCHAR(64) NULL
registered_credential_id UUID NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

目标、签发人和注册凭据均使用同园组合外键；`CHECK (expires_at > created_at)`、
`CHECK (NOT (consumed_at IS NOT NULL AND revoked_at IS NOT NULL))`。索引
`(kindergarten_id, user_id, consumed_at, revoked_at, expires_at)`；重新签发在事务内撤销旧邀请。

### 5.7 `recovery_codes`

```text
id UUID PK
kindergarten_id UUID NOT NULL
user_id UUID NOT NULL
code_hash VARCHAR(128) NOT NULL UNIQUE
issued_at TIMESTAMPTZ NOT NULL
consumed_at TIMESTAMPTZ NULL
revoked_at TIMESTAMPTZ NULL
replaced_by_id UUID NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

同园用户和自引用组合外键；`CHECK (NOT (consumed_at IS NOT NULL AND revoked_at IS NOT NULL))`。
部分唯一索引 `(kindergarten_id, user_id) WHERE consumed_at IS NULL AND revoked_at IS NULL` 保证
每个账号至多一个有效恢复码；账号激活后的首次成功通行密钥认证必须在签发会话的同一事务
插入首个恢复码并只向该用户返回原始值。

### 5.8 `account_recovery_requests`

```text
id UUID PK
kindergarten_id UUID NOT NULL
user_id UUID NOT NULL
recovery_code_id UUID NOT NULL
state VARCHAR(32) NOT NULL
approval_expires_at TIMESTAMPTZ NOT NULL
registration_token_hash VARCHAR(128) NULL UNIQUE
registration_expires_at TIMESTAMPTZ NULL
completed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

同园组合外键指向用户与恢复码；状态只允许 `pending_verification/approved/
registration_pending/completed/rejected/expired`。`registration_token_hash` 与到期时间必须同时空
或同时非空。部分唯一索引保证每个账号至多一个未终结请求；完成事务执行全量旧凭据、会话、
邀请和恢复码撤销并签发新恢复码。

### 5.9 `identity_verification_approvals`

```text
id UUID PK
kindergarten_id UUID NOT NULL
subject_user_id UUID NOT NULL
context_type VARCHAR(24) NOT NULL
context_id UUID NOT NULL
verifier_type VARCHAR(32) NOT NULL
verifier_user_id UUID NULL
verifier_reference VARCHAR(160) NOT NULL
decision VARCHAR(16) NOT NULL
decided_at TIMESTAMPTZ NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

主体和可选管理员核验人使用同园组合外键；`context_type` 只允许 `bootstrap/invitation/recovery`，
`verifier_type` 只允许 `admin/kindergarten_owner/deployment_operator/security_operator`，decision
只允许 `approved/rejected`。唯一 `(kindergarten_id, context_type, context_id, verifier_type,
verifier_reference)`；双人核验的不同自然人约束由应用事务和审计证明。

### 5.10 `roles`

```text
id UUID PK
code VARCHAR(64) NOT NULL UNIQUE
name VARCHAR(120) NOT NULL
is_system BOOLEAN NOT NULL DEFAULT true
```

首期幂等种子只包含 `admin` 和 `teacher`。该表不含园所、审计与时间戳，因为它是由迁移管理的全局只读代码字典，不是园所业务数据。

### 5.11 `user_roles`

```text
kindergarten_id UUID NOT NULL
user_id UUID NOT NULL
role_id UUID NOT NULL FK -> roles.id
assigned_by UUID NOT NULL
assigned_at TIMESTAMPTZ NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
PK (kindergarten_id, user_id, role_id)
```

组合外键指向同园 `users` 的 `user_id` 与 `assigned_by`。“不能移除最后一个有效管理员”需锁定相关用户/角色行并在应用事务中校验，不使用触发器。

### 5.12 `refresh_tokens`

```text
id UUID PK
kindergarten_id UUID NOT NULL
user_id UUID NOT NULL
token_family_id UUID NOT NULL
token_hash VARCHAR(128) NOT NULL UNIQUE
issued_at TIMESTAMPTZ NOT NULL
expires_at TIMESTAMPTZ NOT NULL
last_used_at TIMESTAMPTZ NULL
last_reauthenticated_at TIMESTAMPTZ NULL
revoked_at TIMESTAMPTZ NULL
revoke_reason VARCHAR(64) NULL
replaced_by_id UUID NULL
client_label VARCHAR(160) NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

约束与索引：

- `UNIQUE (kindergarten_id, id)`。
- 组合外键 `(kindergarten_id, user_id)` 指向 `users`。
- 组合自外键 `(kindergarten_id, replaced_by_id)` 指向 `refresh_tokens`。
- `CHECK (expires_at > issued_at)`。
- `CHECK (replaced_by_id IS NULL OR revoked_at IS NOT NULL)`。
- 索引 `(kindergarten_id, user_id, revoked_at, expires_at)` 和 `(token_family_id, revoked_at)`。
- `replaced_by_id` 必须属于同一 `token_family_id` 由轮换事务校验。
- `expires_at` 保存该 `token_family_id` 首次签发后 7 天的固定绝对到期时间；同一 family
  的后续轮换记录必须复制旧记录的 `expires_at`，不得按轮换时间重新计算或延长。
- 撤销整个 family 时，撤销事务必须将该 family 已存在记录的 `revoked_at` 和
  `revoke_reason` 一并更新。首期不增加 `family_expires_at` 或 `family_revoked_at`；前者由同族
  记录共享的 `expires_at` 表达，后者由同族记录的 `revoked_at` 表达。
- Access Token 的 `sid` 必须等于 `token_family_id`；每次 API 请求实时确认该 family 仍有
  未过期、未撤销的当前记录。WebAuthn step-up 更新当前记录的 `last_reauthenticated_at`，轮换
  时复制到新记录；高风险操作只接受 5 分钟内的值。

## 6. 教学设置 Schema

### 6.1 `age_groups`

```text
id UUID PK
kindergarten_id UUID NOT NULL FK -> kindergartens.id
code VARCHAR(64) NOT NULL
name VARCHAR(120) NOT NULL
sort_order INTEGER NOT NULL
is_active BOOLEAN NOT NULL DEFAULT true
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)`、`UNIQUE (kindergarten_id, code)`、`UNIQUE (kindergarten_id, name)`。
- `CHECK (sort_order >= 0)`。
- 每所园幂等种子 `toddler/small/middle/large`。

### 6.2 `classes`

```text
id UUID PK
kindergarten_id UUID NOT NULL
name VARCHAR(120) NOT NULL
name_normalized VARCHAR(120) NOT NULL
age_group_id UUID NOT NULL
is_active BOOLEAN NOT NULL DEFAULT true
created_by UUID NOT NULL
updated_by UUID NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)` 和 `UNIQUE (kindergarten_id, name_normalized)`。
- 组合外键指向同园 `age_groups`、`users(created_by)` 和 `users(updated_by)`。
- 索引 `(kindergarten_id, is_active, name_normalized)`。

### 6.3 `class_teachers`

```text
kindergarten_id UUID NOT NULL
class_id UUID NOT NULL
user_id UUID NOT NULL
is_lead_teacher BOOLEAN NOT NULL DEFAULT false
assigned_by UUID NOT NULL
assigned_at TIMESTAMPTZ NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
PK (kindergarten_id, class_id, user_id)
```

- 组合外键指向同园 `classes`、`users(user_id)` 和 `users(assigned_by)`。
- 部分唯一索引 `(kindergarten_id, class_id) WHERE is_lead_teacher`。
- 反向查询索引 `(kindergarten_id, user_id, class_id)`。
- 用户必须具有 `teacher` 角色由应用事务校验。

### 6.4 `semesters`

```text
id UUID PK
kindergarten_id UUID NOT NULL
name VARCHAR(160) NOT NULL
start_date DATE NOT NULL
end_date DATE NOT NULL
is_current BOOLEAN NOT NULL DEFAULT false
is_active BOOLEAN NOT NULL DEFAULT true
created_by UUID NOT NULL
updated_by UUID NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)`。
- `CHECK (start_date <= end_date)`。
- 部分唯一索引 `(kindergarten_id) WHERE is_current`。
- 排他约束：`EXCLUDE USING gist (kindergarten_id WITH =, daterange(start_date, end_date, '[]') WITH &&) WHERE (is_active)`。
- 组合外键指向同园 `users(created_by/updated_by)`。
- 索引 `(kindergarten_id, start_date, end_date)`。

### 6.5 `class_areas`

```text
id UUID PK
kindergarten_id UUID NOT NULL
class_id UUID NOT NULL
area_type VARCHAR(16) NOT NULL
name VARCHAR(120) NOT NULL
name_normalized VARCHAR(120) NOT NULL
sort_order INTEGER NOT NULL
is_active BOOLEAN NOT NULL DEFAULT true
created_by UUID NOT NULL
updated_by UUID NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)` 和 `UNIQUE (kindergarten_id, class_id, area_type, name_normalized)`。
- `CHECK (area_type IN ('indoor', 'outdoor'))` 和 `CHECK (sort_order >= 0)`。
- 组合外键指向同园 `classes` 与 `users(created_by/updated_by)`。
- 索引 `(kindergarten_id, class_id, area_type, is_active, sort_order)`。

## 7. AI 模型档案 Schema

### 7.1 `ai_model_profiles`

```text
id UUID PK
kindergarten_id UUID NOT NULL
name VARCHAR(120) NOT NULL
name_normalized VARCHAR(120) NOT NULL
api_base_url VARCHAR(500) NOT NULL
model_name VARCHAR(200) NOT NULL
api_key_ciphertext BYTEA NULL
api_key_encryption_version SMALLINT NULL
api_key_key_id VARCHAR(64) NULL
api_key_last_four VARCHAR(8) NULL
max_concurrency INTEGER NOT NULL DEFAULT 2
rate_limit_per_minute INTEGER NULL
is_default BOOLEAN NOT NULL DEFAULT false
is_active BOOLEAN NOT NULL DEFAULT false
risk_confirmed_by UUID NULL
risk_confirmed_at TIMESTAMPTZ NULL
created_by UUID NOT NULL
updated_by UUID NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

约束与索引：

- `UNIQUE (kindergarten_id, id)` 和 `UNIQUE (kindergarten_id, name_normalized)`。
- 部分唯一索引 `(kindergarten_id) WHERE is_default AND is_active`。
- `CHECK (max_concurrency > 0)` 和 `CHECK (rate_limit_per_minute IS NULL OR rate_limit_per_minute > 0)`。
- 密文组约束：`api_key_ciphertext`、`api_key_encryption_version`、`api_key_key_id` 要么同时为空，要么同时非空且版本大于 0。
- 风险确认约束：`risk_confirmed_by` 与 `risk_confirmed_at` 同时为空或同时非空；启用档案必须两者非空并具备完整密文组。
- 组合外键指向同园 `users(risk_confirmed_by/created_by/updated_by)`。

### 7.2 `ai_model_profile_capabilities`

```text
kindergarten_id UUID NOT NULL
model_profile_id UUID NOT NULL
capability_code VARCHAR(64) NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
PK (kindergarten_id, model_profile_id, capability_code)
```

- 组合外键指向同园 `ai_model_profiles`。
- `CHECK (capability_code IN ('text', 'vision', 'structured_output'))`。增加新能力时通过 Alembic 更新该约束和契约测试。

## 8. 提示词 Schema

### 8.1 `prompt_definitions`

```text
id UUID PK
kindergarten_id UUID NOT NULL
code VARCHAR(160) NOT NULL
name VARCHAR(160) NOT NULL
variable_whitelist JSONB NOT NULL
required_capabilities JSONB NOT NULL
result_schema_code VARCHAR(160) NOT NULL
result_schema_version INTEGER NOT NULL
model_profile_id UUID NULL
active_custom_version_id UUID NULL
is_active BOOLEAN NOT NULL DEFAULT true
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)` 和 `UNIQUE (kindergarten_id, code)`。
- `CHECK (jsonb_typeof(variable_whitelist) = 'array')`、`CHECK (jsonb_typeof(required_capabilities) = 'array')`、`CHECK (result_schema_version > 0)`。
- 可空组合外键指向同园 `ai_model_profiles`。
- `active_custom_version_id` 的外键在 `prompt_versions` 创建后以第二步 `ALTER TABLE` 增加：`(kindergarten_id, id, active_custom_version_id) -> prompt_versions(kindergarten_id, prompt_definition_id, id)`，从数据库层保证版本属于当前定义；应用还必须校验其为 `custom + published`。

### 8.2 `prompt_versions`

```text
id UUID PK
kindergarten_id UUID NOT NULL
prompt_definition_id UUID NOT NULL
version_number INTEGER NOT NULL
source_type VARCHAR(16) NOT NULL
lifecycle_state VARCHAR(16) NOT NULL
content TEXT NOT NULL
content_sha256 CHAR(64) NOT NULL
based_on_version_id UUID NULL
created_by UUID NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
published_by UUID NULL
published_at TIMESTAMPTZ NULL
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)`、`UNIQUE (kindergarten_id, prompt_definition_id, id)` 和 `UNIQUE (kindergarten_id, prompt_definition_id, version_number)`。
- 部分唯一索引 `(kindergarten_id, prompt_definition_id) WHERE source_type = 'custom' AND lifecycle_state = 'draft'`。
- `CHECK (version_number > 0)`、`CHECK (source_type IN ('system', 'custom'))`、`CHECK (lifecycle_state IN ('draft', 'published'))`。
- 发布成对约束：`published` 必须有 `published_at`；自定义发布还必须有 `published_by`；`draft` 的两列必须为空。
- 组合外键指向同园 `prompt_definitions` 和 `users(created_by/published_by)`；`(kindergarten_id, prompt_definition_id, based_on_version_id)` 指向同一定义的历史 `prompt_versions`。

### 8.3 `prompt_test_runs`

```text
id UUID PK
kindergarten_id UUID NOT NULL
prompt_definition_id UUID NOT NULL
prompt_version_id UUID NOT NULL
model_profile_id UUID NOT NULL
input_summary JSONB NOT NULL
result_schema_code VARCHAR(160) NOT NULL
result_schema_version INTEGER NOT NULL
output_content JSONB NULL
status VARCHAR(32) NOT NULL
elapsed_ms INTEGER NOT NULL
error_code VARCHAR(64) NULL
error_summary VARCHAR(1000) NULL
created_by UUID NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)`。
- 组合外键指向同园提示词定义、模型档案和创建人；`(kindergarten_id, prompt_definition_id, prompt_version_id)` 指向当前定义的 `prompt_versions`。
- `CHECK (jsonb_typeof(input_summary) = 'object')`、`CHECK (output_content IS NULL OR jsonb_typeof(output_content) = 'object')`、`CHECK (result_schema_version > 0)`、`CHECK (elapsed_ms >= 0)`。
- `CHECK (status IN ('succeeded', 'failed'))`，成功必须有输出且无错误，失败必须有错误代码且允许无输出。
- 索引 `(kindergarten_id, prompt_definition_id, created_at DESC)` 支持保留最近 20 条。

## 9. 一日活动计划 Schema

### 9.1 `daily_activity_plans`

```text
id UUID PK
kindergarten_id UUID NOT NULL
class_id UUID NOT NULL
semester_id UUID NOT NULL
plan_date DATE NOT NULL
kindergarten_name_snapshot VARCHAR(200) NOT NULL
class_name_snapshot VARCHAR(120) NOT NULL
age_group_name_snapshot VARCHAR(120) NOT NULL
semester_name_snapshot VARCHAR(160) NOT NULL
semester_start_date_snapshot DATE NOT NULL
semester_end_date_snapshot DATE NOT NULL
teaching_week_number INTEGER NULL
teaching_week_text VARCHAR(64) NULL
activity_date_text VARCHAR(64) NOT NULL
season_code VARCHAR(16) NOT NULL
content JSONB NOT NULL
content_schema_version INTEGER NOT NULL
version INTEGER NOT NULL DEFAULT 1
archived_at TIMESTAMPTZ NULL
archived_by UUID NULL
created_by UUID NOT NULL
updated_by UUID NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

约束与索引：

- `UNIQUE (kindergarten_id, id)` 和核心唯一 `UNIQUE (kindergarten_id, class_id, plan_date)`，归档记录不例外。
- 组合外键指向同园 `classes`、`semesters` 和 `users(archived_by/created_by/updated_by)`。
- `CHECK (semester_start_date_snapshot <= semester_end_date_snapshot)`、`CHECK ((teaching_week_number IS NULL) = (teaching_week_text IS NULL))`、`CHECK (teaching_week_number IS NULL OR teaching_week_number > 0)`、`CHECK (content_schema_version > 0)`、`CHECK (version > 0)`。活动日期在学期外时两个周次字段必须同时为空。
- `CHECK (season_code IN ('spring', 'summer', 'autumn', 'winter'))`。
- `CHECK (jsonb_typeof(content) = 'object')`。
- `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`。
- 索引 `(kindergarten_id, class_id, plan_date DESC)` 和 `(kindergarten_id, archived_at, plan_date DESC)`。

`kindergarten_id`、`class_id`、`semester_id` 和 `plan_date` 创建后的可变范围由 Repository 白名单限制；所有正文更新使用：

```sql
UPDATE daily_activity_plans
SET content = :content,
    content_schema_version = :schema_version,
    version = version + 1,
    updated_by = :actor_id,
    updated_at = now()
WHERE kindergarten_id = :kindergarten_id
  AND id = :plan_id
  AND version = :expected_version;
```

受影响行数不是 1 时返回稳定并发冲突，不重试覆盖。

### 9.2 `daily_activity_plan_authors`

```text
kindergarten_id UUID NOT NULL
plan_id UUID NOT NULL
user_id UUID NOT NULL
display_name_snapshot VARCHAR(120) NOT NULL
sort_order INTEGER NOT NULL
added_by UUID NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
PK (kindergarten_id, plan_id, user_id)
```

- `UNIQUE (kindergarten_id, plan_id, sort_order)` 和 `CHECK (sort_order >= 0)`。
- 组合外键指向同园教案、作者用户和 `added_by`。
- 索引 `(kindergarten_id, user_id, plan_id)` 支持按编写教师筛选。
- 新增作者必须是当前班级关联教师，且教案至少一名作者；解除关联后保留既有署名快照但立即撤销访问权。这些跨表规则由教案保存与授权事务校验。

### 9.3 `daily_activity_plan_snapshots`

```text
id UUID PK
kindergarten_id UUID NOT NULL
plan_id UUID NOT NULL
plan_version INTEGER NOT NULL
reason_code VARCHAR(32) NOT NULL
context_snapshot JSONB NOT NULL
content JSONB NOT NULL
content_schema_version INTEGER NOT NULL
content_sha256 CHAR(64) NOT NULL
created_by UUID NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)` 和 `UNIQUE (kindergarten_id, plan_id, id)`；同一教案版本可因恢复流程产生不同原因快照，不使用过度唯一约束合并它们。
- `CHECK (plan_version > 0)`、`CHECK (content_schema_version > 0)`、`CHECK (jsonb_typeof(context_snapshot) = 'object')`、`CHECK (jsonb_typeof(content) = 'object')`。
- `CHECK (reason_code IN ('manual_save', 'ai_adopted', 'archive', 'unarchive', 'before_restore', 'restored'))`。
- 组合外键指向同园教案与创建人。
- 索引 `(kindergarten_id, plan_id, created_at DESC)`。
- 该表只允许插入和查询，不提供更新/删除 Repository。

### 9.4 `lesson_plan_sources`

```text
id UUID PK
kindergarten_id UUID NOT NULL
plan_id UUID NOT NULL
source_type VARCHAR(16) NOT NULL
original_filename VARCHAR(255) NULL
source_sha256 CHAR(64) NOT NULL
extracted_text TEXT NOT NULL
uploaded_by UUID NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)`。
- `CHECK (source_type IN ('pasted_text', 'docx'))`。
- `CHECK ((source_type = 'docx' AND original_filename IS NOT NULL) OR (source_type = 'pasted_text' AND original_filename IS NULL))`。
- 组合外键指向同园教案与上传教师。
- 索引 `(kindergarten_id, plan_id, created_at DESC)`。
- 不保存上传 `.docx` 二进制或服务器绝对路径。

### 9.5 `content` JSONB 物理边界

`daily_activity_plans.content`、快照 `content` 与 AI `output_content` 必须带对应正整数 Schema 版本。数据库只验证它们是 JSON object，不在 SQL `CHECK` 中重写 Pydantic 嵌套 Schema。

教案正文顶层必须由应用 Schema 固定为：

```text
morning_activity
morning_talk
group_activity
indoor_area_game
afternoon_outdoor_game
daily_reflection
```

未识别的 Schema 版本可读原始数据，但必须禁止编辑、AI 生成与导出。

## 10. 后台任务与 AI 结果 Schema

### 10.1 `background_jobs`

```text
id UUID PK
kindergarten_id UUID NOT NULL
parent_job_id UUID NULL
retry_of_job_id UUID NULL
job_type VARCHAR(64) NOT NULL
status VARCHAR(32) NOT NULL
plan_id UUID NULL
target_section VARCHAR(64) NULL
requested_resource_version INTEGER NULL
idempotency_key VARCHAR(200) NOT NULL
attempt_count INTEGER NOT NULL DEFAULT 0
max_attempts INTEGER NOT NULL DEFAULT 3
requested_by UUID NOT NULL
trace_id UUID NOT NULL
lease_owner VARCHAR(160) NULL
lease_expires_at TIMESTAMPTZ NULL
last_heartbeat_at TIMESTAMPTZ NULL
queued_at TIMESTAMPTZ NULL
started_at TIMESTAMPTZ NULL
finished_at TIMESTAMPTZ NULL
error_code VARCHAR(64) NULL
error_summary VARCHAR(1000) NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

约束：

- `UNIQUE (kindergarten_id, id)` 和 `UNIQUE (kindergarten_id, idempotency_key)`。
- `UNIQUE (kindergarten_id, parent_job_id, target_section)` 防止同一批次重复栏目子任务。
- 组合自外键 `(kindergarten_id, parent_job_id) -> background_jobs(kindergarten_id, id)`，删除策略为 `RESTRICT`；禁止自引用。
- 组合自外键 `(kindergarten_id, retry_of_job_id) -> background_jobs(kindergarten_id, id)`，删除策略为 `RESTRICT`；禁止自引用。
- 可空组合外键指向同园教案；请求人指向同园用户。
- `CHECK (status IN ('pending_dispatch', 'queued', 'running', 'retrying', 'awaiting_confirmation', 'succeeded', 'failed', 'adopted', 'rejected', 'expired'))`。
- `CHECK (attempt_count >= 0 AND max_attempts > 0 AND attempt_count <= max_attempts)`。
- `CHECK (requested_resource_version IS NULL OR requested_resource_version > 0)`。
- 租约组约束：`lease_owner`、`lease_expires_at`、`last_heartbeat_at` 要么全空，要么前两者非空；心跳允许在领取后稍后写入。
- 完成状态 `succeeded/failed/adopted/rejected/expired` 必须有 `finished_at`；非完成状态必须无 `finished_at`。
- 失败必须有 `error_code`；非失败状态不保存过期错误摘要。

索引：

- `(status, lease_expires_at)` 支持恢复扫描。
- `(kindergarten_id, parent_job_id, created_at)` 支持父任务汇总。
- `(kindergarten_id, plan_id, created_at DESC)` 支持教案任务历史。
- 部分索引 `(status, created_at) WHERE status = 'pending_dispatch'`。

Worker 租约领取使用 PostgreSQL 行锁或条件 `UPDATE ... RETURNING`，重复 Redis 消息不得绕过状态与租约校验。

### 10.2 `ai_generation_results`

```text
id UUID PK
kindergarten_id UUID NOT NULL
job_id UUID NOT NULL
plan_id UUID NOT NULL
target_section VARCHAR(64) NOT NULL
model_profile_id UUID NOT NULL
model_name_snapshot VARCHAR(200) NOT NULL
prompt_definition_id UUID NOT NULL
prompt_version_id UUID NOT NULL
input_context JSONB NULL
input_sha256 CHAR(64) NOT NULL
result_schema_code VARCHAR(160) NOT NULL
result_schema_version INTEGER NOT NULL
output_content JSONB NULL
output_sha256 CHAR(64) NULL
expires_at TIMESTAMPTZ NOT NULL
adopted_at TIMESTAMPTZ NULL
adopted_by UUID NULL
rejected_at TIMESTAMPTZ NULL
content_cleared_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)` 和 `UNIQUE (kindergarten_id, job_id)`。
- 组合外键指向同园任务、教案、模型档案和采用人；`(kindergarten_id, prompt_definition_id, prompt_version_id)` 指向当前定义的提示词版本。
- `CHECK (result_schema_version > 0)`、`CHECK (input_context IS NULL OR jsonb_typeof(input_context) = 'object')`、`CHECK (output_content IS NULL OR jsonb_typeof(output_content) = 'object')`。
- 采用与拒绝互斥；`adopted_at` 与 `adopted_by` 同时为空或同时非空；`rejected_at` 非空时采用组必须为空。
- `content_cleared_at` 非空时 `output_content` 必须为空，但 `output_sha256`、模型、提示词和 Schema 追溯信息保留。
- 索引 `(kindergarten_id, plan_id, target_section, created_at DESC)` 和 `(expires_at) WHERE adopted_at IS NULL AND rejected_at IS NULL`。

## 11. Word 导出 Schema

### 11.1 `daily_activity_plan_exports`

```text
id UUID PK
kindergarten_id UUID NOT NULL
plan_id UUID NOT NULL
plan_version INTEGER NOT NULL
snapshot_id UUID NULL
job_id UUID NOT NULL
status VARCHAR(32) NOT NULL DEFAULT 'pending'
display_filename VARCHAR(255) NOT NULL
storage_key VARCHAR(500) NOT NULL
file_size BIGINT NULL
file_sha256 CHAR(64) NULL
template_code VARCHAR(120) NOT NULL
template_filename VARCHAR(255) NOT NULL
template_sha256 CHAR(64) NOT NULL
exported_by UUID NOT NULL
exported_at TIMESTAMPTZ NULL
error_code VARCHAR(64) NULL
error_summary VARCHAR(1000) NULL
file_missing_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)`、`UNIQUE (kindergarten_id, storage_key)` 和 `UNIQUE (kindergarten_id, job_id)`。
- 组合外键指向同园教案、任务和导出人；可空三列外键 `(kindergarten_id, plan_id, snapshot_id)` 保证快照属于同一教案。
- `CHECK (plan_version > 0)`、`CHECK (file_size IS NULL OR file_size >= 0)`。
- `CHECK (status IN ('pending', 'succeeded', 'failed'))`。
- `succeeded` 必须有 `file_size/file_sha256/exported_at` 且无错误；`failed` 必须有 `error_code` 且成功文件元数据为空；`pending` 的成功与错误列均为空。
- 索引 `(kindergarten_id, plan_id, created_at DESC)` 和 `(kindergarten_id, exported_by, created_at DESC)`。

`storage_key` 是服务器内部唯一键，不是绝对路径或可由浏览器构造的 URL。文件使用临时写入和原子改名，数据库不得先写入指向半成品的成功记录。

## 12. 系统支撑 Schema

### 12.1 `workday_cache`

```text
id UUID PK
kindergarten_id UUID NOT NULL
calendar_date DATE NOT NULL
result_code VARCHAR(16) NOT NULL
source_code VARCHAR(32) NOT NULL
source_version VARCHAR(120) NULL
detail JSONB NOT NULL DEFAULT '{}'
expires_at TIMESTAMPTZ NOT NULL
checked_at TIMESTAMPTZ NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)` 和 `UNIQUE (kindergarten_id, calendar_date)`。
- `CHECK (result_code IN ('workday', 'non_workday', 'unknown'))`、`CHECK (source_code IN ('local', 'online', 'combined', 'unavailable'))`、`CHECK (jsonb_typeof(detail) = 'object')`、`CHECK (expires_at > checked_at)`。两种来源均不可用时保存 `unknown/unavailable`。
- 索引 `(kindergarten_id, expires_at)`。

未知结果的过期时间必须短于已确认结果，由日历模块定义；缓存不是历史教案的权威来源。

### 12.2 `audit_events`

```text
id UUID PK
kindergarten_id UUID NOT NULL
event_code VARCHAR(120) NOT NULL
actor_user_id UUID NULL
actor_role_codes JSONB NOT NULL
resource_type VARCHAR(80) NOT NULL
resource_id UUID NULL
request_id UUID NULL
trace_id UUID NULL
job_id UUID NULL
outcome VARCHAR(16) NOT NULL
metadata JSONB NOT NULL DEFAULT '{}'
occurred_at TIMESTAMPTZ NOT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

- `UNIQUE (kindergarten_id, id)`。
- 可空组合外键 `(kindergarten_id, actor_user_id)` 指向用户；`resource_id` 不创建通用外键。
- `CHECK (jsonb_typeof(actor_role_codes) = 'array')`、`CHECK (jsonb_typeof(metadata) = 'object')`、`CHECK (outcome IN ('success', 'failure'))`。
- `CHECK (updated_at = created_at)` 表达创建后不更新的物理预期；应用还必须不提供更新路径。
- 索引 `(kindergarten_id, occurred_at DESC)`、`(kindergarten_id, event_code, occurred_at DESC)`、`(kindergarten_id, resource_type, resource_id, occurred_at DESC)` 和 `(kindergarten_id, actor_user_id, occurred_at DESC)`。

`metadata` 只允许事件专用白名单 Schema，不接收任意请求体、密钥、令牌、完整教案或完整 AI 输入输出。

## 13. 组合外键矩阵

以下矩阵是 Alembic 实现检查清单。“同园”表示外键必须同时包含 `kindergarten_id`。

| 子表 | 父关系 |
| --- | --- |
| `users` | `kindergartens`；同园 `users(created_by/updated_by)` |
| `webauthn_credentials` | 同园 `users` |
| `webauthn_challenges` | `kindergartens`；同园可选 `users`；purpose 绑定的授权上下文 |
| `bootstrap_initializations` | 同园 `users`、`webauthn_credentials` |
| `account_invitations` | 同园 `users(user_id/issued_by)`、`webauthn_credentials` |
| `recovery_codes` | 同园 `users`；同园自引用 `replaced_by_id` |
| `account_recovery_requests` | 同园 `users`、`recovery_codes` |
| `identity_verification_approvals` | 同园 `users(subject_user_id/verifier_user_id)`；context 由类型约束 |
| `user_roles` | 同园 `users(user_id/assigned_by)`；全局 `roles` |
| `refresh_tokens` | 同园 `users`；同园自引用 `replaced_by_id` |
| `age_groups` | `kindergartens` |
| `classes` | `kindergartens`；同园 `age_groups`、`users` |
| `class_teachers` | 同园 `classes`、`users(user_id/assigned_by)` |
| `semesters` | `kindergartens`；同园 `users` |
| `class_areas` | 同园 `classes`、`users` |
| `ai_model_profiles` | `kindergartens`；同园 `users` |
| `ai_model_profile_capabilities` | 同园 `ai_model_profiles` |
| `prompt_definitions` | `kindergartens`；同园 `ai_model_profiles`、`prompt_versions(active_custom_version_id)` |
| `prompt_versions` | 同园 `prompt_definitions`、自引用版本、`users` |
| `prompt_test_runs` | 同园提示词定义/版本、模型档案、用户 |
| `daily_activity_plans` | 同园班级、学期、用户 |
| `daily_activity_plan_authors` | 同园教案、用户 |
| `daily_activity_plan_snapshots` | 同园教案、用户 |
| `lesson_plan_sources` | 同园教案、用户 |
| `background_jobs` | 同园父任务、可选教案、用户 |
| `ai_generation_results` | 同园任务、教案、模型档案、提示词定义/版本、用户 |
| `daily_activity_plan_exports` | 同园教案、可选快照、任务、用户 |
| `workday_cache` | `kindergartens` |
| `audit_events` | `kindergartens`；同园可选用户 |

## 14. 应用事务不变量

以下规则需要锁定多行或结合权限上下文，不用触发器复制：

- 不能停用最后一个有效管理员，也不能移除其 `admin` 角色。
- 不能由自助操作撤销本人最后一个有效凭据，也不能撤销最后管理员的最后凭据。
- 邀请注册在一个事务保存凭据、消费邀请并推进到 `pending_verification`；人工核验后才激活。
- 首位管理员与最后管理员恢复的两项核验必须来自不同自然人及规定责任类型。
- 恢复完成必须原子撤销旧凭据、会话、邀请和恢复码，签发新恢复码但不创建登录会话。
- `class_teachers.user_id` 必须拥有 `teacher` 角色。
- 教案至少一名作者，且每位作者都是当前班级关联教师。
- 班级使用 AI 区域生成前至少有一个已启用室内区域和一个已启用户外区域。
- 默认 AI 模型档案必须已启用、完成风险确认、具备完整密文组并满足任务能力。
- `active_custom_version_id` 必须指向同一定义的 `custom + published` 版本。
- 手动保存、归档、恢复归档、历史恢复与 AI 结果采用在同一数据库事务中处理乐观锁、快照、正文、作者与审计。
- Repository 不自行 `commit()`；事务由 API 应用用例或 Worker 短用例拥有。

## 15. Alembic 迁移顺序

不要在单个迁移中一次创建全部 31 张表。建议使用下列可独立验证的迁移序列：

1. 启用 `btree_gist`，创建或扩展 `kindergartens`、`users`、WebAuthn/初始化/邀请/恢复七张表、
   `roles`、`user_roles`、`refresh_tokens` 和 `audit_events`，幂等种子角色。审计表必须从首位
   管理员初始化与首次 ceremony 开始可用。
2. 创建 `age_groups`、`classes`、`class_teachers`、`semesters`、`class_areas` 和 `workday_cache`，种子四个年龄段。工作日缓存必须在日期规则与手工教案闭环之前可用。
3. 创建 `ai_model_profiles` 与能力关联表。
4. 创建提示词定义、版本与测试表，然后增加 `active_custom_version_id` 外键并幂等种子 7 个系统定义/默认版本。
5. 创建教案、作者、快照与原始教案来源表。
6. 创建 `background_jobs` 与 `ai_generation_results`。
7. 创建 Word 导出记录。
8. 在空库和包含典型种子数据的 PostgreSQL 库上分别运行完整 `upgrade head`。

旧密码实现采用三段迁移：expand 阶段新增以上结构、禁用密码端点并撤销旧 Refresh family；
enroll 阶段只允许在无 WebAuthn active 管理员时由本机 CLI 为一个既有管理员签发短时
`migration_admin` 登记凭据；contract 阶段确认账号登记门禁后删除 `password_hash`、
`password_changed_at` 和 `is_active`。contract downgrade 只可重建空列，不恢复密码认证；
迁移前数据恢复依赖停机备份，不得把旧密码路由作为回滚方案。

每个迁移必须同时包含本次表的组合外键、检查约束、部分索引与回归测试，不先创建弱约束表再长期拖延补强。

## 16. PostgreSQL 与 SQLite 验证矩阵

| 能力 | SQLite 快速测试 | PostgreSQL 必测 |
| --- | --- | --- |
| 纯领域计算与 Pydantic JSON Schema | 是 | 可选重复 |
| 基本 Repository CRUD | 是 | 是，至少关键路径 |
| UUID、JSONB、TIMESTAMPTZ 语义 | 不充分 | 是 |
| 组合园所外键 | 不充分 | 是 |
| 部分唯一索引 | 不作为生产证据 | 是 |
| `daterange` + GiST 学期排他 | 否 | 是 |
| 乐观锁并发更新 | 不充分 | 是 |
| Worker `SKIP LOCKED`/条件领取 | 否 | 是 |
| Alembic 完整升级 | 可作辅助 | 是 |
| WebAuthn challenge/邀请/恢复并发消费 | 不充分 | 是，行锁与唯一索引 |

## 17. 必须实现的 Schema 验收测试

- 每张园所范围子表存在 `kindergarten_id`、`created_at`、`updated_at`；园所根表 `kindergartens` 无自引用园所列，全局 `roles` 代码字典不受该规则约束。
- 任意伪造跨园父子 ID 组合都被组合外键拒绝。
- 同园用户名、非空手机号、班级规范化名称、提示词代码和模型档案名称按预期唯一。
- Credential ID、challenge hash、邀请/初始化/恢复摘要唯一；每个账号至多一个有效恢复码、
  一个未终结恢复请求，重复消费只有一个事务成功。
- 含旧密码用户和 Refresh family 的 expand/enroll/contract 升级按设计收敛；contract 后物理
  Schema 不含 `password_hash`、`password_changed_at` 或 `is_active`。
- 邀请注册不激活账号，带外核验前不能登录；激活后的首次认证原子签发首个恢复码且管理员/
  CLI 不接触原始值；恢复完成撤销旧认证材料且不直接创建会话。
- 每班最多一名主班教师、每园最多一个当前学期与一个已启用默认模型档案。
- 有效学期日期范围不能重叠，边界日包含在范围内。
- 归档教案仍阻止同班同日创建第二份教案。
- 两个事务用同一 `expected_version` 更新教案时只有一个成功。
- 自动保存不创建快照，手动保存、AI 采用、归档、恢复和历史恢复创建正确原因快照。
- 重复任务幂等键、重复 Redis 投递和过期租约恢复不产生第二个 AI 结果或导出记录。
- AI 结果采用与拒绝互斥，清理正文后保留哈希与追溯元数据。
- 导出成功记录具备文件大小、文件哈希、模板哈希和时间，失败记录不伪装成可下载文件。
- 审计元数据白名单不接受密钥、令牌、完整教案或 AI 正文。

## 18. 实现时禁止的捷径

- 不使用 `Base.metadata.create_all()` 代替 Alembic。
- 不删除、跳过或放宽约束来让 SQLite 测试通过。
- 不先读取跨园数据再在 Service 层过滤。
- 不提供缺少 `kindergarten_id` 的 Repository 方法。
- 不使用动态 JSONB 代替需要索引、外键、唯一性或审计的关系列。
- 不将 Redis 中的任务结果视为权威状态。
- 不在业务 Schema 中增加未被首期功能使用的照片、视觉、对象存储、审批或多园平台表。
- 不因为生产部署已延后而放宽园所隔离、权限、密钥、审计和迁移要求。
