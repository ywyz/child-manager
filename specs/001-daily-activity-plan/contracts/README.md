# API v1 契约总则与端点目录

**Feature**: `001-daily-activity-plan`
**Contract revision**: `2.0.0`（移除密码契约并冻结通行密钥身份流程）
**Base path**: `/api/v1`
**Machine-readable contract**: [openapi.yaml](./openapi.yaml)
**Task semantics**: [job-state-machine.md](./job-state-machine.md)

## 1. 边界与可信上下文

- 浏览器唯一入口是当前实现档位的 NiceGUI Web 端口；浏览器不得直连本档位回环 API 端口。Web 作为
  服务端 BFF，将浏览器 `/api/v1/*` 请求转发到内部 API，并双向转发 Cookie、
  `Origin/Referer`、`X-CSRF-Token` 和 `Set-Cookie`。
- BFF 丢弃浏览器传入的 `Forwarded`、`X-Forwarded-For` 和内部客户端地址头，再按直接
  socket 对端重建内部来源；API 只有在直接对端是显式配置的回环 Web BFF 时才信任该值。
  生产代理链和信任列表不在本 feature 中设计。
- BFF 必须原样转发方法、规范化路径、query 和 body，以及认证 Cookie、`Origin` 或
  `Referer`、`X-CSRF-Token`；响应必须保留状态、body、`Content-Type`、`X-Request-ID` 和全部
  `Set-Cookie`。认证完成/刷新各有两条独立 access/refresh Cookie，退出有两条独立过期 Cookie；
  BFF 不得逗号折叠。请求/响应的 hop-by-hop 头不得转发，内部 API 地址不得暴露给浏览器代码。
- Web 只能通过本 API 使用业务能力，不导入 ORM、Repository 或 `packages/backend`；BFF
  不缓存权限结论，也不自行实现授权、事务或业务规则。
- 请求不得提交 `kindergarten_id` 或角色作为授权依据；API 从已验证会话取得园所、账号、
  当前角色与班级关系，并在每次请求重新检查账号启用状态。
- 教师只访问当前关联班级；管理员可查看、导出、归档/恢复全园教案。管理员只有同时是目标
  班级教师时才能编辑正文、调用 AI、维护区域或成为新作者。
- 历史作者姓名只是展示快照，不授予权限。解除班级关系后立即撤权，但不删除旧署名。
- 跨园或无权资源不得泄露敏感存在性；端点按情形返回 `404 resource.not_found` 或稳定的
  `403 auth.forbidden`，不能返回跨园对象摘要。

## 2. Cookie、令牌与 CSRF

Cookie 名称与属性：

| Cookie | 内容 | 属性 |
| --- | --- | --- |
| `child_manager_access` | 15 分钟 HS256 Access JWT | `Secure; HttpOnly; SameSite=Lax; Path=/` |
| `child_manager_refresh` | 7 天绝对期限的 opaque refresh token | `Secure; HttpOnly; SameSite=Lax; Path=/` |
| `child_manager_csrf` | 签名双提交令牌 | `Secure; SameSite=Lax; Path=/`，允许前端读取 |

不设置 `Domain`。Refresh 每次轮换且不延长 token family 的初始 7 天绝对期限；退出、本人或
管理员撤销会话、凭据恢复、账号停用和重放检测按规格撤销。Access JWT 携带 `sid`，API 每次
请求实时检查对应会话和账号状态，不能仅凭 JWT 未过期继续授权。

所有状态变更请求，包括 ceremony options/verify、刷新和退出，必须：

1. 校验允许来源的 `Origin`；缺失时回退校验 `Referer`。
2. 要求 `X-CSRF-Token` 与签名 CSRF Cookie 值一致且签名有效。
3. CSRF 无效时返回 `403 auth.csrf_invalid`。

`GET /auth/csrf` 是匿名安全端点，用于签发 CSRF Cookie。只有显式开发配置且 Web/API 都
绑定回环地址时可令 Cookie `Secure=false`；`HttpOnly`、SameSite、来源、CSRF 和授权规则
没有开发例外。

## 3. 通用请求与响应

### 3.1 Request ID

客户端可发送 `X-Request-ID`；API 验证格式后使用或生成 UUIDv7，并在响应头返回。后台任务
另有 `trace_id` 和 `job_id`，均可关联但不得携带敏感正文。

### 3.2 分页

所有声明分页的可增长集合使用 `page`、`page_size`：`page >= 1`，默认 1；`page_size` 默认
20，范围 1–100。超限返回 `422 request.invalid_pagination`，不得静默截断。

`/settings/age-groups` 固定为四个系统年龄段，是非分页的完整有序集合。班级区域属于
可增长集合，GET 使用标准分页；PUT 可整体提交有序配置，但成功只返回 `204`，客户端随后
分页读取。其他端点只要声明分页，也必须使用下列固定 envelope；不得为普通可增长列表
自行创造游标或一次返回全部的变体。

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

### 3.3 统一错误

```json
{
  "code": "lesson_plan.version_conflict",
  "message": "教案已被其他教师修改，请刷新后重试。",
  "request_id": "019...",
  "field_errors": [
    {
      "field": "content.morning_activity",
      "code": "required",
      "message": "请填写晨间活动。"
    }
  ]
}
```

`code` 是稳定英文机器码；`message` 和字段消息为简体中文；`field_errors` 无内容时为 `[]`，
只在输入校验错误中包含条目。FastAPI/Pydantic 错误必须转换成同一 envelope。不得返回
堆栈、SQL、绝对路径、模型密钥、token 或完整正文。

### 3.4 乐观锁

自动保存、手动保存、归档、恢复归档、历史恢复、AI 采用和导出请求体携带
`expected_version`。普通资源版本不匹配返回 `409 lesson_plan.version_conflict`。

除反思端点的单事务预保存外，Web 在提交一键或其他单栏 AI 请求前必须先完成无快照
自动保存（autosave）；保存失败或 409 时不得提交生成。生成端点仍携带保存后的 `expected_version`，
API 不信任仅由页面维护的版本状态。

AI 采用额外比较目标栏目基线哈希和实际输入哈希；相关输入变化返回
`409 ai.preview_stale`。生成时的旧全局版本本身不是预览失效理由，但采用提交仍以客户端
最新版本做 CAS。

教师教学上下文是每个任务创建时的不可变输入快照，采用时由服务端复用；页面为下一次
生成修改上下文，不追溯使既有预览失效。当前班级、区域、栏目等可变服务端输入仍须重读。

AI 任务受理事务同时创建唯一结果占位并冻结栏目基线、实际输入、模型、提示词和结果
Schema；Worker 只按 `job_id` 填入输出，不在排队后重读已变化的教案或设置。采用时再以
当前服务端输入复核冻结哈希。

### 3.5 Idempotency-Key

AI 生成/一键生成、提示词测试、显式任务重试和 Word 导出必须携带最大 200 字符的
`Idempotency-Key`。

- 幂等 scope 为同园操作者、HTTP 方法、规范化路由模板和 key；请求摘要另含规范化后的实际
  path 参数、有语义 query 参数与 canonical JSON body。UUID 使用标准小写文本，query 按名称/
  值稳定排序，JSON 对象按 key 排序并去除无意义空白；不得只对 body 做摘要。
- 同 scope、key 和请求摘要相同：返回原任务/记录。
- 同作用域 key 但摘要不同：`409 request.idempotency_conflict`。
- 用户明确新生成、重试或导出：使用新 key。
- Redis 投递失败不改变幂等结果；请求仍返回原 `pending_dispatch` 任务。

## 4. 权限矩阵

| 能力 | 未登录 | 关联教师 | 未关联教师 | 管理员 | 管理员且关联教师 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 查看目标班教案 | 否 | 是 | 否 | 是 | 是 |
| 编辑/自动保存/手动保存 | 否 | 是 | 否 | 否 | 是 |
| 调用/采用/拒绝 AI | 否 | 是 | 否 | 否 | 是 |
| 维护目标班区域 | 否 | 是 | 否 | 否 | 是 |
| 归档/恢复 | 否 | 是 | 否 | 是 | 是 |
| 导出/下载 | 否 | 是 | 否 | 是 | 是 |
| 系统设置、账号、模型、提示词 | 否 | 否 | 否 | 是 | 是 |
| 审计查询 | 否 | 否 | 否 | 是 | 是 |
| 管理本人凭据、恢复码和会话 | 否 | 是 | 是 | 是 | 是 |
| 签发邀请、核验激活、撤销他人凭据/会话 | 否 | 否 | 否 | 是 | 是 |

所有“否”都由 API 执行，不能只隐藏按钮。未登录统一返回 401；已认证但缺少管理员或班级
能力返回 403；跨园、跨班且不应暴露存在性的资源返回 404。BFF 和 Web 页面只能使用 API
返回的 capabilities 改善显示，不能把它们当作最终授权。

## 5. 端点目录

### 5.1 Health（不在 `/api/v1`）

| 方法 | 路径 | 语义 |
| --- | --- | --- |
| GET | `/health/live` | API 进程存活 |
| GET | `/health/ready` | PostgreSQL 和全局 JWT/CSRF 安全配置就绪；AI/Redis/日历/模板/存储故障只令分项 degraded，整体仍 200 |

### 5.2 Authentication & Users

| 方法 | 路径 | 语义 |
| --- | --- | --- |
| GET | `/auth/csrf` | 匿名签发/刷新签名 CSRF Cookie |
| POST | `/auth/bootstrap/registration/options` | 验证短时初始化凭据并生成首位管理员注册 options；成功 verify 才消费 |
| POST | `/auth/bootstrap/registration/verify` | 完成首个凭据登记并进入待核验状态，不建立会话 |
| POST | `/auth/invitation/registration/options` | 验证管理员邀请并生成首个凭据注册 options；成功 verify 才消费 |
| POST | `/auth/invitation/registration/verify` | 完成受邀账号首个凭据登记并进入待核验状态，不建立会话 |
| POST | `/auth/authentication/options` | 生成无用户名通行密钥认证 options |
| POST | `/auth/authentication/verify` | 校验 assertion 并签发 access/refresh Cookie；激活后首次成功认证只向用户返回一次恢复码 |
| POST | `/auth/step-up/options` | 为高风险操作生成新近用户验证 options |
| POST | `/auth/step-up/verify` | 建立 5 分钟 step-up 证明，不签发新会话 |
| POST | `/auth/refresh` | 轮换 access/refresh；检测重放 |
| POST | `/auth/logout` | 撤销当前 token family 并清除 access/refresh Cookie |
| GET | `/auth/me` | 当前账号、角色、园所展示和当前能力 |
| GET | `/auth/credentials` | 查看本人凭据及名称、创建/最近使用时间，不返回公钥 |
| POST | `/auth/credentials/registration/options` | 在新近用户验证后生成新增凭据 options |
| POST | `/auth/credentials/registration/verify` | 完成新增凭据登记 |
| PATCH/DELETE | `/auth/credentials/{credential_id}` | 命名或撤销本人非最后一个有效凭据 |
| POST | `/auth/recovery/requests` | 提交统一响应的恢复申请；恢复码本身不建会话 |
| POST | `/auth/recovery/registration/options` | 人工核验通过后生成恢复登记 options |
| POST | `/auth/recovery/registration/verify` | 登记新凭据，撤销旧凭据/会话/邀请/恢复码并签发新恢复码，不建会话 |
| POST | `/auth/recovery-code/rotate` | 在新近用户验证后主动轮换离线恢复码 |
| GET | `/auth/sessions` | 查看本人当前有效会话 |
| DELETE | `/auth/sessions/{session_id}` | 撤销本人指定会话；撤销当前会话时清除 Cookie |
| GET/POST | `/users` | 管理员分页查询/创建账号 |
| GET/PATCH | `/users/{user_id}` | 查看/修改非凭证字段 |
| PUT | `/users/{user_id}/roles` | 设置角色；阻止移除最后管理员 |
| POST | `/users/{user_id}/activate` | 管理员核验已登记账号并激活；首位管理员改由 CLI 双人激活 |
| POST | `/users/{user_id}/deactivate` | 停用并撤销全部会话 |
| GET/POST | `/users/{user_id}/invitations` | 查看邀请或签发最多 24 小时单次邀请 |
| POST | `/users/{user_id}/invitations/{invitation_id}/revoke` | 撤销未消费邀请 |
| GET | `/users/{user_id}/credentials` | 管理员查看教师凭据元数据 |
| DELETE | `/users/{user_id}/credentials/{credential_id}` | 管理员撤销教师凭据；最后凭据时原子撤销会话并重新邀请 |
| POST | `/users/{user_id}/sessions/revoke` | 管理员撤销教师全部会话 |
| GET | `/users/{user_id}/recovery-requests` | 管理员查看教师待核验恢复申请 |
| POST | `/users/{user_id}/recovery-requests/{recovery_request_id}/approve` | 管理员完成教师人工核验；最后管理员改走双人 CLI 流程 |

不存在公众注册、密码登录/改密/重置端点或万能恢复入口。CLI 生成 15 分钟单次初始化凭据并在
带外核验后激活账号；最后管理员恢复只允许
`init-admin recover-last-admin --recovery-request-id <uuid>`，交互匹配初始化时保存的两项
预登记引用并原子写入批准、推进请求和签发 15 分钟单次登记凭据。CLI 不接收恢复码、
credential JSON、预登记引用参数或相应环境变量；通行密钥必须在 HTTPS 或 `localhost` 浏览器
ceremony 中创建。Challenge 使用 32 字节随机值、5 分钟单次有效，并绑定 purpose、账号/上下文、
RP ID 与精确 Origin；注册要求 discoverable credential，常规 ceremony 强制 UV。成功生成
authentication/step-up options 不增加失败计数；只有 verify 失败或授权材料无效才计数，且失败
计数、challenge 失败结果与脱敏审计不得随 ceremony 业务事务回滚。

### 5.3 Settings

| 方法 | 路径 | 语义 |
| --- | --- | --- |
| GET/PATCH | `/settings/kindergarten` | 读取/修改园所名称；时区固定 |
| GET | `/settings/age-groups` | 读取四个系统年龄段 |
| GET/POST | `/settings/semesters` | 分页查询/创建学期 |
| GET/PATCH | `/settings/semesters/{semester_id}` | 查看/修改学期 |
| POST | `/settings/semesters/{semester_id}/make-current` | 原子设置唯一当前学期 |
| GET/POST | `/settings/classes` | 分页查询/创建班级 |
| GET/PATCH | `/settings/classes/{class_id}` | 查看/修改班级 |
| PUT | `/settings/classes/{class_id}/teachers` | 整体保存教师关系和唯一主班教师 |
| GET/PUT | `/settings/classes/{class_id}/areas/{area_type}` | 读取/整体保存室内或户外有序区域 |
| GET/POST | `/settings/ai-model-profiles` | 分页查询/创建模型档案 |
| GET/PATCH | `/settings/ai-model-profiles/{profile_id}` | 读取/修改；Key 只写、响应仅脱敏 |
| POST | `/settings/ai-model-profiles/{profile_id}/enable` | 首次要求风险确认；验证能力、Key 和 URL |
| POST | `/settings/ai-model-profiles/{profile_id}/disable` | 停用但保留历史引用 |

班级和区域类别都允许暂时为空。区域 PUT 只验证当前类别内部的名称、顺序与权限。

### 5.4 Prompts

| 方法 | 路径 | 语义 |
| --- | --- | --- |
| GET | `/prompts` | 七个稳定定义和生效版本摘要 |
| GET | `/prompts/{code}` | 定义、白名单、固定 Schema、生效版本和草稿 |
| PUT | `/prompts/{code}/draft` | 创建/更新唯一自定义草稿 |
| POST | `/prompts/{code}/publish` | 发布不可变新版本 |
| GET | `/prompts/{code}/versions` | 分页查看系统/自定义历史 |
| GET | `/prompts/{code}/versions/{version_id}` | 查看单一不可变版本 |
| POST | `/prompts/{code}/versions/{version_id}/restore` | 复制历史并发布为新版本 |
| POST | `/prompts/{code}/tests` | 创建异步 `prompt.test`；返回 `202` 任务 ID |
| GET | `/prompts/{code}/tests` | 分页查看最近 20 条测试运行 |
| GET | `/prompts/{code}/tests/{run_id}` | 查看单条运行及可清理结果 |
| DELETE | `/prompts/{code}/tests` | 清空已完成测试记录并写审计 |

系统默认版本只读。白名单外变量返回 `422 prompt.variable_not_allowed`；输出 Schema 不接受
管理端修改。测试 variables 必须先按路径 prompt code 的固定输入 Schema 校验，再在 run/job
受理事务中冻结为不可变 `input_context/input_sha256`、提示词正文/哈希、结果 Schema 和
`profile_id/base_url/model_name/capabilities/call_config_revision` 模型非密钥调用快照；不得复制
API Key 或密文。地址、模型名、能力或密钥变化必须原子递增 revision。Worker 只按 `job_id`
读取冻结上下文；当前 revision 与冻结值不同时，以 `prompt.configuration_changed` 零调用失败；
一致时才读取当前密钥并实时重验权限、模型启用和当前地址安全。完整上下文不进入公开响应、
Redis、日志或审计；公开 `input_summary` 只包含
排序变量名和 `all_values_redacted=true`。重复测试 key 的幂等检查先于 retention：始终返回原任务，
run 仍存在时一并返回；run 已被清理时关联资源为空，不重建、不再次调用模型。只有新 key 才
在定义行锁内清理最旧已完成记录；若仍有 20 条未完成测试，返回
`409 prompt.too_many_active_tests` 且不建任务或 run。

模板只允许 `\{\{[ \t]*([a-z][a-z0-9_]*)[ \t]*\}\}` 白名单纯替换；花括号内不接受换行或
其他 Unicode 空白，禁止表达式、过滤器、循环、函数和嵌套访问，变量值不得递归渲染。字符串
原文插入，空值为空字符串；数组保持顺序、对象按 key 排序并以 UTF-8 紧凑 JSON 序列化。
非法/未知/未闭合占位符在保存或发布时返回 422，执行时缺少已引用变量必须在任何外部模型
调用前失败。

### 5.5 Lesson Plans

| 方法 | 路径 | 语义 |
| --- | --- | --- |
| GET | `/plans` | 按班级、日期、作者、归档状态分页查询 |
| POST | `/plans/open` | 按 `class_id + plan_date` 创建或打开唯一教案 |
| GET | `/plans/{plan_id}` | 正文、上下文快照、版本、能力和软提示 |
| PUT | `/plans/{plan_id}/autosave` | 版本保存，不建快照 |
| PUT | `/plans/{plan_id}/save` | 显式保存正文/有序作者，建 `manual_save` 快照 |
| POST | `/plans/{plan_id}/archive` | 归档并建快照 |
| POST | `/plans/{plan_id}/unarchive` | 恢复归档并建快照 |
| GET | `/plans/{plan_id}/snapshots` | 分页查看不可变历史 |
| POST | `/plans/{plan_id}/snapshots/{snapshot_id}/restore` | 前置快照 + 恢复 + 新快照 |
| GET | `/plans/{plan_id}/group-activity-sources` | 分页查看来源元数据 |
| POST | `/plans/{plan_id}/group-activity-sources/text` | 保存教师确认的粘贴文本 |
| POST | `/plans/{plan_id}/group-activity-sources/docx` | 安全提取 `.docx` 并清理临时文件 |
| POST | `/plans/{plan_id}/ai/batch` | 一键创建晨间/晨谈/室内/户外四子任务 |
| POST | `/plans/{plan_id}/ai/generations` | 创建一个稳定 AI 任务 |
| GET | `/plans/{plan_id}/jobs` | 分页恢复计划任务历史/未完成任务 |

学期外 `teaching_week_number/text` 都为 `null`。`Plan` 响应包含服务端计算的
`capabilities` 和 `soft_warnings[]`，至少有：`semester.out_of_range`、
`calendar.non_workday`、`calendar.unknown`、`calendar.source_conflict`、
`group_activity.ai_step_missing`。

`.docx` 限制：上传 10 MiB、展开 50 MiB、最多 1000 个 ZIP 条目、提取 200,000 字符；
扩展名/MIME/ZIP/OOXML 必须一致，拒绝宏、外部关系、路径穿越和嵌套压缩。

### 5.6 Jobs & AI preview

| 方法 | 路径 | 语义 |
| --- | --- | --- |
| GET | `/jobs/{job_id}` | PostgreSQL 权威子任务；batch 父状态实时派生并含恰好四个子任务 |
| GET | `/jobs/{job_id}/preview` | 读取待确认结构化预览 |
| POST | `/jobs/{job_id}/adopt` | 复核权限/哈希/版本后采用并建一次快照 |
| POST | `/jobs/{job_id}/reject` | 保留原正文，不建快照 |
| POST | `/jobs/{job_id}/retry` | 只为最终失败 AI 栏目任务克隆冻结输入并以新 key 创建重试 |

反思请求携带 `expected_version` 和页面当前正文；API 在同一数据库事务内完成版本 CAS、
预保存当前正文、五个上游栏目 Schema 校验、幂等记录、`pending_dispatch` 任务和唯一 pending
AI 结果占位创建；占位冻结五栏实际输入/哈希、目标基线、模型、提示词和结果 Schema。该
预保存不创建教案快照；任一步失败全部回滚，不创建任务/结果且不消耗 Idempotency-Key。
是否由 AI 生成、是否含 AI 新增集体环节都不是完整性条件。集体拆分采用并保存后才可独立
创建新增环节任务；该任务只读当时已保存的当前集体活动，新增失败不回滚已采用拆分。反思
的 `current_plan` 只含该事务已保存的五个上游栏目及必要展示上下文，不含当前
旧反思。

`ai.batch` 父任务不投递、不租约、不重试，响应 `status/has_partial_failure` 每次从四个子任务
派生，父记录的执行状态、attempt 和租约字段均为 NULL；API 把两个 attempt 字段投影为
`0/0`，不得保存第二套执行真相。显式重试只接受有 AI 结果的 failed 执行任务；batch、
提示词测试、Word 导出和其他状态返回 `409 job.retry_not_allowed`。新重试任务与 pending
结果在同一事务创建，从原结果复制栏目基线、实际输入、模型、提示词及 Schema；要使用当前
新输入必须发起普通新生成。提交前 DB/必要本地配置失败可 503，提交后 Redis 失败仍返回原
`202 pending_dispatch`。

### 5.7 Word Exports

| 方法 | 路径 | 语义 |
| --- | --- | --- |
| POST | `/plans/{plan_id}/exports` | 保存/版本校验后创建异步导出 |
| GET | `/plans/{plan_id}/exports` | 分页查看历史导出 |
| GET | `/exports/{export_id}` | 查看状态、哈希、文件名和错误摘要 |
| GET | `/exports/{export_id}/download` | 再授权后流式下载并写审计 |

导出缺失确认只检查晨间、晨谈、集体、室内和户外五栏。`daily_reflection` 为空不触发
`export.confirmation_required`，但 Word 仍保留反思三行固定位置并输出空内容。

栏目缺失且 `confirm_incomplete=false` 返回 `409 export.confirmation_required` 与缺失字段，
且不保存正文、不创建任务、不消耗该 key。确认或内容完整后，API 在同一事务执行版本 CAS、
无快照保存、复制不可变上下文/正文到导出记录并创建 `pending_dispatch` 任务；任一步失败全
回滚。Worker 只读该导出输入快照，不重读可能已变化的当前教案。每次明确新导出用新 key；
历史文件缺失返回 `410 export.file_missing`，不得重建旧文件。

故障语义按实际依赖区分：AI、Redis 投递、Worker 或在线日历故障不得阻断同步手工能力，
并且在导出存储仍可读时不影响既有成功副本下载；新 Word 生成或存储写入失败不得影响已保存
教案或既有副本，也不得留下可下载半成品。若导出存储读取能力本身不可用，下载返回明确、
脱敏的失败，不承诺继续下载，也不重新生成文件冒充旧副本。

### 5.8 Audit

| 方法 | 路径 | 语义 |
| --- | --- | --- |
| GET | `/audit-events` | 管理员按事件、操作者、资源、结果、日期分页筛选 |
| GET | `/audit-events/{event_id}` | 查看固定白名单元数据 |

审计响应不得包含完整教案/AI 正文、challenge、初始化/邀请/恢复明文、WebAuthn assertion、
Cookie、token、API Key 或服务器路径。

## 6. 主要稳定错误码

| HTTP | `code` | 用途 |
| ---: | --- | --- |
| 400 | `request.invalid` | 无法解析或通用请求错误 |
| 401 | `auth.unauthenticated` | 未登录/会话无效 |
| 401 | `auth.authentication_failed` | 通用认证失败，不区分凭据、账号或签名原因 |
| 403 | `auth.csrf_invalid` | 来源或 CSRF 无效 |
| 403 | `auth.forbidden` | 已认证但无能力 |
| 403 | `auth.reauthentication_required` | 高风险操作缺少 5 分钟内的新近用户验证 |
| 404 | `resource.not_found` | 不存在或不应暴露的资源 |
| 409 | `auth.last_credential` | 本人或管理员操作会撤销最后管理员/本人最后有效凭据 |
| 409 | `auth.credential_counter_anomaly` | 非备份凭据计数器倒退，凭据和会话已进入风险处置 |
| 409 | `identity.last_admin_recovery_requires_cli` | 最后管理员恢复审批必须改走部署控制台双人核验 |
| 409 | `invitation.already_pending` | 目标账号已有可用邀请 |
| 409 | `request.idempotency_conflict` | 同 key 不同请求 |
| 409 | `prompt.too_many_active_tests` | 目标提示词已有 20 条未完成测试 |
| — | `prompt.configuration_changed` | 提示词测试任务终态；受理后模型调用配置或密钥已变化，零外部调用 |
| 409 | `job.retry_not_allowed` | 原任务类型或状态不允许显式重试 |
| 409 | `lesson_plan.version_conflict` | 当前资源版本冲突 |
| 409 | `ai.preview_stale` | 目标栏目或实际输入变化 |
| 409 | `export.confirmation_required` | 缺失栏目需确认 |
| 410 | `export.file_missing` | 历史副本缺失 |
| 410 | `auth.ceremony_expired` | Challenge 已过期、已消费或与当前 ceremony 不匹配 |
| 410 | `invitation.unavailable` | 邀请过期、撤销或已消费；不细分状态 |
| 410 | `recovery.unavailable` | 恢复材料或登记授权过期、撤销或已消费 |
| 422 | `request.validation_failed` | 字段校验失败 |
| 422 | `prompt.variable_not_allowed` | 白名单外变量 |
| 422 | `lesson_plan.current_semester_required` | 无当前学期 |
| 422 | `ai.required_area_missing` | 目标类别区域缺失 |
| 422 | `ai.reflection_inputs_incomplete` | 五个上游栏不完整 |
| 429 | `auth.rate_limited` | 公开身份端点按可信来源和 purpose 限流 |
| 503 | `database.unavailable` | 权威任务/业务数据无法保存 |
| 503 | `configuration.unavailable` | 请求所需服务端本地配置或固定资源缺失/无效 |

PostgreSQL 无法读写权威事实只使用 `database.unavailable`；当前请求必要的服务端本地配置或
固定资源缺失/无效只使用 `configuration.unavailable`，不得互相冒充。整体 ready 只有在
PostgreSQL 或所有核心请求共同依赖的 JWT/CSRF 等全局安全配置不可用时返回 503；AI、Redis、
日历、模板和导出存储只令健康分项 degraded，整体仍返回 200。
Redis 故障但 DB 保存成功时返回 202 `pending_dispatch`，不是 503；API 可以在健康响应中标为
degraded，但同步手工能力保持可用。外部 AI、在线日历或 Word 生成失败通过任务/资源状态和
稳定中文错误表达，不得把整个 API 标成不可用。

## 7. 契约演进

- v1 内只做向后兼容新增；删除/重命名字段、改变稳定枚举或语义需要新 API/Schema 版本。
- Prompt、PlanContent、AI result 和事件都携带独立 Schema code/version。
- 数据库模型不得直接作为响应模型；OpenAPI、`packages/contracts` 和契约测试必须同步。
- 任一端点实现前先写契约测试；实现完成后用生成/校验工具证明 `openapi.yaml` 可解析，且
  实际响应不偏离固定 envelope。
