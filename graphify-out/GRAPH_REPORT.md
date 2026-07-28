# Graph Report - .  (2026-07-28)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2964 nodes · 8316 edges · 261 communities (162 shown, 99 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 708 edges (avg confidence: 0.54)
- Token cost: 11,095 input · 8,747 output

## Graph Freshness
- Built from commit: `a33441f8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Prompt Test Jobs
- Settings and AI Profiles
- Identity Backup Credentials
- AI Generation Request
- Admin Initialization and Keys
- Settings Age Groups and AI
- Prompt Template Renderer
- Auth and Export Contracts
- Identity Audit and Invitations
- Migration Tests
- Audit and Identity Models
- Authentication Flow
- Auth Throttle
- Prompt Test Actors
- WebAuthn Auth Tests
- BFF API Client
- AI Batch Generation Tests
- AI Results Migration Tests
- API Security Config
- Lesson Plan Routes
- TOTP Secret Encryption
- AI Client Errors
- WebAuthn Challenges
- Provider Neutral AI Client
- AI Audit Tests
- User Management Routes
- Project Roadmap Context
- Service Boundaries
- Prompt Test Worker Tests
- Speckit Consistency Analysis
- Secret Token Service
- Calendar Workday Client
- Document Baseline Fixes
- Identity Session Queries
- Lesson Plan Repository
- Lesson Plan Service
- TOTP Generation
- Job State Machine
- Login Throttle
- Prompt Test Store
- Local Dev Environment
- Backup Enrollment Tests
- Identity Auth Verification
- FastAPI App Assembly
- Prompt Test Jobs API Tests
- Navigation by Capabilities
- Audit Repository
- Compose Profile Tests
- AI Results Repository
- Backup Maintenance Tests
- Plan Accessibility Tests
- Speckit Shell Utilities
- AI Contract Tests
- Health Check Tests
- Health Dependencies
- AI Client SSRF Protection
- Prompt Contract Fingerprint
- AI Preview Lifecycle Tests
- AI Key Rotation Tests
- Prompt Test Status
- NiceGUI Web Entry
- Ports and Interfaces
- Invitation Tests
- OpenAPI Contract Tests
- Settings Permissions Tests
- Token Management
- Credential Management Tests
- AI Prompt Settings UI Tests
- Auth Contract Tests
- Password Hashing Policy
- AI Prompt Repository Tests
- OpenAPI Contract Assembly
- Admin CLI Initialization Tests
- Backup Auth Contract Tests
- AI Client Tests
- API Request ID Middleware
- BFF Proxy
- Database Session Management
- Client IP Resolution
- Workday Cache Repository
- AI Generation Pre-save Tests
- AI Model Profiles Tests
- Workday Service Tests
- Security Threat Model
- Identifier Normalization
- Secret Encryption Tests
- AI Prompts Jobs Migration
- Backup Login Migration Test
- OpenAPI Document Validation
- Plan Content V1 Tests
- AI Key Envelope Tests
- AI Model URL Policy Tests
- Prompt Catalog Tests
- Backup Auth Smoke Tests
- Passkey Migration
- Job Message Schema
- Project Constitution
- Task Specifications
- Prompt Renderer Tests
- CSRF Token Management
- Application Service Stack
- Identity and Audit Migration
- Settings Migration
- Password TOTP Backup Migration
- Lesson Plans Migration
- AI Generation Results Migration
- User Contract Tests
- TOTP Tests
- Development Workflow Rules
- Branch Creation Script
- CSRF Tests
- AI Key Rotation Tests
- Calendar Tests
- Agent Dev Tools
- Save Status Module
- Dev Environment Setup
- Child Manager Project
- Core Domain Tables
- Database Schema Concepts
- Snapshot Utilities
- Backup Login Feature
- Lesson Plan Contract Tests
- Calendar Fixture
- Fixed Clock Fixture
- Fake Job Broker
- Migration Dependency Rules
- Lease Utility
- Activity Plan UI Layout
- Fake AI Client
- Child Manager App Unit
- Worker App Unit
- Authentication Methods
- AI and Jobs Tables
- AI Model Profile Tables
- Prompt Definition Tables
- Role Tables
- Database Backend Base
- Weak Password List
- Backend Module
- Shared Contracts
- Prerequisites Check Script
- Plan Setup Script
- Tasks Setup Script
- Audit Feature
- Web Tests Module
- AI and Prompt Rules
- Branch and Git Rules
- Data Model Isolation
- Fact Source and Conflict
- Security and Privacy Rules
- Service Boundaries
- Testing Requirements
- Account Invitations Table
- Account Recovery Table
- Age Groups Table
- AI Results Table
- AI Model Capabilities Table
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
- Daily Activity Plans Table
- Identity Verification Table
- Snapshot Audit Immutability
- JSONB Schema Versioning
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
- Application Owned Transactions
- External Key Source Seam
- Broker
- Protocol
- Child Manager
- Development Workflow
- Governance
- Technical Constraints
- Activity Plan Checklist
- User Story 5
- User Story 6
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
- **System Architecture Components** — concept_nicegui_web, concept_fastapi_api, concept_worker, concept_postgresql, concept_redis, concept_alembic [EXTRACTED 1.00]
- **Project Milestones (M0-M9)** — milestone_m0, milestone_m1, milestone_m2, milestone_m3, milestone_m3a, milestone_m4, milestone_m5, milestone_m6, milestone_m7, milestone_m8, milestone_m9 [EXTRACTED 1.00]
- **User Stories (US1-US7)** — user_story_us1, user_story_us2, user_story_us3, user_story_us4, user_story_us5, user_story_us6, user_story_us7 [EXTRACTED 1.00]
- **User Story 2 Tasks Group** — specs_001-daily-activity-plan_tasks_us2, specs_001-daily-activity-plan_tasks_t046, specs_001-daily-activity-plan_tasks_t047, specs_001-daily-activity-plan_tasks_t048, specs_001-daily-activity-plan_tasks_t052 [EXTRACTED 1.00]
- **Tasks and Concepts for AI Generation in User Story 4** — specs_001_daily_activity_plan_tasks_us4, specs_001_daily_activity_plan_tasks_t087, specs_001_daily_activity_plan_tasks_t098, specs_001_daily_activity_plan_tasks_ai_generation [INFERRED 0.70]
- **Tasks and Concepts for Audit in User Story 7** — specs_001_daily_activity_plan_tasks_us7, specs_001_daily_activity_plan_tasks_audit [EXTRACTED 1.00]
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
- **Speckit Full SDD Lifecycle** — _agents_skills_speckit_specify_skill_speckit_specify, _agents_skills_speckit_plan_skill_speckit_plan, _agents_skills_speckit_tasks_skill_speckit_tasks, _agents_skills_speckit_implement_skill_speckit_implement [EXTRACTED 1.00]
- **Web API Worker Boundary Alignment** — docs_adr_adr_0002_separate_web_api_worker_modular_monolith_modular_monolith, docs_adr_adr_0002_separate_web_api_worker_modular_monolith_service_boundaries, docs_design_system_architecture_modular_runtime_architecture, docs_design_system_architecture_trust_starts_at_api [INFERRED 0.95]
- **本地开发隔离模式** — docs_development_local_development_environments_worktree_resource_isolation, docs_development_local_development_environments_loopback_only_dependencies, docs_development_local_development_environments_production_topology_deferral [EXTRACTED 1.00]
- **M0 收敛证据链** — docs_faq_combined_audit_m0_gate_framework, docs______20260713________m0_gate_closure_evidence, docs______20260713____________final_docs_baseline [INFERRED 0.85]
- **身份纵深防御** — docs_security_threat_model_restricted_public_entry, docs_security_threat_model_phishing_resistant_authentication, docs_security_threat_model_password_totp_backup, docs_security_threat_model_emergency_recovery_dual_control [EXTRACTED 1.00]

## Communities (261 total, 99 thin omitted)

### Community 0 - "Prompt Test Jobs"
Cohesion: 0.05
Nodes (120): alias, get_job(), AdminSessionDependency, UUID, clear_prompt_tests(), create_prompt_test(), _definition(), get_prompt() (+112 more)

### Community 1 - "Settings and AI Profiles"
Cohesion: 0.06
Nodes (53): settings_service(), IntegrityError, NoReturn, AgeGroupRecord, _ai_profile(), AiModelProfileRecord, AiModelProfileRepository, AreaInput (+45 more)

### Community 2 - "Identity Backup Credentials"
Cohesion: 0.05
Nodes (31): _backup_credential(), _backup_enrollment(), BackupCredentialRecord, BackupEnrollmentRecord, BackupRevocationResult, BackupSecurityEventRecord, ChallengeRecord, _credential() (+23 more)

### Community 3 - "AI Generation Request"
Cohesion: 0.06
Nodes (55): ActorFixture, AiBatchRequest, AiGenerationRequest, AiGenerationResultRecord, AiGenerationResultRepository, AiTaskCode, Broker, Connection (+47 more)

### Community 4 - "Admin Initialization and Keys"
Cohesion: 0.07
Nodes (53): AiKeyProvider, ai_model_service(), ArgumentParser, activate_initialization(), migrate_passkeys(), _native_url(), datetime, UUID (+45 more)

### Community 5 - "Settings Age Groups and AI"
Cohesion: 0.08
Nodes (64): AgeGroup, AiModelProfile, AiModelServiceDependency, _age_group(), _ai_model(), _area(), _class(), create_ai_model_profile() (+56 more)

### Community 6 - "Prompt Template Renderer"
Cohesion: 0.11
Nodes (24): prompt_service(), validate_prompt_variables(), PromptTemplateError, Any, ValueError, 仅支持固定白名单纯替换词法的提示词渲染器。, render_prompt(), _render_value() (+16 more)

### Community 7 - "Auth and Export Contracts"
Cohesion: 0.08
Nodes (54): _allowed_origins(), _loopback_aliases(), 同源 Cookie、WebAuthn、邀请、恢复与会话端点。, ContractModel, BaseModel, ExportReference, AdminCredentialRevocationResult, AuthenticationCredential (+46 more)

### Community 8 - "Identity Audit and Invitations"
Cohesion: 0.18
Nodes (7): AuditRepository, InvitationRecord, IdentityService, ManagedUser, UUID, SessionUser, BackupAuthenticationStatus

### Community 9 - "Migration Tests"
Cohesion: 0.07
Nodes (44): migrated_database(), MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds(), test_identity_migration_is_idempotent(), MonkeyPatch, settings_database(), test_age_group_seed_is_fixed_and_idempotent(), test_area_constraints_allow_empty_collections_but_reject_duplicate_names() (+36 more)

### Community 10 - "Audit and Identity Models"
Cohesion: 0.10
Nodes (40): DeclarativeBase, AuditEvent, Base, AccountInvitation, AccountRecoveryRequest, BackupAuthCredential, BackupAuthEnrollment, BootstrapInitialization (+32 more)

### Community 11 - "Authentication Flow"
Cohesion: 0.18
Nodes (49): authenticate_with_password_and_totp(), authentication_start(), authentication_verify(), backup_authentication_status(), bootstrap_options(), bootstrap_verify(), _check_public_throttle(), _clear_auth_cookies() (+41 more)

### Community 12 - "Auth Throttle"
Cohesion: 0.10
Nodes (33): _auth_throttle(), MemoryAuthThrottle, datetime, Redis, timedelta, 公开身份 ceremony 的来源限流公共 seam。, 按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。, 多进程 API 使用的 Redis 固定窗口实现。 (+25 more)

### Community 13 - "Prompt Test Actors"
Cohesion: 0.09
Nodes (27): Actor, build_prompt_test_executor(), Broker, datetime, Protocol, UUID, 只接收 job_id 的 Dramatiq actor 与 PostgreSQL 恢复扫描。, 按 PostgreSQL 权威状态重投 pending/过期租约任务。 (+19 more)

### Community 14 - "WebAuthn Auth Tests"
Cohesion: 0.14
Nodes (37): csrf_headers(), _base64url(), _credential(), MonkeyPatch, TestClient, _registration_credential(), test_authentication_options_are_username_less_and_browser_ready(), test_authentication_options_do_not_increment_failure_limit() (+29 more)

### Community 15 - "BFF API Client"
Cohesion: 0.12
Nodes (30): backup_auth_api_request(), backup_login_api_request(), backup_reauthentication_api_request(), plan_api_request(), NiceGUI 服务端 BFF 客户端的公开接缝。, 以请求正文提交两项备用因素，不把秘密放入 URL。, 为当前备用会话取得仅可新增通行密钥的短时证明。, 读取本人最近 20 条内建安全事件，不产生已读状态。 (+22 more)

### Community 16 - "AI Batch Generation Tests"
Cohesion: 0.12
Nodes (30): admin_client(), passkey_client(), MonkeyPatch, TestClient, 通过 FastAPI 身份依赖注入建立已 step-up 管理员，不借用密码登录。, provision_editable_plan_context(), date, TestClient (+22 more)

### Community 17 - "AI Results Migration Tests"
Cohesion: 0.18
Nodes (34): _insert_job(), _insert_other_tenant_plan(), _insert_result(), _native_url(), _provision_dependencies(), TestClient, UUID, _result_values() (+26 more)

### Community 18 - "API Security Config"
Cohesion: 0.09
Nodes (32): main(), AppSettings, global_security_ready(), BaseModel, 拒绝在非开发环境或非回环地址关闭 Cookie Secure。, 验证进程启动时的 Cookie 与监听地址组合。, JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。, validate_cookie_security() (+24 more)

### Community 19 - "Lesson Plan Routes"
Cohesion: 0.15
Nodes (36): archive_plan(), autosave_plan(), get_plan(), list_plans(), list_snapshots(), open_plan(), _plan(), CurrentSessionDependency (+28 more)

### Community 20 - "TOTP Secret Encryption"
Cohesion: 0.12
Nodes (23): _aad(), decrypt_totp_secret(), decrypt_totp_secret_with_provider(), encrypt_totp_secret(), encrypt_totp_secret_with_provider(), FileIdentitySecretKeyProvider, Path, UUID (+15 more)

### Community 21 - "AI Client Errors"
Cohesion: 0.11
Nodes (15): AiClientError, RuntimeError, CurrentModelCallProfile, ProfileCallLimiter, PromptTestAuthorizer, PromptTestExecutionContext, PromptTestRetry, PromptTestStore (+7 more)

### Community 22 - "WebAuthn Challenges"
Cohesion: 0.10
Nodes (34): ChallengeBinding, ChallengeRecord, consume_challenge(), issue_challenge(), IssuedChallenge, datetime, WebAuthn ceremony challenge 的公共领域 seam。, 签发绑定上下文、五分钟有效且只保存摘要的 challenge。 (+26 more)

### Community 23 - "Provider Neutral AI Client"
Cohesion: 0.10
Nodes (20): BaseTransport, ProviderNeutralAiClient, Resolver, _executor(), Any, datetime, UUID, StatefulStore (+12 more)

### Community 24 - "AI Audit Tests"
Cohesion: 0.14
Nodes (29): create_completed_ai_preview(), provision_enabled_ai_model(), TestClient, UUID, _event(), TestClient, test_ai_audit_event_codes_cover_creation_retries_result_reject_and_adopt(), test_generation_reject_adopt_and_retry_write_sanitized_audit_rows() (+21 more)

### Community 25 - "User Management Routes"
Cohesion: 0.19
Nodes (32): activate(), create_user(), credential_revoke(), credentials(), deactivate(), get_user(), _invitation(), invitation_issue() (+24 more)

### Community 26 - "Project Roadmap Context"
Cohesion: 0.09
Nodes (34): Child Manager Project Context, Dev Handoff 2026-07-24, Child Manager Roadmap, 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。, M5 完成后到 M4 的当前依赖路径是什么？, M0 Shared Design Baseline, M1 Engineering Skeleton, M2 Authentication and Authorization (+26 more)

### Community 27 - "Service Boundaries"
Cohesion: 0.08
Nodes (34): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+26 more)

### Community 28 - "Prompt Test Worker Tests"
Cohesion: 0.15
Nodes (20): _context(), FakeAuthorizer, FakeClient, FakeStore, _modules(), Any, datetime, UUID (+12 more)

### Community 29 - "Speckit Consistency Analysis"
Cohesion: 0.07
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+25 more)

### Community 30 - "Secret Token Service"
Cohesion: 0.14
Nodes (29): identity_service(), _digest(), issue_secret(), IssuedSecret, StrEnum, 生成 256 位一次性秘密，持久化对象中只保留 purpose 绑定摘要。, 以常量时间比较 purpose 绑定摘要。, SecretPurpose (+21 more)

### Community 31 - "Calendar Workday Client"
Cohesion: 0.12
Nodes (23): map_timor_payload(), AsyncBaseTransport, date, TimorWorkdayClient, WorkdayResult, 园所范围工作日缓存 Repository。, combine_workday_results(), date (+15 more)

### Community 32 - "Document Baseline Fixes"
Cohesion: 0.07
Nodes (32): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+24 more)

### Community 33 - "Identity Session Queries"
Cohesion: 0.12
Nodes (16): current_session(), job_query_service(), AuthenticatedSessionDependency, IdentityError, Exception, generate_totp_secret(), 生成认证器广泛兼容的 160 位无填充 Base32 种子。, JobQueryService (+8 more)

### Community 34 - "Lesson Plan Repository"
Cohesion: 0.17
Nodes (11): AuthorRecord, LessonPlanRepository, _plan(), PlanCreationContext, PlanRecord, Any, date, UUID (+3 more)

### Community 35 - "Lesson Plan Service"
Cohesion: 0.26
Nodes (10): lesson_plan_service(), LessonPlanService, OpenPlanResult, PlanView, _PlanViewSeed, date, UUID, 完成单一用例响应；外网解析发生在业务事务关闭之后。 (+2 more)

### Community 36 - "TOTP Generation"
Cohesion: 0.12
Nodes (27): login_page_text(), users_page_text(), BrowserContext, candidate_totp_counters(), _counter(), generate_totp(), _hotp(), RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。 (+19 more)

### Community 37 - "Job State Machine"
Cohesion: 0.07
Nodes (29): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, Child Manager Daily Activity API, Identity and Settings Endpoints, Plans, Jobs, and Exports Endpoints, API v1 Contract (+21 more)

### Community 38 - "Login Throttle"
Cohesion: 0.17
Nodes (10): _digest(), MemoryLoginThrottle, datetime, Redis, timedelta, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision (+2 more)

### Community 39 - "Prompt Test Store"
Cohesion: 0.18
Nodes (9): _native_url(), PostgresPromptTestStore, Any, datetime, UUID, 提示词测试 Worker 的 PostgreSQL 权威状态适配器。, UUID, 按任务与尝试次数生成可复现的有界抖动，便于恢复与确定性测试。 (+1 more)

### Community 40 - "Local Dev Environment"
Cohesion: 0.08
Nodes (25): 本地开发环境规范, 仅回环开发依赖, 生产拓扑延后, 工作树资源隔离, M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线 (+17 more)

### Community 41 - "Backup Enrollment Tests"
Cohesion: 0.19
Nodes (21): ActorFixture, TestClient, test_admin_is_restricted_until_complete_backup_enrollment(), test_backup_status_and_enrollment_require_authentication(), test_enrollment_requires_password_and_totp_together_and_is_single_use(), test_expired_enrollment_cannot_enable_backup_auth(), test_new_enrollment_invalidates_the_previous_pending_enrollment(), test_replacing_enabled_material_revokes_only_related_backup_sessions() (+13 more)

### Community 42 - "Identity Auth Verification"
Cohesion: 0.22
Nodes (11): ChallengePurpose, StrEnum, AuthResult, _challenge_digest(), _client_challenge(), _decode_base64url(), _native_url(), Any (+3 more)

### Community 43 - "FastAPI App Assembly"
Cohesion: 0.15
Nodes (15): _error_response(), FastAPI, Request, UUID, FastAPI 应用装配、统一异常转换与健康端点。, _request_id(), JSONResponse, ErrorResponse (+7 more)

### Community 44 - "Prompt Test Jobs API Tests"
Cohesion: 0.33
Nodes (17): FailingDispatcher, prompt_job_client(), _provision_model_and_version(), Any, TestClient, _resolver(), test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure(), test_draft_version_can_be_tested_before_publication() (+9 more)

### Community 45 - "Navigation by Capabilities"
Cohesion: 0.17
Nodes (16): navigation_for_capabilities(), 按 API capabilities 生成导航。, class_areas_page_text(), settings_page_text(), test_navigation_is_derived_from_current_api_capabilities(), BrowserActor, _free_port(), _m3_services() (+8 more)

### Community 46 - "Audit Repository"
Cohesion: 0.15
Nodes (13): UUID, Dispatcher, Protocol, AuditEventReference, IdentityAuditEventCode, IdentityAuditMetadata, StrEnum, 身份阶段的稳定审计事件代码与最小资源引用。 (+5 more)

### Community 47 - "Compose Profile Tests"
Cohesion: 0.14
Nodes (14): _compose_config(), Any, 双实现本地开发档位的 Compose 合同。, test_compose_accepts_temporary_image_overrides(), test_compose_uses_selected_local_profile(), test_test_database_url_requires_an_explicit_profile(), block_external_network(), isolated_database_url() (+6 more)

### Community 48 - "AI Results Repository"
Cohesion: 0.30
Nodes (10): AiGenerationResultRecord, AiGenerationResultRepository, _json_object(), _optional_uuid(), Any, datetime, 同园隔离的 AI 生成结果 Repository。, _record() (+2 more)

### Community 49 - "Backup Maintenance Tests"
Cohesion: 0.29
Nodes (15): authenticated_session(), IdentityServiceDependency, Cookie, _change_actor_to_teacher(), _enable_backup(), _identity_service(), _login_with_backup(), _native_url() (+7 more)

### Community 50 - "Plan Accessibility Tests"
Cohesion: 0.18
Nodes (12): PlanContentV1, MonkeyPatch, test_rendered_plan_editor_has_labelled_status_fields_focus_order_and_touch_targets(), _job(), _plan(), MonkeyPatch, M6 教案栏目内预览与可恢复状态的 NiceGUI RED 冒烟。, test_generation_autosaves_before_submit_and_renders_accessible_status() (+4 more)

### Community 51 - "Speckit Shell Utilities"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 52 - "AI Contract Tests"
Cohesion: 0.21
Nodes (15): AI Generation, Task T087: Tests for AI contracts, Task T098: Implement AI contracts, User Story 4, _children(), _contract(), Any, ModuleType (+7 more)

### Community 53 - "Health Check Tests"
Cohesion: 0.31
Nodes (15): create_app(), HealthDependencies, check(), dependencies(), Path, test_database_failure_returns_stable_503_code(), test_default_dependencies_check_real_local_runtime(), test_each_optional_dependency_only_degrades_ready_response() (+7 more)

### Community 54 - "Health Dependencies"
Cohesion: 0.23
Nodes (14): _ai_unconfigured(), build_health_dependencies(), _calendar_library_available(), _database_check(), _file_check(), _path_check(), Path, 从进程环境构造真实、无副作用的本地就绪检查。 (+6 more)

### Community 55 - "AI Client SSRF Protection"
Cohesion: 0.26
Nodes (12): _pinned_url(), Any, OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。, _addresses(), AiUrlPolicyError, Resolver, ValueError, AI 模型地址的保存时与连接前 SSRF 防护。 (+4 more)

### Community 56 - "Prompt Contract Fingerprint"
Cohesion: 0.17
Nodes (13): canonical_request_fingerprint(), _normalize_scalar(), 计算覆盖路由、实际资源与语义输入的 canonical SHA-256。, Any, _schema(), test_model_and_job_contracts_freeze_revision_and_stable_errors(), test_prompt_test_contract_exposes_only_redacted_input_summary(), test_prompt_test_fingerprint_changes_across_prompt_codes() (+5 more)

### Community 57 - "AI Preview Lifecycle Tests"
Cohesion: 0.31
Nodes (12): _native_url(), NoCallExpectedClient, TestClient, UUID, _snapshot_count(), test_batch_and_nonfailed_ai_jobs_reject_explicit_retry(), test_cross_tenant_failed_job_is_hidden_from_retry(), test_expiration_scheduler_transitions_due_previews_once() (+4 more)

### Community 58 - "AI Key Rotation Tests"
Cohesion: 0.35
Nodes (10): _candidate(), FakeStore, _modules(), Any, UUID, test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it(), test_rotation_dry_run_and_repeated_batch_are_zero_write(), test_rotation_uses_stable_cursor_and_does_not_change_call_revision() (+2 more)

### Community 59 - "Prompt Test Status"
Cohesion: 0.18
Nodes (8): prompt_test_status(), PromptTestStatus, 异步提示词测试的稳定中文状态与无障碍语义。, should_poll(), prompt_edit_version_id(), prompt_test_record_text(), 刷新时优先恢复未发布草稿，避免用已发布正文覆盖编辑态。, 将服务端已脱敏的测试运行渲染为可读历史记录。

### Community 60 - "NiceGUI Web Entry"
Cohesion: 0.25
Nodes (11): main(), 仅绑定回环地址的 NiceGUI Web 入口。, _require_loopback(), _validate_cookie_security(), configure_logging(), EventDict, 递归清除 Web 日志中的凭证和内部 URL。, _redact() (+3 more)

### Community 61 - "Ports and Interfaces"
Cohesion: 0.21
Nodes (9): AiClient, Clock, DependencyCheck, JobBroker, datetime, Protocol, UUID, M1 外部边界所需的最小 Protocol。 (+1 more)

### Community 62 - "Invitation Tests"
Cohesion: 0.33
Nodes (13): _base64url(), _create_teacher(), _issue(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes(), test_invitation_is_single_use_reissuable_and_revocable() (+5 more)

### Community 63 - "OpenAPI Contract Tests"
Cohesion: 0.40
Nodes (13): _assert_operation_contract(), _canonical_schema(), _effective_security(), _operations(), _parameter_shape(), Any, 运行时 OpenAPI 与冻结身份契约的一致性门禁。, _request_schema() (+5 more)

### Community 64 - "Settings Permissions Tests"
Cohesion: 0.33
Nodes (12): admin_session(), CurrentSessionDependency, _provision_associated_teacher(), TestClient, UUID, _session_for(), teacher_client(), test_all_settings_routes_require_authentication() (+4 more)

### Community 65 - "Token Management"
Cohesion: 0.33
Nodes (10): create_access_token(), decode_access_token(), generate_refresh_token(), hash_refresh_token(), Any, datetime, Access JWT 与 opaque Refresh token 接缝。, test_access_token_contains_minimal_identity_and_fifteen_minute_expiry() (+2 more)

### Community 66 - "Credential Management Tests"
Cohesion: 0.36
Nodes (12): _base64url(), _insert_credential(), _native_url(), MonkeyPatch, TestClient, UUID, _registration_credential(), test_admin_cannot_revoke_last_active_admin_last_credential() (+4 more)

### Community 67 - "AI Prompt Settings UI Tests"
Cohesion: 0.19
Nodes (7): _job_status_module(), Any, MonkeyPatch, test_controls_have_keyboard_focus_and_error_label_associations(), test_job_status_recovers_configuration_change_with_chinese_action(), test_job_status_refreshes_until_terminal_and_restores_after_page_reload(), test_settings_controls_call_model_prompt_and_job_public_api_seams()

### Community 68 - "Auth Contract Tests"
Cohesion: 0.21
Nodes (7): APIRoute, Any, _resolve(), _runtime_routes(), test_auth_success_and_logout_lock_two_raw_cookie_headers(), test_runtime_auth_router_matches_frozen_passkey_paths(), test_runtime_auth_success_statuses_match_frozen_contract()

### Community 69 - "Password Hashing Policy"
Cohesion: 0.33
Nodes (10): hash_password(), password_needs_rehash(), password_violations(), Path, verify_password(), _weak_passwords(), Path, test_backup_password_hash_uses_auditable_argon2id_floor_and_rehashes() (+2 more)

### Community 70 - "AI Prompt Repository Tests"
Cohesion: 0.30
Nodes (9): _modules(), Any, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_call_configuration_change_set_matches_the_frozen_revision_rules(), test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup(), test_model_reads_and_writes_are_tenant_scoped(), test_prompt_run_frozen_fields_cannot_be_updated() (+1 more)

### Community 71 - "OpenAPI Contract Assembly"
Cohesion: 0.29
Nodes (9): _apply_operation_contract(), configure_openapi(), _no_content_response(), _operation(), Any, FastAPI, M2 运行时 OpenAPI 的集中契约装配。, 返回缓存后的 M2 运行时 OpenAPI 生成器。 (+1 more)

### Community 72 - "Admin CLI Initialization Tests"
Cohesion: 0.40
Nodes (10): _prepare_last_admin_recovery(), CompletedProcess, MonkeyPatch, UUID, _run_cli(), test_init_admin_activate_requires_two_distinct_pre_registered_approvers(), test_init_admin_cli_exposes_start_activate_and_migration_commands(), test_init_admin_start_creates_pending_account_and_one_time_secret_without_password() (+2 more)

### Community 73 - "Backup Auth Contract Tests"
Cohesion: 0.24
Nodes (7): Any, _resolve(), _runtime_routes(), test_backup_contract_marks_request_and_one_time_response_secrets(), test_runtime_router_exposes_the_user_story_2_endpoints(), test_runtime_router_matches_the_frozen_backup_contract(), test_runtime_user_story_2_openapi_matches_frozen_security_and_responses()

### Community 74 - "AI Client Tests"
Cohesion: 0.44
Nodes (10): _modules(), Any, _resolver(), test_client_caps_retry_after_at_sixty_seconds(), test_client_errors_are_stable_and_never_include_key_or_prompt(), test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin(), test_client_posts_openai_compatible_request_with_fixed_limits(), test_client_rejects_redirects_without_following_them() (+2 more)

### Community 75 - "API Request ID Middleware"
Cohesion: 0.22
Nodes (7): API 请求 ID 与追踪 ID 中间件。, _request_id(), RequestContextMiddleware, ASGIApp, Receive, Scope, Send

### Community 76 - "BFF Proxy"
Cohesion: 0.29
Nodes (9): BffResponse, proxy_request(), AsyncBaseTransport, 按固定 allowlist 转发请求，并保留响应原始多值头。, MonkeyPatch, test_proxy_ignores_process_proxy_environment(), test_proxy_preserves_auth_set_cookie_as_raw_headers(), test_proxy_preserves_request_and_rebuilds_client_ip() (+1 more)

### Community 77 - "Database Session Management"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 78 - "Client IP Resolution"
Cohesion: 0.33
Nodes (8): Collection, parse_trusted_bff_peers(), 只接受显式配置的回环 BFF socket peer。, resolve_client_ip(), test_configured_loopback_bff_peer_can_supply_internal_client_ip(), test_non_loopback_peer_cannot_be_configured_as_trusted_bff(), test_trusted_bff_peers_are_empty_until_explicitly_configured(), test_untrusted_peer_cannot_supply_internal_client_ip()

### Community 79 - "Workday Cache Repository"
Cohesion: 0.38
Nodes (5): Any, date, datetime, UUID, WorkdayCacheRepository

### Community 80 - "AI Generation Pre-save Tests"
Cohesion: 0.49
Nodes (9): _generation_headers(), MonkeyPatch, TestClient, test_database_unavailable_returns_503_then_leaves_no_job_or_result(), test_dispatch_failure_after_commit_keeps_202_pending_result(), test_generation_acceptance_creates_pending_result_with_frozen_input(), test_missing_model_configuration_returns_503_and_creates_nothing(), test_single_generation_freezes_the_saved_version_without_mutating_plan() (+1 more)

### Community 81 - "AI Model Profiles Tests"
Cohesion: 0.40
Nodes (9): ai_admin_client(), _profile_payload(), Any, TestClient, _resolver(), test_admin_creates_write_only_masked_profile_and_cannot_read_key(), test_call_fields_increment_revision_but_display_and_limits_do_not(), test_disable_preserves_profile_and_default_switch_is_tenant_local() (+1 more)

### Community 82 - "Workday Service Tests"
Cohesion: 0.29
Nodes (6): _module(), MonkeyPatch, test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls(), test_local_result_wins_conflict_and_uses_one_hour_cache(), test_timor_client_enforces_one_total_deadline(), test_unsupported_local_calendar_range_softly_falls_back_to_online()

### Community 83 - "Security Threat Model"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 84 - "Identifier Normalization"
Cohesion: 0.39
Nodes (5): normalize_phone(), normalize_username(), test_invalid_phone_is_rejected(), test_phone_is_mainland_e164_or_empty(), test_username_is_nfkc_trimmed_and_lowercase()

### Community 85 - "Secret Encryption Tests"
Cohesion: 0.39
Nodes (8): _context(), _encryption_module(), Any, Path, test_development_key_provider_requires_owner_only_file_outside_repository(), test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution(), test_totp_secret_envelope_round_trips_with_random_96_bit_nonce(), test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce()

### Community 86 - "AI Prompts Jobs Migration"
Cohesion: 0.36
Nodes (6): Any, Column, 建立 AI 模型、提示词与 PostgreSQL 权威任务基础。, _seed_defaults(), _timestamps(), upgrade()

### Community 87 - "Backup Login Migration Test"
Cohesion: 0.46
Nodes (7): Script, _backup_revision(), MonkeyPatch, test_backup_auth_migration_creates_isolated_credentials_and_enrollments(), test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(), test_backup_auth_revision_follows_settings_and_precedes_lesson_plans(), test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade()

### Community 88 - "OpenAPI Document Validation"
Cohesion: 0.39
Nodes (7): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_document_is_valid_31(), test_openapi_keeps_nicegui_as_the_only_browser_entry(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 89 - "Plan Content V1 Tests"
Cohesion: 0.54
Nodes (7): _contracts(), _schemas(), test_completeness_is_independent_from_progressive_schema_validation(), test_empty_v1_content_supports_progressive_manual_editing(), test_reflection_is_nfkc_normalized_and_limited_to_200_codepoints(), test_statement_and_question_punctuation_are_strictly_chinese(), test_unknown_fields_and_unknown_content_versions_are_not_silently_coerced()

### Community 90 - "AI Key Envelope Tests"
Cohesion: 0.39
Nodes (7): _module(), Any, Path, test_ai_key_envelope_rejects_tampering_and_cross_profile_substitution(), test_ai_key_envelope_round_trips_with_random_96_bit_nonce(), test_file_key_provider_requires_owner_only_files_outside_repository(), test_static_key_provider_reads_old_key_but_writes_with_active_key()

### Community 91 - "AI Model URL Policy Tests"
Cohesion: 0.57
Nodes (7): _module(), Any, _resolver(), test_policy_accepts_only_allowlisted_public_https_and_checks_every_address(), test_policy_detects_dns_rebinding_before_connect(), test_policy_rejects_non_https_and_non_public_networks(), test_policy_requires_explicit_server_allowlist()

### Community 92 - "Prompt Catalog Tests"
Cohesion: 0.43
Nodes (7): _module(), Any, test_catalog_assigns_task_specific_minimum_variable_whitelists(), test_catalog_freezes_seven_codes_whitelists_schemas_and_hashes(), test_catalog_input_validation_excludes_teacher_identity_and_unknown_fields(), test_catalog_result_schemas_are_strict(), test_catalog_result_schemas_match_the_frozen_openapi_shapes()

### Community 93 - "Backup Auth Smoke Tests"
Cohesion: 0.33
Nodes (5): security_event_text(), MonkeyPatch, test_backup_login_and_reauthentication_submit_secrets_only_in_post_bodies(), test_security_event_messages_cover_the_frozen_event_codes(), test_security_events_use_read_only_same_origin_api()

### Community 94 - "Passkey Migration"
Cohesion: 0.52
Nodes (5): Any, Column, _tenant_identity_columns(), _timestamps(), upgrade()

### Community 95 - "Job Message Schema"
Cohesion: 0.29
Nodes (5): JobMessage, Redis 中唯一允许传递的最小任务消息。, ScriptedHeartbeatEvent, test_ai_actor_message_schema_contains_only_job_id(), test_job_message_only_contains_job_id()

### Community 96 - "Project Constitution"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 97 - "Task Specifications"
Cohesion: 0.33
Nodes (7): Daily Activity Plan Tasks Specification, Task T046: Write RED tests for lesson plan content schema and calendar, Task T047: Write RED tests for migration and repository constraints, Task T048: Write RED tests for contract and error handling, Task T052: Implement PlanContentV1 and contracts, User Story 2: Daily Activity Plan, User Story 3: AI Configuration

### Community 98 - "Prompt Renderer Tests"
Cohesion: 0.48
Nodes (6): _module(), Any, test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(), test_renderer_fails_for_missing_variable_before_external_call(), test_renderer_rejects_every_non_frozen_placeholder_form(), test_renderer_uses_stable_json_and_never_recursively_renders_values()

### Community 99 - "CSRF Token Management"
Cohesion: 0.40
Nodes (5): _cookie_secure(), csrf(), _encode(), issue_csrf_token(), verify_csrf_token()

### Community 100 - "Application Service Stack"
Cohesion: 0.40
Nodes (6): Alembic for Database Migrations, FastAPI API Service, NiceGUI Web Service, PostgreSQL Production Database, Redis for Task Queuing, Background Worker Service

### Community 101 - "Identity and Audit Migration"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 102 - "Settings Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 103 - "Password TOTP Backup Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 104 - "Lesson Plans Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 105 - "AI Generation Results Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 107 - "TOTP Tests"
Cohesion: 0.53
Nodes (5): Any, test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps(), test_totp_rejects_the_same_or_earlier_counter_after_success(), test_totp_secret_is_unique_high_entropy_base32(), _totp_module()

### Community 108 - "Development Workflow Rules"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 110 - "CSRF Tests"
Cohesion: 0.60
Nodes (4): TestClient, test_csrf_cookie_is_signed_readable_and_not_httponly(), test_passkey_state_change_rejects_missing_csrf_and_wrong_origin(), test_recovery_rejects_malformed_signed_double_submit_token()

### Community 111 - "AI Key Rotation Tests"
Cohesion: 0.60
Nodes (4): CompletedProcess, _run(), test_bootstrap_cli_exposes_rotation_without_master_key_arguments(), test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets()

### Community 112 - "Calendar Tests"
Cohesion: 0.70
Nodes (4): _calendar(), test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic(), test_out_of_semester_week_number_and_text_are_both_empty(), test_semester_start_week_is_week_one_and_increments_each_monday()

### Community 113 - "Agent Dev Tools"
Cohesion: 0.67
Nodes (4): AGENTS.md 开发规则文件, codebase-memory MCP, Graphify 知识图谱工具, 搜索工具优先级

### Community 114 - "Save Status Module"
Cohesion: 0.67
Nodes (3): save_status(), SaveStatus, SaveState

### Community 115 - "Dev Environment Setup"
Cohesion: 0.67
Nodes (4): Docker Compose 开发环境配置, GitHub Actions 质量检查工作流, PostgreSQL, Redis

### Community 116 - "Child Manager Project"
Cohesion: 0.50
Nodes (4): Child Manager Project, Cloud Version, Daily Activity Plan Feature, Monorepo Structure

### Community 117 - "Core Domain Tables"
Cohesion: 0.50
Nodes (4): Age Groups Table, Class Teachers Table, Classes Table, Daily Activity Plans Table

### Community 118 - "Database Schema Concepts"
Cohesion: 0.50
Nodes (4): Composite Foreign Keys Concept, Kindergarten Isolation Concept, Kindergartens Table, Users Table

### Community 120 - "Backup Login Feature"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 122 - "Lesson Plan Contract Tests"
Cohesion: 0.83
Nodes (3): _contracts(), test_open_and_write_contracts_do_not_accept_tenant_or_ownership_mutation(), test_plan_snapshot_and_page_contracts_are_bounded_and_stable()

### Community 127 - "Migration Dependency Rules"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

### Community 131 - "Activity Plan UI Layout"
Cohesion: 0.67
Nodes (3): AI-Added Step Red Text, Structured Daily Activity Sections, Daily Activity Plan Word Layout

## Knowledge Gaps
- **153 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+148 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **99 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `班级与教师配置` (2× useful, score=1.352895454)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IdentityRepository` connect `Identity Backup Credentials` to `Token Management`, `Identity Session Queries`, `Admin Initialization and Keys`, `Identity Audit and Invitations`, `Migration Tests`, `Identity Auth Verification`, `Auth Throttle`, `TOTP Secret Encryption`, `WebAuthn Challenges`, `User Management Routes`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `ActorFixture` connect `Backup Enrollment Tests` to `Settings Permissions Tests`, `Credential Management Tests`, `Identity Audit and Invitations`, `Auth Throttle`, `Prompt Test Jobs API Tests`, `WebAuthn Auth Tests`, `AI Batch Generation Tests`, `AI Generation Pre-save Tests`, `AI Model Profiles Tests`, `Backup Maintenance Tests`, `TOTP Secret Encryption`, `AI Results Migration Tests`, `Provider Neutral AI Client`, `Secret Token Service`, `AI Audit Tests`, `AI Preview Lifecycle Tests`, `Invitation Tests`, `Job Message Schema`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `IdentityError` connect `Identity Session Queries` to `Settings and AI Profiles`, `Admin Initialization and Keys`, `Prompt Template Renderer`, `Auth and Export Contracts`, `Identity Audit and Invitations`, `Authentication Flow`, `TOTP Secret Encryption`, `WebAuthn Challenges`, `User Management Routes`, `Secret Token Service`, `Calendar Workday Client`, `Lesson Plan Service`, `Identity Auth Verification`, `FastAPI App Assembly`, `Audit Repository`, `Backup Maintenance Tests`, `Health Check Tests`, `Health Dependencies`, `CSRF Token Management`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `ActorFixture` (e.g. with `StaticIdentitySecretKeyProvider` and `IdentityService`) actually correct?**
  _`ActorFixture` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 134 inferred relationships involving `ContractModel` (e.g. with `AuditEventReference` and `IdentityAuditEventCode`) actually correct?**
  _`ContractModel` has 134 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `IdentityError` (e.g. with `create_app()` and `HealthDependencies`) actually correct?**
  _`IdentityError` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `IdentityRepository` (e.g. with `test_totp_counter_and_session_creation_roll_back_together()` and `test_identity_repository_exposes_atomic_backup_auth_operations()`) actually correct?**
  _`IdentityRepository` has 3 INFERRED edges - model-reasoned connections that need verification._