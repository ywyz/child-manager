# Graph Report - child-manager  (2026-07-28)

## Corpus Check
- 347 files · ~210,133 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3069 nodes · 8751 edges · 261 communities (170 shown, 91 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 759 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4aa1b057`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Architecture Decisions
- Speckit Process
- Development Milestones
- AI Prompt & Audit
- Baseline & Gate Process
- API & Job System
- Feature Subsystems & Milestones
- Shell Script Utilities
- Project Plan & Gates
- Requirements & Design Review
- Backup Login Authentication
- Service Components & Setup
- Repository Structure & Docs
- Security Threat Model
- Feature User Stories
- Project Principles & Constraints
- Technology Stack
- Development Workflow
- Feature Creation Scripts
- Development Tools & Rules
- Kindergarten Domain Tables
- Database Schema Concepts
- Backup Login Specification
- Dependency Order Constraints
- AI & Word Layout
- AI & Jobs Tables
- AI Model Profile Tables
- Prompt Tables
- Roles Tables
- Prerequisite Check Script
- Setup Plan Script
- Setup Tasks Script
- AI & Prompt Rules
- Branch & Git Rules
- Data Model & Isolation
- Fact Source Conflict
- Security & Privacy Rules
- Service Boundaries & Dependencies
- Testing Requirements
- Alembic Migrations
- Account Invitations
- Account Recovery Requests
- Age Groups
- AI Generation Results
- AI Model Capabilities
- AI Model Profiles
- Audit Events
- Background Jobs
- Backup Auth Credentials
- Backup Auth Enrollments
- Bootstrap Initializations
- Class Areas
- Class Teachers
- Classes
- Daily Activity Exports
- Daily Activity Snapshots
- Daily Activity Plans
- Identity Verification Approvals
- Immutability Policy
- JSONB Schema Versioning
- Kindergarten Isolation
- Kindergartens
- Lesson Plan Sources
- Prompt Definitions
- Prompt Test Runs
- Prompt Versions
- Recovery Codes
- Refresh Tokens
- Roles
- Semesters
- User Roles
- Users
- WebAuthn Challenges
- WebAuthn Credentials
- Workday Cache
- Account Invitations
- Account Recovery Requests
- Audit Events
- Backup Auth Credentials
- Backup Auth Enrollments
- Bootstrap Initializations
- Class Areas
- JSONB Boundary Concept
- Activity Plan Authors
- Activity Plan Exports
- Activity Plan Snapshots
- Identity Verification Approvals
- Lesson Plan Sources
- Prompt Test Runs
- Recovery Codes
- Refresh Tokens
- Semesters
- WebAuthn Challenges
- WebAuthn Credentials
- Workday Cache
- Application Transactions
- External Key Seam
- PostgreSQL Database
- pytest Testing
- Redis Cache
- Development Quality Gates
- Governance
- Technical Security Constraints
- Daily Activity Checklist
- WebAuthn
- routers/settings.py
- PromptRepository
- Base
- test_backup_authentication.py
- test_config.py
- issue_secret
- IdentityService
- ContractModel
- test_ai_job_recovery.py
- ai_generation.py
- provision_editable_plan_context
- lesson_plans/service.py
- contracts/prompts.py
- IdentityError
- AiKeyEnvelope
- csrf_headers
- actors.py
- routers/plans.py
- AiClientError
- worker/test_prompt_test_jobs.py
- test_ai_retry_policy.py
- routers/prompts.py
- routers/users.py
- WorkdayResult
- LessonPlanRepository
- pages/auth.py
- test_ai_model_profiles.py
- identity/service.py
- MemoryLoginThrottle
- PostgresPromptTestStore
- ActorFixture
- IdentitySecretKeyProvider
- JobRepository
- _Connection
- SessionUser
- ProviderNeutralAiClient
- api/test_prompt_test_jobs.py
- test_settings_smoke.py
- Dev 跨机器开发交接（2026-07-24）
- .authenticate_with_backup
- test_local_development_profiles.py
- test_auth_smoke.py
- AiGenerationResultRepository
- test_identity_isolation.py
- PlanContentV1
- create_app
- test_ai_preview_lifecycle.py
- test_ai_key_rotation.py
- build_health_dependencies
- contracts/jobs.py
- pages/settings.py
- web/__main__.py
- prompts/service.py
- ports.py
- test_backup_maintenance.py
- test_invitations.py
- test_runtime_openapi.py
- test_settings_permissions.py
- pages/plans.py
- validate_prompt_result_schema
- test_credentials.py
- test_plan_ai_contracts.py
- test_ai_prompt_settings_smoke.py
- test_auth_contract.py
- test_ai_prompt_repositories.py
- test_ai_generation_service.py
- openapi.py
- totp.py
- test_backup_auth_contract.py
- test_ai_client.py
- proxy_request
- transactional_session
- test_workday_service.py
- contracts/jobs.py
- canonical_request_fingerprint
- US4 栏目级 AI 与教师采用决定权
- test_secret_encryption.py
- 0007_ai_prompts_jobs.py
- Alembic
- test_openapi_document.py
- test_content_v1.py
- test_ai_key_envelope.py
- test_ai_model_url_policy.py
- test_prompt_catalog.py
- test_backup_auth_smoke.py
- test_settings_isolation.py
- normalize_username
- test_0005_password_totp_backup_login.py
- 0001_identity_and_audit.py
- test_password_to_passkey.py
- 0002_passkey_expand.py
- 0006_lesson_plans.py
- 0008_ai_generation_results.py
- US6 固定 Word 导出与重新下载
- test_users_contract.py
- _totp_module
- Q: 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。
- Q: M5 完成后到 M4 的当前依赖路径是什么？
- US1 M2 认证、授权与身份审计
- _run
- test_calendar.py
- test_prompt_renderer.py
- FakeCalendar
- clock.py
- redis.py
- 0005_password_totp_backup_login.py
- test_0001_identity.py
- leases.py
- FakeAiClient
- apps/__init__.py
- apps/worker/__init__.py
- backend/database/__init__.py
- NOTICE.md
- backend/__init__.py
- contracts/__init__.py
- tests/web/__init__.py
- child-manager

## God Nodes (most connected - your core abstractions)
1. `ActorFixture` - 175 edges
2. `csrf_headers()` - 157 edges
3. `IdentityError` - 151 edges
4. `ContractModel` - 148 edges
5. `SessionUser` - 140 edges
6. `IdentityRepository` - 131 edges
7. `IdentityService` - 103 edges
8. `AuditRepository` - 73 edges
9. `require_csrf()` - 64 edges
10. `provision_editable_plan_context()` - 60 edges

## Surprising Connections (you probably didn't know these)
- `一日活动计划需求面` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_020708_请根据现有文档_和旧仓库的文件思考如何撰写_docs_prd_lesson_management_m.md → docs/faq/combined-audit.md
- `ADR 直接文件核对` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_025449_哪些关键架构决策需要独立_adr_哪些已经确认_决策之间有什么依赖.md → docs/faq/combined-audit.md
- `校正后的数据模型边界` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md → docs/faq/combined-audit.md
- `test_identity_audit_repository_is_append_only()` --indirect_call--> `AuditRepository`  [INFERRED]
  tests/unit/identity/test_audit.py → packages/backend/audit/repository.py
- `test_identity_repository_exposes_atomic_backup_auth_operations()` --indirect_call--> `IdentityRepository`  [INFERRED]
  tests/repository/test_backup_auth_isolation.py → packages/backend/identity/repository.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
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
- **项目治理与规则文档** — agents_agents, specify_memory_constitution_constitution [INFERRED 0.90]
- **认证与安全机制** — agents_security [EXTRACTED 1.00]
- **知识与代码分析工具** — agents_graphify, agents_codebase_mcp, agents_tools [INFERRED 0.85]
- **Speckit Full SDD Lifecycle** — _agents_skills_speckit_specify_skill_speckit_specify, _agents_skills_speckit_plan_skill_speckit_plan, _agents_skills_speckit_tasks_skill_speckit_tasks, _agents_skills_speckit_implement_skill_speckit_implement [EXTRACTED 1.00]
- **Web API Worker Boundary Alignment** — docs_adr_adr_0002_separate_web_api_worker_modular_monolith_modular_monolith, docs_adr_adr_0002_separate_web_api_worker_modular_monolith_service_boundaries, docs_design_system_architecture_modular_runtime_architecture, docs_design_system_architecture_trust_starts_at_api [INFERRED 0.95]
- **本地开发隔离模式** — docs_development_local_development_environments_worktree_resource_isolation, docs_development_local_development_environments_loopback_only_dependencies, docs_development_local_development_environments_production_topology_deferral [EXTRACTED 1.00]
- **M0 收敛证据链** — docs_faq_combined_audit_m0_gate_framework, docs______20260713________m0_gate_closure_evidence, docs______20260713____________final_docs_baseline [INFERRED 0.85]
- **身份纵深防御** — docs_security_threat_model_restricted_public_entry, docs_security_threat_model_phishing_resistant_authentication, docs_security_threat_model_password_totp_backup, docs_security_threat_model_emergency_recovery_dual_control [EXTRACTED 1.00]
- **Password and TOTP Backup Login Baseline** — specs_002_password_totp_backup_login_spec_backup_login_feature, specs_002_password_totp_backup_login_plan_backup_login_implementation_plan, specs_002_password_totp_backup_login_data_model_backup_auth_data_model, specs_002_password_totp_backup_login_contracts_openapi_backup_login_api_fragment, specs_002_password_totp_backup_login_tasks_backup_login_task_plan [EXTRACTED 1.00]

## Communities (261 total, 91 thin omitted)

### Community 0 - "Architecture Decisions"
Cohesion: 0.08
Nodes (34): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+26 more)

### Community 1 - "Speckit Process"
Cohesion: 0.07
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+25 more)

### Community 2 - "Development Milestones"
Cohesion: 0.08
Nodes (25): 本地开发环境规范, 仅回环开发依赖, 生产拓扑延后, 工作树资源隔离, M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线 (+17 more)

### Community 3 - "AI Prompt & Audit"
Cohesion: 0.21
Nodes (12): 安全模型档案与提示词生命周期, 不可变脱敏审计与外部故障隔离, GitHub Issue #10, specs/002-password-totp-backup-login/tasks.md, M8 性能、安全、无障碍与交付验收, 唯一教案、保存、历史、归档与恢复, Polish 与 M8 完整验收, 数据库提交后 Redis 故障仍保持 202 pending_dispatch (+4 more)

### Community 4 - "Baseline & Gate Process"
Cohesion: 0.07
Nodes (32): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+24 more)

### Community 5 - "API & Job System"
Cohesion: 0.07
Nodes (32): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, Child Manager Daily Activity API, Identity and Settings Endpoints, Plans, Jobs, and Exports Endpoints, API v1 Contract (+24 more)

### Community 6 - "Feature Subsystems & Milestones"
Cohesion: 0.10
Nodes (27): dev - Implementation Branch, docs - Design & Spec Baseline, main - Stable Release Baseline, CONTEXT.md - Project Status, AI Prompt Management Subsystem, Daily Lesson Plan System, Settings System - Kindergarten/Semester/Class, Word Document Export (+19 more)

### Community 7 - "Shell Script Utilities"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 8 - "Project Plan & Gates"
Cohesion: 0.13
Nodes (15): 执行授权边界, 可收集且无错误的 RED 门禁, contracts/, data-model.md, graphify-out/graph.json, 常规测试禁止真实 AI、节假日及其他外网调用, 阶段依赖与执行顺序, plan.md (+7 more)

### Community 9 - "Requirements & Design Review"
Cohesion: 0.13
Nodes (25): settings_service(), IntegrityError, NoReturn, current_semester_selection_is_valid(), lead_teacher_selection_is_valid(), _native_url(), normalize_class_areas(), _normalize_display_name() (+17 more)

### Community 10 - "Backup Login Authentication"
Cohesion: 0.06
Nodes (19): _backup_credential(), _backup_enrollment(), BackupCredentialRecord, BackupEnrollmentRecord, BackupRevocationResult, BackupSecurityEventRecord, ChallengeRecord, _credential() (+11 more)

### Community 11 - "Service Components & Setup"
Cohesion: 0.38
Nodes (7): FastAPI API 独立运行单元, 方法、路由、实际 path/query/body 的规范幂等指纹, Foundational T009–T020, docs/development/local-development-environments.md, Setup T001–T008, NiceGUI Web 独立运行单元, 后台 Worker 独立运行单元

### Community 12 - "Repository Structure & Docs"
Cohesion: 0.19
Nodes (45): authenticate_with_password_and_totp(), authentication_start(), authentication_verify(), backup_authentication_status(), bootstrap_options(), bootstrap_verify(), _check_public_throttle(), _clear_public_throttle() (+37 more)

### Community 13 - "Security Threat Model"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 14 - "Feature User Stories"
Cohesion: 0.25
Nodes (8): Feature Specification: 首期一日活动计划完整闭环, User Story 1: Admin Setup, User Story 2: Manual Lesson Plan Loop, User Story 3: Admin Configure Model and Prompts, User Story 4: Teacher Uses AI by Section, User Story 5: Teacher Processes Group Activity Source, User Story 6: Teacher Export and Download Fixed Word, User Story 7: Admin Audit and Degradable Service

### Community 15 - "Project Principles & Constraints"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 16 - "Technology Stack"
Cohesion: 0.50
Nodes (5): FastAPI API Service, NiceGUI Web Service, PostgreSQL Database, Redis Message Broker, Dramatiq Background Worker

### Community 17 - "Development Workflow"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 19 - "Development Tools & Rules"
Cohesion: 0.67
Nodes (4): AGENTS.md 开发规则文件, codebase-memory MCP, Graphify 知识图谱工具, 搜索工具优先级

### Community 20 - "Kindergarten Domain Tables"
Cohesion: 0.50
Nodes (4): Age Groups Table, Class Teachers Table, Classes Table, Daily Activity Plans Table

### Community 21 - "Database Schema Concepts"
Cohesion: 0.50
Nodes (4): Composite Foreign Keys Concept, Kindergarten Isolation Concept, Kindergartens Table, Users Table

### Community 22 - "Backup Login Specification"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 23 - "Dependency Order Constraints"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

### Community 24 - "AI & Word Layout"
Cohesion: 0.67
Nodes (3): AI-Added Step Red Text, Structured Daily Activity Sections, Daily Activity Plan Word Layout

### Community 39 - "Alembic Migrations"
Cohesion: 0.14
Nodes (9): Event, AiExecutionContext, AiJobStore, AiJobStoreProtocol, Any, datetime, Protocol, UUID (+1 more)

### Community 98 - "pytest Testing"
Cohesion: 0.33
Nodes (12): admin_session(), CurrentSessionDependency, _provision_associated_teacher(), TestClient, UUID, _session_for(), teacher_client(), test_all_settings_routes_require_authentication() (+4 more)

### Community 99 - "Redis Cache"
Cohesion: 0.14
Nodes (16): _error_response(), FastAPI, Request, UUID, FastAPI 应用装配、统一异常转换与健康端点。, _request_id(), JSONResponse, ErrorResponse (+8 more)

### Community 104 - "WebAuthn"
Cohesion: 0.10
Nodes (34): ChallengeBinding, ChallengeRecord, consume_challenge(), issue_challenge(), IssuedChallenge, datetime, WebAuthn ceremony challenge 的公共领域 seam。, 签发绑定上下文、五分钟有效且只保存摘要的 challenge。 (+26 more)

### Community 105 - "routers/settings.py"
Cohesion: 0.08
Nodes (64): AgeGroup, AiModelProfile, AiModelServiceDependency, _age_group(), _ai_model(), _area(), _class(), create_ai_model_profile() (+56 more)

### Community 106 - "PromptRepository"
Cohesion: 0.11
Nodes (23): prompt_service(), PromptTemplateError, Any, ValueError, 仅支持固定白名单纯替换词法的提示词渲染器。, render_prompt(), _render_value(), validate_prompt_template() (+15 more)

### Community 107 - "Base"
Cohesion: 0.10
Nodes (40): DeclarativeBase, AuditEvent, Base, AccountInvitation, AccountRecoveryRequest, BackupAuthCredential, BackupAuthEnrollment, BootstrapInitialization (+32 more)

### Community 108 - "test_backup_authentication.py"
Cohesion: 0.10
Nodes (33): _auth_throttle(), MemoryAuthThrottle, datetime, Redis, timedelta, 公开身份 ceremony 的来源限流公共 seam。, 按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。, 多进程 API 使用的 Redis 固定窗口实现。 (+25 more)

### Community 109 - "test_config.py"
Cohesion: 0.05
Nodes (50): main(), AppSettings, global_security_ready(), BaseModel, 拒绝在非开发环境或非回环地址关闭 Cookie Secure。, 验证进程启动时的 Cookie 与监听地址组合。, JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。, validate_cookie_security() (+42 more)

### Community 110 - "issue_secret"
Cohesion: 0.07
Nodes (58): ArgumentParser, activate_initialization(), migrate_passkeys(), _native_url(), datetime, UUID, 首位管理员的部署控制台初始化与双人核验激活。, 仅在通行密钥已登记并完成两位预登记人员核验后激活。 (+50 more)

### Community 111 - "IdentityService"
Cohesion: 0.13
Nodes (19): identity_service(), AuditRepository, ChallengePurpose, StrEnum, _challenge_digest(), _client_challenge(), _decode_base64url(), IdentityError (+11 more)

### Community 112 - "ContractModel"
Cohesion: 0.08
Nodes (54): _allowed_origins(), _loopback_aliases(), 同源 Cookie、WebAuthn、邀请、恢复与会话端点。, ContractModel, BaseModel, ExportReference, AdminCredentialRevocationResult, AuthenticationCredential (+46 more)

### Community 113 - "test_ai_job_recovery.py"
Cohesion: 0.10
Nodes (50): JobMessage, Redis 中唯一允许传递的最小任务消息。, SimpleNamespace, _insert_job(), _insert_other_tenant_plan(), _insert_result(), _native_url(), _provision_dependencies() (+42 more)

### Community 114 - "ai_generation.py"
Cohesion: 0.08
Nodes (31): AiGenerationResultRecord, AiGenerationResultRepository, _json_object(), _optional_uuid(), Any, datetime, 同园隔离的 AI 生成结果 Repository。, _record() (+23 more)

### Community 115 - "provision_editable_plan_context"
Cohesion: 0.11
Nodes (35): current_session(), AuthenticatedSessionDependency, admin_client(), passkey_client(), MonkeyPatch, TestClient, 通过 FastAPI 身份依赖注入建立已 step-up 管理员，不借用密码登录。, provision_editable_plan_context() (+27 more)

### Community 116 - "lesson_plans/service.py"
Cohesion: 0.26
Nodes (10): lesson_plan_service(), LessonPlanService, OpenPlanResult, PlanView, _PlanViewSeed, date, UUID, 完成单一用例响应；外网解析发生在业务事务关闭之后。 (+2 more)

### Community 117 - "contracts/prompts.py"
Cohesion: 0.06
Nodes (107): alias, clear_prompt_tests(), create_prompt_test(), _definition(), get_prompt(), get_prompt_test(), get_prompt_version(), _job() (+99 more)

### Community 118 - "IdentityError"
Cohesion: 0.13
Nodes (17): AgeGroupRecord, _ai_profile(), AreaInput, AreaRecord, ClassRecord, KindergartenRecord, Any, date (+9 more)

### Community 119 - "AiKeyEnvelope"
Cohesion: 0.09
Nodes (37): AiKeyProvider, ai_model_service(), UUID, run_rotation(), _aad(), AiKeyEnvelope, decrypt_api_key(), decrypt_api_key_with_provider() (+29 more)

### Community 120 - "csrf_headers"
Cohesion: 0.12
Nodes (41): csrf_headers(), _base64url(), _credential(), MonkeyPatch, TestClient, _registration_credential(), test_authentication_options_are_username_less_and_browser_ready(), test_authentication_options_do_not_increment_failure_limit() (+33 more)

### Community 121 - "actors.py"
Cohesion: 0.16
Nodes (16): Actor, build_prompt_test_executor(), Broker, register_actors(), build_redis_broker(), build_test_broker(), Broker, 生产 Redis 与确定性测试消息代理装配。 (+8 more)

### Community 122 - "routers/plans.py"
Cohesion: 0.15
Nodes (36): archive_plan(), autosave_plan(), get_plan(), list_plans(), list_snapshots(), open_plan(), _plan(), CurrentSessionDependency (+28 more)

### Community 123 - "AiClientError"
Cohesion: 0.24
Nodes (3): PromptTestStore, datetime, UUID

### Community 124 - "worker/test_prompt_test_jobs.py"
Cohesion: 0.15
Nodes (20): _context(), FakeAuthorizer, FakeClient, FakeStore, _modules(), Any, datetime, UUID (+12 more)

### Community 125 - "test_ai_retry_policy.py"
Cohesion: 0.10
Nodes (22): BaseTransport, ProviderNeutralAiClient, Resolver, cap_retry_after_seconds(), is_retryable_ai_error(), UUID, 按任务与尝试次数生成可复现的有界抖动，便于恢复与确定性测试。, retry_delay_seconds() (+14 more)

### Community 126 - "routers/prompts.py"
Cohesion: 0.25
Nodes (13): MonkeyPatch, UUID, RecordingConnection, RecordingResult, _seed_backup_repository(), test_admin_role_gate_restricts_and_then_releases_webauthn_sessions(), test_backup_credential_reads_are_scoped_to_kindergarten_and_user(), test_backup_version_change_revokes_only_related_sessions() (+5 more)

### Community 127 - "routers/users.py"
Cohesion: 0.19
Nodes (32): activate(), create_user(), credential_revoke(), credentials(), deactivate(), get_user(), _invitation(), invitation_issue() (+24 more)

### Community 128 - "WorkdayResult"
Cohesion: 0.09
Nodes (30): map_timor_payload(), AsyncBaseTransport, date, TimorWorkdayClient, WorkdayResult, Any, date, datetime (+22 more)

### Community 129 - "LessonPlanRepository"
Cohesion: 0.16
Nodes (11): AuthorRecord, LessonPlanRepository, _plan(), PlanCreationContext, PlanRecord, Any, date, UUID (+3 more)

### Community 130 - "pages/auth.py"
Cohesion: 0.12
Nodes (30): backup_auth_api_request(), backup_login_api_request(), backup_reauthentication_api_request(), plan_api_request(), NiceGUI 服务端 BFF 客户端的公开接缝。, 以请求正文提交两项备用因素，不把秘密放入 URL。, 为当前备用会话取得仅可新增通行密钥的短时证明。, 读取本人最近 20 条内建安全事件，不产生已读状态。 (+22 more)

### Community 131 - "test_ai_model_profiles.py"
Cohesion: 0.14
Nodes (18): AiClientError, RuntimeError, AiJobAuthorizer, AiJobRetry, AiJobRunner, RuntimeError, AI 生成任务的冻结上下文执行器与 PostgreSQL 状态适配器。, 通知消息代理按权威任务给出的退避时间重投。 (+10 more)

### Community 132 - "identity/service.py"
Cohesion: 0.13
Nodes (14): Broker, UUID, 仅投递 job_id 的提示词测试分发边界。, RedisJobDispatcher, Dispatcher, _FrozenTask, Protocol, _TaskSpec (+6 more)

### Community 133 - "MemoryLoginThrottle"
Cohesion: 0.17
Nodes (10): _digest(), MemoryLoginThrottle, datetime, Redis, timedelta, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision (+2 more)

### Community 134 - "PostgresPromptTestStore"
Cohesion: 0.23
Nodes (6): _native_url(), PostgresPromptTestStore, Any, datetime, UUID, 提示词测试 Worker 的 PostgreSQL 权威状态适配器。

### Community 135 - "ActorFixture"
Cohesion: 0.22
Nodes (9): datetime, Protocol, UUID, 按 PostgreSQL 权威状态重投 pending/过期租约任务。, recover_prompt_test_jobs(), RecoveryStore, Any, 向已注册 actor 投递唯一的 job_id。 (+1 more)

### Community 136 - "IdentitySecretKeyProvider"
Cohesion: 0.10
Nodes (28): _aad(), decrypt_totp_secret(), decrypt_totp_secret_with_provider(), encrypt_totp_secret(), encrypt_totp_secret_with_provider(), FileIdentitySecretKeyProvider, Path, UUID (+20 more)

### Community 137 - "JobRepository"
Cohesion: 0.19
Nodes (18): pytest, ai_admin_client(), _profile_payload(), Any, TestClient, _resolver(), test_admin_creates_write_only_masked_profile_and_cannot_read_key(), test_call_fields_increment_revision_but_display_and_limits_do_not() (+10 more)

### Community 138 - "_Connection"
Cohesion: 0.11
Nodes (20): MonkeyPatch, settings_database(), test_age_group_seed_is_fixed_and_idempotent(), test_area_constraints_allow_empty_collections_but_reject_duplicate_names(), test_postgresql_enforces_semester_and_lead_teacher_uniqueness(), test_settings_migration_creates_the_five_tenant_scoped_tables(), test_settings_relations_use_composite_tenant_foreign_keys(), lesson_plan_database() (+12 more)

### Community 139 - "SessionUser"
Cohesion: 0.42
Nodes (6): datetime, _session(), test_backup_reauthentication_only_authorizes_add_passkey_for_five_minutes(), test_expired_backup_reauthentication_cannot_add_passkey(), test_recent_webauthn_proof_satisfies_high_risk_identity_boundary(), test_restricted_enrollment_session_cannot_enter_business_routes()

### Community 140 - "ProviderNeutralAiClient"
Cohesion: 0.21
Nodes (13): 只接收 job_id 的 Dramatiq actor 与 PostgreSQL 恢复扫描。, _pinned_url(), Any, OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。, _addresses(), AiUrlPolicyError, Resolver, ValueError (+5 more)

### Community 142 - "api/test_prompt_test_jobs.py"
Cohesion: 0.33
Nodes (17): FailingDispatcher, prompt_job_client(), _provision_model_and_version(), Any, TestClient, _resolver(), test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure(), test_draft_version_can_be_tested_before_publication() (+9 more)

### Community 143 - "test_settings_smoke.py"
Cohesion: 0.17
Nodes (16): navigation_for_capabilities(), 按 API capabilities 生成导航。, class_areas_page_text(), settings_page_text(), test_navigation_is_derived_from_current_api_capabilities(), BrowserActor, _free_port(), _m3_services() (+8 more)

### Community 144 - "Dev 跨机器开发交接（2026-07-24）"
Cohesion: 0.11
Nodes (18): 1. 恢复时先确认的基线, 2.1 已完成, 2.2 已验证门禁, 2.3 尚未实现, 2. 当前实现进度, 3. 下一步：只从 T016 开始, 4.1 项目必须项, 4.2 当前主机已发现的工具缺口 (+10 more)

### Community 145 - ".authenticate_with_backup"
Cohesion: 0.17
Nodes (20): hash_password(), password_needs_rehash(), password_violations(), Path, verify_password(), _weak_passwords(), create_access_token(), decode_access_token() (+12 more)

### Community 146 - "test_local_development_profiles.py"
Cohesion: 0.22
Nodes (7): API 请求 ID 与追踪 ID 中间件。, _request_id(), RequestContextMiddleware, ASGIApp, Receive, Scope, Send

### Community 147 - "test_auth_smoke.py"
Cohesion: 0.12
Nodes (27): login_page_text(), users_page_text(), BrowserContext, candidate_totp_counters(), _counter(), generate_totp(), _hotp(), RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。 (+19 more)

### Community 148 - "AiGenerationResultRepository"
Cohesion: 0.33
Nodes (8): Collection, parse_trusted_bff_peers(), 只接受显式配置的回环 BFF socket peer。, resolve_client_ip(), test_configured_loopback_bff_peer_can_supply_internal_client_ip(), test_non_loopback_peer_cannot_be_configured_as_trusted_bff(), test_trusted_bff_peers_are_empty_until_explicitly_configured(), test_untrusted_peer_cannot_supply_internal_client_ip()

### Community 149 - "test_identity_isolation.py"
Cohesion: 0.13
Nodes (30): create_completed_ai_preview(), provision_enabled_ai_model(), TestClient, UUID, _event(), TestClient, test_ai_audit_event_codes_cover_creation_retries_result_reject_and_adopt(), test_generation_reject_adopt_and_retry_write_sanitized_audit_rows() (+22 more)

### Community 150 - "PlanContentV1"
Cohesion: 0.52
Nodes (6): _job(), _plan(), MonkeyPatch, M6 教案栏目内预览与可恢复状态的 NiceGUI RED 冒烟。, test_generation_autosaves_before_submit_and_renders_accessible_status(), test_reload_restores_preview_reject_keeps_original_and_failed_column_retries()

### Community 152 - "create_app"
Cohesion: 0.21
Nodes (20): create_app(), HealthDependencies, check(), dependencies(), MonkeyPatch, Path, test_database_failure_returns_stable_503_code(), test_default_calendar_check_degrades_when_library_is_unavailable() (+12 more)

### Community 153 - "test_ai_preview_lifecycle.py"
Cohesion: 0.31
Nodes (12): _native_url(), NoCallExpectedClient, TestClient, UUID, _snapshot_count(), test_batch_and_nonfailed_ai_jobs_reject_explicit_retry(), test_cross_tenant_failed_job_is_hidden_from_retry(), test_expiration_scheduler_transitions_due_previews_once() (+4 more)

### Community 154 - "test_ai_key_rotation.py"
Cohesion: 0.35
Nodes (10): _candidate(), FakeStore, _modules(), Any, UUID, test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it(), test_rotation_dry_run_and_repeated_batch_are_zero_write(), test_rotation_uses_stable_cursor_and_does_not_change_call_revision() (+2 more)

### Community 155 - "build_health_dependencies"
Cohesion: 0.24
Nodes (13): _ai_unconfigured(), authenticated_session(), build_health_dependencies(), _calendar_library_available(), _database_check(), _file_check(), _path_check(), IdentityServiceDependency (+5 more)

### Community 156 - "contracts/jobs.py"
Cohesion: 0.43
Nodes (3): job_query_service(), JobQueryService, UUID

### Community 157 - "pages/settings.py"
Cohesion: 0.18
Nodes (8): prompt_test_status(), PromptTestStatus, 异步提示词测试的稳定中文状态与无障碍语义。, should_poll(), prompt_edit_version_id(), prompt_test_record_text(), 刷新时优先恢复未发布草稿，避免用已发布正文覆盖编辑态。, 将服务端已脱敏的测试运行渲染为可读历史记录。

### Community 158 - "web/__main__.py"
Cohesion: 0.25
Nodes (11): main(), 仅绑定回环地址的 NiceGUI Web 入口。, _require_loopback(), _validate_cookie_security(), configure_logging(), EventDict, 递归清除 Web 日志中的凭证和内部 URL。, _redact() (+3 more)

### Community 159 - "prompts/service.py"
Cohesion: 0.18
Nodes (11): UUID, AuditEventReference, IdentityAuditEventCode, IdentityAuditMetadata, StrEnum, 身份阶段的稳定审计事件代码与最小资源引用。, 身份审计只允许承载最小、严格类型化的非秘密元数据。, ResourceReference (+3 more)

### Community 160 - "ports.py"
Cohesion: 0.21
Nodes (9): AiClient, Clock, DependencyCheck, JobBroker, datetime, Protocol, UUID, M1 外部边界所需的最小 Protocol。 (+1 more)

### Community 161 - "test_backup_maintenance.py"
Cohesion: 0.40
Nodes (12): _change_actor_to_teacher(), _enable_backup(), _identity_service(), _login_with_backup(), _native_url(), TestClient, test_admin_cannot_disable_required_backup_authentication(), test_backup_maintenance_and_security_events_require_authentication() (+4 more)

### Community 162 - "test_invitations.py"
Cohesion: 0.33
Nodes (13): _base64url(), _create_teacher(), _issue(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes(), test_invitation_is_single_use_reissuable_and_revocable() (+5 more)

### Community 163 - "test_runtime_openapi.py"
Cohesion: 0.40
Nodes (13): _assert_operation_contract(), _canonical_schema(), _effective_security(), _operations(), _parameter_shape(), Any, 运行时 OpenAPI 与冻结身份契约的一致性门禁。, _request_schema() (+5 more)

### Community 164 - "test_settings_permissions.py"
Cohesion: 0.19
Nodes (21): ActorFixture, TestClient, test_admin_is_restricted_until_complete_backup_enrollment(), test_backup_status_and_enrollment_require_authentication(), test_enrollment_requires_password_and_totp_together_and_is_single_use(), test_expired_enrollment_cannot_enable_backup_auth(), test_new_enrollment_invalidates_the_previous_pending_enrollment(), test_replacing_enabled_material_revokes_only_related_backup_sessions() (+13 more)

### Community 165 - "pages/plans.py"
Cohesion: 0.67
Nodes (3): save_status(), SaveStatus, SaveState

### Community 166 - "validate_prompt_result_schema"
Cohesion: 0.20
Nodes (21): AiTaskCode, JsonValue, canonical_json_sha256(), generation_input_sha256(), 对 JSON 值进行稳定序列化并计算 SHA-256。, 计算逐任务实际输入哈希。      ``server_input`` 只应包含该任务白名单内的服务端输入。采用预览时，调用方必须复用任务     创建时冻结的, section_sha256(), AiBatchRequest (+13 more)

### Community 167 - "test_credentials.py"
Cohesion: 0.36
Nodes (12): _base64url(), _insert_credential(), _native_url(), MonkeyPatch, TestClient, UUID, _registration_credential(), test_admin_cannot_revoke_last_active_admin_last_credential() (+4 more)

### Community 168 - "test_plan_ai_contracts.py"
Cohesion: 0.29
Nodes (11): _children(), _contract(), Any, ModuleType, M6 教案 AI 公共契约的 RED 验收。, test_ai_child_succeeded_is_not_a_valid_batch_completion_state(), test_batch_job_projects_zero_attempts_and_rejects_execution_shape(), test_batch_status_is_derived_only_from_exactly_four_children() (+3 more)

### Community 169 - "test_ai_prompt_settings_smoke.py"
Cohesion: 0.19
Nodes (7): _job_status_module(), Any, MonkeyPatch, test_controls_have_keyboard_focus_and_error_label_associations(), test_job_status_recovers_configuration_change_with_chinese_action(), test_job_status_refreshes_until_terminal_and_restores_after_page_reload(), test_settings_controls_call_model_prompt_and_job_public_api_seams()

### Community 170 - "test_auth_contract.py"
Cohesion: 0.21
Nodes (7): APIRoute, Any, _resolve(), _runtime_routes(), test_auth_success_and_logout_lock_two_raw_cookie_headers(), test_runtime_auth_router_matches_frozen_passkey_paths(), test_runtime_auth_success_statuses_match_frozen_contract()

### Community 171 - "test_ai_prompt_repositories.py"
Cohesion: 0.30
Nodes (9): _modules(), Any, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_call_configuration_change_set_matches_the_frozen_revision_rules(), test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup(), test_model_reads_and_writes_are_tenant_scoped(), test_prompt_run_frozen_fields_cannot_be_updated() (+1 more)

### Community 172 - "test_ai_generation_service.py"
Cohesion: 0.29
Nodes (9): _clear_auth_cookies(), _cookie_secure(), csrf(), logout(), Response, _set_auth_cookies(), _encode(), issue_csrf_token() (+1 more)

### Community 173 - "openapi.py"
Cohesion: 0.29
Nodes (9): _apply_operation_contract(), configure_openapi(), _no_content_response(), _operation(), Any, FastAPI, M2 运行时 OpenAPI 的集中契约装配。, 返回缓存后的 M2 运行时 OpenAPI 生成器。 (+1 more)

### Community 174 - "totp.py"
Cohesion: 0.30
Nodes (14): identity_database(), _insert_kindergarten(), _insert_user(), MonkeyPatch, UUID, test_cross_kindergarten_role_assignment_is_rejected_by_composite_foreign_key(), test_refresh_replacement_cannot_cross_kindergarten(), test_refresh_revocation_serializes_with_rotation_and_revokes_the_new_token() (+6 more)

### Community 175 - "test_backup_auth_contract.py"
Cohesion: 0.27
Nodes (6): Any, _resolve(), _runtime_routes(), test_backup_contract_marks_request_and_one_time_response_secrets(), test_runtime_router_exposes_the_user_story_2_endpoints(), test_runtime_router_matches_the_frozen_backup_contract()

### Community 176 - "test_ai_client.py"
Cohesion: 0.44
Nodes (10): _modules(), Any, _resolver(), test_client_caps_retry_after_at_sixty_seconds(), test_client_errors_are_stable_and_never_include_key_or_prompt(), test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin(), test_client_posts_openai_compatible_request_with_fixed_limits(), test_client_rejects_redirects_without_following_them() (+2 more)

### Community 178 - "proxy_request"
Cohesion: 0.29
Nodes (9): BffResponse, proxy_request(), AsyncBaseTransport, 按固定 allowlist 转发请求，并保留响应原始多值头。, MonkeyPatch, test_proxy_ignores_process_proxy_environment(), test_proxy_preserves_auth_set_cookie_as_raw_headers(), test_proxy_preserves_request_and_rebuilds_client_ip() (+1 more)

### Community 179 - "transactional_session"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 180 - "test_workday_service.py"
Cohesion: 0.29
Nodes (6): _module(), MonkeyPatch, test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls(), test_local_result_wins_conflict_and_uses_one_hour_cache(), test_timor_client_enforces_one_total_deadline(), test_unsupported_local_calendar_range_softly_falls_back_to_online()

### Community 181 - "contracts/jobs.py"
Cohesion: 0.22
Nodes (9): get_job(), AdminSessionDependency, UUID, JobQueryServiceDependency, JobStatus, derive_batch_projection(), Job, JobChild (+1 more)

### Community 182 - "canonical_request_fingerprint"
Cohesion: 0.17
Nodes (13): canonical_request_fingerprint(), _normalize_scalar(), 计算覆盖路由、实际资源与语义输入的 canonical SHA-256。, Any, _schema(), test_model_and_job_contracts_freeze_revision_and_stable_errors(), test_prompt_test_contract_exposes_only_redacted_input_summary(), test_prompt_test_fingerprint_changes_across_prompt_codes() (+5 more)

### Community 183 - "US4 栏目级 AI 与教师采用决定权"
Cohesion: 0.25
Nodes (9): AI 输入、提示词、模型与 Schema 冻结上下文, M6 T087–T126 in_progress，T103 为下一项, Batch 父任务不执行且状态由四个子任务派生, AI 外呼前实时重验账号、角色、班级、教案与模型, 栏目 AI 预览、采用、拒绝与重试, 复用共享重试策略与提示词渲染器, T103 AI Runner, 教师是 AI 预览的唯一采用决策者 (+1 more)

### Community 184 - "test_secret_encryption.py"
Cohesion: 0.39
Nodes (8): _context(), _encryption_module(), Any, Path, test_development_key_provider_requires_owner_only_file_outside_repository(), test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution(), test_totp_secret_envelope_round_trips_with_random_96_bit_nonce(), test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce()

### Community 185 - "0007_ai_prompts_jobs.py"
Cohesion: 0.36
Nodes (6): Any, Column, 建立 AI 模型、提示词与 PostgreSQL 权威任务基础。, _seed_defaults(), _timestamps(), upgrade()

### Community 186 - "Alembic"
Cohesion: 0.20
Nodes (5): Alembic, Any, Column, _timestamps(), upgrade()

### Community 188 - "test_openapi_document.py"
Cohesion: 0.39
Nodes (7): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_document_is_valid_31(), test_openapi_keeps_nicegui_as_the_only_browser_entry(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 190 - "test_content_v1.py"
Cohesion: 0.54
Nodes (7): _contracts(), _schemas(), test_completeness_is_independent_from_progressive_schema_validation(), test_empty_v1_content_supports_progressive_manual_editing(), test_reflection_is_nfkc_normalized_and_limited_to_200_codepoints(), test_statement_and_question_punctuation_are_strictly_chinese(), test_unknown_fields_and_unknown_content_versions_are_not_silently_coerced()

### Community 191 - "test_ai_key_envelope.py"
Cohesion: 0.39
Nodes (7): _module(), Any, Path, test_ai_key_envelope_rejects_tampering_and_cross_profile_substitution(), test_ai_key_envelope_round_trips_with_random_96_bit_nonce(), test_file_key_provider_requires_owner_only_files_outside_repository(), test_static_key_provider_reads_old_key_but_writes_with_active_key()

### Community 192 - "test_ai_model_url_policy.py"
Cohesion: 0.57
Nodes (7): _module(), Any, _resolver(), test_policy_accepts_only_allowlisted_public_https_and_checks_every_address(), test_policy_detects_dns_rebinding_before_connect(), test_policy_rejects_non_https_and_non_public_networks(), test_policy_requires_explicit_server_allowlist()

### Community 193 - "test_prompt_catalog.py"
Cohesion: 0.43
Nodes (7): _module(), Any, test_catalog_assigns_task_specific_minimum_variable_whitelists(), test_catalog_freezes_seven_codes_whitelists_schemas_and_hashes(), test_catalog_input_validation_excludes_teacher_identity_and_unknown_fields(), test_catalog_result_schemas_are_strict(), test_catalog_result_schemas_match_the_frozen_openapi_shapes()

### Community 194 - "test_backup_auth_smoke.py"
Cohesion: 0.33
Nodes (5): security_event_text(), MonkeyPatch, test_backup_login_and_reauthentication_submit_secrets_only_in_post_bodies(), test_security_event_messages_cover_the_frozen_event_codes(), test_security_events_use_read_only_same_origin_api()

### Community 195 - "test_settings_isolation.py"
Cohesion: 0.38
Nodes (7): _assert_queries_are_tenant_scoped(), UUID, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_class_area_reads_filter_by_kindergarten_and_class(), test_class_area_writes_filter_by_kindergarten_and_class(), test_top_level_setting_reads_filter_by_kindergarten()

### Community 196 - "normalize_username"
Cohesion: 0.39
Nodes (5): normalize_phone(), normalize_username(), test_invalid_phone_is_rejected(), test_phone_is_mainland_e164_or_empty(), test_username_is_nfkc_trimmed_and_lowercase()

### Community 198 - "test_0005_password_totp_backup_login.py"
Cohesion: 0.46
Nodes (7): Script, _backup_revision(), MonkeyPatch, test_backup_auth_migration_creates_isolated_credentials_and_enrollments(), test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(), test_backup_auth_revision_follows_settings_and_precedes_lesson_plans(), test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade()

### Community 199 - "0001_identity_and_audit.py"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 200 - "test_password_to_passkey.py"
Cohesion: 0.54
Nodes (7): _assert_passkey_revisions_exist(), _native_url(), MonkeyPatch, test_contract_removes_password_data_and_downgrade_recreates_only_empty_columns(), test_expand_moves_existing_accounts_to_enrollment_and_revokes_old_sessions(), test_passkey_migration_has_explicit_expand_and_contract_boundaries(), _user_columns()

### Community 201 - "0002_passkey_expand.py"
Cohesion: 0.52
Nodes (5): Any, Column, _tenant_identity_columns(), _timestamps(), upgrade()

### Community 202 - "0006_lesson_plans.py"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 203 - "0008_ai_generation_results.py"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 204 - "US6 固定 Word 导出与重新下载"
Cohesion: 0.40
Nodes (6): 固定 Word 模板原件哈希与样式完整性, templates/teacherplan/teacherplan.docx, 集体活动拆分后再新增环节的两阶段流程, US5 集体活动原始教案处理, US6 固定 Word 导出与重新下载, 固定模板 Word 导出、历史与重新授权下载

### Community 206 - "_totp_module"
Cohesion: 0.53
Nodes (5): Any, test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps(), test_totp_rejects_the_same_or_earlier_counter_after_success(), test_totp_secret_is_unique_high_entropy_base32(), _totp_module()

### Community 207 - "Q: 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。, Source Nodes

### Community 208 - "Q: M5 完成后到 M4 的当前依赖路径是什么？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: M5 完成后到 M4 的当前依赖路径是什么？, Source Nodes

### Community 209 - "US1 M2 认证、授权与身份审计"
Cohesion: 0.50
Nodes (5): 园所、学期、班级、教师关系与区域设置, kindergarten_id 园所隔离, US1 M2 认证、授权与身份审计, US1 M3 首期必要设置, WebAuthn 身份安全与会话撤销

### Community 210 - "_run"
Cohesion: 0.60
Nodes (4): CompletedProcess, _run(), test_bootstrap_cli_exposes_rotation_without_master_key_arguments(), test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets()

### Community 212 - "test_calendar.py"
Cohesion: 0.70
Nodes (4): _calendar(), test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic(), test_out_of_semester_week_number_and_text_are_both_empty(), test_semester_start_week_is_week_one_and_increments_each_monday()

### Community 213 - "test_prompt_renderer.py"
Cohesion: 0.48
Nodes (6): _module(), Any, test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(), test_renderer_fails_for_missing_variable_before_external_call(), test_renderer_rejects_every_non_frozen_placeholder_form(), test_renderer_uses_stable_json_and_never_recursively_renders_values()

### Community 220 - "0005_password_totp_backup_login.py"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 221 - "test_0001_identity.py"
Cohesion: 0.50
Nodes (4): migrated_database(), MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds(), test_identity_migration_is_idempotent()

## Knowledge Gaps
- **189 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+184 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **91 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `班级与教师配置` (2× useful, score=1.352895454)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IdentityRepository` connect `Backup Login Authentication` to `validate_prompt_result_schema`, `IdentitySecretKeyProvider`, `WebAuthn`, `test_backup_authentication.py`, `issue_secret`, `IdentityService`, `totp.py`, `.authenticate_with_backup`, `routers/prompts.py`, `routers/users.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `IdentityError` connect `IdentityService` to `WorkdayResult`, `identity/service.py`, `IdentitySecretKeyProvider`, `Requirements & Design Review`, `SessionUser`, `Repository Structure & Docs`, `create_app`, `build_health_dependencies`, `contracts/jobs.py`, `prompts/service.py`, `test_backup_maintenance.py`, `validate_prompt_result_schema`, `test_ai_generation_service.py`, `Redis Cache`, `WebAuthn`, `PromptRepository`, `issue_secret`, `ContractModel`, `ai_generation.py`, `lesson_plans/service.py`, `AiKeyEnvelope`, `routers/users.py`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `ActorFixture` connect `test_settings_permissions.py` to `test_backup_maintenance.py`, `test_invitations.py`, `pytest Testing`, `validate_prompt_result_schema`, `test_credentials.py`, `IdentitySecretKeyProvider`, `JobRepository`, `test_backup_authentication.py`, `api/test_prompt_test_jobs.py`, `IdentityService`, `issue_secret`, `test_ai_job_recovery.py`, `provision_editable_plan_context`, `test_identity_isolation.py`, `csrf_headers`, `test_ai_preview_lifecycle.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `ActorFixture` (e.g. with `StaticIdentitySecretKeyProvider` and `IdentityService`) actually correct?**
  _`ActorFixture` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `IdentityError` (e.g. with `create_app()` and `HealthDependencies`) actually correct?**
  _`IdentityError` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 134 inferred relationships involving `ContractModel` (e.g. with `AuditEventReference` and `IdentityAuditEventCode`) actually correct?**
  _`ContractModel` has 134 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `SessionUser` (e.g. with `HealthDependencies` and `AuditRepository`) actually correct?**
  _`SessionUser` has 27 INFERRED edges - model-reasoned connections that need verification._