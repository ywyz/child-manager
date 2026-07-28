# Graph Report - .  (2026-07-28)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2953 nodes · 8309 edges · 256 communities (161 shown, 95 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 711 edges (avg confidence: 0.54)
- Token cost: 11,036 input · 9,203 output

## Graph Freshness
- Built from commit: `b0f2f862`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Prompt Test Jobs
- Backup Credential Repository
- Settings Repository
- AI Generation Dispatcher
- AI Key Rotation
- Settings Management
- Admin Initialization
- Identity Migration Tests
- Prompt Renderer
- AI Generation Results
- Auth Endpoints
- Identity Service
- Database Models
- Authentication Flow
- Auth Throttling
- Admin Test Helpers
- WebAuthn Tests
- BFF API Client
- Security Configuration
- Plan Routes
- Challenge Management
- TOTP Secret Encryption
- User Management
- Architecture Boundaries
- Worker Prompt Tests
- Speckit Analysis
- Calendar Client
- Project Documentation
- Password Hashing
- Lesson Plan Repository
- Development Roadmap
- Lesson Plan Service
- Transactional Semantics
- Login Throttle
- Prompt Test Store
- AI Client Transport
- Local Dev Environment
- Identity Enums
- Backup Enrollment Tests
- Worker Broker
- Auth Smoke Tests
- Job Service
- AI Generation Presave
- Prompt Test Job API
- Audit Service
- Local Dev Profile Tests
- Navigation
- AI Results Repository
- Common Schemas
- Backup Maintenance Tests
- Recovery Actors
- Plan Content Tests
- Shell Scripts
- Health Checks
- AI Client SSRF
- AI Batch Generation Tests
- CSRF Tests
- AI Preview Lifecycle
- AI Key Rotation Tests
- Job Status UI
- Web Entry
- Port Interfaces
- AI Preview Adoption
- Invitation Tests
- OpenAPI Contract Tests
- FastAPI App
- Settings Permissions
- Health Dependencies
- Credential Tests
- Plan AI Contracts
- AI Prompt Settings Tests
- Auth Contract Tests
- Project Context
- Calendar Cache
- AI Prompt Repository Tests
- OpenAPI Config
- Authorization Assurance
- TOTP Primitives
- Backup Auth Contract
- AI Client Tests
- Request Middleware
- BFF Proxy
- Database Sessions
- Client IP Resolution
- Workday Service Tests
- Security Defense
- Identifier Normalization
- Secret Encryption Tests
- AI Prompts Migration
- Backup Login Migration
- Task Tracking
- AI Prompt Contracts
- OpenAPI Document Tests
- Content V1 Tests
- AI Key Envelope Tests
- AI URL Policy Tests
- Prompt Catalog Tests
- Job Query Service
- Backup Auth Smoke
- Passkey Migration
- Project Constitution
- Prompt Renderer Tests
- CSRF Token Management
- Identity & Audit Migration
- Settings Migration
- Password TOTP Migration
- Lesson Plans Migration
- AI Results Migration
- User Contract Tests
- TOTP Tests
- Development Workflow Docs
- Feature Branch Script
- AI Key Rotation Tests
- Calendar Tests
- Dev Agent Tools
- Save Status Module
- Kindergarten Core Tables
- Database Isolation Concepts
- Snapshot Hash Utilities
- Backup Login Feature
- Lesson Plan Contract Tests
- Calendar Fake Fixture
- Fixed Clock Fixture
- Redis Fake Fixture
- Migration Dependency Order
- Lease Expiry Logic
- AI Step UI Layout
- AI Client Fake
- Child Manager Module
- Worker Module
- AI Jobs Tables
- AI Model Tables
- Prompt Tables
- Roles Tables
- Database Base Module
- Weak Passwords List
- Backend Module
- Contracts Module
- Prerequisites Check Script
- Setup Plan Script
- Setup Tasks Script
- Web Tests Module
- AI Prompt Rules
- Git Branch Rules
- Data Isolation Rules
- Conflict Resolution Rules
- Security Privacy Rules
- Service Dependency Rules
- Testing Requirements
- Account Invitations Table
- Account Recovery Requests
- Age Groups Table
- AI Results Table
- AI Profile Capabilities
- AI Model Profiles Table
- Audit Events Table
- Background Jobs Table
- Backup Auth Credentials
- Backup Auth Enrollments
- Bootstrap Init Table
- Class Areas Table
- Class Teachers Table
- Classes Table
- Plan Exports Table
- Plan Snapshots Table
- Daily Activity Plans
- Identity Verification Table
- Snapshot Immutability Rule
- JSONB Schema Versioning
- Kindergarten Isolation
- Kindergartens Table
- Lesson Plan Sources
- Prompt Definitions Table
- Prompt Test Runs Table
- Prompt Versions Table
- Recovery Codes Table
- Refresh Tokens Table
- Roles Table
- Semesters Table
- User Roles Table
- Users Table
- WebAuthn Challenges
- WebAuthn Credentials
- Workday Cache Table
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
- Application Owned Transactions
- External Key Source
- Broker
- Protocol
- Child Manager
- Dev Workflow & Quality
- Governance
- Technical Security Constraints
- Activity Plan Quality Checklist
- Password TOTP Backup Login
- Test Client

## God Nodes (most connected - your core abstractions)
1. `ActorFixture` - 167 edges
2. `csrf_headers()` - 154 edges
3. `ContractModel` - 148 edges
4. `IdentityError` - 131 edges
5. `IdentityRepository` - 129 edges
6. `SessionUser` - 127 edges
7. `IdentityService` - 103 edges
8. `AuditRepository` - 73 edges
9. `require_csrf()` - 64 edges
10. `provision_editable_plan_context()` - 55 edges

## Surprising Connections (you probably didn't know these)
- `一日活动计划需求面` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_020708_请根据现有文档_和旧仓库的文件思考如何撰写_docs_prd_lesson_management_m.md → docs/faq/combined-audit.md
- `ADR 直接文件核对` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_025449_哪些关键架构决策需要独立_adr_哪些已经确认_决策之间有什么依赖.md → docs/faq/combined-audit.md
- `校正后的数据模型边界` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md → docs/faq/combined-audit.md
- `test_identity_audit_repository_is_append_only()` --indirect_call--> `AuditRepository`  [INFERRED]
  tests/unit/identity/test_audit.py → packages/backend/audit/repository.py
- `test_repository_exposes_atomic_passkey_lifecycle_operations()` --indirect_call--> `IdentityRepository`  [INFERRED]
  tests/repository/test_identity_isolation.py → packages/backend/identity/repository.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **All Task Groups in M3A Milestone** — milestone_m3a, task_group_t001_t002, task_group_t003_t009, task_group_t010_t015, task_group_t016_t019, task_group_t020_t029, task_group_t030_t034 [EXTRACTED 1.00]
- **Tables Implementing Kindergarten Isolation** — docs_design_database_schema_users, docs_design_database_schema_webauthn_credentials, docs_design_database_schema_webauthn_challenges, docs_design_database_schema_backup_auth_credentials, docs_design_database_schema_backup_auth_enrollments, docs_design_database_schema_bootstrap_initializations, docs_design_database_schema_account_invitations, docs_design_database_schema_recovery_codes, docs_design_database_schema_account_recovery_requests, docs_design_database_schema_identity_verification_approvals, docs_design_database_schema_user_roles, docs_design_database_schema_refresh_tokens, docs_design_database_schema_age_groups, docs_design_database_schema_classes, docs_design_database_schema_class_teachers, docs_design_database_schema_semesters, docs_design_database_schema_class_areas, docs_design_database_schema_ai_model_profiles, docs_design_database_schema_ai_model_profile_capabilities, docs_design_database_schema_prompt_definitions, docs_design_database_schema_prompt_versions, docs_design_database_schema_prompt_test_runs, docs_design_database_schema_daily_activity_plans, docs_design_database_schema_daily_activity_plan_authors, docs_design_database_schema_daily_activity_plan_snapshots, docs_design_database_schema_lesson_plan_sources, docs_design_database_schema_background_jobs, docs_design_database_schema_ai_generation_results, docs_design_database_schema_daily_activity_plan_exports, docs_design_database_schema_workday_cache, docs_design_database_schema_audit_events [EXTRACTED 1.00]
- **Tables Involved in Authentication Flow** — docs_design_database_schema_users, docs_design_database_schema_webauthn_credentials, docs_design_database_schema_webauthn_challenges, docs_design_database_schema_backup_auth_credentials, docs_design_database_schema_backup_auth_enrollments, docs_design_database_schema_refresh_tokens [INFERRED 0.80]
- **Lesson Planning System Tables** — docs_design_database_schema_daily_activity_plans, docs_design_database_schema_daily_activity_plan_authors, docs_design_database_schema_daily_activity_plan_snapshots, docs_design_database_schema_lesson_plan_sources [INFERRED 0.80]
- **Identity and Authentication System** — docs_design_data_model_kindergartens, docs_design_data_model_users, docs_design_data_model_webauthn_credentials, docs_design_data_model_webauthn_challenges, docs_design_data_model_backup_auth_credentials, docs_design_data_model_backup_auth_enrollments, docs_design_data_model_bootstrap_initializations, docs_design_data_model_account_invitations, docs_design_data_model_recovery_codes, docs_design_data_model_account_recovery_requests, docs_design_data_model_identity_verification_approvals, docs_design_data_model_roles, docs_design_data_model_user_roles, docs_design_data_model_refresh_tokens, docs_design_data_model_audit_events, docs_design_data_model_kindergarten_isolation, docs_design_data_model_immutability [EXTRACTED 1.00]
- **Core Principles of Constitution** — specify_memory_constitution_principle_1, specify_memory_constitution_principle_2, specify_memory_constitution_principle_3, specify_memory_constitution_principle_4, specify_memory_constitution_principle_5, specify_memory_constitution_principle_6 [EXTRACTED 1.00]
- **Governance Framework** — specify_memory_constitution_constitution, specify_memory_constitution_technical_constraints, specify_memory_constitution_development_workflow, specify_memory_constitution_governance [EXTRACTED 1.00]
- **项目治理与规则文档** — agents_agents, specify_memory_constitution_constitution [INFERRED 0.90]
- **认证与安全机制** — agents_security [EXTRACTED 1.00]
- **知识与代码分析工具** — agents_graphify, agents_codebase_mcp, agents_tools [INFERRED 0.85]
- **Feature 001: Daily Activity Plan** — specs_001_daily_activity_plan_plan, specs_001_daily_activity_plan_spec, docs_roadmap, milestone_m6, user_story_us4, user_story_us5, user_story_us6, user_story_us7 [INFERRED 0.90]
- **Core Project Components** — context_ai, context_word, context_postgresql, context_redis, context_webauthn [INFERRED 0.80]
- **Speckit Full SDD Lifecycle** — _agents_skills_speckit_specify_skill_speckit_specify, _agents_skills_speckit_plan_skill_speckit_plan, _agents_skills_speckit_tasks_skill_speckit_tasks, _agents_skills_speckit_implement_skill_speckit_implement [EXTRACTED 1.00]
- **Web API Worker Boundary Alignment** — docs_adr_adr_0002_separate_web_api_worker_modular_monolith_modular_monolith, docs_adr_adr_0002_separate_web_api_worker_modular_monolith_service_boundaries, docs_design_system_architecture_modular_runtime_architecture, docs_design_system_architecture_trust_starts_at_api [INFERRED 0.95]
- **本地开发隔离模式** — docs_development_local_development_environments_worktree_resource_isolation, docs_development_local_development_environments_loopback_only_dependencies, docs_development_local_development_environments_production_topology_deferral [EXTRACTED 1.00]
- **M0 收敛证据链** — docs_faq_combined_audit_m0_gate_framework, docs______20260713________m0_gate_closure_evidence, docs______20260713____________final_docs_baseline [INFERRED 0.85]
- **身份纵深防御** — docs_security_threat_model_restricted_public_entry, docs_security_threat_model_phishing_resistant_authentication, docs_security_threat_model_password_totp_backup, docs_security_threat_model_emergency_recovery_dual_control [EXTRACTED 1.00]

## Communities (256 total, 95 thin omitted)

### Community 0 - "Prompt Test Jobs"
Cohesion: 0.05
Nodes (121): alias, get_job(), AdminSessionDependency, UUID, clear_prompt_tests(), create_prompt_test(), _definition(), get_prompt() (+113 more)

### Community 1 - "Backup Credential Repository"
Cohesion: 0.05
Nodes (30): _backup_credential(), _backup_enrollment(), BackupCredentialRecord, BackupEnrollmentRecord, BackupRevocationResult, BackupSecurityEventRecord, ChallengeRecord, _credential() (+22 more)

### Community 2 - "Settings Repository"
Cohesion: 0.07
Nodes (47): settings_service(), IntegrityError, NoReturn, AgeGroupRecord, AreaInput, AreaRecord, ClassRecord, KindergartenRecord (+39 more)

### Community 3 - "AI Generation Dispatcher"
Cohesion: 0.06
Nodes (55): ActorFixture, AiBatchRequest, AiGenerationRequest, AiGenerationResultRecord, AiGenerationResultRepository, AiTaskCode, Broker, Connection (+47 more)

### Community 4 - "AI Key Rotation"
Cohesion: 0.08
Nodes (38): AiKeyProvider, ai_model_service(), UUID, run_rotation(), _aad(), AiKeyEnvelope, decrypt_api_key(), decrypt_api_key_with_provider() (+30 more)

### Community 5 - "Settings Management"
Cohesion: 0.08
Nodes (65): AgeGroup, AiModelProfile, AiModelServiceDependency, _age_group(), _ai_model(), _area(), _class(), create_ai_model_profile() (+57 more)

### Community 6 - "Admin Initialization"
Cohesion: 0.07
Nodes (58): ArgumentParser, activate_initialization(), migrate_passkeys(), _native_url(), datetime, UUID, 首位管理员的部署控制台初始化与双人核验激活。, 仅在通行密钥已登记并完成两位预登记人员核验后激活。 (+50 more)

### Community 7 - "Identity Migration Tests"
Cohesion: 0.06
Nodes (49): Event, StaticIdentitySecretKeyProvider, migrated_database(), MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds(), test_identity_migration_is_idempotent(), MonkeyPatch, settings_database() (+41 more)

### Community 8 - "Prompt Renderer"
Cohesion: 0.11
Nodes (23): prompt_service(), PromptTemplateError, Any, ValueError, 仅支持固定白名单纯替换词法的提示词渲染器。, render_prompt(), _render_value(), validate_prompt_template() (+15 more)

### Community 9 - "AI Generation Results"
Cohesion: 0.10
Nodes (45): JobMessage, Redis 中唯一允许传递的最小任务消息。, SimpleNamespace, _insert_job(), _insert_other_tenant_plan(), _insert_result(), _native_url(), _provision_dependencies() (+37 more)

### Community 10 - "Auth Endpoints"
Cohesion: 0.08
Nodes (54): _allowed_origins(), _loopback_aliases(), 同源 Cookie、WebAuthn、邀请、恢复与会话端点。, ContractModel, BaseModel, ExportReference, AdminCredentialRevocationResult, AuthenticationCredential (+46 more)

### Community 11 - "Identity Service"
Cohesion: 0.18
Nodes (7): AuditRepository, InvitationRecord, IdentityService, ManagedUser, UUID, SessionUser, BackupAuthenticationStatus

### Community 12 - "Database Models"
Cohesion: 0.10
Nodes (40): DeclarativeBase, AuditEvent, Base, AccountInvitation, AccountRecoveryRequest, BackupAuthCredential, BackupAuthEnrollment, BootstrapInitialization (+32 more)

### Community 13 - "Authentication Flow"
Cohesion: 0.18
Nodes (49): authenticate_with_password_and_totp(), authentication_start(), authentication_verify(), backup_authentication_status(), bootstrap_options(), bootstrap_verify(), _check_public_throttle(), _clear_auth_cookies() (+41 more)

### Community 14 - "Auth Throttling"
Cohesion: 0.10
Nodes (33): _auth_throttle(), MemoryAuthThrottle, datetime, Redis, timedelta, 公开身份 ceremony 的来源限流公共 seam。, 按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。, 多进程 API 使用的 Redis 固定窗口实现。 (+25 more)

### Community 15 - "Admin Test Helpers"
Cohesion: 0.09
Nodes (36): current_session(), AuthenticatedSessionDependency, admin_client(), passkey_client(), MonkeyPatch, TestClient, 通过 FastAPI 身份依赖注入建立已 step-up 管理员，不借用密码登录。, provision_editable_plan_context() (+28 more)

### Community 16 - "WebAuthn Tests"
Cohesion: 0.14
Nodes (37): csrf_headers(), _base64url(), _credential(), MonkeyPatch, TestClient, _registration_credential(), test_authentication_options_are_username_less_and_browser_ready(), test_authentication_options_do_not_increment_failure_limit() (+29 more)

### Community 17 - "BFF API Client"
Cohesion: 0.12
Nodes (30): backup_auth_api_request(), backup_login_api_request(), backup_reauthentication_api_request(), plan_api_request(), NiceGUI 服务端 BFF 客户端的公开接缝。, 以请求正文提交两项备用因素，不把秘密放入 URL。, 为当前备用会话取得仅可新增通行密钥的短时证明。, 读取本人最近 20 条内建安全事件，不产生已读状态。 (+22 more)

### Community 18 - "Security Configuration"
Cohesion: 0.09
Nodes (32): main(), AppSettings, global_security_ready(), BaseModel, 拒绝在非开发环境或非回环地址关闭 Cookie Secure。, 验证进程启动时的 Cookie 与监听地址组合。, JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。, validate_cookie_security() (+24 more)

### Community 19 - "Plan Routes"
Cohesion: 0.15
Nodes (36): archive_plan(), autosave_plan(), get_plan(), list_plans(), list_snapshots(), open_plan(), _plan(), CurrentSessionDependency (+28 more)

### Community 20 - "Challenge Management"
Cohesion: 0.10
Nodes (33): ChallengeBinding, ChallengeRecord, consume_challenge(), issue_challenge(), IssuedChallenge, datetime, WebAuthn ceremony challenge 的公共领域 seam。, 签发绑定上下文、五分钟有效且只保存摘要的 challenge。 (+25 more)

### Community 21 - "TOTP Secret Encryption"
Cohesion: 0.13
Nodes (20): identity_service(), _aad(), decrypt_totp_secret(), decrypt_totp_secret_with_provider(), encrypt_totp_secret(), encrypt_totp_secret_with_provider(), FileIdentitySecretKeyProvider, Path (+12 more)

### Community 22 - "User Management"
Cohesion: 0.19
Nodes (32): activate(), create_user(), credential_revoke(), credentials(), deactivate(), get_user(), _invitation(), invitation_issue() (+24 more)

### Community 23 - "Architecture Boundaries"
Cohesion: 0.08
Nodes (34): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+26 more)

### Community 24 - "Worker Prompt Tests"
Cohesion: 0.15
Nodes (20): _context(), FakeAuthorizer, FakeClient, FakeStore, _modules(), Any, datetime, UUID (+12 more)

### Community 25 - "Speckit Analysis"
Cohesion: 0.07
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+25 more)

### Community 26 - "Calendar Client"
Cohesion: 0.12
Nodes (23): _calendar_library_available(), map_timor_payload(), AsyncBaseTransport, date, TimorWorkdayClient, WorkdayResult, combine_workday_results(), date (+15 more)

### Community 27 - "Project Documentation"
Cohesion: 0.07
Nodes (32): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+24 more)

### Community 28 - "Password Hashing"
Cohesion: 0.14
Nodes (24): hash_password(), password_needs_rehash(), password_violations(), Path, verify_password(), _weak_passwords(), _native_url(), 通行密钥身份用例、一次性材料状态机与实时会话授权。 (+16 more)

### Community 29 - "Lesson Plan Repository"
Cohesion: 0.17
Nodes (11): AuthorRecord, LessonPlanRepository, _plan(), PlanCreationContext, PlanRecord, Any, date, UUID (+3 more)

### Community 30 - "Development Roadmap"
Cohesion: 0.10
Nodes (30): Dev Handoff 2026-07-24, Child Manager Roadmap, 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。, M5 完成后到 M4 的当前依赖路径是什么？, M0 Shared Baseline, M1 Engineering Skeleton, M2 Authentication Authorization, M3 Initial Settings (+22 more)

### Community 31 - "Lesson Plan Service"
Cohesion: 0.26
Nodes (10): lesson_plan_service(), LessonPlanService, OpenPlanResult, PlanView, _PlanViewSeed, date, UUID, 完成单一用例响应；外网解析发生在业务事务关闭之后。 (+2 more)

### Community 32 - "Transactional Semantics"
Cohesion: 0.07
Nodes (29): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, Child Manager Daily Activity API, Identity and Settings Endpoints, Plans, Jobs, and Exports Endpoints, API v1 Contract (+21 more)

### Community 33 - "Login Throttle"
Cohesion: 0.17
Nodes (10): _digest(), MemoryLoginThrottle, datetime, Redis, timedelta, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision (+2 more)

### Community 34 - "Prompt Test Store"
Cohesion: 0.18
Nodes (10): _native_url(), PostgresPromptTestStore, Any, datetime, UUID, 提示词测试 Worker 的 PostgreSQL 权威状态适配器。, UUID, 按任务与尝试次数生成可复现的有界抖动，便于恢复与确定性测试。 (+2 more)

### Community 35 - "AI Client Transport"
Cohesion: 0.12
Nodes (17): BaseTransport, ProviderNeutralAiClient, Resolver, AiClientError, RuntimeError, AddStepStore, AlwaysTimeoutClient, InvalidAddStepClient (+9 more)

### Community 36 - "Local Dev Environment"
Cohesion: 0.08
Nodes (25): 本地开发环境规范, 仅回环开发依赖, 生产拓扑延后, 工作树资源隔离, M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线 (+17 more)

### Community 37 - "Identity Enums"
Cohesion: 0.22
Nodes (13): ChallengePurpose, StrEnum, CredentialRecord, AuthResult, _challenge_digest(), _client_challenge(), _decode_base64url(), IdentityError (+5 more)

### Community 38 - "Backup Enrollment Tests"
Cohesion: 0.19
Nodes (21): ActorFixture, TestClient, test_admin_is_restricted_until_complete_backup_enrollment(), test_backup_status_and_enrollment_require_authentication(), test_enrollment_requires_password_and_totp_together_and_is_single_use(), test_expired_enrollment_cannot_enable_backup_auth(), test_new_enrollment_invalidates_the_previous_pending_enrollment(), test_replacing_enabled_material_revokes_only_related_backup_sessions() (+13 more)

### Community 39 - "Worker Broker"
Cohesion: 0.16
Nodes (16): Actor, build_prompt_test_executor(), Broker, register_actors(), build_redis_broker(), build_test_broker(), Broker, 生产 Redis 与确定性测试消息代理装配。 (+8 more)

### Community 40 - "Auth Smoke Tests"
Cohesion: 0.17
Nodes (19): login_page_text(), users_page_text(), BrowserContext, Page, _add_virtual_authenticator(), _auth_cookie_names(), _bootstrap_activate(), _bootstrap_start() (+11 more)

### Community 41 - "Job Service"
Cohesion: 0.12
Nodes (12): CurrentModelCallProfile, ProfileCallLimiter, PromptTestAuthorizer, PromptTestRetry, PromptTestStore, datetime, Protocol, RuntimeError (+4 more)

### Community 42 - "AI Generation Presave"
Cohesion: 0.30
Nodes (18): provision_enabled_ai_model(), _generation_headers(), MonkeyPatch, TestClient, test_database_unavailable_returns_503_then_leaves_no_job_or_result(), test_dispatch_failure_after_commit_keeps_202_pending_result(), test_generation_acceptance_creates_pending_result_with_frozen_input(), test_missing_model_configuration_returns_503_and_creates_nothing() (+10 more)

### Community 43 - "Prompt Test Job API"
Cohesion: 0.33
Nodes (17): FailingDispatcher, prompt_job_client(), _provision_model_and_version(), Any, TestClient, _resolver(), test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure(), test_draft_version_can_be_tested_before_publication() (+9 more)

### Community 44 - "Audit Service"
Cohesion: 0.15
Nodes (13): UUID, Dispatcher, Protocol, AuditEventReference, IdentityAuditEventCode, IdentityAuditMetadata, StrEnum, 身份阶段的稳定审计事件代码与最小资源引用。 (+5 more)

### Community 45 - "Local Dev Profile Tests"
Cohesion: 0.14
Nodes (14): _compose_config(), Any, 双实现本地开发档位的 Compose 合同。, test_compose_accepts_temporary_image_overrides(), test_compose_uses_selected_local_profile(), test_test_database_url_requires_an_explicit_profile(), block_external_network(), isolated_database_url() (+6 more)

### Community 46 - "Navigation"
Cohesion: 0.18
Nodes (15): navigation_for_capabilities(), 按 API capabilities 生成导航。, class_areas_page_text(), settings_page_text(), BrowserActor, _free_port(), _m3_services(), MonkeyPatch (+7 more)

### Community 47 - "AI Results Repository"
Cohesion: 0.30
Nodes (10): AiGenerationResultRecord, AiGenerationResultRepository, _json_object(), _optional_uuid(), Any, datetime, 同园隔离的 AI 生成结果 Repository。, _record() (+2 more)

### Community 48 - "Common Schemas"
Cohesion: 0.17
Nodes (14): canonical_request_fingerprint(), ErrorResponse, FieldError, _normalize_scalar(), Pagination, 跨服务使用的公共 Schema 与规范化函数。, 计算覆盖路由、实际资源与语义输入的 canonical SHA-256。, 统一错误、分页和 Request ID 契约。 (+6 more)

### Community 49 - "Backup Maintenance Tests"
Cohesion: 0.29
Nodes (15): authenticated_session(), IdentityServiceDependency, Cookie, _change_actor_to_teacher(), _enable_backup(), _identity_service(), _login_with_backup(), _native_url() (+7 more)

### Community 50 - "Recovery Actors"
Cohesion: 0.19
Nodes (10): datetime, Protocol, UUID, 只接收 job_id 的 Dramatiq actor 与 PostgreSQL 恢复扫描。, 按 PostgreSQL 权威状态重投 pending/过期租约任务。, recover_prompt_test_jobs(), RecoveryStore, Any (+2 more)

### Community 51 - "Plan Content Tests"
Cohesion: 0.18
Nodes (12): PlanContentV1, MonkeyPatch, test_rendered_plan_editor_has_labelled_status_fields_focus_order_and_touch_targets(), _job(), _plan(), MonkeyPatch, M6 教案栏目内预览与可恢复状态的 NiceGUI RED 冒烟。, test_generation_autosaves_before_submit_and_renders_accessible_status() (+4 more)

### Community 52 - "Shell Scripts"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 53 - "Health Checks"
Cohesion: 0.31
Nodes (15): create_app(), HealthDependencies, check(), dependencies(), Path, test_database_failure_returns_stable_503_code(), test_default_dependencies_check_real_local_runtime(), test_each_optional_dependency_only_degrades_ready_response() (+7 more)

### Community 54 - "AI Client SSRF"
Cohesion: 0.26
Nodes (12): _pinned_url(), Any, OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。, _addresses(), AiUrlPolicyError, Resolver, ValueError, AI 模型地址的保存时与连接前 SSRF 防护。 (+4 more)

### Community 55 - "AI Batch Generation Tests"
Cohesion: 0.26
Nodes (14): _idempotent_headers(), TestClient, test_batch_accepts_exactly_four_independent_children_and_derives_parent(), test_batch_database_parent_is_never_executable_or_dispatched(), test_batch_idempotency_replays_original_parent_and_rejects_changed_body(), ai_admin_client(), _profile_payload(), Any (+6 more)

### Community 56 - "CSRF Tests"
Cohesion: 0.60
Nodes (4): TestClient, test_csrf_cookie_is_signed_readable_and_not_httponly(), test_passkey_state_change_rejects_missing_csrf_and_wrong_origin(), test_recovery_rejects_malformed_signed_double_submit_token()

### Community 57 - "AI Preview Lifecycle"
Cohesion: 0.31
Nodes (12): _native_url(), NoCallExpectedClient, TestClient, UUID, _snapshot_count(), test_batch_and_nonfailed_ai_jobs_reject_explicit_retry(), test_cross_tenant_failed_job_is_hidden_from_retry(), test_expiration_scheduler_transitions_due_previews_once() (+4 more)

### Community 58 - "AI Key Rotation Tests"
Cohesion: 0.35
Nodes (10): _candidate(), FakeStore, _modules(), Any, UUID, test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it(), test_rotation_dry_run_and_repeated_batch_are_zero_write(), test_rotation_uses_stable_cursor_and_does_not_change_call_revision() (+2 more)

### Community 59 - "Job Status UI"
Cohesion: 0.18
Nodes (8): prompt_test_status(), PromptTestStatus, 异步提示词测试的稳定中文状态与无障碍语义。, should_poll(), prompt_edit_version_id(), prompt_test_record_text(), 刷新时优先恢复未发布草稿，避免用已发布正文覆盖编辑态。, 将服务端已脱敏的测试运行渲染为可读历史记录。

### Community 60 - "Web Entry"
Cohesion: 0.25
Nodes (11): main(), 仅绑定回环地址的 NiceGUI Web 入口。, _require_loopback(), _validate_cookie_security(), configure_logging(), EventDict, 递归清除 Web 日志中的凭证和内部 URL。, _redact() (+3 more)

### Community 61 - "Port Interfaces"
Cohesion: 0.21
Nodes (9): AiClient, Clock, DependencyCheck, JobBroker, datetime, Protocol, UUID, M1 外部边界所需的最小 Protocol。 (+1 more)

### Community 62 - "AI Preview Adoption"
Cohesion: 0.30
Nodes (11): create_completed_ai_preview(), TestClient, UUID, _native_url(), TestClient, UUID, _snapshot_count(), test_adopt_merges_preview_once_and_repeated_request_creates_no_second_snapshot() (+3 more)

### Community 63 - "Invitation Tests"
Cohesion: 0.33
Nodes (13): _base64url(), _create_teacher(), _issue(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes(), test_invitation_is_single_use_reissuable_and_revocable() (+5 more)

### Community 64 - "OpenAPI Contract Tests"
Cohesion: 0.40
Nodes (13): _assert_operation_contract(), _canonical_schema(), _effective_security(), _operations(), _parameter_shape(), Any, 运行时 OpenAPI 与冻结身份契约的一致性门禁。, _request_schema() (+5 more)

### Community 65 - "FastAPI App"
Cohesion: 0.21
Nodes (11): _error_response(), FastAPI, Request, UUID, FastAPI 应用装配、统一异常转换与健康端点。, _request_id(), Docker Compose 开发环境配置, GitHub Actions 质量检查工作流 (+3 more)

### Community 66 - "Settings Permissions"
Cohesion: 0.33
Nodes (12): admin_session(), CurrentSessionDependency, _provision_associated_teacher(), TestClient, UUID, _session_for(), teacher_client(), test_all_settings_routes_require_authentication() (+4 more)

### Community 67 - "Health Dependencies"
Cohesion: 0.24
Nodes (13): _ai_unconfigured(), build_health_dependencies(), _database_check(), _file_check(), _path_check(), Path, 从进程环境构造真实、无副作用的本地就绪检查。, _redis_check() (+5 more)

### Community 68 - "Credential Tests"
Cohesion: 0.36
Nodes (12): _base64url(), _insert_credential(), _native_url(), MonkeyPatch, TestClient, UUID, _registration_credential(), test_admin_cannot_revoke_last_active_admin_last_credential() (+4 more)

### Community 69 - "Plan AI Contracts"
Cohesion: 0.29
Nodes (11): _children(), _contract(), Any, ModuleType, M6 教案 AI 公共契约的 RED 验收。, test_ai_child_succeeded_is_not_a_valid_batch_completion_state(), test_batch_job_projects_zero_attempts_and_rejects_execution_shape(), test_batch_status_is_derived_only_from_exactly_four_children() (+3 more)

### Community 70 - "AI Prompt Settings Tests"
Cohesion: 0.19
Nodes (7): _job_status_module(), Any, MonkeyPatch, test_controls_have_keyboard_focus_and_error_label_associations(), test_job_status_recovers_configuration_change_with_chinese_action(), test_job_status_refreshes_until_terminal_and_restores_after_page_reload(), test_settings_controls_call_model_prompt_and_job_public_api_seams()

### Community 71 - "Auth Contract Tests"
Cohesion: 0.21
Nodes (7): APIRoute, Any, _resolve(), _runtime_routes(), test_auth_success_and_logout_lock_two_raw_cookie_headers(), test_runtime_auth_router_matches_frozen_passkey_paths(), test_runtime_auth_success_statuses_match_frozen_contract()

### Community 72 - "Project Context"
Cohesion: 0.24
Nodes (10): AI, Authentication, Authorization, Branch: dev, Branch: docs, Branch: main, PostgreSQL, Redis (+2 more)

### Community 73 - "Calendar Cache"
Cohesion: 0.32
Nodes (6): Any, date, datetime, UUID, 园所范围工作日缓存 Repository。, WorkdayCacheRepository

### Community 74 - "AI Prompt Repository Tests"
Cohesion: 0.30
Nodes (9): _modules(), Any, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_call_configuration_change_set_matches_the_frozen_revision_rules(), test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup(), test_model_reads_and_writes_are_tenant_scoped(), test_prompt_run_frozen_fields_cannot_be_updated() (+1 more)

### Community 75 - "OpenAPI Config"
Cohesion: 0.29
Nodes (9): _apply_operation_contract(), configure_openapi(), _no_content_response(), _operation(), Any, FastAPI, M2 运行时 OpenAPI 的集中契约装配。, 返回缓存后的 M2 运行时 OpenAPI 生成器。 (+1 more)

### Community 76 - "Authorization Assurance"
Cohesion: 0.38
Nodes (6): datetime, _session(), test_backup_reauthentication_only_authorizes_add_passkey_for_five_minutes(), test_expired_backup_reauthentication_cannot_add_passkey(), test_recent_webauthn_proof_satisfies_high_risk_identity_boundary(), test_restricted_enrollment_session_cannot_enter_business_routes()

### Community 77 - "TOTP Primitives"
Cohesion: 0.31
Nodes (10): candidate_totp_counters(), _counter(), generate_totp(), _hotp(), RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。, 返回当前时间步及相邻一个时间步，按 counter 递增排序。, 按固定 SHA-1、6 位、30 秒参数生成 TOTP。, 返回匹配且尚未消费的 counter；失败或重放时返回 ``None``。 (+2 more)

### Community 78 - "Backup Auth Contract"
Cohesion: 0.24
Nodes (7): Any, _resolve(), _runtime_routes(), test_backup_contract_marks_request_and_one_time_response_secrets(), test_runtime_router_exposes_the_user_story_2_endpoints(), test_runtime_router_matches_the_frozen_backup_contract(), test_runtime_user_story_2_openapi_matches_frozen_security_and_responses()

### Community 79 - "AI Client Tests"
Cohesion: 0.44
Nodes (10): _modules(), Any, _resolver(), test_client_caps_retry_after_at_sixty_seconds(), test_client_errors_are_stable_and_never_include_key_or_prompt(), test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin(), test_client_posts_openai_compatible_request_with_fixed_limits(), test_client_rejects_redirects_without_following_them() (+2 more)

### Community 80 - "Request Middleware"
Cohesion: 0.22
Nodes (7): API 请求 ID 与追踪 ID 中间件。, _request_id(), RequestContextMiddleware, ASGIApp, Receive, Scope, Send

### Community 81 - "BFF Proxy"
Cohesion: 0.29
Nodes (9): BffResponse, proxy_request(), AsyncBaseTransport, 按固定 allowlist 转发请求，并保留响应原始多值头。, MonkeyPatch, test_proxy_ignores_process_proxy_environment(), test_proxy_preserves_auth_set_cookie_as_raw_headers(), test_proxy_preserves_request_and_rebuilds_client_ip() (+1 more)

### Community 82 - "Database Sessions"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 83 - "Client IP Resolution"
Cohesion: 0.33
Nodes (8): Collection, parse_trusted_bff_peers(), 只接受显式配置的回环 BFF socket peer。, resolve_client_ip(), test_configured_loopback_bff_peer_can_supply_internal_client_ip(), test_non_loopback_peer_cannot_be_configured_as_trusted_bff(), test_trusted_bff_peers_are_empty_until_explicitly_configured(), test_untrusted_peer_cannot_supply_internal_client_ip()

### Community 84 - "Workday Service Tests"
Cohesion: 0.29
Nodes (6): _module(), MonkeyPatch, test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls(), test_local_result_wins_conflict_and_uses_one_hour_cache(), test_timor_client_enforces_one_total_deadline(), test_unsupported_local_calendar_range_softly_falls_back_to_online()

### Community 85 - "Security Defense"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 86 - "Identifier Normalization"
Cohesion: 0.39
Nodes (5): normalize_phone(), normalize_username(), test_invalid_phone_is_rejected(), test_phone_is_mainland_e164_or_empty(), test_username_is_nfkc_trimmed_and_lowercase()

### Community 87 - "Secret Encryption Tests"
Cohesion: 0.39
Nodes (8): _context(), _encryption_module(), Any, Path, test_development_key_provider_requires_owner_only_file_outside_repository(), test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution(), test_totp_secret_envelope_round_trips_with_random_96_bit_nonce(), test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce()

### Community 88 - "AI Prompts Migration"
Cohesion: 0.36
Nodes (6): Any, Column, 建立 AI 模型、提示词与 PostgreSQL 权威任务基础。, _seed_defaults(), _timestamps(), upgrade()

### Community 89 - "Backup Login Migration"
Cohesion: 0.46
Nodes (7): Script, _backup_revision(), MonkeyPatch, test_backup_auth_migration_creates_isolated_credentials_and_enrollments(), test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(), test_backup_auth_revision_follows_settings_and_precedes_lesson_plans(), test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade()

### Community 90 - "Task Tracking"
Cohesion: 0.32
Nodes (8): Foundational, Setup, T001, T002, T009, T021, Tasks: 首期一日活动计划完整闭环, User Story 1

### Community 91 - "AI Prompt Contracts"
Cohesion: 0.32
Nodes (6): Any, _schema(), test_model_and_job_contracts_freeze_revision_and_stable_errors(), test_prompt_test_contract_exposes_only_redacted_input_summary(), test_prompt_test_fingerprint_changes_across_prompt_codes(), test_runtime_exposes_the_complete_frozen_m4_route_surface()

### Community 92 - "OpenAPI Document Tests"
Cohesion: 0.39
Nodes (7): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_document_is_valid_31(), test_openapi_keeps_nicegui_as_the_only_browser_entry(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 93 - "Content V1 Tests"
Cohesion: 0.54
Nodes (7): _contracts(), _schemas(), test_completeness_is_independent_from_progressive_schema_validation(), test_empty_v1_content_supports_progressive_manual_editing(), test_reflection_is_nfkc_normalized_and_limited_to_200_codepoints(), test_statement_and_question_punctuation_are_strictly_chinese(), test_unknown_fields_and_unknown_content_versions_are_not_silently_coerced()

### Community 94 - "AI Key Envelope Tests"
Cohesion: 0.39
Nodes (7): _module(), Any, Path, test_ai_key_envelope_rejects_tampering_and_cross_profile_substitution(), test_ai_key_envelope_round_trips_with_random_96_bit_nonce(), test_file_key_provider_requires_owner_only_files_outside_repository(), test_static_key_provider_reads_old_key_but_writes_with_active_key()

### Community 95 - "AI URL Policy Tests"
Cohesion: 0.57
Nodes (7): _module(), Any, _resolver(), test_policy_accepts_only_allowlisted_public_https_and_checks_every_address(), test_policy_detects_dns_rebinding_before_connect(), test_policy_rejects_non_https_and_non_public_networks(), test_policy_requires_explicit_server_allowlist()

### Community 96 - "Prompt Catalog Tests"
Cohesion: 0.43
Nodes (7): _module(), Any, test_catalog_assigns_task_specific_minimum_variable_whitelists(), test_catalog_freezes_seven_codes_whitelists_schemas_and_hashes(), test_catalog_input_validation_excludes_teacher_identity_and_unknown_fields(), test_catalog_result_schemas_are_strict(), test_catalog_result_schemas_match_the_frozen_openapi_shapes()

### Community 97 - "Job Query Service"
Cohesion: 0.43
Nodes (3): job_query_service(), JobQueryService, UUID

### Community 98 - "Backup Auth Smoke"
Cohesion: 0.33
Nodes (5): security_event_text(), MonkeyPatch, test_backup_login_and_reauthentication_submit_secrets_only_in_post_bodies(), test_security_event_messages_cover_the_frozen_event_codes(), test_security_events_use_read_only_same_origin_api()

### Community 99 - "Passkey Migration"
Cohesion: 0.52
Nodes (5): Any, Column, _tenant_identity_columns(), _timestamps(), upgrade()

### Community 100 - "Project Constitution"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 101 - "Prompt Renderer Tests"
Cohesion: 0.48
Nodes (6): _module(), Any, test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(), test_renderer_fails_for_missing_variable_before_external_call(), test_renderer_rejects_every_non_frozen_placeholder_form(), test_renderer_uses_stable_json_and_never_recursively_renders_values()

### Community 102 - "CSRF Token Management"
Cohesion: 0.40
Nodes (5): _cookie_secure(), csrf(), _encode(), issue_csrf_token(), verify_csrf_token()

### Community 103 - "Identity & Audit Migration"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 104 - "Settings Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 105 - "Password TOTP Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 106 - "Lesson Plans Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 107 - "AI Results Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 109 - "TOTP Tests"
Cohesion: 0.53
Nodes (5): Any, test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps(), test_totp_rejects_the_same_or_earlier_counter_after_success(), test_totp_secret_is_unique_high_entropy_base32(), _totp_module()

### Community 110 - "Development Workflow Docs"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 113 - "AI Key Rotation Tests"
Cohesion: 0.60
Nodes (4): CompletedProcess, _run(), test_bootstrap_cli_exposes_rotation_without_master_key_arguments(), test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets()

### Community 114 - "Calendar Tests"
Cohesion: 0.70
Nodes (4): _calendar(), test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic(), test_out_of_semester_week_number_and_text_are_both_empty(), test_semester_start_week_is_week_one_and_increments_each_monday()

### Community 115 - "Dev Agent Tools"
Cohesion: 0.67
Nodes (4): AGENTS.md 开发规则文件, codebase-memory MCP, Graphify 知识图谱工具, 搜索工具优先级

### Community 116 - "Save Status Module"
Cohesion: 0.67
Nodes (3): save_status(), SaveStatus, SaveState

### Community 117 - "Kindergarten Core Tables"
Cohesion: 0.50
Nodes (4): Age Groups Table, Class Teachers Table, Classes Table, Daily Activity Plans Table

### Community 118 - "Database Isolation Concepts"
Cohesion: 0.50
Nodes (4): Composite Foreign Keys Concept, Kindergarten Isolation Concept, Kindergartens Table, Users Table

### Community 120 - "Backup Login Feature"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 122 - "Lesson Plan Contract Tests"
Cohesion: 0.83
Nodes (3): _contracts(), test_open_and_write_contracts_do_not_accept_tenant_or_ownership_mutation(), test_plan_snapshot_and_page_contracts_are_bounded_and_stable()

### Community 127 - "Migration Dependency Order"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

### Community 131 - "AI Step UI Layout"
Cohesion: 0.67
Nodes (3): AI-Added Step Red Text, Structured Daily Activity Sections, Daily Activity Plan Word Layout

## Knowledge Gaps
- **153 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+148 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **95 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `班级与教师配置` (2× useful, score=1.352895454)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IdentityRepository` connect `Backup Credential Repository` to `Identity Enums`, `Admin Initialization`, `Identity Migration Tests`, `Identity Service`, `Auth Throttling`, `Challenge Management`, `TOTP Secret Encryption`, `User Management`, `Password Hashing`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `ActorFixture` connect `Backup Enrollment Tests` to `Settings Permissions`, `Credential Tests`, `Admin Initialization`, `Identity Migration Tests`, `AI Generation Results`, `AI Generation Presave`, `Identity Service`, `Prompt Test Job API`, `Auth Throttling`, `Admin Test Helpers`, `WebAuthn Tests`, `Backup Maintenance Tests`, `AI Batch Generation Tests`, `AI Preview Lifecycle`, `AI Preview Adoption`, `Invitation Tests`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `IdentityError` connect `Identity Enums` to `Settings Repository`, `AI Key Rotation`, `Admin Initialization`, `Prompt Renderer`, `Auth Endpoints`, `Identity Service`, `Authentication Flow`, `Challenge Management`, `TOTP Secret Encryption`, `User Management`, `Calendar Client`, `Password Hashing`, `Lesson Plan Service`, `Audit Service`, `Backup Maintenance Tests`, `Health Checks`, `FastAPI App`, `Authorization Assurance`, `Job Query Service`, `CSRF Token Management`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `ActorFixture` (e.g. with `StaticIdentitySecretKeyProvider` and `IdentityService`) actually correct?**
  _`ActorFixture` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 134 inferred relationships involving `ContractModel` (e.g. with `AuditEventReference` and `IdentityAuditEventCode`) actually correct?**
  _`ContractModel` has 134 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `IdentityError` (e.g. with `create_app()` and `HealthDependencies`) actually correct?**
  _`IdentityError` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `IdentityRepository` (e.g. with `test_totp_counter_and_session_creation_roll_back_together()` and `test_identity_repository_exposes_atomic_backup_auth_operations()`) actually correct?**
  _`IdentityRepository` has 3 INFERRED edges - model-reasoned connections that need verification._