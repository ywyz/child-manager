# 桌面 Slice 1 手工 MVP RED 证据

日期：2026-08-09

## 固定基线与授权

- 分支：`dev`
- 当前提交：`ba9251d2ee74c8959ea53e888cd5a030571fdc69`
- docs 基线：`eaee3592aedeef6a01f8c11d2df2c977489828ef`
- Issue：https://github.com/ywyz/child-manager/issues/14
- 当前授权：补齐公共 seam tracer tests，重新取得干净 RED；完成 Standards/Spec 双轴 Review 后
  创建本地 RED 检查点，再执行 T019–T033 GREEN，并在本地全绿和第二次 Review 后提交、推送与
  等待 CI。
- 独立门禁：T034 仍由未参与实现的 Windows 验收参与者完成；T035 以后、PR 与 `main` 集成不在
  当前执行范围，T034 通过后的下一实施切片必须先是 Slice 2A。

正式桌面代码位于 `src/kindergarten_manager/`。可丢弃的
`apps/desktop/prototype_daily_plan.py` 未复制、移动、导入或进入测试夹具。

## 环境

- CPython：3.14.6
- uv：0.11.30
- PySide6 / Qt：6.11.1 / 6.11.1
- SQLAlchemy：2.0.51
- Alembic：1.19.0
- 平台：Linux offscreen；本证据不替代 Windows 验收。

`uv sync --locked` 成功解析 121 个锁定包并建立 Python 3.14.6 环境。

## Foundation 门禁

执行：

```bash
uv run pytest \
  tests/desktop/test_fixtures.py \
  tests/desktop/contracts/test_architecture_boundaries.py \
  tests/desktop/unit/test_application_dto.py \
  tests/desktop/ui/test_runtime_bridge.py
uv run ruff format --check .
uv run ruff check .
uv run pyright
```

结果：

- Foundation：14 collected / 14 passed。
- Ruff format：355 files already formatted。
- Ruff check：All checks passed。
- Pyright：0 errors / 0 warnings / 0 informations。
- 架构门禁真实扫描 `src/kindergarten_manager`，禁止旧 Web/API/Worker、`packages`、
  FastAPI/NiceGUI/PostgreSQL/Redis/Dramatiq 运行时依赖，并验证 UI/Application/Domain 方向。

## 强制 collect-only

执行：

```bash
uv run pytest --collect-only tests/desktop
```

结果：49 collected，退出码 0。没有 import、fixture、Qt、模板、SQLite、数据库配置或其他环境
收集错误。其中 14 项是已通过的 Foundation 测试，35 项是 T011–T017 及其公共 seam tracer 的
Slice 1 行为测试。

另执行 `uv run pytest --collect-only --quiet` 对整个仓库收集：778 collected，退出码 0；旧 Cloud
测试也未因本次桌面测试环境隔离产生收集错误。旧 PostgreSQL 测试仍只在实际运行相关 fixture
时要求仓库外的测试数据库配置，不计入本轮 RED。

## Slice 1 RED

执行：

```bash
uv run pytest \
  tests/desktop/unit/test_paths.py \
  tests/desktop/application/test_bootstrap.py \
  tests/desktop/database/test_engine.py \
  tests/desktop/database/test_migrations.py \
  tests/desktop/database/test_settings_repository.py \
  tests/desktop/application/test_settings_service.py \
  tests/desktop/unit/test_content.py \
  tests/desktop/unit/test_calendar.py \
  tests/desktop/application/test_lesson_plan_service.py \
  tests/desktop/database/test_lesson_plan_repository.py \
  tests/desktop/contracts/test_word_single_export.py \
  tests/desktop/ui/test_first_run_daily_plan_flow.py \
  tests/desktop/integration/test_composition_root.py --tb=short
```

结果：35 collected / 35 failed / 0 errors。每项失败均由测试辅助函数标记为 `SLICE1_RED`，只指向
T019–T033 尚未实现的公开行为：

| 行为组 | 失败数 | 未实现任务 |
|---|---:|---|
| 数据路径 | 1 | T019 |
| 启动与数据库状态拒绝 | 4 | T024 |
| SQLAlchemy Session 工厂与 SQLite PRAGMA | 1 | T021 |
| SQLite 迁移与不可变版本 | 2 | T023–T024 |
| SQLite 设置持久化、唯一性与原子区域替换 | 1 | T025–T026 |
| 首次设置与事务回滚 | 6 | T026 |
| 结构化教案内容 | 3 | T020 |
| 教学周、日期、季节与工作日软提示 | 3 | T020 |
| 教案应用服务 | 2 | T027 |
| SQLite 教案 Repository | 2 | T025 |
| 单日 Word 冻结快照、完整映射/模板、稳定失败、重开校验与原子发布 | 6 | T028–T029 |
| 首次设置到保存/重启/覆盖确认/导出 UI 闭环及唯一 composition root | 4 | T030–T033 |

总计：35。首次复跑曾因新的 `data/` 层级暴露 3 个测试准备目录缺失，修正 fixture 后重新执行
collect-only 和完整 RED；最终不存在通过捕获 import、fixture 或环境异常伪装的 RED。辅助函数
只捕获明确的 `NotImplementedError`，任何其他异常都会按测试错误直接暴露。

第一轮 Standards/Spec Review 没有放行：Standards 轴指出一个未使用的 RED 专用异常类型，Spec
轴指出 SQLite 设置持久化、独立 Alembic 闭包、Word 失败语义和真实 composition root tracer
不足。后续 Review 又指出 Word 成功样本未真正满足重开结构/日期校验、旧 Renderer 字段映射不全，
以及单日结果缺少 `skipped=()`。现已删除死类型并补齐全部上述公共 seam 契约；本节的 49/35 数字
和命令均来自最终补强后的重新执行，仍须双轴复审通过才可创建 RED 检查点。

## 额外完整性检查

- `templates/teacherplan/teacherplan.docx` SHA-256：
  `72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043`，未修改。
- 测试资料均为“测试教师”“星河幼儿园”“向日葵班”等虚构内容。
- 桌面测试通过 autouse fixture 禁止包括回环地址在内的真实网络访问。
- 最终补强公共 seam tracer 后重新执行 `graphify update .`：4693 nodes / 13479 edges / 265 communities；
  `graphify diagnose multigraph --graph graphify-out/graph.json --undirected` 报告缺失端点、悬空边、
  自环、精确重复边和有向/无向端点折叠均为 0。
- 当前 `dev` 只保留未提交本地变更；未执行 commit 或 push。

## 停止边界

本证据只证明 Slice 1 测试接口已正常收集并得到干净 RED，不证明手工 MVP 已实现。当前下一门禁
是对 `dev@ba9251d2ee74c8959ea53e888cd5a030571fdc69` 到本工作树执行 Standards/Spec 双轴只读
Review；前序发现已在测试/接口范围内整改，只有最终双轴复审通过才创建本地 RED 检查点并
执行 T019–T033。T034 Windows 独立人工验收
继续单列，且不得跳过 Slice 2A 直接进入 Agent Foundation。
