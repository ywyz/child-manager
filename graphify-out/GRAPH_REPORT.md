# Graph Report - .  (2026-08-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 5327 nodes · 15280 edges · 313 communities (261 shown, 52 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 1465 edges (avg confidence: 0.58)
- Token cost: 19,110 input · 33,347 output

## Graph Freshness
- Built from commit: `d81791fd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- AI Services Events
- Workday Calendar Client
- DOCX Text Extraction
- Identity & Auth Service
- Identity Backup Repository
- Prompt Template Renderer
- Desktop Main Window
- System Architecture & ADRs
- Prompt Schema Catalog
- Word Export Service
- AI Runtime Adapter
- Worker Job Runners
- Settings API Router
- Jobs API Router
- AI Key Encryption
- Daily Plan Export
- App Bootstrap Startup
- WebAuthn Authentication Tests
- Prompts API Router
- Batch Job Query
- Identity Contract Models
- Observability Task DTOs
- Database Models Migrations
- TOTP Secret Encryption
- AI Generation Coordinator
- Desktop Feature Evidence
- Branch Strategy & Issues
- Word Export Job Store
- AI Job Execution
- AI Model Key Management
- Redis Job Message Contract
- Architecture & Audit Docs
- Development Toolchain Rules
- Passkey Test Helpers
- Daily Plan Page UI
- Admin Initialization CLI
- AI Retry Policy
- Prompt Test Job Tests
- First Run Plan Tests
- Prompt Test Store
- Auth API Router
- AI Preview Adoption Tests
- Provider-Neutral AI Client
- Domain Entity Catalog
- WebAuthn Challenge Store
- Exports API Router
- Export Flow Tests
- Spec Kit Skills
- Backup Auth BFF
- Users API Router
- Plan BFF API Client
- AI Job Execution Store
- Backup Enrollment Tests
- Settings Database Tests
- Prompt Test Worker Tests
- Feature Specification Areas
- Job Repository
- Settings Views
- AI Adoption Service
- Desktop UI Pages
- Exports API Tests
- Desktop Services Interface
- Auth Throttling
- Auth Smoke Tests
- Security Architecture
- Architecture Decision Records
- Word Export Job Tests
- Login Throttling
- Word Export Storage
- Identity Password Hashing
- Teacher Plan Renderer
- Data Model Documentation
- Application Port Interfaces
- AI Preview Panel
- Health Check Dependencies
- Teacher Plan Rendering
- Database Migrations
- Redis Job Dispatcher
- System Architecture Overview
- Credential Management API
- Feature Specs & Contracts
- AI Prompt Definitions
- Project Quality Gates
- AI Preview Flow Tests
- AI Task Schema Contracts
- Daily Plan Workspace
- AI Results Repository
- Message Broker Setup
- AI Generation Tests
- AI Preview Flow
- Capability Navigation
- Developer Handoff Notes
- Auth Assurance Levels
- AI Batch Generation Tests
- Backup Authentication Tests
- Backup Auth Isolation Tests
- FastAPI App Assembly
- API Dependency Wiring
- BFF Proxy Client
- Repository Workflow Plan
- Export Repository
- Backend Module Map
- AI Prompt Contract Tests
- Repository Shell Utilities
- Isolated Test Database Setup
- Database Profile Security Tests
- Log Redaction Observability
- Identity Isolation Tests
- Group Activity Preview Adoption
- Settings Page Widget
- AI Client SSRF Policy
- Controlled Agent Runtime Contract
- Desktop Application Services
- Runtime OpenAPI Contract
- AI Key Rotation
- Teacher Plan DOCX Rendering
- AI Settings Page
- Web Entry Security Logging
- AI Generation Results Migration
- Security Configuration Settings
- Plan Content Completeness
- Invitation Registration Flow
- Export Contract Schemas
- Desktop SQLite Migrations
- Local Readiness Checks
- Desktop Backup Security Design
- Desktop System Architecture
- AI Repository Persistence
- AI Prompt Settings UI
- Authentication Contract Tests
- Controlled Agent ADR
- Slice 2A Red Evidence
- Backup Package Contract
- Prompt Validation
- Settings API Contract
- AI Prompt Repository Tests
- AI Generation Service Tests
- Runtime OpenAPI Assembly
- Prompt JSON Schema
- Lesson Plan Service Logic
- Local-First Desktop ADR
- Initial Admin CLI
- Backup Authentication Contract
- Export Repository Persistence
- AI Client Behavior Tests
- Request ID Middleware
- AI Prompt Job Status
- Transactional Session Boundaries
- Trusted BFF Client IP
- Desktop UI Design System
- Contracts and Feature Phases
- Manual Lesson Plan Workflow
- TOTP Generation Primitives
- Group Activity Source Validation
- Local Dev Compose Profiles
- Architecture Dependency Boundaries
- Workday Calendar Service
- AI Preview Adoption Service
- Target Service Architecture
- Slice 1 Red Evidence
- Group Activity AI Contract
- OpenAPI Document Validation
- Word Export Migration
- Secret Encryption Envelope
- API Security Bootstrap
- Agent Runtime Design Decisions
- Desktop System Architecture
- AI Jobs Database Migration
- Backup Auth Migration
- Word Export Contract
- Password to Passkey Migration
- Content V1 Validation
- AI Key Envelope Encryption
- AI Model URL Policy
- Prompt Catalog Contract
- Passkey Expand Migration
- Group Activity AI Features
- Group Activity AI Jobs
- Settings Domain Features
- Prompt Renderer Grammar
- Service Architecture Planning
- Slice 1 Review Remediation
- Identity Audit Migration
- Settings Database Migration
- Password TOTP Migration
- Group Activity Sources Migration
- Word Exports Migration
- Word Export Contract Features
- Users API Contract
- TOTP Authentication Logic
- Slice 1 Acceptance Evidence
- Progress Environment Query
- Milestone Dependency Query
- Desktop GUI Prototype Query
- Windows Theme Fix Query
- Manual Testing Query
- Timing Acceptance Clarification
- Test Numbering Corrections
- Feature Branch Script
- AI Key Rotation CLI
- Lesson Plan Calendar Tests
- Lesson Plan Contracts
- Lesson Plan Contract Tests
- Calendar Fixture
- Fixed Clock
- Job Broker Fixture
- Identity Audit Metadata
- Lease Expiration
- Local-First Tasks
- AI Client Fixture
- Child Manager App
- Dramatiq Worker
- ADR Decision Analysis
- SQLAlchemy Alembic Base
- SecLists Notice
- Backend Capabilities
- Shared Data Contracts
- Prerequisite Check Script
- Plan Setup Script
- Task Setup Script
- AI Infrastructure Adapter
- SQLite Migration Chain
- Qt Widgets UI
- Web and BFF Tests
- Batch Export Prototype
- Group Activity Editor Prototype
- Weekly Plan Workbench Prototype
- Weekly Plan Dark Mode Prototype
- Backend Package
- Contracts Package
- Integrations Module
- Issue Template Config
- Prototype A Classic
- Prototype B Focus
- Prototype B Dark
- Common Passwords List
- Child Manager
- Kindergarten Domain
- Workday Cache
- Phase 2 Foundation
- Specification Quality Checklist
- Iteration Validation
- Offline Windows Acceptance
- First Startup Flow
- AI Domain Models
- Credentials Boundary
- AI Client Prompts
- AI Migration Protection
- AI Generation Application
- AI Settings UI
- AI Application Assembly
- AI Acceptance Testing
- Settings Repository
- Word Template

## God Nodes (most connected - your core abstractions)
1. `ActorFixture` - 226 edges
2. `csrf_headers()` - 178 edges
3. `IdentityError` - 172 edges
4. `ContractModel` - 161 edges
5. `SessionUser` - 156 edges
6. `IdentityRepository` - 133 edges
7. `provision_editable_plan_context()` - 97 edges
8. `IdentityService` - 96 edges
9. `AuditRepository` - 82 edges
10. `_Connection` - 77 edges

## Surprising Connections (you probably didn't know these)
- `WebAuthn 通行密钥认证` --semantically_similar_to--> `WebAuthn/备用登录安全约束`  [INFERRED] [semantically similar]
  docs/ADR/ADR-0010-restricted-public-entry-passkey-authentication-and-recovery.md → .specify/memory/constitution.md
- `FR-019 提示词变量白名单与占位符词法` --conceptually_related_to--> `packages/backend/prompts/renderer.py 白名单纯替换渲染器`  [INFERRED]
  specs/001-daily-activity-plan/spec.md → packages/backend/prompts/renderer.py
- `Phase 1 Setup (Pre-M1文档门禁与工程初始化)` --references--> `packages/contracts/exports.py 导出契约`  [EXTRACTED]
  specs/001-daily-activity-plan/tasks.md → packages/contracts/exports.py
- `Phase 1 Setup (Pre-M1文档门禁与工程初始化)` --references--> `packages/contracts/identity.py 身份契约`  [EXTRACTED]
  specs/001-daily-activity-plan/tasks.md → packages/contracts/identity.py
- `Phase 1 Setup (Pre-M1文档门禁与工程初始化)` --references--> `packages/contracts/settings.py 设置契约`  [EXTRACTED]
  specs/001-daily-activity-plan/tasks.md → packages/contracts/settings.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **AI preview lifecycle (cancel, reject, stale invalidation, adopt)** — tests_desktop_test_cancel_and_close_discard_late_results, tests_desktop_test_page_change_invalidates_epoch_and_discards_late_signal, tests_desktop_test_reject_changes_only_preview_and_stale_target_cannot_be_adopted, tests_desktop_test_stale_preview_is_invalidated_without_snapshot_or_content_write, tests_desktop_test_adoption_snapshots_before_mutating_current_content, docs_implementation_evidence_desktop_slice_2a_acceptance_preview_epoch, docs_implementation_evidence_desktop_slice_2a_acceptance_pre_ai_adopt_snapshot [EXTRACTED 0.90]
- **Unified three-call AI retry budget** — tests_desktop_test_retryable_failure_is_retried_at_most_twice, tests_desktop_test_transport_and_structure_errors_share_one_three_call_budget, docs_implementation_evidence_desktop_slice_2a_acceptance_retry_budget, docs_implementation_evidence_desktop_slice_2a_acceptance_httpx_mocktransport [EXTRACTED 0.90]
- **Slice 2A Implementation Tasks** — specs_003_desktop_local_first_tasks_t041, specs_003_desktop_local_first_tasks_t042, specs_003_desktop_local_first_tasks_t043, specs_003_desktop_local_first_tasks_t044, specs_003_desktop_local_first_tasks_t045, specs_003_desktop_local_first_tasks_t046, specs_003_desktop_local_first_tasks_t047, specs_003_desktop_local_first_tasks_t048 [EXTRACTED 1.00]
- **AI Generation Prompts for Lesson Plan Sections** — src_kindergarten_manager_infrastructure_ai_prompts_afternoon_outdoor_game, src_kindergarten_manager_infrastructure_ai_prompts_daily_reflection, src_kindergarten_manager_infrastructure_ai_prompts_indoor_area_game, src_kindergarten_manager_infrastructure_ai_prompts_morning_activity, src_kindergarten_manager_infrastructure_ai_prompts_morning_talk [INFERRED 0.75]
- **Slice 2A clean RED 的五类公开模块 seam** — docs_implementation_evidence_desktop_slice_2a_red_domain_ai_public_module_seam, docs_implementation_evidence_desktop_slice_2a_red_infrastructure_ai_client_public_module_seam, docs_implementation_evidence_desktop_slice_2a_red_application_ai_generation_public_module_seam, docs_implementation_evidence_desktop_slice_2a_red_ui_ai_preview_public_module_seam [EXTRACTED 1.00]
- **Spec Kit Specification→Plan→Tasks→Implement Workflow** — agents_spec_kit_skills, agents_skills_speckit_specify_skill, agents_skills_speckit_clarify_skill, agents_skills_speckit_plan_skill, agents_skills_speckit_tasks_skill, agents_skills_speckit_analyze_skill, agents_skills_speckit_checklist_skill, agents_skills_speckit_implement_skill, agents_skills_speckit_converge_skill, agents_skills_speckit_constitution_skill, agents_skills_speckit_taskstoissues_skill [EXTRACTED 0.90]
- **Service Boundary and Data Flow** — readme_nicegui_web, readme_fastapi_api, readme_background_worker, readme_postgresql, readme_redis_queue, readme_ai_compatible_service, readme_object_storage_boundary [EXTRACTED 0.90]
- **Phase-1 Daily Activity Plan Closed Loop** — readme_daily_activity_plan, readme_ai_model_profile, readme_ai_prompt_management, readme_async_generation, readme_word_export, agents_optimistic_lock, agents_ai_snapshot_rule, agents_kindergarten_isolation [INFERRED 0.75]
- **Spec Kit 全生命周期流程 (specify→plan→tasks→implement)** — specify_workflows_speckit_workflow_specify_step, specify_workflows_speckit_workflow_review_spec_gate, specify_workflows_speckit_workflow_plan_step, specify_workflows_speckit_workflow_review_plan_gate, specify_workflows_speckit_workflow_tasks_step, specify_workflows_speckit_workflow_implement_step [EXTRACTED 1.00]
- **Roadmap 里程碑依赖链 M0→M9** — docs_roadmap_m0, docs_roadmap_m1, docs_roadmap_m2, docs_roadmap_m3, docs_roadmap_m3a, docs_roadmap_m5, docs_roadmap_m4, docs_roadmap_m6, docs_roadmap_m7, docs_roadmap_m8, docs_roadmap_m9 [EXTRACTED 1.00]
- **宪章六大核心原则** — specify_memory_constitution_source_of_truth, specify_memory_constitution_service_boundary, specify_memory_constitution_kindergarten_isolation, specify_memory_constitution_authoritative_state, specify_memory_constitution_teacher_control, specify_memory_constitution_executable_verification [EXTRACTED 1.00]
- **Identity, Authentication and Recovery Flow** — docs_design_database_schema_users, docs_design_database_schema_webauthn_credentials, docs_design_database_schema_webauthn_challenges, docs_design_database_schema_backup_auth_credentials, docs_design_database_schema_backup_auth_enrollments, docs_design_database_schema_bootstrap_initializations, docs_design_database_schema_account_invitations, docs_design_database_schema_recovery_codes, docs_design_database_schema_account_recovery_requests, docs_design_database_schema_identity_verification_approvals, docs_design_database_schema_roles, docs_design_database_schema_user_roles, docs_design_database_schema_refresh_tokens [EXTRACTED 0.90]
- **AI-Assisted Daily Activity Plan Generation and Adoption Flow** — docs_design_database_schema_daily_activity_plans, docs_design_database_schema_daily_activity_plan_snapshots, docs_design_database_schema_lesson_plan_sources, docs_design_database_schema_background_jobs, docs_design_database_schema_ai_generation_results, docs_design_database_schema_prompt_definitions, docs_design_database_schema_prompt_versions, docs_design_database_schema_prompt_test_runs, docs_design_database_schema_ai_model_profiles [EXTRACTED 0.85]
- **Child Manager Cloud Runtime Deployment Units** — docs_design_system_architecture_web_bff, docs_design_system_architecture_api, docs_design_system_architecture_worker, docs_design_system_architecture_contracts, docs_design_system_architecture_backend, docs_design_system_architecture_postgresql, docs_design_system_architecture_redis [EXTRACTED 0.90]
- **M1 双 Agent 独立实现与 Issue 层级交付结构** — concept_branch_codex, concept_branch_trae, concept_issue_1, concept_issue_2, concept_issue_3 [EXTRACTED 0.90]
- **M1 已确认技术基线** — concept_tech_python, concept_tech_uv, concept_tech_nicegui, concept_tech_fastapi, concept_tech_dramatiq, concept_tech_postgresql, concept_tech_redis, concept_tech_alembic, concept_tech_docker_compose [EXTRACTED 0.90]
- **M2 认证授权与身份审计交付结构** — concept_issue_4, concept_issue_5, concept_issue_6, concept_tasks_t021_t035, specs_001_daily_activity_plan_contracts_openapi_doc, docs_adr_adr_0004_same_origin_cookie_authentication [EXTRACTED 0.90]
- **M0 Quality Gates G1–G8** — docs_faq_combined_audit_m0_g1_model_contract_alignment, docs_faq_combined_audit_m0_g2_template_instructions, docs_faq_combined_audit_m0_g3_template_hash, docs_faq_combined_audit_m0_g4_scope_status_alignment, docs_faq_combined_audit_m0_g5_static_validation, docs_faq_combined_audit_m0_g6_graph_consistency, docs_faq_combined_audit_m0_g7_history_privacy_cleanup, docs_faq_combined_audit_m0_g8_shared_baseline, docs_faq_combined_audit_m0_milestone [EXTRACTED 1.00]
- **First-Phase Threat Scenarios** — docs_security_threat_model_scenario_public_scanning, docs_security_threat_model_scenario_phishing, docs_security_threat_model_scenario_invite_leak, docs_security_threat_model_scenario_passkey_loss, docs_security_threat_model_scenario_last_admin, docs_security_threat_model_scenario_device_theft, docs_security_threat_model_scenario_export_leak [EXTRACTED 0.95]
- **M0 Remediation Pipeline (A→D2→M1)** — docs_shenchabaogao_20260713_xiufufangan_task_a, docs_shenchabaogao_20260713_xiufufangan_task_b, docs_shenchabaogao_20260713_xiufufangan_task_c, docs_shenchabaogao_20260713_xiufufangan_task_d1, docs_shenchabaogao_20260713_xiufufangan_task_d2, docs_shenchabaogao_20260713_xiufufangan_m1_launch [EXTRACTED 0.95]
- **M0 内容门禁 G1–G8（2026-07-14 全部关闭）** — gate_m0_g1, gate_m0_g2, gate_m0_g3, gate_m0_g4, gate_m0_g5, gate_m0_g6, gate_m0_g7, gate_m0_g8 [EXTRACTED 0.95]
- **M1 Issue 层级：一个共享父 Issue + Codex/Trae 两个实现子 Issue** — issue_m1_parent, issue_m1_codex, issue_m1_trae [EXTRACTED 0.95]
- **M1 启动授权链：Issue 创建 → T003 建分支 → 实现（各自独立授权，互不推导）** — issue_m1_parent, specs_001_daily_activity_plan_tasks_t003, branch_codex, branch_trae [INFERRED 0.85]
- **身份认证与会话族 (WebAuthn + 备用认证 + 邀请恢复 + Refresh 轮换)** — specs_001_daily_activity_plan_data_model_users, specs_001_daily_activity_plan_data_model_webauthn_credentials, specs_001_daily_activity_plan_data_model_webauthn_challenges, specs_001_daily_activity_plan_data_model_backup_auth_credentials, specs_001_daily_activity_plan_data_model_backup_auth_enrollments, specs_001_daily_activity_plan_data_model_bootstrap_initializations, specs_001_daily_activity_plan_data_model_account_invitations, specs_001_daily_activity_plan_data_model_recovery_codes, specs_001_daily_activity_plan_data_model_account_recovery_requests, specs_001_daily_activity_plan_data_model_identity_verification_approvals, specs_001_daily_activity_plan_data_model_user_roles, specs_001_daily_activity_plan_data_model_roles, specs_001_daily_activity_plan_data_model_refresh_tokens [EXTRACTED 0.90]
- **AI 生成与提示词测试管线 (PostgreSQL 权威任务状态驱动)** — specs_001_daily_activity_plan_data_model_ai_model_profiles, specs_001_daily_activity_plan_data_model_ai_model_profile_capabilities, specs_001_daily_activity_plan_data_model_prompt_definitions, specs_001_daily_activity_plan_data_model_prompt_versions, specs_001_daily_activity_plan_data_model_prompt_test_runs, specs_001_daily_activity_plan_data_model_background_jobs, specs_001_daily_activity_plan_data_model_ai_generation_results, specs_001_daily_activity_plan_data_model_daily_activity_plans, specs_001_daily_activity_plan_data_model_daily_activity_plan_snapshots [EXTRACTED 0.90]
- **七个系统默认提示词与逐任务变量白名单** — specs_001_daily_activity_plan_spec_prompt_morning_activity, specs_001_daily_activity_plan_spec_prompt_morning_talk, specs_001_daily_activity_plan_spec_prompt_group_activity_split, specs_001_daily_activity_plan_spec_prompt_group_activity_add_step, specs_001_daily_activity_plan_spec_prompt_indoor_area_game, specs_001_daily_activity_plan_spec_prompt_afternoon_outdoor_game, specs_001_daily_activity_plan_spec_prompt_daily_reflection, specs_001_daily_activity_plan_spec_fr_016, specs_001_daily_activity_plan_spec_prompt_definition [EXTRACTED 0.95]
- **US1 安全初始化与必要设置分阶段交付 (M2/M3/M3A)** — specs_001_daily_activity_plan_spec_us1, specs_001_daily_activity_plan_tasks_phase_3_us1_m2, specs_001_daily_activity_plan_tasks_phase_3_us1_m3, specs_001_daily_activity_plan_tasks_phase_3_us1_m3a [EXTRACTED 0.90]
- **异步AI生成→预览→采用闭环** — specs_001_daily_activity_plan_spec_fr_035, specs_001_daily_activity_plan_spec_fr_037, specs_001_daily_activity_plan_spec_fr_041, specs_001_daily_activity_plan_spec_background_job, specs_001_daily_activity_plan_spec_ai_generation_preview, specs_001_daily_activity_plan_spec_daily_activity_plan, packages_backend_lesson_plans_ai_generation_module, packages_backend_jobs_ai_runner_module, packages_backend_lesson_plans_ai_adoption_module [INFERRED 0.75]
- **Password+TOTP Backup Authentication Flow (M3A)** — packages_backend_identity_passwords_passwords_module, packages_backend_identity_totp_totp_module, packages_backend_identity_secret_encryption_secret_encryption_module, packages_backend_identity_repository_repository_module, packages_backend_identity_service_service_module, packages_contracts_identity_identity_module, apps_api_routers_auth_router, apps_web_pages_auth_page [EXTRACTED 0.90]

## Communities (313 total, 52 thin omitted)

### Community 0 - "AI Services Events"
Cohesion: 0.09
Nodes (32): ai_generation_service(), ai_retry_service(), reflection_generation_service(), append_ai_event(), Any, UUID, AiRetryService, _native_url() (+24 more)

### Community 1 - "Workday Calendar Client"
Cohesion: 0.05
Nodes (53): _calendar_library_available(), map_timor_payload(), AsyncBaseTransport, date, TimorWorkdayClient, WorkdayResult, Any, date (+45 more)

### Community 2 - "DOCX Text Extraction"
Cohesion: 0.07
Nodes (73): lesson_plan_source_service(), _ByteWriter, _check_deadline(), _deadline(), DocxExtractionError, _extract_document_text(), extract_docx_text(), Path (+65 more)

### Community 3 - "Identity & Auth Service"
Cohesion: 0.12
Nodes (18): AuditRepository, AuthResult, _challenge_digest(), _client_challenge(), _decode_base64url(), IdentityError, IdentityService, ManagedUser (+10 more)

### Community 4 - "Identity Backup Repository"
Cohesion: 0.06
Nodes (19): _backup_credential(), _backup_enrollment(), BackupCredentialRecord, BackupEnrollmentRecord, BackupRevocationResult, BackupSecurityEventRecord, ChallengeRecord, _credential() (+11 more)

### Community 5 - "Prompt Template Renderer"
Cohesion: 0.11
Nodes (25): prompt_service(), PromptTemplateError, Any, ValueError, 仅支持固定白名单纯替换词法的提示词渲染器。, render_prompt(), _render_value(), validate_prompt_template() (+17 more)

### Community 6 - "Desktop Main Window"
Cohesion: 0.11
Nodes (13): ColorScheme, QCloseEvent, ResolvedTheme, DesktopMainWindow, QWidget, ThemePreference, _setup_complete(), _validated_theme() (+5 more)

### Community 7 - "System Architecture & ADRs"
Cohesion: 0.06
Nodes (74): ADR-0010 Identity Rewrite, ADR-0011 Password+TOTP Backup, API Application, API Dependencies, API OpenAPI Generation, Auth API Router, Exports API Router, Web API Client (+66 more)

### Community 8 - "Prompt Schema Catalog"
Cohesion: 0.32
Nodes (35): PromptSpec, BaseModel, 固定提示词目录、输入与结果 Schema 路由。, _spec(), AiAreaGame, AiDailyReflection, AiGroupActivity, AiMorningActivity (+27 more)

### Community 9 - "Word Export Service"
Cohesion: 0.17
Nodes (20): ExportService, BytesRenderer, _content(), _east_asia_font(), FrozenContentSnapshot, _opaque_snapshot(), _paragraph_properties_without_numbering(), Any (+12 more)

### Community 10 - "AI Runtime Adapter"
Cohesion: 0.04
Nodes (44): ProgressReporter, ProviderNeutralAiClient, _AiRuntimeAdapter, _BatchOutcome, create_desktop_window(), _DesktopServiceFacade, _now_utc_ms(), Any (+36 more)

### Community 11 - "Worker Job Runners"
Cohesion: 0.10
Nodes (36): Actor, AiJobScopeResolver, AiRunner, build_ai_job_runner(), build_ai_result_repository(), build_prompt_test_executor(), build_word_export_runner(), build_worker_scope_resolver() (+28 more)

### Community 12 - "Settings API Router"
Cohesion: 0.10
Nodes (60): AgeGroup, AiModelProfile, AiModelServiceDependency, _age_group(), _ai_model(), _area(), _class(), create_ai_model_profile() (+52 more)

### Community 13 - "Jobs API Router"
Cohesion: 0.07
Nodes (78): AiAdoptionServiceDependency, AiGenerationServiceDependency, AiRetryServiceDependency, adopt_ai_preview(), get_ai_preview(), get_job(), alias, CurrentSessionDependency (+70 more)

### Community 14 - "AI Key Encryption"
Cohesion: 0.15
Nodes (23): UUID, run_rotation(), _aad(), AiKeyEnvelope, decrypt_api_key(), decrypt_api_key_with_provider(), encrypt_api_key(), encrypt_api_key_with_provider() (+15 more)

### Community 15 - "Daily Plan Export"
Cohesion: 0.05
Nodes (45): Self, AdoptionCandidate, CancellationToken, DailyPlanExportSnapshot, DayRenderer, ExportError, ExportResult, Path (+37 more)

### Community 16 - "App Bootstrap Startup"
Cohesion: 0.05
Nodes (72): Engine, BootstrapService, RuntimeError, StartupError, StartupState, _apply_sqlite_pragmas(), connect_sqlite(), create_session_factory() (+64 more)

### Community 17 - "WebAuthn Authentication Tests"
Cohesion: 0.12
Nodes (41): csrf_headers(), _base64url(), _credential(), MonkeyPatch, TestClient, _registration_credential(), test_authentication_options_are_username_less_and_browser_ready(), test_authentication_options_do_not_increment_failure_limit() (+33 more)

### Community 18 - "Prompts API Router"
Cohesion: 0.17
Nodes (30): clear_prompt_tests(), create_prompt_test(), _definition(), get_prompt(), get_prompt_test(), get_prompt_version(), _job(), list_prompt_tests() (+22 more)

### Community 19 - "Batch Job Query"
Cohesion: 0.15
Nodes (19): job_query_service(), JobStatus, BatchJobAggregationRepository, Any, UUID, `ai.batch` 父任务的只读状态投影。, 从恰好四个子任务派生父任务响应，不写入父任务执行字段。, JobQueryService (+11 more)

### Community 20 - "Identity Contract Models"
Cohesion: 0.07
Nodes (49): ContractModel, BaseModel, AdminCredentialRevocationResult, AuthenticationCredential, AuthenticationCredentialResponse, AuthenticationPublicKey, AuthenticationResult, AuthenticatorSelection (+41 more)

### Community 21 - "Observability Task DTOs"
Cohesion: 0.09
Nodes (30): BackgroundTask, QObject, QRunnable, ErrorCode, StrEnum, TaskProgress, _is_sensitive_key(), Any (+22 more)

### Community 22 - "Database Models Migrations"
Cohesion: 0.09
Nodes (43): DeclarativeBase, AuditEvent, Base, DailyActivityPlanExport, Word 导出 SQLAlchemy 模型。, AccountInvitation, AccountRecoveryRequest, BackupAuthCredential (+35 more)

### Community 23 - "TOTP Secret Encryption"
Cohesion: 0.13
Nodes (22): _aad(), decrypt_totp_secret(), decrypt_totp_secret_with_provider(), encrypt_totp_secret(), encrypt_totp_secret_with_provider(), FileIdentitySecretKeyProvider, Path, UUID (+14 more)

### Community 24 - "AI Generation Coordinator"
Cohesion: 0.06
Nodes (36): AdoptedContent, AdoptionTransaction, AiGenerationCoordinator, AiGenerationError, AiPreviewStore, FrozenGenerationInput, GenerationRuntime, _Operation (+28 more)

### Community 25 - "Desktop Feature Evidence"
Cohesion: 0.09
Nodes (41): Issue #19 (child-manager), Desktop Slice 2A Local Acceptance Evidence, AiPreviewPanel (AI preview panel), Alembic migration runner, Application Service, Atomic AI settings persistence, Bootstrap, CommandResult (+33 more)

### Community 26 - "Branch Strategy & Issues"
Cohesion: 0.11
Nodes (39): codex 分支 (历史双实现线), dev 分支 (唯一实现与集成), docs 分支 (文档与契约), main 分支 (稳定发布基线), trae 分支 (历史双实现线), Codex Agent, Dev 本地档位 (端口/Compose/数据库隔离), graphify 知识图谱工具与 graphify-out 输出 (+31 more)

### Community 27 - "Word Export Job Store"
Cohesion: 0.12
Nodes (14): canonical_export_content_sha256(), Any, _has_valid_frozen_input(), PostgresWordExportStore, Any, datetime, Protocol, RuntimeError (+6 more)

### Community 28 - "AI Job Execution"
Cohesion: 0.11
Nodes (17): AiClientError, RuntimeError, AiJobAuthorizer, AI 生成任务的冻结上下文执行器与 PostgreSQL 状态适配器。, CurrentModelCallProfile, ProfileCallLimiter, PromptTestAuthorizer, PromptTestExecutionContext (+9 more)

### Community 29 - "AI Model Key Management"
Cohesion: 0.05
Nodes (59): AiKeyProvider, IntegrityError, NoReturn, AiModelService, _display(), _key(), _native_url(), Resolver (+51 more)

### Community 30 - "Redis Job Message Contract"
Cohesion: 0.07
Nodes (71): JobMessage, Redis 中唯一允许传递的最小任务消息。, _insert_job(), _insert_other_tenant_plan(), _insert_result(), _native_url(), _provision_dependencies(), TestClient (+63 more)

### Community 31 - "Architecture & Audit Docs"
Cohesion: 0.09
Nodes (50): CSRF & Origin Verification, Data Model Design, Database Schema Design, System Architecture, main Branch (stable release baseline), Combined Audit Conclusion (Q1–Q26), M0-G1 Model & Contract Alignment, M0-G2 Template Instructions Alignment (+42 more)

### Community 32 - "Development Toolchain Rules"
Cohesion: 0.12
Nodes (49): AGENTS.md 开发规则, AES-256-GCM Key Encryption, Autosave / Snapshot Rules, dev Branch, docs Branch, main Branch, codebase-memory MCP, codegraph (+41 more)

### Community 33 - "Passkey Test Helpers"
Cohesion: 0.08
Nodes (46): current_session(), AuthenticatedSessionDependency, StaticIdentitySecretKeyProvider, admin_client(), passkey_client(), MonkeyPatch, TestClient, 通过 FastAPI 身份依赖注入建立已 step-up 管理员，不借用密码登录。 (+38 more)

### Community 34 - "Daily Plan Page UI"
Cohesion: 0.14
Nodes (12): EditorKind, QLabel, QScrollArea, DailyPlanPage, FieldDefinition, _lines(), ProcessEditor, Any (+4 more)

### Community 35 - "Admin Initialization CLI"
Cohesion: 0.13
Nodes (32): ArgumentParser, activate_initialization(), migrate_passkeys(), _native_url(), datetime, UUID, 首位管理员的部署控制台初始化与双人核验激活。, 仅在通行密钥已登记并完成两位预登记人员核验后激活。 (+24 more)

### Community 36 - "AI Retry Policy"
Cohesion: 0.09
Nodes (24): ProviderNeutralAiClient, BaseTransport, Resolver, cap_retry_after_seconds(), is_retryable_ai_error(), UUID, 按任务与尝试次数生成可复现的有界抖动，便于恢复与确定性测试。, retry_delay_seconds() (+16 more)

### Community 37 - "Prompt Test Job Tests"
Cohesion: 0.33
Nodes (17): FailingDispatcher, prompt_job_client(), _provision_model_and_version(), Any, TestClient, _resolver(), test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure(), test_draft_version_can_be_tested_before_publication() (+9 more)

### Community 38 - "First Run Plan Tests"
Cohesion: 0.16
Nodes (19): DailyPlanContext, _build(), _child(), FakeDesktopServices, Any, date, LogCaptureFixture, MonkeyPatch (+11 more)

### Community 39 - "Prompt Test Store"
Cohesion: 0.23
Nodes (6): _native_url(), PostgresPromptTestStore, Any, datetime, UUID, 提示词测试 Worker 的 PostgreSQL 权威状态适配器。

### Community 40 - "Auth API Router"
Cohesion: 0.16
Nodes (58): _allowed_origins(), authenticate_with_password_and_totp(), authentication_start(), authentication_verify(), backup_authentication_status(), bootstrap_options(), bootstrap_verify(), _check_public_throttle() (+50 more)

### Community 41 - "AI Preview Adoption Tests"
Cohesion: 0.12
Nodes (38): create_completed_ai_preview(), provision_enabled_ai_model(), TestClient, UUID, _native_url(), TestClient, UUID, _snapshot_count() (+30 more)

### Community 42 - "Provider-Neutral AI Client"
Cohesion: 0.15
Nodes (14): Client, AiClientError, _chat_completions_endpoint(), ProviderNeutralAiClient, Any, BaseTransport, RuntimeError, validate_base_url() (+6 more)

### Community 43 - "Domain Entity Catalog"
Cohesion: 0.08
Nodes (39): Account Invitations, Account Recovery Requests, Age Groups, AI Generation Results, AI Model Profile Capabilities, AI Model Profiles, Audit Events, Background Jobs (+31 more)

### Community 44 - "WebAuthn Challenge Store"
Cohesion: 0.10
Nodes (36): ChallengeBinding, ChallengePurpose, ChallengeRecord, consume_challenge(), issue_challenge(), IssuedChallenge, datetime, StrEnum (+28 more)

### Community 45 - "Exports API Router"
Cohesion: 0.12
Nodes (33): _accepted(), create_export(), download_export(), _export(), get_export(), _job(), list_exports(), alias (+25 more)

### Community 46 - "Export Flow Tests"
Cohesion: 0.13
Nodes (31): Element, _complete_plan(), _export(), MonkeyPatch, T132 Word 导出保存、确认、轮询、历史与下载 RED 冒烟。, test_download_failure_uses_server_chinese_feedback(), test_download_javascript_failure_logs_only_sanitized_diagnostic(), test_empty_reflection_exports_current_editor_content_polls_and_keeps_two_histories() (+23 more)

### Community 47 - "Spec Kit Skills"
Cohesion: 0.12
Nodes (35): speckit-analyze Skill, speckit-checklist Skill, speckit-clarify Skill, speckit-constitution Skill, speckit-converge Skill, speckit-implement Skill, speckit-plan Skill, speckit-specify Skill (+27 more)

### Community 48 - "Backup Auth BFF"
Cohesion: 0.12
Nodes (27): backup_auth_api_request(), backup_login_api_request(), backup_reauthentication_api_request(), 只通过同源 BFF 访问本人备用登录端点。, 以请求正文提交两项备用因素，不把秘密放入 URL。, 为当前备用会话取得仅可新增通行密钥的短时证明。, 读取本人最近 20 条内建安全事件，不产生已读状态。, 从浏览器经同源 BFF 调用 API，并为写请求取得 CSRF token。 (+19 more)

### Community 49 - "Users API Router"
Cohesion: 0.21
Nodes (31): activate(), create_user(), credential_revoke(), credentials(), deactivate(), get_user(), _invitation(), invitation_issue() (+23 more)

### Community 50 - "Plan BFF API Client"
Cohesion: 0.11
Nodes (26): export_file_download(), plan_api_request(), plan_docx_preview_request(), 通过同源 BFF 提取 DOCX，返回待教师确认的临时文本。, 只通过同源 BFF 访问教案及其任务端点。, 通过同源 fetch 下载受保护文件，并保留 API 错误反馈。, AiSectionAction, preview_title() (+18 more)

### Community 51 - "AI Job Execution Store"
Cohesion: 0.13
Nodes (11): AiExecutionContext, AiJobStore, AiJobStoreProtocol, _log_sanitized_exception(), Any, datetime, Exception, Protocol (+3 more)

### Community 52 - "Backup Enrollment Tests"
Cohesion: 0.19
Nodes (21): ActorFixture, TestClient, test_admin_is_restricted_until_complete_backup_enrollment(), test_backup_status_and_enrollment_require_authentication(), test_enrollment_requires_password_and_totp_together_and_is_single_use(), test_expired_enrollment_cannot_enable_backup_auth(), test_new_enrollment_invalidates_the_previous_pending_enrollment(), test_replacing_enabled_material_revokes_only_related_backup_sessions() (+13 more)

### Community 53 - "Settings Database Tests"
Cohesion: 0.09
Nodes (26): MonkeyPatch, settings_database(), test_age_group_seed_is_fixed_and_idempotent(), test_area_constraints_allow_empty_collections_but_reject_duplicate_names(), test_postgresql_enforces_semester_and_lead_teacher_uniqueness(), test_settings_migration_creates_the_five_tenant_scoped_tables(), test_settings_relations_use_composite_tenant_foreign_keys(), lesson_plan_database() (+18 more)

### Community 54 - "Prompt Test Worker Tests"
Cohesion: 0.15
Nodes (20): _context(), FakeAuthorizer, FakeClient, FakeStore, _modules(), Any, datetime, UUID (+12 more)

### Community 55 - "Feature Specification Areas"
Cohesion: 0.09
Nodes (46): codex 实现分支（待授权创建）, main 分支（docs-only 基线）, trae 实现分支（待授权创建）, AI 生成与提示词规则, 班级与教师配置, 一日活动计划, 日期选择与校验, 教案结构化 (+38 more)

### Community 56 - "Job Repository"
Cohesion: 0.21
Nodes (10): _ai_job(), AiJobRecord, _job(), JobRecord, JobRepository, Any, datetime, PostgreSQL 权威后台任务 Repository。 (+2 more)

### Community 57 - "Settings Views"
Cohesion: 0.05
Nodes (42): _areas(), _class_view(), ClassView, KindergartenView, AbstractContextManager, date, Protocol, ValueError (+34 more)

### Community 58 - "AI Adoption Service"
Cohesion: 0.11
Nodes (25): ai_adoption_service(), AiAdoptionService, _native_url(), AiTaskCode, Any, datetime, JsonValue, LessonPlanRepository (+17 more)

### Community 59 - "Desktop UI Pages"
Cohesion: 0.25
Nodes (8): BaseException, user_error_message(), Slice 1 结构化一日活动计划编辑页。, build_first_run_daily_plan_window(), build_first_run_page(), QWidget, export_current_day(), QWidget

### Community 60 - "Exports API Tests"
Cohesion: 0.45
Nodes (23): SimpleNamespace, _complete_content(), _headers(), _native_url(), MonkeyPatch, Path, TestClient, _request_body() (+15 more)

### Community 61 - "Desktop Services Interface"
Cohesion: 0.10
Nodes (6): DesktopServices, Any, date, Path, Protocol, UUID

### Community 62 - "Auth Throttling"
Cohesion: 0.13
Nodes (15): _auth_throttle(), MemoryAuthThrottle, datetime, Redis, timedelta, 公开身份 ceremony 的来源限流公共 seam。, 按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。, 多进程 API 使用的 Redis 固定窗口实现。 (+7 more)

### Community 63 - "Auth Smoke Tests"
Cohesion: 0.18
Nodes (18): login_page_text(), users_page_text(), BrowserContext, Page, _add_virtual_authenticator(), _auth_cookie_names(), _bootstrap_activate(), _bootstrap_start() (+10 more)

### Community 64 - "Security Architecture"
Cohesion: 0.12
Nodes (26): ADR-0009 Defer Production Deployment Until Feature Complete, Security Threat Model, AES-256-GCM Secret Encryption, Argon2id Password Hashing, External AI Service, FastAPI API (private network), Last-Admin Recovery CLI, NiceGUI Web / BFF (sole public entry) (+18 more)

### Community 65 - "Architecture Decision Records"
Cohesion: 0.10
Nodes (40): ADR-0001 Cloud Only, kindergarten_id 园所隔离约束, ADR-0002 独立 Web/API/Worker 模块化单体, background_job 权威任务状态机, ADR-0003 PostgreSQL 权威任务状态 + Dramatiq/Redis, ADR-0004 同源 Cookie 认证, 提示词草稿/发布/回滚生命周期, ADR-0005 AI 供应商中立与提示词系统 (+32 more)

### Community 66 - "Word Export Job Tests"
Cohesion: 0.15
Nodes (16): FailingRenderer, FakeRenderer, FakeStorage, FakeStore, Any, Path, UUID, T131/T138 Word Worker 只读冻结输入与幂等落位 RED。 (+8 more)

### Community 67 - "Login Throttling"
Cohesion: 0.17
Nodes (10): _digest(), MemoryLoginThrottle, datetime, Redis, timedelta, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision (+2 more)

### Community 68 - "Word Export Storage"
Cohesion: 0.09
Nodes (25): ExportDownload, _native_url(), Word 导出创建、历史、详情与实时授权下载用例。, build_display_filename(), ExportStorage, new_storage_key(), Path, UUID (+17 more)

### Community 69 - "Identity Password Hashing"
Cohesion: 0.12
Nodes (27): normalize_phone(), normalize_username(), hash_password(), password_needs_rehash(), password_violations(), Path, verify_password(), _weak_passwords() (+19 more)

### Community 70 - "Teacher Plan Renderer"
Cohesion: 0.16
Nodes (10): Any, _Cell, DocumentType, Paragraph, Path, ValueError, 固定 teacherplan.docx 副本渲染器。, 只读取固定模板，并在内存副本中替换已确认字段。 (+2 more)

### Community 71 - "Data Model Documentation"
Cohesion: 0.08
Nodes (25): 1. 建模原则, 2. 关系概览, 3. 通用存储约定, 4.10 `prompt_overrides`, 4.11 `ai_previews`, 4.12 `agent_action_audits`（Agent 写入阶段）, 4.13 `backup_records`, 4.1 `app_profile`（单例） (+17 more)

### Community 72 - "Application Port Interfaces"
Cohesion: 0.21
Nodes (9): AiClient, Clock, DependencyCheck, JobBroker, datetime, Protocol, UUID, M1 外部边界所需的最小 Protocol。 (+1 more)

### Community 73 - "AI Preview Panel"
Cohesion: 0.33
Nodes (3): AiPreviewPanel, QFrame, 实际教案页中的可选 AI 入口、逐栏预览与显式采用面板。

### Community 74 - "Health Check Dependencies"
Cohesion: 0.31
Nodes (15): create_app(), HealthDependencies, check(), dependencies(), Path, test_database_failure_returns_stable_503_code(), test_default_dependencies_check_real_local_runtime(), test_each_optional_dependency_only_degrades_ready_response() (+7 more)

### Community 75 - "Teacher Plan Rendering"
Cohesion: 0.17
Nodes (8): _Cell, DocumentType, Paragraph, Path, ValueError, TeacherplanRenderer, TeacherplanTemplateError, Table

### Community 76 - "Database Migrations"
Cohesion: 0.10
Nodes (9): Alembic 迁移, Any, Column, _timestamps(), upgrade(), migrated_database(), MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds() (+1 more)

### Community 77 - "Redis Job Dispatcher"
Cohesion: 0.19
Nodes (16): Any, 向已注册 actor 投递唯一的 job_id。, RedisJobDispatcher, AiRecoveryStore, AiResultMaintenanceCounts, AiResultMaintenanceRepository, datetime, Protocol (+8 more)

### Community 78 - "System Architecture Overview"
Cohesion: 0.05
Nodes (87): AI 生成与提示词规则 (graphify 源节点), apps/api FastAPI API, apps/web NiceGUI Web + BFF, apps/worker Dramatiq Worker, BFF 服务端转发层 (Backend for Frontend), chinesecalendar (本地工作日库), cryptography (AES-GCM/Argon2id), Dramatiq 2 + Redis (+79 more)

### Community 79 - "Credential Management API"
Cohesion: 0.36
Nodes (12): _base64url(), _insert_credential(), _native_url(), MonkeyPatch, TestClient, UUID, _registration_credential(), test_admin_cannot_revoke_last_active_admin_last_credential() (+4 more)

### Community 80 - "Feature Specs & Contracts"
Cohesion: 0.13
Nodes (22): docs/design/data-model.md 数据模型, docs/design/database-schema.md 数据库Schema, docs/design/system-architecture.md 系统架构, docs/PRD/lesson-management.md 产品PRD, packages/contracts/identity.py 身份契约, specs/001-daily-activity-plan/contracts/openapi.yaml OpenAPI契约, 班级与教师关联, Feature Spec: 首期一日活动计划完整闭环 (M0–M8) (+14 more)

### Community 81 - "AI Prompt Definitions"
Cohesion: 0.16
Nodes (22): FR-016 七个稳定AI任务与只读默认提示词, 晨间公共变量集 (7变量), daily_activity_plan.afternoon_outdoor_game 下午户外游戏, daily_activity_plan.daily_reflection 一日活动反思, 提示词定义与版本 (草稿/发布/历史), daily_activity_plan.group_activity_add_step 集体活动新增环节, daily_activity_plan.group_activity_split 集体活动拆分, daily_activity_plan.indoor_area_game 室内区域游戏 (+14 more)

### Community 82 - "Project Quality Gates"
Cohesion: 0.09
Nodes (21): 10. Agent 写入阶段, 11.1 实施前 spike 门禁, 11.2 业务验收, 11. Word 批量导出, 12. Windows UI 与 DPI, 13. Windows standalone 与安装器, 14. 后期 MSIX 兼容性（非首期完成门禁）, 15. 完整质量门禁 (+13 more)

### Community 83 - "AI Preview Flow Tests"
Cohesion: 0.16
Nodes (11): CoordinatorState, FakeAiServices, _flow(), QtBot, UUID, test_actual_panel_wires_per_section_preview_adopt_and_retry(), test_adopt_and_reject_emit_only_explicit_preview_intents(), test_ai_entry_is_optional_and_unconfigured_state_does_not_block_manual_flow() (+3 more)

### Community 84 - "AI Task Schema Contracts"
Cohesion: 0.29
Nodes (10): _contract(), Any, ModuleType, M6 AI 固定结果与输入最小化 RED 验收。, test_area_result_cannot_own_areas_and_adoption_reuses_validated_input(), test_daily_reflection_is_nonempty_nfkc_and_limited_by_unicode_code_points(), test_group_activity_results_are_closed_and_add_step_index_is_not_clamped(), test_morning_activity_requires_three_nonempty_chinese_statements() (+2 more)

### Community 85 - "Daily Plan Workspace"
Cohesion: 0.09
Nodes (21): DailyPlanWorkspace, _filename_part(), Any, date, LessonPlanService, Path, Protocol, RuntimeError (+13 more)

### Community 86 - "AI Results Repository"
Cohesion: 0.23
Nodes (12): AiGenerationResultRecord, AiGenerationResultRepository, _json_object(), _optional_uuid(), Any, datetime, 同园隔离的 AI 生成结果 Repository。, 将同园到期预览条件收敛为 expired，不修改结果正文或决策字段。 (+4 more)

### Community 87 - "Message Broker Setup"
Cohesion: 0.10
Nodes (24): build_test_broker(), 生产 Redis 与确定性测试消息代理装配。, Event, AiJobRetry, RuntimeError, 通知消息代理按权威任务给出的退避时间重投。, StubBroker, _ai_actor() (+16 more)

### Community 88 - "AI Generation Tests"
Cohesion: 0.08
Nodes (39): _coordinator(), _module(), PersistentPreviewStore, PreviewStore, UUID, ScriptedRuntime, test_adoption_snapshots_before_mutating_current_content(), test_batch_keeps_successful_previews_when_one_section_fails() (+31 more)

### Community 89 - "AI Preview Flow"
Cohesion: 0.14
Nodes (5): AiPreviewFlow, UUID, 不依赖 Qt 的预览状态机；所有正文变更必须由显式 intent 触发。, SectionFailure, SectionPreview

### Community 90 - "Capability Navigation"
Cohesion: 0.17
Nodes (16): navigation_for_capabilities(), 按 API capabilities 生成导航。, class_areas_page_text(), settings_page_text(), test_navigation_is_derived_from_current_api_capabilities(), BrowserActor, _free_port(), _m3_services() (+8 more)

### Community 91 - "Developer Handoff Notes"
Cohesion: 0.11
Nodes (18): 1. 恢复时先确认的基线, 2.1 已完成, 2.2 已验证门禁, 2.3 尚未实现, 2. 当前实现进度, 3. 下一步：只从 T016 开始, 4.1 项目必须项, 4.2 当前主机已发现的工具缺口 (+10 more)

### Community 92 - "Auth Assurance Levels"
Cohesion: 0.40
Nodes (6): datetime, _session(), test_backup_reauthentication_only_authorizes_add_passkey_for_five_minutes(), test_expired_backup_reauthentication_cannot_add_passkey(), test_recent_webauthn_proof_satisfies_high_risk_identity_boundary(), test_restricted_enrollment_session_cannot_enter_business_routes()

### Community 93 - "AI Batch Generation Tests"
Cohesion: 0.26
Nodes (15): _configure_batch_areas(), _idempotent_headers(), TestClient, test_batch_accepts_exactly_four_independent_children_and_derives_parent(), test_batch_database_parent_is_never_executable_or_dispatched(), test_batch_idempotency_replays_original_parent_and_rejects_changed_body(), ai_admin_client(), _profile_payload() (+7 more)

### Community 94 - "Backup Authentication Tests"
Cohesion: 0.30
Nodes (18): _base64url(), _enable_backup(), _generic_failure_payload(), MonkeyPatch, Response, TestClient, _registration_credential(), _request() (+10 more)

### Community 95 - "Backup Auth Isolation Tests"
Cohesion: 0.25
Nodes (13): MonkeyPatch, UUID, RecordingConnection, RecordingResult, _seed_backup_repository(), test_admin_role_gate_restricts_and_then_releases_webauthn_sessions(), test_backup_credential_reads_are_scoped_to_kindergarten_and_user(), test_backup_version_change_revokes_only_related_sessions() (+5 more)

### Community 96 - "FastAPI App Assembly"
Cohesion: 0.19
Nodes (13): _error_response(), _identity_error_response(), FastAPI, Request, UUID, FastAPI 应用装配、统一异常转换与健康端点。, _request_id(), JSONResponse (+5 more)

### Community 97 - "API Dependency Wiring"
Cohesion: 0.10
Nodes (36): admin_session(), ai_model_service(), authenticated_session(), export_service(), identity_service(), lesson_plan_service(), CurrentSessionDependency, IdentityServiceDependency (+28 more)

### Community 98 - "BFF Proxy Client"
Cohesion: 0.21
Nodes (12): BffResponse, proxy_request(), AsyncBaseTransport, NiceGUI 服务端 BFF 客户端的公开接缝。, 按固定 allowlist 转发请求，并保留响应原始多值头。, HTTPX (外部 HTTP 客户端), MonkeyPatch, test_plan_docx_preview_request_forwards_csrf_cookie_and_multipart() (+4 more)

### Community 99 - "Repository Workflow Plan"
Cohesion: 0.24
Nodes (14): Repository Workflow Reset 2026-07-21, Codex Agent, dev Branch (Codex implementation branch), Development Flow (需求→docs→Issue→dev→测试→Review→main), docs Branch (single source of truth), M2 Parent Issue #4 (shared parent → dev acceptance entry), M2 Codex Issue #5 (implementation & acceptance evidence), M2 Trae Issue #6 (closed not planned) (+6 more)

### Community 100 - "Export Repository"
Cohesion: 0.19
Nodes (10): ExportRecord, ExportRepository, Any, 园所范围 Word 导出 PostgreSQL Repository。, 所有查询和变更都同时约束 ``kindergarten_id``。, _record(), _uuid(), ExportService (+2 more)

### Community 101 - "Backend Module Map"
Cohesion: 0.13
Nodes (17): packages/backend/jobs/ai_results.py AI结果仓储 (pending→output), packages/backend/jobs/ai_runner.py AI执行Runner, packages/backend/jobs/retry_policy.py 重试分类/退避, packages/backend/lesson_plans/ai_adoption.py 采用事务, packages/backend/lesson_plans/ai_generation.py 生成受理/batch, packages/backend/lesson_plans/reflection.py 反思生成, packages/backend/prompts/renderer.py 白名单纯替换渲染器, AI生成预览 (短期结构化候选) (+9 more)

### Community 102 - "AI Prompt Contract Tests"
Cohesion: 0.32
Nodes (6): Any, _schema(), test_model_and_job_contracts_freeze_revision_and_stable_errors(), test_prompt_test_contract_exposes_only_redacted_input_summary(), test_prompt_test_fingerprint_changes_across_prompt_codes(), test_runtime_exposes_the_complete_frozen_m4_route_surface()

### Community 103 - "Repository Shell Utilities"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 104 - "Isolated Test Database Setup"
Cohesion: 0.15
Nodes (12): str, block_external_network(), isolated_database_url(), _LazyTestDatabaseUrl, _native_psycopg_url(), MonkeyPatch, 只在旧 PostgreSQL 测试真正使用 URL 时读取环境配置。, 只允许回环 TCP 和本机 Unix socket。 (+4 more)

### Community 105 - "Database Profile Security Tests"
Cohesion: 0.31
Nodes (15): MonkeyPatch, Path, test_environment_test_database_url_takes_precedence_over_profile(), test_test_database_profile_must_stay_outside_the_repository(), test_test_database_profile_rejects_group_or_other_access(), test_test_database_url_rejects_nonisolated_or_nonpostgresql_targets(), test_test_database_url_reports_missing_environment_and_profile(), test_test_database_url_uses_secure_repo_external_profile() (+7 more)

### Community 106 - "Log Redaction Observability"
Cohesion: 0.22
Nodes (14): merge_request_context(), EventDict, 递归清除日志中的密钥、令牌、认证材料与 URL 凭证。, 将当前请求关联字段合并到真实 structlog 事件。, _redact(), redact_mapping(), _redact_url(), request_context() (+6 more)

### Community 107 - "Identity Isolation Tests"
Cohesion: 0.28
Nodes (15): TeacherInput, identity_database(), _insert_kindergarten(), _insert_user(), MonkeyPatch, UUID, test_cross_kindergarten_role_assignment_is_rejected_by_composite_foreign_key(), test_refresh_replacement_cannot_cross_kindergarten() (+7 more)

### Community 108 - "Group Activity Preview Adoption"
Cohesion: 0.43
Nodes (15): _complete_preview(), _headers(), _native_url(), _prepare_adopted_split(), Any, TestClient, UUID, _request_generation() (+7 more)

### Community 109 - "Settings Page Widget"
Cohesion: 0.33
Nodes (3): QDateEdit, QWidget, SettingsPage

### Community 110 - "AI Client SSRF Policy"
Cohesion: 0.29
Nodes (12): _pinned_url(), Any, OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。, _addresses(), AiUrlPolicyError, Resolver, ValueError, AI 模型地址的保存时与连接前 SSRF 防护。 (+4 more)

### Community 111 - "Controlled Agent Runtime Contract"
Cohesion: 0.13
Nodes (15): 10. 线程契约, 11. 事务与 WRITE 契约, 12. 无长期业务记忆, 13. 验证矩阵, 14. 明确非目标, 1. 目的与适用阶段, 2. 依赖与信任规则, 3. `Runtime` (+7 more)

### Community 112 - "Desktop Application Services"
Cohesion: 0.13
Nodes (15): 10. `ExportService`, 11. `BackupService`, 12. Qt 运行时桥接, 13. 架构契约测试, 1. 目的, 2. 依赖规则, 3. 共享结果类型, 4. `BootstrapService` (+7 more)

### Community 113 - "Runtime OpenAPI Contract"
Cohesion: 0.37
Nodes (14): _assert_operation_contract(), _canonical_schema(), _effective_security(), _operations(), _parameter_shape(), Any, 运行时 OpenAPI 与冻结身份契约的一致性门禁。, _request_schema() (+6 more)

### Community 114 - "AI Key Rotation"
Cohesion: 0.35
Nodes (10): _candidate(), FakeStore, _modules(), Any, UUID, test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it(), test_rotation_dry_run_and_repeated_batch_are_zero_write(), test_rotation_uses_stable_cursor_and_does_not_change_call_revision() (+2 more)

### Community 115 - "Teacher Plan DOCX Rendering"
Cohesion: 0.28
Nodes (14): _east_asia_font(), _fixture(), Any, Path, T130 固定 teacherplan.docx 渲染结构与样式 RED。, _render(), _renderer_type(), test_empty_week_and_reflection_keep_fixed_positions_and_three_rows() (+6 more)

### Community 117 - "Web Entry Security Logging"
Cohesion: 0.25
Nodes (11): main(), 仅绑定回环地址的 NiceGUI Web 入口。, _require_loopback(), _validate_cookie_security(), configure_logging(), EventDict, 递归清除 Web 日志中的凭证和内部 URL。, _redact() (+3 more)

### Community 118 - "AI Generation Results Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 119 - "Security Configuration Settings"
Cohesion: 0.25
Nodes (12): AppSettings, global_security_ready(), BaseModel, JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。, MonkeyPatch, settings(), test_api_entrypoint_rejects_insecure_cookie_on_non_loopback(), test_development_insecure_cookie_requires_loopback_binding() (+4 more)

### Community 120 - "Plan Content Completeness"
Cohesion: 0.17
Nodes (18): missing_export_sections(), ExportSection, PlanContentV1, 返回需要二次确认的五栏；反思永远不参与确认。, _area_complete(), content_completeness(), EditableContent, _group_activity_complete() (+10 more)

### Community 121 - "Invitation Registration Flow"
Cohesion: 0.33
Nodes (13): _base64url(), _create_teacher(), _issue(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes(), test_invitation_is_single_use_reissuable_and_revocable() (+5 more)

### Community 122 - "Export Contract Schemas"
Cohesion: 0.10
Nodes (30): canonical_request_fingerprint(), _normalize_scalar(), 跨服务使用的公共 Schema 与规范化函数。, 计算覆盖路由、实际资源与语义输入的 canonical SHA-256。, _export_payload(), _job_payload(), Any, UUID (+22 more)

### Community 124 - "Local Readiness Checks"
Cohesion: 0.24
Nodes (13): _ai_unconfigured(), build_health_dependencies(), _database_check(), _file_check(), _path_check(), Path, 从进程环境构造真实、无副作用的本地就绪检查。, _redis_check() (+5 more)

### Community 125 - "Desktop Backup Security Design"
Cohesion: 0.15
Nodes (12): 1. 本地数据权威, 2. Schema 迁移, 3. 保存、版本与归档, 4. 凭据存储, 5. 备份包, 6. 备份与恢复流程, 7. 非同步保证, 8. 威胁与验证 (+4 more)

### Community 126 - "Desktop System Architecture"
Cohesion: 0.15
Nodes (13): 10. WebDAV 与 S3, 11. Windows 构建、安装与后期 MSIX, 12. 旧 B/S 复用原则, 1. Python、PySide6 与界面技术, 2. SQLite、SQLAlchemy 与 Alembic, 3. 数据目录与资源定位, 4. 线程、任务和取消, 5. 模块边界 (+5 more)

### Community 127 - "AI Repository Persistence"
Cohesion: 0.36
Nodes (10): _create_preview_through_application(), NoopRuntime, Path, UUID, _repository(), _seed_plan(), test_ai_configuration_and_prompt_override_store_no_secret(), test_ai_settings_aggregate_rolls_back_configuration_and_prompts_together() (+2 more)

### Community 128 - "AI Prompt Settings UI"
Cohesion: 0.19
Nodes (7): _job_status_module(), Any, MonkeyPatch, test_controls_have_keyboard_focus_and_error_label_associations(), test_job_status_recovers_configuration_change_with_chinese_action(), test_job_status_refreshes_until_terminal_and_restores_after_page_reload(), test_settings_controls_call_model_prompt_and_job_public_api_seams()

### Community 129 - "Authentication Contract Tests"
Cohesion: 0.21
Nodes (7): APIRoute, Any, _resolve(), _runtime_routes(), test_auth_success_and_logout_lock_two_raw_cookie_headers(), test_runtime_auth_router_matches_frozen_passkey_paths(), test_runtime_auth_success_statuses_match_frozen_contract()

### Community 130 - "Controlled Agent ADR"
Cohesion: 0.17
Nodes (12): ADR-0013：受控单 Agent 运行时, Provider 直接调用 Repository 或 SQL, 代价, 取舍, 后续复审条件, 多 Agent 与 Level 3 Workflow, 持久化完整对话、向量记忆或自动摘要, 收益 (+4 more)

### Community 131 - "Slice 2A Red Evidence"
Cohesion: 0.24
Nodes (12): desktop-slice-2a-red.md：桌面 Slice 2A clean RED 证据, 公开模块 seam：kindergarten_manager.application.ai_generation, clean RED：33 failed，全部稳定转换为 SLICE2A_RED, 先收集结果：827 tests collected，较 Slice 1 的 794 项新增 33 项, 公开模块 seam：kindergarten_manager.domain.ai, 公开模块 seam：kindergarten_manager.infrastructure.ai.client, Issue #19 Slice 2A RED 固定范围：docs SHA fff6e0908fcb591c927205d53cdbacd35037bce3、Slice 1 Review SHA 11527404d4bd13551fe23d793b5e81d8e0e22b74、main merge 52432295377c7b88f490822664cfaed0412d3836, 替身与隐私边界：无真实网络、AI、操作系统凭据或付费服务 (+4 more)

### Community 132 - "Backup Package Contract"
Cohesion: 0.17
Nodes (12): 10. 验证矩阵, 1. 范围, 2. 内部完整包, 3. 一致性快照生成, 4. 加密信封, 5. 凭据存储, 6. 远程对象, 7. 轮换 (+4 more)

### Community 133 - "Prompt Validation"
Cohesion: 0.67
Nodes (4): prompt_spec(), Any, validate_prompt_result(), validate_prompt_variables()

### Community 134 - "Settings API Contract"
Cohesion: 0.24
Nodes (5): _operation_parameters(), Any, _resolve(), test_age_groups_are_a_fixed_four_item_non_paginated_collection(), test_area_get_uses_default_20_maximum_100_pagination()

### Community 135 - "AI Prompt Repository Tests"
Cohesion: 0.30
Nodes (9): _modules(), Any, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_call_configuration_change_set_matches_the_frozen_revision_rules(), test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup(), test_model_reads_and_writes_are_tenant_scoped(), test_prompt_run_frozen_fields_cannot_be_updated() (+1 more)

### Community 136 - "AI Generation Service Tests"
Cohesion: 0.23
Nodes (19): AiGenerationRequest, _native_url(), TestClient, UUID, RecordingDispatcher, _replace_areas(), _session(), test_batch_creates_non_executable_parent_and_exactly_four_dispatched_children() (+11 more)

### Community 137 - "Runtime OpenAPI Assembly"
Cohesion: 0.29
Nodes (9): _apply_operation_contract(), configure_openapi(), _no_content_response(), _operation(), Any, FastAPI, M2 运行时 OpenAPI 的集中契约装配。, 返回缓存后的 M2 运行时 OpenAPI 生成器。 (+1 more)

### Community 138 - "Prompt JSON Schema"
Cohesion: 1.00
Nodes (3): JsonSchemaValue, _render_prompt_test_run_schema(), _render_union_as_one_of()

### Community 139 - "Lesson Plan Service Logic"
Cohesion: 0.40
Nodes (6): date, FixedClock, PlanContentV1, RecordingLessonPlanRepository, test_open_or_create_is_stable_for_same_class_and_date(), test_save_increments_revision_and_stale_base_is_rejected()

### Community 140 - "Local-First Desktop ADR"
Cohesion: 0.18
Nodes (11): ADR-0012：本地优先桌面产品方向重置, 代价, 使用 PyQt6, 决策, 取舍, 将现有 B/S 系统封装进桌面窗口, 收益, 背景 (+3 more)

### Community 141 - "Initial Admin CLI"
Cohesion: 0.40
Nodes (10): _prepare_last_admin_recovery(), CompletedProcess, MonkeyPatch, UUID, _run_cli(), test_init_admin_activate_requires_two_distinct_pre_registered_approvers(), test_init_admin_cli_exposes_start_activate_and_migration_commands(), test_init_admin_start_creates_pending_account_and_one_time_secret_without_password() (+2 more)

### Community 142 - "Backup Authentication Contract"
Cohesion: 0.24
Nodes (7): Any, _resolve(), _runtime_routes(), test_backup_contract_marks_request_and_one_time_response_secrets(), test_runtime_router_exposes_the_user_story_2_endpoints(), test_runtime_router_matches_the_frozen_backup_contract(), test_runtime_user_story_2_openapi_matches_frozen_security_and_responses()

### Community 144 - "Export Repository Persistence"
Cohesion: 0.55
Nodes (10): _create_pending(), _insert_word_job(), _native_url(), Any, TestClient, UUID, _repository(), test_frozen_context_and_content_cannot_be_updated_after_creation() (+2 more)

### Community 145 - "AI Client Behavior Tests"
Cohesion: 0.44
Nodes (10): _modules(), Any, _resolver(), test_client_caps_retry_after_at_sixty_seconds(), test_client_errors_are_stable_and_never_include_key_or_prompt(), test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin(), test_client_posts_openai_compatible_request_with_fixed_limits(), test_client_rejects_redirects_without_following_them() (+2 more)

### Community 146 - "Request ID Middleware"
Cohesion: 0.22
Nodes (7): API 请求 ID 与追踪 ID 中间件。, _request_id(), RequestContextMiddleware, ASGIApp, Receive, Scope, Send

### Community 147 - "AI Prompt Job Status"
Cohesion: 0.17
Nodes (10): ai_job_status(), AiJobStatus, prompt_test_status(), PromptTestStatus, 异步提示词测试的稳定中文状态与无障碍语义。, build_ai_prompt_settings_section(), prompt_edit_version_id(), prompt_test_record_text() (+2 more)

### Community 148 - "Transactional Session Boundaries"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 149 - "Trusted BFF Client IP"
Cohesion: 0.33
Nodes (8): Collection, parse_trusted_bff_peers(), 只接受显式配置的回环 BFF socket peer。, resolve_client_ip(), test_configured_loopback_bff_peer_can_supply_internal_client_ip(), test_non_loopback_peer_cannot_be_configured_as_trusted_bff(), test_trusted_bff_peers_are_empty_until_explicitly_configured(), test_untrusted_peer_cannot_supply_internal_client_ip()

### Community 150 - "Desktop UI Design System"
Cohesion: 0.20
Nodes (9): 1. 体验目标, 2. 信息架构, 3. 视觉令牌, 4. 已确认教案编辑布局, 5. 固定状态位置, 6. 可用性与无障碍, 7. 主题行为, Word 导出入口 (+1 more)

### Community 151 - "Contracts and Feature Phases"
Cohesion: 0.22
Nodes (10): packages/backend/integrations/crypto/ai_keys.py 密钥信封, packages/contracts/audit.py 审计契约, packages/contracts/common.py 公共错误/分页/幂等契约, packages/contracts/jobs.py 任务契约, packages/contracts/lesson_plans.py 教案契约, packages/contracts/prompts.py 提示词契约, FR-019 提示词变量白名单与占位符词法, US3 管理员配置模型与提示词 (P3) (+2 more)

### Community 152 - "Manual Lesson Plan Workflow"
Cohesion: 0.24
Nodes (10): 一日活动计划 (六栏目/版本/归档), 一日活动反思 (highlights/issues/adjustments), FR-022 同园同班同日唯一教案, FR-028 六栏目结构化Schema与反思200上限, FR-030 版本号并发检测, FR-067 五栏完整后显式生成反思, 教案历史快照 (不可变/带原因), 学期 (Semester) (+2 more)

### Community 153 - "TOTP Generation Primitives"
Cohesion: 0.13
Nodes (28): candidate_totp_counters(), _counter(), generate_totp(), generate_totp_secret(), _hotp(), RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。, 生成认证器广泛兼容的 160 位无填充 Base32 种子。, 返回当前时间步及相邻一个时间步，按 counter 递增排序。 (+20 more)

### Community 154 - "Group Activity Source Validation"
Cohesion: 0.49
Nodes (9): _insert_other_kindergarten_plan(), TestClient, UUID, _source_history_total(), _source_url(), test_confirmed_text_creates_metadata_only_and_each_confirmation_is_retained(), test_cross_kindergarten_plan_identifier_is_not_accepted_as_a_source_target(), test_docx_extraction_requires_explicit_confirmation_before_persisting_metadata() (+1 more)

### Community 155 - "Local Dev Compose Profiles"
Cohesion: 0.27
Nodes (8): _compose_config(), Any, Path, 双实现本地开发档位的 Compose 合同。, test_compose_accepts_temporary_image_overrides(), test_compose_uses_selected_local_profile(), test_quality_workflow_provides_an_isolated_postgresql_database(), test_test_database_url_requires_an_explicit_profile()

### Community 156 - "Architecture Dependency Boundaries"
Cohesion: 0.40
Nodes (9): _imports(), _matches(), _package_for(), Path, test_application_and_domain_dependencies_point_inward(), test_composition_root_only_wires_adapters_and_application_services(), test_desktop_namespace_does_not_import_legacy_runtime(), test_ui_only_reaches_application_boundary() (+1 more)

### Community 158 - "Workday Calendar Service"
Cohesion: 0.29
Nodes (6): _module(), MonkeyPatch, test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls(), test_local_result_wins_conflict_and_uses_one_hour_cache(), test_timor_client_enforces_one_total_deadline(), test_unsupported_local_calendar_range_softly_falls_back_to_online()

### Community 159 - "AI Preview Adoption Service"
Cohesion: 0.58
Nodes (9): _completed_preview(), _native_url(), TestClient, UUID, _service(), _session(), test_adopt_is_atomic_and_idempotent(), test_reject_is_atomic_and_idempotent_without_plan_change() (+1 more)

### Community 160 - "Target Service Architecture"
Cohesion: 0.31
Nodes (9): OpenAI-Compatible Model Service, FastAPI API (apps/api), Export Storage Seam, Holiday Adapter, Key Source Seam, PostgreSQL, Redis, NiceGUI Web / BFF (apps/web) (+1 more)

### Community 161 - "Slice 1 Red Evidence"
Cohesion: 0.22
Nodes (8): Foundation 门禁, Slice 1 RED, 停止边界, 固定基线与授权, 强制 collect-only, 桌面 Slice 1 手工 MVP RED 证据, 环境, 额外完整性检查

### Community 163 - "Group Activity AI Contract"
Cohesion: 0.39
Nodes (8): _contract(), Any, US5 集体活动来源与两阶段 AI 契约 RED。, _source_payload(), test_docx_extraction_preview_is_separate_from_confirmed_source_metadata(), test_source_metadata_is_closed_and_never_exposes_original_text_or_attachment(), test_source_page_is_closed_and_preserves_pagination_metadata(), test_split_and_incremental_add_schemas_are_closed_and_validate_index_bounds()

### Community 164 - "OpenAPI Document Validation"
Cohesion: 0.36
Nodes (8): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_declares_confirmation_and_generic_word_export_conflicts(), test_openapi_document_is_valid_31(), test_openapi_keeps_nicegui_as_the_only_browser_entry(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 166 - "Word Export Migration"
Cohesion: 0.25
Nodes (7): MonkeyPatch, T129 Word 导出迁移与数据库不变量 RED。, test_0010_can_downgrade_to_0009_and_upgrade_again(), test_export_status_uniqueness_and_success_failure_shapes_are_database_enforced(), test_export_table_has_frozen_input_and_long_term_history_columns(), test_export_uses_same_tenant_composite_foreign_keys(), word_export_database()

### Community 167 - "Secret Encryption Envelope"
Cohesion: 0.39
Nodes (8): _context(), _encryption_module(), Any, Path, test_development_key_provider_requires_owner_only_file_outside_repository(), test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution(), test_totp_secret_envelope_round_trips_with_random_96_bit_nonce(), test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce()

### Community 168 - "API Security Bootstrap"
Cohesion: 0.32
Nodes (6): main(), 拒绝在非开发环境或非回环地址关闭 Cookie Secure。, 验证进程启动时的 Cookie 与监听地址组合。, validate_cookie_security(), configure_logging(), 配置 JSON 结构化日志和最终脱敏处理器。

### Community 170 - "Agent Runtime Design Decisions"
Cohesion: 0.25
Nodes (8): 1. 单 Agent 与 Application Layer, 2. Tool-only 业务访问, 3. 有界 Context 与无长期业务记忆, 4. 分阶段权限与确认写入, 5. 线程、事务与失败语义, 6. Provider port, 7. 固定实施顺序, 决策

### Community 171 - "Desktop System Architecture"
Cohesion: 0.25
Nodes (8): 1. 目标与边界, 2. 运行结构, 3. 线程与任务, 4. 模块结构目标, 5. 可复用与不可直接迁移, 6. 平台与数据目录, 7. 验证责任, 幼儿园管理助手桌面系统架构

### Community 172 - "AI Jobs Database Migration"
Cohesion: 0.36
Nodes (6): Any, Column, 建立 AI 模型、提示词与 PostgreSQL 权威任务基础。, _seed_defaults(), _timestamps(), upgrade()

### Community 173 - "Backup Auth Migration"
Cohesion: 0.46
Nodes (7): Script, _backup_revision(), MonkeyPatch, test_backup_auth_migration_creates_isolated_credentials_and_enrollments(), test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(), test_backup_auth_revision_follows_settings_and_precedes_lesson_plans(), test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade()

### Community 175 - "Word Export Contract"
Cohesion: 0.25
Nodes (8): 1. 共同不变量, 2. 冻结输入, 3. 单日导出, 4. 批量预览, 5. 批量 DOCX 结构, 6. 进度、取消与原子发布, 7. 验证矩阵, Word 导出契约

### Community 176 - "Password to Passkey Migration"
Cohesion: 0.54
Nodes (7): _assert_passkey_revisions_exist(), _native_url(), MonkeyPatch, test_contract_removes_password_data_and_downgrade_recreates_only_empty_columns(), test_expand_moves_existing_accounts_to_enrollment_and_revokes_old_sessions(), test_passkey_migration_has_explicit_expand_and_contract_boundaries(), _user_columns()

### Community 177 - "Content V1 Validation"
Cohesion: 0.54
Nodes (7): _contracts(), _schemas(), test_completeness_is_independent_from_progressive_schema_validation(), test_empty_v1_content_supports_progressive_manual_editing(), test_reflection_is_nfkc_normalized_and_limited_to_200_codepoints(), test_statement_and_question_punctuation_are_strictly_chinese(), test_unknown_fields_and_unknown_content_versions_are_not_silently_coerced()

### Community 178 - "AI Key Envelope Encryption"
Cohesion: 0.39
Nodes (7): _module(), Any, Path, test_ai_key_envelope_rejects_tampering_and_cross_profile_substitution(), test_ai_key_envelope_round_trips_with_random_96_bit_nonce(), test_file_key_provider_requires_owner_only_files_outside_repository(), test_static_key_provider_reads_old_key_but_writes_with_active_key()

### Community 179 - "AI Model URL Policy"
Cohesion: 0.57
Nodes (7): _module(), Any, _resolver(), test_policy_accepts_only_allowlisted_public_https_and_checks_every_address(), test_policy_detects_dns_rebinding_before_connect(), test_policy_rejects_non_https_and_non_public_networks(), test_policy_requires_explicit_server_allowlist()

### Community 180 - "Prompt Catalog Contract"
Cohesion: 0.43
Nodes (7): _module(), Any, test_catalog_assigns_task_specific_minimum_variable_whitelists(), test_catalog_freezes_seven_codes_whitelists_schemas_and_hashes(), test_catalog_input_validation_excludes_teacher_identity_and_unknown_fields(), test_catalog_result_schemas_are_strict(), test_catalog_result_schemas_match_the_frozen_openapi_shapes()

### Community 181 - "Passkey Expand Migration"
Cohesion: 0.52
Nodes (5): Any, Column, _tenant_identity_columns(), _timestamps(), upgrade()

### Community 182 - "Group Activity AI Features"
Cohesion: 0.33
Nodes (7): packages/backend/integrations/files/docx.py DOCX安全提取, packages/backend/lesson_plans/group_activity_ai.py 集体活动AI, FR-044 集体活动仅文本/.docx来源, FR-047 新增适龄环节结构化标记is_ai_added, 集体活动来源 (文本/.docx 提取记录), US5 教师处理集体活动原始教案 (P5), Phase 7 US5 集体活动导入与生成

### Community 183 - "Group Activity AI Jobs"
Cohesion: 0.38
Nodes (5): Any, 新增环节只基于教师已采用并保存的完整当前集体活动。, require_complete_saved_group_activity(), T122 集体活动新增环节的真实输入校验。, test_add_step_input_requires_complete_saved_group_activity()

### Community 184 - "Settings Domain Features"
Cohesion: 0.29
Nodes (7): packages/contracts/settings.py 设置契约, 班级区域 (室内/户外有序可启停), FR-011 室内/户外有序区域维护, FR-078 密码+TOTP两项共同成立的备用登录, US1 管理员完成安全初始化与必要设置 (P1), US1 M3 首期必要设置 (学期/班级/区域), US1 M3A 密码+TOTP备用登录 (独立规格002)

### Community 186 - "Prompt Renderer Grammar"
Cohesion: 0.48
Nodes (6): _module(), Any, test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(), test_renderer_fails_for_missing_variable_before_external_call(), test_renderer_rejects_every_non_frozen_placeholder_form(), test_renderer_uses_stable_json_and_never_recursively_renders_values()

### Community 187 - "Service Architecture Planning"
Cohesion: 0.60
Nodes (6): 共同实施路线, 当前仓库与分支状态, Web、API 与 Worker 服务边界, 目标服务架构, 查询记录 2026-07-11 02:19：接下来需要生成什么文件, 查询记录 2026-07-11 02:42：系统架构文档要素

### Community 188 - "Slice 1 Review Remediation"
Cohesion: 0.40
Nodes (6): desktop-slice-1-review-remediation.md：桌面 Slice 1 双轴 Review 修复证据, CI run 31450912844 attempt 1：completed、success、headSha=7af4d46f1114616eb798e5991805a164026c63df, 双轴 Review 同源阻断 finding：产品显示名偏差, Review 修复提交角色：docs SHA fff6e0908fcb591c927205d53cdbacd35037bce3、原始实现 cf106e44cb907a4958879a16ee061dccc8c2b1f9、初始 docs-only 收口 b53c1c43c69e3ae3058d74b6163ecfc2bd7d4e95、修复锚点 7af4d46f1114616eb798e5991805a164026c63df、后继 docs-only 固定 Review SHA, Review gate：双轴 Review 通过、合并 SHA Quality CI 成功前不得合并 main、关闭 Issue 或进入 Slice 2A, TDD red/green：显示名断言先失败，修复后通过

### Community 189 - "Identity Audit Migration"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 190 - "Settings Database Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 191 - "Password TOTP Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 193 - "Group Activity Sources Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 194 - "Word Exports Migration"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 195 - "Word Export Contract Features"
Cohesion: 0.33
Nodes (6): packages/contracts/exports.py 导出契约, FR-049 导出同事务冻结快照, FR-054 导出文件名 一日活动计划_{班级}_{YYYY-MM-DD}.docx, US6 教师导出并重新下载固定Word (P6), Word导出记录 (独立副本/哈希), Phase 8 US6 固定Word导出与历史

### Community 197 - "TOTP Authentication Logic"
Cohesion: 0.53
Nodes (5): Any, test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps(), test_totp_rejects_the_same_or_earlier_counter_after_success(), test_totp_secret_is_unique_high_entropy_base32(), _totp_module()

### Community 198 - "Slice 1 Acceptance Evidence"
Cohesion: 0.40
Nodes (5): desktop-slice-1-acceptance.md：桌面 Slice 1 Windows 手工验收证据, CI run 31392074261 attempt 2：completed、success、headSha=cf106e44cb907a4958879a16ee061dccc8c2b1f9, 验收固定角色：docs SHA fff6e0908fcb591c927205d53cdbacd35037bce3、原始实现 cf106e44cb907a4958879a16ee061dccc8c2b1f9、初始 Review b53c1c43c69e3ae3058d74b6163ecfc2bd7d4e95、修复锚点 7af4d46f1114616eb798e5991805a164026c63df，以及后继 docs-only Review SHA, 停止边界：T035–T040 由独立 Slice 2A Issue 驱动并停在 T040，不进入 T041 GREEN, T034 Windows 无计时二元验收通过：首次启动、基础设置、第一份教案、重启读取、当天 Word 在 Microsoft Word 打开均通过

### Community 199 - "Progress Environment Query"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。, Source Nodes

### Community 200 - "Milestone Dependency Query"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: M5 完成后到 M4 的当前依赖路径是什么？, Source Nodes

### Community 201 - "Desktop GUI Prototype Query"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: desktop gui prototype semester date teacherplan renderer word export 室内区域游戏 下午户外游戏 日期选择与校验：C 周计划工作台、用户选择学期起止日期、集体活动编辑空间与 Word 单层编号应由哪些节点和契约约束？, Source Nodes

### Community 202 - "Windows Theme Fix Query"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Windows 下主题颜色白底白字、暗黑模式缺失、缺乏设置选项导致学期无法修改、日期无法一键回到今天，应如何修复？, Source Nodes

### Community 203 - "Manual Testing Query"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 通过人工测试，后台 PS C:\Users\admin\code\child-manager> uv run python -m kindergarten_manager 输出 QFont::setPointSize: Point size <= 0 (-1), must be greater than 0, Source Nodes

### Community 204 - "Timing Acceptance Clarification"
Cohesion: 0.40
Nodes (5): Graphify 查询：通过、未计时、需要计时的事实由来, 历史口径：旧 SC-001 曾要求首次使用五分钟, 历史结论：未计时只证明功能闭环，计时不是当前通过条件, 无需计时：保留首次启动、设置、第一份教案、重启和 Word 打开的五项二元证据, Graphify 查询：不需要计时要求

### Community 205 - "Test Numbering Corrections"
Cohesion: 0.40
Nodes (5): 编号修正：T034 是 Windows 验收；T035–T040 是独立 Slice 2A clean RED，必须停在 T040，不进入 T041 GREEN, Graphify 查询：编号冲突修正与后续步骤, T042 是 AI 凭据实现，不是 Windows 验收, desktop-cloud-retirement.md：旧 Cloud 退役候选工作包, Cloud 退役候选提案未授权且不阻塞当前 Slice 1 或 Slice 2A

### Community 207 - "AI Key Rotation CLI"
Cohesion: 0.60
Nodes (4): CompletedProcess, _run(), test_bootstrap_cli_exposes_rotation_without_master_key_arguments(), test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets()

### Community 209 - "Lesson Plan Calendar Tests"
Cohesion: 0.70
Nodes (4): _calendar(), test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic(), test_out_of_semester_week_number_and_text_are_both_empty(), test_semester_start_week_is_week_one_and_increments_each_monday()

### Community 210 - "Lesson Plan Contracts"
Cohesion: 0.10
Nodes (16): AiGroupActivityStep, DailyReflection, GroupActivityStepCandidate, LessonPlanReference, 按任务冻结的过程长度校验索引；越界必须进入结构错误重试。, _require_nonblank(), _require_question(), _require_statement() (+8 more)

### Community 212 - "Lesson Plan Contract Tests"
Cohesion: 0.83
Nodes (3): _contracts(), test_open_and_write_contracts_do_not_accept_tenant_or_ownership_mutation(), test_plan_snapshot_and_page_contracts_are_bounded_and_stable()

### Community 217 - "Identity Audit Metadata"
Cohesion: 0.22
Nodes (8): UUID, AiGenerationAuditMetadata, AuditEventReference, IdentityAuditMetadata, 身份阶段的稳定审计事件代码与最小资源引用。, 身份审计只允许承载最小、严格类型化的非秘密元数据。, ResourceReference, test_explicit_retry_audit_metadata_contains_ids_but_no_body_or_frozen_input()

### Community 220 - "Local-First Tasks"
Cohesion: 0.67
Nodes (3): Desktop Local-First Tasks, Task Implementation, Test Execution

### Community 301 - "Settings Repository"
Cohesion: 0.13
Nodes (9): CursorResult, DatabaseSource, RuntimeError, sessionmaker, _session_factory(), SettingsRepository, FixedClock, Path (+1 more)

## Ambiguous Edges - Review These
- `Repository Workflow Reset 2026-07-21` → `Combined Audit Conclusion (Q1–Q26)`  [AMBIGUOUS]
  docs/faq/combined-audit.md · relation: conceptually_related_to
- `M2 Milestone` → `M1 Milestone`  [AMBIGUOUS]
  docs/faq/combined-audit.md · relation: conceptually_related_to
- `Q23 Production Deployment Deferral` → `ADR-0009 Defer Production Deployment Until Feature Complete`  [AMBIGUOUS]
  docs/faq/combined-audit.md · relation: conceptually_related_to
- `codex 实现分支（待授权创建）` → `提交 e9a0e77（HEAD = origin/main 共同基线）`  [AMBIGUOUS]
  docs/审查报告/20260714审查报告.md · relation: references
- `trae 实现分支（待授权创建）` → `提交 e9a0e77（HEAD = origin/main 共同基线）`  [AMBIGUOUS]
  docs/审查报告/20260714审查报告.md · relation: references
- `Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界` → `ai_generation_results AI 生成结果预览`  [AMBIGUOUS]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md · relation: conceptually_related_to
- `Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界` → `background_jobs PostgreSQL 权威异步任务`  [AMBIGUOUS]
  graphify-out/memory/query_20260712_071357_一日活动计划系统的数据实体_关系_唯一约束_历史版本_异步任务和安全边界是什么.md · relation: conceptually_related_to

## Knowledge Gaps
- **355 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+350 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **52 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `日期选择与校验` (4× useful, score=2.436076358)
- `theme.py` (2× useful, score=1.971339735)
- `共同实施路线` (2× useful, score=0.975741016)
- `Web、API 与 Worker 服务边界` (2× useful, score=0.975741016)
- `目标服务架构` (2× useful, score=0.975741016)
- `班级与教师配置` (2× useful, score=0.963499175)
- `教案结构化` (2× useful, score=0.963499175)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Repository Workflow Reset 2026-07-21` and `Combined Audit Conclusion (Q1–Q26)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `M2 Milestone` and `M1 Milestone`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Q23 Production Deployment Deferral` and `ADR-0009 Defer Production Deployment Until Feature Complete`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `codex 实现分支（待授权创建）` and `提交 e9a0e77（HEAD = origin/main 共同基线）`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `trae 实现分支（待授权创建）` and `提交 e9a0e77（HEAD = origin/main 共同基线）`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界` and `ai_generation_results AI 生成结果预览`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界` and `background_jobs PostgreSQL 权威异步任务`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._