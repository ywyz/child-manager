# 桌面默认门禁与旧 Cloud 退役候选工作包

> 状态：候选提案，未进入 `003-desktop-local-first/tasks.md` 的正式任务编号。
>
> 本文不授权实现，不改变 Issue #14 的 T001–T034，也不阻塞 T034 Windows 验收或
> T035–T040 Slice 2A clean RED。若维护者决定实施，必须先确认执行时点，再以新的完整 docs
> SHA 和独立 Issue 固定范围、非目标、验收与验证方式。

## 背景

`dev@cf106e44cb907a4958879a16ee061dccc8c2b1f9` 的 Quality CI 仍会运行旧 Web/API/Worker
测试；一次失败来自旧 Web Playwright 设置流程，原提交重跑后通过。这说明“当前桌面切片通过”
与“默认门禁已经完全退役旧 Cloud”是两个不同事实，后者不能通过改写既有 003 任务编号被
静默加入 Slice 1。

## 候选范围

| 候选项 | 内容 |
|---|---|
| CDR-01 | 将旧 calendar/content 中仍适用于桌面的教学周、四季、正文结构与校验断言迁入 `tests/desktop`，只面向 `kindergarten_manager.domain`。 |
| CDR-02 | 将供应商中立的 AI 结果 Schema、规范 JSON、栏目 hash 和冻结输入 hash 断言迁入桌面测试，排除 Job、API、身份、园所和 PostgreSQL 语义。 |
| CDR-03 | 迁移仍适用的 Word 模板段落、标题、强调、错误拒绝和确定性 DOCX fixture 断言，不迁入 HTTP、Worker 或导出 Store。 |
| CDR-04 | 只为上述行为证据补齐最小纯领域规则，不复制旧 ContractModel、tenant、Provider、Job 或 Agent 编排。 |
| CDR-05 | 评估并收敛默认 Pytest/Pyright 范围与正式依赖；任何依赖移除都必须重新生成 `uv.lock` 并证明桌面回归完整。 |
| CDR-06 | 评估把 Quality workflow 收敛为桌面默认门禁；如保留 legacy workflow，只能手工触发、非 required，并固定历史提交。 |
| CDR-07 | 记录收集/通过数量、依赖树、默认 CI 服务、零长期 skip 和 legacy 退出条件。 |
| CDR-08 | 在固定实现提交上独立执行 Standards/Spec Review，确认没有丢失适用行为，也没有迁入 Web/API/Worker/PostgreSQL 语义。 |

## 决策边界

- 不把 CDR-01–CDR-08 插入既有 T034 之前，也不重编号 T035–T124。
- 不因旧 Cloud 测试仍存在，就否定已经按 Issue #14 验收的桌面 Slice 1 行为。
- 不把一次旧 Web 测试抖动等同于桌面产品回归。
- 是否在 Slice 2A 之前、之后或发布收敛阶段实施，必须由独立 Issue 决定。
