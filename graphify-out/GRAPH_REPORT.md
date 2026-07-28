# Graph Report - .  (2026-07-28)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 408 nodes · 371 edges · 95 communities (24 shown, 71 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.86)
- Token cost: 2,423 input · 3,620 output

## Graph Freshness
- Built from commit: `05a37740`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Architecture & Authorization Design
- Speckit Quality Workflow
- AI Model & Prompt Configuration
- Engineering Skeleton & Gates
- Project Directory Structure
- Baseline & Quality Gates
- Background Jobs & Plans API
- Core Subsystems & Milestones
- Shell Utility Functions
- Project Plan & Contracts
- Security & Model Convergence
- Backup Login Implementation
- API & Web Setup Isolation
- Repository Branches & Milestones
- Security & Authentication
- Daily Activity Plan Features
- Project Constitution Principles
- Technology Stack Services
- Development Workflow Rules
- Feature Branch Script
- Core Data Tables
- Database Relationships
- Backup Login Specification
- Implementation Order Dependencies
- Lesson Plan Content Structure
- AI Jobs Tables
- AI Model Profile Tables
- Prompt Management Tables
- User Roles Tables
- Prerequisites Check Script
- Setup Plan Script
- Setup Tasks Script
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
- Development Workflow Gates
- Governance
- Technical Security Constraints
- Plan Spec Quality Checklist
- WebAuthn

## God Nodes (most connected - your core abstractions)
1. `AGENTS.md Rules Document` - 19 edges
2. `Architecture Decision Index` - 11 edges
3. `首期一日活动计划完整闭环任务清单` - 10 edges
4. `US4 栏目级 AI 与教师采用决定权` - 10 edges
5. `US7 审计与可降级服务` - 8 edges
6. `单一实现开发协议` - 7 edges
7. `Feature Specification: 首期一日活动计划完整闭环` - 7 edges
8. `CONTEXT.md - Project Status` - 7 edges
9. `US3 模型与提示词配置` - 7 edges
10. `Speckit Tasks` - 6 edges

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
- **Development Technology Stack** — python, postgresql, nicegui, fastapi, redis, worker [INFERRED 0.75]
- **Git Branching Model** — docs_directory, apps_web, apps_api [INFERRED 0.75]
- **Documentation and Specification Sources** — readme, context, docs_directory, specs_directory, openapi_contracts, templates_directory [INFERRED 0.75]
- **Setup 到 M8 的阶段执行链** — specs_001_daily_activity_plan_tasks_setup, specs_001_daily_activity_plan_tasks_foundational, specs_001_daily_activity_plan_tasks_us1_m2, specs_001_daily_activity_plan_tasks_us1_m3, specs_001_daily_activity_plan_tasks_us1_m3a, specs_001_daily_activity_plan_tasks_us2_manual_plan, specs_001_daily_activity_plan_tasks_us3_ai_prompt_settings, specs_001_daily_activity_plan_tasks_us4_section_ai, specs_001_daily_activity_plan_tasks_us5_group_activity, specs_001_daily_activity_plan_tasks_us6_word_export, specs_001_daily_activity_plan_tasks_us7_audit_degradation, specs_001_daily_activity_plan_tasks_polish_m8 [EXTRACTED 1.00]
- **三个独立运行单元** — specs_001_daily_activity_plan_tasks_api_runtime, specs_001_daily_activity_plan_tasks_worker_runtime, specs_001_daily_activity_plan_tasks_web_runtime [EXTRACTED 1.00]
- **用户故事 RED、最小实现与 Checkpoint 模式** — specs_001_daily_activity_plan_tasks_us1_m2, specs_001_daily_activity_plan_tasks_us1_m3, specs_001_daily_activity_plan_tasks_us2_manual_plan, specs_001_daily_activity_plan_tasks_us3_ai_prompt_settings, specs_001_daily_activity_plan_tasks_us4_section_ai, specs_001_daily_activity_plan_tasks_us5_group_activity, specs_001_daily_activity_plan_tasks_us6_word_export, specs_001_daily_activity_plan_tasks_us7_audit_degradation [EXTRACTED 1.00]
- **Daily Activity Plan Full Pipeline** — child_manager_domain_settings, child_manager_domain_lesson_plans, child_manager_domain_ai_prompts, child_manager_domain_word_export [EXTRACTED 1.00]
- **Milestone Dependency Chain M0→M9** — child_manager_milestone_m0, child_manager_milestone_m1, child_manager_milestone_m2, child_manager_milestone_m3, child_manager_milestone_m3a, child_manager_milestone_m5, child_manager_milestone_m4, child_manager_milestone_m6, child_manager_milestone_m7, child_manager_milestone_m8, child_manager_milestone_m9 [EXTRACTED 1.00]
- **Three-Service Architecture Pattern** — child_manager_arch_nicegui_web, child_manager_arch_fastapi_api, child_manager_arch_worker [EXTRACTED 1.00]
- **Tables Implementing Kindergarten Isolation** — docs_design_database_schema_users, docs_design_database_schema_webauthn_credentials, docs_design_database_schema_webauthn_challenges, docs_design_database_schema_backup_auth_credentials, docs_design_database_schema_backup_auth_enrollments, docs_design_database_schema_bootstrap_initializations, docs_design_database_schema_account_invitations, docs_design_database_schema_recovery_codes, docs_design_database_schema_account_recovery_requests, docs_design_database_schema_identity_verification_approvals, docs_design_database_schema_user_roles, docs_design_database_schema_refresh_tokens, docs_design_database_schema_age_groups, docs_design_database_schema_classes, docs_design_database_schema_class_teachers, docs_design_database_schema_semesters, docs_design_database_schema_class_areas, docs_design_database_schema_ai_model_profiles, docs_design_database_schema_ai_model_profile_capabilities, docs_design_database_schema_prompt_definitions, docs_design_database_schema_prompt_versions, docs_design_database_schema_prompt_test_runs, docs_design_database_schema_daily_activity_plans, docs_design_database_schema_daily_activity_plan_authors, docs_design_database_schema_daily_activity_plan_snapshots, docs_design_database_schema_lesson_plan_sources, docs_design_database_schema_background_jobs, docs_design_database_schema_ai_generation_results, docs_design_database_schema_daily_activity_plan_exports, docs_design_database_schema_workday_cache, docs_design_database_schema_audit_events [EXTRACTED 1.00]
- **Tables Involved in Authentication Flow** — docs_design_database_schema_users, docs_design_database_schema_webauthn_credentials, docs_design_database_schema_webauthn_challenges, docs_design_database_schema_backup_auth_credentials, docs_design_database_schema_backup_auth_enrollments, docs_design_database_schema_refresh_tokens [INFERRED 0.80]
- **Lesson Planning System Tables** — docs_design_database_schema_daily_activity_plans, docs_design_database_schema_daily_activity_plan_authors, docs_design_database_schema_daily_activity_plan_snapshots, docs_design_database_schema_lesson_plan_sources [INFERRED 0.80]
- **Identity and Authentication System** — docs_design_data_model_kindergartens, docs_design_data_model_users, docs_design_data_model_webauthn_credentials, docs_design_data_model_webauthn_challenges, docs_design_data_model_backup_auth_credentials, docs_design_data_model_backup_auth_enrollments, docs_design_data_model_bootstrap_initializations, docs_design_data_model_account_invitations, docs_design_data_model_recovery_codes, docs_design_data_model_account_recovery_requests, docs_design_data_model_identity_verification_approvals, docs_design_data_model_roles, docs_design_data_model_user_roles, docs_design_data_model_refresh_tokens, docs_design_data_model_audit_events, docs_design_data_model_kindergarten_isolation, docs_design_data_model_immutability [EXTRACTED 1.00]
- **Core Principles of Constitution** — specify_memory_constitution_principle_1, specify_memory_constitution_principle_2, specify_memory_constitution_principle_3, specify_memory_constitution_principle_4, specify_memory_constitution_principle_5, specify_memory_constitution_principle_6 [EXTRACTED 1.00]
- **Governance Framework** — specify_memory_constitution_constitution, specify_memory_constitution_technical_constraints, specify_memory_constitution_development_workflow, specify_memory_constitution_governance [EXTRACTED 1.00]
- **Speckit Full SDD Lifecycle** — _agents_skills_speckit_specify_skill_speckit_specify, _agents_skills_speckit_plan_skill_speckit_plan, _agents_skills_speckit_tasks_skill_speckit_tasks, _agents_skills_speckit_implement_skill_speckit_implement [EXTRACTED 1.00]
- **Web API Worker Boundary Alignment** — docs_adr_adr_0002_separate_web_api_worker_modular_monolith_modular_monolith, docs_adr_adr_0002_separate_web_api_worker_modular_monolith_service_boundaries, docs_design_system_architecture_modular_runtime_architecture, docs_design_system_architecture_trust_starts_at_api [INFERRED 0.95]
- **本地开发隔离模式** — docs_development_local_development_environments_worktree_resource_isolation, docs_development_local_development_environments_loopback_only_dependencies, docs_development_local_development_environments_production_topology_deferral [EXTRACTED 1.00]
- **M0 收敛证据链** — docs_faq_combined_audit_m0_gate_framework, docs______20260713________m0_gate_closure_evidence, docs______20260713____________final_docs_baseline [INFERRED 0.85]
- **身份纵深防御** — docs_security_threat_model_restricted_public_entry, docs_security_threat_model_phishing_resistant_authentication, docs_security_threat_model_password_totp_backup, docs_security_threat_model_emergency_recovery_dual_control [EXTRACTED 1.00]
- **Password and TOTP Backup Login Baseline** — specs_002_password_totp_backup_login_spec_backup_login_feature, specs_002_password_totp_backup_login_plan_backup_login_implementation_plan, specs_002_password_totp_backup_login_data_model_backup_auth_data_model, specs_002_password_totp_backup_login_contracts_openapi_backup_login_api_fragment, specs_002_password_totp_backup_login_tasks_backup_login_task_plan [EXTRACTED 1.00]

## Communities (95 total, 71 thin omitted)

### Community 0 - "Architecture & Authorization Design"
Cohesion: 0.08
Nodes (34): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+26 more)

### Community 1 - "Speckit Quality Workflow"
Cohesion: 0.07
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+25 more)

### Community 2 - "AI Model & Prompt Configuration"
Cohesion: 0.11
Nodes (27): 安全模型档案与提示词生命周期, 固定 Word 模板原件哈希与样式完整性, AI 输入、提示词、模型与 Schema 冻结上下文, 不可变脱敏审计与外部故障隔离, GitHub Issue #10, specs/002-password-totp-backup-login/tasks.md, M6 T087–T126 in_progress，T103 为下一项, M8 性能、安全、无障碍与交付验收 (+19 more)

### Community 3 - "Engineering Skeleton & Gates"
Cohesion: 0.08
Nodes (25): 本地开发环境规范, 仅回环开发依赖, 生产拓扑延后, 工作树资源隔离, M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线 (+17 more)

### Community 4 - "Project Directory Structure"
Cohesion: 0.11
Nodes (20): AGENTS.md Rules Document, AI Generation, Alembic, apps/api/ Directory, apps/web/ Directory, CONTEXT.md, docs/ Directory, FastAPI API (+12 more)

### Community 5 - "Baseline & Quality Gates"
Cohesion: 0.11
Nodes (19): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+11 more)

### Community 6 - "Background Jobs & Plans API"
Cohesion: 0.11
Nodes (19): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, Child Manager Daily Activity API, Identity and Settings Endpoints, Plans, Jobs, and Exports Endpoints, API v1 Contract (+11 more)

### Community 7 - "Core Subsystems & Milestones"
Cohesion: 0.14
Nodes (17): AI Prompt Management Subsystem, Daily Lesson Plan System, Settings System - Kindergarten/Semester/Class, Word Document Export, Password + TOTP Backup Login, WebAuthn Passkey Authentication, M0 Shared Design Baseline, M1 Engineering Skeleton (+9 more)

### Community 8 - "Shell Utility Functions"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 9 - "Project Plan & Contracts"
Cohesion: 0.13
Nodes (15): 执行授权边界, 可收集且无错误的 RED 门禁, contracts/, data-model.md, graphify-out/graph.json, 常规测试禁止真实 AI、节假日及其他外网调用, 阶段依赖与执行顺序, plan.md (+7 more)

### Community 10 - "Security & Model Convergence"
Cohesion: 0.17
Nodes (13): AI 密钥安全边界, 权威模型与契约收敛, 客户端幂等作用域, 历史合并审查, M0 收敛门禁框架, Word 模板隐私与历史清理, 旧设计不具权威性, 一日活动计划 PRD 查询 (+5 more)

### Community 11 - "Backup Login Implementation"
Cohesion: 0.18
Nodes (13): Backup Authentication Data Model, Encrypted Credentials and Enrollments, Session Assurance and TOTP Replay Protection, Backup Login Implementation Plan, Identity Deep Module Reuse, Backup Login Acceptance Guide, Recovery Is Not Downgraded, AES-GCM Secret Envelope and Layered Throttling (+5 more)

### Community 12 - "API & Web Setup Isolation"
Cohesion: 0.21
Nodes (12): FastAPI API 独立运行单元, 方法、路由、实际 path/query/body 的规范幂等指纹, Foundational T009–T020, docs/development/local-development-environments.md, 园所、学期、班级、教师关系与区域设置, Setup T001–T008, kindergarten_id 园所隔离, US1 M2 认证、授权与身份审计 (+4 more)

### Community 13 - "Repository Branches & Milestones"
Cohesion: 0.31
Nodes (10): dev - Implementation Branch, docs - Design & Spec Baseline, main - Stable Release Baseline, CONTEXT.md - Project Status, Issue #11 - M6 AI Async Generation, Old Repository - kindergartenManager, README.md - Product Overview, Implementation Plan - Daily Activity Plan (+2 more)

### Community 14 - "Security & Authentication"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 15 - "Daily Activity Plan Features"
Cohesion: 0.25
Nodes (8): Feature Specification: 首期一日活动计划完整闭环, User Story 1: Admin Setup, User Story 2: Manual Lesson Plan Loop, User Story 3: Admin Configure Model and Prompts, User Story 4: Teacher Uses AI by Section, User Story 5: Teacher Processes Group Activity Source, User Story 6: Teacher Export and Download Fixed Word, User Story 7: Admin Audit and Degradable Service

### Community 16 - "Project Constitution Principles"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 17 - "Technology Stack Services"
Cohesion: 0.50
Nodes (5): FastAPI API Service, NiceGUI Web Service, PostgreSQL Database, Redis Message Broker, Dramatiq Background Worker

### Community 18 - "Development Workflow Rules"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 20 - "Core Data Tables"
Cohesion: 0.50
Nodes (4): Age Groups Table, Class Teachers Table, Classes Table, Daily Activity Plans Table

### Community 21 - "Database Relationships"
Cohesion: 0.50
Nodes (4): Composite Foreign Keys Concept, Kindergarten Isolation Concept, Kindergartens Table, Users Table

### Community 22 - "Backup Login Specification"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 23 - "Implementation Order Dependencies"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

### Community 24 - "Lesson Plan Content Structure"
Cohesion: 0.67
Nodes (3): AI-Added Step Red Text, Structured Daily Activity Sections, Daily Activity Plan Word Layout

## Knowledge Gaps
- **172 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+167 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **71 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `Web、API 与 Worker 服务边界` (2× useful, score=1.416647594) _(code changed — re-verify)_
- `班级与教师配置` (2× useful, score=1.39887405)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Polish 与 M8 完整验收` connect `AI Model & Prompt Configuration` to `Project Plan & Contracts`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **What connects `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script` to the rest of the system?**
  _172 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Architecture & Authorization Design` be split into smaller, more focused modules?**
  _Cohesion score 0.0784313725490196 - nodes in this community are weakly interconnected._
- **Should `Speckit Quality Workflow` be split into smaller, more focused modules?**
  _Cohesion score 0.07386363636363637 - nodes in this community are weakly interconnected._
- **Should `AI Model & Prompt Configuration` be split into smaller, more focused modules?**
  _Cohesion score 0.10826210826210826 - nodes in this community are weakly interconnected._
- **Should `Engineering Skeleton & Gates` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._
- **Should `Project Directory Structure` be split into smaller, more focused modules?**
  _Cohesion score 0.11052631578947368 - nodes in this community are weakly interconnected._