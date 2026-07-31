# Graph Report - .  (2026-07-31)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 377 nodes · 316 edges · 106 communities (22 shown, 84 thin omitted)
- Extraction: 88% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 36 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `246affe8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Architecture & Authorization Design
- Speckit Quality Workflow
- AI Async Generation System
- 单一实现开发协议
- Project Directory Structure
- Baseline & Quality Gates
- common.sh
- Backup Login Implementation Plan
- 历史合并审查
- Background Job State Machine
- T031: Implement Identity Service
- 后台任务
- 安全威胁模型
- docs/ROADMAP.md - Product & Engineering Roadmap
- Child Manager Project Constitution
- Retired Dual Agent Protocol
- create-new-feature.sh
- Classes Table
- Kindergarten Isolation Concept
- Password and TOTP Backup Login Feature
- 教案基础先于 AI
- Daily Activity Plan Word Layout
- Password + TOTP Backup Login
- AI Generation Results Table
- AI Model Profile Capabilities Table
- Prompt Definitions Table
- Roles Table
- check-prerequisites.sh
- setup-plan.sh
- setup-tasks.sh
- Child Manager - Kindergarten Education Management System
- Standard Quality Commands (uv/ruff/pyright/pytest)
- Account Invitations Table
- Account Recovery Requests Table
- Age Groups Table
- AI Generation Results Table
- AI Model Capabilities Table
- AI Model Profiles Table
- Audit Events Table
- Background Jobs Table
- Backup Credentials Table
- Backup Enrollments Table
- Bootstrap Initializations Table
- Class Areas Table
- Class Teachers Table
- Classes Table
- Plan Exports Table
- Plan Snapshots Table
- Daily Activity Plans Table
- Identity Approvals Table
- Snapshot Immutability
- JSONB Versioning
- Kindergarten Isolation
- Kindergartens Table
- Lesson Plan Sources Table
- Prompt Definitions Table
- Prompt Test Runs Table
- Prompt Versions Table
- Recovery Codes Table
- Refresh Tokens Table
- Roles Table
- Semesters Table
- User Roles Table
- Users Table
- WebAuthn Challenges Table
- WebAuthn Credentials Table
- Workday Cache Table
- Account Invitations Table
- Account Recovery Requests Table
- Audit Events Table
- Backup Credentials Table
- Backup Enrollments Table
- Bootstrap Initializations Table
- Class Areas Table
- JSONB Content Boundary
- Daily Activity Plan Authors Table
- Plan Exports Table
- Plan Snapshots Table
- Identity Approvals Table
- Lesson Plan Sources Table
- Prompt Test Runs Table
- Recovery Codes Table
- Refresh Tokens Table
- Semesters Table
- WebAuthn Challenges Table
- WebAuthn Credentials Table
- Workday Cache Table
- Application Owned Transactions
- External Key Source Seam
- pytest
- Development Workflow and Quality Gates
- Governance
- Technical, Security and Scope Constraints
- Daily Activity Plan Specification Quality Checklist
- AI 生成预览
- 备用登录配置
- 班级区域
- 一日活动反思
- 集体活动来源
- 幼儿园
- 教案历史快照
- 提示词测试记录
- Word 导出记录
- 工作日缓存
- WebAuthn

## God Nodes (most connected - your core abstractions)
1. `AGENTS.md Rules Document` - 19 edges
2. `Architecture Decision Index` - 11 edges
3. `Daily Activity Plan (一日活动计划)` - 7 edges
4. `FastAPI API Service` - 7 edges
5. `AI Async Generation System` - 7 edges
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
- **Three-Service Architecture Boundary (Web→API→Worker)** — concept_nicegui_web, concept_fastapi_api, concept_dramatiq_worker, concept_bff_proxy, concept_packages_contracts, concept_packages_backend [EXTRACTED 1.00]
- **Lesson Plan Creation→AI→Export Full Data Flow** — concept_daily_activity_plan, concept_ai_generation, concept_word_export, concept_lesson_plan_columns, concept_prompt_management, concept_optimistic_locking, concept_snapshot_history [EXTRACTED 1.00]
- **Authentication & Authorization Framework (WebAuthn + Password/TOTP + Recovery)** — concept_webauthn, concept_password_totp, concept_kindergarten_id, concept_teacher_class_relation, concept_audit_logging [EXTRACTED 1.00]
- **AI Generation Flow** — specs_001_daily_activity_plan_spec_daily_activity_plan, specs_001_daily_activity_plan_spec_ai_model_profile, specs_001_daily_activity_plan_spec_prompt_definition_version, specs_001_daily_activity_plan_spec_background_task, specs_001_daily_activity_plan_spec_ai_generation_preview [INFERRED 0.85]
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

## Communities (106 total, 84 thin omitted)

### Community 0 - "Architecture & Authorization Design"
Cohesion: 0.08
Nodes (34): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+26 more)

### Community 1 - "Speckit Quality Workflow"
Cohesion: 0.07
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+25 more)

### Community 2 - "AI Async Generation System"
Cohesion: 0.10
Nodes (28): OpenAI-Compatible AI Adapter & Test Doubles, AI Async Generation System, Alembic Migrations, Audit Logging & Sensitive Data Redaction, Web BFF Proxy (Browser-Only Entry), Class Indoor & Outdoor Areas, Daily Activity Plan (一日活动计划), Dramatiq Background Worker (+20 more)

### Community 3 - "单一实现开发协议"
Cohesion: 0.10
Nodes (21): M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线, 阶段授权分离, M2 Issue 执行记录, M2 RED-GREEN 顺序, 设计到主分支门禁流 (+13 more)

### Community 4 - "Project Directory Structure"
Cohesion: 0.11
Nodes (20): AGENTS.md Rules Document, AI Generation, Alembic, apps/api/ Directory, apps/web/ Directory, CONTEXT.md, docs/ Directory, FastAPI API (+12 more)

### Community 5 - "Baseline & Quality Gates"
Cohesion: 0.11
Nodes (19): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+11 more)

### Community 6 - "common.sh"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 7 - "Backup Login Implementation Plan"
Cohesion: 0.14
Nodes (16): Password and TOTP Backup Login API Fragment, Backup Enrollment and Authentication Endpoints, Backup Authentication Security Event Endpoint, Backup Authentication Data Model, Encrypted Credentials and Enrollments, Session Assurance and TOTP Replay Protection, Backup Login Implementation Plan, Identity Deep Module Reuse (+8 more)

### Community 8 - "历史合并审查"
Cohesion: 0.17
Nodes (13): AI 密钥安全边界, 权威模型与契约收敛, 客户端幂等作用域, 历史合并审查, M0 收敛门禁框架, Word 模板隐私与历史清理, 旧设计不具权威性, 一日活动计划 PRD 查询 (+5 more)

### Community 9 - "Background Job State Machine"
Cohesion: 0.17
Nodes (13): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, API v1 Contract, Optimistic Lock and Idempotency Contract, Trusted NiceGUI BFF Boundary, Daily Activity Plan Data Model (+5 more)

### Community 10 - "T031: Implement Identity Service"
Cohesion: 0.24
Nodes (10): POST /api/v1/auth/bootstrap/registration/options, GET /api/v1/auth/csrf, 认证会话, 初始化与邀请, 恢复码与恢复请求, 用户与角色, WebAuthn 凭据与 Challenge, T021: Identity Tests (+2 more)

### Community 11 - "后台任务"
Cohesion: 0.20
Nodes (10): GET /health/live, GET /health/ready, AI 模型档案, 审计事件, 后台任务, 班级与教师关联, 一日活动计划, 教案编写者 (+2 more)

### Community 12 - "安全威胁模型"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 13 - "docs/ROADMAP.md - Product & Engineering Roadmap"
Cohesion: 0.43
Nodes (7): Old Repository ywyz/kindergartenManager, CONTEXT.md - Project Context Document, docs/ROADMAP.md - Product & Engineering Roadmap, README.md - Product Overview, specs/001-daily-activity-plan/plan.md - Implementation Plan, specs/001-daily-activity-plan/quickstart.md - Quickstart Guide, specs/001-daily-activity-plan/spec.md - Feature Specification

### Community 14 - "Child Manager Project Constitution"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 15 - "Retired Dual Agent Protocol"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 17 - "Classes Table"
Cohesion: 0.50
Nodes (4): Age Groups Table, Class Teachers Table, Classes Table, Daily Activity Plans Table

### Community 18 - "Kindergarten Isolation Concept"
Cohesion: 0.50
Nodes (4): Composite Foreign Keys Concept, Kindergarten Isolation Concept, Kindergartens Table, Users Table

### Community 19 - "Password and TOTP Backup Login Feature"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 20 - "教案基础先于 AI"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

### Community 21 - "Daily Activity Plan Word Layout"
Cohesion: 0.67
Nodes (3): AI-Added Step Red Text, Structured Daily Activity Sections, Daily Activity Plan Word Layout

## Ambiguous Edges - Review These
- `README.md - Product Overview` → `Old Repository ywyz/kindergartenManager`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **169 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+164 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **84 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `Web、API 与 Worker 服务边界` (2× useful, score=1.416647594) _(code changed — re-verify)_
- `班级与教师配置` (2× useful, score=1.39887405)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `README.md - Product Overview` and `Old Repository ywyz/kindergartenManager`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `2026-07-13 编码前审查报告` connect `Baseline & Quality Gates` to `历史合并审查`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **What connects `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script` to the rest of the system?**
  _169 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Architecture & Authorization Design` be split into smaller, more focused modules?**
  _Cohesion score 0.0784313725490196 - nodes in this community are weakly interconnected._
- **Should `Speckit Quality Workflow` be split into smaller, more focused modules?**
  _Cohesion score 0.07386363636363637 - nodes in this community are weakly interconnected._
- **Should `AI Async Generation System` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `单一实现开发协议` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._