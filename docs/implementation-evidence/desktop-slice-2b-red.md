# 桌面 Slice 2B clean RED 证据

## 1. 固定范围

- 执行 Issue：[Issue #20](https://github.com/ywyz/child-manager/issues/20)
- 完整 docs SHA：`d4ac961a04a273a0384e295190296f69538b313b`
- 实现基线：`8d285f03616033e757ee1f31e298da6d58a3501b`
- Slice 2A 远端 CI：run `31472760153`，`headSha` 与实现基线一致且结论为
  `success`。
- 2026-08-11 的直接授权依次覆盖 T050、T051、T052，并由 T053 汇总；T049 是进入
  本轮前已有的本地 RED。
- 本证据只覆盖 T049–T053。T054–T060 GREEN、Review、commit、push、Issue 写入和
  `main` 集成都未获授权。

## 2. 先收集

进入 T050 前先对包含 T049 的仓库执行：

```bash
uv run pytest --collect-only -q
```

结果：`858 tests collected in 5.16s`，collection 无 fixture、数据库、网络或环境错误。

完成 T050–T052 后，按 T053 精确收集四个文件：

```bash
uv run pytest --collect-only -q \
  tests/desktop/contracts/test_agent_runtime_contract.py \
  tests/desktop/unit/test_agent_context.py \
  tests/desktop/application/test_agent_read_draft.py \
  tests/desktop/ui/test_agent_draft_flow.py
```

结果：`41 tests collected in 0.11s`。分布如下：

- T049 Agent Runtime 契约：13 项；
- T050 最小 `AgentContext`：12 项；
- T051 READ/DRAFT Tool loop：8 项；
- T052 Agent 草稿 UI：8 项。

再次执行完整仓库收集，结果为 `889 tests collected in 4.94s`；相对进入 T050 前新增
31 项：T050–T052 新增 28 项，并按 Review 补齐 T049 对 `output_schema` 的 3 项对称约束。

## 3. clean RED

```bash
uv run pytest -q --tb=short \
  tests/desktop/contracts/test_agent_runtime_contract.py \
  tests/desktop/unit/test_agent_context.py \
  tests/desktop/application/test_agent_read_draft.py \
  tests/desktop/ui/test_agent_draft_flow.py
```

结果：`41 failed in 0.17s`。全部失败均由测试转换为稳定 `SLICE2B_RED` 断言，当前直接
原因仅为以下计划中的公开模块尚未实现：

- `kindergarten_manager.application.agent_runtime`；
- `kindergarten_manager.ui.widgets.agent_draft`。

没有用 skip、fixture 失败、数据库失败、网络失败、环境失败或放宽断言制造 RED。T051 使用
`ScriptedProvider`，没有访问真实或付费 AI；T052 使用内存服务替身，没有启动后台线程或写入
业务数据。

## 4. 行为边界

- T050 固定 `AgentContext` 十个字段，要求实体 revision 与事实匹配且均不可变；上下文到期或
  班级/学期/教案/日期 scope 切换后失效。
- T049 对 `input_schema` 与 `output_schema` 使用同一组版本化、顶层关闭约束；T050 断言
  `ActiveScope` 与 `ContextFact` 自身不可变，并拒绝 `ContextFact.value` 内嵌 dict/list/set/
  bytearray 等可变对象，避免只冻结顶层 dataclass。
- T050 明确拒绝 API Key、绝对路径、无关班级和完整历史进入 facts，并验证 repr 与结构化日志
  不显示事实值。
- T051 覆盖单 Agent、READ 后 DRAFT、稳定 `PlanPatch` 哈希、Tool 调用数、Provider 响应长度、
  turn 总时限、Provider 拒绝/结构错误和取消；每条路径都断言正文、revision、历史版本、AI
  preview 和审计计数不变。行为测试只调用冻结的 `start_turn/cancel`，并通过 Qt runtime 的
  `succeeded/failed/finished` 信号观察结果；构造、固定时钟和限制集中在
  `tests/desktop/application/agent_runtime_harness.py` 测试内部装配 seam，不扩展公共契约。
- T052 只展示字段级只读草案；重复 turn 被阻止，可取消；页面切换/关闭后迟到结果不回填；
  “直接修改”和“以后总是允许”均没有 WRITE/Confirmation 入口。

## 5. 无 Agent 状态持久化扫描

仓库内只读验证脚本为
`tests/desktop/contracts/agent_persistence_probe.py`。从仓库根目录执行的精确命令为：

```bash
env -u PYTHONPATH PYTHONPATH=src uv run --no-sync python \
  tests/desktop/contracts/agent_persistence_probe.py
```

其中 `env -u PYTHONPATH PYTHONPATH=src` 显式建立与当时 Pytest 相同、且不继承调用者
`PYTHONPATH` 的 RED 测试导入环境；`--no-sync` 保证探针不改变锁定环境。脚本使用标准库
`TemporaryDirectory(prefix="child-manager-agent-probe-")` 创建并自动清理隔离根目录，在其中构造
`DesktopPaths`、执行 `BootstrapService.start()`，只读取生成的 SQLite schema、备份目录和日志
目录。

源码扫描路径固定为：

```text
src/kindergarten_manager/infrastructure/database
src/kindergarten_manager/application/bootstrap.py
src/kindergarten_manager/app.py
```

探针对上述数据库模型、Repository、迁移和桌面启动代码扫描下列稳定标识：

```text
agent_context, agent_session, conversation, agent_message, tool_result,
plan_patch, agent_patch, context_fact, entity_revision, provider_transcript
```

源码扫描结果：`agent_persistence_source_hits=0`。

另在隔离临时目录启动当时的桌面 SQLite，扫描 `sqlite_master` 中全部表、索引、触发器、定义
以及每张表的 `PRAGMA table_info` 字段，再递归枚举备份目录和日志目录。在这个 RED 检查点，
`pyproject.toml` 仍为 `[tool.uv] package = false`，所以该结果只证明 T053 的持久化边界，不作为
源码启动验收证据；后续修复与隔离启动记录在
`docs/implementation-evidence/desktop-non-windows-blockers.md`。完整结果：

```text
import_mode=explicit-src-test-harness
temporary_root=stdlib.TemporaryDirectory
source_paths=src/kindergarten_manager/infrastructure/database,src/kindergarten_manager/application/bootstrap.py,src/kindergarten_manager/app.py
agent_persistence_source_hits=0
source_hit_details=[]
schema_revision=0002_desktop_ai
sqlite_schema_objects=23
forbidden_persistence_hits=[]
broad_forbidden_schema_hits=[]
backup_files=0
log_files=0
```

其中 broad schema 扫描额外使用 `conversation`、`thread`、`message`、`vector`、
`agent_context`、`agent_patch` 和 `plan_patch`；均无表、索引、触发器或字段命中。源码中的
普通异常构造参数 `message` 不属于持久化结构，未被误报为 Agent 记忆。

直接运行 `uv run python` 的首次扫描在导入业务包前即因
`No module named 'kindergarten_manager'` 退出，未计入上述通过结果；既有源码启动阻塞仍然存在，
本轮没有越权修改打包配置。

## 6. 回归与质量门禁

排除四个预期 RED 文件后执行现有桌面测试：

```bash
uv run pytest -q tests/desktop \
  --ignore=tests/desktop/contracts/test_agent_runtime_contract.py \
  --ignore=tests/desktop/unit/test_agent_context.py \
  --ignore=tests/desktop/application/test_agent_read_draft.py \
  --ignore=tests/desktop/ui/test_agent_draft_flow.py
```

结果：`119 passed in 6.44s`。

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

结果：395 files already formatted；Ruff All checks passed；Pyright 0 errors / 0 warnings /
0 informations。

## 7. 停止边界

- T049–T053 已完成并标记；T054 与后续任务保持未勾选。
- 当前仅包含 RED 测试、证据、任务状态和工具生成的图谱变更；没有 Agent GREEN 业务实现。
- 本地变更未提交、未推送；RED Review、commit、push、Issue 更新和进入 T054–T060 均需要
  后续独立授权。
