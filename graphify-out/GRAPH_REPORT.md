# Graph Report - child-manager  (2026-07-28)

## Corpus Check
- 344 files · ~204,854 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2923 nodes · 8220 edges · 261 communities (166 shown, 95 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 710 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9176d00c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Calendar Workday Service
- Settings Repository
- Prompt Test Routes
- Prompt Job Dispatcher
- Identity Backup Repository
- Settings API Routes
- AI Key Encryption
- Authentication Routes
- Identity Service
- Project Milestone Tags
- Authentication Flow Functions
- Development Milestones
- Admin Initialization Script
- Plan Routes
- Testing & Migration
- Backup Login User Stories
- API Main & Config
- Architecture Decisions
- Prompt Job Worker Test
- User Routes
- WebAuthn Challenges
- AI Model Profile Tests
- Database Migration Tests
- Identity Service Errors
- Backup Auth API Client
- WebAuthn Auth Tests
- Prompt Test Actors
- Auth Throttling
- Database Models
- Credential Management
- Login Throttling
- ADR & Milestones
- TOTP Secret Encryption
- Prompt Test Store
- Identity & Password Hashing
- Backup Login Design
- Public Entry & Passkey
- Data Model Design
- Backup Auth Data Model
- Schema Constraints
- AI Client Errors
- API Contract v1
- Data Model Docs
- AI Client Transport
- Security Threat Model
- Audit Repository
- Service Architecture
- FastAPI App Assembly
- Navigation Generation
- Auth Smoke Tests
- Worker & Backend Modules
- Backup Auth Tests
- Prompt Job API Tests
- Local Dev Profiles
- Backup Auth Isolation Tests
- Backup Maintenance Tests
- Shell Script Utilities
- Recovery Tests
- Health Check Tests
- Health Dependencies
- Prompt Test Store Methods
- Port Interfaces
- Job Status UI
- Token Management
- Contract Fingerprint Tests
- Identity Isolation Tests
- AI Key Rotation Tests
- Web Entry Point
- Job Recovery
- ADR: PostgreSQL Jobs
- Backup Login Spec
- Backup Login Research
- Invitation Tests
- OpenAPI Contract Tests
- Settings Permissions Tests
- ADR: AI Provider Neutral
- Credential Tests
- Prompt Settings UI Tests
- Auth Contract Tests
- Plan Editor UI
- ADR: Modular Monolith
- ADR: Word Export
- ADR: Calendar Degradable
- Backup Login Implementation Plan
- Prompt Repository Tests
- OpenAPI Configuration
- Backup Auth Contract Tests
- AI Client Tests
- Request ID Middleware
- BFF Proxy
- Database Session
- Client IP Resolution
- Settings Models
- Implementation Phases
- Workday Service Tests
- TOTP Primitives
- User Management Tests
- Secret Encryption Tests
- AI Prompts Migration
- Backup Login Migration Test
- OpenAPI Document Testing
- Passkey Migration
- Content Schema Validation
- AI Key Envelope
- AI Model URL Policy
- Prompt Catalog
- Security Events
- ADR Governance
- Passkey Expand Migration
- Secret Key Provider
- Lesson Plan Models
- Prompt Renderer
- Spec Kit Implementation
- CSRF Tokens
- Identity Audit Migration
- Settings Migration
- Password TOTP Migration
- Lesson Plans Migration
- M3A Spec Readiness
- Backup Auth Credentials
- Password TOTP Spec Quality
- Users Contract
- TOTP Implementation
- Feature Branch Script
- CSRF Testing
- AI Key Rotation CLI
- M0 Acceptance Gate
- Dependency Boundaries
- Lesson Plan Contract
- Calendar Fixture
- Fixed Clock
- Fake Job Broker
- Alembic Bootstrap
- Backup Auth State Models
- Identity M3A Migrations
- Foundation Migration
- Lease Expiration
- Backup Login Contract
- Spec Kit Templates
- Fake AI Client
- Child Manager App
- Worker App
- Contributing Guide
- Backend Capabilities
- Shared Contracts
- Prerequisites Script
- Setup Plan Script
- Setup Tasks Script
- Backup Auth Zero Leak
- Package Skeleton
- 测试要求
- Requirements Unit Tests
- Spec Kit Checklist
- Ambiguity Coverage Scan
- Q&A Incremental Writeback
- Spec Clarification
- Spec Charter Maintenance
- Charter Sync Impact
- Semantic Version Sync
- Append-Only Tasks
- Intent Gap Assessment
- Spec Kit Convergence
- Pre-Implementation Gate
- Phased Task Execution
- Phase One Data Model
- Phase Zero Research
- Spec Quality Iteration
- Feature Catalog Generation
- Dependency Acceptance Checks
- User Story Tasks
- Standardized Issue Creation
- GitHub De-duplication
- Spec Kit GitHub Issues
- Checklist Template
- Project Charter Template
- Same-Origin Cookie Auth
- API App
- Routers
- Components
- Web App
- Pages
- Scheduler
- Avoid Date Documents
- Codex Implementation Issue
- Common Baseline Branch
- Conflict Freeze
- Dual Agent Checklist
- GitHub Issue Creation
- Graphify Integrity Check
- Graphify Workspace Change Handling
- Independent Authorization Boundary
- Real-time Baseline Evidence
- M1 Exit Gate
- M1 Issue Structure
- Non-destructive Workspace Retention
- Non-target Production Deployment
- Read-only Cross Review
- Recommended Execution Order
- Shared Document Sync
- M1 Shared Parent Issue
- Startup Checklist Wording Clarification
- Execution Stop Condition
- T003 Shared Authorization & Branch Gate
- T004-T020 Implementation Tasks
- TDD-driven M1 Implementation
- Trae Implementation Sub-Issue
- 2026-07-14 Pre-Code Convergence Review
- Branch Operation Authorization Gate
- Canonical Phase State Consistency
- Cannot Enter Coding Now
- M0-G1 to M0-G8 Closed
- M1 Codex Implementation Sub-Issue
- M1 Parent-Child Issue Hierarchy
- WorkdayCacheRepository
- normalize_username
- test_ai_prompt_contracts.py
- Tasks (002 Password TOTP Backup Login)
- validate_prompt_variables
- test_lesson_plan_contract.py
- authenticated_session
- _render_prompt_test_run_schema
- ai_result_model

## God Nodes (most connected - your core abstractions)
1. `ActorFixture` - 167 edges
2. `csrf_headers()` - 154 edges
3. `ContractModel` - 148 edges
4. `IdentityError` - 131 edges
5. `IdentityRepository` - 129 edges
6. `SessionUser` - 127 edges
7. `IdentityService` - 103 edges
8. `AuditRepository` - 73 edges
9. `pytest` - 73 edges
10. `require_csrf()` - 64 edges

## Surprising Connections (you probably didn't know these)
- `一日活动计划需求面` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_020708_请根据现有文档_和旧仓库的文件思考如何撰写_docs_prd_lesson_management_m.md → docs/faq/combined-audit.md
- `ADR 直接文件核对` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260711_025449_哪些关键架构决策需要独立_adr_哪些已经确认_决策之间有什么依赖.md → docs/faq/combined-audit.md
- `校正后的数据模型边界` --semantically_similar_to--> `权威模型与契约收敛`  [INFERRED] [semantically similar]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md → docs/faq/combined-audit.md
- `test_repository_exposes_atomic_passkey_lifecycle_operations()` --indirect_call--> `IdentityRepository`  [INFERRED]
  tests/repository/test_identity_isolation.py → packages/backend/identity/repository.py
- `Speckit Tasks to Issues` --semantically_similar_to--> `Implementation Issue Template`  [INFERRED] [semantically similar]
  .agents/skills/speckit-taskstoissues/SKILL.md → .github/ISSUE_TEMPLATE/implementation.yml

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

## Communities (261 total, 95 thin omitted)

### Community 0 - "Calendar Workday Service"
Cohesion: 0.32
Nodes (35): PromptSpec, BaseModel, 固定提示词目录、输入与结果 Schema 路由。, _spec(), AiAreaGame, AiDailyReflection, AiGroupActivity, AiMorningActivity (+27 more)

### Community 1 - "Settings Repository"
Cohesion: 0.06
Nodes (49): settings_service(), IntegrityError, NoReturn, AgeGroupRecord, _ai_profile(), AreaInput, AreaRecord, ClassRecord (+41 more)

### Community 2 - "Prompt Test Routes"
Cohesion: 0.07
Nodes (36): prompt_service(), Dramatiq, Broker, UUID, 仅投递 job_id 的提示词测试分发边界。, RedisJobDispatcher, _job(), JobRecord (+28 more)

### Community 3 - "Prompt Job Dispatcher"
Cohesion: 0.05
Nodes (31): _backup_credential(), _backup_enrollment(), BackupCredentialRecord, BackupEnrollmentRecord, BackupRevocationResult, BackupSecurityEventRecord, ChallengeRecord, _credential() (+23 more)

### Community 4 - "Identity Backup Repository"
Cohesion: 0.08
Nodes (65): AgeGroup, AiModelProfile, AiModelServiceDependency, _age_group(), _ai_model(), _area(), _class(), create_ai_model_profile() (+57 more)

### Community 5 - "Settings API Routes"
Cohesion: 0.06
Nodes (56): AiKeyProvider, ai_model_service(), ArgumentParser, activate_initialization(), migrate_passkeys(), _native_url(), datetime, UUID (+48 more)

### Community 6 - "AI Key Encryption"
Cohesion: 0.14
Nodes (18): AuditRepository, UUID, InvitationRecord, IdentityError, IdentityService, ManagedUser, Exception, UUID (+10 more)

### Community 7 - "Authentication Routes"
Cohesion: 0.08
Nodes (54): _allowed_origins(), _loopback_aliases(), 同源 Cookie、WebAuthn、邀请、恢复与会话端点。, ContractModel, BaseModel, ExportReference, AdminCredentialRevocationResult, AuthenticationCredential (+46 more)

### Community 8 - "Identity Service"
Cohesion: 0.18
Nodes (34): _insert_job(), _insert_other_tenant_plan(), _insert_result(), _native_url(), _provision_dependencies(), TestClient, UUID, _result_values() (+26 more)

### Community 9 - "Project Milestone Tags"
Cohesion: 0.07
Nodes (40): Event, migrated_database(), MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds(), test_identity_migration_is_idempotent(), MonkeyPatch, settings_database(), test_age_group_seed_is_fixed_and_idempotent() (+32 more)

### Community 10 - "Authentication Flow Functions"
Cohesion: 0.21
Nodes (41): authenticate_with_password_and_totp(), authentication_start(), backup_authentication_status(), bootstrap_options(), bootstrap_verify(), _check_public_throttle(), _clear_public_throttle(), _credential() (+33 more)

### Community 11 - "Development Milestones"
Cohesion: 0.10
Nodes (33): _auth_throttle(), MemoryAuthThrottle, datetime, Redis, timedelta, 公开身份 ceremony 的来源限流公共 seam。, 按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。, 多进程 API 使用的 Redis 固定窗口实现。 (+25 more)

### Community 12 - "Admin Initialization Script"
Cohesion: 0.40
Nodes (10): _prepare_last_admin_recovery(), CompletedProcess, MonkeyPatch, UUID, _run_cli(), test_init_admin_activate_requires_two_distinct_pre_registered_approvers(), test_init_admin_cli_exposes_start_activate_and_migration_commands(), test_init_admin_start_creates_pending_account_and_one_time_secret_without_password() (+2 more)

### Community 13 - "Plan Routes"
Cohesion: 0.10
Nodes (42): current_session(), AuthenticatedSessionDependency, pytest, admin_client(), passkey_client(), MonkeyPatch, TestClient, 通过 FastAPI 身份依赖注入建立已 step-up 管理员，不借用密码登录。 (+34 more)

### Community 14 - "Testing & Migration"
Cohesion: 0.13
Nodes (20): Actor, build_prompt_test_executor(), Broker, register_actors(), build_redis_broker(), build_test_broker(), Broker, 生产 Redis 与确定性测试消息代理装配。 (+12 more)

### Community 15 - "Backup Login User Stories"
Cohesion: 0.09
Nodes (32): main(), AppSettings, global_security_ready(), BaseModel, 拒绝在非开发环境或非回环地址关闭 Cookie Secure。, 验证进程启动时的 Cookie 与监听地址组合。, JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。, validate_cookie_security() (+24 more)

### Community 16 - "API Main & Config"
Cohesion: 0.18
Nodes (32): archive_plan(), autosave_plan(), get_plan(), list_plans(), list_snapshots(), open_plan(), _plan(), CurrentSessionDependency (+24 more)

### Community 17 - "Architecture Decisions"
Cohesion: 0.10
Nodes (34): ChallengeBinding, ChallengeRecord, consume_challenge(), issue_challenge(), IssuedChallenge, datetime, WebAuthn ceremony challenge 的公共领域 seam。, 签发绑定上下文、五分钟有效且只保存摘要的 challenge。 (+26 more)

### Community 18 - "Prompt Job Worker Test"
Cohesion: 0.13
Nodes (16): AiClientError, RuntimeError, _native_url(), datetime, 提示词测试 Worker 的 PostgreSQL 权威状态适配器。, CurrentModelCallProfile, ProfileCallLimiter, PromptTestAuthorizer (+8 more)

### Community 19 - "User Routes"
Cohesion: 0.14
Nodes (20): _context(), FakeAuthorizer, FakeClient, FakeStore, _modules(), Any, datetime, UUID (+12 more)

### Community 20 - "WebAuthn Challenges"
Cohesion: 0.11
Nodes (19): BaseTransport, ProviderNeutralAiClient, Resolver, UUID, 按任务与尝试次数生成可复现的有界抖动，便于恢复与确定性测试。, retry_delay_seconds(), _executor(), AddStepStore (+11 more)

### Community 21 - "AI Model Profile Tests"
Cohesion: 0.08
Nodes (34): Cloud Only Product, Kindergarten Isolation Boundary, Separate Web API Worker Modular Monolith, Web API Worker Service Boundaries, Recoverable Idempotent Async Execution, PostgreSQL Authoritative Job State, API Authoritative Authorization, Same Origin HttpOnly Cookie Authentication (+26 more)

### Community 22 - "Database Migration Tests"
Cohesion: 0.07
Nodes (33): Cross-Artifact Consistency Analysis, Speckit Analyze, Requirements Quality Checks, Speckit Checklist, Incremental Clarification Integration, Speckit Clarify, Constitution Consistency Propagation, Speckit Constitution (+25 more)

### Community 23 - "Identity Service Errors"
Cohesion: 0.06
Nodes (50): lesson_plan_service(), map_timor_payload(), AsyncBaseTransport, date, TimorWorkdayClient, WorkdayResult, Any, date (+42 more)

### Community 24 - "Backup Auth API Client"
Cohesion: 0.19
Nodes (32): activate(), create_user(), credential_revoke(), credentials(), deactivate(), get_user(), _invitation(), invitation_issue() (+24 more)

### Community 25 - "WebAuthn Auth Tests"
Cohesion: 0.07
Nodes (32): 最终不可移动文档基线, 2026-07-13 编码前修复方案, 有序门禁修复, 历史清理独立授权, M0 初始阻塞判断, M0 门禁关闭证据, 2026-07-13 编码前审查报告, 隐私历史清理证据 (+24 more)

### Community 26 - "Prompt Test Actors"
Cohesion: 0.27
Nodes (7): save_status(), SaveStatus, build_plan_editor_page(), 不依赖 AI 的一日活动计划日历、列表与六栏目编辑页。, 构建教案编辑页，并让归档能力变化立即反映到控件。, NiceGUI, SaveState

### Community 27 - "Auth Throttling"
Cohesion: 0.10
Nodes (31): Dev Handoff 2026-07-24, Child Manager Roadmap, 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。, M5 完成后到 M4 的当前依赖路径是什么？, M0 Shared Baseline, M1 Engineering Skeleton, M2 Authentication Authorization, M3 Initial Settings (+23 more)

### Community 28 - "Database Models"
Cohesion: 0.18
Nodes (29): alias, clear_prompt_tests(), create_prompt_test(), _definition(), get_prompt(), get_prompt_test(), get_prompt_version(), list_prompt_tests() (+21 more)

### Community 29 - "Credential Management"
Cohesion: 0.14
Nodes (37): csrf_headers(), _base64url(), _credential(), MonkeyPatch, TestClient, _registration_credential(), test_authentication_options_are_username_less_and_browser_ready(), test_authentication_options_do_not_increment_failure_limit() (+29 more)

### Community 30 - "Login Throttling"
Cohesion: 0.11
Nodes (16): AiBatchRequest, AiGenerationRequest, AiGroupActivityStep, apply_ai_area_result(), DailyReflection, GroupActivityStep, GroupActivityStepCandidate, LessonPlanReference (+8 more)

### Community 31 - "ADR & Milestones"
Cohesion: 0.19
Nodes (9): ChallengePurpose, StrEnum, AuthResult, _challenge_digest(), _client_challenge(), _decode_base64url(), Any, datetime (+1 more)

### Community 32 - "TOTP Secret Encryption"
Cohesion: 0.12
Nodes (22): _aad(), decrypt_totp_secret(), decrypt_totp_secret_with_provider(), encrypt_totp_secret(), encrypt_totp_secret_with_provider(), FileIdentitySecretKeyProvider, Path, UUID (+14 more)

### Community 33 - "Prompt Test Store"
Cohesion: 0.07
Nodes (29): AI Preview Adoption Transaction, Background Job State Machine, PostgreSQL Job Authority, Retry and Idempotency Semantics, Child Manager Daily Activity API, Identity and Settings Endpoints, Plans, Jobs, and Exports Endpoints, API v1 Contract (+21 more)

### Community 34 - "Identity & Password Hashing"
Cohesion: 0.10
Nodes (28): Graphify, Milestone M2, Milestone M3, Milestone M3A (Password/TOTP), Milestone M4, Milestone M5, Milestone M6, Milestone M7 (+20 more)

### Community 35 - "Backup Login Design"
Cohesion: 0.17
Nodes (10): _digest(), MemoryLoginThrottle, datetime, Redis, timedelta, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision (+2 more)

### Community 36 - "Public Entry & Passkey"
Cohesion: 0.19
Nodes (21): ActorFixture, TestClient, test_admin_is_restricted_until_complete_backup_enrollment(), test_backup_status_and_enrollment_require_authentication(), test_enrollment_requires_password_and_totp_together_and_is_single_use(), test_expired_enrollment_cannot_enable_backup_auth(), test_new_enrollment_invalidates_the_previous_pending_enrollment(), test_replacing_enabled_material_revokes_only_related_backup_sessions() (+13 more)

### Community 37 - "Data Model Design"
Cohesion: 0.08
Nodes (25): 本地开发环境规范, 仅回环开发依赖, 生产拓扑延后, 工作树资源隔离, M1 工程骨架, M1 Issue 执行记录, M1 质量门禁, 认证授权审计基线 (+17 more)

### Community 38 - "Backup Auth Data Model"
Cohesion: 0.31
Nodes (13): admin_session(), CurrentSessionDependency, SimpleNamespace, _provision_associated_teacher(), TestClient, UUID, _session_for(), teacher_client() (+5 more)

### Community 39 - "Schema Constraints"
Cohesion: 0.40
Nodes (12): _change_actor_to_teacher(), _enable_backup(), _identity_service(), _login_with_backup(), _native_url(), TestClient, test_admin_cannot_disable_required_backup_authentication(), test_backup_maintenance_and_security_events_require_authentication() (+4 more)

### Community 40 - "AI Client Errors"
Cohesion: 0.19
Nodes (10): datetime, Protocol, UUID, 只接收 job_id 的 Dramatiq actor 与 PostgreSQL 恢复扫描。, 按 PostgreSQL 权威状态重投 pending/过期租约任务。, recover_prompt_test_jobs(), RecoveryStore, Any (+2 more)

### Community 41 - "API Contract v1"
Cohesion: 0.19
Nodes (12): canonical_request_fingerprint(), 计算覆盖路由、实际资源与语义输入的 canonical SHA-256。, Any, _schema(), test_model_and_job_contracts_freeze_revision_and_stable_errors(), test_prompt_test_contract_exposes_only_redacted_input_summary(), test_prompt_test_fingerprint_changes_across_prompt_codes(), test_runtime_exposes_the_complete_frozen_m4_route_surface() (+4 more)

### Community 42 - "Data Model Docs"
Cohesion: 0.11
Nodes (25): backup_auth_api_request(), backup_login_api_request(), backup_reauthentication_api_request(), plan_api_request(), NiceGUI 服务端 BFF 客户端的公开接缝。, 以请求正文提交两项备用因素，不把秘密放入 URL。, 为当前备用会话取得仅可新增通行密钥的短时证明。, 读取本人最近 20 条内建安全事件，不产生已读状态。 (+17 more)

### Community 43 - "AI Client Transport"
Cohesion: 0.31
Nodes (15): create_app(), HealthDependencies, check(), dependencies(), Path, test_database_failure_returns_stable_503_code(), test_default_dependencies_check_real_local_runtime(), test_each_optional_dependency_only_degrades_ready_response() (+7 more)

### Community 44 - "Security Threat Model"
Cohesion: 0.24
Nodes (12): class_areas_page_text(), settings_page_text(), BrowserActor, _free_port(), _m3_services(), MonkeyPatch, Popen, _seed_browser_actors() (+4 more)

### Community 45 - "Audit Repository"
Cohesion: 0.15
Nodes (21): navigation_for_capabilities(), 按 API capabilities 生成导航。, login_page_text(), users_page_text(), BrowserContext, Page, _add_virtual_authenticator(), _auth_cookie_names() (+13 more)

### Community 46 - "Service Architecture"
Cohesion: 0.14
Nodes (25): DeclarativeBase, AuditEvent, Base, AccountInvitation, AccountRecoveryRequest, BackupAuthCredential, BackupAuthEnrollment, BootstrapInitialization (+17 more)

### Community 47 - "FastAPI App Assembly"
Cohesion: 0.36
Nodes (17): FailingDispatcher, prompt_job_client(), _provision_model_and_version(), Any, TestClient, _resolver(), test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure(), test_draft_version_can_be_tested_before_publication() (+9 more)

### Community 48 - "Navigation Generation"
Cohesion: 0.14
Nodes (14): _compose_config(), Any, 双实现本地开发档位的 Compose 合同。, test_compose_accepts_temporary_image_overrides(), test_compose_uses_selected_local_profile(), test_test_database_url_requires_an_explicit_profile(), block_external_network(), isolated_database_url() (+6 more)

### Community 49 - "Auth Smoke Tests"
Cohesion: 0.30
Nodes (10): AiGenerationResultRecord, AiGenerationResultRepository, _json_object(), _optional_uuid(), Any, datetime, 同园隔离的 AI 生成结果 Repository。, _record() (+2 more)

### Community 50 - "Worker & Backend Modules"
Cohesion: 0.30
Nodes (3): PostgresPromptTestStore, Any, UUID

### Community 52 - "Prompt Job API Tests"
Cohesion: 0.12
Nodes (26): normalize_phone(), normalize_username(), hash_password(), password_needs_rehash(), password_violations(), Path, verify_password(), _weak_passwords() (+18 more)

### Community 53 - "Local Dev Profiles"
Cohesion: 0.12
Nodes (24): _area_complete(), content_completeness(), EditableContent, _group_activity_complete(), _morning_activity_complete(), _morning_talk_complete(), parse_content_for_editing(), Any (+16 more)

### Community 54 - "Backup Auth Isolation Tests"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 55 - "Backup Maintenance Tests"
Cohesion: 0.14
Nodes (29): identity_service(), _digest(), issue_secret(), IssuedSecret, StrEnum, 生成 256 位一次性秘密，持久化对象中只保留 purpose 绑定摘要。, 以常量时间比较 purpose 绑定摘要。, SecretPurpose (+21 more)

### Community 56 - "Shell Script Utilities"
Cohesion: 0.15
Nodes (15): _error_response(), FastAPI, Request, UUID, FastAPI 应用装配、统一异常转换与健康端点。, _request_id(), JSONResponse, ErrorResponse (+7 more)

### Community 57 - "Recovery Tests"
Cohesion: 0.36
Nodes (5): AuditEventReference, IdentityAuditMetadata, 身份阶段的稳定审计事件代码与最小资源引用。, 身份审计只允许承载最小、严格类型化的非秘密元数据。, ResourceReference

### Community 58 - "Health Check Tests"
Cohesion: 0.26
Nodes (12): _pinned_url(), Any, OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。, _addresses(), AiUrlPolicyError, Resolver, ValueError, AI 模型地址的保存时与连接前 SSRF 防护。 (+4 more)

### Community 59 - "Health Dependencies"
Cohesion: 0.14
Nodes (29): create_completed_ai_preview(), provision_enabled_ai_model(), TestClient, UUID, _event(), TestClient, test_ai_audit_event_codes_cover_creation_retries_result_reject_and_adopt(), test_generation_reject_adopt_and_retry_write_sanitized_audit_rows() (+21 more)

### Community 60 - "Prompt Test Store Methods"
Cohesion: 0.23
Nodes (14): _ai_unconfigured(), build_health_dependencies(), _calendar_library_available(), _database_check(), _file_check(), _path_check(), Path, 从进程环境构造真实、无副作用的本地就绪检查。 (+6 more)

### Community 61 - "Port Interfaces"
Cohesion: 0.25
Nodes (11): main(), 仅绑定回环地址的 NiceGUI Web 入口。, _require_loopback(), _validate_cookie_security(), configure_logging(), EventDict, 递归清除 Web 日志中的凭证和内部 URL。, _redact() (+3 more)

### Community 62 - "Job Status UI"
Cohesion: 0.18
Nodes (11): get_job(), AdminSessionDependency, UUID, _job(), JobQueryServiceDependency, JobStatus, derive_batch_projection(), Job (+3 more)

### Community 63 - "Token Management"
Cohesion: 0.31
Nodes (12): _native_url(), NoCallExpectedClient, TestClient, UUID, _snapshot_count(), test_batch_and_nonfailed_ai_jobs_reject_explicit_retry(), test_cross_tenant_failed_job_is_hidden_from_retry(), test_expiration_scheduler_transitions_due_previews_once() (+4 more)

### Community 64 - "Contract Fingerprint Tests"
Cohesion: 0.35
Nodes (10): _candidate(), FakeStore, _modules(), Any, UUID, test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it(), test_rotation_dry_run_and_repeated_batch_are_zero_write(), test_rotation_uses_stable_cursor_and_does_not_change_call_revision() (+2 more)

### Community 65 - "Identity Isolation Tests"
Cohesion: 0.21
Nodes (9): AiClient, Clock, DependencyCheck, JobBroker, datetime, Protocol, UUID, M1 外部边界所需的最小 Protocol。 (+1 more)

### Community 66 - "AI Key Rotation Tests"
Cohesion: 0.40
Nodes (9): ai_admin_client(), _profile_payload(), Any, TestClient, _resolver(), test_admin_creates_write_only_masked_profile_and_cannot_read_key(), test_call_fields_increment_revision_but_display_and_limits_do_not(), test_disable_preserves_profile_and_default_switch_is_tenant_local() (+1 more)

### Community 67 - "Web Entry Point"
Cohesion: 0.33
Nodes (13): _base64url(), _create_teacher(), _issue(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes(), test_invitation_is_single_use_reissuable_and_revocable() (+5 more)

### Community 68 - "Job Recovery"
Cohesion: 0.40
Nodes (13): _assert_operation_contract(), _canonical_schema(), _effective_security(), _operations(), _parameter_shape(), Any, 运行时 OpenAPI 与冻结身份契约的一致性门禁。, _request_schema() (+5 more)

### Community 69 - "ADR: PostgreSQL Jobs"
Cohesion: 0.28
Nodes (11): validate_prompt_result_schema(), _contract(), Any, ModuleType, M6 AI 固定结果与输入最小化 RED 验收。, test_area_result_cannot_own_areas_and_adoption_reuses_validated_input(), test_daily_reflection_is_nonempty_nfkc_and_limited_by_unicode_code_points(), test_group_activity_results_are_closed_and_add_step_index_is_not_clamped() (+3 more)

### Community 70 - "Backup Login Spec"
Cohesion: 0.34
Nodes (13): hash_refresh_token(), _base64url(), _insert_credential(), _native_url(), MonkeyPatch, TestClient, UUID, _registration_credential() (+5 more)

### Community 71 - "Backup Login Research"
Cohesion: 0.29
Nodes (11): _children(), _contract(), Any, ModuleType, M6 教案 AI 公共契约的 RED 验收。, test_ai_child_succeeded_is_not_a_valid_batch_completion_state(), test_batch_job_projects_zero_attempts_and_rejects_execution_shape(), test_batch_status_is_derived_only_from_exactly_four_children() (+3 more)

### Community 72 - "Invitation Tests"
Cohesion: 0.19
Nodes (7): _job_status_module(), Any, MonkeyPatch, test_controls_have_keyboard_focus_and_error_label_associations(), test_job_status_recovers_configuration_change_with_chinese_action(), test_job_status_refreshes_until_terminal_and_restores_after_page_reload(), test_settings_controls_call_model_prompt_and_job_public_api_seams()

### Community 73 - "OpenAPI Contract Tests"
Cohesion: 0.14
Nodes (10): Alembic, Any, Column, _timestamps(), upgrade(), Any, Column, _timestamps() (+2 more)

### Community 74 - "Settings Permissions Tests"
Cohesion: 0.21
Nodes (7): APIRoute, Any, _resolve(), _runtime_routes(), test_auth_success_and_logout_lock_two_raw_cookie_headers(), test_runtime_auth_router_matches_frozen_passkey_paths(), test_runtime_auth_success_statuses_match_frozen_contract()

### Community 75 - "ADR: AI Provider Neutral"
Cohesion: 0.24
Nodes (10): AI, Authentication, Authorization, Branch: dev, Branch: docs, Branch: main, PostgreSQL, Redis (+2 more)

### Community 76 - "Credential Tests"
Cohesion: 0.30
Nodes (9): _modules(), Any, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_call_configuration_change_set_matches_the_frozen_revision_rules(), test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup(), test_model_reads_and_writes_are_tenant_scoped(), test_prompt_run_frozen_fields_cannot_be_updated() (+1 more)

### Community 77 - "Prompt Settings UI Tests"
Cohesion: 0.29
Nodes (9): _apply_operation_contract(), configure_openapi(), _no_content_response(), _operation(), Any, FastAPI, M2 运行时 OpenAPI 的集中契约装配。, 返回缓存后的 M2 运行时 OpenAPI 生成器。 (+1 more)

### Community 78 - "Auth Contract Tests"
Cohesion: 0.20
Nodes (13): candidate_totp_counters(), _counter(), generate_totp(), generate_totp_secret(), _hotp(), RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。, 生成认证器广泛兼容的 160 位无填充 Base32 种子。, 返回当前时间步及相邻一个时间步，按 counter 递增排序。 (+5 more)

### Community 79 - "Plan Editor UI"
Cohesion: 0.24
Nodes (7): Any, _resolve(), _runtime_routes(), test_backup_contract_marks_request_and_one_time_response_secrets(), test_runtime_router_exposes_the_user_story_2_endpoints(), test_runtime_router_matches_the_frozen_backup_contract(), test_runtime_user_story_2_openapi_matches_frozen_security_and_responses()

### Community 80 - "ADR: Modular Monolith"
Cohesion: 0.44
Nodes (10): _modules(), Any, _resolver(), test_client_caps_retry_after_at_sixty_seconds(), test_client_errors_are_stable_and_never_include_key_or_prompt(), test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin(), test_client_posts_openai_compatible_request_with_fixed_limits(), test_client_rejects_redirects_without_following_them() (+2 more)

### Community 81 - "ADR: Word Export"
Cohesion: 0.22
Nodes (7): API 请求 ID 与追踪 ID 中间件。, _request_id(), RequestContextMiddleware, ASGIApp, Receive, Scope, Send

### Community 82 - "ADR: Calendar Degradable"
Cohesion: 0.29
Nodes (9): BffResponse, proxy_request(), AsyncBaseTransport, 按固定 allowlist 转发请求，并保留响应原始多值头。, MonkeyPatch, test_proxy_ignores_process_proxy_environment(), test_proxy_preserves_auth_set_cookie_as_raw_headers(), test_proxy_preserves_request_and_rebuilds_client_ip() (+1 more)

### Community 83 - "Backup Login Implementation Plan"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 84 - "Prompt Repository Tests"
Cohesion: 0.33
Nodes (8): Collection, parse_trusted_bff_peers(), 只接受显式配置的回环 BFF socket peer。, resolve_client_ip(), test_configured_loopback_bff_peer_can_supply_internal_client_ip(), test_non_loopback_peer_cannot_be_configured_as_trusted_bff(), test_trusted_bff_peers_are_empty_until_explicitly_configured(), test_untrusted_peer_cannot_supply_internal_client_ip()

### Community 85 - "OpenAPI Configuration"
Cohesion: 0.38
Nodes (6): datetime, _session(), test_backup_reauthentication_only_authorizes_add_passkey_for_five_minutes(), test_expired_backup_reauthentication_cannot_add_passkey(), test_recent_webauthn_proof_satisfies_high_risk_identity_boundary(), test_restricted_enrollment_session_cannot_enter_business_routes()

### Community 86 - "Backup Auth Contract Tests"
Cohesion: 0.29
Nodes (9): AiTaskCode, JsonValue, canonical_json_sha256(), generation_input_sha256(), 对 JSON 值进行稳定序列化并计算 SHA-256。, 计算逐任务实际输入哈希。      ``server_input`` 只应包含该任务白名单内的服务端输入。采用预览时，调用方必须复用任务     创建时冻结的, section_sha256(), test_generation_input_hash_reuses_frozen_teacher_context_and_current_server_input() (+1 more)

### Community 87 - "AI Client Tests"
Cohesion: 0.36
Nodes (9): AgeGroup, AiModelProfile, AiModelProfileCapability, ClassArea, ClassRoom, ClassTeacher, 首期必要设置的 SQLAlchemy 模型。, Semester (+1 more)

### Community 88 - "Request ID Middleware"
Cohesion: 0.29
Nodes (6): _module(), MonkeyPatch, test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls(), test_local_result_wins_conflict_and_uses_one_hour_cache(), test_timor_client_enforces_one_total_deadline(), test_unsupported_local_calendar_range_softly_falls_back_to_online()

### Community 89 - "BFF Proxy"
Cohesion: 0.22
Nodes (9): 纵深防御, 紧急恢复双人控制, 最小权限导出, 密码与 TOTP 备用登录, 抗钓鱼主认证, 受限公网唯一入口, 安全威胁模型, AGENTS 规则差距查询 (+1 more)

### Community 90 - "Database Session"
Cohesion: 0.39
Nodes (8): _context(), _encryption_module(), Any, Path, test_development_key_provider_requires_owner_only_file_outside_repository(), test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution(), test_totp_secret_envelope_round_trips_with_random_96_bit_nonce(), test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce()

### Community 91 - "Client IP Resolution"
Cohesion: 0.36
Nodes (6): Any, Column, 建立 AI 模型、提示词与 PostgreSQL 权威任务基础。, _seed_defaults(), _timestamps(), upgrade()

### Community 92 - "Settings Models"
Cohesion: 0.46
Nodes (7): Script, _backup_revision(), MonkeyPatch, test_backup_auth_migration_creates_isolated_credentials_and_enrollments(), test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(), test_backup_auth_revision_follows_settings_and_precedes_lesson_plans(), test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade()

### Community 93 - "Implementation Phases"
Cohesion: 0.39
Nodes (7): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_document_is_valid_31(), test_openapi_keeps_nicegui_as_the_only_browser_entry(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 94 - "Workday Service Tests"
Cohesion: 0.54
Nodes (7): _assert_passkey_revisions_exist(), _native_url(), MonkeyPatch, test_contract_removes_password_data_and_downgrade_recreates_only_empty_columns(), test_expand_moves_existing_accounts_to_enrollment_and_revokes_old_sessions(), test_passkey_migration_has_explicit_expand_and_contract_boundaries(), _user_columns()

### Community 95 - "TOTP Primitives"
Cohesion: 0.54
Nodes (7): _contracts(), _schemas(), test_completeness_is_independent_from_progressive_schema_validation(), test_empty_v1_content_supports_progressive_manual_editing(), test_reflection_is_nfkc_normalized_and_limited_to_200_codepoints(), test_statement_and_question_punctuation_are_strictly_chinese(), test_unknown_fields_and_unknown_content_versions_are_not_silently_coerced()

### Community 96 - "User Management Tests"
Cohesion: 0.39
Nodes (7): _module(), Any, Path, test_ai_key_envelope_rejects_tampering_and_cross_profile_substitution(), test_ai_key_envelope_round_trips_with_random_96_bit_nonce(), test_file_key_provider_requires_owner_only_files_outside_repository(), test_static_key_provider_reads_old_key_but_writes_with_active_key()

### Community 97 - "Secret Encryption Tests"
Cohesion: 0.57
Nodes (7): _module(), Any, _resolver(), test_policy_accepts_only_allowlisted_public_https_and_checks_every_address(), test_policy_detects_dns_rebinding_before_connect(), test_policy_rejects_non_https_and_non_public_networks(), test_policy_requires_explicit_server_allowlist()

### Community 98 - "AI Prompts Migration"
Cohesion: 0.43
Nodes (7): _module(), Any, test_catalog_assigns_task_specific_minimum_variable_whitelists(), test_catalog_freezes_seven_codes_whitelists_schemas_and_hashes(), test_catalog_input_validation_excludes_teacher_identity_and_unknown_fields(), test_catalog_result_schemas_are_strict(), test_catalog_result_schemas_match_the_frozen_openapi_shapes()

### Community 99 - "Backup Login Migration Test"
Cohesion: 0.22
Nodes (14): authentication_verify(), _clear_auth_cookies(), _cookie_secure(), csrf(), me(), _payload(), Response, SettingsServiceDependency (+6 more)

### Community 100 - "OpenAPI Document Testing"
Cohesion: 0.18
Nodes (9): prompt_test_status(), PromptTestStatus, 异步提示词测试的稳定中文状态与无障碍语义。, should_poll(), build_ai_prompt_settings_section(), prompt_edit_version_id(), prompt_test_record_text(), 刷新时优先恢复未发布草稿，避免用已发布正文覆盖编辑态。 (+1 more)

### Community 101 - "Passkey Migration"
Cohesion: 0.52
Nodes (5): Any, Column, _tenant_identity_columns(), _timestamps(), upgrade()

### Community 102 - "Content Schema Validation"
Cohesion: 0.48
Nodes (6): DailyActivityPlan, DailyActivityPlanAuthor, DailyActivityPlanSnapshot, 一日活动计划 SQLAlchemy 模型。, Timestamped, WorkdayCache

### Community 103 - "AI Key Envelope"
Cohesion: 0.29
Nodes (7): Child Manager Project Constitution, Fact Source and Scope Fidelity, Service Boundary and Unidirectional Dependency, Kindergarten Isolation and Server Authorization, Authoritative State, Transaction and Recoverability, Teacher Control, AI and Word Fidelity, Executable Verification and Real Evidence

### Community 104 - "AI Model URL Policy"
Cohesion: 0.48
Nodes (6): _module(), Any, test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(), test_renderer_fails_for_missing_variable_before_external_call(), test_renderer_rejects_every_non_frozen_placeholder_form(), test_renderer_uses_stable_json_and_never_recursively_renders_values()

### Community 105 - "Prompt Catalog"
Cohesion: 0.40
Nodes (6): Docker Compose 开发环境配置, GitHub Actions 质量检查工作流, PostgreSQL, Pyright, Redis, Ruff

### Community 106 - "Security Events"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 107 - "ADR Governance"
Cohesion: 0.36
Nodes (4): Any, datetime, UUID, StatefulStore

### Community 108 - "Passkey Expand Migration"
Cohesion: 0.43
Nodes (3): job_query_service(), JobQueryService, UUID

### Community 109 - "Secret Key Provider"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 111 - "Prompt Renderer"
Cohesion: 0.53
Nodes (5): Any, test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps(), test_totp_rejects_the_same_or_earlier_counter_after_success(), test_totp_secret_is_unique_high_entropy_base32(), _totp_module()

### Community 112 - "Spec Kit Implementation"
Cohesion: 0.40
Nodes (5): Main Docs Dev Branch Responsibilities, Design to Implement Workflow, Independent Implementation Boundaries, Read Only Cross Review, Retired Dual Agent Protocol

### Community 114 - "Identity Audit Migration"
Cohesion: 0.60
Nodes (4): TestClient, test_csrf_cookie_is_signed_readable_and_not_httponly(), test_passkey_state_change_rejects_missing_csrf_and_wrong_origin(), test_recovery_rejects_malformed_signed_double_submit_token()

### Community 115 - "Settings Migration"
Cohesion: 0.60
Nodes (4): CompletedProcess, _run(), test_bootstrap_cli_exposes_rotation_without_master_key_arguments(), test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets()

### Community 116 - "Password TOTP Migration"
Cohesion: 0.70
Nodes (4): _calendar(), test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic(), test_out_of_semester_week_number_and_text_are_both_empty(), test_semester_start_week_is_week_one_and_increments_each_monday()

### Community 117 - "Lesson Plans Migration"
Cohesion: 0.67
Nodes (4): AGENTS.md 开发规则文件, codebase-memory MCP, Graphify 知识图谱工具, 搜索工具优先级

### Community 118 - "M3A Spec Readiness"
Cohesion: 0.42
Nodes (8): NiceGUI 页面与同源 API BFF 装配。, register_web(), api_request(), post_same_origin(), register_class_area_pages(), register_plan_pages(), register_settings_pages(), register_users_page()

### Community 119 - "Backup Auth Credentials"
Cohesion: 0.50
Nodes (4): Age Groups Table, Class Teachers Table, Classes Table, Daily Activity Plans Table

### Community 120 - "Password TOTP Spec Quality"
Cohesion: 0.50
Nodes (4): Composite Foreign Keys Concept, Kindergarten Isolation Concept, Kindergartens Table, Users Table

### Community 121 - "Users Contract"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 122 - "TOTP Implementation"
Cohesion: 0.50
Nodes (4): Backup Login Specification Quality Checklist, Password and TOTP Backup Login Feature, Phishing-Resistant Primary Path, Three Backup Login User Stories

### Community 128 - "M0 Acceptance Gate"
Cohesion: 1.00
Nodes (3): 教案基础先于 AI, M5 先于 M4 的固定顺序, 0006 到 0007 迁移依赖

### Community 131 - "Lesson Plan Contract"
Cohesion: 0.67
Nodes (3): AI-Added Step Red Text, Structured Daily Activity Sections, Daily Activity Plan Word Layout

### Community 256 - "validate_prompt_variables"
Cohesion: 0.67
Nodes (4): prompt_spec(), Any, validate_prompt_result(), validate_prompt_variables()

### Community 257 - "test_lesson_plan_contract.py"
Cohesion: 0.83
Nodes (3): _contracts(), test_open_and_write_contracts_do_not_accept_tenant_or_ownership_mutation(), test_plan_snapshot_and_page_contracts_are_bounded_and_stable()

### Community 258 - "authenticated_session"
Cohesion: 0.67
Nodes (3): authenticated_session(), IdentityServiceDependency, Cookie

### Community 259 - "_render_prompt_test_run_schema"
Cohesion: 1.00
Nodes (3): JsonSchemaValue, _render_prompt_test_run_schema(), _render_union_as_one_of()

### Community 260 - "ai_result_model"
Cohesion: 0.67
Nodes (3): ai_result_model(), BaseModel, 按冻结的 Schema 代码取得结果模型。

## Knowledge Gaps
- **167 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+162 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **95 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `班级与教师配置` (2× useful, score=1.352895454)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `pytest` connect `Plan Routes` to `test_lesson_plan_contract.py`, `Settings Repository`, `Prompt Job Dispatcher`, `Identity Backup Repository`, `AI Key Encryption`, `Identity Service`, `Project Milestone Tags`, `Development Milestones`, `Admin Initialization Script`, `Testing & Migration`, `Backup Login User Stories`, `Architecture Decisions`, `User Routes`, `WebAuthn Challenges`, `Credential Management`, `TOTP Secret Encryption`, `Identity & Password Hashing`, `Public Entry & Passkey`, `Backup Auth Data Model`, `Schema Constraints`, `Data Model Docs`, `AI Client Transport`, `Security Threat Model`, `Audit Repository`, `FastAPI App Assembly`, `Navigation Generation`, `Prompt Job API Tests`, `Local Dev Profiles`, `Backup Maintenance Tests`, `Shell Script Utilities`, `Token Management`, `Contract Fingerprint Tests`, `AI Key Rotation Tests`, `Web Entry Point`, `ADR: PostgreSQL Jobs`, `Backup Login Spec`, `Backup Login Research`, `Invitation Tests`, `Settings Permissions Tests`, `Credential Tests`, `ADR: Modular Monolith`, `ADR: Calendar Degradable`, `Backup Login Implementation Plan`, `Prompt Repository Tests`, `OpenAPI Configuration`, `Request ID Middleware`, `Database Session`, `Settings Models`, `Workday Service Tests`, `TOTP Primitives`, `User Management Tests`, `Secret Encryption Tests`, `AI Prompts Migration`, `AI Model URL Policy`, `Prompt Catalog`, `Lesson Plan Models`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Why does `IdentityError` connect `AI Key Encryption` to `Settings Repository`, `authenticated_session`, `Prompt Test Routes`, `Settings API Routes`, `Authentication Routes`, `Authentication Flow Functions`, `Architecture Decisions`, `Identity Service Errors`, `Backup Auth API Client`, `ADR & Milestones`, `TOTP Secret Encryption`, `Schema Constraints`, `AI Client Transport`, `Prompt Job API Tests`, `Backup Maintenance Tests`, `Shell Script Utilities`, `Prompt Test Store Methods`, `Auth Contract Tests`, `OpenAPI Configuration`, `Backup Login Migration Test`, `Passkey Expand Migration`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `IdentityRepository` connect `Prompt Job Dispatcher` to `TOTP Secret Encryption`, `Settings API Routes`, `AI Key Encryption`, `Project Milestone Tags`, `Development Milestones`, `Auth Contract Tests`, `Architecture Decisions`, `Prompt Job API Tests`, `Backup Auth API Client`, `ADR & Milestones`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `ActorFixture` (e.g. with `StaticIdentitySecretKeyProvider` and `IdentityService`) actually correct?**
  _`ActorFixture` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 134 inferred relationships involving `ContractModel` (e.g. with `AuditEventReference` and `IdentityAuditEventCode`) actually correct?**
  _`ContractModel` has 134 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `IdentityError` (e.g. with `create_app()` and `HealthDependencies`) actually correct?**
  _`IdentityError` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `IdentityRepository` (e.g. with `test_totp_counter_and_session_creation_roll_back_together()` and `test_identity_repository_exposes_atomic_backup_auth_operations()`) actually correct?**
  _`IdentityRepository` has 3 INFERRED edges - model-reasoned connections that need verification._