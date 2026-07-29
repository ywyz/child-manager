# Graph Report - child-manager  (2026-07-29)

## Corpus Check
- 348 files · ~210,879 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3098 nodes · 8852 edges · 273 communities (186 shown, 87 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 763 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4a9974ea`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Identity Repository
- Settings Router
- Identity Service
- Authentication Endpoints
- AI Job Recovery Tests
- Log Redaction & Observability
- Database Models & Migrations
- Audit Service
- Auth Throttle
- AI Job Execution
- Prompt Test Management
- Auth Router & Contracts
- AI Result Repository
- Prompt Test Actors
- AI Key Rotation
- Jobs Router & Contracts
- WebAuthn Tests
- BFF API Client
- Passkey Migration & Tests
- Plans Router
- WebAuthn Challenges
- Prompt Test Store
- AI Batch Tests
- AI Results Migration Test
- Users Router
- Architecture Design Principles
- Prompt Test Worker Tests
- Development Methodology
- Auth Challenge Verification
- Settings Repository
- Calendar Workday
- Project Planning Documents
- Lesson Plan Repository
- Test Database Config
- Lesson Plan Service
- AI Retry Policy Tests
- Prompt Repository
- API Contracts & Architecture
- App Configuration
- Backup Enrollment Tests
- Job Query Service
- Login Throttle
- TOTP Secret Encryption
- Local Dev Environment
- CSRF Token
- AI Job Runner
- Prompt Template Renderer
- Test Fixtures & Isolation
- Auth Smoke Tests
- Local Dev Profiles Tests
- Plan Editor Page
- FastAPI App Setup
- Settings Smoke Tests
- ai_models.py
- API Main Entry
- Backup Auth Isolation Tests
- Backup Maintenance Tests
- Plan Accessibility Tests
- Dev Shell Scripts
- lesson_plans.py
- Health Check
- Health Dependencies
- AI Client
- AI Preview Lifecycle Tests
- AI Key Rotation Tests
- Development Rules & Constraints
- Job & Prompt Test Status
- NiceGUI Web Entry
- Password & Identity Utilities
- Admin Initialization
- Ports & Adapters Interfaces
- AI Generation Architecture
- AI Model Profile Tests
- Invitation Tests
- OpenAPI Contract Tests
- Settings Permissions Tests
- api/test_prompt_test_jobs.py
- Quality Gates & Docs
- Credential Management Tests
- Migration Tests
- AI Prompt Settings Tests
- Auth Contract Tests
- AI Prompt Repository Tests
- validate_prompt_result_schema
- Feature Milestones
- OpenAPI Configuration
- Dev Handoff & Milestones
- test_recovery.py
- test_identity_isolation.py
- Backup Auth Contract Tests
- AI Client Tests
- issue_secret
- Request ID Middleware
- BFF Proxy
- DB Session Management
- Client IP Resolution
- test_ai_preview_adoption.py
- Workday Cache Repository
- schemas.py
- test_auth_assurance.py
- Workday Service Tests
- Repo Branches & Docs
- Security Threat Model
- Spec Tasks & Roadmap
- Secret Encryption Tests
- Milestones Overview
- AI Prompts & Jobs Migration
- test_init_admin_cli.py
- Backup Login Migration Test
- User Stories Activity Plan
- AI Prompt Contract Tests
- OpenAPI Document Tests
- totp.py
- Content Validation Tests
- AI Key Envelope Tests
- AI Model URL Policy
- Lesson Plans Migration & Catalog
- Database Migrations & Dependencies
- test_password_to_passkey.py
- Security Events & Backup Auth
- Passkey Expand Migration
- Project Constitution & Guidelines
- Independent Runtime Units
- Prompt Renderer Tests
- 0006_lesson_plans.py
- Identity & Audit Migration
- Settings Migration
- Password/TOTP/Backup Migration
- _render_prompt_test_run_schema
- AI Generation Results Migration
- Word Template Processing
- Users Contract Tests
- TOTP Tests
- Service Roles & Boundaries
- Service Infrastructure
- Branch Responsibilities
- Feature Script
- Kindergarten Setup
- AI Key Rotation CLI
- Calendar Tests
- Branch Roles
- Docker & CI Config
- Core Database Tables
- Database Concepts
- Canonical SHA256 Snapshots
- Backup Login Spec
- Lesson Plan Contract Tests
- Calendar Fixtures
- Clock Fixture
- Redis Fixture
- Knowledge Graph Tools
- Migration Order
- Lease Expiration
- AI Step Red Text
- AI Client Fixture
- Child Manager App
- Worker App
- AI & Jobs Tables
- AI Model Profiles
- Prompt Definitions
- Roles Tables
- Backend Database Init
- Weak Passwords List
- Backend Init
- Contracts Init
- Prerequisites Script
- Setup Plan Script
- Setup Tasks Script
- Web Tests
- Account Invitations Table
- Account Recovery Requests Table
- Age Groups Table
- AI Generation Results Table
- AI Model Profile Capabilities Table
- AI Model Profiles Table
- Audit Events Table
- Background Jobs Table
- Backup Auth Credentials Table
- Backup Auth Enrollments Table
- Bootstrap Initializations Table
- Class Areas Table
- Class Teachers Table
- Classes Table
- Daily Activity Plan Exports Table
- Daily Activity Plan Snapshots Table
- Daily Activity Plans Table
- Identity Verification Approvals Table
- Snapshot/Audit Immutability
- JSONB Schema Versioning
- Kindergarten Isolation Principle
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
- Workday Cache
- Account Invitations
- Account Recovery Requests
- Audit Events
- Backup Auth Credentials
- Backup Auth Enrollments
- Bootstrap Initializations
- Class Areas
- Content JSONB Boundary
- Daily Activity Plan Authors
- Daily Activity Plan Exports
- Daily Activity Plan Snapshots
- Identity Verification Approvals
- Lesson Plan Sources
- Prompt Test Runs
- Recovery Codes
- Refresh Tokens
- Semesters
- WebAuthn Challenges
- WebAuthn Credentials
- Workday Cache
- App Owned Transactions
- External Key Source Seam
- M5-M4 Dependency Path
- Child Manager
- PostgreSQL Database
- Development Workflow
- Governance
- Technical Constraints
- Activity Plan Quality
- Password TOTP Backup

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

## Communities (273 total, 87 thin omitted)

### Community 0 - "Identity Repository"
Cohesion: 0.07
Nodes (17): _backup_credential(), _backup_enrollment(), BackupCredentialRecord, BackupEnrollmentRecord, BackupRevocationResult, BackupSecurityEventRecord, ChallengeRecord, IdentityRepository (+9 more)

### Community 1 - "Settings Router"
Cohesion: 0.07
Nodes (66): AgeGroup, AiModelProfile, AiModelServiceDependency, _age_group(), _ai_model(), _area(), _class(), create_ai_model_profile() (+58 more)

### Community 2 - "Identity Service"
Cohesion: 0.16
Nodes (11): identity_service(), AuditRepository, IdentityError, IdentityService, ManagedUser, datetime, Exception, UUID (+3 more)

### Community 3 - "Authentication Endpoints"
Cohesion: 0.18
Nodes (49): authenticate_with_password_and_totp(), authentication_start(), authentication_verify(), backup_authentication_status(), bootstrap_options(), bootstrap_verify(), _check_public_throttle(), _clear_auth_cookies() (+41 more)

### Community 4 - "AI Job Recovery Tests"
Cohesion: 0.10
Nodes (55): LogCaptureFixture, JobMessage, Redis 中唯一允许传递的最小任务消息。, SimpleNamespace, _insert_job(), _insert_other_tenant_plan(), _insert_result(), _native_url() (+47 more)

### Community 5 - "Log Redaction & Observability"
Cohesion: 0.22
Nodes (14): merge_request_context(), EventDict, 递归清除日志中的密钥、令牌、认证材料与 URL 凭证。, 将当前请求关联字段合并到真实 structlog 事件。, _redact(), redact_mapping(), _redact_url(), request_context() (+6 more)

### Community 6 - "Database Models & Migrations"
Cohesion: 0.10
Nodes (40): DeclarativeBase, AuditEvent, Base, AccountInvitation, AccountRecoveryRequest, BackupAuthCredential, BackupAuthEnrollment, BootstrapInitialization (+32 more)

### Community 7 - "Audit Service"
Cohesion: 0.17
Nodes (12): UUID, AuditEventReference, IdentityAuditEventCode, IdentityAuditMetadata, StrEnum, 身份阶段的稳定审计事件代码与最小资源引用。, 身份审计只允许承载最小、严格类型化的非秘密元数据。, 跨服务使用的公共 Schema 与规范化函数。 (+4 more)

### Community 8 - "Auth Throttle"
Cohesion: 0.10
Nodes (33): _auth_throttle(), MemoryAuthThrottle, datetime, Redis, timedelta, 公开身份 ceremony 的来源限流公共 seam。, 按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。, 多进程 API 使用的 Redis 固定窗口实现。 (+25 more)

### Community 9 - "AI Job Execution"
Cohesion: 0.14
Nodes (10): AiExecutionContext, AiJobStore, AiJobStoreProtocol, _log_sanitized_exception(), Any, datetime, Exception, Protocol (+2 more)

### Community 10 - "Prompt Test Management"
Cohesion: 0.31
Nodes (36): EditableContent, PromptSpec, BaseModel, 固定提示词目录、输入与结果 Schema 路由。, _spec(), AiAreaGame, AiDailyReflection, AiGroupActivity (+28 more)

### Community 11 - "Auth Router & Contracts"
Cohesion: 0.08
Nodes (54): _allowed_origins(), _loopback_aliases(), 同源 Cookie、WebAuthn、邀请、恢复与会话端点。, ContractModel, BaseModel, ExportReference, AdminCredentialRevocationResult, AuthenticationCredential (+46 more)

### Community 12 - "AI Result Repository"
Cohesion: 0.05
Nodes (58): AiTaskCode, JsonValue, AiGenerationResultRecord, AiGenerationResultRepository, _json_object(), _optional_uuid(), Any, datetime (+50 more)

### Community 13 - "Prompt Test Actors"
Cohesion: 0.10
Nodes (26): Actor, build_prompt_test_executor(), Broker, datetime, Protocol, UUID, 只接收 job_id 的 Dramatiq actor 与 PostgreSQL 恢复扫描。, 按 PostgreSQL 权威状态重投 pending/过期租约任务。 (+18 more)

### Community 14 - "AI Key Rotation"
Cohesion: 0.15
Nodes (23): UUID, run_rotation(), _aad(), AiKeyEnvelope, decrypt_api_key(), decrypt_api_key_with_provider(), encrypt_api_key(), encrypt_api_key_with_provider() (+15 more)

### Community 15 - "Jobs Router & Contracts"
Cohesion: 0.11
Nodes (22): get_job(), AdminSessionDependency, UUID, _job(), JobQueryServiceDependency, JobStatus, derive_batch_projection(), Job (+14 more)

### Community 16 - "WebAuthn Tests"
Cohesion: 0.14
Nodes (37): csrf_headers(), _base64url(), _credential(), MonkeyPatch, TestClient, _registration_credential(), test_authentication_options_are_username_less_and_browser_ready(), test_authentication_options_do_not_increment_failure_limit() (+29 more)

### Community 17 - "BFF API Client"
Cohesion: 0.12
Nodes (27): backup_auth_api_request(), backup_login_api_request(), backup_reauthentication_api_request(), plan_api_request(), NiceGUI 服务端 BFF 客户端的公开接缝。, 以请求正文提交两项备用因素，不把秘密放入 URL。, 为当前备用会话取得仅可新增通行密钥的短时证明。, 读取本人最近 20 条内建安全事件，不产生已读状态。 (+19 more)

### Community 18 - "Passkey Migration & Tests"
Cohesion: 0.10
Nodes (27): current_session(), AuthenticatedSessionDependency, pytest, admin_client(), passkey_client(), MonkeyPatch, TestClient, 通过 FastAPI 身份依赖注入建立已 step-up 管理员，不借用密码登录。 (+19 more)

### Community 19 - "Plans Router"
Cohesion: 0.19
Nodes (31): archive_plan(), autosave_plan(), get_plan(), list_plans(), list_snapshots(), open_plan(), _plan(), CurrentSessionDependency (+23 more)

### Community 20 - "WebAuthn Challenges"
Cohesion: 0.10
Nodes (36): ChallengeBinding, ChallengePurpose, ChallengeRecord, consume_challenge(), issue_challenge(), IssuedChallenge, datetime, StrEnum (+28 more)

### Community 21 - "Prompt Test Store"
Cohesion: 0.24
Nodes (3): PromptTestStore, datetime, UUID

### Community 22 - "AI Batch Tests"
Cohesion: 0.17
Nodes (33): provision_enabled_ai_model(), provision_editable_plan_context(), date, TestClient, TestClient, test_generation_reject_adopt_and_retry_write_sanitized_audit_rows(), _idempotent_headers(), TestClient (+25 more)

### Community 23 - "AI Results Migration Test"
Cohesion: 0.17
Nodes (30): alias, clear_prompt_tests(), create_prompt_test(), _definition(), get_prompt(), get_prompt_test(), get_prompt_version(), list_prompt_tests() (+22 more)

### Community 24 - "Users Router"
Cohesion: 0.19
Nodes (32): activate(), create_user(), credential_revoke(), credentials(), deactivate(), get_user(), _invitation(), invitation_issue() (+24 more)

### Community 25 - "Architecture Design Principles"
Cohesion: 0.08
Nodes (34): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+26 more)

### Community 26 - "Prompt Test Worker Tests"
Cohesion: 0.15
Nodes (20): _context(), FakeAuthorizer, FakeClient, FakeStore, _modules(), Any, datetime, UUID (+12 more)

### Community 27 - "Development Methodology"
Cohesion: 0.07
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+25 more)

### Community 28 - "Auth Challenge Verification"
Cohesion: 0.23
Nodes (8): _credential(), CredentialRecord, AuthResult, _challenge_digest(), _client_challenge(), _decode_base64url(), Any, _RegistrationResult

### Community 29 - "Settings Repository"
Cohesion: 0.06
Nodes (50): settings_service(), IntegrityError, NoReturn, _ai_profile(), AiModelProfileRecord, AiModelProfileRepository, AreaInput, call_configuration_changed() (+42 more)

### Community 30 - "Calendar Workday"
Cohesion: 0.12
Nodes (23): map_timor_payload(), AsyncBaseTransport, date, TimorWorkdayClient, WorkdayResult, 园所范围工作日缓存 Repository。, combine_workday_results(), date (+15 more)

### Community 31 - "Project Planning Documents"
Cohesion: 0.07
Nodes (32): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+24 more)

### Community 32 - "Lesson Plan Repository"
Cohesion: 0.17
Nodes (11): AuthorRecord, LessonPlanRepository, _plan(), PlanCreationContext, PlanRecord, Any, date, UUID (+3 more)

### Community 33 - "Test Database Config"
Cohesion: 0.31
Nodes (15): MonkeyPatch, Path, test_environment_test_database_url_takes_precedence_over_profile(), test_test_database_profile_must_stay_outside_the_repository(), test_test_database_profile_rejects_group_or_other_access(), test_test_database_url_rejects_nonisolated_or_nonpostgresql_targets(), test_test_database_url_reports_missing_environment_and_profile(), test_test_database_url_uses_secure_repo_external_profile() (+7 more)

### Community 34 - "Lesson Plan Service"
Cohesion: 0.26
Nodes (10): lesson_plan_service(), LessonPlanService, OpenPlanResult, PlanView, _PlanViewSeed, date, UUID, 完成单一用例响应；外网解析发生在业务事务关闭之后。 (+2 more)

### Community 35 - "AI Retry Policy Tests"
Cohesion: 0.09
Nodes (24): BaseTransport, ProviderNeutralAiClient, Resolver, AiClientError, RuntimeError, cap_retry_after_seconds(), is_retryable_ai_error(), UUID (+16 more)

### Community 36 - "Prompt Repository"
Cohesion: 0.20
Nodes (11): _definition(), prompt_test_input_summary(), PromptDefinitionRecord, PromptRepository, PromptTestRunRecord, PromptVersionRecord, Any, UUID (+3 more)

### Community 37 - "API Contracts & Architecture"
Cohesion: 0.07
Nodes (29): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, Child Manager Daily Activity API, Identity and Settings Endpoints, Plans, Jobs, and Exports Endpoints, API v1 Contract (+21 more)

### Community 38 - "App Configuration"
Cohesion: 0.25
Nodes (12): AppSettings, global_security_ready(), BaseModel, JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。, MonkeyPatch, settings(), test_api_entrypoint_rejects_insecure_cookie_on_non_loopback(), test_development_insecure_cookie_requires_loopback_binding() (+4 more)

### Community 39 - "Backup Enrollment Tests"
Cohesion: 0.16
Nodes (25): ActorFixture, TestClient, test_admin_is_restricted_until_complete_backup_enrollment(), test_backup_status_and_enrollment_require_authentication(), test_enrollment_requires_password_and_totp_together_and_is_single_use(), test_expired_enrollment_cannot_enable_backup_auth(), test_new_enrollment_invalidates_the_previous_pending_enrollment(), test_replacing_enabled_material_revokes_only_related_backup_sessions() (+17 more)

### Community 40 - "Job Query Service"
Cohesion: 0.43
Nodes (3): job_query_service(), JobQueryService, UUID

### Community 41 - "Login Throttle"
Cohesion: 0.17
Nodes (10): _digest(), MemoryLoginThrottle, datetime, Redis, timedelta, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision (+2 more)

### Community 42 - "TOTP Secret Encryption"
Cohesion: 0.10
Nodes (25): _aad(), decrypt_totp_secret(), decrypt_totp_secret_with_provider(), encrypt_totp_secret(), encrypt_totp_secret_with_provider(), FileIdentitySecretKeyProvider, Path, UUID (+17 more)

### Community 43 - "Local Dev Environment"
Cohesion: 0.08
Nodes (25): 本地开发环境规范, 仅回环开发依赖, 生产拓扑延后, 工作树资源隔离, M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线 (+17 more)

### Community 44 - "CSRF Token"
Cohesion: 0.40
Nodes (5): _cookie_secure(), csrf(), _encode(), issue_csrf_token(), verify_csrf_token()

### Community 45 - "AI Job Runner"
Cohesion: 0.11
Nodes (24): AiJobAuthorizer, AiJobRetry, AiJobRunner, RuntimeError, AI 生成任务的冻结上下文执行器与 PostgreSQL 状态适配器。, 通知消息代理按权威任务给出的退避时间重投。, CurrentModelCallProfile, ProfileCallLimiter (+16 more)

### Community 46 - "Prompt Template Renderer"
Cohesion: 0.22
Nodes (7): _native_url(), PostgresPromptTestStore, Any, datetime, UUID, 提示词测试 Worker 的 PostgreSQL 权威状态适配器。, PromptTestExecutionContext

### Community 47 - "Test Fixtures & Isolation"
Cohesion: 0.20
Nodes (10): str, block_external_network(), isolated_database_url(), _native_psycopg_url(), MonkeyPatch, 只允许回环 TCP 和本机 Unix socket。, 为请求该夹具的测试创建并清理独立 PostgreSQL schema。, 保留连接字符串行为，但禁止失败报告通过 ``repr`` 展开凭据。 (+2 more)

### Community 48 - "Auth Smoke Tests"
Cohesion: 0.18
Nodes (18): login_page_text(), users_page_text(), BrowserContext, Page, _add_virtual_authenticator(), _auth_cookie_names(), _bootstrap_activate(), _bootstrap_start() (+10 more)

### Community 49 - "Local Dev Profiles Tests"
Cohesion: 0.27
Nodes (8): _compose_config(), Any, Path, 双实现本地开发档位的 Compose 合同。, test_compose_accepts_temporary_image_overrides(), test_compose_uses_selected_local_profile(), test_quality_workflow_provides_an_isolated_postgresql_database(), test_test_database_url_requires_an_explicit_profile()

### Community 50 - "Plan Editor Page"
Cohesion: 0.31
Nodes (5): prompt_service(), Dispatcher, PromptService, Protocol, UUID

### Community 51 - "FastAPI App Setup"
Cohesion: 0.16
Nodes (13): _error_response(), FastAPI, Request, UUID, FastAPI 应用装配、统一异常转换与健康端点。, _request_id(), JSONResponse, ErrorResponse (+5 more)

### Community 52 - "Settings Smoke Tests"
Cohesion: 0.17
Nodes (16): navigation_for_capabilities(), 按 API capabilities 生成导航。, class_areas_page_text(), settings_page_text(), test_navigation_is_derived_from_current_api_capabilities(), BrowserActor, _free_port(), _m3_services() (+8 more)

### Community 53 - "ai_models.py"
Cohesion: 0.23
Nodes (9): AiKeyProvider, ai_model_service(), AiModelService, _display(), _key(), _native_url(), Resolver, UUID (+1 more)

### Community 54 - "API Main Entry"
Cohesion: 0.32
Nodes (6): main(), 拒绝在非开发环境或非回环地址关闭 Cookie Secure。, 验证进程启动时的 Cookie 与监听地址组合。, validate_cookie_security(), configure_logging(), 配置 JSON 结构化日志和最终脱敏处理器。

### Community 55 - "Backup Auth Isolation Tests"
Cohesion: 0.25
Nodes (13): MonkeyPatch, UUID, RecordingConnection, RecordingResult, _seed_backup_repository(), test_admin_role_gate_restricts_and_then_releases_webauthn_sessions(), test_backup_credential_reads_are_scoped_to_kindergarten_and_user(), test_backup_version_change_revokes_only_related_sessions() (+5 more)

### Community 56 - "Backup Maintenance Tests"
Cohesion: 0.40
Nodes (12): _change_actor_to_teacher(), _enable_backup(), _identity_service(), _login_with_backup(), _native_url(), TestClient, test_admin_cannot_disable_required_backup_authentication(), test_backup_maintenance_and_security_events_require_authentication() (+4 more)

### Community 57 - "Plan Accessibility Tests"
Cohesion: 0.18
Nodes (12): PlanContentV1, MonkeyPatch, test_rendered_plan_editor_has_labelled_status_fields_focus_order_and_touch_targets(), _job(), _plan(), MonkeyPatch, M6 教案栏目内预览与可恢复状态的 NiceGUI RED 冒烟。, test_generation_autosaves_before_submit_and_renders_accessible_status() (+4 more)

### Community 58 - "Dev Shell Scripts"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 59 - "lesson_plans.py"
Cohesion: 0.12
Nodes (15): AiGroupActivityStep, apply_ai_area_result(), DailyReflection, GroupActivityStep, GroupActivityStepCandidate, LessonPlanReference, PlanSnapshotContext, 区域名称属于冻结输入；模型只能选择重点指导区域，不能改写区域列表。 (+7 more)

### Community 60 - "Health Check"
Cohesion: 0.31
Nodes (15): create_app(), HealthDependencies, check(), dependencies(), Path, test_database_failure_returns_stable_503_code(), test_default_dependencies_check_real_local_runtime(), test_each_optional_dependency_only_degrades_ready_response() (+7 more)

### Community 61 - "Health Dependencies"
Cohesion: 0.18
Nodes (17): _ai_unconfigured(), authenticated_session(), build_health_dependencies(), _calendar_library_available(), _database_check(), _file_check(), _path_check(), IdentityServiceDependency (+9 more)

### Community 62 - "AI Client"
Cohesion: 0.26
Nodes (12): _pinned_url(), Any, OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。, _addresses(), AiUrlPolicyError, Resolver, ValueError, AI 模型地址的保存时与连接前 SSRF 防护。 (+4 more)

### Community 63 - "AI Preview Lifecycle Tests"
Cohesion: 0.31
Nodes (12): _native_url(), NoCallExpectedClient, TestClient, UUID, _snapshot_count(), test_batch_and_nonfailed_ai_jobs_reject_explicit_retry(), test_cross_tenant_failed_job_is_hidden_from_retry(), test_expiration_scheduler_transitions_due_previews_once() (+4 more)

### Community 64 - "AI Key Rotation Tests"
Cohesion: 0.35
Nodes (10): _candidate(), FakeStore, _modules(), Any, UUID, test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it(), test_rotation_dry_run_and_repeated_batch_are_zero_write(), test_rotation_uses_stable_cursor_and_does_not_change_call_revision() (+2 more)

### Community 65 - "Development Rules & Constraints"
Cohesion: 0.15
Nodes (14): Child Manager Agent Development Rules, Data Model and Kindergarten Isolation, Fact Sources and Conflict Handling, GitHub Issue Execution Scope Fact Source, Kindergarten ID Isolation Field, One-Day Activity Plan Business Invariants, PRD/Specs Architecture Decision Records Fact Source, README Product Overview Fact Source (+6 more)

### Community 66 - "Job & Prompt Test Status"
Cohesion: 0.18
Nodes (8): prompt_test_status(), PromptTestStatus, 异步提示词测试的稳定中文状态与无障碍语义。, should_poll(), prompt_edit_version_id(), prompt_test_record_text(), 刷新时优先恢复未发布草稿，避免用已发布正文覆盖编辑态。, 将服务端已脱敏的测试运行渲染为可读历史记录。

### Community 67 - "NiceGUI Web Entry"
Cohesion: 0.25
Nodes (11): main(), 仅绑定回环地址的 NiceGUI Web 入口。, _require_loopback(), _validate_cookie_security(), configure_logging(), EventDict, 递归清除 Web 日志中的凭证和内部 URL。, _redact() (+3 more)

### Community 68 - "Password & Identity Utilities"
Cohesion: 0.11
Nodes (29): normalize_phone(), normalize_username(), hash_password(), password_needs_rehash(), password_violations(), Path, verify_password(), _weak_passwords() (+21 more)

### Community 69 - "Admin Initialization"
Cohesion: 0.20
Nodes (20): ArgumentParser, activate_initialization(), migrate_passkeys(), _native_url(), datetime, UUID, 首位管理员的部署控制台初始化与双人核验激活。, 仅在通行密钥已登记并完成两位预登记人员核验后激活。 (+12 more)

### Community 70 - "Ports & Adapters Interfaces"
Cohesion: 0.21
Nodes (9): AiClient, Clock, DependencyCheck, JobBroker, datetime, Protocol, UUID, M1 外部边界所需的最小 Protocol。 (+1 more)

### Community 71 - "AI Generation Architecture"
Cohesion: 0.18
Nodes (14): 安全模型档案与提示词生命周期, AI 输入、提示词、模型与 Schema 冻结上下文, 不可变脱敏审计与外部故障隔离, GitHub Issue #10, M6 T087–T126 in_progress，T103 为下一项, Batch 父任务不执行且状态由四个子任务派生, 数据库提交后 Redis 故障仍保持 202 pending_dispatch, AI 外呼前实时重验账号、角色、班级、教案与模型 (+6 more)

### Community 72 - "AI Model Profile Tests"
Cohesion: 0.23
Nodes (19): ai_admin_client(), _profile_payload(), Any, TestClient, _resolver(), test_admin_creates_write_only_masked_profile_and_cannot_read_key(), test_call_fields_increment_revision_but_display_and_limits_do_not(), test_disable_preserves_profile_and_default_switch_is_tenant_local() (+11 more)

### Community 73 - "Invitation Tests"
Cohesion: 0.33
Nodes (13): _base64url(), _create_teacher(), _issue(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes(), test_invitation_is_single_use_reissuable_and_revocable() (+5 more)

### Community 74 - "OpenAPI Contract Tests"
Cohesion: 0.40
Nodes (13): _assert_operation_contract(), _canonical_schema(), _effective_security(), _operations(), _parameter_shape(), Any, 运行时 OpenAPI 与冻结身份契约的一致性门禁。, _request_schema() (+5 more)

### Community 75 - "Settings Permissions Tests"
Cohesion: 0.33
Nodes (12): admin_session(), CurrentSessionDependency, _provision_associated_teacher(), TestClient, UUID, _session_for(), teacher_client(), test_all_settings_routes_require_authentication() (+4 more)

### Community 76 - "api/test_prompt_test_jobs.py"
Cohesion: 0.33
Nodes (17): FailingDispatcher, prompt_job_client(), _provision_model_and_version(), Any, TestClient, _resolver(), test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure(), test_draft_version_can_be_tested_before_publication() (+9 more)

### Community 77 - "Quality Gates & Docs"
Cohesion: 0.15
Nodes (13): 执行授权边界, 可收集且无错误的 RED 门禁, contracts/, data-model.md, graphify-out/graph.json, 常规测试禁止真实 AI、节假日及其他外网调用, 阶段依赖与执行顺序, plan.md (+5 more)

### Community 78 - "Credential Management Tests"
Cohesion: 0.36
Nodes (12): _base64url(), _insert_credential(), _native_url(), MonkeyPatch, TestClient, UUID, _registration_credential(), test_admin_cannot_revoke_last_active_admin_last_credential() (+4 more)

### Community 79 - "Migration Tests"
Cohesion: 0.09
Nodes (25): migrated_database(), MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds(), test_identity_migration_is_idempotent(), MonkeyPatch, settings_database(), test_age_group_seed_is_fixed_and_idempotent(), test_area_constraints_allow_empty_collections_but_reject_duplicate_names() (+17 more)

### Community 80 - "AI Prompt Settings Tests"
Cohesion: 0.19
Nodes (7): _job_status_module(), Any, MonkeyPatch, test_controls_have_keyboard_focus_and_error_label_associations(), test_job_status_recovers_configuration_change_with_chinese_action(), test_job_status_refreshes_until_terminal_and_restores_after_page_reload(), test_settings_controls_call_model_prompt_and_job_public_api_seams()

### Community 81 - "Auth Contract Tests"
Cohesion: 0.21
Nodes (7): APIRoute, Any, _resolve(), _runtime_routes(), test_auth_success_and_logout_lock_two_raw_cookie_headers(), test_runtime_auth_router_matches_frozen_passkey_paths(), test_runtime_auth_success_statuses_match_frozen_contract()

### Community 82 - "AI Prompt Repository Tests"
Cohesion: 0.30
Nodes (9): _modules(), Any, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_call_configuration_change_set_matches_the_frozen_revision_rules(), test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup(), test_model_reads_and_writes_are_tenant_scoped(), test_prompt_run_frozen_fields_cannot_be_updated() (+1 more)

### Community 83 - "validate_prompt_result_schema"
Cohesion: 0.20
Nodes (15): prompt_spec(), Any, validate_prompt_result(), validate_prompt_result_schema(), validate_prompt_variables(), _contract(), Any, ModuleType (+7 more)

### Community 84 - "Feature Milestones"
Cohesion: 0.24
Nodes (11): AI Generation Behavior Rules, AI Prompt Management System, Daily Lesson Plan System, Word Document Export, Issue #11 - M6 AI Async Generation, M4 AI Model & Prompt Basics, M5 Manual Lesson Plan Closure, M6 AI Async Generation (+3 more)

### Community 85 - "OpenAPI Configuration"
Cohesion: 0.29
Nodes (9): _apply_operation_contract(), configure_openapi(), _no_content_response(), _operation(), Any, FastAPI, M2 运行时 OpenAPI 的集中契约装配。, 返回缓存后的 M2 运行时 OpenAPI 生成器。 (+1 more)

### Community 86 - "Dev Handoff & Milestones"
Cohesion: 0.29
Nodes (11): Dev Handoff 2026-07-24, 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。, Milestone M2: Core Authentication & Permissions, Milestone M3: Settings, Milestone M3A: Password + TOTP Backup Login, Tasks T001–T002: Issue #8 & Docs Baseline, Tasks T003–T009: RED Gate for M3A, Tasks T010–T015: M3A Backup Auth Foundation (+3 more)

### Community 87 - "test_recovery.py"
Cohesion: 0.26
Nodes (16): _authentication_credential(), _base64url(), _identity_service(), _native_url(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes() (+8 more)

### Community 88 - "test_identity_isolation.py"
Cohesion: 0.32
Nodes (14): Event, TeacherInput, _insert_kindergarten(), _insert_user(), UUID, test_cross_kindergarten_role_assignment_is_rejected_by_composite_foreign_key(), test_refresh_replacement_cannot_cross_kindergarten(), test_refresh_revocation_serializes_with_rotation_and_revokes_the_new_token() (+6 more)

### Community 89 - "Backup Auth Contract Tests"
Cohesion: 0.24
Nodes (7): Any, _resolve(), _runtime_routes(), test_backup_contract_marks_request_and_one_time_response_secrets(), test_runtime_router_exposes_the_user_story_2_endpoints(), test_runtime_router_matches_the_frozen_backup_contract(), test_runtime_user_story_2_openapi_matches_frozen_security_and_responses()

### Community 90 - "AI Client Tests"
Cohesion: 0.44
Nodes (10): _modules(), Any, _resolver(), test_client_caps_retry_after_at_sixty_seconds(), test_client_errors_are_stable_and_never_include_key_or_prompt(), test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin(), test_client_posts_openai_compatible_request_with_fixed_limits(), test_client_rejects_redirects_without_following_them() (+2 more)

### Community 91 - "issue_secret"
Cohesion: 0.32
Nodes (12): _digest(), issue_secret(), IssuedSecret, StrEnum, 生成 256 位一次性秘密，持久化对象中只保留 purpose 绑定摘要。, 以常量时间比较 purpose 绑定摘要。, SecretPurpose, SecretRecord (+4 more)

### Community 92 - "Request ID Middleware"
Cohesion: 0.22
Nodes (7): API 请求 ID 与追踪 ID 中间件。, _request_id(), RequestContextMiddleware, ASGIApp, Receive, Scope, Send

### Community 93 - "BFF Proxy"
Cohesion: 0.29
Nodes (9): BffResponse, proxy_request(), AsyncBaseTransport, 按固定 allowlist 转发请求，并保留响应原始多值头。, MonkeyPatch, test_proxy_ignores_process_proxy_environment(), test_proxy_preserves_auth_set_cookie_as_raw_headers(), test_proxy_preserves_request_and_rebuilds_client_ip() (+1 more)

### Community 94 - "DB Session Management"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 95 - "Client IP Resolution"
Cohesion: 0.33
Nodes (8): Collection, parse_trusted_bff_peers(), 只接受显式配置的回环 BFF socket peer。, resolve_client_ip(), test_configured_loopback_bff_peer_can_supply_internal_client_ip(), test_non_loopback_peer_cannot_be_configured_as_trusted_bff(), test_trusted_bff_peers_are_empty_until_explicitly_configured(), test_untrusted_peer_cannot_supply_internal_client_ip()

### Community 96 - "test_ai_preview_adoption.py"
Cohesion: 0.30
Nodes (11): create_completed_ai_preview(), TestClient, UUID, _native_url(), TestClient, UUID, _snapshot_count(), test_adopt_merges_preview_once_and_repeated_request_creates_no_second_snapshot() (+3 more)

### Community 97 - "Workday Cache Repository"
Cohesion: 0.38
Nodes (5): Any, date, datetime, UUID, WorkdayCacheRepository

### Community 98 - "schemas.py"
Cohesion: 0.30
Nodes (11): _area_complete(), content_completeness(), _group_activity_complete(), _morning_activity_complete(), _morning_talk_complete(), parse_content_for_editing(), Any, 已知且有效的版本返回强类型内容，未知版本保持原始数据只读。 (+3 more)

### Community 99 - "test_auth_assurance.py"
Cohesion: 0.38
Nodes (6): datetime, _session(), test_backup_reauthentication_only_authorizes_add_passkey_for_five_minutes(), test_expired_backup_reauthentication_cannot_add_passkey(), test_recent_webauthn_proof_satisfies_high_risk_identity_boundary(), test_restricted_enrollment_session_cannot_enter_business_routes()

### Community 100 - "Workday Service Tests"
Cohesion: 0.29
Nodes (6): _module(), MonkeyPatch, test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls(), test_local_result_wins_conflict_and_uses_one_hour_cache(), test_timor_client_enforces_one_total_deadline(), test_unsupported_local_calendar_range_softly_falls_back_to_online()

### Community 101 - "Repo Branches & Docs"
Cohesion: 0.33
Nodes (9): dev - Implementation Branch, docs - Design & Spec Baseline, main - Stable Release Baseline, CONTEXT.md - Project Status, Old Repository - kindergartenManager, README.md - Product Overview, Implementation Plan - Daily Activity Plan, Quickstart - Acceptance Contract (+1 more)

### Community 102 - "Security Threat Model"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 103 - "Spec Tasks & Roadmap"
Cohesion: 0.25
Nodes (9): specs/002-password-totp-backup-login/tasks.md, M8 性能、安全、无障碍与交付验收, 唯一教案、保存、历史、归档与恢复, Polish 与 M8 完整验收, M9 生产部署复审排除在任务范围外, Roadmap M1–M8 范围, US1 M3A 密码与 TOTP 备用登录, US2 纯手工教案闭环 (+1 more)

### Community 104 - "Secret Encryption Tests"
Cohesion: 0.39
Nodes (8): _context(), _encryption_module(), Any, Path, test_development_key_provider_requires_owner_only_file_outside_repository(), test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution(), test_totp_secret_envelope_round_trips_with_random_96_bit_nonce(), test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce()

### Community 105 - "Milestones Overview"
Cohesion: 0.25
Nodes (8): Settings System - Kindergarten/Semester/Class, Password + TOTP Backup Login, WebAuthn Passkey Authentication, M0 Shared Design Baseline, M1 Engineering Skeleton, M2 Authentication & Authorization, M3 Essential Settings, M3A Password & TOTP Backup Login

### Community 106 - "AI Prompts & Jobs Migration"
Cohesion: 0.36
Nodes (6): Any, Column, 建立 AI 模型、提示词与 PostgreSQL 权威任务基础。, _seed_defaults(), _timestamps(), upgrade()

### Community 107 - "test_init_admin_cli.py"
Cohesion: 0.40
Nodes (10): _prepare_last_admin_recovery(), CompletedProcess, MonkeyPatch, UUID, _run_cli(), test_init_admin_activate_requires_two_distinct_pre_registered_approvers(), test_init_admin_cli_exposes_start_activate_and_migration_commands(), test_init_admin_start_creates_pending_account_and_one_time_secret_without_password() (+2 more)

### Community 108 - "Backup Login Migration Test"
Cohesion: 0.46
Nodes (7): Script, _backup_revision(), MonkeyPatch, test_backup_auth_migration_creates_isolated_credentials_and_enrollments(), test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(), test_backup_auth_revision_follows_settings_and_precedes_lesson_plans(), test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade()

### Community 109 - "User Stories Activity Plan"
Cohesion: 0.25
Nodes (8): Feature Specification: 首期一日活动计划完整闭环, User Story 1: Admin Setup, User Story 2: Manual Lesson Plan Loop, User Story 3: Admin Configure Model and Prompts, User Story 4: Teacher Uses AI by Section, User Story 5: Teacher Processes Group Activity Source, User Story 6: Teacher Export and Download Fixed Word, User Story 7: Admin Audit and Degradable Service

### Community 110 - "AI Prompt Contract Tests"
Cohesion: 0.32
Nodes (6): Any, _schema(), test_model_and_job_contracts_freeze_revision_and_stable_errors(), test_prompt_test_contract_exposes_only_redacted_input_summary(), test_prompt_test_fingerprint_changes_across_prompt_codes(), test_runtime_exposes_the_complete_frozen_m4_route_surface()

### Community 111 - "OpenAPI Document Tests"
Cohesion: 0.39
Nodes (7): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_document_is_valid_31(), test_openapi_keeps_nicegui_as_the_only_browser_entry(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 112 - "totp.py"
Cohesion: 0.33
Nodes (8): candidate_totp_counters(), _counter(), generate_totp(), _hotp(), RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。, 返回当前时间步及相邻一个时间步，按 counter 递增排序。, 按固定 SHA-1、6 位、30 秒参数生成 TOTP。, _secret_bytes()

### Community 113 - "Content Validation Tests"
Cohesion: 0.54
Nodes (7): _contracts(), _schemas(), test_completeness_is_independent_from_progressive_schema_validation(), test_empty_v1_content_supports_progressive_manual_editing(), test_reflection_is_nfkc_normalized_and_limited_to_200_codepoints(), test_statement_and_question_punctuation_are_strictly_chinese(), test_unknown_fields_and_unknown_content_versions_are_not_silently_coerced()

### Community 114 - "AI Key Envelope Tests"
Cohesion: 0.39
Nodes (7): _module(), Any, Path, test_ai_key_envelope_rejects_tampering_and_cross_profile_substitution(), test_ai_key_envelope_round_trips_with_random_96_bit_nonce(), test_file_key_provider_requires_owner_only_files_outside_repository(), test_static_key_provider_reads_old_key_but_writes_with_active_key()

### Community 115 - "AI Model URL Policy"
Cohesion: 0.57
Nodes (7): _module(), Any, _resolver(), test_policy_accepts_only_allowlisted_public_https_and_checks_every_address(), test_policy_detects_dns_rebinding_before_connect(), test_policy_rejects_non_https_and_non_public_networks(), test_policy_requires_explicit_server_allowlist()

### Community 116 - "Lesson Plans Migration & Catalog"
Cohesion: 0.43
Nodes (7): _module(), Any, test_catalog_assigns_task_specific_minimum_variable_whitelists(), test_catalog_freezes_seven_codes_whitelists_schemas_and_hashes(), test_catalog_input_validation_excludes_teacher_identity_and_unknown_fields(), test_catalog_result_schemas_are_strict(), test_catalog_result_schemas_match_the_frozen_openapi_shapes()

### Community 117 - "Database Migrations & Dependencies"
Cohesion: 0.29
Nodes (7): Alembic Database Migrations, PostgreSQL Production Database, pyproject.toml Dependency Management, Python 3.14+ Minimum Version, SQLAlchemy 2.x ORM, Technology and Dependency Baseline, uv.lock Version Locking

### Community 118 - "test_password_to_passkey.py"
Cohesion: 0.54
Nodes (7): _assert_passkey_revisions_exist(), _native_url(), MonkeyPatch, test_contract_removes_password_data_and_downgrade_recreates_only_empty_columns(), test_expand_moves_existing_accounts_to_enrollment_and_revokes_old_sessions(), test_passkey_migration_has_explicit_expand_and_contract_boundaries(), _user_columns()

### Community 119 - "Security Events & Backup Auth"
Cohesion: 0.18
Nodes (11): api_request(), _javascript_helpers(), perform_authentication(), perform_registration(), post_same_origin(), security_event_text(), register_users_page(), MonkeyPatch (+3 more)

### Community 120 - "Passkey Expand Migration"
Cohesion: 0.52
Nodes (5): Any, Column, _tenant_identity_columns(), _timestamps(), upgrade()

### Community 121 - "Project Constitution & Guidelines"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 122 - "Independent Runtime Units"
Cohesion: 0.38
Nodes (7): FastAPI API 独立运行单元, 方法、路由、实际 path/query/body 的规范幂等指纹, Foundational T009–T020, docs/development/local-development-environments.md, Setup T001–T008, NiceGUI Web 独立运行单元, 后台 Worker 独立运行单元

### Community 123 - "Prompt Renderer Tests"
Cohesion: 0.48
Nodes (6): _module(), Any, test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(), test_renderer_fails_for_missing_variable_before_external_call(), test_renderer_rejects_every_non_frozen_placeholder_form(), test_renderer_uses_stable_json_and_never_recursively_renders_values()

### Community 124 - "0006_lesson_plans.py"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 125 - "Identity & Audit Migration"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 126 - "Settings Migration"
Cohesion: 0.20
Nodes (5): Alembic, Any, Column, _timestamps(), upgrade()

### Community 127 - "Password/TOTP/Backup Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 128 - "_render_prompt_test_run_schema"
Cohesion: 1.00
Nodes (3): JsonSchemaValue, _render_prompt_test_run_schema(), _render_union_as_one_of()

### Community 129 - "AI Generation Results Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 130 - "Word Template Processing"
Cohesion: 0.40
Nodes (6): 固定 Word 模板原件哈希与样式完整性, templates/teacherplan/teacherplan.docx, 集体活动拆分后再新增环节的两阶段流程, US5 集体活动原始教案处理, US6 固定 Word 导出与重新下载, 固定模板 Word 导出、历史与重新授权下载

### Community 132 - "TOTP Tests"
Cohesion: 0.53
Nodes (5): Any, test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps(), test_totp_rejects_the_same_or_earlier_counter_after_success(), test_totp_secret_is_unique_high_entropy_base32(), _totp_module()

### Community 133 - "Service Roles & Boundaries"
Cohesion: 0.60
Nodes (5): Background Worker Role, FastAPI API Service Role, NiceGUI Web Service Role, Service Boundaries and Dependency Direction, Shared Contracts Package

### Community 134 - "Service Infrastructure"
Cohesion: 0.50
Nodes (5): FastAPI API Service, NiceGUI Web Service, PostgreSQL Database, Redis Message Broker, Dramatiq Background Worker

### Community 135 - "Branch Responsibilities"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 138 - "Kindergarten Setup"
Cohesion: 0.50
Nodes (5): 园所、学期、班级、教师关系与区域设置, kindergarten_id 园所隔离, US1 M2 认证、授权与身份审计, US1 M3 首期必要设置, WebAuthn 身份安全与会话撤销

### Community 139 - "AI Key Rotation CLI"
Cohesion: 0.60
Nodes (4): CompletedProcess, _run(), test_bootstrap_cli_exposes_rotation_without_master_key_arguments(), test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets()

### Community 141 - "Calendar Tests"
Cohesion: 0.70
Nodes (4): _calendar(), test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic(), test_out_of_semester_week_number_and_text_are_both_empty(), test_semester_start_week_is_week_one_and_increments_each_monday()

### Community 142 - "Branch Roles"
Cohesion: 0.50
Nodes (4): Dev Branch Role, Development Workflow and Git Rules, Docs Branch Role, Main Branch Role

### Community 144 - "Docker & CI Config"
Cohesion: 0.67
Nodes (4): Docker Compose 开发环境配置, GitHub Actions 质量检查工作流, PostgreSQL, Redis

### Community 145 - "Core Database Tables"
Cohesion: 0.50
Nodes (4): Age Groups Table, Class Teachers Table, Classes Table, Daily Activity Plans Table

### Community 146 - "Database Concepts"
Cohesion: 0.50
Nodes (4): Composite Foreign Keys Concept, Kindergarten Isolation Concept, Kindergartens Table, Users Table

### Community 148 - "Backup Login Spec"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 150 - "Lesson Plan Contract Tests"
Cohesion: 0.83
Nodes (3): _contracts(), test_open_and_write_contracts_do_not_accept_tenant_or_ownership_mutation(), test_plan_snapshot_and_page_contracts_are_bounded_and_stable()

### Community 155 - "Knowledge Graph Tools"
Cohesion: 1.00
Nodes (3): Codebase-Memory MCP Usage, Codegraph Usage, Graphify Knowledge Graph Usage

### Community 157 - "Migration Order"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

### Community 161 - "AI Step Red Text"
Cohesion: 0.67
Nodes (3): AI-Added Step Red Text, Structured Daily Activity Sections, Daily Activity Plan Word Layout

## Knowledge Gaps
- **185 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+180 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **87 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `班级与教师配置` (2× useful, score=1.352895454)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ActorFixture` connect `Backup Enrollment Tests` to `test_ai_preview_adoption.py`, `Identity Service`, `AI Job Recovery Tests`, `AI Model Profile Tests`, `Auth Throttle`, `TOTP Secret Encryption`, `Invitation Tests`, `api/test_prompt_test_jobs.py`, `Settings Permissions Tests`, `Credential Management Tests`, `WebAuthn Tests`, `Passkey Migration & Tests`, `AI Batch Tests`, `test_recovery.py`, `Backup Maintenance Tests`, `AI Preview Lifecycle Tests`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `IdentityError` connect `Identity Service` to `Authentication Endpoints`, `Audit Service`, `Auth Router & Contracts`, `AI Result Repository`, `WebAuthn Challenges`, `Users Router`, `Auth Challenge Verification`, `Settings Repository`, `Calendar Workday`, `Lesson Plan Service`, `Job Query Service`, `TOTP Secret Encryption`, `CSRF Token`, `AI Job Runner`, `Plan Editor Page`, `FastAPI App Setup`, `ai_models.py`, `Backup Maintenance Tests`, `Health Check`, `Health Dependencies`, `Password & Identity Utilities`, `AI Model Profile Tests`, `test_recovery.py`, `issue_secret`, `test_auth_assurance.py`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `IdentityRepository` connect `Identity Repository` to `Identity Service`, `Password & Identity Utilities`, `Admin Initialization`, `Auth Throttle`, `AI Model Profile Tests`, `TOTP Secret Encryption`, `WebAuthn Challenges`, `Backup Auth Isolation Tests`, `Users Router`, `test_identity_isolation.py`, `Auth Challenge Verification`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `ActorFixture` (e.g. with `StaticIdentitySecretKeyProvider` and `IdentityService`) actually correct?**
  _`ActorFixture` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `IdentityError` (e.g. with `create_app()` and `HealthDependencies`) actually correct?**
  _`IdentityError` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 134 inferred relationships involving `ContractModel` (e.g. with `AuditEventReference` and `IdentityAuditEventCode`) actually correct?**
  _`ContractModel` has 134 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `SessionUser` (e.g. with `HealthDependencies` and `AuditRepository`) actually correct?**
  _`SessionUser` has 27 INFERRED edges - model-reasoned connections that need verification._