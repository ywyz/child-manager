# Desktop Slice 2B Windows 手工验收检查表

状态：**待用户在 Windows 手工执行**。本文不记录或暗示任何 Windows 已通过结果。

固定事实基线：

- docs SHA：`d4ac961a04a273a0384e295190296f69538b313b`
- dev 基线 SHA：`8d285f03616033e757ee1f31e298da6d58a3501b`
- 实现范围：T054–T060 与 Review 回归修复；固定提交 SHA 由 Issue #20 的最终证据填写
- Python：3.14；依赖来源：`pyproject.toml` 与 `uv.lock`

## 1. 可复现构建

在本工作树根目录执行：

```powershell
uv sync --locked
uv lock --check
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv build --out-dir dist
Get-FileHash dist\child_manager-0.1.0-py3-none-any.whl -Algorithm SHA256
Get-FileHash dist\child_manager-0.1.0.tar.gz -Algorithm SHA256
```

Linux 可复现构建已确认 wheel 同时包含 `app.py`、`agent_runtime.py`、`agent_tools.py`、
`agent_provider.py` 和 `agent_draft.py`。Windows 应记录其本机构建哈希，不要求与另一平台的压缩包
哈希相同。

## 2. 手工行为检查

- [ ] `uv run python -m kindergarten_manager` 从源码正常启动，无 `PYTHONPATH` 绕过。
- [ ] 一日活动计划页面可见 Agent 意图区、非阻断状态、取消和“丢弃草案”。
- [ ] Agent 结果只显示字段级 before/after 草案；不存在“确认写入”“总是允许”或任何直接写入控件。
- [ ] 输入“直接修改当前教案”或“以后总是允许直接修改”时明确拒绝，正文与 revision 不变。
- [ ] Agent 运行时再次提交会被拒绝；取消后不出现迟到 Tool 结果或草案。
- [ ] Provider 等待期间切换班级/日期、离开页面或关闭窗口后，不显示迟到结果。
- [ ] 重启应用后不恢复 Agent 会话、意图、Context、Provider transcript、ToolResult 或 PlanPatch。
- [ ] Agent READ/DRAFT 前后，正文、revision、历史版本、AI preview、audit 数量不变。
- [ ] SQLite schema 不存在 agent/session/conversation/message/context/patch/vector 等表或列。
- [ ] Agent 操作不触发备份；日志不含 Context fact value、正文、Provider 原文、密钥或 Patch 内容。
- [ ] 默认 `uv run pytest -q` 不要求 PostgreSQL、Redis、Cloud 环境变量或网络服务。
- [ ] 仅提及晨间谈话的意图不会把反思、集体活动等无关正文发送给 Provider。
- [ ] Agent 完成后草案自动显示，不需要切换页面或手工刷新。
- [ ] 切换班级/日期恰逢 Provider 返回时，旧 turn 不会重新出现草案。

## 3. 结果记录

请记录 Windows 版本、Python/uv 版本、上述命令原始结果、构建哈希、应用数据目录、截图或录像索引，
以及每个未通过项的稳定复现步骤。真实结果由用户填写；Linux/静态结果不得代替本表。
