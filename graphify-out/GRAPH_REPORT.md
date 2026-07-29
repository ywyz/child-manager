# Graph Report - child-manager  (2026-07-29)

## Corpus Check
- 360 files · ~218,727 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3300 nodes · 9847 edges · 274 communities (187 shown, 87 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 867 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d6754cb8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Identity Repository
- Settings Routers
- Identity & Audit
- Auth Endpoints
- Job Recovery
- Observability
- Database Models
- Audit Events
- Auth Throttling
- AI Job Store
- AI Schemas
- Auth & CSRF
- AI Generation Service
- AI Job Actors
- AI Key Rotation
- Jobs Repository
- WebAuthn Tests
- Backup Auth API
- Test Helpers
- Plans Routers
- WebAuthn Challenges
- AI Execution Errors
- AI Batch Tests
- Prompts Routers
- User Management
- Architecture Boundaries
- Prompt Test Worker
- Quality Analysis
- AI Generation Tests
- Settings Repository
- Calendar Client
- Project Documentation
- Lesson Plan Repository
- Database Profile Tests
- Lesson Plan Service
- AI Client Retry
- Prompt Repository
- Domain Boundaries
- App Configuration
- Backup Enrollment Tests
- Job Query Service
- Login Throttling
- TOTP Encryption
- Development Environment
- Auth Sessions
- Job Dispatcher
- Prompt Test Store
- Test Configuration
- TOTP Utilities
- Local Dev Profiles
- AI Results Repository
- FastAPI Application
- Navigation Tests
- Jobs API
- API Startup Security Checks
- Backup Auth Isolation Tests
- Backup Maintenance Tests
- Plan Accessibility Tests
- Shell Scripts
- Prompt Schema Tests
- App Health Tests
- Health Checks
- AI Client & SSRF
- AI Preview Lifecycle Tests
- AI Key Rotation Tests
- Development Rules
- Job Status UI
- Web Entry
- Identity Helpers
- Admin Initialization
- Ports & Protocols
- Domain Documentation
- AI Generation Service Tests
- Invitation Tests
- OpenAPI Contract Tests
- Common Schemas
- Prompt Test API Tests
- Quality Gates
- Token Management
- Settings Migration Tests
- Prompt Settings Smoke Tests
- Auth Contract Tests
- Prompt Repository Tests
- Recovery Tests
- System Documentation
- OpenAPI Configuration
- Development Handoff
- AI Model Profile Tests
- Identity Isolation Tests
- Backup Auth Contract Tests
- AI Client Tests
- Plan AI Contract Tests
- Request Middleware
- BFF Proxy
- Session Management
- Client IP Resolution
- Scheduler & Recovery
- Workday Cache Repository
- Prompt Test Dispatch
- Auth Logic
- Workday Service Tests
- Development Branch Labels
- Security Defense Concepts
- Task Specification Tracking
- Secret Encryption Tests
- Feature Milestones Overview
- AI Prompts Jobs Migration
- Content Schemas
- Password TOTP Migration Tests
- Feature Spec User Stories
- Canonical Fingerprint
- OpenAPI Document Tests
- AI Generation Presave Tests
- Content V1 Validation Tests
- AI Key Envelope Tests
- AI Model URL Policy Tests
- Prompt Catalog Tests
- Technology Stack Baseline
- Password to Passkey Tests
- Backup Auth Smoke Tests
- Passkey Expand Migration
- Project Architecture Principles
- Service Units Specifications
- Prompt Renderer Tests
- Lesson Plans Migration
- Identity Audit Migration
- Database Migrations
- Password TOTP Migration
- Save Status Tracking
- AI Generation Results Migration
- Word Export Template Handling
- Users Contract Tests
- TOTP Algorithm Tests
- Service Boundary Definitions
- Deployment Infrastructure
- Development Workflow Roles
- Job Dispatcher
- Feature Branch Script
- Kindergarten Auth Setup
- AI Key Rotation CLI Tests
- Calendar Tests
- Branch Workflow Roles
- Identity Migration Tests
- Core Entity Tables
- Database Schema Concepts
- Backup Login Feature
- Lesson Plan Contract Tests
- Fake Calendar Fixture
- Fixed Clock Fixture
- Fake Job Broker
- Development Tools Usage
- CSRF Protection Tests
- Migration Dependency Order
- JSON Schema Utilities
- Lease Expiration Utility
- Lesson Plan UI Components
- Fake AI Client
- Child Manager App
- Background Worker App
- AI Results Jobs Tables
- AI Model Profile Tables
- Prompt Definition Tables
- User Roles Tables
- Database Backend Setup
- Common Passwords List
- Backend Module
- Shared Contracts Module
- Prerequisites Script
- Setup Plan Script
- Setup Tasks Script
- Web Tests Module
- Account Invitations Table
- Account Recovery Requests Table
- Age Groups Table
- AI Generation Results Table
- AI Profile Capabilities Table
- AI Model Profiles Table
- Audit Events Table
- Background Jobs Table
- Backup Auth Credentials Table
- Backup Auth Enrollments Table
- Bootstrap Initializations Table
- Class Areas Table
- Class Teachers Table
- Classes Table
- Activity Plan Exports Table
- Activity Plan Snapshots Table
- Daily Activity Plans
- Identity Verification Approvals
- Snapshot Immutability
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
- Application Transactions
- External Key Source
- M5 M4 Dependency Path
- Child Manager
- PostgreSQL Database
- Dev Workflow Quality
- Governance
- Tech Security Constraints
- Activity Plan Quality
- Password TOTP Backup

## God Nodes (most connected - your core abstractions)
1. `ActorFixture` - 192 edges
2. `IdentityError` - 175 edges
3. `SessionUser` - 160 edges
4. `csrf_headers()` - 159 edges
5. `ContractModel` - 151 edges
6. `IdentityRepository` - 133 edges
7. `IdentityService` - 103 edges
8. `AuditRepository` - 76 edges
9. `require_csrf()` - 70 edges
10. `provision_editable_plan_context()` - 67 edges

## Surprising Connections (you probably didn't know these)
- `一日活动计划需求面` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_020708_请根据现有文档_和旧仓库的文件思考如何撰写_docs_prd_lesson_management_m.md → docs/faq/combined-audit.md
- `ADR 直接文件核对` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_025449_哪些关键架构决策需要独立_adr_哪些已经确认_决策之间有什么依赖.md → docs/faq/combined-audit.md
- `校正后的数据模型边界` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md → docs/faq/combined-audit.md
- `test_identity_repository_exposes_atomic_backup_auth_operations()` --indirect_call--> `IdentityRepository`  [INFERRED]
  tests/repository/test_backup_auth_isolation.py → packages/backend/identity/repository.py
- `test_repository_exposes_atomic_passkey_lifecycle_operations()` --indirect_call--> `IdentityRepository`  [INFERRED]
  tests/repository/test_identity_isolation.py → packages/backend/identity/repository.py

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

## Communities (274 total, 87 thin omitted)

### Community 0 - "Identity Repository"
Cohesion: 0.06
Nodes (19): _backup_credential(), _backup_enrollment(), BackupCredentialRecord, BackupEnrollmentRecord, BackupRevocationResult, BackupSecurityEventRecord, ChallengeRecord, _credential() (+11 more)

### Community 1 - "Settings Routers"
Cohesion: 0.05
Nodes (92): AgeGroup, AiKeyProvider, AiModelProfile, AiModelServiceDependency, _age_group(), _ai_model(), _area(), _class() (+84 more)

### Community 2 - "Identity & Audit"
Cohesion: 0.11
Nodes (22): identity_service(), AuditRepository, ChallengePurpose, StrEnum, AuthResult, _challenge_digest(), _client_challenge(), _decode_base64url() (+14 more)

### Community 3 - "Auth Endpoints"
Cohesion: 0.18
Nodes (49): authenticate_with_password_and_totp(), authentication_start(), authentication_verify(), backup_authentication_status(), bootstrap_options(), bootstrap_verify(), _check_public_throttle(), _clear_auth_cookies() (+41 more)

### Community 4 - "Job Recovery"
Cohesion: 0.12
Nodes (18): ai_adoption_service(), AiAdoptionService, _native_url(), preview_is_current(), AiTaskCode, Any, datetime, JsonValue (+10 more)

### Community 5 - "Observability"
Cohesion: 0.22
Nodes (14): merge_request_context(), EventDict, 递归清除日志中的密钥、令牌、认证材料与 URL 凭证。, 将当前请求关联字段合并到真实 structlog 事件。, _redact(), redact_mapping(), _redact_url(), request_context() (+6 more)

### Community 6 - "Database Models"
Cohesion: 0.10
Nodes (40): DeclarativeBase, AuditEvent, Base, AccountInvitation, AccountRecoveryRequest, BackupAuthCredential, BackupAuthEnrollment, BootstrapInitialization (+32 more)

### Community 7 - "Audit Events"
Cohesion: 0.30
Nodes (18): _base64url(), _enable_backup(), _generic_failure_payload(), MonkeyPatch, Response, TestClient, _registration_credential(), _request() (+10 more)

### Community 8 - "Auth Throttling"
Cohesion: 0.13
Nodes (15): _auth_throttle(), MemoryAuthThrottle, datetime, Redis, timedelta, 公开身份 ceremony 的来源限流公共 seam。, 按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。, 多进程 API 使用的 Redis 固定窗口实现。 (+7 more)

### Community 9 - "AI Job Store"
Cohesion: 0.10
Nodes (20): AiExecutionContext, AiJobAuthorizer, AiJobStore, AiJobStoreProtocol, _log_sanitized_exception(), Any, datetime, Exception (+12 more)

### Community 10 - "AI Schemas"
Cohesion: 0.32
Nodes (35): PromptSpec, BaseModel, 固定提示词目录、输入与结果 Schema 路由。, _spec(), AiAreaGame, AiDailyReflection, AiGroupActivity, AiMorningActivity (+27 more)

### Community 11 - "Auth & CSRF"
Cohesion: 0.08
Nodes (54): _allowed_origins(), _loopback_aliases(), 同源 Cookie、WebAuthn、邀请、恢复与会话端点。, ContractModel, BaseModel, ExportReference, AdminCredentialRevocationResult, AuthenticationCredential (+46 more)

### Community 12 - "AI Generation Service"
Cohesion: 0.19
Nodes (14): ai_generation_service(), reflection_generation_service(), AiGenerationResultRepository, AiGenerationAcceptance, AiGenerationService, _FrozenTask, Any, UUID (+6 more)

### Community 13 - "AI Job Actors"
Cohesion: 0.08
Nodes (37): Actor, AiJobScopeResolver, AiRunner, build_ai_job_runner(), build_ai_result_repository(), build_prompt_test_executor(), build_worker_scope_resolver(), _native_url() (+29 more)

### Community 14 - "AI Key Rotation"
Cohesion: 0.27
Nodes (14): admin_session(), current_session(), AuthenticatedSessionDependency, CurrentSessionDependency, _provision_associated_teacher(), TestClient, UUID, _session_for() (+6 more)

### Community 15 - "Jobs Repository"
Cohesion: 0.23
Nodes (10): _ai_job(), AiJobRecord, _job(), JobRecord, JobRepository, Any, datetime, PostgreSQL 权威后台任务 Repository。 (+2 more)

### Community 16 - "WebAuthn Tests"
Cohesion: 0.14
Nodes (37): csrf_headers(), _base64url(), _credential(), MonkeyPatch, TestClient, _registration_credential(), test_authentication_options_are_username_less_and_browser_ready(), test_authentication_options_do_not_increment_failure_limit() (+29 more)

### Community 17 - "Backup Auth API"
Cohesion: 0.14
Nodes (25): backup_auth_api_request(), backup_login_api_request(), backup_reauthentication_api_request(), BffResponse, NiceGUI 服务端 BFF 客户端的公开接缝。, 以请求正文提交两项备用因素，不把秘密放入 URL。, 为当前备用会话取得仅可新增通行密钥的短时证明。, 读取本人最近 20 条内建安全事件，不产生已读状态。 (+17 more)

### Community 18 - "Test Helpers"
Cohesion: 0.16
Nodes (23): pytest, admin_client(), passkey_client(), MonkeyPatch, TestClient, 通过 FastAPI 身份依赖注入建立已 step-up 管理员，不借用密码登录。, _event(), test_ai_audit_event_codes_cover_creation_retries_result_reject_and_adopt() (+15 more)

### Community 19 - "Plans Routers"
Cohesion: 0.09
Nodes (63): AiAdoptionServiceDependency, AiGenerationServiceDependency, AiRetryServiceDependency, adopt_ai_preview(), get_ai_preview(), get_job(), alias, CurrentSessionDependency (+55 more)

### Community 20 - "WebAuthn Challenges"
Cohesion: 0.10
Nodes (34): ChallengeBinding, ChallengeRecord, consume_challenge(), issue_challenge(), IssuedChallenge, datetime, WebAuthn ceremony challenge 的公共领域 seam。, 签发绑定上下文、五分钟有效且只保存摘要的 challenge。 (+26 more)

### Community 21 - "AI Execution Errors"
Cohesion: 0.12
Nodes (16): AiClientError, RuntimeError, CurrentModelCallProfile, ProfileCallLimiter, PromptTestAuthorizer, PromptTestExecutionContext, PromptTestExecutor, PromptTestRetry (+8 more)

### Community 22 - "AI Batch Tests"
Cohesion: 0.15
Nodes (38): provision_enabled_ai_model(), provision_editable_plan_context(), date, TestClient, TestClient, test_generation_reject_adopt_and_retry_write_sanitized_audit_rows(), _configure_batch_areas(), _idempotent_headers() (+30 more)

### Community 23 - "Prompts Routers"
Cohesion: 0.17
Nodes (30): clear_prompt_tests(), create_prompt_test(), _definition(), get_prompt(), get_prompt_test(), get_prompt_version(), _job(), list_prompt_tests() (+22 more)

### Community 24 - "User Management"
Cohesion: 0.19
Nodes (32): activate(), create_user(), credential_revoke(), credentials(), deactivate(), get_user(), _invitation(), invitation_issue() (+24 more)

### Community 25 - "Architecture Boundaries"
Cohesion: 0.08
Nodes (34): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+26 more)

### Community 26 - "Prompt Test Worker"
Cohesion: 0.15
Nodes (20): _context(), FakeAuthorizer, FakeClient, FakeStore, _modules(), Any, datetime, UUID (+12 more)

### Community 27 - "Quality Analysis"
Cohesion: 0.07
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+25 more)

### Community 28 - "AI Generation Tests"
Cohesion: 0.07
Nodes (71): JobMessage, Redis 中唯一允许传递的最小任务消息。, SimpleNamespace, _insert_job(), _insert_other_tenant_plan(), _insert_result(), _native_url(), _provision_dependencies() (+63 more)

### Community 29 - "Settings Repository"
Cohesion: 0.06
Nodes (51): settings_service(), IntegrityError, NoReturn, AgeGroupRecord, _ai_profile(), AreaInput, AreaRecord, call_configuration_changed() (+43 more)

### Community 30 - "Calendar Client"
Cohesion: 0.19
Nodes (13): canonical_json_sha256(), generation_input_sha256(), AiTaskCode, JsonValue, 对 JSON 值进行稳定序列化并计算 SHA-256。, 计算逐任务实际输入哈希。      ``server_input`` 只应包含该任务白名单内的服务端输入。采用预览时，调用方必须复用任务     创建时冻结的, section_sha256(), _native_url() (+5 more)

### Community 31 - "Project Documentation"
Cohesion: 0.07
Nodes (32): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+24 more)

### Community 32 - "Lesson Plan Repository"
Cohesion: 0.06
Nodes (51): lesson_plan_service(), map_timor_payload(), AsyncBaseTransport, date, TimorWorkdayClient, WorkdayResult, Any, date (+43 more)

### Community 33 - "Database Profile Tests"
Cohesion: 0.31
Nodes (15): MonkeyPatch, Path, test_environment_test_database_url_takes_precedence_over_profile(), test_test_database_profile_must_stay_outside_the_repository(), test_test_database_profile_rejects_group_or_other_access(), test_test_database_url_rejects_nonisolated_or_nonpostgresql_targets(), test_test_database_url_reports_missing_environment_and_profile(), test_test_database_url_uses_secure_repo_external_profile() (+7 more)

### Community 34 - "Lesson Plan Service"
Cohesion: 0.24
Nodes (12): candidate_totp_counters(), _counter(), generate_totp(), generate_totp_secret(), _hotp(), RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。, 生成认证器广泛兼容的 160 位无填充 Base32 种子。, 返回当前时间步及相邻一个时间步，按 counter 递增排序。 (+4 more)

### Community 35 - "AI Client Retry"
Cohesion: 0.13
Nodes (15): BaseTransport, ProviderNeutralAiClient, Resolver, AddStepStore, AlwaysTimeoutClient, InvalidAddStepClient, Any, datetime (+7 more)

### Community 36 - "Prompt Repository"
Cohesion: 0.14
Nodes (15): prompt_service(), _definition(), prompt_test_input_summary(), PromptDefinitionRecord, PromptRepository, PromptTestRunRecord, PromptVersionRecord, Any (+7 more)

### Community 37 - "Domain Boundaries"
Cohesion: 0.07
Nodes (29): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, Child Manager Daily Activity API, Identity and Settings Endpoints, Plans, Jobs, and Exports Endpoints, API v1 Contract (+21 more)

### Community 38 - "App Configuration"
Cohesion: 0.17
Nodes (16): main(), AppSettings, global_security_ready(), BaseModel, 拒绝在非开发环境或非回环地址关闭 Cookie Secure。, 验证进程启动时的 Cookie 与监听地址组合。, JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。, validate_cookie_security() (+8 more)

### Community 39 - "Backup Enrollment Tests"
Cohesion: 0.11
Nodes (34): ActorFixture, TestClient, test_admin_is_restricted_until_complete_backup_enrollment(), test_backup_status_and_enrollment_require_authentication(), test_enrollment_requires_password_and_totp_together_and_is_single_use(), test_expired_enrollment_cannot_enable_backup_auth(), test_new_enrollment_invalidates_the_previous_pending_enrollment(), test_replacing_enabled_material_revokes_only_related_backup_sessions() (+26 more)

### Community 40 - "Job Query Service"
Cohesion: 0.24
Nodes (5): _operation_parameters(), Any, _resolve(), test_age_groups_are_a_fixed_four_item_non_paginated_collection(), test_area_get_uses_default_20_maximum_100_pagination()

### Community 41 - "Login Throttling"
Cohesion: 0.17
Nodes (10): _digest(), MemoryLoginThrottle, datetime, Redis, timedelta, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision (+2 more)

### Community 42 - "TOTP Encryption"
Cohesion: 0.13
Nodes (22): _aad(), decrypt_totp_secret(), decrypt_totp_secret_with_provider(), encrypt_totp_secret(), encrypt_totp_secret_with_provider(), FileIdentitySecretKeyProvider, Path, UUID (+14 more)

### Community 43 - "Development Environment"
Cohesion: 0.08
Nodes (25): 本地开发环境规范, 仅回环开发依赖, 生产拓扑延后, 工作树资源隔离, M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线 (+17 more)

### Community 44 - "Auth Sessions"
Cohesion: 0.40
Nodes (5): _cookie_secure(), csrf(), _encode(), issue_csrf_token(), verify_csrf_token()

### Community 45 - "Job Dispatcher"
Cohesion: 0.20
Nodes (16): AiJobRetry, RuntimeError, 通知消息代理按权威任务给出的退避时间重投。, _ai_actor(), FakeRunner, FakeScopeResolver, PartiallyFailingRecoveryStore, datetime (+8 more)

### Community 46 - "Prompt Test Store"
Cohesion: 0.23
Nodes (6): _native_url(), PostgresPromptTestStore, Any, datetime, UUID, 提示词测试 Worker 的 PostgreSQL 权威状态适配器。

### Community 47 - "Test Configuration"
Cohesion: 0.20
Nodes (10): str, block_external_network(), isolated_database_url(), _native_psycopg_url(), MonkeyPatch, 只允许回环 TCP 和本机 Unix socket。, 为请求该夹具的测试创建并清理独立 PostgreSQL schema。, 保留连接字符串行为，但禁止失败报告通过 ``repr`` 展开凭据。 (+2 more)

### Community 48 - "TOTP Utilities"
Cohesion: 0.18
Nodes (18): login_page_text(), users_page_text(), BrowserContext, Page, _add_virtual_authenticator(), _auth_cookie_names(), _bootstrap_activate(), _bootstrap_start() (+10 more)

### Community 49 - "Local Dev Profiles"
Cohesion: 0.27
Nodes (8): _compose_config(), Any, Path, 双实现本地开发档位的 Compose 合同。, test_compose_accepts_temporary_image_overrides(), test_compose_uses_selected_local_profile(), test_quality_workflow_provides_an_isolated_postgresql_database(), test_test_database_url_requires_an_explicit_profile()

### Community 50 - "AI Results Repository"
Cohesion: 0.21
Nodes (11): AiGenerationResultRecord, _json_object(), _optional_uuid(), Any, datetime, 同园隔离的 AI 生成结果 Repository。, 将同园到期预览条件收敛为 expired，不修改结果正文或决策字段。, 按园所幂等清理短期正文，同时保留哈希和追溯元数据。 (+3 more)

### Community 51 - "FastAPI Application"
Cohesion: 0.13
Nodes (17): _error_response(), FastAPI, Request, UUID, FastAPI 应用装配、统一异常转换与健康端点。, _request_id(), Docker Compose 开发环境配置, GitHub Actions 质量检查工作流 (+9 more)

### Community 52 - "Navigation Tests"
Cohesion: 0.17
Nodes (16): navigation_for_capabilities(), 按 API capabilities 生成导航。, class_areas_page_text(), settings_page_text(), test_navigation_is_derived_from_current_api_capabilities(), BrowserActor, _free_port(), _m3_services() (+8 more)

### Community 53 - "Jobs API"
Cohesion: 0.15
Nodes (18): job_query_service(), JobStatus, BatchJobAggregationRepository, Any, UUID, `ai.batch` 父任务的只读状态投影。, 从恰好四个子任务派生父任务响应，不写入父任务执行字段。, JobQueryService (+10 more)

### Community 54 - "API Startup Security Checks"
Cohesion: 0.40
Nodes (10): _prepare_last_admin_recovery(), CompletedProcess, MonkeyPatch, UUID, _run_cli(), test_init_admin_activate_requires_two_distinct_pre_registered_approvers(), test_init_admin_cli_exposes_start_activate_and_migration_commands(), test_init_admin_start_creates_pending_account_and_one_time_secret_without_password() (+2 more)

### Community 55 - "Backup Auth Isolation Tests"
Cohesion: 0.25
Nodes (13): MonkeyPatch, UUID, RecordingConnection, RecordingResult, _seed_backup_repository(), test_admin_role_gate_restricts_and_then_releases_webauthn_sessions(), test_backup_credential_reads_are_scoped_to_kindergarten_and_user(), test_backup_version_change_revokes_only_related_sessions() (+5 more)

### Community 56 - "Backup Maintenance Tests"
Cohesion: 0.40
Nodes (12): _change_actor_to_teacher(), _enable_backup(), _identity_service(), _login_with_backup(), _native_url(), TestClient, test_admin_cannot_disable_required_backup_authentication(), test_backup_maintenance_and_security_events_require_authentication() (+4 more)

### Community 57 - "Plan Accessibility Tests"
Cohesion: 0.12
Nodes (24): _area_complete(), content_completeness(), EditableContent, _group_activity_complete(), _morning_activity_complete(), _morning_talk_complete(), parse_content_for_editing(), Any (+16 more)

### Community 58 - "Shell Scripts"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 59 - "Prompt Schema Tests"
Cohesion: 0.21
Nodes (14): prompt_spec(), Any, validate_prompt_result(), validate_prompt_result_schema(), _contract(), Any, ModuleType, M6 AI 固定结果与输入最小化 RED 验收。 (+6 more)

### Community 60 - "App Health Tests"
Cohesion: 0.15
Nodes (25): create_app(), HealthDependencies, check(), dependencies(), MonkeyPatch, Path, test_database_failure_returns_stable_503_code(), test_default_calendar_check_degrades_when_library_is_unavailable() (+17 more)

### Community 61 - "Health Checks"
Cohesion: 0.24
Nodes (13): _ai_unconfigured(), authenticated_session(), build_health_dependencies(), _calendar_library_available(), _database_check(), _file_check(), _path_check(), IdentityServiceDependency (+5 more)

### Community 62 - "AI Client & SSRF"
Cohesion: 0.26
Nodes (12): _pinned_url(), Any, OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。, _addresses(), AiUrlPolicyError, Resolver, ValueError, AI 模型地址的保存时与连接前 SSRF 防护。 (+4 more)

### Community 63 - "AI Preview Lifecycle Tests"
Cohesion: 0.17
Nodes (23): create_completed_ai_preview(), TestClient, UUID, _native_url(), TestClient, UUID, _snapshot_count(), test_adopt_merges_preview_once_and_repeated_request_creates_no_second_snapshot() (+15 more)

### Community 64 - "AI Key Rotation Tests"
Cohesion: 0.35
Nodes (10): _candidate(), FakeStore, _modules(), Any, UUID, test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it(), test_rotation_dry_run_and_repeated_batch_are_zero_write(), test_rotation_uses_stable_cursor_and_does_not_change_call_revision() (+2 more)

### Community 65 - "Development Rules"
Cohesion: 0.15
Nodes (14): Child Manager Agent Development Rules, Data Model and Kindergarten Isolation, Fact Sources and Conflict Handling, GitHub Issue Execution Scope Fact Source, Kindergarten ID Isolation Field, One-Day Activity Plan Business Invariants, PRD/Specs Architecture Decision Records Fact Source, README Product Overview Fact Source (+6 more)

### Community 66 - "Job Status UI"
Cohesion: 0.17
Nodes (11): ai_job_status(), AiJobStatus, prompt_test_status(), PromptTestStatus, 异步提示词测试的稳定中文状态与无障碍语义。, should_poll(), build_ai_prompt_settings_section(), prompt_edit_version_id() (+3 more)

### Community 67 - "Web Entry"
Cohesion: 0.25
Nodes (11): main(), 仅绑定回环地址的 NiceGUI Web 入口。, _require_loopback(), _validate_cookie_security(), configure_logging(), EventDict, 递归清除 Web 日志中的凭证和内部 URL。, _redact() (+3 more)

### Community 68 - "Identity Helpers"
Cohesion: 0.16
Nodes (22): hash_password(), password_needs_rehash(), password_violations(), Path, verify_password(), _weak_passwords(), _native_url(), 通行密钥身份用例、一次性材料状态机与实时会话授权。 (+14 more)

### Community 69 - "Admin Initialization"
Cohesion: 0.14
Nodes (25): ArgumentParser, activate_initialization(), migrate_passkeys(), _native_url(), datetime, UUID, 首位管理员的部署控制台初始化与双人核验激活。, 仅在通行密钥已登记并完成两位预登记人员核验后激活。 (+17 more)

### Community 70 - "Ports & Protocols"
Cohesion: 0.21
Nodes (9): AiClient, Clock, DependencyCheck, JobBroker, datetime, Protocol, UUID, M1 外部边界所需的最小 Protocol。 (+1 more)

### Community 71 - "Domain Documentation"
Cohesion: 0.18
Nodes (14): 安全模型档案与提示词生命周期, AI 输入、提示词、模型与 Schema 冻结上下文, 不可变脱敏审计与外部故障隔离, GitHub Issue #10, M6 T087–T126 in_progress，T103 为下一项, Batch 父任务不执行且状态由四个子任务派生, 数据库提交后 Redis 故障仍保持 202 pending_dispatch, AI 外呼前实时重验账号、角色、班级、教案与模型 (+6 more)

### Community 72 - "AI Generation Service Tests"
Cohesion: 0.48
Nodes (10): _native_url(), TestClient, UUID, RecordingDispatcher, _replace_areas(), _session(), test_batch_creates_non_executable_parent_and_exactly_four_dispatched_children(), test_batch_missing_indoor_area_only_fails_indoor_child_and_single_is_rejected() (+2 more)

### Community 73 - "Invitation Tests"
Cohesion: 0.33
Nodes (13): _base64url(), _create_teacher(), _issue(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes(), test_invitation_is_single_use_reissuable_and_revocable() (+5 more)

### Community 74 - "OpenAPI Contract Tests"
Cohesion: 0.40
Nodes (13): _assert_operation_contract(), _canonical_schema(), _effective_security(), _operations(), _parameter_shape(), Any, 运行时 OpenAPI 与冻结身份契约的一致性门禁。, _request_schema() (+5 more)

### Community 75 - "Common Schemas"
Cohesion: 0.21
Nodes (10): AiGroupActivityStep, GroupActivityStepCandidate, LessonPlanReference, 按任务冻结的过程长度校验索引；越界必须进入结构错误重试。, _require_nonblank(), _require_question(), _require_statement(), _validate_group_add_step_index() (+2 more)

### Community 76 - "Prompt Test API Tests"
Cohesion: 0.30
Nodes (18): ai_model_service(), FailingDispatcher, prompt_job_client(), _provision_model_and_version(), Any, TestClient, _resolver(), test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure() (+10 more)

### Community 77 - "Quality Gates"
Cohesion: 0.15
Nodes (13): 执行授权边界, 可收集且无错误的 RED 门禁, contracts/, data-model.md, graphify-out/graph.json, 常规测试禁止真实 AI、节假日及其他外网调用, 阶段依赖与执行顺序, plan.md (+5 more)

### Community 78 - "Token Management"
Cohesion: 0.36
Nodes (12): _base64url(), _insert_credential(), _native_url(), MonkeyPatch, TestClient, UUID, _registration_credential(), test_admin_cannot_revoke_last_active_admin_last_credential() (+4 more)

### Community 79 - "Settings Migration Tests"
Cohesion: 0.25
Nodes (7): MonkeyPatch, settings_database(), test_age_group_seed_is_fixed_and_idempotent(), test_area_constraints_allow_empty_collections_but_reject_duplicate_names(), test_postgresql_enforces_semester_and_lead_teacher_uniqueness(), test_settings_migration_creates_the_five_tenant_scoped_tables(), test_settings_relations_use_composite_tenant_foreign_keys()

### Community 80 - "Prompt Settings Smoke Tests"
Cohesion: 0.19
Nodes (7): _job_status_module(), Any, MonkeyPatch, test_controls_have_keyboard_focus_and_error_label_associations(), test_job_status_recovers_configuration_change_with_chinese_action(), test_job_status_refreshes_until_terminal_and_restores_after_page_reload(), test_settings_controls_call_model_prompt_and_job_public_api_seams()

### Community 81 - "Auth Contract Tests"
Cohesion: 0.21
Nodes (7): APIRoute, Any, _resolve(), _runtime_routes(), test_auth_success_and_logout_lock_two_raw_cookie_headers(), test_runtime_auth_router_matches_frozen_passkey_paths(), test_runtime_auth_success_statuses_match_frozen_contract()

### Community 82 - "Prompt Repository Tests"
Cohesion: 0.30
Nodes (9): _modules(), Any, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_call_configuration_change_set_matches_the_frozen_revision_rules(), test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup(), test_model_reads_and_writes_are_tenant_scoped(), test_prompt_run_frozen_fields_cannot_be_updated() (+1 more)

### Community 83 - "Recovery Tests"
Cohesion: 0.15
Nodes (28): _digest(), issue_secret(), IssuedSecret, StrEnum, 生成 256 位一次性秘密，持久化对象中只保留 purpose 绑定摘要。, 以常量时间比较 purpose 绑定摘要。, SecretPurpose, SecretRecord (+20 more)

### Community 84 - "System Documentation"
Cohesion: 0.24
Nodes (11): AI Generation Behavior Rules, AI Prompt Management System, Daily Lesson Plan System, Word Document Export, Issue #11 - M6 AI Async Generation, M4 AI Model & Prompt Basics, M5 Manual Lesson Plan Closure, M6 AI Async Generation (+3 more)

### Community 85 - "OpenAPI Configuration"
Cohesion: 0.29
Nodes (9): _apply_operation_contract(), configure_openapi(), _no_content_response(), _operation(), Any, FastAPI, M2 运行时 OpenAPI 的集中契约装配。, 返回缓存后的 M2 运行时 OpenAPI 生成器。 (+1 more)

### Community 86 - "Development Handoff"
Cohesion: 0.29
Nodes (11): Dev Handoff 2026-07-24, 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。, Milestone M2: Core Authentication & Permissions, Milestone M3: Settings, Milestone M3A: Password + TOTP Backup Login, Tasks T001–T002: Issue #8 & Docs Baseline, Tasks T003–T009: RED Gate for M3A, Tasks T010–T015: M3A Backup Auth Foundation (+3 more)

### Community 87 - "AI Model Profile Tests"
Cohesion: 0.36
Nodes (8): PromptTemplateError, Any, ValueError, 仅支持固定白名单纯替换词法的提示词渲染器。, render_prompt(), _render_value(), validate_prompt_template(), _variables()

### Community 88 - "Identity Isolation Tests"
Cohesion: 0.22
Nodes (20): Event, lesson_plan_database(), MonkeyPatch, test_0006_creates_tenant_scoped_plan_snapshot_author_and_cache_tables(), test_database_contains_unique_cas_week_and_unavailable_constraints(), identity_database(), _insert_kindergarten(), _insert_user() (+12 more)

### Community 89 - "Backup Auth Contract Tests"
Cohesion: 0.24
Nodes (7): Any, _resolve(), _runtime_routes(), test_backup_contract_marks_request_and_one_time_response_secrets(), test_runtime_router_exposes_the_user_story_2_endpoints(), test_runtime_router_matches_the_frozen_backup_contract(), test_runtime_user_story_2_openapi_matches_frozen_security_and_responses()

### Community 90 - "AI Client Tests"
Cohesion: 0.44
Nodes (10): _modules(), Any, _resolver(), test_client_caps_retry_after_at_sixty_seconds(), test_client_errors_are_stable_and_never_include_key_or_prompt(), test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin(), test_client_posts_openai_compatible_request_with_fixed_limits(), test_client_rejects_redirects_without_following_them() (+2 more)

### Community 91 - "Plan AI Contract Tests"
Cohesion: 0.26
Nodes (12): _children(), _contract(), Any, ModuleType, M6 教案 AI 公共契约的 RED 验收。, test_ai_child_succeeded_is_not_a_valid_batch_completion_state(), test_batch_job_projects_zero_attempts_and_rejects_execution_shape(), test_batch_status_is_derived_only_from_exactly_four_children() (+4 more)

### Community 92 - "Request Middleware"
Cohesion: 0.22
Nodes (7): API 请求 ID 与追踪 ID 中间件。, _request_id(), RequestContextMiddleware, ASGIApp, Receive, Scope, Send

### Community 93 - "BFF Proxy"
Cohesion: 0.33
Nodes (8): proxy_request(), AsyncBaseTransport, 按固定 allowlist 转发请求，并保留响应原始多值头。, MonkeyPatch, test_proxy_ignores_process_proxy_environment(), test_proxy_preserves_auth_set_cookie_as_raw_headers(), test_proxy_preserves_request_and_rebuilds_client_ip(), test_proxy_strips_hop_by_hop_and_spoofed_source_headers()

### Community 94 - "Session Management"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 95 - "Client IP Resolution"
Cohesion: 0.33
Nodes (8): Collection, parse_trusted_bff_peers(), 只接受显式配置的回环 BFF socket peer。, resolve_client_ip(), test_configured_loopback_bff_peer_can_supply_internal_client_ip(), test_non_loopback_peer_cannot_be_configured_as_trusted_bff(), test_trusted_bff_peers_are_empty_until_explicitly_configured(), test_untrusted_peer_cannot_supply_internal_client_ip()

### Community 96 - "Scheduler & Recovery"
Cohesion: 0.20
Nodes (13): Any, 向已注册 actor 投递唯一的 job_id。, RedisJobDispatcher, AiRecoveryStore, AiResultMaintenanceCounts, AiResultMaintenanceRepository, datetime, Protocol (+5 more)

### Community 97 - "Workday Cache Repository"
Cohesion: 0.25
Nodes (7): m4_database(), MonkeyPatch, test_0007_creates_all_tenant_scoped_ai_prompt_and_job_tables(), test_background_job_batch_and_execution_attempt_constraints_are_frozen(), test_migration_seeds_exactly_seven_system_versions_per_existing_kindergarten(), test_model_activation_and_job_terminal_invariants_are_database_enforced(), test_model_revision_and_prompt_run_frozen_context_are_database_enforced()

### Community 98 - "Prompt Test Dispatch"
Cohesion: 0.08
Nodes (30): append_ai_event(), Any, UUID, UUID, UUID, Broker, UUID, 仅投递 job_id 的提示词测试分发边界。 (+22 more)

### Community 99 - "Auth Logic"
Cohesion: 0.44
Nodes (6): datetime, _session(), test_backup_reauthentication_only_authorizes_add_passkey_for_five_minutes(), test_expired_backup_reauthentication_cannot_add_passkey(), test_recent_webauthn_proof_satisfies_high_risk_identity_boundary(), test_restricted_enrollment_session_cannot_enter_business_routes()

### Community 100 - "Workday Service Tests"
Cohesion: 0.29
Nodes (6): _module(), MonkeyPatch, test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls(), test_local_result_wins_conflict_and_uses_one_hour_cache(), test_timor_client_enforces_one_total_deadline(), test_unsupported_local_calendar_range_softly_falls_back_to_online()

### Community 101 - "Development Branch Labels"
Cohesion: 0.33
Nodes (9): dev - Implementation Branch, docs - Design & Spec Baseline, main - Stable Release Baseline, CONTEXT.md - Project Status, Old Repository - kindergartenManager, README.md - Product Overview, Implementation Plan - Daily Activity Plan, Quickstart - Acceptance Contract (+1 more)

### Community 102 - "Security Defense Concepts"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 103 - "Task Specification Tracking"
Cohesion: 0.25
Nodes (9): specs/002-password-totp-backup-login/tasks.md, M8 性能、安全、无障碍与交付验收, 唯一教案、保存、历史、归档与恢复, Polish 与 M8 完整验收, M9 生产部署复审排除在任务范围外, Roadmap M1–M8 范围, US1 M3A 密码与 TOTP 备用登录, US2 纯手工教案闭环 (+1 more)

### Community 104 - "Secret Encryption Tests"
Cohesion: 0.39
Nodes (8): _context(), _encryption_module(), Any, Path, test_development_key_provider_requires_owner_only_file_outside_repository(), test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution(), test_totp_secret_envelope_round_trips_with_random_96_bit_nonce(), test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce()

### Community 105 - "Feature Milestones Overview"
Cohesion: 0.25
Nodes (8): Settings System - Kindergarten/Semester/Class, Password + TOTP Backup Login, WebAuthn Passkey Authentication, M0 Shared Design Baseline, M1 Engineering Skeleton, M2 Authentication & Authorization, M3 Essential Settings, M3A Password & TOTP Backup Login

### Community 106 - "AI Prompts Jobs Migration"
Cohesion: 0.36
Nodes (6): Any, Column, 建立 AI 模型、提示词与 PostgreSQL 权威任务基础。, _seed_defaults(), _timestamps(), upgrade()

### Community 107 - "Content Schemas"
Cohesion: 0.57
Nodes (7): _complete_content(), _native_url(), TestClient, _service(), _session(), test_incomplete_reflection_acceptance_rolls_back_and_key_remains_available(), test_reflection_acceptance_saves_once_without_snapshot_and_replays()

### Community 108 - "Password TOTP Migration Tests"
Cohesion: 0.46
Nodes (7): Script, _backup_revision(), MonkeyPatch, test_backup_auth_migration_creates_isolated_credentials_and_enrollments(), test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(), test_backup_auth_revision_follows_settings_and_precedes_lesson_plans(), test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade()

### Community 109 - "Feature Spec User Stories"
Cohesion: 0.25
Nodes (8): Feature Specification: 首期一日活动计划完整闭环, User Story 1: Admin Setup, User Story 2: Manual Lesson Plan Loop, User Story 3: Admin Configure Model and Prompts, User Story 4: Teacher Uses AI by Section, User Story 5: Teacher Processes Group Activity Source, User Story 6: Teacher Export and Download Fixed Word, User Story 7: Admin Audit and Degradable Service

### Community 110 - "Canonical Fingerprint"
Cohesion: 0.50
Nodes (4): MonkeyPatch, TestClient, test_autosave_creates_no_snapshot_and_stale_version_never_overwrites(), test_manual_save_rolls_back_content_version_snapshot_and_audit_together()

### Community 111 - "OpenAPI Document Tests"
Cohesion: 0.39
Nodes (7): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_document_is_valid_31(), test_openapi_keeps_nicegui_as_the_only_browser_entry(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 113 - "Content V1 Validation Tests"
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

### Community 117 - "Technology Stack Baseline"
Cohesion: 0.29
Nodes (7): Alembic Database Migrations, PostgreSQL Production Database, pyproject.toml Dependency Management, Python 3.14+ Minimum Version, SQLAlchemy 2.x ORM, Technology and Dependency Baseline, uv.lock Version Locking

### Community 118 - "Password to Passkey Tests"
Cohesion: 0.54
Nodes (7): _assert_passkey_revisions_exist(), _native_url(), MonkeyPatch, test_contract_removes_password_data_and_downgrade_recreates_only_empty_columns(), test_expand_moves_existing_accounts_to_enrollment_and_revokes_old_sessions(), test_passkey_migration_has_explicit_expand_and_contract_boundaries(), _user_columns()

### Community 119 - "Backup Auth Smoke Tests"
Cohesion: 0.33
Nodes (5): security_event_text(), MonkeyPatch, test_backup_login_and_reauthentication_submit_secrets_only_in_post_bodies(), test_security_event_messages_cover_the_frozen_event_codes(), test_security_events_use_read_only_same_origin_api()

### Community 120 - "Passkey Expand Migration"
Cohesion: 0.52
Nodes (5): Any, Column, _tenant_identity_columns(), _timestamps(), upgrade()

### Community 121 - "Project Architecture Principles"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 122 - "Service Units Specifications"
Cohesion: 0.38
Nodes (7): FastAPI API 独立运行单元, 方法、路由、实际 path/query/body 的规范幂等指纹, Foundational T009–T020, docs/development/local-development-environments.md, Setup T001–T008, NiceGUI Web 独立运行单元, 后台 Worker 独立运行单元

### Community 123 - "Prompt Renderer Tests"
Cohesion: 0.48
Nodes (6): _module(), Any, test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(), test_renderer_fails_for_missing_variable_before_external_call(), test_renderer_rejects_every_non_frozen_placeholder_form(), test_renderer_uses_stable_json_and_never_recursively_renders_values()

### Community 124 - "Lesson Plans Migration"
Cohesion: 0.20
Nodes (5): Alembic, Any, Column, _timestamps(), upgrade()

### Community 125 - "Identity Audit Migration"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 126 - "Database Migrations"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 127 - "Password TOTP Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 128 - "Save Status Tracking"
Cohesion: 0.16
Nodes (14): plan_api_request(), 只通过同源 BFF 访问教案及其任务端点。, AiSectionAction, preview_title(), 教案 AI 预览的稳定栏目、动作与展示数据。, poll_interval_ms(), save_status(), SaveStatus (+6 more)

### Community 129 - "AI Generation Results Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 130 - "Word Export Template Handling"
Cohesion: 0.40
Nodes (6): 固定 Word 模板原件哈希与样式完整性, templates/teacherplan/teacherplan.docx, 集体活动拆分后再新增环节的两阶段流程, US5 集体活动原始教案处理, US6 固定 Word 导出与重新下载, 固定模板 Word 导出、历史与重新授权下载

### Community 132 - "TOTP Algorithm Tests"
Cohesion: 0.53
Nodes (5): Any, test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps(), test_totp_rejects_the_same_or_earlier_counter_after_success(), test_totp_secret_is_unique_high_entropy_base32(), _totp_module()

### Community 133 - "Service Boundary Definitions"
Cohesion: 0.60
Nodes (5): Background Worker Role, FastAPI API Service Role, NiceGUI Web Service Role, Service Boundaries and Dependency Direction, Shared Contracts Package

### Community 134 - "Deployment Infrastructure"
Cohesion: 0.50
Nodes (5): FastAPI API Service, NiceGUI Web Service, PostgreSQL Database, Redis Message Broker, Dramatiq Background Worker

### Community 135 - "Development Workflow Roles"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 136 - "Job Dispatcher"
Cohesion: 0.16
Nodes (8): ai_retry_service(), AiRetryService, _native_url(), Dispatcher, dispatch_after_commit(), Dispatcher, Protocol, 尽力投递已提交任务；单个 Redis 故障不得回滚或阻断其余子任务。

### Community 138 - "Kindergarten Auth Setup"
Cohesion: 0.50
Nodes (5): 园所、学期、班级、教师关系与区域设置, kindergarten_id 园所隔离, US1 M2 认证、授权与身份审计, US1 M3 首期必要设置, WebAuthn 身份安全与会话撤销

### Community 139 - "AI Key Rotation CLI Tests"
Cohesion: 0.60
Nodes (4): CompletedProcess, _run(), test_bootstrap_cli_exposes_rotation_without_master_key_arguments(), test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets()

### Community 141 - "Calendar Tests"
Cohesion: 0.70
Nodes (4): _calendar(), test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic(), test_out_of_semester_week_number_and_text_are_both_empty(), test_semester_start_week_is_week_one_and_increments_each_monday()

### Community 142 - "Branch Workflow Roles"
Cohesion: 0.50
Nodes (4): Dev Branch Role, Development Workflow and Git Rules, Docs Branch Role, Main Branch Role

### Community 144 - "Identity Migration Tests"
Cohesion: 0.50
Nodes (4): migrated_database(), MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds(), test_identity_migration_is_idempotent()

### Community 145 - "Core Entity Tables"
Cohesion: 0.50
Nodes (4): Age Groups Table, Class Teachers Table, Classes Table, Daily Activity Plans Table

### Community 146 - "Database Schema Concepts"
Cohesion: 0.50
Nodes (4): Composite Foreign Keys Concept, Kindergarten Isolation Concept, Kindergartens Table, Users Table

### Community 148 - "Backup Login Feature"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 150 - "Lesson Plan Contract Tests"
Cohesion: 0.83
Nodes (3): _contracts(), test_open_and_write_contracts_do_not_accept_tenant_or_ownership_mutation(), test_plan_snapshot_and_page_contracts_are_bounded_and_stable()

### Community 155 - "Development Tools Usage"
Cohesion: 1.00
Nodes (3): Codebase-Memory MCP Usage, Codegraph Usage, Graphify Knowledge Graph Usage

### Community 156 - "CSRF Protection Tests"
Cohesion: 0.60
Nodes (4): TestClient, test_csrf_cookie_is_signed_readable_and_not_httponly(), test_passkey_state_change_rejects_missing_csrf_and_wrong_origin(), test_recovery_rejects_malformed_signed_double_submit_token()

### Community 157 - "Migration Dependency Order"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

### Community 158 - "JSON Schema Utilities"
Cohesion: 1.00
Nodes (3): JsonSchemaValue, _render_prompt_test_run_schema(), _render_union_as_one_of()

### Community 161 - "Lesson Plan UI Components"
Cohesion: 0.67
Nodes (3): AI-Added Step Red Text, Structured Daily Activity Sections, Daily Activity Plan Word Layout

## Knowledge Gaps
- **186 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+181 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **87 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `班级与教师配置` (2× useful, score=1.352895454)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IdentityError` connect `Identity & Audit` to `Settings Routers`, `Auth Endpoints`, `Job Recovery`, `Job Dispatcher`, `Auth & CSRF`, `AI Generation Service`, `AI Job Actors`, `WebAuthn Challenges`, `AI Batch Tests`, `User Management`, `Settings Repository`, `Calendar Client`, `Lesson Plan Repository`, `Prompt Repository`, `TOTP Encryption`, `Auth Sessions`, `FastAPI Application`, `Jobs API`, `Backup Maintenance Tests`, `App Health Tests`, `Health Checks`, `Identity Helpers`, `AI Generation Service Tests`, `Recovery Tests`, `Prompt Test Dispatch`, `Auth Logic`, `Content Schemas`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `SessionUser` connect `Identity & Audit` to `Settings Routers`, `Auth Endpoints`, `Job Recovery`, `Job Dispatcher`, `Auth & CSRF`, `AI Generation Service`, `AI Key Rotation`, `WebAuthn Challenges`, `AI Batch Tests`, `Settings Repository`, `Calendar Client`, `Lesson Plan Repository`, `Prompt Repository`, `TOTP Encryption`, `Jobs API`, `App Health Tests`, `Health Checks`, `Identity Helpers`, `AI Generation Service Tests`, `Recovery Tests`, `Prompt Test Dispatch`, `Auth Logic`, `Content Schemas`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `ActorFixture` connect `Backup Enrollment Tests` to `Identity & Audit`, `Audit Events`, `AI Generation Service Tests`, `Invitation Tests`, `TOTP Encryption`, `Content Schemas`, `Prompt Test API Tests`, `Token Management`, `Canonical Fingerprint`, `WebAuthn Tests`, `AI Key Rotation`, `Test Helpers`, `Recovery Tests`, `AI Batch Tests`, `Backup Maintenance Tests`, `AI Generation Tests`, `AI Preview Lifecycle Tests`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `ActorFixture` (e.g. with `StaticIdentitySecretKeyProvider` and `IdentityService`) actually correct?**
  _`ActorFixture` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `IdentityError` (e.g. with `create_app()` and `HealthDependencies`) actually correct?**
  _`IdentityError` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `SessionUser` (e.g. with `HealthDependencies` and `AuditRepository`) actually correct?**
  _`SessionUser` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 137 inferred relationships involving `ContractModel` (e.g. with `AiGenerationAuditMetadata` and `AuditEventReference`) actually correct?**
  _`ContractModel` has 137 INFERRED edges - model-reasoned connections that need verification._