# Graph Report - child-manager  (2026-08-01)

## Corpus Check
- 395 files · ~239,895 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4064 nodes · 12563 edges · 239 communities (212 shown, 27 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1163 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `31d50f3a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- lesson_plans.py
- SettingsRepository
- test_ai_job_recovery.py
- routers/plans.py
- IdentityRepository
- test_docx_extractor.py
- prompts/service.py
- routers/settings.py
- IdentityError
- ai_models.py
- routers/auth.py
- provision_editable_plan_context
- identity/service.py
- ContractModel
- IdentityAuditEventCode
- Base
- AI Generation & Adoption (async tasks, previews)
- LessonPlanService
- issue_secret
- csrf_headers
- test_webauthn.py
- actors.py
- Child Manager Agent Development Rules
- ai_runner.py
- AiGenerationService
- routers/users.py
- Architecture Decision Index
- LessonPlanRepository
- worker/test_prompt_test_jobs.py
- Speckit Tasks
- pytest
- calendar/service.py
- 历史合并审查
- LessonPlanSourceRepository
- pages/auth.py
- pages/plans.py
- MemoryAuthThrottle
- test_ai_retry_policy.py
- ActorFixture
- CONTEXT.md
- MemoryLoginThrottle
- JobRepository
- create_app
- dependencies.py
- api/test_prompt_test_jobs.py
- AiGenerationResultRepository
- test_plan_ai_contracts.py
- 单一实现开发协议
- ._verify_authentication_transaction
- prompt_test_store.py
- _Connection
- api/app.py
- test_ai_generation_service.py
- test_settings_smoke.py
- test_auth_smoke.py
- test_ai_job_actors.py
- test_backup_authentication.py
- web/app.py
- PostgresPromptTestStore
- require_test_database_url
- test_backup_auth_isolation.py
- Alembic
- UUID
- common.sh
- test_ai_preview_lifecycle.py
- test_group_activity_adoption.py
- test_recovery.py
- test_group_activity_smoke.py
- .adopt
- test_backup_maintenance.py
- ai/client.py
- backend/observability.py
- api_client.py
- Authentication Module
- test_ai_key_rotation.py
- test_settings_permissions.py
- build_health_dependencies
- run_ai_result_maintenance
- test_config.py
- Phase 10: Polish & Cross-Cutting Concerns (M8 Acceptance)
- test_invitations.py
- test_runtime_openapi.py
- ports.py
- Background Job State Machine
- Backup Login Implementation Plan
- test_ai_prompt_settings_smoke.py
- test_ai_model_profiles.py
- test_auth_contract.py
- Export Service (create, list, detail, download with authorization)
- recover_prompt_test_jobs
- test_lesson_plan_sources.py
- SensitiveDatabaseUrl
- test_ai_preview_adoption.py
- test_settings_contract.py
- test_ai_prompt_repositories.py
- test_ai_adoption_service.py
- openapi.py
- broker.py
- test_auth_assurance.py
- totp.py
- test_init_admin_cli.py
- test_backup_auth_contract.py
- test_ai_client.py
- middleware.py
- transactional_session
- resolve_client_ip
- StaticIdentitySecretKeyProvider
- test_local_development_profiles.py
- test_workday_service.py
- test_reflection_service.py
- 安全威胁模型
- test_group_activity_contract.py
- test_0004_settings.py
- test_ai_prompts_jobs_migration.py
- test_secret_encryption.py
- api/__main__.py
- 0007_ai_prompts_jobs.py
- retry_policy.py
- test_0005_password_totp_backup_login.py
- test_ai_batch_generation.py
- test_job_polling.py
- test_openapi_document.py
- test_0009_group_activity_sources.py
- test_password_to_passkey.py
- test_content_v1.py
- test_ai_key_envelope.py
- test_ai_model_url_policy.py
- test_prompt_catalog.py
- 0002_passkey_expand.py
- .__init__
- Child Manager Project Constitution
- test_prompt_renderer.py
- 0009_group_activity_sources.py
- 0001_identity_and_audit.py
- 0004_settings.py
- 0006_lesson_plans.py
- 0008_ai_generation_results.py
- lesson_plans/calendar.py
- test_users_contract.py
- _totp_module
- Retired Dual Agent Protocol
- create-new-feature.sh
- test_csrf.py
- _run
- test_calendar.py
- test_us2_manual_plan_smoke.py
- save_status.py
- GitHub Actions 质量检查工作流
- Classes Table
- Kindergarten Isolation Concept
- Password and TOTP Backup Login Feature
- test_dependency_boundaries.py
- FakeCalendar
- clock.py
- redis.py
- test_alembic_bootstrap.py
- 教案基础先于 AI
- 0000_foundation.py
- leases.py
- Daily Activity Plan Word Layout
- FakeAiClient
- apps/__init__.py
- Audit Web Page (sidebar, filter, pagination)
- apps/worker/__init__.py
- AI Generation Results Table
- AI Model Profile Capabilities Table
- Prompt Definitions Table
- Roles Table
- Implementation Plan
- Database Backend Setup
- Common Passwords List
- Backend Module
- Shared Contracts Module
- Prerequisites Script
- Setup Plan Script
- Setup Tasks Script
- Package Skeleton Tests
- Error Handling Tests
- test_password_to_passkey.py
- Web Tests Module
- IdentityServiceDependency
- apps/api/__init__.py
- Audit Router (HTTP filter, pagination, detail)
- routers/__init__.py
- le
- Query
- AsyncBaseTransport
- Export History Component
- components/__init__.py
- apps/web/__init__.py
- pages/__init__.py
- Account Invitations Table
- Account Recovery Requests Table
- Age Groups Table
- Audit Events Table
- Roles Table
- test_ai_batch_generation.py
- test_0009_group_activity_sources.py
- test_0001_identity.py

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
10. `require_csrf()` - 75 edges

## Surprising Connections (you probably didn't know these)
- `Jobs Contracts` --references--> `Background Job State Machine Contract`  [INFERRED]
  packages/contracts/jobs.py → specs/001-daily-activity-plan/contracts/job-state-machine.md
- `WebAuthn 通行密钥认证` --semantically_similar_to--> `WebAuthn/备用登录安全约束`  [INFERRED] [semantically similar]
  docs/ADR/ADR-0010-restricted-public-entry-passkey-authentication-and-recovery.md → .specify/memory/constitution.md
- `Phase 1 Setup (Pre-M1文档门禁与工程初始化)` --references--> `packages/contracts/exports.py 导出契约`  [EXTRACTED]
  specs/001-daily-activity-plan/tasks.md → packages/contracts/exports.py
- `Phase 1 Setup (Pre-M1文档门禁与工程初始化)` --references--> `packages/contracts/identity.py 身份契约`  [EXTRACTED]
  specs/001-daily-activity-plan/tasks.md → packages/contracts/identity.py
- `Phase 1 Setup (Pre-M1文档门禁与工程初始化)` --references--> `packages/contracts/prompts.py 提示词契约`  [EXTRACTED]
  specs/001-daily-activity-plan/tasks.md → packages/contracts/prompts.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
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

## Communities (239 total, 27 thin omitted)

### Community 0 - "lesson_plans.py"
Cohesion: 0.11
Nodes (45): CSRF & Origin Verification, Data Model Design, Database Schema Design, System Architecture, Single-Implementation Development Guide, Combined Audit Conclusion (Q1–Q26), M0-G1 Model & Contract Alignment, M0-G2 Template Instructions Alignment (+37 more)

### Community 1 - "SettingsRepository"
Cohesion: 0.13
Nodes (46): AGENTS.md 开发规则, AES-256-GCM Key Encryption, Autosave / Snapshot Rules, dev Branch, docs Branch, main Branch, codebase-memory MCP, codegraph (+38 more)

### Community 2 - "test_ai_job_recovery.py"
Cohesion: 0.11
Nodes (39): codex 分支 (历史双实现线), dev 分支 (唯一实现与集成), docs 分支 (文档与契约), main 分支 (稳定发布基线), trae 分支 (历史双实现线), Codex Agent, Dev 本地档位 (端口/Compose/数据库隔离), graphify 知识图谱工具与 graphify-out 输出 (+31 more)

### Community 3 - "routers/plans.py"
Cohesion: 0.13
Nodes (35): codex 实现分支（待授权创建）, main 分支（docs-only 基线）, trae 实现分支（待授权创建）, 架构契约 Q13（幂等定义）, CONTEXT.md（项目上下文）, 2026-07-14 编码前审查报告（Codex + Trae 收敛版）, 2026-07-14 编码前审查解决方案, FR-031（原因码与恢复顺序） (+27 more)

### Community 4 - "IdentityRepository"
Cohesion: 0.12
Nodes (28): ADR-0010 Restricted Public Entry & Passkey Auth, ADR-0011 Password+TOTP Backup Login, ADR-0009 Defer Production Deployment Until Feature Complete, Security Threat Model, AES-256-GCM Secret Encryption, Argon2id Password Hashing, External AI Service, FastAPI API (private network) (+20 more)

### Community 5 - "test_docx_extractor.py"
Cohesion: 0.08
Nodes (39): Account Invitations, Account Recovery Requests, Age Groups, AI Generation Results, AI Model Profile Capabilities, AI Model Profiles, Audit Events, Background Jobs (+31 more)

### Community 6 - "prompts/service.py"
Cohesion: 0.07
Nodes (72): lesson_plan_source_service(), _ByteWriter, _check_deadline(), _deadline(), DocxExtractionError, _extract_document_text(), extract_docx_text(), Path (+64 more)

### Community 7 - "routers/settings.py"
Cohesion: 0.05
Nodes (77): ADR-0010 Identity Rewrite, ADR-0011 Password+TOTP Backup, API Application, API Dependencies, API OpenAPI Generation, Auth API Router, Exports API Router, Web API Client (+69 more)

### Community 8 - "IdentityError"
Cohesion: 0.12
Nodes (35): speckit-analyze Skill, speckit-checklist Skill, speckit-clarify Skill, speckit-constitution Skill, speckit-converge Skill, speckit-implement Skill, speckit-plan Skill, speckit-specify Skill (+27 more)

### Community 9 - "ai_models.py"
Cohesion: 0.10
Nodes (40): ADR-0001 Cloud Only, kindergarten_id 园所隔离约束, ADR-0002 独立 Web/API/Worker 模块化单体, background_job 权威任务状态机, ADR-0003 PostgreSQL 权威任务状态 + Dramatiq/Redis, ADR-0004 同源 Cookie 认证, 提示词草稿/发布/回滚生命周期, ADR-0005 AI 供应商中立与提示词系统 (+32 more)

### Community 10 - "routers/auth.py"
Cohesion: 0.12
Nodes (22): AI 生成与提示词规则 (graphify 源节点), python-docx (Word 导出), Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界, age_groups 年龄段, ai_generation_results AI 生成结果预览, audit_events 审计事件, background_jobs PostgreSQL 权威异步任务, class_areas 班级区域(室内/户外) (+14 more)

### Community 11 - "provision_editable_plan_context"
Cohesion: 0.16
Nodes (22): FR-016 七个稳定AI任务与只读默认提示词, 晨间公共变量集 (7变量), daily_activity_plan.afternoon_outdoor_game 下午户外游戏, daily_activity_plan.daily_reflection 一日活动反思, 提示词定义与版本 (草稿/发布/历史), daily_activity_plan.group_activity_add_step 集体活动新增环节, daily_activity_plan.group_activity_split 集体活动拆分, daily_activity_plan.indoor_area_game 室内区域游戏 (+14 more)

### Community 12 - "identity/service.py"
Cohesion: 0.09
Nodes (31): current_session(), AuthenticatedSessionDependency, FastAPI, admin_client(), passkey_client(), MonkeyPatch, TestClient, 通过 FastAPI 身份依赖注入建立已 step-up 管理员，不借用密码登录。 (+23 more)

### Community 13 - "ContractModel"
Cohesion: 0.06
Nodes (19): _backup_credential(), _backup_enrollment(), BackupCredentialRecord, BackupEnrollmentRecord, BackupRevocationResult, BackupSecurityEventRecord, ChallengeRecord, _credential() (+11 more)

### Community 14 - "IdentityAuditEventCode"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 15 - "Base"
Cohesion: 0.17
Nodes (16): docs/design/data-model.md 数据模型, docs/design/database-schema.md 数据库Schema, docs/design/system-architecture.md 系统架构, docs/PRD/lesson-management.md 产品PRD, specs/001-daily-activity-plan/contracts/openapi.yaml OpenAPI契约, Feature Spec: 首期一日活动计划完整闭环 (M0–M8), FR-078 密码+TOTP两项共同成立的备用登录, SC-001 关闭外部依赖仍可完成手工教案闭环 (+8 more)

### Community 16 - "AI Generation & Adoption (async tasks, previews)"
Cohesion: 0.07
Nodes (77): AiAdoptionServiceDependency, AiGenerationServiceDependency, AiRetryServiceDependency, adopt_ai_preview(), get_ai_preview(), get_job(), alias, CurrentSessionDependency (+69 more)

### Community 17 - "LessonPlanService"
Cohesion: 0.27
Nodes (13): apps/api/ FastAPI路由/中间件/健康检查, apps/web/ NiceGUI BFF与页面, packages/backend/database/migrations/ Alembic 0001–0009, packages/backend/jobs/ai_results.py AI结果仓储 (pending→output), packages/backend/jobs/ 后台任务/幂等/租约/重试, packages/backend/lesson_plans/ai_adoption.py 采用事务, packages/backend/lesson_plans/ai_generation.py 生成受理/batch, packages/backend/lesson_plans/ 教案/快照/归档/恢复 (+5 more)

### Community 18 - "issue_secret"
Cohesion: 0.18
Nodes (13): packages/backend/audit/ 审计仓储与服务, packages/backend/bootstrap/ init-admin/rotate-ai-keys CLI, packages/backend/identity/ 身份/WebAuthn/会话/限流, packages/contracts/identity.py 身份契约, 班级与教师关联, FR-001 首位管理员初始化凭据与双人带外核验, FR-002 WebAuthn可发现凭据与Refresh family, FR-005 教师仅访问关联班级/管理员只读 (+5 more)

### Community 19 - "csrf_headers"
Cohesion: 0.20
Nodes (12): packages/backend/integrations/calendar/ 工作日服务, 一日活动计划 (六栏目/版本/归档), 一日活动反思 (highlights/issues/adjustments), FR-022 同园同班同日唯一教案, FR-028 六栏目结构化Schema与反思200上限, FR-030 版本号并发检测, FR-067 五栏完整后显式生成反思, 教案历史快照 (不可变/带原因) (+4 more)

### Community 20 - "test_webauthn.py"
Cohesion: 0.22
Nodes (10): packages/backend/settings/ 学期/班级/区域/模型档案, packages/contracts/audit.py 审计契约, packages/contracts/common.py 公共错误/分页/幂等契约, packages/contracts/jobs.py 任务契约, packages/contracts/lesson_plans.py 教案契约, packages/contracts/settings.py 设置契约, 班级区域 (室内/户外有序可启停), FR-011 室内/户外有序区域维护 (+2 more)

### Community 21 - "actors.py"
Cohesion: 0.31
Nodes (9): OpenAI-Compatible Model Service, FastAPI API (apps/api), Export Storage Seam, Holiday Adapter, Key Source Seam, PostgreSQL, Redis, NiceGUI Web / BFF (apps/web) (+1 more)

### Community 22 - "Child Manager Agent Development Rules"
Cohesion: 0.14
Nodes (15): AuditRepository, _challenge_digest(), _client_challenge(), _decode_base64url(), IdentityError, IdentityService, ManagedUser, Any (+7 more)

### Community 23 - "ai_runner.py"
Cohesion: 0.25
Nodes (9): packages/backend/integrations/crypto/ai_keys.py 密钥信封, packages/backend/jobs/ai_runner.py AI执行Runner, packages/backend/jobs/retry_policy.py 重试分类/退避, packages/backend/prompts/ 提示词目录/生命周期/渲染, packages/backend/prompts/renderer.py 白名单纯替换渲染器, packages/contracts/prompts.py 提示词契约, FR-019 提示词变量白名单与占位符词法, US3 管理员配置模型与提示词 (P3) (+1 more)

### Community 24 - "AiGenerationService"
Cohesion: 0.25
Nodes (8): packages/backend/integrations/ai/ 供应商中立AI客户端/URL策略, AI生成预览 (短期结构化候选), AI模型档案 (地址/密钥密文/能力/revision), 审计事件 (脱敏/保留一年), 后台任务 (权威状态/幂等/retry谱系), FR-037 ai.batch父任务与pending_dispatch, FR-041 显式采用与预览有效性双哈希, 提示词测试记录 (冻结上下文/脱敏摘要)

### Community 25 - "routers/users.py"
Cohesion: 0.29
Nodes (7): apps/worker/ Dramatiq Broker/Actor/Scheduler, packages/contracts/exports.py 导出契约, FR-049 导出同事务冻结快照, FR-054 导出文件名 一日活动计划_{班级}_{YYYY-MM-DD}.docx, US6 教师导出并重新下载固定Word (P6), Word导出记录 (独立副本/哈希), Phase 8 US6 固定Word导出与历史

### Community 26 - "Architecture Decision Index"
Cohesion: 0.33
Nodes (7): packages/backend/integrations/files/docx.py DOCX安全提取, packages/backend/lesson_plans/group_activity_ai.py 集体活动AI, FR-044 集体活动仅文本/.docx来源, FR-047 新增适龄环节结构化标记is_ai_added, 集体活动来源 (文本/.docx 提取记录), US5 教师处理集体活动原始教案 (P5), Phase 7 US5 集体活动导入与生成

### Community 27 - "LessonPlanRepository"
Cohesion: 0.60
Nodes (6): 共同实施路线, 当前仓库与分支状态, Web、API 与 Worker 服务边界, 目标服务架构, 查询记录 2026-07-11 02:19：接下来需要生成什么文件, 查询记录 2026-07-11 02:42：系统架构文档要素

### Community 28 - "worker/test_prompt_test_jobs.py"
Cohesion: 0.10
Nodes (60): AgeGroup, AiModelProfile, AiModelServiceDependency, _age_group(), _ai_model(), _area(), _class(), create_ai_model_profile() (+52 more)

### Community 41 - "JobRepository"
Cohesion: 0.11
Nodes (33): AiJobScopeResolver, AiRunner, build_ai_job_runner(), build_ai_result_repository(), build_prompt_test_executor(), build_word_export_runner(), build_worker_scope_resolver(), _native_url() (+25 more)

### Community 42 - "create_app"
Cohesion: 0.08
Nodes (49): ContractModel, BaseModel, AdminCredentialRevocationResult, AuthenticationCredential, AuthenticationCredentialResponse, AuthenticationPublicKey, AuthenticationResult, AuthenticatorSelection (+41 more)

### Community 43 - "dependencies.py"
Cohesion: 0.29
Nodes (12): _pinned_url(), Any, OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。, _addresses(), AiUrlPolicyError, Resolver, ValueError, AI 模型地址的保存时与连接前 SSRF 防护。 (+4 more)

### Community 44 - "api/test_prompt_test_jobs.py"
Cohesion: 0.09
Nodes (43): DeclarativeBase, AuditEvent, Base, DailyActivityPlanExport, Word 导出 SQLAlchemy 模型。, AccountInvitation, AccountRecoveryRequest, BackupAuthCredential (+35 more)

### Community 45 - "AiGenerationResultRepository"
Cohesion: 0.14
Nodes (37): csrf_headers(), _base64url(), _credential(), MonkeyPatch, TestClient, _registration_credential(), test_authentication_options_are_username_less_and_browser_ready(), test_authentication_options_do_not_increment_failure_limit() (+29 more)

### Community 46 - "test_plan_ai_contracts.py"
Cohesion: 0.30
Nodes (7): ExportRecord, ExportRepository, Any, 园所范围 Word 导出 PostgreSQL Repository。, 所有查询和变更都同时约束 ``kindergarten_id``。, _record(), _uuid()

### Community 47 - "单一实现开发协议"
Cohesion: 0.11
Nodes (25): prompt_service(), PromptTemplateError, Any, ValueError, 仅支持固定白名单纯替换词法的提示词渲染器。, render_prompt(), _render_value(), validate_prompt_template() (+17 more)

### Community 48 - "._verify_authentication_transaction"
Cohesion: 0.13
Nodes (18): append_ai_event(), Any, UUID, UUID, UUID, AI 生成任务的冻结上下文执行器与 PostgreSQL 状态适配器。, UUID, 显式一日活动反思的预保存与 AI 任务受理事务。 (+10 more)

### Community 49 - "prompt_test_store.py"
Cohesion: 0.11
Nodes (43): create_completed_ai_preview(), provision_enabled_ai_model(), TestClient, UUID, TestClient, test_generation_reject_adopt_and_retry_write_sanitized_audit_rows(), _generation_headers(), MonkeyPatch (+35 more)

### Community 50 - "_Connection"
Cohesion: 0.11
Nodes (16): AiClientError, RuntimeError, CurrentModelCallProfile, ProfileCallLimiter, PromptTestAuthorizer, PromptTestExecutionContext, PromptTestExecutor, PromptTestRetry (+8 more)

### Community 51 - "api/app.py"
Cohesion: 0.28
Nodes (6): ai_generation_service(), AiGenerationAcceptance, AiGenerationService, Any, UUID, validate_prompt_variables()

### Community 52 - "test_ai_generation_service.py"
Cohesion: 0.38
Nodes (32): PromptSpec, AiAreaGame, AiDailyReflection, AiGroupActivity, AiMorningActivity, AiMorningTalk, AreaGame, GroupActivity (+24 more)

### Community 53 - "test_settings_smoke.py"
Cohesion: 0.05
Nodes (61): AiKeyProvider, settings_service(), IntegrityError, NoReturn, AiModelService, _display(), _key(), _native_url() (+53 more)

### Community 54 - "test_auth_smoke.py"
Cohesion: 0.09
Nodes (21): canonical_export_content_sha256(), Any, _has_valid_frozen_input(), PostgresWordExportStore, Any, datetime, Protocol, RuntimeError (+13 more)

### Community 55 - "test_ai_job_actors.py"
Cohesion: 0.16
Nodes (58): _allowed_origins(), authenticate_with_password_and_totp(), authentication_start(), authentication_verify(), backup_authentication_status(), bootstrap_options(), bootstrap_verify(), _check_public_throttle() (+50 more)

### Community 56 - "test_backup_authentication.py"
Cohesion: 0.10
Nodes (40): ChallengeBinding, ChallengePurpose, ChallengeRecord, consume_challenge(), issue_challenge(), IssuedChallenge, datetime, StrEnum (+32 more)

### Community 57 - "web/app.py"
Cohesion: 0.05
Nodes (83): JobMessage, Redis 中唯一允许传递的最小任务消息。, _insert_job(), _insert_other_tenant_plan(), _insert_result(), _native_url(), _provision_dependencies(), TestClient (+75 more)

### Community 58 - "PostgresPromptTestStore"
Cohesion: 0.17
Nodes (10): _Cell, DocumentType, Any, Path, ValueError, 固定 teacherplan.docx 副本渲染器。, 只读取固定模板，并在内存副本中替换已确认字段。, TeacherplanRenderer (+2 more)

### Community 59 - "require_test_database_url"
Cohesion: 0.09
Nodes (43): ArgumentParser, activate_initialization(), migrate_passkeys(), _native_url(), datetime, UUID, 首位管理员的部署控制台初始化与双人核验激活。, 仅在通行密钥已登记并完成两位预登记人员核验后激活。 (+35 more)

### Community 60 - "test_backup_auth_isolation.py"
Cohesion: 0.33
Nodes (13): _base64url(), _create_teacher(), _issue(), MonkeyPatch, TestClient, _registration_credential(), _secret_bytes(), test_invitation_is_single_use_reissuable_and_revocable() (+5 more)

### Community 61 - "Alembic"
Cohesion: 0.06
Nodes (59): job_query_service(), _accepted(), create_export(), download_export(), _export(), get_export(), _job(), list_exports() (+51 more)

### Community 62 - "UUID"
Cohesion: 0.11
Nodes (25): export_file_download(), plan_api_request(), plan_docx_preview_request(), 通过同源 BFF 提取 DOCX，返回待教师确认的临时文本。, 只通过同源 BFF 访问教案及其任务端点。, 通过同源 fetch 下载受保护文件，并保留 API 错误反馈。, AiSectionAction, preview_title() (+17 more)

### Community 63 - "common.sh"
Cohesion: 0.19
Nodes (32): activate(), create_user(), credential_revoke(), credentials(), deactivate(), get_user(), _invitation(), invitation_issue() (+24 more)

### Community 64 - "test_ai_preview_lifecycle.py"
Cohesion: 0.13
Nodes (31): Element, _complete_plan(), _export(), MonkeyPatch, T132 Word 导出保存、确认、轮询、历史与下载 RED 冒烟。, test_download_failure_uses_server_chinese_feedback(), test_download_javascript_failure_logs_only_sanitized_diagnostic(), test_empty_reflection_exports_current_editor_content_polls_and_keeps_two_histories() (+23 more)

### Community 65 - "test_group_activity_adoption.py"
Cohesion: 0.12
Nodes (12): AiExecutionContext, AiJobAuthorizer, AiJobStore, AiJobStoreProtocol, _log_sanitized_exception(), Any, datetime, Exception (+4 more)

### Community 66 - "test_recovery.py"
Cohesion: 0.15
Nodes (26): ActorFixture, TestClient, test_admin_is_restricted_until_complete_backup_enrollment(), test_backup_status_and_enrollment_require_authentication(), test_enrollment_requires_password_and_totp_together_and_is_single_use(), test_expired_enrollment_cannot_enable_backup_auth(), test_new_enrollment_invalidates_the_previous_pending_enrollment(), test_replacing_enabled_material_revokes_only_related_backup_sessions() (+18 more)

### Community 67 - "test_group_activity_smoke.py"
Cohesion: 0.15
Nodes (20): _context(), FakeAuthorizer, FakeClient, FakeStore, _modules(), Any, datetime, UUID (+12 more)

### Community 68 - ".adopt"
Cohesion: 0.15
Nodes (29): _digest(), issue_secret(), IssuedSecret, StrEnum, 生成 256 位一次性秘密，持久化对象中只保留 purpose 绑定摘要。, 以常量时间比较 purpose 绑定摘要。, SecretPurpose, SecretRecord (+21 more)

### Community 69 - "test_backup_maintenance.py"
Cohesion: 0.14
Nodes (15): ai_adoption_service(), AiAdoptionService, _native_url(), AiTaskCode, Any, datetime, JsonValue, UUID (+7 more)

### Community 70 - "ai/client.py"
Cohesion: 0.17
Nodes (31): clear_prompt_tests(), create_prompt_test(), _definition(), get_prompt(), get_prompt_test(), get_prompt_version(), _job(), list_prompt_tests() (+23 more)

### Community 71 - "backend/observability.py"
Cohesion: 0.14
Nodes (20): identity_service(), _aad(), decrypt_totp_secret(), decrypt_totp_secret_with_provider(), encrypt_totp_secret(), encrypt_totp_secret_with_provider(), FileIdentitySecretKeyProvider, Path (+12 more)

### Community 72 - "api_client.py"
Cohesion: 0.33
Nodes (12): admin_session(), CurrentSessionDependency, _provision_associated_teacher(), TestClient, UUID, _session_for(), teacher_client(), test_all_settings_routes_require_authentication() (+4 more)

### Community 73 - "Authentication Module"
Cohesion: 0.09
Nodes (29): map_timor_payload(), AsyncBaseTransport, date, TimorWorkdayClient, WorkdayResult, Any, date, datetime (+21 more)

### Community 74 - "test_ai_key_rotation.py"
Cohesion: 0.26
Nodes (10): lesson_plan_service(), LessonPlanService, OpenPlanResult, PlanView, _PlanViewSeed, date, UUID, 完成单一用例响应；外网解析发生在业务事务关闭之后。 (+2 more)

### Community 75 - "test_settings_permissions.py"
Cohesion: 0.13
Nodes (15): _auth_throttle(), MemoryAuthThrottle, datetime, Redis, timedelta, 公开身份 ceremony 的来源限流公共 seam。, 按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。, 多进程 API 使用的 Redis 固定窗口实现。 (+7 more)

### Community 76 - "build_health_dependencies"
Cohesion: 0.12
Nodes (27): backup_auth_api_request(), backup_login_api_request(), backup_reauthentication_api_request(), 只通过同源 BFF 访问本人备用登录端点。, 以请求正文提交两项备用因素，不把秘密放入 URL。, 为当前备用会话取得仅可新增通行密钥的短时证明。, 读取本人最近 20 条内建安全事件，不产生已读状态。, 从浏览器经同源 BFF 调用 API，并为写请求取得 CSRF token。 (+19 more)

### Community 77 - "run_ai_result_maintenance"
Cohesion: 0.15
Nodes (11): AuthorRecord, LessonPlanRepository, _plan(), PlanCreationContext, PlanRecord, Any, date, UUID (+3 more)

### Community 78 - "test_config.py"
Cohesion: 0.40
Nodes (26): SimpleNamespace, provision_editable_plan_context(), date, TestClient, _complete_content(), _headers(), _native_url(), MonkeyPatch (+18 more)

### Community 79 - "Phase 10: Polish & Cross-Cutting Concerns (M8 Acceptance)"
Cohesion: 0.18
Nodes (21): create_app(), HealthDependencies, check(), dependencies(), Path, test_database_failure_returns_stable_503_code(), test_default_dependencies_check_real_local_runtime(), test_each_optional_dependency_only_degrades_ready_response() (+13 more)

### Community 80 - "test_invitations.py"
Cohesion: 0.16
Nodes (21): chinesecalendar (本地工作日库), Dramatiq 2 + Redis, 旧仓库 adapt_client.py (新增环节参考), 旧仓库 generate_client.py (提示词措辞参考), 旧仓库 lesson_plan_client.py (拆分参考), Psycopg 3, Pydantic 2, PyJWT (HS256 Access Token) (+13 more)

### Community 81 - "test_runtime_openapi.py"
Cohesion: 0.17
Nodes (10): _digest(), MemoryLoginThrottle, datetime, Redis, timedelta, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision (+2 more)

### Community 82 - "ports.py"
Cohesion: 0.09
Nodes (27): ExportAcceptance, ExportDownload, _native_url(), Word 导出创建、历史、详情与实时授权下载用例。, build_display_filename(), ExportStorage, new_storage_key(), Path (+19 more)

### Community 83 - "Background Job State Machine"
Cohesion: 0.24
Nodes (16): ai_admin_client(), _profile_payload(), Any, TestClient, _resolver(), test_admin_creates_write_only_masked_profile_and_cannot_read_key(), test_call_fields_increment_revision_but_display_and_limits_do_not(), test_disable_preserves_profile_and_default_switch_is_tenant_local() (+8 more)

### Community 84 - "Backup Login Implementation Plan"
Cohesion: 0.40
Nodes (3): export_service(), ExportService, UUID

### Community 85 - "test_ai_prompt_settings_smoke.py"
Cohesion: 0.18
Nodes (18): login_page_text(), users_page_text(), BrowserContext, Page, _add_virtual_authenticator(), _auth_cookie_names(), _bootstrap_activate(), _bootstrap_start() (+10 more)

### Community 86 - "test_ai_model_profiles.py"
Cohesion: 0.22
Nodes (4): StaticIdentitySecretKeyProvider, MonkeyPatch, test_service_generates_persisted_enrollment_id_before_encrypting_totp_aad(), _Transaction

### Community 87 - "test_auth_contract.py"
Cohesion: 0.19
Nodes (16): Any, 向已注册 actor 投递唯一的 job_id。, RedisJobDispatcher, AiRecoveryStore, AiResultMaintenanceCounts, AiResultMaintenanceRepository, datetime, Protocol (+8 more)

### Community 88 - "Export Service (create, list, detail, download with authorization)"
Cohesion: 0.23
Nodes (6): _native_url(), PostgresPromptTestStore, Any, datetime, UUID, 提示词测试 Worker 的 PostgreSQL 权威状态适配器。

### Community 89 - "recover_prompt_test_jobs"
Cohesion: 0.10
Nodes (26): Actor, Broker, register_actors(), build_test_broker(), 生产 Redis 与确定性测试消息代理装配。, StubBroker, test_test_broker_registers_minimal_actor_without_redis(), test_worker_keeps_running_until_stop_is_requested() (+18 more)

### Community 90 - "test_lesson_plan_sources.py"
Cohesion: 0.39
Nodes (5): normalize_phone(), normalize_username(), test_invalid_phone_is_rejected(), test_phone_is_mainland_e164_or_empty(), test_username_is_nfkc_trimmed_and_lowercase()

### Community 91 - "SensitiveDatabaseUrl"
Cohesion: 0.23
Nodes (12): AiGenerationResultRecord, AiGenerationResultRepository, _json_object(), _optional_uuid(), Any, datetime, 同园隔离的 AI 生成结果 Repository。, 将同园到期预览条件收敛为 expired，不修改结果正文或决策字段。 (+4 more)

### Community 92 - "test_ai_preview_adoption.py"
Cohesion: 0.17
Nodes (16): navigation_for_capabilities(), 按 API capabilities 生成导航。, class_areas_page_text(), settings_page_text(), test_navigation_is_derived_from_current_api_capabilities(), BrowserActor, _free_port(), _m3_services() (+8 more)

### Community 93 - "test_settings_contract.py"
Cohesion: 0.20
Nodes (16): AiJobRetry, RuntimeError, 通知消息代理按权威任务给出的退避时间重投。, _ai_actor(), FakeRunner, FakeScopeResolver, PartiallyFailingRecoveryStore, datetime (+8 more)

### Community 94 - "test_ai_prompt_repositories.py"
Cohesion: 0.34
Nodes (14): _FrozenTask, _TaskSpec, AiBatchRequest, AiGenerationRequest, _native_url(), TestClient, UUID, RecordingDispatcher (+6 more)

### Community 95 - "test_ai_adoption_service.py"
Cohesion: 0.16
Nodes (14): _export_payload(), _job_payload(), Any, UUID, T127 固定 Word 导出公共契约 RED。, _required(), test_confirmation_required_error_is_closed_and_carries_only_export_sections(), test_export_fingerprint_includes_actual_plan_path() (+6 more)

### Community 96 - "openapi.py"
Cohesion: 0.36
Nodes (9): create_access_token(), decode_access_token(), generate_refresh_token(), Any, datetime, Access JWT 与 opaque Refresh token 接缝。, test_access_token_contains_minimal_identity_and_fifteen_minute_expiry(), test_access_token_expires() (+1 more)

### Community 97 - "broker.py"
Cohesion: 0.33
Nodes (17): FailingDispatcher, prompt_job_client(), _provision_model_and_version(), Any, TestClient, _resolver(), test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure(), test_draft_version_can_be_tested_before_publication() (+9 more)

### Community 98 - "test_auth_assurance.py"
Cohesion: 0.11
Nodes (18): 1. 恢复时先确认的基线, 2.1 已完成, 2.2 已验证门禁, 2.3 尚未实现, 2. 当前实现进度, 3. 下一步：只从 T016 开始, 4.1 项目必须项, 4.2 当前主机已发现的工具缺口 (+10 more)

### Community 99 - "totp.py"
Cohesion: 0.30
Nodes (18): _base64url(), _enable_backup(), _generic_failure_payload(), MonkeyPatch, Response, TestClient, _registration_credential(), _request() (+10 more)

### Community 100 - "test_init_admin_cli.py"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 101 - "test_backup_auth_contract.py"
Cohesion: 0.22
Nodes (16): missing_export_sections(), ExportSection, 返回需要二次确认的五栏；反思永远不参与确认。, _area_complete(), content_completeness(), EditableContent, _group_activity_complete(), _morning_activity_complete() (+8 more)

### Community 102 - "test_ai_client.py"
Cohesion: 0.23
Nodes (11): hash_password(), password_needs_rehash(), password_violations(), Path, verify_password(), _weak_passwords(), datetime, Path (+3 more)

### Community 103 - "middleware.py"
Cohesion: 0.25
Nodes (13): MonkeyPatch, UUID, RecordingConnection, RecordingResult, _seed_backup_repository(), test_admin_role_gate_restricts_and_then_releases_webauthn_sessions(), test_backup_credential_reads_are_scoped_to_kindergarten_and_user(), test_backup_version_change_revokes_only_related_sessions() (+5 more)

### Community 104 - "transactional_session"
Cohesion: 0.15
Nodes (15): _error_response(), _identity_error_response(), FastAPI, Request, UUID, FastAPI 应用装配、统一异常转换与健康端点。, _request_id(), API 请求 ID 与追踪 ID 中间件。 (+7 more)

### Community 105 - "resolve_client_ip"
Cohesion: 0.31
Nodes (15): MonkeyPatch, Path, test_environment_test_database_url_takes_precedence_over_profile(), test_test_database_profile_must_stay_outside_the_repository(), test_test_database_profile_rejects_group_or_other_access(), test_test_database_url_rejects_nonisolated_or_nonpostgresql_targets(), test_test_database_url_reports_missing_environment_and_profile(), test_test_database_url_uses_secure_repo_external_profile() (+7 more)

### Community 106 - "StaticIdentitySecretKeyProvider"
Cohesion: 0.22
Nodes (14): merge_request_context(), EventDict, 递归清除日志中的密钥、令牌、认证材料与 URL 凭证。, 将当前请求关联字段合并到真实 structlog 事件。, _redact(), redact_mapping(), _redact_url(), request_context() (+6 more)

### Community 107 - "test_local_development_profiles.py"
Cohesion: 0.16
Nodes (17): prompt_spec(), Any, BaseModel, 固定提示词目录、输入与结果 Schema 路由。, _spec(), validate_prompt_result(), validate_prompt_result_schema(), _contract() (+9 more)

### Community 108 - "test_workday_service.py"
Cohesion: 0.16
Nodes (12): AiGroupActivityStep, GroupActivityStepCandidate, LessonPlanReference, 按任务冻结的过程长度校验索引；越界必须进入结构错误重试。, _require_nonblank(), _require_question(), _require_statement(), _validate_group_add_step_index() (+4 more)

### Community 109 - "test_reflection_service.py"
Cohesion: 0.43
Nodes (15): _complete_preview(), _headers(), _native_url(), _prepare_adopted_split(), Any, TestClient, UUID, _request_generation() (+7 more)

### Community 110 - "安全威胁模型"
Cohesion: 0.21
Nodes (12): BffResponse, proxy_request(), AsyncBaseTransport, NiceGUI 服务端 BFF 客户端的公开接缝。, 按固定 allowlist 转发请求，并保留响应原始多值头。, HTTPX (外部 HTTP 客户端), MonkeyPatch, test_plan_docx_preview_request_forwards_csrf_cookie_and_multipart() (+4 more)

### Community 111 - "test_group_activity_contract.py"
Cohesion: 0.19
Nodes (18): Repository Workflow Reset 2026-07-21, Codex Agent, dev Branch (Codex implementation branch), Development Flow (需求→docs→Issue→dev→测试→Review→main), docs Branch (single source of truth), M2 Parent Issue #4 (shared parent → dev acceptance entry), M2 Codex Issue #5 (implementation & acceptance evidence), M2 Trae Issue #6 (closed not planned) (+10 more)

### Community 112 - "test_0004_settings.py"
Cohesion: 0.35
Nodes (10): _candidate(), FakeStore, _modules(), Any, UUID, test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it(), test_rotation_dry_run_and_repeated_batch_are_zero_write(), test_rotation_uses_stable_cursor_and_does_not_change_call_revision() (+2 more)

### Community 113 - "test_ai_prompts_jobs_migration.py"
Cohesion: 0.25
Nodes (11): main(), 仅绑定回环地址的 NiceGUI Web 入口。, _require_loopback(), _validate_cookie_security(), configure_logging(), EventDict, 递归清除 Web 日志中的凭证和内部 URL。, _redact() (+3 more)

### Community 114 - "test_secret_encryption.py"
Cohesion: 0.23
Nodes (20): Event, lesson_plan_database(), MonkeyPatch, test_0006_creates_tenant_scoped_plan_snapshot_author_and_cache_tables(), test_database_contains_unique_cas_week_and_unavailable_constraints(), identity_database(), _insert_kindergarten(), _insert_user() (+12 more)

### Community 115 - "api/__main__.py"
Cohesion: 0.25
Nodes (12): AppSettings, global_security_ready(), BaseModel, JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。, MonkeyPatch, settings(), test_api_entrypoint_rejects_insecure_cookie_on_non_loopback(), test_development_insecure_cookie_requires_loopback_binding() (+4 more)

### Community 116 - "0007_ai_prompts_jobs.py"
Cohesion: 0.17
Nodes (10): AiClient, Clock, DependencyCheck, JobBroker, date, datetime, Protocol, UUID (+2 more)

### Community 117 - "retry_policy.py"
Cohesion: 0.40
Nodes (12): _change_actor_to_teacher(), _enable_backup(), _identity_service(), _login_with_backup(), _native_url(), TestClient, test_admin_cannot_disable_required_backup_authentication(), test_backup_maintenance_and_security_events_require_authentication() (+4 more)

### Community 118 - "test_0005_password_totp_backup_login.py"
Cohesion: 0.37
Nodes (14): _assert_operation_contract(), _canonical_schema(), _effective_security(), _operations(), _parameter_shape(), Any, 运行时 OpenAPI 与冻结身份契约的一致性门禁。, _request_schema() (+6 more)

### Community 119 - "test_ai_batch_generation.py"
Cohesion: 0.26
Nodes (15): apps/api FastAPI API, apps/web NiceGUI Web + BFF, apps/worker Dramatiq Worker, BFF 服务端转发层 (Backend for Frontend), NiceGUI 3.x, packages/backend 领域/应用/Repository, packages/contracts 稳定契约, Phase 1 Setup T001–T008 (graphify 源节点) (+7 more)

### Community 120 - "test_job_polling.py"
Cohesion: 0.21
Nodes (15): ai_model_service(), _ai_unconfigured(), build_health_dependencies(), _calendar_library_available(), _database_check(), _file_check(), _path_check(), Path (+7 more)

### Community 121 - "test_openapi_document.py"
Cohesion: 0.17
Nodes (10): ai_job_status(), AiJobStatus, prompt_test_status(), PromptTestStatus, 异步提示词测试的稳定中文状态与无障碍语义。, should_poll(), prompt_edit_version_id(), prompt_test_record_text() (+2 more)

### Community 122 - "test_0009_group_activity_sources.py"
Cohesion: 0.22
Nodes (12): candidate_totp_counters(), _counter(), generate_totp(), generate_totp_secret(), _hotp(), RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。, 生成认证器广泛兼容的 160 位无填充 Base32 种子。, 返回当前时间步及相邻一个时间步，按 counter 递增排序。 (+4 more)

### Community 123 - "test_password_to_passkey.py"
Cohesion: 0.36
Nodes (12): _base64url(), _insert_credential(), _native_url(), MonkeyPatch, TestClient, UUID, _registration_credential(), test_admin_cannot_revoke_last_active_admin_last_credential() (+4 more)

### Community 124 - "test_content_v1.py"
Cohesion: 0.12
Nodes (24): canonical_request_fingerprint(), ErrorResponse, _normalize_scalar(), Pagination, 跨服务使用的公共 Schema 与规范化函数。, 计算覆盖路由、实际资源与语义输入的 canonical SHA-256。, 统一错误、分页和 Request ID 契约。, test_error_response_has_stable_shape_and_empty_field_errors() (+16 more)

### Community 125 - "test_ai_key_envelope.py"
Cohesion: 0.19
Nodes (7): _job_status_module(), Any, MonkeyPatch, test_controls_have_keyboard_focus_and_error_label_associations(), test_job_status_recovers_configuration_change_with_chinese_action(), test_job_status_refreshes_until_terminal_and_restores_after_page_reload(), test_settings_controls_call_model_prompt_and_job_public_api_seams()

### Community 126 - "test_ai_model_url_policy.py"
Cohesion: 0.21
Nodes (7): APIRoute, Any, _resolve(), _runtime_routes(), test_auth_success_and_logout_lock_two_raw_cookie_headers(), test_runtime_auth_router_matches_frozen_passkey_paths(), test_runtime_auth_success_statuses_match_frozen_contract()

### Community 127 - "test_prompt_catalog.py"
Cohesion: 0.28
Nodes (15): init-admin activate (双人核验后激活), init-admin recover-last-admin (最后管理员 CLI 恢复), init-admin start (首位管理员初始化), Migration 0005 password_totp_backup_login, Migration 0006 lesson_plans, Migration 0007 ai_prompts_jobs, Migration 0008 ai_generation_results, Migration 0009 group_activity_sources (+7 more)

### Community 128 - "0002_passkey_expand.py"
Cohesion: 0.29
Nodes (9): canonical_json_sha256(), generation_input_sha256(), AiTaskCode, JsonValue, 对 JSON 值进行稳定序列化并计算 SHA-256。, 计算逐任务实际输入哈希。      ``server_input`` 只应包含该任务白名单内的服务端输入。采用预览时，调用方必须复用任务     创建时冻结的, section_sha256(), test_generation_input_hash_reuses_frozen_teacher_context_and_current_server_input() (+1 more)

### Community 129 - ".__init__"
Cohesion: 0.20
Nodes (10): str, block_external_network(), isolated_database_url(), _native_psycopg_url(), MonkeyPatch, 只允许回环 TCP 和本机 Unix socket。, 为请求该夹具的测试创建并清理独立 PostgreSQL schema。, 保留连接字符串行为，但禁止失败报告通过 ``repr`` 展开凭据。 (+2 more)

### Community 130 - "Child Manager Project Constitution"
Cohesion: 0.24
Nodes (5): _operation_parameters(), Any, _resolve(), test_age_groups_are_a_fixed_four_item_non_paginated_collection(), test_area_get_uses_default_20_maximum_100_pagination()

### Community 131 - "test_prompt_renderer.py"
Cohesion: 0.30
Nodes (9): _modules(), Any, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_call_configuration_change_set_matches_the_frozen_revision_rules(), test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup(), test_model_reads_and_writes_are_tenant_scoped(), test_prompt_run_frozen_fields_cannot_be_updated() (+1 more)

### Community 132 - "0009_group_activity_sources.py"
Cohesion: 0.29
Nodes (4): ai_retry_service(), AiRetryService, _native_url(), Dispatcher

### Community 133 - "0001_identity_and_audit.py"
Cohesion: 0.29
Nodes (9): _apply_operation_contract(), configure_openapi(), _no_content_response(), _operation(), Any, FastAPI, M2 运行时 OpenAPI 的集中契约装配。, 返回缓存后的 M2 运行时 OpenAPI 生成器。 (+1 more)

### Community 134 - "0004_settings.py"
Cohesion: 0.25
Nodes (7): MonkeyPatch, settings_database(), test_age_group_seed_is_fixed_and_idempotent(), test_area_constraints_allow_empty_collections_but_reject_duplicate_names(), test_postgresql_enforces_semester_and_lead_teacher_uniqueness(), test_settings_migration_creates_the_five_tenant_scoped_tables(), test_settings_relations_use_composite_tenant_foreign_keys()

### Community 135 - "0006_lesson_plans.py"
Cohesion: 0.16
Nodes (14): cryptography (AES-GCM/Argon2id), account_invitations 账号邀请, ai_model_profile_capabilities 模型能力, ai_model_profiles AI 模型档案, backup_auth_credentials 密码+TOTP 备用材料, backup_auth_enrollments 备用绑定流程, recovery_codes 离线恢复码, refresh_tokens 会话刷新令牌族 (+6 more)

### Community 136 - "0008_ai_generation_results.py"
Cohesion: 0.28
Nodes (14): _east_asia_font(), _fixture(), Any, Path, T130 固定 teacherplan.docx 渲染结构与样式 RED。, _render(), _renderer_type(), test_empty_week_and_reflection_keep_fixed_positions_and_three_rows() (+6 more)

### Community 137 - "lesson_plans/calendar.py"
Cohesion: 0.40
Nodes (10): _prepare_last_admin_recovery(), CompletedProcess, MonkeyPatch, UUID, _run_cli(), test_init_admin_activate_requires_two_distinct_pre_registered_approvers(), test_init_admin_cli_exposes_start_activate_and_migration_commands(), test_init_admin_start_creates_pending_account_and_one_time_secret_without_password() (+2 more)

### Community 138 - "test_users_contract.py"
Cohesion: 0.24
Nodes (7): Any, _resolve(), _runtime_routes(), test_backup_contract_marks_request_and_one_time_response_secrets(), test_runtime_router_exposes_the_user_story_2_endpoints(), test_runtime_router_matches_the_frozen_backup_contract(), test_runtime_user_story_2_openapi_matches_frozen_security_and_responses()

### Community 139 - "_totp_module"
Cohesion: 0.55
Nodes (10): _create_pending(), _insert_word_job(), _native_url(), Any, TestClient, UUID, _repository(), test_frozen_context_and_content_cannot_be_updated_after_creation() (+2 more)

### Community 140 - "Retired Dual Agent Protocol"
Cohesion: 0.44
Nodes (10): _modules(), Any, _resolver(), test_client_caps_retry_after_at_sixty_seconds(), test_client_errors_are_stable_and_never_include_key_or_prompt(), test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin(), test_client_posts_openai_compatible_request_with_fixed_limits(), test_client_rejects_redirects_without_following_them() (+2 more)

### Community 141 - "create-new-feature.sh"
Cohesion: 0.25
Nodes (7): m4_database(), MonkeyPatch, test_0007_creates_all_tenant_scoped_ai_prompt_and_job_tables(), test_background_job_batch_and_execution_attempt_constraints_are_frozen(), test_migration_seeds_exactly_seven_system_versions_per_existing_kindergarten(), test_model_activation_and_job_terminal_invariants_are_database_enforced(), test_model_revision_and_prompt_run_frozen_context_are_database_enforced()

### Community 142 - "test_csrf.py"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 143 - "_run"
Cohesion: 0.33
Nodes (8): Collection, parse_trusted_bff_peers(), 只接受显式配置的回环 BFF socket peer。, resolve_client_ip(), test_configured_loopback_bff_peer_can_supply_internal_client_ip(), test_non_loopback_peer_cannot_be_configured_as_trusted_bff(), test_trusted_bff_peers_are_empty_until_explicitly_configured(), test_untrusted_peer_cannot_supply_internal_client_ip()

### Community 144 - "test_calendar.py"
Cohesion: 0.38
Nodes (6): datetime, _session(), test_backup_reauthentication_only_authorizes_add_passkey_for_five_minutes(), test_expired_backup_reauthentication_cannot_add_passkey(), test_recent_webauthn_proof_satisfies_high_risk_identity_boundary(), test_restricted_enrollment_session_cannot_enter_business_routes()

### Community 145 - "test_us2_manual_plan_smoke.py"
Cohesion: 0.49
Nodes (9): _insert_other_kindergarten_plan(), TestClient, UUID, _source_history_total(), _source_url(), test_confirmed_text_creates_metadata_only_and_each_confirmation_is_retained(), test_cross_kindergarten_plan_identifier_is_not_accepted_as_a_source_target(), test_docx_extraction_requires_explicit_confirmation_before_persisting_metadata() (+1 more)

### Community 146 - "save_status.py"
Cohesion: 0.27
Nodes (8): _compose_config(), Any, Path, 双实现本地开发档位的 Compose 合同。, test_compose_accepts_temporary_image_overrides(), test_compose_uses_selected_local_profile(), test_quality_workflow_provides_an_isolated_postgresql_database(), test_test_database_url_requires_an_explicit_profile()

### Community 147 - "GitHub Actions 质量检查工作流"
Cohesion: 0.25
Nodes (7): MonkeyPatch, T129 Word 导出迁移与数据库不变量 RED。, test_0010_can_downgrade_to_0009_and_upgrade_again(), test_export_status_uniqueness_and_success_failure_shapes_are_database_enforced(), test_export_table_has_frozen_input_and_long_term_history_columns(), test_export_uses_same_tenant_composite_foreign_keys(), word_export_database()

### Community 148 - "Classes Table"
Cohesion: 0.29
Nodes (6): _module(), MonkeyPatch, test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls(), test_local_result_wins_conflict_and_uses_one_hour_cache(), test_timor_client_enforces_one_total_deadline(), test_unsupported_local_calendar_range_softly_falls_back_to_online()

### Community 149 - "Kindergarten Isolation Concept"
Cohesion: 0.58
Nodes (9): _completed_preview(), _native_url(), TestClient, UUID, _service(), _session(), test_adopt_is_atomic_and_idempotent(), test_reject_is_atomic_and_idempotent_without_plan_change() (+1 more)

### Community 150 - "Password and TOTP Backup Login Feature"
Cohesion: 0.33
Nodes (4): reflection_generation_service(), _native_url(), Dispatcher, ReflectionGenerationService

### Community 151 - "test_dependency_boundaries.py"
Cohesion: 0.39
Nodes (8): _contract(), Any, US5 集体活动来源与两阶段 AI 契约 RED。, _source_payload(), test_docx_extraction_preview_is_separate_from_confirmed_source_metadata(), test_source_metadata_is_closed_and_never_exposes_original_text_or_attachment(), test_source_page_is_closed_and_preserves_pagination_metadata(), test_split_and_incremental_add_schemas_are_closed_and_validate_index_bounds()

### Community 152 - "FakeCalendar"
Cohesion: 0.36
Nodes (8): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_declares_confirmation_and_generic_word_export_conflicts(), test_openapi_document_is_valid_31(), test_openapi_keeps_nicegui_as_the_only_browser_entry(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 153 - "clock.py"
Cohesion: 0.33
Nodes (11): AI 生成与提示词规则, 班级与教师配置, 一日活动计划, 日期选择与校验, 教案结构化, 园所数据隔离, Word 导出格式控制, Word 模板保护与导出验证 (+3 more)

### Community 154 - "redis.py"
Cohesion: 0.71
Nodes (6): _configure_batch_areas(), _headers(), TestClient, test_each_get_rederives_parent_projection_without_writing_parent_state(), test_plan_job_history_restores_batch_with_exactly_four_children(), test_poll_interval_stays_between_one_and_two_seconds()

### Community 155 - "test_alembic_bootstrap.py"
Cohesion: 0.39
Nodes (8): _context(), _encryption_module(), Any, Path, test_development_key_provider_requires_owner_only_file_outside_repository(), test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution(), test_totp_secret_envelope_round_trips_with_random_96_bit_nonce(), test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce()

### Community 156 - "教案基础先于 AI"
Cohesion: 0.32
Nodes (6): main(), 拒绝在非开发环境或非回环地址关闭 Cookie Secure。, 验证进程启动时的 Cookie 与监听地址组合。, validate_cookie_security(), configure_logging(), 配置 JSON 结构化日志和最终脱敏处理器。

### Community 157 - "0000_foundation.py"
Cohesion: 0.36
Nodes (6): Any, Column, 建立 AI 模型、提示词与 PostgreSQL 权威任务基础。, _seed_defaults(), _timestamps(), upgrade()

### Community 158 - "leases.py"
Cohesion: 0.46
Nodes (7): Script, _backup_revision(), MonkeyPatch, test_backup_auth_migration_creates_isolated_credentials_and_enrollments(), test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(), test_backup_auth_revision_follows_settings_and_precedes_lesson_plans(), test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade()

### Community 159 - "Daily Activity Plan Word Layout"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 160 - "FakeAiClient"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 161 - "apps/__init__.py"
Cohesion: 0.54
Nodes (7): _contracts(), _schemas(), test_completeness_is_independent_from_progressive_schema_validation(), test_empty_v1_content_supports_progressive_manual_editing(), test_reflection_is_nfkc_normalized_and_limited_to_200_codepoints(), test_statement_and_question_punctuation_are_strictly_chinese(), test_unknown_fields_and_unknown_content_versions_are_not_silently_coerced()

### Community 162 - "Audit Web Page (sidebar, filter, pagination)"
Cohesion: 0.39
Nodes (7): _module(), Any, Path, test_ai_key_envelope_rejects_tampering_and_cross_profile_substitution(), test_ai_key_envelope_round_trips_with_random_96_bit_nonce(), test_file_key_provider_requires_owner_only_files_outside_repository(), test_static_key_provider_reads_old_key_but_writes_with_active_key()

### Community 163 - "apps/worker/__init__.py"
Cohesion: 0.57
Nodes (7): _module(), Any, _resolver(), test_policy_accepts_only_allowlisted_public_https_and_checks_every_address(), test_policy_detects_dns_rebinding_before_connect(), test_policy_rejects_non_https_and_non_public_networks(), test_policy_requires_explicit_server_allowlist()

### Community 164 - "AI Generation Results Table"
Cohesion: 0.43
Nodes (7): _module(), Any, test_catalog_assigns_task_specific_minimum_variable_whitelists(), test_catalog_freezes_seven_codes_whitelists_schemas_and_hashes(), test_catalog_input_validation_excludes_teacher_identity_and_unknown_fields(), test_catalog_result_schemas_are_strict(), test_catalog_result_schemas_match_the_frozen_openapi_shapes()

### Community 166 - "Prompt Definitions Table"
Cohesion: 0.52
Nodes (5): Any, Column, _tenant_identity_columns(), _timestamps(), upgrade()

### Community 167 - "Roles Table"
Cohesion: 0.17
Nodes (11): dispatch_after_commit(), Dispatcher, _native_url(), datetime, Protocol, 尽力投递已提交任务；单个 Redis 故障不得回滚或阻断其余子任务。, Any, 新增环节只基于教师已采用并保存的完整当前集体活动。 (+3 more)

### Community 168 - "Implementation Plan"
Cohesion: 0.48
Nodes (6): _module(), Any, test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(), test_renderer_fails_for_missing_variable_before_external_call(), test_renderer_rejects_every_non_frozen_placeholder_form(), test_renderer_uses_stable_json_and_never_recursively_renders_values()

### Community 169 - "Database Backend Setup"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 170 - "Common Passwords List"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 171 - "Backend Module"
Cohesion: 0.20
Nodes (5): Alembic 迁移, Any, Column, _timestamps(), upgrade()

### Community 172 - "Shared Contracts Module"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 174 - "Setup Plan Script"
Cohesion: 0.53
Nodes (5): Any, test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps(), test_totp_rejects_the_same_or_earlier_counter_after_success(), test_totp_secret_is_unique_high_entropy_base32(), _totp_module()

### Community 175 - "Setup Tasks Script"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。, Source Nodes

### Community 176 - "Package Skeleton Tests"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: M5 完成后到 M4 的当前依赖路径是什么？, Source Nodes

### Community 177 - "Error Handling Tests"
Cohesion: 0.60
Nodes (4): CompletedProcess, _run(), test_bootstrap_cli_exposes_rotation_without_master_key_arguments(), test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets()

### Community 178 - "test_password_to_passkey.py"
Cohesion: 0.54
Nodes (7): _assert_passkey_revisions_exist(), _native_url(), MonkeyPatch, test_contract_removes_password_data_and_downgrade_recreates_only_empty_columns(), test_expand_moves_existing_accounts_to_enrollment_and_revokes_old_sessions(), test_passkey_migration_has_explicit_expand_and_contract_boundaries(), _user_columns()

### Community 179 - "Web Tests Module"
Cohesion: 0.70
Nodes (4): _calendar(), test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic(), test_out_of_semester_week_number_and_text_are_both_empty(), test_semester_start_week_is_week_one_and_increments_each_monday()

### Community 181 - "IdentityServiceDependency"
Cohesion: 0.83
Nodes (3): _contracts(), test_open_and_write_contracts_do_not_accept_tenant_or_ownership_mutation(), test_plan_snapshot_and_page_contracts_are_bounded_and_stable()

### Community 186 - "le"
Cohesion: 0.67
Nodes (3): authenticated_session(), IdentityServiceDependency, Cookie

### Community 187 - "Query"
Cohesion: 1.00
Nodes (3): JsonSchemaValue, _render_prompt_test_run_schema(), _render_union_as_one_of()

### Community 236 - "test_ai_batch_generation.py"
Cohesion: 0.71
Nodes (6): _configure_batch_areas(), _idempotent_headers(), TestClient, test_batch_accepts_exactly_four_independent_children_and_derives_parent(), test_batch_database_parent_is_never_executable_or_dispatched(), test_batch_idempotency_replays_original_parent_and_rejects_changed_body()

### Community 237 - "test_0009_group_activity_sources.py"
Cohesion: 0.38
Nodes (6): _columns(), _foreign_keys(), group_activity_source_database(), MonkeyPatch, test_source_table_keeps_only_metadata_and_hash(), test_source_uses_tenant_composite_foreign_keys_for_plan_and_uploader()

### Community 238 - "test_0001_identity.py"
Cohesion: 0.50
Nodes (4): migrated_database(), MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds(), test_identity_migration_is_idempotent()

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
- **143 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+138 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `班级与教师配置` (2× useful, score=1.352895454)

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