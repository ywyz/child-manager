# 桌面 Slice 2B GREEN 与验收证据

## 1. 固定范围与停止边界

- 执行 Issue：[Issue #20](https://github.com/ywyz/child-manager/issues/20)
- 完整 docs SHA：`d4ac961a04a273a0384e295190296f69538b313b`
- Slice 2A 固定 GREEN / 本 Slice 实现基线：
  `8d285f03616033e757ee1f31e298da6d58a3501b`
- 实施分支和工作树：`dev`、`/home/admin/code/child-manager-dev-desktop`。
- 本轮目标和授权包含 T054–T060、回归修复、Review、提交、推送、精确 CI 与 Issue 回填；不实现
  WRITE/Confirmation、子 Agent、并行 Tool、长期记忆或 Agent 状态持久化。
- 提交和推送只进入 `dev`；不创建 PR、不切换分支、不进入 `main`。
- Windows 验收保留为用户手工门禁；2026-08-12 已补充完成源码启动与 `0001 -> 0002` 迁移
  保护复测，其余 Agent READ/DRAFT 行为仍以独立检查表为准。

## 2. 进入 T055 前的 clean RED

```bash
uv run pytest --collect-only -q
uv run pytest -q --tb=short
```

结果：`166 tests collected`；默认入口为 `145 passed, 21 failed`。21 项失败全部来自尚未实现的
Provider DTO/port、关闭 registry、Runtime loop 和 Agent 草稿 UI；没有 import、fixture、网络、
Cloud、PostgreSQL、Redis 或其他环境错误。

## 3. T055 Provider port 与 Adapter

定向 RED：

```bash
uv run pytest -q --tb=short \
  tests/desktop/contracts/test_agent_runtime_contract.py::test_provider_port_uses_only_application_owned_request_and_result_types \
  tests/desktop/contracts/test_agent_runtime_contract.py::test_provider_port_public_annotations_do_not_leak_concrete_sdk_types
```

结果：`2 failed`，均为 `SLICE2B_RED`，原因是 `AgentProviderPort` 和 Application-owned Provider
DTO 尚未实现。

最小 GREEN 后同一命令结果：`2 passed`。`AgentProviderPort.complete()` 只接收/返回
`ProviderTurnRequest`/`ProviderTurnResult`；公开类型注解不包含 `openai`、`anthropic`、`httpx`、
`ChatCompletion` 或 stream 类型。`OpenAICompatibleAgentProvider` 构造函数不接收 registry、
executor、Repository、Session 或 Tool callable；它只把关闭 Schema 发给 OpenAI-compatible
Endpoint，并把文本/Tool call 解析为冻结 Application DTO。测试 fixture 继续使用确定性的
`ScriptedProvider`，不访问真实网络或付费 Provider。

T055 完整验证：

```bash
uv run pytest -q \
  --ignore=tests/desktop/contracts/test_agent_runtime_contract.py \
  --ignore=tests/desktop/unit/test_agent_context.py \
  --ignore=tests/desktop/application/test_agent_read_draft.py \
  --ignore=tests/desktop/ui/test_agent_draft_flow.py
uv run pytest -q tests/desktop/packaging tests/desktop/packaging/test_default_quality_gate.py
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv sync --locked
uv lock --check
env -u PYTHONPATH uv run --no-sync python \
  tests/desktop/contracts/agent_persistence_probe.py
```

结果：稳定桌面回归 `125 passed`；打包/默认质量入口 `3 passed`；Ruff format 为 400 files、
Ruff lint 通过、Pyright `0 errors / 0 warnings / 0 informations`；锁定同步和锁检查通过。持久化
探针为 `agent_persistence_source_hits=0`、SQLite forbidden/broad hits 均为空、backup/log files
均为 0。另用标准库 `TemporaryDirectory`、隔离 `PYTHONPATH` 和 offscreen Qt 启动
`python -I -m kindergarten_manager`，3 秒后仍在事件循环且已创建桌面 SQLite。

业务代码变更后执行：

```bash
graphify update .
graphify diagnose multigraph --graph graphify-out/graph.json --undirected
```

结果：5543 nodes、16012 edges；missing/dangling/self-loop/collapsed 均为 0。图中仍报告 2 个
unverified code nodes；因节点数超过 5000，HTML 按 Graphify 保护规则跳过，JSON/报告已更新。

## 4. T056 关闭 READ/DRAFT registry

定向 RED：

```bash
uv run pytest -q --tb=short \
  tests/desktop/contracts/test_agent_runtime_contract.py::test_registry_rejects_unknown_write_and_forged_permission
```

结果：`3 failed`，全部为 `SLICE2B_RED`，原因是公开模块
`kindergarten_manager.application.agent_tools` 尚未实现；三项分别证明未知 Tool、WRITE descriptor
和伪造 Permission 的目标拒绝行为。

最小 GREEN 后同一测试为 `3 passed`，T049 完整契约为 `13 passed`。`ToolRegistry` 只接受固定
六项批准名称，descriptor 和 handler 都由本地构造；拒绝 WRITE permission、未知/重复名称、
permission 不匹配和不完整 handler 映射。批准面精确为：

```text
READ  lesson_plan.read_current
READ  lesson_plan.read_context
READ  calendar.read_evaluation
READ  settings.read_class_areas
DRAFT lesson_plan.draft_section_patch
DRAFT lesson_plan.draft_reflection_patch
```

registry 不包含动态发现、MCP/插件、文件、URL、SQL、代码或任意函数调用入口；两个 DRAFT
handler 只通过注入的纯 Application callable 返回 `ToolResult`，registry 本身无 Repository、
Session 或写事务能力。

T056 完整验证：

```bash
uv run pytest -q \
  --ignore=tests/desktop/application/test_agent_read_draft.py \
  --ignore=tests/desktop/ui/test_agent_draft_flow.py
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv sync --locked
uv lock --check
env -u PYTHONPATH uv run --no-sync python \
  tests/desktop/contracts/agent_persistence_probe.py
graphify update .
graphify diagnose multigraph --graph graphify-out/graph.json --undirected
```

结果：`150 passed`；Ruff/Pyright/锁检查全绿；Agent persistence source/schema/backup/log 命中均
为 0。Graphify 为 5551 nodes、16070 edges，2 个 unverified code nodes；missing、dangling、
self-loop、duplicate 和 collapsed 均为 0。

## 5. T057 单 turn 串行 Runtime loop

定向 RED：

```bash
uv run pytest -q --tb=short tests/desktop/application/test_agent_read_draft.py
```

结果：`8 failed`，全部因 `AgentRuntime` 仍是不可实例化的冻结 Protocol；没有 Provider、registry、
数据库或环境失败。

最小 GREEN 后同一文件 `8 passed`。结合 T049/T050/T054 与 runtime bridge 回归：

```bash
uv run pytest -q \
  tests/desktop/application/test_agent_read_draft.py \
  tests/desktop/contracts/test_agent_runtime_contract.py \
  tests/desktop/unit/test_agent_context.py \
  tests/desktop/unit/test_agent_runtime_values.py \
  tests/desktop/ui/test_runtime_bridge.py
```

结果：`41 passed`。证据覆盖：

- 全应用同一 Runtime 同时只接受一个 turn；第二个 turn 返回 `agent.operation_in_progress`。
- Provider 与 Tool 在一个 `RuntimeBridge(max_workers=1)` operation 内逐次串行；没有并行 Tool 或
  子 Agent。
- 每次 call 按本地 descriptor 的 name/Permission/关闭 Schema 检查；未知、伪造、越权和不匹配
  `ToolResult` fail closed。
- Tool call 数、Provider 文本长度和 turn 总时限均有本地上限；Provider refusal/非法结构只返回
  脱敏稳定错误码。
- 取消在 Provider 返回后、Tool 执行前再次检查；迟到结果由 cancellation token 和 operation ID
  丢弃，目标测试确认 registry calls 为空。
- DRAFT 结果在本地规范化为稳定 `PlanPatch`；两次参数键顺序不同仍得到同一 canonical SHA。
- Runtime 公共方法仍精确为 `start_turn/cancel/reject`，没有 Confirmation 或 WRITE 方法。

Runtime 不持有 Repository/Session；Provider 等待期间不存在数据库事务。生产 registry 的 READ
handler seam 由 composition root 注入短生命周期 Application callable，每次调用自行建立/关闭
所需 Session；DRAFT 只消费冻结 Context/arguments。

T057 完整验证：除尚未实现 T058 UI 外的桌面集 `158 passed`；全仓 Ruff format/lint、Pyright、
`uv sync --locked`、`uv lock --check` 全绿；Agent persistence source/schema/backup/log 命中均为
0。Graphify 更新为 5597 nodes、16212 edges，2 个 unverified code nodes；missing、dangling、
self-loop、duplicate 和 collapsed 均为 0。

## 6. T058 Agent 草案 UI

定向 RED：

```bash
uv run pytest -q --tb=short tests/desktop/ui/test_agent_draft_flow.py
```

结果：`8 failed`，全部为 `SLICE2B_RED`，唯一原因是
`kindergarten_manager.ui.widgets.agent_draft` 尚未实现。

最小 GREEN 后同一文件 `8 passed`，默认质量入口 `166 passed`。`AgentDraftPanel` 提供固定状态区、
当前 scope 的意图提交、取消、字段级只读 before/after 表和“丢弃草案”；运行期间禁用重复提交，
保留取消按钮。离开页面或关闭面板先取消当前 operation，再清空 patch 并使后续 refresh 永久忽略
迟到结果。

对“直接修改当前教案”和“以后总是允许直接修改”的定向测试均显示“当前阶段仅支持读取和草拟”，
没有调用 service；组件树中不存在 `confirm_agent_patch`、`always_allow_agent`、“确认写入”或
“总是允许”控件。

T058 完整验证：

```bash
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv sync --locked
uv lock --check
env -u PYTHONPATH uv run --no-sync python \
  tests/desktop/contracts/agent_persistence_probe.py
graphify update .
graphify diagnose multigraph --graph graphify-out/graph.json --undirected
```

结果：`166 passed`；Ruff/Pyright/锁检查全绿；Agent persistence source/schema/backup/log 命中均为
0。Graphify 为 5593 nodes、16222 edges，2 个 unverified code nodes；missing、dangling、
self-loop、duplicate 和 collapsed 均为 0。

## 7. T059 唯一 Runtime 组合根

固定实现基线 RED 探针：

```bash
git show HEAD:src/kindergarten_manager/app.py \
  | rg -n "AgentRuntime|build_read_draft_registry|OpenAICompatibleAgentProvider"
```

结果：退出码 `1`，固定基线组合根没有 Runtime、Provider Adapter 或 registry 装配。首次接入页面后，
现有组合/UI 回归进一步以 `10 failed, 9 passed` 证明旧服务替身不具备 Agent 端口时页面不能构造；
最小兼容修复后，生产服务具备 Agent 端口时才挂载面板，既有非 Agent 测试替身无需伪造运行时。

组合根只创建一个 `AgentRuntime` 和一个 `RuntimeBridge(max_workers=1)`。Provider Adapter 每次仅加载
当前启用配置并返回 Provider DTO，不持有 registry、executor 或 Tool callable。四个 READ handler
分别校验 Provider 参数必须等于当前 `ActiveScope`，并以各自 `with session_factory()` 短会话执行固定
`SELECT`；两个 DRAFT handler 只消费冻结 Context 与 arguments，生成字段级 Patch，不访问数据库。
退出顺序为失效 Context/Patch、停止单 Agent bridge、再停止既有 AI runtime；切换班级/日期也先失效并
取消当前 operation。没有子 Agent、并行 Tool、Provider 托管线程、WRITE 或 Confirmation 接口。

T059 验证：

```bash
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv sync --locked
uv lock --check
env -u PYTHONPATH uv run --no-sync python \
  tests/desktop/contracts/agent_persistence_probe.py
```

结果：`166 passed`；402 files formatted；Ruff lint 通过；Pyright `0 errors / 0 warnings /
0 informations`；锁定同步和锁检查通过。持久化探针区分数据库/Bootstrap 全量禁词扫描与组合根
持久化 sink 扫描，结果 source/schema/backup/log 命中均为 0。隔离 `XDG_DATA_HOME`、清除
`PYTHONPATH`、offscreen Qt 的 `python -I -m kindergarten_manager` 在 3 秒时仍处于事件循环（timeout
退出码 124）且只创建预期桌面 SQLite。

业务代码变更后执行 `graphify update .` 与 undirected multigraph diagnose：5617 nodes、16500
edges、2 个 unverified code nodes；missing、dangling、self-loop、duplicate 和 collapsed 均为 0。
7 个非代码配置源产生零节点的警告不影响代码增量图；HTML 因节点数超过 5000 按保护规则跳过。

## 8. T060 Slice 2B 综合验收

T049–T052、T058 UI 与默认质量入口矩阵：

```bash
uv run pytest -q \
  tests/desktop/contracts/test_agent_runtime_contract.py \
  tests/desktop/unit/test_agent_context.py \
  tests/desktop/application/test_agent_read_draft.py \
  tests/desktop/ui/test_runtime_bridge.py \
  tests/desktop/ui/test_agent_draft_flow.py \
  tests/desktop/packaging/test_default_quality_gate.py
```

结果：最终扩展矩阵 `60 passed`。Provider port 的公开注解只包含 Application DTO；具体 Adapter 构造参数只有
endpoint/key/model/transport/响应上限，源码没有 registry、executor、`.execute(` 或 `ToolResult`，
因此 Provider 只能返回 Tool call，不能执行 Tool。

Tool-only 越权矩阵全部 fail closed 且业务状态不变：

| 输入/事件 | 本地结果 | 写入结果 |
|---|---|---|
| 未知 `unknown.tool` | `agent.tool_not_allowed` | 0 |
| 未批准 `lesson_plan.write_current` / WRITE | registry 构造拒绝 | 0 |
| READ 名称伪造 DRAFT permission | `agent.tool_not_allowed` | 0 |
| 关闭 Schema 缺版本、开放额外字段或字段缺失 | descriptor/call 校验拒绝 | 0 |
| 第二个并发 turn | `agent.operation_in_progress` | 0 |
| 重复 Tool call 超过上限 | `agent.tool_call_limit` | 0 |
| Provider 文本超过上限 | `agent.response_too_large` | 0 |
| turn 总时限超过上限 | `agent.turn_timeout` | 0 |
| Provider refusal/非法结构 | 脱敏稳定错误码 | 0 |
| Provider 返回前取消 | 迟到结果丢弃，registry call 为 0 | 0 |
| 页面切换/关闭 | 取消并忽略迟到结果 | 0 |
| “直接修改”/“总是允许”意图 | UI 拒绝，无 service call | 0 |

运行时矩阵以同一个可变业务快照同时观察正文、`revision`、历史版本数、preview 数和 audit 数；所有
成功 READ/DRAFT 与所有负向路径前后完全相等。Runtime 只有单一 bridge worker，Provider/Tool 串行，
没有子 Agent、并行 Tool、长期 Agent 状态或 Provider 托管 thread。

零持久化探针：

```bash
env -u PYTHONPATH uv run --no-sync python \
  tests/desktop/contracts/agent_persistence_probe.py
```

结果：数据库/Bootstrap 全量禁词扫描 0；组合根 persistence sink 扫描 0；AST 固定 SQL 扫描同时
覆盖组合根 handler 与 Repository 的 `load_tool_*` 短 Session 实现，没有
INSERT/UPDATE/DELETE/DDL；SQLite forbidden 与 broad schema 命中均为空；
备份文件 0，日志文件 0。当前 Alembic revision 仍为 `0002_desktop_ai`、23 个 schema object，没有
Agent migration。因没有 Agent schema、文件或日志 sink，重启后没有可恢复的 Context、session、
conversation、message、ToolResult、PlanPatch 或 Provider transcript。

最终 Linux/静态质量入口：

```bash
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv sync --locked
uv lock --check
uv build --out-dir <temporary-directory>
```

结果：最终默认桌面测试 `178 passed`（`178 tests collected`），无 Cloud/PostgreSQL/Redis fixture、
环境或服务错误；Ruff format 403 files、lint、Pyright（0/0/0）、锁定同步与锁检查均通过。隔离源码启动探针进入 Qt 事件循环并
只创建预期 SQLite。临时目录构建成功产生 `child_manager-0.1.0-py3-none-any.whl` 与 sdist，wheel
包含五个 Agent 组合/Runtime/registry/Provider/UI 文件；构建物未写入仓库。

Windows 结果为**部分完成**：维护者已确认无需 `PYTHONPATH` 的源码启动、真实既有
`0001 -> 0002_desktop_ai` 迁移、保护副本、数据保留和重启通过；其余 Agent READ/DRAFT 行为仍
待按 `docs/implementation-evidence/desktop-slice-2b-windows-checklist.md` 手工执行。此处不以
Linux 结果替代未执行项目。

最终业务代码增量使用 `graphify update .`，文档语义抽取首选 OpenAI-compatible backend 并成功，
未触发 DeepSeek/`luna_worker` 降级。T060 验收抽取为 5663 nodes / 15999 edges / 343
communities；加入下一切片本地 Issue 草案后的交付图为 5664 nodes / 15998 edges / 342
communities，均有 2 个 unverified code nodes，且 missing、dangling、self-loop、duplicate 和
collapsed 均为 0。首次语义抽取报告 5 个跨文件误归因 code nodes 并按 fail-closed 规则丢弃，
没有写入图谱。

## 9. 回归修复与固定工作树 Review

以 Slice 2A 基线 `8d285f03616033e757ee1f31e298da6d58a3501b` 固定比较当前工作树，分别执行
Standards 与 Spec Review。首轮合并后确认五类合理问题：Context 未按意图最小化、Tool Schema 与
字段类型校验不完整、READ SQL 越过 Application seam、生产 UI 不自动观察后台完成、Context
失效与迟到结果存在竞态。

回归测试先形成可复现 RED：迟到草案未失效、Context loader 不接收当前意图、运行中的 UI 不自动
刷新；另补恶意参数/字段类型、完整正文绕过意图投影和 Repository SQL 扫描。修复后：

- `AgentContext` 只包含当前意图命中的注册栏目字段，`read_current` 也只能回送该投影；
- DRAFT 输入以关闭 `oneOf`、注册路径和字段关联类型 fail closed；Tool 输出同样校验；
- 四个 READ Tool 通过 `DailyPlanWorkspace` 调用 Repository 短 Session；
- UI 只在 operation 运行时以 100 ms Qt timer 刷新，完成或离页立即停止；
- Runtime 用 epoch 与 operation ID 原子检查拒绝切换、取消或退出后的迟到结果。

第三轮双轴复审结果：Standards `0 findings`，Spec `0 findings`，新增 smell `0`。最终固定实现提交
SHA 为 `a14a24dc65e3a535125b356b3d740c0062adf545`；证据提交 SHA 与精确 CI run/headSha 在提交、推送和远端验证完成后回填 Issue #20；本文不写
不可自证的“当前文件自身提交 SHA”。

回归修复和重大证据文档语义抽取后的最终图为 5691 nodes / 16217 edges / 342 communities，含
2 个 unverified code nodes；`graphify diagnose multigraph --graph graphify-out/graph.json
--undirected` 的 missing、dangling、self-loop、duplicate 和 collapsed 均为 0。语义抽取和社区
命名均由首选 OpenAI-compatible backend 成功完成（33967 input / 25527 output tokens），未触发
DeepSeek 或 `luna_worker` 降级。

## 10. Windows 启动与迁移修复交付

- 包安装与源码入口修复后，Windows 的 `uv sync --locked` 成功构建并安装本地
  `child-manager==0.1.0`；无需 `PYTHONPATH` 即进入桌面启动路径。
- `c2a22a2c9b3e7002b0fdd218239d29935f63cbe1` 将保护副本 `fsync` 改为可写描述符；
  Quality run [31603619776](https://github.com/ywyz/child-manager/actions/runs/31603619776) 为
  `completed/success`，但 Windows 实机继续发现未关闭 SQLite 连接阻止原子重命名。
- `7cf57cce3cda948d790121a169bef666a5f0370d` 显式关闭保护副本的 source、destination 与
  verification 连接；Quality run
  [31605026083](https://github.com/ywyz/child-manager/actions/runs/31605026083) 为
  `completed/success` 且精确匹配该 `headSha`。
- 修复前 Windows 只读检查证明数据库仍停在 `0001_desktop_initial`，关键表计数为
  `1/1/1/15`、正式保护副本为 0。维护者在最终修复后明确确认最近下发的源码启动、迁移保护、
  数据保留和重启复测全部通过。
- 后续 Windows 默认测试在 179 项中出现 1 项平台兼容失败：Git 将不可变迁移文件检出为 CRLF，
  原始字节哈希因此不同；将同一 LF 内容转换为 CRLF 可精确复现实机哈希，确认不是迁移内容被
  改写。`1bd441fde1c585a8aff5c3b20cea6b1aff621d9b` 增加 CRLF 回归并在哈希前只规范化
  `CRLF -> LF`，本地迁移、Bootstrap、完整桌面、Ruff 与 Pyright 均通过，仍待 Windows 重跑。
- 本节不把这项启动/迁移通过扩张为 Agent Provider、取消、迟到结果、最小 Context 或零写入
  等其余 Windows 项目通过，也不授权 PR、`main` 或 T061。
