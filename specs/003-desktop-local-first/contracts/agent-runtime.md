# 受控 Agent Runtime 契约

## 1. 目的与适用阶段

本契约冻结受控单 Agent 的 Application Layer 接口、值对象、Provider seam、Tool 权限、确认写入
以及线程/事务语义。它落实
[`ADR-0013`](../../../docs/ADR/ADR-0013-controlled-agent-runtime.md)，不授权实现。

能力按以下顺序解锁：

```text
Slice 1 manual MVP
  -> Slice 2A optional AI Provider + structured preview
  -> Slice 2B Agent Foundation + Context + READ/DRAFT Tools (no durable write)
  -> Slice 3 backup/restore
  -> Agent WRITE = PlanPatch + Confirmation + audit + transaction
  -> Level 3 Workflow (deferred)
```

Slice 2A 的 `AiGenerationCoordinator` 仍可直接请求结构化栏目预览；它与 Agent 共用 Provider
Adapter 和 Endpoint 安全策略，但不伪装成 Tool loop。Slice 2B 及以后只允许一个 AgentRuntime，
不得增加隐藏 Agent、委派或 Workflow 执行器。

## 2. 依赖与信任规则

```text
Qt UI -> AgentRuntime (Application Layer) -> registered Application Tools
                    |
                    +-> AgentProviderPort -> OpenAI-compatible Adapter
```

- Runtime、Tool registry、Permission/Confirmation 校验位于 Application Layer。
- Provider Adapter 是不受信外部输出入口；任何文本和 Tool call 都必须按本契约校验。
- Tool 只调用既有应用模块或纯领域函数；不得向 Provider 暴露 Repository、Session、SQLite 路径、
  Widget、文件句柄、凭据、任意网络客户端或 application service locator。
- 不提供 shell、Python、SQL、任意文件、任意 URL、动态 import、MCP/插件发现或“按名称调用函数”
  Tool。
- Runtime 不根据 Provider 文本推断权限、确认或事务成功；只认本地类型化状态。

## 3. `Runtime`

外部 Interface 保持最小：

```text
AgentRuntime.start_turn(intent, context_request) -> OperationAccepted
AgentRuntime.cancel(operation_id) -> ToolResult[None]
AgentRuntime.confirm(confirmation) -> OperationAccepted
AgentRuntime.reject(patch_id) -> ToolResult[None]
```

Runtime 的深实现负责：

1. 从当前 UI 选择构建最小 Context 请求，而不是接收任意 Prompt 拼接数据。
2. 用 READ Tool 从权威业务状态生成冻结 `AgentContext`。
3. 根据当前阶段过滤可见 Tool Schema。
4. 驱动单 Agent turn，逐次验证 Provider Tool call，并设置最大 Tool call 数、Context 大小、
   Provider 响应大小和总时限。
5. 把 DRAFT 结果规范化为可显示文本或 `PlanPatch`；不得自动升级为 WRITE。
6. 在收到本地有效 `Confirmation` 后，启动一次新的 WRITE operation。
7. 汇总脱敏 `ToolResult`，通过 Qt runtime 信号返回 UI。

状态机：

```text
idle -> running -> awaiting_confirmation -> writing -> succeeded | failed | cancelled -> idle
           |                 |                 |
           +------draft------+------reject----+
```

- 全应用同时最多一个 `running/awaiting_confirmation/writing` Agent operation。
- `awaiting_confirmation` 不占用数据库事务或 Provider 请求；应用关闭后不恢复。
- `confirm()` 只接受本 Runtime 在当前会话签发且仍有效的 Confirmation 请求上下文。
- Runtime 重启后回到 `idle`，内存会话、ToolResult、Patch 和 nonce 全部失效。

## 4. `AgentContext`

```text
AgentContext
  context_id: UUID
  session_id: UUID
  turn_id: UUID
  created_at_utc: datetime
  expires_at_utc: datetime
  locale: "zh-CN"
  active_scope:
    class_id: int | null
    semester_id: int | null
    lesson_plan_id: int | null
    plan_date: date | null
  entity_revisions: tuple[EntityRevision, ...]
  facts: tuple[ContextFact, ...]
  allowed_permissions: frozenset[Permission]
```

约束：

- Context 是一次 turn 的冻结、短生命周期、最小业务投影；不包含 ORM/Session/Widget/可变对象。
- `facts` 只允许已注册 READ Tool 的结构化输出，字段按当前意图白名单裁剪。
- 不包含 API Key、远程凭据、恢复口令、数据库/文件绝对路径、日志、无关班级、完整历史版本、
  隐藏系统 Prompt 或超出当前任务的正文。
- Context 必须携带相关实体 revision；无法取得一致 revision 时停止生成 Patch。
- Context 不写入 SQLite、备份、日志、凭据库或 Provider cache。结束 turn、切换业务上下文、取消、
  超时或退出应用时丢弃。
- 后续 turn 不自动继承旧业务事实；必须重新经 READ Tool 获取。

## 5. `Permission`

```text
Permission = READ | DRAFT | WRITE
```

| Permission | 允许 | 禁止 |
|---|---|---|
| `READ` | 返回裁剪的业务投影和 revision | 写库、创建快照、文件发布、远程副作用 |
| `DRAFT` | 对冻结输入进行纯计算，返回建议或 PlanPatch | 打开写事务、改变 preview/正文/设置、隐式采用 |
| `WRITE` | 执行一个已确认的精确 PlanPatch | 扩大目标/字段、调用未确认 Tool、后台自动重试 |

Tool descriptor 固定声明 Permission，不允许 Provider 或 Prompt 覆盖。Slice 2B registry 不注册
任何 WRITE Tool；不存在“先隐藏但可调用”的写入口。

## 6. Tool descriptor 与 `ToolResult`

```text
ToolDescriptor
  name: stable dotted name
  permission: Permission
  input_schema: versioned closed schema
  output_schema: versioned closed schema
  redaction_policy: stable code
  timeout_ms: positive integer

ToolResult[T]
  call_id: UUID
  tool_name: str
  permission: Permission
  status: ok | rejected | failed | cancelled | stale
  value: T | null
  error_code: str | null
  message: str
  retryable: bool
  observed_revisions: tuple[EntityRevision, ...]
  redactions: tuple[str, ...]
```

- Schema 顶层拒绝未知字段；ID、枚举、长度、日期范围和集合数量均有上限。
- Runtime 为每次 call 生成 ID，并验证返回 Tool 名、Permission 和 operation/turn 归属。
- `value` 只含 Provider 继续当前 turn 必需的数据；用户可见 `message` 为简体中文。
- 正文、Prompt、Key、口令、token 和完整异常不得进入 `message`、repr 或结构化日志。
- retryable 只授权 Runtime 重试 READ/DRAFT 或 Provider 调用；WRITE 永不自动重试。
- 未知 Tool、Schema 错误和阶段禁用返回 `agent.tool_not_allowed`，不尝试近似匹配。

Slice 2B 首批 Tool 面保持窄小：

```text
READ  lesson_plan.read_current
READ  lesson_plan.read_context
READ  calendar.read_evaluation
READ  settings.read_class_areas
DRAFT lesson_plan.draft_section_patch
DRAFT lesson_plan.draft_reflection_patch
```

DRAFT Tool 只生成 Patch，不持久化 `ai_previews` 或业务正文。若需复用 AI 结构化校验，可调用纯
领域实现，不得把现有 `adopt()` 当作 DRAFT。

## 7. `PlanPatch`

```text
PlanPatch
  patch_id: UUID
  schema_version: 1
  created_at_utc: datetime
  expires_at_utc: datetime
  context_id: UUID
  turn_id: UUID
  tool_name: str
  target:
    entity_type: lesson_plan
    entity_id: int
  base_revisions: tuple[EntityRevision, ...]
  operations: tuple[PatchOperation, ...]
  warnings: tuple[str, ...]
  canonical_sha256: lowercase hex

PatchOperation
  field_path: registered closed path
  before_sha256: lowercase hex
  before_display: bounded redacted text
  after_value: schema-valid structured value
  after_display: bounded redacted text
```

- 只允许 registry 为当前 WRITE Tool 注册的实体、字段路径和操作；不接受通用 JSON Patch、SQL、
  文件路径、表达式或可执行代码。
- operations 必须确定有序、无重复/重叠路径，并以规范 JSON 计算 SHA-256。
- UI 必须展示 Tool、目标、每一项 before/after、警告和“将创建快照/审计”的影响。
- Patch 只是提案，不是业务状态；DRAFT 完成、教师拒绝、过期、Context 改变或应用关闭后可直接
  丢弃，不写数据库或备份。
- Provider 不签发、确认或修改 Patch；Runtime 从已校验 DRAFT 输出重新构造规范 Patch。

## 8. `Confirmation`

```text
Confirmation
  confirmation_id: UUID
  patch_id: UUID
  patch_sha256: lowercase hex
  session_id: UUID
  turn_id: UUID
  target: EntityRef
  base_revisions: tuple[EntityRevision, ...]
  issued_at_utc: datetime
  expires_at_utc: datetime
  nonce: cryptographically random bytes
  decision: accept
```

- UI 只能在完整 Patch 已可见后，由明确的确认操作创建 `decision=accept`。
- Confirmation 绑定单一 Patch、目标、revision、会话和 turn；不得复用于其他 Patch 或批量目标。
- nonce 单次使用并仅存内存。拒绝、超时、取消、修改 Patch、切换 Context、revision 改变、应用
  退出或首次提交尝试结束后立即失效。
- 不支持“本次会话都允许”“始终允许”、启动参数、Prompt 字样或 Provider tool call 充当确认。
- Runtime 在进入 WRITE 前验证一次，WRITE Tool 在事务内结合当前 revision 再验证一次。

稳定错误码：`agent.confirmation_required`、`agent.confirmation_expired`、
`agent.confirmation_mismatch`、`agent.confirmation_reused`、`agent.patch_stale`。

## 9. Provider port

```text
AgentProviderPort.complete(request: ProviderTurnRequest) -> ProviderTurnResult

ProviderTurnRequest
  operation_id: UUID
  system_policy: versioned local resource ID
  context: AgentContext
  messages: bounded current-session messages
  tools: tuple[ToolDescriptor, ...]
  response_limit: integer

ProviderTurnResult
  assistant_content: bounded text | null
  tool_calls: tuple[ProviderToolCall, ...]
  finish_reason: completed | tool_calls | length | refused | cancelled
  provider_request_id: redacted string | null
```

- Application Layer 不依赖具体供应商 SDK 类型、消息类、stream event、异常或 token 计费结构。
- 生产 OpenAI-compatible Adapter 复用现有一个当前模型、凭据、Endpoint/重定向/超时/响应上限
  规则；Scripted Adapter 是确定性测试替身，因此该 seam 有两个真实用途。
- Adapter 不执行 Tool。它只解析并返回结构化 Tool call；Runtime 负责验证、调度和回送结果。
- Provider 请求遵循数据最小化，不发送教师显示名、凭据、绝对路径、无关正文或完整历史。
- Provider 失败、拒绝或结构错误不改变业务数据，不把原始响应写日志或持久化。

## 10. 线程契约

- Qt 主线程只创建 Context request、提交 Runtime operation 和显示结果。
- 整个 Agent loop 与 Provider Adapter 在一个受控后台 operation 中串行运行；首期不并行 Tool
  call，也不创建子 Agent。
- 跨线程只传冻结 `AgentContext`、Tool call、`ToolResult`、`PlanPatch` 和 operation ID。
- Widget、ViewModel、SQLAlchemy Session/Connection、Repository、Provider SDK client 的可变
  stream 对象均不得跨线程。
- 每次需要数据库的 Tool 在其执行线程内创建并关闭 Session；不得复用 Context 构建时的连接。
- 页面切换、operation ID 不匹配、取消或应用关闭后，迟到 Provider/Tool 结果一律丢弃。
- 退出顺序遵循：停止新 turn -> 使 Confirmation/Patch 失效 -> 请求取消 -> 有界等待 -> 关闭数据库。

## 11. 事务与 WRITE 契约

READ/DRAFT：

- READ 使用短只读事务，返回结果后立即关闭；Provider 等待期间没有打开事务。
- DRAFT 只消费冻结输入并返回结果，不写 `ai_previews`、audit 或业务表。

WRITE（只在 Agent 写入阶段注册）：

```text
validate confirmation locally
  -> open one write transaction
  -> load exact target and current revision
  -> revalidate patch hash, revision, field before hashes and domain invariants
  -> save operation-before immutable lesson_plan_version
  -> apply every operation in the PlanPatch
  -> increment revision
  -> append minimal agent_action_audit
  -> commit
```

- Patch 必须全有或全无；禁止逐 operation 提交或成功一半后再请求确认。
- stale、归档只读、Schema/领域校验或 audit 写入失败均回滚正文、快照和 audit。
- 一个 Confirmation 只对应一次提交尝试；未知 commit 结果必须按 revision/audit key 对账，不能
  自动重放 WRITE。
- 事务内不调用 Provider、网络、Word、备份或 UI；写事务等待时间不得包含教师确认时间。
- 首期 WRITE 只允许已注册的教案字段 Patch；设置、删除、归档、恢复、文件、备份和远程操作
  不因 Agent Runtime 获得写能力。

最小审计：

```text
AgentActionAudit
  action_id: UUID
  tool_name: str
  target_type: str
  target_id: int
  patch_sha256: str
  confirmation_id: UUID
  base_revision: int
  result_revision: int
  outcome: committed
  created_at_utc: datetime
```

不保存 Prompt、对话、Provider 原文、完整 Context、Tool 输入输出、before/after 正文或 Key。

## 12. 无长期业务记忆

首期禁止创建或使用：

- conversation/thread/message/run 表；
- embedding/vector store/retrieval index；
- 自动生成的教师画像、偏好、长期摘要或“记忆”；
- Provider 托管 thread、assistant state 或跨会话 cache 作为业务事实来源；
- 聊天记录、Context、Patch、ToolResult 的备份/恢复协议。

允许持久化的只有既有业务实体、教师明确采用后的正文/版本，以及 WRITE 的最小不可变审计。
如果未来需要跨会话偏好，必须先新增规格和数据生命周期设计，不能复用 audit 推断偏好。

## 13. 验证矩阵

Slice 2B：

- Provider 请求未知 Tool、WRITE Tool、额外参数、越界 ID/长度或伪造 Permission，全部拒绝。
- READ 结果只含白名单字段；Key、路径、无关班级和历史正文不进入 Context/Provider/log/repr。
- DRAFT 产生稳定 PlanPatch；取消、拒绝、过期、关闭应用后 SQLite 和版本计数完全不变。
- Scripted Adapter 覆盖正常文本、一次/多次 Tool call、循环上限、拒绝、超长、结构错误和取消。
- 同时第二个 turn 被拒绝；不存在子 Agent、并行 Tool 或持久化 thread 恢复。

Agent 写入阶段：

- 未确认、伪造、错 Patch hash、错 target、错 turn、过期、复用 nonce、revision/field hash 变化
  均零写入。
- 有效确认只执行展示的字段；快照、正文、revision 和最小 audit 同事务成功。
- 归档只读、领域校验、audit 失败和 commit 异常全部回滚；未知 commit 按 action ID 对账且不重放。
- Provider/网络在确认后不可用不影响本地 WRITE，因为事务只消费已确认规范 Patch。
- 应用重启后没有会话/Context/Patch/Confirmation 恢复，业务状态只由 SQLite READ Tool 重建。

## 14. 明确非目标

- 多 Agent、Agent 委派、并行 Agent、Planner/Executor/Critic 角色。
- Level 3 Workflow、跨步骤自治、定时/后台自主执行、无人值守 WRITE。
- 通用插件/MCP 市场、动态 Tool、shell/Python/SQL/任意文件或任意网络访问。
- 长期业务记忆、向量检索、教师画像、跨设备 Agent thread 同步。
- Agent 修改设置、凭据、归档、删除、备份、恢复、Word 文件或远程对象。
- 以日志、audit 或 Provider 历史替代 SQLite 权威状态。
