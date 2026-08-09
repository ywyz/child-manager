# ADR-0013：受控单 Agent 运行时

- 状态：已接受
- 日期：2026-08-08
- 决策者：项目维护者
- 依赖：[ADR-0012](ADR-0012-local-first-desktop-product-reset.md)
- 契约：[`specs/003-desktop-local-first/contracts/agent-runtime.md`](../../specs/003-desktop-local-first/contracts/agent-runtime.md)

## 背景

ADR-0012 已把产品重置为本地优先桌面应用，并把 AI 冻结为可选联网增强。现有“选栏目 ->
生成结构化预览 -> 教师采用”仍是可独立使用的 AI Provider 能力，但不能直接演变为拥有数据库、
文件或任意 Python 执行权限的自治 Agent。

受控 Agent 需要帮助教师读取当前业务状态、形成建议和提出可审阅修改，同时继续满足以下硬约束：

- SQLite 是业务数据唯一权威，Provider 不是事实来源。
- Widget 不承载业务规则，Provider 不得绕过 Application Layer。
- 教师明确确认之前不得正式写入；失败、取消和过期结果不得改变正文。
- 正文、凭据和无关业务数据不得被长期保存为 Agent 记忆或跨会话自动注入。
- 首期只有单机、单教师和有限并发需求，没有多 Agent 编排的收益。

## 决策

### 1. 单 Agent 与 Application Layer

应用只装配一个 `AgentRuntime`，同一时刻最多执行一个 Agent turn。Runtime 位于 Application
Layer，负责 Agent 循环、上下文裁剪、Tool 调度、权限检查、确认门禁、取消和结果汇总；Qt
页面只提交命令并显示不可变结果。

不引入 Planner/Executor/Critic 等隐藏子 Agent、Agent 间委派、并行 Agent、角色群组或通用
Workflow 引擎。所谓“计划”只是教师可审阅的 `PlanPatch`，不是第二个执行主体。

### 2. Tool-only 业务访问

Provider 只能返回文本或请求已注册 Tool。它不得获得 Repository、SQLAlchemy Session、
SQLite 路径、文件系统句柄、Widget、任意 HTTP 客户端、Python/shell 执行器或应用服务定位器。

每个 Tool 是 Application Layer 提供的窄用例接口，声明稳定名称、输入 Schema、输出 Schema、
`Permission` 和脱敏策略。Runtime 拒绝未知 Tool、参数不符合 Schema、权限超出当前阶段或工具
结果与当前 turn 不匹配的请求。读取、草拟和写入都不得通过自然语言旁路 Tool registry。

### 3. 有界 Context 与无长期业务记忆

`AgentContext` 是一次 turn 的冻结最小快照，只包含完成当前意图所需的实体 ID、revision、选定
结构化字段、区域/学期等必要参考和 UI locale。它不包含凭据、数据库路径、完整历史、无关班级
或任意对象引用。

Runtime 可在当前进程、当前交互中保留有界消息窗口和 ToolResult；应用关闭、教师结束会话或
上下文切换后即丢弃。首期不建立 conversation、message、embedding、vector、summary、profile
或自动回忆表，不把聊天记录、正文副本、Provider 响应或隐藏摘要写入业务数据库、备份、日志或
凭据库。新的 turn 必须通过 READ Tool 从权威业务状态重建 Context。

必要的写入审计不是业务记忆：只保存 Tool 名、目标标识、确认/补丁摘要哈希、结果、revision
和时间等最小元数据，不保存提示词、对话、完整 Tool 输入输出或正文。

### 4. 分阶段权限与确认写入

`Permission` 固定为 `READ`、`DRAFT`、`WRITE`：

- `READ` 只读取并返回经过裁剪的业务投影。
- `DRAFT` 只计算建议或 `PlanPatch`，不得打开写事务或改变持久状态。
- `WRITE` 只能执行一个已经展示并由教师明确确认的精确 `PlanPatch`。

Slice 2B 只注册 `READ` 和 `DRAFT` Tool。写入阶段到来前，即使 Provider 请求 WRITE 或教师以
自然语言说“直接改”，Runtime 也必须拒绝；不得预建隐藏写入口。

写入阶段中，Runtime 先生成规范化 `PlanPatch`，UI 展示目标、字段级 before/after、影响、警告
和快照 revision。教师的 `Confirmation` 必须绑定该 Patch 的 SHA-256、目标、base revision、
会话/turn、过期时间和一次性 nonce。拒绝、修改意图、Context 变化、revision 变化、过期、取消
或重复使用确认均不写入，必须重新生成并再次确认。不得使用启动时授权、长期“总是允许”、
模糊批量同意或仅由 Provider 声称的确认。

### 5. 线程、事务与失败语义

Provider 调用和 Agent 循环在 Qt 后台任务中运行，只交换冻结 DTO；Widget、ViewModel、Session
和数据库连接不跨线程。Provider 等待期间不保持数据库事务。

READ Tool 使用短只读事务并返回带 revision 的 `ToolResult`；DRAFT Tool 是纯计算或只消费冻结
输入。WRITE Tool 在收到有效 Confirmation 后才开启一个短写事务，并在同一事务中重新读取目标、
校验 revision/不变量、应用完整 Patch、创建业务快照并写最小审计。任一步失败则全部回滚。

ToolResult 是数据，不是控制权。Runtime 只向 Provider 返回完成下一步所需的脱敏结果；稳定
错误码区分 stale、permission denied、confirmation required、cancelled 和 retryable provider
failure。取消、页面切换、应用关闭或迟到结果不得自动重试 WRITE、自动重新确认或采用结果。

### 6. Provider port

Application Layer 只依赖供应商中立的 `AgentProviderPort`。它接收裁剪后的 turn 请求与可用 Tool
Schema，输出 Assistant 内容、结构化 Tool call 或终止原因；不得暴露具体 SDK message、stream、
usage 或异常类型给 Runtime 之外的调用者。

首个生产 Adapter 复用现有 OpenAI 兼容配置与安全 Endpoint 策略，测试使用本地 Scripted
Adapter。更换 Provider 不改变 Tool、Permission、Confirmation、PlanPatch 或业务事务语义。

### 7. 固定实施顺序

1. **Slice 1**：桌面手工 MVP。
2. **Slice 2A**：现有可选 AI Provider 与结构化预览/人工采用。
3. **Slice 2B**：Agent Foundation、最小 `AgentContext`、Provider port、`READ`/`DRAFT` Tools；
   禁止正式写入。
4. **Slice 3**：备份与恢复。
5. **Agent 写入阶段**：`PlanPatch`、逐次确认、最小审计和单事务 WRITE。
6. **Level 3 Workflow**：继续延后，必须经新的 Design/ADR/Issue 才能考虑跨步骤自动编排。

现有批量 Word、历史/归档、桌面体验与分发工作仍按 003 任务依赖继续，但不得改变上述 Agent
能力解锁顺序。

## 取舍

### 收益

- 教师保留最终控制权，Provider 失误被限制在可审阅结果和精确 Tool 接口内。
- 事务、权限和业务不变量集中在 Application Layer，UI、Prompt 和 Provider 不重复实现。
- 无长期业务记忆降低隐私、陈旧上下文、备份泄漏和不可解释自动行为风险。
- 单 Agent 和有限 Tool 面减少测试组合，便于用 Scripted Adapter 重放完整失败矩阵。

### 代价

- 每次写入都需要生成 Patch、重新校验和明确确认，交互步骤多于自治 Agent。
- Context 必须按 turn 重建，不能依赖跨会话“记住教师习惯”获得便利。
- 首期不能自动完成长工作流，也不能由多个 Agent 并行处理栏目。

## 被否决方案

### Provider 直接调用 Repository 或 SQL

这会把权限、事务、Schema 和隐私语义暴露给不受信输出，并绕过应用服务不变量。

### 通用 MCP/插件或 shell/python Tool

首期没有任意扩展需求可以证明这种能力；宽工具会使文件、网络、凭据和代码执行面无法被字段级
确认覆盖。

### 自动采用 DRAFT 或预先授权所有写入

自然语言意图不能替代对精确差异的确认，也无法处理确认后发生的 revision 变化。

### 持久化完整对话、向量记忆或自动摘要

这些副本会携带正文和陈旧业务事实，扩大备份、删除、迁移与隐私边界；首期没有必须跨会话记忆
才能完成的用户故事。

### 多 Agent 与 Level 3 Workflow

它们会引入委派、共享状态、部分提交、恢复和审计语义。当前单教师桌面用例不证明其复杂度；
继续延后，不预建调度器或兼容空壳。

## 后续复审条件

只有真实验收证明单 Agent READ/DRAFT/确认 WRITE 不能满足明确用户故事时，才可通过新 ADR
复审长期偏好、跨会话记忆、多 Agent 或 Level 3 Workflow。复审必须先冻结数据分类、删除/导出、
Prompt injection、工具授权、部分提交恢复和可重放审计，不得以 Provider 新功能自动解锁。
