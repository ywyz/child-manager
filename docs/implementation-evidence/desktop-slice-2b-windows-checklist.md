# Desktop Slice 2B Windows 手工验收检查表

状态：**部分完成**。2026-08-12 已由用户手工确认源码启动与 `0001 -> 0002` 迁移保护通过；
其余 Agent READ/DRAFT 行为仍待执行，本文不以 Linux 结果替代。

固定事实基线：

- docs SHA：`d4ac961a04a273a0384e295190296f69538b313b`
- dev 基线 SHA：`8d285f03616033e757ee1f31e298da6d58a3501b`
- Slice 2B 固定实现 SHA：`a14a24dc65e3a535125b356b3d740c0062adf545`
- Windows 启动/迁移修复 SHA：`7cf57cce3cda948d790121a169bef666a5f0370d`
- 修复 Quality CI：[31605026083](https://github.com/ywyz/child-manager/actions/runs/31605026083)，
  `completed/success`，精确匹配上述 SHA
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

2026-08-12 Windows 实测记录：

- `uv sync --locked`、`uv lock --check`、Ruff format/check 与 Pyright 通过；Pyright 为
  `0 errors, 0 warnings, 0 informations`。
- `uv run pytest -q` 为 `178 passed, 1 failed`。唯一失败是 `0001_desktop_initial.py` 的原始
  字节哈希在 Windows CRLF 检出下不同；CRLF 转换可精确复现实机哈希，排除迁移正文改写。
- 修复提交 `1bd441fde1c585a8aff5c3b20cea6b1aff621d9b` 增加 CRLF 回归，并仅在测试哈希入口规范化
  `CRLF -> LF`；该提交仍待 Windows 默认测试复验。
- `uv build --out-dir dist` 成功；uv `0.12.2` 对项目 `uv-build>=0.11.30,<0.12` 范围给出警告，
  但未阻止 wheel 与 sdist 生成。
- Windows 构建 SHA-256：wheel
  `F93694B92DAF0554061869476D2F7E3DC8F4DE8E336E898B646A920B7F2D94C0`；sdist
  `6382D59C63B1FEE251E51E9037962E506FFD8E971F3BE47349150739E2209EF2`。

## 2. 手工行为检查

- [x] `uv run python -m kindergarten_manager` 从源码正常启动，无 `PYTHONPATH` 绕过。
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

## 3. 启动与迁移保护结果

- [x] 真实既有 `0001_desktop_initial` 数据库在升级前生成并验证保护副本。
- [x] 活动库升级到 `0002_desktop_ai`，原有教师、学期、班级与 15 份教案保留。
- [x] 保护副本仍为 `0001_desktop_initial`，完整性与外键检查通过。
- [x] 关闭并重启后数据仍在，且不会为已经位于 `0002` 的数据库重复创建迁移保护副本。

修复前维护者提供的只读诊断输出确认活动库仍为 `0001`，关键表计数为 `1/1/1/15`，正式保护
副本为 0。最终修复后维护者明确回复“测试通过”；成功迁移的原始终端输出仍未提供，因此不在
本文补造。后续自动化输出和构建哈希已按第 1 节记录。该结果只覆盖最近下发的启动/迁移复测，
不自动勾选上节其余 Agent 行为。

## 4. 后续结果记录

请记录 Windows 版本、Python/uv 版本、上述命令原始结果、构建哈希、应用数据目录、截图或录像索引，
以及每个未通过项的稳定复现步骤。真实结果由用户填写；Linux/静态结果不得代替本表。
