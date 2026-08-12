# 桌面非 Windows 阻塞收口证据

## 1. 范围与停止边界

- 2026-08-12，维护者明确保留全部 Windows 验收为手工门禁，并授权先解决其余阻塞。
- 本轮处理默认质量门禁的旧 Cloud/PostgreSQL/Redis 依赖、源码启动复验、既有桌面 QA
  复验和现场 Word 重号；不进入 T055。
- `specs/003-desktop-local-first/tasks.md` 保持 T054 已完成、T055–T060 未勾选。
- 没有提交、推送、创建 PR、更新 Issue 或切换分支。

## 2. 既有桌面 QA 复验

当前实现已经在首次设置和设置页使用可编辑 `QDateEdit` 保存学期起止日期；周工作台按布局 C
保留顶部周带、左侧当天栏目、中央编辑区和右侧可选 AI 面板。集体活动按“主题/准备、目标、
重点/难点、过程”排列，过程表最小高度 260 px 并在中央滚动区扩展。

在 `QT_QPA_PLATFORM=offscreen` 下创建 1366×768 窗口、切换 `section_nav_4` 并抓取窗口，观察到
中央集体活动编辑区约占主工作区三分之二；对照
`docs/design/assets/desktop-prototype/desktop-prototype-c-collective.png`，信息架构和内容优先级一致。
截图只写入 `/tmp/child-manager-collective-linux.png`，没有进入仓库。

可执行回归：

```bash
uv run pytest -q \
  tests/desktop/ui/test_first_run_daily_plan_flow.py::test_first_run_collects_minimum_settings_and_opens_structured_editor \
  tests/desktop/ui/test_first_run_daily_plan_flow.py::test_daily_plan_uses_week_workspace_and_gives_collective_activity_room \
  tests/desktop/ui/test_first_run_daily_plan_flow.py::test_settings_page_changes_theme_and_current_semester_without_restarting \
  tests/desktop/integration/test_composition_root.py::test_composition_root_persists_first_daily_plan_across_restart_and_exports_word \
  tests/desktop/contracts/test_word_single_export.py::test_snapshot_is_frozen_and_renderer_preserves_template_contract \
  tests/desktop/contracts/test_word_single_export.py::test_area_game_lists_render_one_numbering_layer_without_numbered_labels
```

结果：`7 passed in 2.61s`。Windows 字体、原生日期控件和 Word 分页仍由维护者手工验收。

## 3. Word 活动过程重号

首次渲染带序号的活动过程输入得到 `1.1.师...`、`2.2、幼...`，证明普通列表已有的输入序号
规范化没有覆盖 `group_activity.process[].lines`。新增同一 `render_day` seam 的参数化测试后，修复前
结果为 `1 failed, 1 passed`；修复将普通列表和活动过程统一通过同一 `_LIST_PREFIX` 规范化，
不修改 `templates/teacherplan/teacherplan.docx`。

```bash
uv run pytest -q \
  tests/desktop/contracts/test_word_single_export.py::test_group_process_renders_one_numbering_layer
uv run pytest -q tests/desktop/contracts/test_word_single_export.py
```

结果：参数化重号用例 `2 passed`，Word 契约文件 `10 passed in 0.93s`。

按文档验收技能使用仓库内确定性探针生成包含 `1.`、`1．`、`1、` 混合输入的 DOCX，再执行：

```bash
CHILD_WORD_ROOT=$(mktemp -d /tmp/child-manager-word-fixed.XXXXXX)
uv run python tests/desktop/contracts/word_numbering_probe.py \
  "$CHILD_WORD_ROOT/numbering-fixed.docx"
uv run --with pdf2image python \
  /home/admin/.codex/plugins/cache/openai-primary-runtime/documents/26.805.11740/skills/documents/render_docx.py \
  "$CHILD_WORD_ROOT/numbering-fixed.docx" \
  --output_dir "$CHILD_WORD_ROOT/rendered" --emit_pdf
```

结果：生成 4 张页面 PNG 和非空 PDF；逐页检查无重号、文字截断、表格重叠或边框破坏。模板自身
另行渲染为 5 页，确认输出分页差异来自填充固定模板而不是模板被覆盖；模板哈希继续由契约测试
固定为 `72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043`。

## 4. 默认 Cloud 门禁退役

先增加 `tests/desktop/packaging/test_default_quality_gate.py`，修复前稳定失败于
`testpaths = ["tests"]`。收敛后：

- Pytest 默认只发现 `tests/desktop`，并以 `--confcutdir=tests/desktop` 阻止父级旧 Cloud
  `tests/conftest.py` 顶层导入 `psycopg`；桌面自己的禁网、固定数据和 Qt offscreen 夹具继续生效。
- Pyright 默认只检查 `src/kindergarten_manager` 与 `tests/desktop`。
- Quality CI 不再创建 PostgreSQL/Redis service，不再安装 Playwright 或验证旧 OpenAPI。
- 移除只服务于退役 Cloud/Web/API/Worker/Auth 测试的直接依赖；保留桌面计划明确需要的
  PySide6、SQLite/SQLAlchemy/Alembic、python-docx、日历、Provider、keyring、cryptography
  和未来备份适配器依赖。`uv tree --depth 1` 的锁定解析从 121 个包收敛到 52 个包。
- 旧 Cloud 源码和测试文件未删除；若需要考古，应在固定历史提交和独立环境中执行，不再把它们
  当作桌面产品的默认完成证据。

门禁契约：

```bash
uv run pytest -q tests/desktop/packaging/test_default_quality_gate.py
uv sync --locked
uv lock --check
```

结果：契约 `1 passed`，锁定同步与锁检查通过。

## 5. 当前测试边界

```bash
uv run pytest --collect-only -q
```

结果：`166 tests collected in 0.91s`，无 fixture、数据库、网络或环境收集错误。

排除仍明确属于 T055–T058 的四个 clean RED 文件运行当前稳定桌面集：

```bash
uv run pytest -q \
  --ignore=tests/desktop/contracts/test_agent_runtime_contract.py \
  --ignore=tests/desktop/unit/test_agent_context.py \
  --ignore=tests/desktop/application/test_agent_read_draft.py \
  --ignore=tests/desktop/ui/test_agent_draft_flow.py
```

结果：`125 passed in 7.67s`。

直接运行默认入口：

```bash
uv run pytest -q --tb=short
```

结果：`145 passed, 21 failed in 7.90s`。21 项全部是已审阅的 `SLICE2B_RED`：Provider port/
adapter、Tool registry、Runtime loop 和 Agent 草稿 UI 尚待 T055–T058；没有 PostgreSQL、Redis、
Playwright、旧 Cloud fixture 或依赖导入失败。它们是下一阶段的计划工作，不是环境阻塞。

## 6. 源码启动与静态质量

```bash
uv run pytest -q tests/desktop/packaging
env -u PYTHONPATH \
  XDG_DATA_HOME="$CHILD_START_ROOT/data" \
  XDG_CACHE_HOME="$CHILD_START_ROOT/cache" \
  QT_QPA_PLATFORM=offscreen \
  timeout 3s uv run --no-sync python -I -m kindergarten_manager
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

结果：打包契约 `3 passed`；隔离启动返回预期 timeout `124`，此前已生成
`data/cn.kindergartenmanager.desktop/data/child-manager.sqlite3`，证明已进入 Qt 事件循环而不是导入
失败；Ruff format、Ruff lint 和 Pyright 均通过（0 errors / 0 warnings）。

## 7. 剩余门禁

- 非 Windows 环境与依赖阻塞已清除。
- T055 是下一段持续推进的首个实现任务；T055–T060 完成前，21 项 clean RED 按设计保留。
- 固定提交后的 Standards/Spec Review、CI、commit/push/Issue 更新，以及全部 Windows 手工验收
  仍是独立后续门禁。

## 8. 2026-08-12 后续状态更新

本文件第 1–7 节是进入 T055 前的历史检查点，不再代表当前 `dev` 状态。随后 T055–T060、
双轴 Review、提交、推送和精确 Quality CI 已完成；Windows 源码启动与真实
`0001 -> 0002_desktop_ai` 迁移保护也已由维护者在
`dev@7cf57cce3cda948d790121a169bef666a5f0370d` 上确认通过。其余 Agent READ/DRAFT Windows
行为仍见 `desktop-slice-2b-windows-checklist.md` 的未勾选项；Issue #20、`main` 和 T061 不因
本补充验收自动完成或获得授权。
