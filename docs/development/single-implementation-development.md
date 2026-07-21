# Child Manager 单实现开发协议

文档版本：v1.0

状态：已确认

日期：2026-07-21

适用对象：Codex、维护者与审阅者

## 1. 目的

本文定义 `main`、`docs`、`dev` 三条长期分支的职责，以及文档优先、Issue 驱动、Design → Implement、验证、Review 和发布流程。Codex 负责唯一代码实现，不再维护 Trae 独立开发线。

本次调整只改变开发治理，不改变 Python 3.14+、NiceGUI、FastAPI、PostgreSQL、Service Layer、Cloud Only、幼儿园教育管理系统和教案管理首发模块等产品与技术目标。

## 2. 事实来源

1. `AGENTS.md`：开发、安全、Git、修改边界与验证规则。
2. `docs` 分支中的 PRD、ADR、Architecture、Context、Development Guide、共享规格、OpenAPI 契约和模板：产品与设计的单一事实来源。
3. GitHub Issue：执行范围、状态、阻塞与验收证据。
4. `main`：最近一个稳定版本的代码和对应文档快照。
5. `dev` 的代码、迁移、测试和 CI：当前已实现行为的证据，但不能自行推翻已确认文档。

来源冲突时按 `AGENTS.md` 暂停受影响实现并请求确认。

## 3. 分支模型

| 分支 | 责任 | 禁止 |
| --- | --- | --- |
| `main` | 稳定版本、发布基线、版本标签 | 临时开发、未验收提交、直接实验 |
| `docs` | PRD、Architecture、ADR、Context、Development Guide、Spec Kit 宪章/模板、`specs/`、OpenAPI、`templates/`、生成的 `graphify-out/` | 业务代码、迁移、实现测试、依赖锁 |
| `dev` | Codex 唯一实现与集成；Python、迁移、UI、测试、依赖锁 | 无 Issue 开发、绕过文档改需求、未经验证发布 |

`docs` 从 `main` 继承稳定代码快照是正常的，但每个 `docs` 提交必须通过路径门禁，证明没有修改业务实现。

三条长期分支均禁止强制推送和无归档删除。`main` 只接受完成完整门禁和 Review 的 `dev` 结果。

## 4. 文档流程

需求先进入 `docs`：

1. 编写或修订 PRD，明确目标、用户、范围、非目标和验收结果。
2. 涉及跨模块、数据、安全、外部契约或难以逆转选择时新增或更新 ADR/Architecture。
3. 同步 `specs/`、OpenAPI 和模板，避免设计与可执行契约分离。
4. 执行链接、格式、契约和交叉一致性检查。
5. 人工确认后形成单一目的提交，记录精确提交 ID。

README 只提供产品概览和稳定状态导航；CONTEXT 记录当前交接；Roadmap 记录里程碑与门禁。可变执行状态保存在 GitHub Issue，不在多个文档复制流水账。

## 5. Issue 驱动实现

正式实现 Issue 必须固定引用已确认的 `docs` 提交，而不是只写 `docs` 分支。Issue 至少包含：

- 用户可观察目标、范围、非目标。
- PRD、ADR、Architecture、契约和模板链接。
- 可执行验收标准、失败路径和安全边界。
- 数据库、API、UI、Worker、Word 和文档影响。
- RED 测试、最小实现、专项验证与完整门禁。

缺少文档基线或验收标准时，Issue 只能保持设计状态，不得开始业务实现。

## 6. Codex 实现

1. 在 `dev` 开始前核对分支、HEAD、工作区和 Issue 文档基线。
2. 给出简短计划，为每一步定义验证方式。
3. 缺陷修复和业务规则优先使用测试驱动开发。
4. 只修改 Issue 必需内容，不顺手建设未来模块或重构无关代码。
5. 发现共享设计缺口时暂停受影响实现，先回到 `docs` 处理。
6. 完成后运行相关快速测试、专项验证和标准完整门禁。

## 7. Review 与发布

Review 同时检查：

- Standards：是否遵守仓库开发、安全、隔离、测试和维护性规则。
- Spec：是否符合 Issue 固定的 PRD、ADR、Architecture、契约和验收标准。

Review 发现可复现缺陷时回到 `dev` 修复并重新验证；发现设计冲突时回到 `docs`。所有必需门禁通过后，才可将 `dev` 合并到 `main`，记录发布提交/标签并回填 Issue。

## 8. 历史双实现退役

`docs/development/dual-agent-development.md`、历史 Issue 草稿、审查报告和原 Trae 分支只作为历史审计材料。Trae 最终提交通过归档标签保留，原分支删除；历史未通过最终独立验收的结果不得改写为 `completed`。
