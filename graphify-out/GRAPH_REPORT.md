# Graph Report - /home/admin/code/child-manager-docs-auth  (2026-08-01)

## Corpus Check
- 7 files · ~92,717 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 431 nodes · 387 edges · 101 communities (25 shown, 76 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 50 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- 核心架构决策
- 规格驱动工具链
- M6交接状态
- Word导出验收
- 开发流程治理
- 项目技术架构
- M0门禁收敛
- M7导出规格
- M7任务序列
- 规格公共脚本
- Word导出实现
- 备用登录设计
- M6验收基线
- 文档审计查询
- 教案异步契约
- 身份安全边界
- 项目开发宪章
- 分支协作流程
- 功能分支脚本
- 教案基础数据表
- 园所隔离数据表
- 备用登录规格
- 导出下载权限
- 里程碑迁移顺序
- Word模板结构
- AI任务结果表
- AI模型档案
- 提示词版本表
- 用户角色表
- 前置条件脚本
- 计划初始化脚本
- 任务初始化脚本
- 教案接口契约
- 账号邀请表
- 账号恢复请求表
- 年龄段表
- AI生成结果表
- AI模型能力表
- AI模型档案表
- 审计事件表
- 后台任务表
- 备用认证凭据表
- 备用认证登记表
- 首位管理员初始化表
- 班级区域表
- 班级教师关联表
- 班级表
- 教案导出记录表
- 教案历史快照表
- 一日活动计划表
- 身份核验批准表
- 快照审计不可变性
- JSONB模式版本
- 园所数据隔离
- 幼儿园表
- 教案来源表
- 提示词定义表
- 提示词测试记录表
- 提示词版本表
- 恢复码表
- 刷新令牌表
- 角色表
- 学期表
- 用户角色关联表
- 用户表
- WebAuthn挑战表
- WebAuthn凭据表
- 工作日缓存表
- 账号邀请表
- 账号恢复请求表
- 审计事件表
- 备用认证凭据表
- 备用认证登记表
- 首位管理员初始化表
- 班级区域表
- 内容JSONB边界
- 教案作者关联表
- 教案导出记录表
- 教案历史快照表
- 身份核验批准表
- 教案来源表
- 提示词测试记录表
- 恢复码表
- 刷新令牌表
- 学期表
- WebAuthn挑战表
- WebAuthn凭据表
- 工作日缓存表
- 应用事务边界
- 外部密钥来源
- Pytest测试框架
- 开发质量门禁
- 项目治理规则
- 技术安全约束
- 教案规格检查
- WebAuthn注册选项
- CSRF令牌接口
- 存活健康检查
- 就绪健康检查
- WebAuthn认证

## God Nodes (most connected - your core abstractions)
1. `AGENTS.md Rules Document` - 19 edges
2. `T127–T141固定顺序` - 16 edges
3. `Architecture Decision Index` - 11 edges
4. `M7 ready` - 11 edges
5. `M6 complete` - 7 edges
6. `Speckit Tasks` - 6 edges
7. `单一实现开发协议` - 6 edges
8. `历史合并审查` - 6 edges
9. `安全威胁模型` - 6 edges
10. `Backup Login Implementation Plan` - 6 edges

## Surprising Connections (you probably didn't know these)
- `一日活动计划需求面` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_020708_请根据现有文档_和旧仓库的文件思考如何撰写_docs_prd_lesson_management_m.md → docs/faq/combined-audit.md
- `ADR 直接文件核对` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_025449_哪些关键架构决策需要独立_adr_哪些已经确认_决策之间有什么依赖.md → docs/faq/combined-audit.md
- `校正后的数据模型边界` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md → docs/faq/combined-audit.md
- `Speckit Tasks to Issues` --semantically_similar_to--> `Implementation Issue Template`  [INFERRED] [semantically similar]
  .agents/skills/speckit-taskstoissues/SKILL.md → .github/ISSUE_TEMPLATE/implementation.yml
- `Retired Dual Agent Protocol` --semantically_similar_to--> `Design to Implement Workflow`  [INFERRED] [semantically similar]
  docs/development/dual-agent-development.md → CONTRIBUTING.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **M6完成证据集合** — docs_roadmap_m6_complete, docs_roadmap_m6_exit_gate, docs_roadmap_us4_us5_complete, docs_roadmap_tests_graphify_pass, docs_roadmap_dual_axis_review_pass, docs_roadmap_main_beb8784, docs_roadmap_issue_11_completed [EXTRACTED 1.00]
- **M7就绪与解锁动作** — docs_roadmap_m6_complete, docs_roadmap_main_beb8784, docs_roadmap_us6_design, docs_roadmap_template_hash, docs_roadmap_t127_t141, docs_roadmap_acceptance_commands, docs_roadmap_m7_ready, docs_roadmap_new_immutable_docs_sha, docs_roadmap_m7_us6_issue [EXTRACTED 1.00]
- **M7固定Word导出与历史实现组成** — docs_roadmap_m7_word_export_history, docs_roadmap_word_export_record, docs_roadmap_export_task, docs_roadmap_missing_columns_soft_confirmation, docs_roadmap_immutable_lesson_context, docs_roadmap_template_copy_formatting, docs_roadmap_atomic_export_storage, docs_roadmap_authorized_download_history [EXTRACTED 1.00]
- **最终 main 稳定基线证据组合** — specs_001_daily_activity_plan_plan_final_main_beb8784, specs_001_daily_activity_plan_plan_review_pass [EXTRACTED 1.00]
- **M6 complete 固定证据集** — specs_001_daily_activity_plan_plan_issue_11, specs_001_daily_activity_plan_plan_m6_completion_rationale, specs_001_daily_activity_plan_plan_m6_complete, specs_001_daily_activity_plan_plan_final_main_beb8784 [EXTRACTED 1.00]
- **M7 Word 导出验收流** — specs_001_daily_activity_plan_quickstart_m7_ready, specs_001_daily_activity_plan_quickstart_export_presave, specs_001_daily_activity_plan_quickstart_missing_fields_confirmation, specs_001_daily_activity_plan_quickstart_atomic_export_freeze, specs_001_daily_activity_plan_quickstart_export_fidelity, specs_001_daily_activity_plan_quickstart_authorized_export_history [EXTRACTED 1.00]
- **M6 完成证据解锁 M7 Ready** — specs_001_daily_activity_plan_spec_m6_complete_evidence, specs_001_daily_activity_plan_spec_final_main_beb8784_baseline, specs_001_daily_activity_plan_spec_m7_ready, specs_001_daily_activity_plan_tasks_m6_exit_complete, specs_001_daily_activity_plan_tasks_final_main_beb8784_quality_evidence [INFERRED 0.95]
- **US6 T127-T141 RED 到 GREEN 到 Exit Gate** — specs_001_daily_activity_plan_tasks_m7_us6_scope, specs_001_daily_activity_plan_tasks_t127_t132_red_tests, specs_001_daily_activity_plan_tasks_t133_t140_green_implementation, specs_001_daily_activity_plan_tasks_t141_us6_exit_gate [EXTRACTED 1.00]
- **Development Technology Stack** — python, postgresql, nicegui, fastapi, redis, worker [INFERRED 0.75]
- **Git Branching Model** — docs_directory, apps_web, apps_api [INFERRED 0.75]
- **Documentation and Specification Sources** — readme, context, docs_directory, specs_directory, openapi_contracts, templates_directory [INFERRED 0.75]
- **Tables Implementing Kindergarten Isolation** — docs_design_database_schema_users, docs_design_database_schema_webauthn_credentials, docs_design_database_schema_webauthn_challenges, docs_design_database_schema_backup_auth_credentials, docs_design_database_schema_backup_auth_enrollments, docs_design_database_schema_bootstrap_initializations, docs_design_database_schema_account_invitations, docs_design_database_schema_recovery_codes, docs_design_database_schema_account_recovery_requests, docs_design_database_schema_identity_verification_approvals, docs_design_database_schema_user_roles, docs_design_database_schema_refresh_tokens, docs_design_database_schema_age_groups, docs_design_database_schema_classes, docs_design_database_schema_class_teachers, docs_design_database_schema_semesters, docs_design_database_schema_class_areas, docs_design_database_schema_ai_model_profiles, docs_design_database_schema_ai_model_profile_capabilities, docs_design_database_schema_prompt_definitions, docs_design_database_schema_prompt_versions, docs_design_database_schema_prompt_test_runs, docs_design_database_schema_daily_activity_plans, docs_design_database_schema_daily_activity_plan_authors, docs_design_database_schema_daily_activity_plan_snapshots, docs_design_database_schema_lesson_plan_sources, docs_design_database_schema_background_jobs, docs_design_database_schema_ai_generation_results, docs_design_database_schema_daily_activity_plan_exports, docs_design_database_schema_workday_cache, docs_design_database_schema_audit_events [EXTRACTED 1.00]
- **Tables Involved in Authentication Flow** — docs_design_database_schema_users, docs_design_database_schema_webauthn_credentials, docs_design_database_schema_webauthn_challenges, docs_design_database_schema_backup_auth_credentials, docs_design_database_schema_backup_auth_enrollments, docs_design_database_schema_refresh_tokens [INFERRED 0.80]
- **Lesson Planning System Tables** — docs_design_database_schema_daily_activity_plans, docs_design_database_schema_daily_activity_plan_authors, docs_design_database_schema_daily_activity_plan_snapshots, docs_design_database_schema_lesson_plan_sources [INFERRED 0.80]
- **Identity and Authentication System** — docs_design_data_model_kindergartens, docs_design_data_model_users, docs_design_data_model_webauthn_credentials, docs_design_data_model_webauthn_challenges, docs_design_data_model_backup_auth_credentials, docs_design_data_model_backup_auth_enrollments, docs_design_data_model_bootstrap_initializations, docs_design_data_model_account_invitations, docs_design_data_model_recovery_codes, docs_design_data_model_account_recovery_requests, docs_design_data_model_identity_verification_approvals, docs_design_data_model_roles, docs_design_data_model_user_roles, docs_design_data_model_refresh_tokens, docs_design_data_model_audit_events, docs_design_data_model_kindergarten_isolation, docs_design_data_model_immutability [EXTRACTED 1.00]
- **Core Principles of Constitution** — specify_memory_constitution_principle_1, specify_memory_constitution_principle_2, specify_memory_constitution_principle_3, specify_memory_constitution_principle_4, specify_memory_constitution_principle_5, specify_memory_constitution_principle_6 [EXTRACTED 1.00]
- **Governance Framework** — specify_memory_constitution_constitution, specify_memory_constitution_technical_constraints, specify_memory_constitution_development_workflow, specify_memory_constitution_governance [EXTRACTED 1.00]
- **Speckit Full SDD Lifecycle** — _agents_skills_speckit_specify_skill_speckit_specify, _agents_skills_speckit_plan_skill_speckit_plan, _agents_skills_speckit_tasks_skill_speckit_tasks, _agents_skills_speckit_implement_skill_speckit_implement [EXTRACTED 1.00]
- **Web API Worker Boundary Alignment** — docs_adr_adr_0002_separate_web_api_worker_modular_monolith_modular_monolith, docs_adr_adr_0002_separate_web_api_worker_modular_monolith_service_boundaries, docs_design_system_architecture_modular_runtime_architecture, docs_design_system_architecture_trust_starts_at_api [INFERRED 0.95]
- **M0 收敛证据链** — docs_faq_combined_audit_m0_gate_framework, docs______20260713________m0_gate_closure_evidence, docs______20260713____________final_docs_baseline [INFERRED 0.85]
- **身份纵深防御** — docs_security_threat_model_restricted_public_entry, docs_security_threat_model_phishing_resistant_authentication, docs_security_threat_model_password_totp_backup, docs_security_threat_model_emergency_recovery_dual_control [EXTRACTED 1.00]
- **Password and TOTP Backup Login Baseline** — specs_002_password_totp_backup_login_spec_backup_login_feature, specs_002_password_totp_backup_login_plan_backup_login_implementation_plan, specs_002_password_totp_backup_login_data_model_backup_auth_data_model, specs_002_password_totp_backup_login_contracts_openapi_backup_login_api_fragment, specs_002_password_totp_backup_login_tasks_backup_login_task_plan [EXTRACTED 1.00]

## Communities (101 total, 76 thin omitted)

### Community 0 - "核心架构决策"
Cohesion: 0.08
Nodes (34): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+26 more)

### Community 1 - "规格驱动工具链"
Cohesion: 0.07
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+25 more)

### Community 2 - "M6交接状态"
Cohesion: 0.09
Nodes (28): CONTEXT, 固定新的immutable docs SHA驱动M7 US6, Issue #11 completed并关闭, M6 complete，T087–T126 已完成并集成 main, M7 ready, 最终基线理由：M6 Review结果、T126、状态文档和语义图谱已收敛，且同headSha Quality run通过, Quality run 30631050997 attempt 2 同 headSha 全部通过, M7验收命令已冻结 (+20 more)

### Community 3 - "Word导出验收"
Cohesion: 0.09
Nodes (22): 固定 Word 模板 teacherplan.docx, 导出事务冻结的不可变上下文与正文输入, M7 门禁：固定模板导出及历史下载保真, 模板 SHA-256 72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043, 验证顺序：每个故事先失败测试，再最小实现，相关快速测试后执行完整门禁, 验证顺序理由：先证明当前纵向切片的失败和最小通过行为，再用完整质量命令与 Graphify 更新检查跨故事影响, Word 导出, Word 保真理由：模板漂移由固定哈希和单元格及样式断言阻止，导出使用不可变输入和独立副本避免后续教案修改或重复下载改变既有结果 (+14 more)

### Community 4 - "开发流程治理"
Cohesion: 0.10
Nodes (21): M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线, 阶段授权分离, M2 Issue 执行记录, M2 RED-GREEN 顺序, 设计到主分支门禁流 (+13 more)

### Community 5 - "项目技术架构"
Cohesion: 0.11
Nodes (20): AGENTS.md Rules Document, AI Generation, Alembic, apps/api/ Directory, apps/web/ Directory, CONTEXT.md, docs/ Directory, FastAPI API (+12 more)

### Community 6 - "M0门禁收敛"
Cohesion: 0.11
Nodes (19): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+11 more)

### Community 7 - "M7导出规格"
Cohesion: 0.18
Nodes (18): 首期一日活动计划完整闭环规格, 最终 main@beb8784 稳定基线, M6 T087-T126 完成证据, M7 Word 导出里程碑 Ready, M7 Ready 不等于 Word 导出已实现, US6 固定 Word 导出与历史下载, 导出历史下载实时授权, Word 导出事务性不可变快照 (+10 more)

### Community 8 - "M7任务序列"
Cohesion: 0.12
Nodes (17): 同步最终main和docs后进入M7 T127, T127, T127–T141固定顺序, T128, T129, T130, T131, T132 (+9 more)

### Community 9 - "规格公共脚本"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 10 - "Word导出实现"
Cohesion: 0.13
Nodes (16): 临时文件、刷盘、哈希校验和原子改名的导出存储缝隙, 成功记录保存文件大小、文件哈希、模板哈希和导出时间, API校验权限和教案版本后创建后台导出任务, Worker使用不可变教案上下文, 重复导出产生独立记录和存储键, M7固定Word导出与历史, 前五个关键栏目缺失时软确认，反思为空不触发确认, 原子改名后数据库失败的重试补偿或孤儿清理 (+8 more)

### Community 11 - "备用登录设计"
Cohesion: 0.14
Nodes (16): Password and TOTP Backup Login API Fragment, Backup Enrollment and Authentication Endpoints, Backup Authentication Security Event Endpoint, Backup Authentication Data Model, Encrypted Credentials and Enrollments, Session Assurance and TOTP Replay Protection, Backup Login Implementation Plan, Identity Deep Module Reuse (+8 more)

### Community 12 - "M6验收基线"
Cohesion: 0.19
Nodes (14): Implementation Plan：首期一日活动计划完整闭环, 最终稳定基线 main@beb8784cd5dd5cb2f1ddd39a46f7d0bff0ab3098, Issue #11：M6 T087–T126, M6 complete, M6 完成依据：US4 T087–T110、US5 T111–T126 和 T126 独立验收完成；dev@32d3c102 的完整 Quality、49 项设置测试、56 项 US5 测试、666 项完整 pytest、恶意样本临时残留为 0、Graphify 诊断和双轴 Review 均通过, M7 就绪依据：M6 已完成并集成至最终 main 稳定基线，固定 headSha 的 Quality 和 Standards/Spec Review 均通过, M7 ready, main@b7676c27 → dev@d654b704 Standards/Spec 双轴 Review PASS (+6 more)

### Community 13 - "文档审计查询"
Cohesion: 0.17
Nodes (13): AI 密钥安全边界, 权威模型与契约收敛, 客户端幂等作用域, 历史合并审查, M0 收敛门禁框架, Word 模板隐私与历史清理, 旧设计不具权威性, 一日活动计划 PRD 查询 (+5 more)

### Community 14 - "教案异步契约"
Cohesion: 0.17
Nodes (13): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, API v1 Contract, Optimistic Lock and Idempotency Contract, Trusted NiceGUI BFF Boundary, Daily Activity Plan Data Model (+5 more)

### Community 15 - "身份安全边界"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 16 - "项目开发宪章"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 17 - "分支协作流程"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 19 - "教案基础数据表"
Cohesion: 0.50
Nodes (4): Age Groups Table, Class Teachers Table, Classes Table, Daily Activity Plans Table

### Community 20 - "园所隔离数据表"
Cohesion: 0.50
Nodes (4): Composite Foreign Keys Concept, Kindergarten Isolation Concept, Kindergartens Table, Users Table

### Community 21 - "备用登录规格"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 22 - "导出下载权限"
Cohesion: 0.67
Nodes (3): API鉴权下载且导出历史可重新下载, 使用虚构数据完成docx浏览器导出与重新下载冒烟, 跨园、未关联班级教师和无权用户禁止下载

### Community 23 - "里程碑迁移顺序"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

### Community 24 - "Word模板结构"
Cohesion: 0.67
Nodes (3): AI-Added Step Red Text, Structured Daily Activity Sections, Daily Activity Plan Word Layout

## Knowledge Gaps
- **178 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+173 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **76 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `M7 ready` connect `M6交接状态` to `M7任务序列`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `最终稳定基线 main@beb8784cd5dd5cb2f1ddd39a46f7d0bff0ab3098` connect `M6验收基线` to `M6交接状态`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `Quality run 30631050997 attempt 2 同 headSha 全部通过` connect `M6交接状态` to `M6验收基线`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script` to the rest of the system?**
  _178 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `核心架构决策` be split into smaller, more focused modules?**
  _Cohesion score 0.0784313725490196 - nodes in this community are weakly interconnected._
- **Should `规格驱动工具链` be split into smaller, more focused modules?**
  _Cohesion score 0.07386363636363637 - nodes in this community are weakly interconnected._
- **Should `M6交接状态` be split into smaller, more focused modules?**
  _Cohesion score 0.09259259259259259 - nodes in this community are weakly interconnected._