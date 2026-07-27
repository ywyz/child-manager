# Graph Report - .  (2026-07-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 260 nodes · 298 edges · 19 communities (15 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.88)
- Token cost: 1,195 input · 1,685 output

## Graph Freshness
- Built from commit: `71110c7e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Speckit Specification Pipeline
- Architecture Decisions Deployment
- Daily Activity Plan Jobs
- Development Environment Milestones
- Baseline Gate Fixes
- Backup Login Authentication
- Shell Utility Scripts
- Constitution Issue Templates
- Milestone Dependencies Workflow
- Review Security Boundaries
- Async Jobs AI System
- Security Threat Model
- Tenant Isolation Data Model
- Feature Creation Scripts
- Backup Login Specification
- Milestone Ordering Dependencies
- Prerequisites Check Script
- Plan Setup Script
- Tasks Setup Script

## God Nodes (most connected - your core abstractions)
1. `Child Manager Constitution` - 14 edges
2. `Architecture Decision Index` - 12 edges
3. `Speckit Tasks` - 7 edges
4. `Child Manager Agent Development Rules` - 7 edges
5. `单一实现开发协议` - 7 edges
6. `Daily Activity Plan Implementation Plan` - 7 edges
7. `Speckit Specify` - 6 edges
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
- `Web API Worker Service Boundaries` --semantically_similar_to--> `Service Boundaries and One-Way Dependencies`  [INFERRED] [semantically similar]
  AGENTS.md → .specify/memory/constitution.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Speckit Full SDD Lifecycle** — _agents_skills_speckit_specify_skill_speckit_specify, _agents_skills_speckit_plan_skill_speckit_plan, _agents_skills_speckit_tasks_skill_speckit_tasks, _agents_skills_speckit_implement_skill_speckit_implement [EXTRACTED 1.00]
- **Immutable Docs Implementation Gate** — agents_design_docs_issue_dev_review_main, _github_issue_template_implementation_immutable_docs_baseline, _specify_templates_plan_template_constitution_and_docs_gate, _specify_templates_tasks_template_task_authorization_boundary [EXTRACTED 1.00]
- **Child Manager Non-Negotiable Safety Boundaries** — agents_service_boundaries, agents_kindergarten_isolation, agents_ai_and_prompt_security, _specify_memory_constitution_authoritative_state_and_recovery [EXTRACTED 1.00]
- **Web API Worker Boundary Alignment** — readme_service_topology, docs_adr_adr_0002_separate_web_api_worker_modular_monolith_modular_monolith, docs_adr_adr_0002_separate_web_api_worker_modular_monolith_service_boundaries, docs_design_system_architecture_modular_runtime_architecture, docs_design_system_architecture_trust_starts_at_api [INFERRED 0.95]
- **Kindergarten Isolation Stack** — docs_adr_adr_0001_cloud_only_kindergarten_isolation, docs_prd_lesson_management_lesson_plan_invariants, docs_design_data_model_tenant_scoped_data_model, docs_design_database_schema_composite_tenant_foreign_keys, docs_design_system_architecture_trust_starts_at_api [INFERRED 0.95]
- **M6 Readiness Gate** — context_m6_ready, docs_roadmap_m4_complete, docs_roadmap_m6_ready, docs_design_system_architecture_reliable_async_jobs, docs_design_data_model_background_job_model [INFERRED 0.85]
- **本地开发隔离模式** — docs_development_local_development_environments_worktree_resource_isolation, docs_development_local_development_environments_loopback_only_dependencies, docs_development_local_development_environments_production_topology_deferral [EXTRACTED 1.00]
- **M0 收敛证据链** — docs_faq_combined_audit_m0_gate_framework, docs______20260713________m0_gate_closure_evidence, docs______20260713____________final_docs_baseline [INFERRED 0.85]
- **身份纵深防御** — docs_security_threat_model_restricted_public_entry, docs_security_threat_model_phishing_resistant_authentication, docs_security_threat_model_password_totp_backup, docs_security_threat_model_emergency_recovery_dual_control [EXTRACTED 1.00]
- **Daily Activity Plan Document Baseline** — specs_001_daily_activity_plan_spec_daily_activity_feature, specs_001_daily_activity_plan_plan_daily_activity_implementation_plan, specs_001_daily_activity_plan_tasks_daily_activity_task_plan, specs_001_daily_activity_plan_contracts_readme_api_v1_contract, specs_001_daily_activity_plan_quickstart_daily_activity_acceptance_contract [EXTRACTED 1.00]
- **M6 Reliable AI and Group Activity** — specs_001_daily_activity_plan_tasks_m6_ai_and_group_activity, specs_001_daily_activity_plan_contracts_job_state_machine_background_job_state_machine, specs_001_daily_activity_plan_contracts_job_state_machine_ai_preview_adoption, specs_001_daily_activity_plan_spec_teacher_controlled_ai, templates_teacherplan_ai_added_step_red_text [EXTRACTED 1.00]
- **Password and TOTP Backup Login Baseline** — specs_002_password_totp_backup_login_spec_backup_login_feature, specs_002_password_totp_backup_login_plan_backup_login_implementation_plan, specs_002_password_totp_backup_login_data_model_backup_auth_data_model, specs_002_password_totp_backup_login_contracts_openapi_backup_login_api_fragment, specs_002_password_totp_backup_login_tasks_backup_login_task_plan [EXTRACTED 1.00]

## Communities (19 total, 4 thin omitted)

### Community 0 - "Speckit Specification Pipeline"
Cohesion: 0.09
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Append-Only Convergence Phase, Speckit Converge (+25 more)

### Community 1 - "Architecture Decisions Deployment"
Cohesion: 0.08
Nodes (33): Cloud Only Product, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication, Fixed Word Template Export Boundary, Immutable Traceable Export Copies, Secrets Outside Database Image and Logs (+25 more)

### Community 2 - "Daily Activity Plan Jobs"
Cohesion: 0.08
Nodes (29): Daily Activity Plan Specification Quality Checklist, AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, API v1 Contract, Optimistic Lock and Idempotency Contract, Trusted NiceGUI BFF Boundary (+21 more)

### Community 3 - "Development Environment Milestones"
Cohesion: 0.08
Nodes (25): 本地开发环境规范, 仅回环开发依赖, 生产拓扑延后, 工作树资源隔离, M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线 (+17 more)

### Community 4 - "Baseline Gate Fixes"
Cohesion: 0.11
Nodes (19): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+11 more)

### Community 5 - "Backup Login Authentication"
Cohesion: 0.12
Nodes (19): Child Manager Daily Activity API, Identity and Settings Endpoints, Plans, Jobs, and Exports Endpoints, Password and TOTP Backup Login API Fragment, Backup Enrollment and Authentication Endpoints, Backup Authentication Security Event Endpoint, Backup Authentication Data Model, Encrypted Credentials and Enrollments (+11 more)

### Community 6 - "Shell Utility Scripts"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 7 - "Constitution Issue Templates"
Cohesion: 0.16
Nodes (15): Constitution Consistency Propagation, Speckit Constitution, GitHub Issue Deduplication, Speckit Tasks to Issues, Blank Issue Policy, Immutable Docs Baseline, Implementation Issue Template, Constitution Template (+7 more)

### Community 8 - "Milestone Dependencies Workflow"
Cohesion: 0.17
Nodes (13): Current Project State, M6 Ready After M4 and M5, Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Ordered Alembic Migration Chain, Incremental Alembic Sequence, Independent Implementation Boundaries, Read Only Cross Review (+5 more)

### Community 9 - "Review Security Boundaries"
Cohesion: 0.17
Nodes (13): AI 密钥安全边界, 权威模型与契约收敛, 客户端幂等作用域, 历史合并审查, M0 收敛门禁框架, Word 模板隐私与历史清理, 旧设计不具权威性, 一日活动计划 PRD 查询 (+5 more)

### Community 10 - "Async Jobs AI System"
Cohesion: 0.20
Nodes (12): Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, Central Versioned Prompt System, Provider Neutral AI Interface, AI Profile and Prompt Version Model, Background Job and AI Result Model, Cross Row Transaction Invariants, AI Prompt and Job Physical Schema (+4 more)

### Community 11 - "Security Threat Model"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 12 - "Tenant Isolation Data Model"
Cohesion: 0.40
Nodes (5): Kindergarten Isolation Boundary, Tenant Scoped Data Model, Composite Kindergarten Foreign Keys, PostgreSQL and SQLite Validation Matrix, PostgreSQL Physical Schema Contract

### Community 14 - "Backup Login Specification"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 15 - "Milestone Ordering Dependencies"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

## Knowledge Gaps
- **50 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `Web、API 与 Worker 服务边界` (2× useful, score=1.416647594) _(code changed — re-verify)_
- `班级与教师配置` (2× useful, score=1.39887405)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Architecture Decision Index` connect `Architecture Decisions Deployment` to `Async Jobs AI System`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `PostgreSQL Authoritative Job State` connect `Async Jobs AI System` to `Architecture Decisions Deployment`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `Reliable Async Job Architecture` connect `Async Jobs AI System` to `Milestone Dependencies Workflow`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **What connects `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Speckit Specification Pipeline` be split into smaller, more focused modules?**
  _Cohesion score 0.08522727272727272 - nodes in this community are weakly interconnected._
- **Should `Architecture Decisions Deployment` be split into smaller, more focused modules?**
  _Cohesion score 0.08143939393939394 - nodes in this community are weakly interconnected._
- **Should `Daily Activity Plan Jobs` be split into smaller, more focused modules?**
  _Cohesion score 0.08374384236453201 - nodes in this community are weakly interconnected._