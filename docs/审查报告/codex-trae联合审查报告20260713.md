# Child Manager 编码前联合审查报告（Codex + Trae）

> 审查日期：2026-07-13  
> 报告性质：Codex 与 Trae 编码前审查的合并定稿  
> 事实基线：以 `docs/faq/combined-audit.md` 及其引用的 canonical 文档为准  
> 操作边界：本报告不授权编码、创建或切换分支、提交、推送、创建 Issue、Pull Request 或改写 Git 历史。

## 1. 联合结论

**当前不能进入编码，也不应发布 M1 实现 Issue 任务列表。**

两份原审查报告已经在核心决策、主要阻断项、M0 门禁状态和解锁顺序上完成收敛。项目的业务规格、实现计划和任务覆盖已经足够详细；当前阻塞不在任务数量，而在 M0 共享基线尚未形成一致、可信、可重复验证的完成证据。

可以准备 Issue 草稿，但在 M0-G1～M0-G8 全部关闭前，不应创建 M1 实现子 Issue、执行 T003 或开始 T004 之后的代码任务。

## 2. 当前文档与已满足规则

### 2.1 文档状态

| 文档类型 | 文件路径 | 当前判断 |
| --- | --- | --- |
| 规格文档 | `specs/001-daily-activity-plan/spec.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| 实现计划 | `specs/001-daily-activity-plan/plan.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| 任务清单 | `specs/001-daily-activity-plan/tasks.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| 数据模型 | `specs/001-daily-activity-plan/data-model.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| OpenAPI 契约 | `specs/001-daily-activity-plan/contracts/openapi.yaml` | 文件已存在、结构基本完备、待 M0 收敛 |
| 状态机契约 | `specs/001-daily-activity-plan/contracts/job-state-machine.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| 系统架构 | `docs/design/system-architecture.md` | 文件已存在、结构基本完备、待 M0 收敛 |
| 交叉审计结论 | `docs/faq/combined-audit.md` | 当前唯一有效的审计事实基线 |

### 2.2 已确认满足的规则

- AES-256-GCM、随机 96 位 nonce、AAD 和密钥轮换边界已经进入开发规则和数据模型。
- `expired` 已进入任务状态机。
- `retry_of_job_id` 已定义为独立的同园组合自外键。
- 首期时区固定为只读 `Asia/Shanghai`。
- `before_restore`、`restored` 已在数据模型中定义。
- 当前 Word 模板已经脱敏，SHA-256 为 `72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043`，固定引用一致。
- `ai_generation_results` 已明确完整结果最多保留 30 天；采用后可清理正文，但保留必要任务、模型、提示词、Schema、哈希和审计元数据。该项符合 Q8，不是遗漏。

## 3. M0 阻断项

以下事项均须处理；不使用“低优先级”表达，避免误解为可以跳过。

### 3.1 模型与契约

1. `spec.md` FR-031 只描述“带原因的完整快照”，尚未明确完整原因码：
   - `manual_save`
   - `ai_adopted`
   - `archive`
   - `unarchive`
   - `before_restore`
   - `restored`
2. `docs/design/system-architecture.md` 尚未概括并引用 Q13 的完整客户端幂等定义：园所、操作者、HTTP 方法、规范化路由模板和 key 构成 scope；请求 fingerprint 另含规范化实际 path、业务 query 与 canonical JSON body。

### 3.2 模板说明

`templates/teacherplan/一日活动计划系统说明.md` 尚有以下漂移：

- 节假日服务仍使用旧 HTTP 地址，未同步为 `https://timor.tech/api/holiday/info/{YYYY-MM-DD}`。
- 集体活动仍使用 `[[字段名]]` 文本标记，未明确新增环节由 `is_ai_added=true` 表达，正文不得写入“新增”等标记文字。
- 反思仍使用旧字段和 `[[...]]` 标记，未同步 `highlights`、`issues`、`adjustments` 及中文三行映射。
- 未明确三个反思值分别执行 Unicode NFKC 规范化后拼接，按完整 Unicode 码点计数；空格、标点和 emoji 均计入，合计不得超过 200。
- 仍保留 `U+0000–U+FFFF` 及超出范围可能截断或替换的 BMP 旧规则，与完整 Unicode 和 emoji 支持冲突。

### 3.3 状态、证据与分支流程

- `spec.md` 标记为 `Ready for Implementation`，`plan.md` 声称只剩分支授权；Roadmap 和 `combined-audit.md` 明确 M0 仍为 `in_progress`，CONTEXT 与 Tasks 也保留尚未完成的同步步骤和过时流程。各文件的状态语义与证据必须统一。
- T002 仍使用提交 `56cc5e2` 的旧审查证据，不能证明当前文档基线通过最终门禁。
- T003 仍要求选择单一实现分支并 cherry-pick 旧基线，与当前双 Agent 协议冲突。
- 正确流程是：M0 完成并形成最终 docs-only `main` 基线后，经明确授权从同一提交创建 `codex` 和 `trae`，记录相同基线提交 ID；后续新的共享文档提交才分别在授权后 cherry-pick。

### 3.4 静态验证、图谱、历史与最终基线

- README 的 OpenAPI 与契约说明链接错误指向根目录 `contracts/`，当前本地链接门禁失败。
- 文档修订后必须重新验证本地链接、模板结构/样式/哈希和 Spec Kit 一致性。
- graphify 必须在最终文档修订后再次更新和诊断；仅刷新本报告不能提前关闭 M0-G6。
- 当前模板文件已脱敏，但早期模板仍可从 Git 历史访问。历史隐私清理属于独立高风险操作，必须另行授权并验证本地、远程、分支和标签状态。
- 前述门禁未关闭，最终单一目的 docs-only `main` 共享基线尚未形成。

## 4. M0 门禁最终判断

| 门禁 | 当前判断 | 主要原因 |
| --- | --- | --- |
| M0-G1 模型与契约一致 | 未关闭 | FR-031 原因码缺失；系统架构未概括并引用 Q13 客户端幂等定义 |
| M0-G2 模板说明一致 | 未关闭 | 反思字段、结构化标记、NFKC、码点、200 限制、HTTPS 和 BMP 规则存在漂移 |
| M0-G3 模板脱敏与哈希一致 | 当前满足，待复核 | 当前模板已脱敏且固定哈希一致；结构/样式随 G5 复核，历史问题归入 G7 |
| M0-G4 范围与状态一致 | 未关闭 | Roadmap、CONTEXT、Spec、Plan、Tasks 的状态语义、证据和分支流程不一致 |
| M0-G5 静态一致性验证 | 未关闭 | 已发现两个 README 失效链接；修复后还需复核模板结构、样式和哈希 |
| M0-G6 知识图谱一致 | 未关闭 | 最终文档修订后必须重新更新、查询和诊断 |
| M0-G7 历史隐私清理 | 未关闭 | 旧模板历史仍可访问，需独立授权清理并复核全部历史引用 |
| M0-G8 共享基线形成 | 未关闭 | 前置门禁未完成，当前 HEAD 不能作为最终冻结基线 |

## 5. Spec Kit 与 Issue 组织判断

机械覆盖结论沿用双方已核验结果：

- 功能需求 72 项，编号连续，均有任务映射。
- 成功标准 17 项，编号连续，均有任务映射。
- 任务 T001～T165 编号连续、无重复。
- T002 虽已勾选，但其审查证据已经过期，必须在最终基线上重新复核。
- 任务覆盖率只表示计划已经映射需求，不表示功能已实现或 M0 已通过。

M1 进入 `ready` 后，Issue 应按里程碑和可验证纵向切片组织，不机械创建 165 个 Issue：

```text
M<n> 共享父 Issue
├── M<n> Codex 实现子 Issue
└── M<n> Trae 实现子 Issue
```

## 6. 建议解锁顺序

1. 修订模板说明：同步三字段反思、结构化新增标志、NFKC、完整 Unicode 码点、合计 200、HTTPS 地址，并删除 `[[...]]` 和 BMP 旧规则。
2. 在 FR-031 明确完整快照原因码及 `before_restore`、`restored` 恢复顺序。
3. 在系统架构概括并引用 Q13 客户端幂等 scope 与 fingerprint 定义。
4. 修复 README 的两个契约链接。
5. 统一 `combined-audit.md`、Roadmap、CONTEXT、Spec、Plan 和 Tasks 的状态语义、日期、门禁证据与下一步。
6. 重写 T002/T003，删除旧证据和初始 cherry-pick 流程。
7. 重新执行文档链接、模板结构/字体/字号/段落/换行/哈希和 Spec Kit 一致性检查。
8. 更新、查询并诊断 graphify；清理临时产物。
9. 经单独明确授权执行 Git 历史隐私清理，并验证本地、远程、分支和标签状态。
10. 经授权形成最终单一目的 docs-only `main` 基线提交，将 M0 标记为 `complete`、M1 标记为 `ready`。
11. 经再次授权从同一最终提交创建 `codex`、`trae`，记录相同基线提交 ID。
12. 建立 M1 共享父 Issue、Codex 实现子 Issue和 Trae 实现子 Issue，再分别进入独立实现。

## 7. 最终决策与授权边界

当前决策为：**不允许进入编码，不发布 M1 实现 Issue，不执行 T003。**

M0 内容门禁与后续操作授权必须分开：完成 M0 不自动授权提交、历史改写、分支或 Issue 操作。历史清理、最终基线提交和实现分支操作仍须分别获得用户明确授权。

本报告合并后，原 Codex、Trae 阶段性报告不再作为独立当前依据；后续审查统一引用本文和 `docs/faq/combined-audit.md`。
