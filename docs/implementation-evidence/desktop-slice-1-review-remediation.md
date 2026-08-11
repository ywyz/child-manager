# 桌面 Slice 1 双轴 Review 修复证据

日期：2026-08-11

## 固定提交角色

- docs 基线：`fff6e0908fcb591c927205d53cdbacd35037bce3`
- 原始 Slice 1 实现锚点：`cf106e44cb907a4958879a16ee061dccc8c2b1f9`
- 初始 docs-only 收口：`b53c1c43c69e3ae3058d74b6163ecfc2bd7d4e95`
- Review 修复锚点：`7af4d46f1114616eb798e5991805a164026c63df`
- 新固定 Review SHA：由包含本文、任务状态与 Graphify 同步的后继 docs-only 收口提交确定。

`cf106e44...` 仍是完整 Slice 1 功能实现锚点；`7af4d46...` 只修复首次双轴 Review 发现的产品
显示名偏差，并增加对应公开窗口接口断言。

## 首次双轴 Review 结论

固定 Review SHA `b53c1c43...` 的 Standards 与 Spec 两轴各报告 1 个同源阻断 finding：

- `src/kindergarten_manager/ui/main_window.py` 把主窗口标题设置为“幼儿园一日活动计划”。
- 宪章 4.1.0 与 ADR-0012 冻结产品显示名为“幼儿园管理助手”。
- 判断性 code smell 为 0；其余 T001–T034 未发现缺失、越界或表面实现问题。

## TDD 修复证据

公开验证 seam 为 `create_desktop_window(...).windowTitle()`。

1. 只增加标题断言后运行组合根测试：1 failed；实际值为“幼儿园一日活动计划”，期望值为
   “幼儿园管理助手”。
2. 只把 `DesktopMainWindow` 标题改为冻结显示名后重跑同一测试：1 passed。
3. `uv run pytest tests/desktop --quiet`：65 passed。
4. `uv run ruff format --check .`：370 files already formatted。
5. `uv run ruff check .`：All checks passed。
6. `uv run pyright`：0 errors / 0 warnings / 0 informations。

本地完整 `uv run pytest` 正常收集 794 项，但仓库外 PostgreSQL `127.0.0.1:15432` 未运行，
产生 282 个数据库 setup errors 和 1 个依赖健康检查失败；其余 511 项通过。尝试按正式 Dev
档位启动 Compose 时，当前用户无权访问 `/var/run/docker.sock`，因此不把该结果当作代码失败，
也不把本地完整套件声称为通过。

## 精确远端 CI

Review 修复锚点的 GitHub Actions Quality 证据为
[run 31450912844 attempt 1](https://github.com/ywyz/child-manager/actions/runs/31450912844)：

- `status=completed`
- `conclusion=success`
- `run_attempt=1`
- `headSha=7af4d46f1114616eb798e5991805a164026c63df`
- Ruff format：370 files already formatted
- Ruff check：All checks passed
- Pyright：0 errors / 0 warnings / 0 informations
- Pytest：794 passed / 1 warning

## Graphify 辅助验证

常规 `graphify update .` 曾错误移除 plan/spec/checklist 的 43 个文档语义节点，因此该结果被
拒绝并从 Git 基线恢复。随后只对两个真实改动 Python 文件运行 Graphify AST extractor，并用
`build_merge` 受控替换来源；与初始收口图相比没有丢失旧节点，最终为 4926 nodes、14161 edges、
24 hyperedges，目标代码与测试来源均存在。`graphify diagnose multigraph --undirected` 的
missing endpoint、dangling endpoint、self-loop、exact duplicate 和 collapsed edge 均为 0。

Graphify 只提供导航和辅助一致性证据；最终完成权仍由固定 SHA 的测试、双轴 Review、Windows
手工验收和 Issue 门禁共同决定。

## 当前门禁

下一步只允许把本证据、任务状态和 Graphify 生成物封存为新的 docs-only Review SHA，并在该
固定 SHA 上重新执行 Standards/Spec 双轴 Review。双轴均通过前不得合并 `main`；合并 SHA 的
Quality CI 完成且成功前不得关闭 Issue #14，也不得进入 Slice 2A。
