# Repository Workflow Reset（2026-07-21）

状态：已确认并执行

## 1. 决策

项目停止 Codex/Trae 双 AI 平行开发，采用：

- `main`：稳定版本与发布基线。
- `docs`：PRD、Architecture、ADR、Context、Development Guide、`specs/`、OpenAPI 契约和 `templates/` 的单一事实来源。
- `dev`：Codex 负责的唯一实现与集成分支。

开发固定遵循 `需求 -> docs -> Issue -> dev -> 测试 -> Review -> main`。

## 2. 不变目标

- Python 3.14+
- NiceGUI Web 与 FastAPI API
- PostgreSQL、SQLAlchemy 2.x 与 Alembic
- Service Layer 与明确服务边界
- Cloud Only
- 幼儿园教育管理系统
- 教案管理作为首个业务模块

## 3. 迁移基线

- 迁移前 `main`：`ac0a17d80470347706bad349bf759a46f8202ce2`。
- 新 `docs`：从该 `main` 基线建立，再提交本次治理更新。
- 新 `dev`：从历史 Codex `ca2d3937dbd0a58ce0b425361f1f51feff86a29c` 建立，再同步已确认的 `docs`。
- 历史 `codex`：只作为迁移来源，不再接受新开发；是否删除另行授权。

当前 `main` 仍是迁移前 docs-only 基线。`dev` 完成当前文档同步、完整验证和 #4 Review 前，不把它升级为稳定应用基线。

## 4. Trae 归档

- 最终提交：`2023d9ea68de9a87501437335a6589e65ed057ff`。
- 归档标签：`archive/trae-m2-20260721`。
- 历史 Issue：#6 以 `not planned` 关闭，不标记为完成。
- 标签经远端解析验证后删除 `trae` 分支。

归档保留提交、Issue、评论和审查证据。Trae 最终提交在流程重置前申请了再次复核，但没有取得绑定该 HEAD 的最终独立 PASS；不得在历史记录中补写为已验收。

## 5. M2 Issue

- #5：保留为历史 Codex M2 实现与验收证据。
- #6：保留为历史 Trae 实现记录，以 `not planned` 关闭。
- #4：由双实现共享父 Issue 改为 `dev` 单实现验收入口。

#4 只有在 `dev` 对齐当前 `docs`、完成标准质量命令和 M2 专项门禁、通过 Review 后才能关闭。
