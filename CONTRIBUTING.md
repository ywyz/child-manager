# Child Manager 贡献指南

本项目采用文档优先、Issue 驱动和单实现开发。Codex 是当前唯一实现者；产品目标、技术基线和业务不变量不因开发工具变化而改变。

## 1. 开始工作前

按以下顺序阅读：

1. `AGENTS.md`：安全、修改边界、Git 与验证规则。
2. `README.md` 与 `CONTEXT.md`：项目概览、当前状态和下一步。
3. `docs` 分支中当前任务对应的 PRD、ADR、架构、规格、OpenAPI 契约和模板。
4. GitHub Issue：本次范围、非目标、验收标准和固定的 `docs` 提交 ID。
5. 实现相关迁移、测试和局部 `AGENTS.md`。

文档之间存在冲突时，停止会固化冲突的实现并请求确认。

## 2. 分支职责

| 分支 | 职责 | 允许的主要变更 |
| --- | --- | --- |
| `main` | 稳定版本与发布基线 | 经完整测试和 Review 的 `dev` 结果、发布记录 |
| `docs` | 文档和稳定契约的单一事实来源 | 根目录治理文件、`.github/ISSUE_TEMPLATE/`、`.specify/memory/constitution.md`、`.specify/templates/`、`docs/`、`specs/`、OpenAPI 契约、`templates/`、生成的 `graphify-out/` |
| `dev` | 唯一实现与集成分支 | Python、Alembic、NiceGUI、测试、依赖锁及已确认文档同步 |

禁止直接在 `main` 进行临时开发；禁止在 `docs` 提交业务代码、迁移、实现测试或依赖锁。

## 3. Design → Implement

```text
需求提出
  -> docs 编写或修订 PRD / ADR / Architecture / Contract
  -> 人工确认并固定 docs commit
  -> 创建 GitHub Issue
  -> Codex 在 dev 实现
  -> 测试与 Review
  -> 合并 main 并回填 Issue
```

实现过程中发现需求缺口时，先暂停受影响实现，回到 `docs` 完成确认，再更新 Issue 的文档基线。不得修改文档来迁就已经写出的代码。

## 4. Issue 要求

实现 Issue 必须包含：

- 固定的 `docs` 提交 ID 和直接文档链接。
- 用户可观察目标、范围与非目标。
- 可执行验收标准和负向场景。
- 数据库、权限、园所隔离、安全、UI、Worker、Word 与文档影响。
- 测试计划、标准质量命令和未执行项说明。

没有满足上述要求的 Issue 不进入实现。

## 5. 提交、验证与 Review

- 提交保持单一目的，使用 Conventional Commits，主题中文优先。
- 修复缺陷先增加能够复现问题的测试。
- 先运行相关快速测试，再运行风险相称的完整门禁。
- 不删除、跳过或放宽断言来制造通过结果。
- Review 同时检查代码标准和 Issue/文档符合度。
- 未经明确授权，不提交、推送、合并、创建 Pull Request 或改写历史。

实现分支标准命令：

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

涉及迁移、OpenAPI、Redis、浏览器、Word 或其他高风险边界时，还必须运行对应专项检查。

## 6. 发布与历史

只有 `dev` 对齐已确认 `docs` 基线、全部必要门禁通过且 Review 完成后，才能合并到 `main`。发布记录应固定源码、文档和 Issue 证据。

旧 Codex/Trae 双实现分支、Issue 和审查报告属于历史审计材料，不构成当前开发流程，也不得被改写为从未发生。
