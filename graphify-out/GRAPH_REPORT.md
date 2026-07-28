# Graph Report - .  (2026-07-28)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 3076 nodes · 8776 edges · 278 communities (188 shown, 90 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 760 edges (avg confidence: 0.54)
- Token cost: 13,255 input · 10,398 output

## Graph Freshness
- Built from commit: `8113ee2a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Backup Credential Management
- AI Model & Age Group Settings
- Identity Service & Audit
- Auth Flow & CSRF
- Job Message Dispatching
- API Security Config
- Database Schema Models
- Admin Init & Audit
- Auth Rate Limiting
- AI Job Execution
- AI Prompt Schemas
- Identity Credential Models
- Job Dispatching
- Prompt Test Actor
- AI Key Rotation
- Credential Challenge
- WebAuthn Auth Tests
- Backup Auth API Client
- Session & Passkey Tests
- Lesson Plan Endpoints
- Challenge Issuance
- Prompt Test Store
- Batch Generation Tests
- Settings Repository
- User Management
- Architecture Boundaries
- Prompt Test Worker Tests
- Cross-Artifact Consistency
- Prompt Management
- Settings Service
- Workday Calendar
- Architecture Baseline
- Lesson Plan Repository
- AI Model Service
- Lesson Plan Service
- AI Client Transport
- Prompt Repository
- Core Domain Contracts
- Settings Schema Tests
- Backup Enrollment Tests
- Job Status API
- Login Throttle
- TOTP Encryption
- Dev Environment Spec
- Job Repository
- Prompt Renderer
- Teacher Settings Validation
- Prompt Service
- Auth Browser Tests
- Prompt Test API Tests
- Lesson Plan Content
- API App Setup
- Navigation Tests
- AI Result Repository
- Prompt Test Store
- Auth Isolation Tests
- Backup Maintenance Tests
- Lesson Plan UI Tests
- Shell Scripts
- Admin Recovery Tests
- Health Check
- Health Checks
- AI Client SSRF
- AI Preview Tests
- Key Rotation Tests
- Development Rules
- Job Status UI
- NiceGUI Web App
- Password Management
- Secret Tokens
- Ports & Interfaces
- AI Safety & Lifecycle
- AI Adoption Tests
- Invitation Tests
- OpenAPI Contract Tests
- Settings Permissions
- AI Schema Tests
- RED Gate Contracts
- Credential Tests
- Identity Isolation Tests
- Prompt Settings UI
- Auth Contract Tests
- Prompt Repository Tests
- Generation Service Tests
- Project Milestones
- OpenAPI Assembly
- Dev Handoff
- TOTP Primitive
- Admin CLI Tests
- Backup Auth Contract
- AI Client Tests
- Input Hashing
- Request Context Middleware
- BFF Proxy
- Session & Transaction
- Client IP Trust
- Passkey Authorization
- Workday Cache
- Model Profile Tests
- Settings Isolation Tests
- Workday Service Tests
- Development Branch & Docs
- Security & System Boundaries
- Milestones & User Stories
- Secret Encryption Tests
- Auth & Settings Baseline
- AI Prompts Migration
- Content Completeness Schemas
- Backup Auth Migration Tests
- Daily Plan User Stories
- AI Prompt Contract Tests
- OpenAPI Document Tests
- Password to Passkey Tests
- Content V1 Schema Tests
- AI Key Envelope Tests
- AI Model URL Policy Tests
- Prompt Catalog Tests
- Tech Stack & Dependencies
- Job Query Service
- Security Event Tests
- Passkey Expand Migration
- Project Governance & Boundaries
- Service Components & Tests
- Prompt Renderer Tests
- Workday Cache Migration
- Identity & Audit Migration
- Settings Migration
- Password TOTP Migration
- Lesson Plans Migration
- AI Gen Results Migration
- Word Template & Export
- User Contract Tests
- TOTP Tests
- Service Roles & Boundaries
- Infrastructure Components
- Development Workflow & Review
- AI Key Provider Methods
- Feature Branch Script
- Kindergarten Auth & Settings
- AI Key Rotation CLI Tests
- Identity Migration Tests
- Calendar Tests
- Git Branch Roles
- Save Status Module
- Dev Environment & CI
- Core Database Tables
- Schema Isolation & Keys
- Content Snapshot Hashing
- Backup Login Feature
- Lesson Plan Contract Tests
- Calendar Fixture
- Clock Fixture
- Redis Fixture
- Knowledge Graph Tools
- AI Key Provider
- Migration Dependency Order
- Json Schema Utilities
- Lease Expiration
- Daily Activity Word Layout
- AI Client Fixture
- Child Manager App
- Background Worker
- AI & Job Tables
- AI Model Capabilities
- Prompt Tables
- Roles & Permissions Tables
- Database Foundation
- Common Passwords List
- Backend API Module
- Shared Contracts Module
- Prerequisites Check Script
- Setup Plan Script
- Setup Tasks Script
- Web Tests Module
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
- Bootstrap Init
- Class Areas
- Class Teachers
- Classes
- Activity Plan Exports
- Activity Plan Snapshots
- Daily Activity Plans
- ID Verification Approvals
- Snapshot Immutability
- JSONB Versioning
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
- JSONB Content Boundary
- Activity Plan Authors
- Activity Plan Exports
- Activity Plan Snapshots
- ID Verification Approvals
- Lesson Plan Sources
- Prompt Test Runs
- Recovery Codes
- Refresh Tokens
- Semesters
- WebAuthn Challenges
- WebAuthn Credentials
- Workday Cache
- App Owned Transactions
- External Key Source
- M5-M4 Dependency Path
- Child Manager
- PostgreSQL Database
- Dev Workflow & Quality
- Governance
- Technical Constraints
- Activity Plan Checklist
- Password TOTP Backup Login

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
- `Speckit Tasks to Issues` --semantically_similar_to--> `Implementation Issue Template`  [INFERRED] [semantically similar]
  .agents/skills/speckit-taskstoissues/SKILL.md → .github/ISSUE_TEMPLATE/implementation.yml
- `Retired Dual Agent Protocol` --semantically_similar_to--> `Design to Implement Workflow`  [INFERRED] [semantically similar]
  docs/development/dual-agent-development.md → CONTRIBUTING.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **All Task Groups in M3A Milestone** — milestone_m3a, task_group_t001_t002, task_group_t003_t009, task_group_t010_t015, task_group_t016_t019, task_group_t020_t029, task_group_t030_t034 [EXTRACTED 1.00]
- **Core Technology Stack and Dependencies** — AGENTS_python_version, AGENTS_postgresql, AGENTS_sqlalchemy, AGENTS_alembic, AGENTS_pyproject_toml, AGENTS_uv_lock [EXTRACTED 0.95]
- **Monorepo Service Architecture** — AGENTS_nicegui_web, AGENTS_fastapi_api, AGENTS_background_worker, AGENTS_shared_contracts [EXTRACTED 0.95]
- **Code and Knowledge Analysis Toolset** — AGENTS_graphify_knowledge_graph, AGENTS_codebase_memory_mcp, AGENTS_codegraph, AGENTS_tool_priority [EXTRACTED 0.90]
- **Setup 到 M8 的阶段执行链** — specs_001_daily_activity_plan_tasks_setup, specs_001_daily_activity_plan_tasks_foundational, specs_001_daily_activity_plan_tasks_us1_m2, specs_001_daily_activity_plan_tasks_us1_m3, specs_001_daily_activity_plan_tasks_us1_m3a, specs_001_daily_activity_plan_tasks_us2_manual_plan, specs_001_daily_activity_plan_tasks_us3_ai_prompt_settings, specs_001_daily_activity_plan_tasks_us4_section_ai, specs_001_daily_activity_plan_tasks_us5_group_activity, specs_001_daily_activity_plan_tasks_us6_word_export, specs_001_daily_activity_plan_tasks_us7_audit_degradation, specs_001_daily_activity_plan_tasks_polish_m8 [EXTRACTED 1.00]
- **三个独立运行单元** — specs_001_daily_activity_plan_tasks_api_runtime, specs_001_daily_activity_plan_tasks_worker_runtime, specs_001_daily_activity_plan_tasks_web_runtime [EXTRACTED 1.00]
- **用户故事 RED、最小实现与 Checkpoint 模式** — specs_001_daily_activity_plan_tasks_us1_m2, specs_001_daily_activity_plan_tasks_us1_m3, specs_001_daily_activity_plan_tasks_us2_manual_plan, specs_001_daily_activity_plan_tasks_us3_ai_prompt_settings, specs_001_daily_activity_plan_tasks_us4_section_ai, specs_001_daily_activity_plan_tasks_us5_group_activity, specs_001_daily_activity_plan_tasks_us6_word_export, specs_001_daily_activity_plan_tasks_us7_audit_degradation [EXTRACTED 1.00]
- **Daily Activity Plan Full Pipeline** — child_manager_domain_settings, child_manager_domain_lesson_plans, child_manager_domain_word_export [EXTRACTED 1.00]
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
- **Password and TOTP Backup Login Baseline** — specs_002_password_totp_backup_login_spec_backup_login_feature, specs_002_password_totp_backup_login_plan_backup_login_implementation_plan, specs_002_password_totp_backup_login_data_model_backup_auth_data_model, specs_002_password_totp_backup_login_contracts_openapi_backup_login_api_fragment [EXTRACTED 1.00]

## Communities (278 total, 90 thin omitted)

### Community 0 - "Backup Credential Management"
Cohesion: 0.07
Nodes (17): _backup_credential(), _backup_enrollment(), BackupCredentialRecord, BackupEnrollmentRecord, BackupRevocationResult, BackupSecurityEventRecord, ChallengeRecord, IdentityRepository (+9 more)

### Community 1 - "AI Model & Age Group Settings"
Cohesion: 0.08
Nodes (65): AgeGroup, AiModelProfile, AiModelServiceDependency, _age_group(), _ai_model(), _area(), _class(), create_ai_model_profile() (+57 more)

### Community 2 - "Identity Service & Audit"
Cohesion: 0.13
Nodes (14): identity_service(), AuditRepository, FileIdentitySecretKeyProvider, 开发环境读取仓库外、仅属主可读的 32 字节二进制密钥文件。, IdentityError, IdentityService, ManagedUser, Exception (+6 more)

### Community 3 - "Auth Flow & CSRF"
Cohesion: 0.13
Nodes (66): _allowed_origins(), authenticate_with_password_and_totp(), authentication_start(), authentication_verify(), backup_authentication_status(), bootstrap_options(), bootstrap_verify(), _check_public_throttle() (+58 more)

### Community 4 - "Job Message Dispatching"
Cohesion: 0.10
Nodes (50): JobMessage, Redis 中唯一允许传递的最小任务消息。, SimpleNamespace, _insert_job(), _insert_other_tenant_plan(), _insert_result(), _native_url(), _provision_dependencies() (+42 more)

### Community 5 - "API Security Config"
Cohesion: 0.05
Nodes (50): main(), AppSettings, global_security_ready(), BaseModel, 拒绝在非开发环境或非回环地址关闭 Cookie Secure。, 验证进程启动时的 Cookie 与监听地址组合。, JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。, validate_cookie_security() (+42 more)

### Community 6 - "Database Schema Models"
Cohesion: 0.10
Nodes (40): DeclarativeBase, AuditEvent, Base, AccountInvitation, AccountRecoveryRequest, BackupAuthCredential, BackupAuthEnrollment, BootstrapInitialization (+32 more)

### Community 7 - "Admin Init & Audit"
Cohesion: 0.08
Nodes (36): ArgumentParser, UUID, activate_initialization(), migrate_passkeys(), _native_url(), datetime, UUID, 首位管理员的部署控制台初始化与双人核验激活。 (+28 more)

### Community 8 - "Auth Rate Limiting"
Cohesion: 0.10
Nodes (32): MemoryAuthThrottle, datetime, Redis, timedelta, 公开身份 ceremony 的来源限流公共 seam。, 按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。, 多进程 API 使用的 Redis 固定窗口实现。, RedisAuthThrottle (+24 more)

### Community 9 - "AI Job Execution"
Cohesion: 0.09
Nodes (21): AiExecutionContext, AiJobAuthorizer, AiJobRetry, AiJobRunner, AiJobStore, AiJobStoreProtocol, Any, datetime (+13 more)

### Community 10 - "AI Prompt Schemas"
Cohesion: 0.28
Nodes (38): EditableContent, prompt_spec(), PromptSpec, BaseModel, 固定提示词目录、输入与结果 Schema 路由。, _spec(), validate_prompt_result(), AiAreaGame (+30 more)

### Community 11 - "Identity Credential Models"
Cohesion: 0.08
Nodes (42): ContractModel, BaseModel, ExportReference, AdminCredentialRevocationResult, AuthenticationCredential, AuthenticationCredentialResponse, AuthenticationPublicKey, AuthenticationResult (+34 more)

### Community 12 - "Job Dispatching"
Cohesion: 0.12
Nodes (21): Broker, UUID, 仅投递 job_id 的提示词测试分发边界。, RedisJobDispatcher, AiGenerationAcceptance, AiGenerationService, dispatch_after_commit(), Dispatcher (+13 more)

### Community 13 - "Prompt Test Actor"
Cohesion: 0.09
Nodes (27): Actor, build_prompt_test_executor(), Broker, datetime, Protocol, UUID, 只接收 job_id 的 Dramatiq actor 与 PostgreSQL 恢复扫描。, 按 PostgreSQL 权威状态重投 pending/过期租约任务。 (+19 more)

### Community 14 - "AI Key Rotation"
Cohesion: 0.15
Nodes (23): UUID, run_rotation(), _aad(), AiKeyEnvelope, decrypt_api_key(), decrypt_api_key_with_provider(), encrypt_api_key(), encrypt_api_key_with_provider() (+15 more)

### Community 15 - "Credential Challenge"
Cohesion: 0.12
Nodes (25): ChallengePurpose, StrEnum, _credential(), CredentialRecord, AuthResult, _challenge_digest(), _client_challenge(), _decode_base64url() (+17 more)

### Community 16 - "WebAuthn Auth Tests"
Cohesion: 0.14
Nodes (37): csrf_headers(), _base64url(), _credential(), MonkeyPatch, TestClient, _registration_credential(), test_authentication_options_are_username_less_and_browser_ready(), test_authentication_options_do_not_increment_failure_limit() (+29 more)

### Community 17 - "Backup Auth API Client"
Cohesion: 0.12
Nodes (30): backup_auth_api_request(), backup_login_api_request(), backup_reauthentication_api_request(), plan_api_request(), NiceGUI 服务端 BFF 客户端的公开接缝。, 以请求正文提交两项备用因素，不把秘密放入 URL。, 为当前备用会话取得仅可新增通行密钥的短时证明。, 读取本人最近 20 条内建安全事件，不产生已读状态。 (+22 more)

### Community 18 - "Session & Passkey Tests"
Cohesion: 0.10
Nodes (27): current_session(), AuthenticatedSessionDependency, pytest, admin_client(), passkey_client(), MonkeyPatch, TestClient, 通过 FastAPI 身份依赖注入建立已 step-up 管理员，不借用密码登录。 (+19 more)

### Community 19 - "Lesson Plan Endpoints"
Cohesion: 0.15
Nodes (36): archive_plan(), autosave_plan(), get_plan(), list_plans(), list_snapshots(), open_plan(), _plan(), CurrentSessionDependency (+28 more)

### Community 20 - "Challenge Issuance"
Cohesion: 0.10
Nodes (34): ChallengeBinding, ChallengeRecord, consume_challenge(), issue_challenge(), IssuedChallenge, datetime, WebAuthn ceremony challenge 的公共领域 seam。, 签发绑定上下文、五分钟有效且只保存摘要的 challenge。 (+26 more)

### Community 21 - "Prompt Test Store"
Cohesion: 0.11
Nodes (16): _native_url(), datetime, 提示词测试 Worker 的 PostgreSQL 权威状态适配器。, CurrentModelCallProfile, ProfileCallLimiter, PromptTestAuthorizer, PromptTestExecutionContext, PromptTestRetry (+8 more)

### Community 22 - "Batch Generation Tests"
Cohesion: 0.17
Nodes (33): provision_enabled_ai_model(), provision_editable_plan_context(), date, TestClient, TestClient, test_generation_reject_adopt_and_retry_write_sanitized_audit_rows(), _idempotent_headers(), TestClient (+25 more)

### Community 23 - "Settings Repository"
Cohesion: 0.14
Nodes (12): AgeGroupRecord, AreaInput, AreaRecord, ClassRecord, KindergartenRecord, date, UUID, 园所范围设置的 PostgreSQL Repository。 (+4 more)

### Community 24 - "User Management"
Cohesion: 0.19
Nodes (32): activate(), create_user(), credential_revoke(), credentials(), deactivate(), get_user(), _invitation(), invitation_issue() (+24 more)

### Community 25 - "Architecture Boundaries"
Cohesion: 0.08
Nodes (34): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+26 more)

### Community 26 - "Prompt Test Worker Tests"
Cohesion: 0.15
Nodes (20): _context(), FakeAuthorizer, FakeClient, FakeStore, _modules(), Any, datetime, UUID (+12 more)

### Community 27 - "Cross-Artifact Consistency"
Cohesion: 0.07
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+25 more)

### Community 28 - "Prompt Management"
Cohesion: 0.16
Nodes (32): alias, clear_prompt_tests(), create_prompt_test(), _definition(), get_prompt(), get_prompt_test(), get_prompt_version(), _job() (+24 more)

### Community 29 - "Settings Service"
Cohesion: 0.23
Nodes (9): settings_service(), IntegrityError, NoReturn, 所有读写都在 SQL 中显式携带 ``kindergarten_id``。, SettingsRepository, UUID, 合并身份能力与基于当前班级关系实时计算的设置能力。, _required_display_name() (+1 more)

### Community 30 - "Workday Calendar"
Cohesion: 0.12
Nodes (23): map_timor_payload(), AsyncBaseTransport, date, TimorWorkdayClient, WorkdayResult, 园所范围工作日缓存 Repository。, combine_workday_results(), date (+15 more)

### Community 31 - "Architecture Baseline"
Cohesion: 0.07
Nodes (32): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+24 more)

### Community 32 - "Lesson Plan Repository"
Cohesion: 0.17
Nodes (11): AuthorRecord, LessonPlanRepository, _plan(), PlanCreationContext, PlanRecord, Any, date, UUID (+3 more)

### Community 33 - "AI Model Service"
Cohesion: 0.17
Nodes (13): ai_model_service(), AiModelService, _display(), _key(), _native_url(), UUID, AI 模型档案生命周期与调用配置 revision 事务。, _ai_profile() (+5 more)

### Community 34 - "Lesson Plan Service"
Cohesion: 0.26
Nodes (10): lesson_plan_service(), LessonPlanService, OpenPlanResult, PlanView, _PlanViewSeed, date, UUID, 完成单一用例响应；外网解析发生在业务事务关闭之后。 (+2 more)

### Community 35 - "AI Client Transport"
Cohesion: 0.13
Nodes (17): BaseTransport, ProviderNeutralAiClient, Resolver, AiClientError, RuntimeError, AddStepStore, AlwaysTimeoutClient, InvalidAddStepClient (+9 more)

### Community 36 - "Prompt Repository"
Cohesion: 0.20
Nodes (11): _definition(), prompt_test_input_summary(), PromptDefinitionRecord, PromptRepository, PromptTestRunRecord, PromptVersionRecord, Any, UUID (+3 more)

### Community 37 - "Core Domain Contracts"
Cohesion: 0.07
Nodes (29): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, Child Manager Daily Activity API, Identity and Settings Endpoints, Plans, Jobs, and Exports Endpoints, API v1 Contract (+21 more)

### Community 38 - "Settings Schema Tests"
Cohesion: 0.10
Nodes (22): MonkeyPatch, settings_database(), test_age_group_seed_is_fixed_and_idempotent(), test_area_constraints_allow_empty_collections_but_reject_duplicate_names(), test_postgresql_enforces_semester_and_lead_teacher_uniqueness(), test_settings_migration_creates_the_five_tenant_scoped_tables(), test_settings_relations_use_composite_tenant_foreign_keys(), lesson_plan_database() (+14 more)

### Community 39 - "Backup Enrollment Tests"
Cohesion: 0.15
Nodes (25): ActorFixture, TestClient, test_admin_is_restricted_until_complete_backup_enrollment(), test_backup_status_and_enrollment_require_authentication(), test_enrollment_requires_password_and_totp_together_and_is_single_use(), test_expired_enrollment_cannot_enable_backup_auth(), test_new_enrollment_invalidates_the_previous_pending_enrollment(), test_replacing_enabled_material_revokes_only_related_backup_sessions() (+17 more)

### Community 40 - "Job Status API"
Cohesion: 0.12
Nodes (21): get_job(), AdminSessionDependency, UUID, JobQueryServiceDependency, JobStatus, derive_batch_projection(), Job, JobChild (+13 more)

### Community 41 - "Login Throttle"
Cohesion: 0.17
Nodes (10): _digest(), MemoryLoginThrottle, datetime, Redis, timedelta, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision (+2 more)

### Community 42 - "TOTP Encryption"
Cohesion: 0.18
Nodes (19): _aad(), decrypt_totp_secret(), decrypt_totp_secret_with_provider(), encrypt_totp_secret(), encrypt_totp_secret_with_provider(), UUID, TOTP 种子的 AES-256-GCM 信封与数据库外密钥适配器。, 验证信封及 AAD 后返回种子；认证标签失败由 ``AESGCM`` 原样拒绝。 (+11 more)

### Community 43 - "Dev Environment Spec"
Cohesion: 0.08
Nodes (25): 本地开发环境规范, 仅回环开发依赖, 生产拓扑延后, 工作树资源隔离, M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线 (+17 more)

### Community 44 - "Job Repository"
Cohesion: 0.24
Nodes (10): _ai_job(), AiJobRecord, _job(), JobRecord, JobRepository, Any, datetime, PostgreSQL 权威后台任务 Repository。 (+2 more)

### Community 45 - "Prompt Renderer"
Cohesion: 0.15
Nodes (18): Any, validate_prompt_variables(), PromptTemplateError, Any, ValueError, 仅支持固定白名单纯替换词法的提示词渲染器。, render_prompt(), _render_value() (+10 more)

### Community 46 - "Teacher Settings Validation"
Cohesion: 0.16
Nodes (19): TeacherInput, current_semester_selection_is_valid(), lead_teacher_selection_is_valid(), _native_url(), normalize_class_areas(), _normalize_display_name(), _normalize_key(), date (+11 more)

### Community 47 - "Prompt Service"
Cohesion: 0.36
Nodes (3): prompt_service(), PromptService, UUID

### Community 48 - "Auth Browser Tests"
Cohesion: 0.17
Nodes (19): login_page_text(), users_page_text(), BrowserContext, Page, _add_virtual_authenticator(), _auth_cookie_names(), _bootstrap_activate(), _bootstrap_start() (+11 more)

### Community 49 - "Prompt Test API Tests"
Cohesion: 0.33
Nodes (17): FailingDispatcher, prompt_job_client(), _provision_model_and_version(), Any, TestClient, _resolver(), test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure(), test_draft_version_can_be_tested_before_publication() (+9 more)

### Community 50 - "Lesson Plan Content"
Cohesion: 0.13
Nodes (14): AiGroupActivityStep, apply_ai_area_result(), DailyReflection, GroupActivityStep, GroupActivityStepCandidate, LessonPlanReference, 区域名称属于冻结输入；模型只能选择重点指导区域，不能改写区域列表。, 按任务冻结的过程长度校验索引；越界必须进入结构错误重试。 (+6 more)

### Community 51 - "API App Setup"
Cohesion: 0.15
Nodes (14): _auth_throttle(), _error_response(), FastAPI, Request, UUID, FastAPI 应用装配、统一异常转换与健康端点。, _request_id(), JSONResponse (+6 more)

### Community 52 - "Navigation Tests"
Cohesion: 0.18
Nodes (15): navigation_for_capabilities(), 按 API capabilities 生成导航。, class_areas_page_text(), settings_page_text(), BrowserActor, _free_port(), _m3_services(), MonkeyPatch (+7 more)

### Community 53 - "AI Result Repository"
Cohesion: 0.30
Nodes (10): AiGenerationResultRecord, AiGenerationResultRepository, _json_object(), _optional_uuid(), Any, datetime, 同园隔离的 AI 生成结果 Repository。, _record() (+2 more)

### Community 54 - "Prompt Test Store"
Cohesion: 0.30
Nodes (3): PostgresPromptTestStore, Any, UUID

### Community 55 - "Auth Isolation Tests"
Cohesion: 0.25
Nodes (13): MonkeyPatch, UUID, RecordingConnection, RecordingResult, _seed_backup_repository(), test_admin_role_gate_restricts_and_then_releases_webauthn_sessions(), test_backup_credential_reads_are_scoped_to_kindergarten_and_user(), test_backup_version_change_revokes_only_related_sessions() (+5 more)

### Community 56 - "Backup Maintenance Tests"
Cohesion: 0.29
Nodes (15): authenticated_session(), IdentityServiceDependency, Cookie, _change_actor_to_teacher(), _enable_backup(), _identity_service(), _login_with_backup(), _native_url() (+7 more)

### Community 57 - "Lesson Plan UI Tests"
Cohesion: 0.18
Nodes (12): PlanContentV1, MonkeyPatch, test_rendered_plan_editor_has_labelled_status_fields_focus_order_and_touch_targets(), _job(), _plan(), MonkeyPatch, M6 教案栏目内预览与可恢复状态的 NiceGUI RED 冒烟。, test_generation_autosaves_before_submit_and_renders_accessible_status() (+4 more)

### Community 58 - "Shell Scripts"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 59 - "Admin Recovery Tests"
Cohesion: 0.26
Nodes (16): _authentication_credential(), _base64url(), _identity_service(), _native_url(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes() (+8 more)

### Community 60 - "Health Check"
Cohesion: 0.31
Nodes (15): create_app(), HealthDependencies, check(), dependencies(), Path, test_database_failure_returns_stable_503_code(), test_default_dependencies_check_real_local_runtime(), test_each_optional_dependency_only_degrades_ready_response() (+7 more)

### Community 61 - "Health Checks"
Cohesion: 0.23
Nodes (14): _ai_unconfigured(), build_health_dependencies(), _calendar_library_available(), _database_check(), _file_check(), _path_check(), Path, 从进程环境构造真实、无副作用的本地就绪检查。 (+6 more)

### Community 62 - "AI Client SSRF"
Cohesion: 0.26
Nodes (12): _pinned_url(), Any, OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。, _addresses(), AiUrlPolicyError, Resolver, ValueError, AI 模型地址的保存时与连接前 SSRF 防护。 (+4 more)

### Community 63 - "AI Preview Tests"
Cohesion: 0.31
Nodes (12): _native_url(), NoCallExpectedClient, TestClient, UUID, _snapshot_count(), test_batch_and_nonfailed_ai_jobs_reject_explicit_retry(), test_cross_tenant_failed_job_is_hidden_from_retry(), test_expiration_scheduler_transitions_due_previews_once() (+4 more)

### Community 64 - "Key Rotation Tests"
Cohesion: 0.35
Nodes (10): _candidate(), FakeStore, _modules(), Any, UUID, test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it(), test_rotation_dry_run_and_repeated_batch_are_zero_write(), test_rotation_uses_stable_cursor_and_does_not_change_call_revision() (+2 more)

### Community 65 - "Development Rules"
Cohesion: 0.15
Nodes (14): Child Manager Agent Development Rules, Data Model and Kindergarten Isolation, Fact Sources and Conflict Handling, GitHub Issue Execution Scope Fact Source, Kindergarten ID Isolation Field, One-Day Activity Plan Business Invariants, PRD/Specs Architecture Decision Records Fact Source, README Product Overview Fact Source (+6 more)

### Community 66 - "Job Status UI"
Cohesion: 0.18
Nodes (8): prompt_test_status(), PromptTestStatus, 异步提示词测试的稳定中文状态与无障碍语义。, should_poll(), prompt_edit_version_id(), prompt_test_record_text(), 刷新时优先恢复未发布草稿，避免用已发布正文覆盖编辑态。, 将服务端已脱敏的测试运行渲染为可读历史记录。

### Community 67 - "NiceGUI Web App"
Cohesion: 0.25
Nodes (11): main(), 仅绑定回环地址的 NiceGUI Web 入口。, _require_loopback(), _validate_cookie_security(), configure_logging(), EventDict, 递归清除 Web 日志中的凭证和内部 URL。, _redact() (+3 more)

### Community 68 - "Password Management"
Cohesion: 0.29
Nodes (10): hash_password(), password_needs_rehash(), password_violations(), Path, verify_password(), _weak_passwords(), Path, test_backup_password_hash_uses_auditable_argon2id_floor_and_rehashes() (+2 more)

### Community 69 - "Secret Tokens"
Cohesion: 0.32
Nodes (12): _digest(), issue_secret(), IssuedSecret, StrEnum, 生成 256 位一次性秘密，持久化对象中只保留 purpose 绑定摘要。, 以常量时间比较 purpose 绑定摘要。, SecretPurpose, SecretRecord (+4 more)

### Community 70 - "Ports & Interfaces"
Cohesion: 0.21
Nodes (9): AiClient, Clock, DependencyCheck, JobBroker, datetime, Protocol, UUID, M1 外部边界所需的最小 Protocol。 (+1 more)

### Community 71 - "AI Safety & Lifecycle"
Cohesion: 0.18
Nodes (14): 安全模型档案与提示词生命周期, AI 输入、提示词、模型与 Schema 冻结上下文, 不可变脱敏审计与外部故障隔离, GitHub Issue #10, M6 T087–T126 in_progress，T103 为下一项, Batch 父任务不执行且状态由四个子任务派生, 数据库提交后 Redis 故障仍保持 202 pending_dispatch, AI 外呼前实时重验账号、角色、班级、教案与模型 (+6 more)

### Community 72 - "AI Adoption Tests"
Cohesion: 0.30
Nodes (11): create_completed_ai_preview(), TestClient, UUID, _native_url(), TestClient, UUID, _snapshot_count(), test_adopt_merges_preview_once_and_repeated_request_creates_no_second_snapshot() (+3 more)

### Community 73 - "Invitation Tests"
Cohesion: 0.33
Nodes (13): _base64url(), _create_teacher(), _issue(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes(), test_invitation_is_single_use_reissuable_and_revocable() (+5 more)

### Community 74 - "OpenAPI Contract Tests"
Cohesion: 0.40
Nodes (13): _assert_operation_contract(), _canonical_schema(), _effective_security(), _operations(), _parameter_shape(), Any, 运行时 OpenAPI 与冻结身份契约的一致性门禁。, _request_schema() (+5 more)

### Community 75 - "Settings Permissions"
Cohesion: 0.33
Nodes (12): admin_session(), CurrentSessionDependency, _provision_associated_teacher(), TestClient, UUID, _session_for(), teacher_client(), test_all_settings_routes_require_authentication() (+4 more)

### Community 76 - "AI Schema Tests"
Cohesion: 0.28
Nodes (11): validate_prompt_result_schema(), _contract(), Any, ModuleType, M6 AI 固定结果与输入最小化 RED 验收。, test_area_result_cannot_own_areas_and_adoption_reuses_validated_input(), test_daily_reflection_is_nonempty_nfkc_and_limited_by_unicode_code_points(), test_group_activity_results_are_closed_and_add_step_index_is_not_clamped() (+3 more)

### Community 77 - "RED Gate Contracts"
Cohesion: 0.15
Nodes (13): 执行授权边界, 可收集且无错误的 RED 门禁, contracts/, data-model.md, graphify-out/graph.json, 常规测试禁止真实 AI、节假日及其他外网调用, 阶段依赖与执行顺序, plan.md (+5 more)

### Community 78 - "Credential Tests"
Cohesion: 0.36
Nodes (12): _base64url(), _insert_credential(), _native_url(), MonkeyPatch, TestClient, UUID, _registration_credential(), test_admin_cannot_revoke_last_active_admin_last_credential() (+4 more)

### Community 79 - "Identity Isolation Tests"
Cohesion: 0.38
Nodes (12): _insert_kindergarten(), _insert_user(), UUID, test_cross_kindergarten_role_assignment_is_rejected_by_composite_foreign_key(), test_refresh_replacement_cannot_cross_kindergarten(), test_refresh_revocation_serializes_with_rotation_and_revokes_the_new_token(), test_repository_exposes_atomic_passkey_lifecycle_operations(), test_repository_refuses_to_deactivate_last_active_admin() (+4 more)

### Community 80 - "Prompt Settings UI"
Cohesion: 0.19
Nodes (7): _job_status_module(), Any, MonkeyPatch, test_controls_have_keyboard_focus_and_error_label_associations(), test_job_status_recovers_configuration_change_with_chinese_action(), test_job_status_refreshes_until_terminal_and_restores_after_page_reload(), test_settings_controls_call_model_prompt_and_job_public_api_seams()

### Community 81 - "Auth Contract Tests"
Cohesion: 0.21
Nodes (7): APIRoute, Any, _resolve(), _runtime_routes(), test_auth_success_and_logout_lock_two_raw_cookie_headers(), test_runtime_auth_router_matches_frozen_passkey_paths(), test_runtime_auth_success_statuses_match_frozen_contract()

### Community 82 - "Prompt Repository Tests"
Cohesion: 0.30
Nodes (9): _modules(), Any, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_call_configuration_change_set_matches_the_frozen_revision_rules(), test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup(), test_model_reads_and_writes_are_tenant_scoped(), test_prompt_run_frozen_fields_cannot_be_updated() (+1 more)

### Community 83 - "Generation Service Tests"
Cohesion: 0.48
Nodes (10): _native_url(), TestClient, UUID, RecordingDispatcher, _replace_areas(), _session(), test_batch_creates_non_executable_parent_and_exactly_four_dispatched_children(), test_batch_missing_indoor_area_only_fails_indoor_child_and_single_is_rejected() (+2 more)

### Community 84 - "Project Milestones"
Cohesion: 0.24
Nodes (11): AI Generation Behavior Rules, AI Prompt Management System, Daily Lesson Plan System, Word Document Export, Issue #11 - M6 AI Async Generation, M4 AI Model & Prompt Basics, M5 Manual Lesson Plan Closure, M6 AI Async Generation (+3 more)

### Community 85 - "OpenAPI Assembly"
Cohesion: 0.29
Nodes (9): _apply_operation_contract(), configure_openapi(), _no_content_response(), _operation(), Any, FastAPI, M2 运行时 OpenAPI 的集中契约装配。, 返回缓存后的 M2 运行时 OpenAPI 生成器。 (+1 more)

### Community 86 - "Dev Handoff"
Cohesion: 0.29
Nodes (11): Dev Handoff 2026-07-24, 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。, Milestone M2: Core Authentication & Permissions, Milestone M3: Settings, Milestone M3A: Password + TOTP Backup Login, Tasks T001–T002: Issue #8 & Docs Baseline, Tasks T003–T009: RED Gate for M3A, Tasks T010–T015: M3A Backup Auth Foundation (+3 more)

### Community 87 - "TOTP Primitive"
Cohesion: 0.31
Nodes (10): candidate_totp_counters(), _counter(), generate_totp(), _hotp(), RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。, 返回当前时间步及相邻一个时间步，按 counter 递增排序。, 按固定 SHA-1、6 位、30 秒参数生成 TOTP。, 返回匹配且尚未消费的 counter；失败或重放时返回 ``None``。 (+2 more)

### Community 88 - "Admin CLI Tests"
Cohesion: 0.40
Nodes (10): _prepare_last_admin_recovery(), CompletedProcess, MonkeyPatch, UUID, _run_cli(), test_init_admin_activate_requires_two_distinct_pre_registered_approvers(), test_init_admin_cli_exposes_start_activate_and_migration_commands(), test_init_admin_start_creates_pending_account_and_one_time_secret_without_password() (+2 more)

### Community 89 - "Backup Auth Contract"
Cohesion: 0.24
Nodes (7): Any, _resolve(), _runtime_routes(), test_backup_contract_marks_request_and_one_time_response_secrets(), test_runtime_router_exposes_the_user_story_2_endpoints(), test_runtime_router_matches_the_frozen_backup_contract(), test_runtime_user_story_2_openapi_matches_frozen_security_and_responses()

### Community 90 - "AI Client Tests"
Cohesion: 0.44
Nodes (10): _modules(), Any, _resolver(), test_client_caps_retry_after_at_sixty_seconds(), test_client_errors_are_stable_and_never_include_key_or_prompt(), test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin(), test_client_posts_openai_compatible_request_with_fixed_limits(), test_client_rejects_redirects_without_following_them() (+2 more)

### Community 91 - "Input Hashing"
Cohesion: 0.29
Nodes (9): AiTaskCode, JsonValue, canonical_json_sha256(), generation_input_sha256(), 对 JSON 值进行稳定序列化并计算 SHA-256。, 计算逐任务实际输入哈希。      ``server_input`` 只应包含该任务白名单内的服务端输入。采用预览时，调用方必须复用任务     创建时冻结的, section_sha256(), test_generation_input_hash_reuses_frozen_teacher_context_and_current_server_input() (+1 more)

### Community 92 - "Request Context Middleware"
Cohesion: 0.22
Nodes (7): API 请求 ID 与追踪 ID 中间件。, _request_id(), RequestContextMiddleware, ASGIApp, Receive, Scope, Send

### Community 93 - "BFF Proxy"
Cohesion: 0.29
Nodes (9): BffResponse, proxy_request(), AsyncBaseTransport, 按固定 allowlist 转发请求，并保留响应原始多值头。, MonkeyPatch, test_proxy_ignores_process_proxy_environment(), test_proxy_preserves_auth_set_cookie_as_raw_headers(), test_proxy_preserves_request_and_rebuilds_client_ip() (+1 more)

### Community 94 - "Session & Transaction"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 95 - "Client IP Trust"
Cohesion: 0.33
Nodes (8): Collection, parse_trusted_bff_peers(), 只接受显式配置的回环 BFF socket peer。, resolve_client_ip(), test_configured_loopback_bff_peer_can_supply_internal_client_ip(), test_non_loopback_peer_cannot_be_configured_as_trusted_bff(), test_trusted_bff_peers_are_empty_until_explicitly_configured(), test_untrusted_peer_cannot_supply_internal_client_ip()

### Community 96 - "Passkey Authorization"
Cohesion: 0.38
Nodes (6): datetime, _session(), test_backup_reauthentication_only_authorizes_add_passkey_for_five_minutes(), test_expired_backup_reauthentication_cannot_add_passkey(), test_recent_webauthn_proof_satisfies_high_risk_identity_boundary(), test_restricted_enrollment_session_cannot_enter_business_routes()

### Community 97 - "Workday Cache"
Cohesion: 0.38
Nodes (5): Any, date, datetime, UUID, WorkdayCacheRepository

### Community 98 - "Model Profile Tests"
Cohesion: 0.40
Nodes (9): ai_admin_client(), _profile_payload(), Any, TestClient, _resolver(), test_admin_creates_write_only_masked_profile_and_cannot_read_key(), test_call_fields_increment_revision_but_display_and_limits_do_not(), test_disable_preserves_profile_and_default_switch_is_tenant_local() (+1 more)

### Community 99 - "Settings Isolation Tests"
Cohesion: 0.38
Nodes (7): _assert_queries_are_tenant_scoped(), UUID, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_class_area_reads_filter_by_kindergarten_and_class(), test_class_area_writes_filter_by_kindergarten_and_class(), test_top_level_setting_reads_filter_by_kindergarten()

### Community 100 - "Workday Service Tests"
Cohesion: 0.29
Nodes (6): _module(), MonkeyPatch, test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls(), test_local_result_wins_conflict_and_uses_one_hour_cache(), test_timor_client_enforces_one_total_deadline(), test_unsupported_local_calendar_range_softly_falls_back_to_online()

### Community 101 - "Development Branch & Docs"
Cohesion: 0.33
Nodes (9): dev - Implementation Branch, docs - Design & Spec Baseline, main - Stable Release Baseline, CONTEXT.md - Project Status, Old Repository - kindergartenManager, README.md - Product Overview, Implementation Plan - Daily Activity Plan, Quickstart - Acceptance Contract (+1 more)

### Community 102 - "Security & System Boundaries"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 103 - "Milestones & User Stories"
Cohesion: 0.25
Nodes (9): specs/002-password-totp-backup-login/tasks.md, M8 性能、安全、无障碍与交付验收, 唯一教案、保存、历史、归档与恢复, Polish 与 M8 完整验收, M9 生产部署复审排除在任务范围外, Roadmap M1–M8 范围, US1 M3A 密码与 TOTP 备用登录, US2 纯手工教案闭环 (+1 more)

### Community 104 - "Secret Encryption Tests"
Cohesion: 0.39
Nodes (8): _context(), _encryption_module(), Any, Path, test_development_key_provider_requires_owner_only_file_outside_repository(), test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution(), test_totp_secret_envelope_round_trips_with_random_96_bit_nonce(), test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce()

### Community 105 - "Auth & Settings Baseline"
Cohesion: 0.25
Nodes (8): Settings System - Kindergarten/Semester/Class, Password + TOTP Backup Login, WebAuthn Passkey Authentication, M0 Shared Design Baseline, M1 Engineering Skeleton, M2 Authentication & Authorization, M3 Essential Settings, M3A Password & TOTP Backup Login

### Community 106 - "AI Prompts Migration"
Cohesion: 0.36
Nodes (6): Any, Column, 建立 AI 模型、提示词与 PostgreSQL 权威任务基础。, _seed_defaults(), _timestamps(), upgrade()

### Community 107 - "Content Completeness Schemas"
Cohesion: 0.50
Nodes (7): _area_complete(), content_completeness(), _group_activity_complete(), _morning_activity_complete(), _morning_talk_complete(), _three_questions(), _three_statements()

### Community 108 - "Backup Auth Migration Tests"
Cohesion: 0.46
Nodes (7): Script, _backup_revision(), MonkeyPatch, test_backup_auth_migration_creates_isolated_credentials_and_enrollments(), test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(), test_backup_auth_revision_follows_settings_and_precedes_lesson_plans(), test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade()

### Community 109 - "Daily Plan User Stories"
Cohesion: 0.25
Nodes (8): Feature Specification: 首期一日活动计划完整闭环, User Story 1: Admin Setup, User Story 2: Manual Lesson Plan Loop, User Story 3: Admin Configure Model and Prompts, User Story 4: Teacher Uses AI by Section, User Story 5: Teacher Processes Group Activity Source, User Story 6: Teacher Export and Download Fixed Word, User Story 7: Admin Audit and Degradable Service

### Community 110 - "AI Prompt Contract Tests"
Cohesion: 0.32
Nodes (6): Any, _schema(), test_model_and_job_contracts_freeze_revision_and_stable_errors(), test_prompt_test_contract_exposes_only_redacted_input_summary(), test_prompt_test_fingerprint_changes_across_prompt_codes(), test_runtime_exposes_the_complete_frozen_m4_route_surface()

### Community 111 - "OpenAPI Document Tests"
Cohesion: 0.39
Nodes (7): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_document_is_valid_31(), test_openapi_keeps_nicegui_as_the_only_browser_entry(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 112 - "Password to Passkey Tests"
Cohesion: 0.54
Nodes (7): _assert_passkey_revisions_exist(), _native_url(), MonkeyPatch, test_contract_removes_password_data_and_downgrade_recreates_only_empty_columns(), test_expand_moves_existing_accounts_to_enrollment_and_revokes_old_sessions(), test_passkey_migration_has_explicit_expand_and_contract_boundaries(), _user_columns()

### Community 113 - "Content V1 Schema Tests"
Cohesion: 0.54
Nodes (7): _contracts(), _schemas(), test_completeness_is_independent_from_progressive_schema_validation(), test_empty_v1_content_supports_progressive_manual_editing(), test_reflection_is_nfkc_normalized_and_limited_to_200_codepoints(), test_statement_and_question_punctuation_are_strictly_chinese(), test_unknown_fields_and_unknown_content_versions_are_not_silently_coerced()

### Community 114 - "AI Key Envelope Tests"
Cohesion: 0.39
Nodes (7): _module(), Any, Path, test_ai_key_envelope_rejects_tampering_and_cross_profile_substitution(), test_ai_key_envelope_round_trips_with_random_96_bit_nonce(), test_file_key_provider_requires_owner_only_files_outside_repository(), test_static_key_provider_reads_old_key_but_writes_with_active_key()

### Community 115 - "AI Model URL Policy Tests"
Cohesion: 0.57
Nodes (7): _module(), Any, _resolver(), test_policy_accepts_only_allowlisted_public_https_and_checks_every_address(), test_policy_detects_dns_rebinding_before_connect(), test_policy_rejects_non_https_and_non_public_networks(), test_policy_requires_explicit_server_allowlist()

### Community 116 - "Prompt Catalog Tests"
Cohesion: 0.43
Nodes (7): _module(), Any, test_catalog_assigns_task_specific_minimum_variable_whitelists(), test_catalog_freezes_seven_codes_whitelists_schemas_and_hashes(), test_catalog_input_validation_excludes_teacher_identity_and_unknown_fields(), test_catalog_result_schemas_are_strict(), test_catalog_result_schemas_match_the_frozen_openapi_shapes()

### Community 117 - "Tech Stack & Dependencies"
Cohesion: 0.29
Nodes (7): Alembic Database Migrations, PostgreSQL Production Database, pyproject.toml Dependency Management, Python 3.14+ Minimum Version, SQLAlchemy 2.x ORM, Technology and Dependency Baseline, uv.lock Version Locking

### Community 118 - "Job Query Service"
Cohesion: 0.43
Nodes (3): job_query_service(), JobQueryService, UUID

### Community 119 - "Security Event Tests"
Cohesion: 0.33
Nodes (5): security_event_text(), MonkeyPatch, test_backup_login_and_reauthentication_submit_secrets_only_in_post_bodies(), test_security_event_messages_cover_the_frozen_event_codes(), test_security_events_use_read_only_same_origin_api()

### Community 120 - "Passkey Expand Migration"
Cohesion: 0.52
Nodes (5): Any, Column, _tenant_identity_columns(), _timestamps(), upgrade()

### Community 121 - "Project Governance & Boundaries"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 122 - "Service Components & Tests"
Cohesion: 0.38
Nodes (7): FastAPI API 独立运行单元, 方法、路由、实际 path/query/body 的规范幂等指纹, Foundational T009–T020, docs/development/local-development-environments.md, Setup T001–T008, NiceGUI Web 独立运行单元, 后台 Worker 独立运行单元

### Community 123 - "Prompt Renderer Tests"
Cohesion: 0.48
Nodes (6): _module(), Any, test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(), test_renderer_fails_for_missing_variable_before_external_call(), test_renderer_rejects_every_non_frozen_placeholder_form(), test_renderer_uses_stable_json_and_never_recursively_renders_values()

### Community 125 - "Identity & Audit Migration"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 126 - "Settings Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 127 - "Password TOTP Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 128 - "Lesson Plans Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 129 - "AI Gen Results Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 130 - "Word Template & Export"
Cohesion: 0.40
Nodes (6): 固定 Word 模板原件哈希与样式完整性, templates/teacherplan/teacherplan.docx, 集体活动拆分后再新增环节的两阶段流程, US5 集体活动原始教案处理, US6 固定 Word 导出与重新下载, 固定模板 Word 导出、历史与重新授权下载

### Community 132 - "TOTP Tests"
Cohesion: 0.53
Nodes (5): Any, test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps(), test_totp_rejects_the_same_or_earlier_counter_after_success(), test_totp_secret_is_unique_high_entropy_base32(), _totp_module()

### Community 133 - "Service Roles & Boundaries"
Cohesion: 0.60
Nodes (5): Background Worker Role, FastAPI API Service Role, NiceGUI Web Service Role, Service Boundaries and Dependency Direction, Shared Contracts Package

### Community 134 - "Infrastructure Components"
Cohesion: 0.50
Nodes (5): FastAPI API Service, NiceGUI Web Service, PostgreSQL Database, Redis Message Broker, Dramatiq Background Worker

### Community 135 - "Development Workflow & Review"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 138 - "Kindergarten Auth & Settings"
Cohesion: 0.50
Nodes (5): 园所、学期、班级、教师关系与区域设置, kindergarten_id 园所隔离, US1 M2 认证、授权与身份审计, US1 M3 首期必要设置, WebAuthn 身份安全与会话撤销

### Community 139 - "AI Key Rotation CLI Tests"
Cohesion: 0.60
Nodes (4): CompletedProcess, _run(), test_bootstrap_cli_exposes_rotation_without_master_key_arguments(), test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets()

### Community 140 - "Identity Migration Tests"
Cohesion: 0.50
Nodes (4): migrated_database(), MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds(), test_identity_migration_is_idempotent()

### Community 141 - "Calendar Tests"
Cohesion: 0.70
Nodes (4): _calendar(), test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic(), test_out_of_semester_week_number_and_text_are_both_empty(), test_semester_start_week_is_week_one_and_increments_each_monday()

### Community 142 - "Git Branch Roles"
Cohesion: 0.50
Nodes (4): Dev Branch Role, Development Workflow and Git Rules, Docs Branch Role, Main Branch Role

### Community 143 - "Save Status Module"
Cohesion: 0.67
Nodes (3): save_status(), SaveStatus, SaveState

### Community 144 - "Dev Environment & CI"
Cohesion: 0.67
Nodes (4): Docker Compose 开发环境配置, GitHub Actions 质量检查工作流, PostgreSQL, Redis

### Community 145 - "Core Database Tables"
Cohesion: 0.50
Nodes (4): Age Groups Table, Class Teachers Table, Classes Table, Daily Activity Plans Table

### Community 146 - "Schema Isolation & Keys"
Cohesion: 0.50
Nodes (4): Composite Foreign Keys Concept, Kindergarten Isolation Concept, Kindergartens Table, Users Table

### Community 148 - "Backup Login Feature"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 150 - "Lesson Plan Contract Tests"
Cohesion: 0.83
Nodes (3): _contracts(), test_open_and_write_contracts_do_not_accept_tenant_or_ownership_mutation(), test_plan_snapshot_and_page_contracts_are_bounded_and_stable()

### Community 155 - "Knowledge Graph Tools"
Cohesion: 1.00
Nodes (3): Codebase-Memory MCP Usage, Codegraph Usage, Graphify Knowledge Graph Usage

### Community 157 - "Migration Dependency Order"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

### Community 158 - "Json Schema Utilities"
Cohesion: 1.00
Nodes (3): JsonSchemaValue, _render_prompt_test_run_schema(), _render_union_as_one_of()

### Community 161 - "Daily Activity Word Layout"
Cohesion: 0.67
Nodes (3): AI-Added Step Red Text, Structured Daily Activity Sections, Daily Activity Plan Word Layout

## Knowledge Gaps
- **185 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+180 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **90 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `班级与教师配置` (2× useful, score=1.352895454)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IdentityError` connect `Identity Service & Audit` to `Auth Flow & CSRF`, `Admin Init & Audit`, `Job Dispatching`, `Credential Challenge`, `Challenge Issuance`, `User Management`, `Settings Service`, `Workday Calendar`, `AI Model Service`, `Lesson Plan Service`, `TOTP Encryption`, `Prompt Renderer`, `Teacher Settings Validation`, `Prompt Service`, `API App Setup`, `Backup Maintenance Tests`, `Admin Recovery Tests`, `Health Check`, `Health Checks`, `Password Management`, `Secret Tokens`, `Generation Service Tests`, `Passkey Authorization`, `Job Query Service`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `ActorFixture` connect `Backup Enrollment Tests` to `Identity Service & Audit`, `Model Profile Tests`, `Job Message Dispatching`, `AI Adoption Tests`, `Auth Rate Limiting`, `TOTP Encryption`, `Invitation Tests`, `Settings Permissions`, `Credential Tests`, `WebAuthn Auth Tests`, `Prompt Test API Tests`, `Session & Passkey Tests`, `Generation Service Tests`, `Batch Generation Tests`, `Backup Maintenance Tests`, `Admin Recovery Tests`, `AI Preview Tests`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `csrf_headers()` connect `WebAuthn Auth Tests` to `Model Profile Tests`, `Job Message Dispatching`, `Backup Enrollment Tests`, `AI Adoption Tests`, `Auth Rate Limiting`, `Invitation Tests`, `Settings Permissions`, `Credential Tests`, `Prompt Test API Tests`, `Session & Passkey Tests`, `Generation Service Tests`, `Batch Generation Tests`, `Backup Maintenance Tests`, `Admin Recovery Tests`, `AI Preview Tests`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `ActorFixture` (e.g. with `StaticIdentitySecretKeyProvider` and `IdentityService`) actually correct?**
  _`ActorFixture` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `IdentityError` (e.g. with `create_app()` and `HealthDependencies`) actually correct?**
  _`IdentityError` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 134 inferred relationships involving `ContractModel` (e.g. with `AuditEventReference` and `IdentityAuditEventCode`) actually correct?**
  _`ContractModel` has 134 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `SessionUser` (e.g. with `HealthDependencies` and `AuditRepository`) actually correct?**
  _`SessionUser` has 27 INFERRED edges - model-reasoned connections that need verification._