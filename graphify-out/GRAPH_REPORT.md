# Graph Report - .  (2026-08-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 4920 nodes · 14183 edges · 274 communities (246 shown, 28 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 1288 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cf106e44`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Combined Audit Conclusion (Q1–Q26)
- CONTEXT.md
- M1 Issue 草稿与执行记录
- 2026-07-14 编码前审查报告（Codex + Trae 收敛版）
- Security Threat Model
- Users
- test_docx_extractor.py
- prompts/service.py
- Spec Kit Constitution
- ROADMAP.md
- 001 研究 research.md
- 晨间公共变量集 (7变量)
- dependencies.py
- IdentityRepository
- common.sh
- Feature Spec: 首期一日活动计划完整闭环 (M0–M8)
- routers/plans.py
- Phase 6 US4 栏目级AI与显式采用/反思
- US1 M2 认证、授权与身份审计
- 一日活动计划 (六栏目/版本/归档)
- Phase 1 Setup (Pre-M1文档门禁与工程初始化)
- FastAPI API (apps/api)
- IdentityError
- Phase 5 US3 模型与提示词配置/异步测试
- 后台任务 (权威状态/幂等/retry谱系)
- Phase 8 US6 固定Word导出与历史
- Phase 7 US5 集体活动导入与生成
- 目标服务架构
- routers/settings.py
- create-new-feature.sh
- 需要直接比较文件
- check-prerequisites.sh
- setup-plan.sh
- setup-tasks.sh
- Backend Package (packages/backend)
- Contracts Package (packages/contracts)
- Integrations Module
- Issue Template Config
- 幼儿园 (Kindergarten)
- 002 Specification Quality Checklist
- 固定 Word 模板 teacherplan.docx
- actors.py
- ContractModel
- AiGenerationService
- Base
- csrf_headers
- identity/service.py
- PromptRepository
- DesktopServices
- test_0008_ai_generation_results.py
- jobs/service.py
- ActorFixture
- contracts/prompts.py
- SettingsRepository
- BootstrapService
- routers/auth.py
- test_webauthn.py
- generation_input_sha256
- TeacherplanRenderer
- AiKeyEnvelope
- DailyPlanPage
- api/app.py
- pages/plans.py
- routers/users.py
- test_export_flow.py
- ai_runner.py
- test_group_activity_sources.py
- worker/test_prompt_test_jobs.py
- test_recovery.py
- runner.py
- JobRepository
- IdentitySecretKeyProvider
- TeacherplanRenderer
- M3A: Password+TOTP Backup Login
- run_ai_result_maintenance
- MemoryAuthThrottle
- pages/auth.py
- lesson_plans/service.py
- provision_editable_plan_context
- create_app
- SensitiveDatabaseUrl
- MemoryLoginThrottle
- Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界
- DesktopMainWindow
- test_init_admin_cli.py
- test_auth_smoke.py
- test_backup_authentication.py
- ExportStorage
- PostgresPromptTestStore
- test_word_export_job.py
- issue_secret
- AiGenerationResultRepository
- test_settings_smoke.py
- AiJobRetry
- daily_plan.py
- ErrorResponse
- routers/prompts.py
- domain/calendar.py
- Dev 跨机器开发交接（2026-07-24）
- RecordingSettingsRepository
- test_ai_generation_presave.py
- middleware.py
- ._load_content
- test_backup_auth_isolation.py
- AiClientError
- api/test_prompt_test_jobs.py
- backend/observability.py
- ReflectionGenerationService
- 0008_ai_generation_results.py
- test_group_activity_adoption.py
- proxy_request
- Repository Workflow Reset 2026-07-21
- FakeStore
- web/__main__.py
- _Connection
- test_config.py
- require_test_database_url
- tasks.md
- 实施计划 plan.md
- test_us2_manual_plan_smoke.py
- FakeDesktopServices
- ExportService
- 001 数据模型 data-model.md
- contracts/lesson_plans.py
- test_backup_maintenance.py
- test_ai_prompt_settings_smoke.py
- test_auth_contract.py
- test_plan_ai_contracts.py
- IdentityAuditEventCode
- test_ai_job_recovery.py
- test_settings_contract.py
- test_ai_prompt_repositories.py
- users 用户
- exports/service.py
- workspace.py
- test_teacherplan_renderer.py
- test_0005_password_totp_backup_login.py
- backend/ports.py
- test_export_repository.py
- test_ai_client.py
- hash_refresh_token
- transactional_session
- resolve_client_ip
- test_reflection_service.py
- T034 Windows 无计时二元验收已完成：首次启动、基础设置、第一份教案、重启读取、当天 Word 在 Windows Microsoft Word 打开均通过
- CancellationToken
- Q: 通过人工测试，后台 PS C:\Users\admin\code\child-manager> uv run python -m kindergarten_manager 输出 QFont::setPointSize: Point size <= 0 (-1), must be greater than 0
- test_workday_service.py
- 查询记录 2026-07-11 02:07：如何撰写 lesson-management PRD
- query_service.py
- test_group_activity_contract.py
- test_openapi_document.py
- test_local_development_profiles.py
- ai_adoption.py
- test_secret_encryption.py
- 4. 实体
- 0007_ai_prompts_jobs.py
- Specification Quality Checklist: 幼儿园管理助手桌面首期
- test_content_v1.py
- _module
- User Scenarios & Testing *(mandatory)*
- _module
- 桌面首期实施后快速验收指南
- 0002_passkey_expand.py
- schemas.py
- _module
- validate_prompt_result_schema
- test_users_contract.py
- _totp_module
- Q: 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。
- Q: M5 完成后到 M4 的当前依赖路径是什么？
- _run
- lesson_plans/test_calendar.py
- test_lesson_plan_contract.py
- FakeCalendar
- clock.py
- redis.py
- configure_logging
- leases.py
- FakeAiClient
- apps/__init__.py
- apps/worker/__init__.py
- backend/database/__init__.py
- NOTICE.md
- backend/__init__.py
- packages/contracts/__init__.py
- tests/web/__init__.py
- child-manager
- 受控 Agent Runtime 契约
- _resolver
- ai_generation.py
- 桌面应用服务契约
- 决策
- ADR-0012：本地优先桌面产品方向重置
- 桌面数据、凭据与备份设计
- 0004_settings.py
- Implementation Plan: 幼儿园管理助手桌面首期
- 桌面首期技术研究与决策
- KMBACKUP1 备份包与恢复契约
- 幼儿园管理助手桌面系统架构
- Word 导出契约
- 桌面界面设计系统
- DailyPlanWorkspace
- 0001_identity_and_audit.py
- 桌面 Slice 1 手工 MVP RED 证据
- implemented
- PlanContentV1
- provision_enabled_ai_model
- test_architecture_boundaries.py
- Frozen Architecture Decisions
- kindergarten_manager/ui/__init__.py
- Alembic 迁移
- canonical_request_fingerprint
- infrastructure/database/migrations/__init__.py
- 0009_group_activity_sources.py
- .require_add_passkey_authorization
- Q: desktop gui prototype semester date teacherplan renderer word export 室内区域游戏 下午户外游戏 日期选择与校验：C 周计划工作台、用户选择学期起止日期、集体活动编辑空间与 Word 单层编号应由哪些节点和契约约束？
- Q: Windows 下主题颜色白底白字、暗黑模式缺失、缺乏设置选项导致学期无法修改、日期无法一键回到今天，应如何修复？
- _render_prompt_test_run_schema

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

## Communities (274 total, 28 thin omitted)

### Community 0 - "Combined Audit Conclusion (Q1–Q26)"
Cohesion: 0.10
Nodes (48): CSRF & Origin Verification, Data Model Design, Database Schema Design, System Architecture, Single-Implementation Development Guide, Combined Audit Conclusion (Q1–Q26), M0-G1 Model & Contract Alignment, M0-G2 Template Instructions Alignment (+40 more)

### Community 1 - "CONTEXT.md"
Cohesion: 0.13
Nodes (45): AGENTS.md 开发规则, AES-256-GCM Key Encryption, Autosave / Snapshot Rules, dev Branch, docs Branch, main Branch, codebase-memory MCP, codegraph (+37 more)

### Community 2 - "M1 Issue 草稿与执行记录"
Cohesion: 0.11
Nodes (39): codex 分支 (历史双实现线), dev 分支 (唯一实现与集成), docs 分支 (文档与契约), main 分支 (稳定发布基线), trae 分支 (历史双实现线), Codex Agent, Dev 本地档位 (端口/Compose/数据库隔离), graphify 知识图谱工具与 graphify-out 输出 (+31 more)

### Community 3 - "2026-07-14 编码前审查报告（Codex + Trae 收敛版）"
Cohesion: 0.13
Nodes (33): codex 实现分支（待授权创建）, main 分支（docs-only 基线）, trae 实现分支（待授权创建）, 架构契约 Q13（幂等定义）, CONTEXT.md（项目上下文）, 2026-07-14 编码前审查报告（Codex + Trae 收敛版）, 2026-07-14 编码前审查解决方案, FR-031（原因码与恢复顺序） (+25 more)

### Community 4 - "Security Threat Model"
Cohesion: 0.12
Nodes (29): ADR-0010 Restricted Public Entry & Passkey Auth, ADR-0011 Password+TOTP Backup Login, ADR-0009 Defer Production Deployment Until Feature Complete, Technology Stack (Python 3.14, NiceGUI, FastAPI, PostgreSQL, SQLAlchemy 2.x, Alembic), Security Threat Model, AES-256-GCM Secret Encryption, Argon2id Password Hashing, External AI Service (+21 more)

### Community 5 - "Users"
Cohesion: 0.08
Nodes (39): Account Invitations, Account Recovery Requests, Age Groups, AI Generation Results, AI Model Profile Capabilities, AI Model Profiles, Audit Events, Background Jobs (+31 more)

### Community 6 - "test_docx_extractor.py"
Cohesion: 0.07
Nodes (71): lesson_plan_source_service(), _ByteWriter, _check_deadline(), _deadline(), DocxExtractionError, _extract_document_text(), extract_docx_text(), Path (+63 more)

### Community 7 - "prompts/service.py"
Cohesion: 0.18
Nodes (14): prompt_service(), PromptTemplateError, Any, ValueError, 仅支持固定白名单纯替换词法的提示词渲染器。, render_prompt(), _render_value(), validate_prompt_template() (+6 more)

### Community 8 - "Spec Kit Constitution"
Cohesion: 0.12
Nodes (35): speckit-analyze Skill, speckit-checklist Skill, speckit-clarify Skill, speckit-constitution Skill, speckit-converge Skill, speckit-implement Skill, speckit-plan Skill, speckit-specify Skill (+27 more)

### Community 9 - "ROADMAP.md"
Cohesion: 0.10
Nodes (42): ADR-0001 Cloud Only, kindergarten_id 园所隔离约束, ADR-0002 独立 Web/API/Worker 模块化单体, background_job 权威任务状态机, ADR-0003 PostgreSQL 权威任务状态 + Dramatiq/Redis, ADR-0004 同源 Cookie 认证, 提示词草稿/发布/回滚生命周期, ADR-0005 AI 供应商中立与提示词系统 (+34 more)

### Community 10 - "001 研究 research.md"
Cohesion: 0.15
Nodes (22): chinesecalendar (本地工作日库), Dramatiq 2 + Redis, NiceGUI 3.x, 旧仓库 adapt_client.py (新增环节参考), 旧仓库 generate_client.py (提示词措辞参考), 旧仓库 lesson_plan_client.py (拆分参考), Psycopg 3, Pydantic 2 (+14 more)

### Community 11 - "晨间公共变量集 (7变量)"
Cohesion: 0.16
Nodes (22): FR-016 七个稳定AI任务与只读默认提示词, 晨间公共变量集 (7变量), daily_activity_plan.afternoon_outdoor_game 下午户外游戏, daily_activity_plan.daily_reflection 一日活动反思, 提示词定义与版本 (草稿/发布/历史), daily_activity_plan.group_activity_add_step 集体活动新增环节, daily_activity_plan.group_activity_split 集体活动拆分, daily_activity_plan.indoor_area_game 室内区域游戏 (+14 more)

### Community 12 - "dependencies.py"
Cohesion: 0.06
Nodes (48): admin_session(), authenticated_session(), current_session(), export_service(), identity_service(), lesson_plan_service(), AuthenticatedSessionDependency, CurrentSessionDependency (+40 more)

### Community 13 - "IdentityRepository"
Cohesion: 0.06
Nodes (19): _backup_credential(), _backup_enrollment(), BackupCredentialRecord, BackupEnrollmentRecord, BackupRevocationResult, BackupSecurityEventRecord, ChallengeRecord, _credential() (+11 more)

### Community 14 - "common.sh"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 15 - "Feature Spec: 首期一日活动计划完整闭环 (M0–M8)"
Cohesion: 0.17
Nodes (16): docs/design/data-model.md 数据模型, docs/design/database-schema.md 数据库Schema, docs/design/system-architecture.md 系统架构, docs/PRD/lesson-management.md 产品PRD, specs/001-daily-activity-plan/contracts/openapi.yaml OpenAPI契约, Feature Spec: 首期一日活动计划完整闭环 (M0–M8), FR-078 密码+TOTP两项共同成立的备用登录, SC-001 关闭外部依赖仍可完成手工教案闭环 (+8 more)

### Community 16 - "routers/plans.py"
Cohesion: 0.07
Nodes (77): AiAdoptionServiceDependency, AiGenerationServiceDependency, AiRetryServiceDependency, adopt_ai_preview(), get_ai_preview(), get_job(), alias, CurrentSessionDependency (+69 more)

### Community 17 - "Phase 6 US4 栏目级AI与显式采用/反思"
Cohesion: 0.27
Nodes (13): apps/api/ FastAPI路由/中间件/健康检查, apps/web/ NiceGUI BFF与页面, packages/backend/database/migrations/ Alembic 0001–0009, packages/backend/jobs/ai_results.py AI结果仓储 (pending→output), packages/backend/jobs/ 后台任务/幂等/租约/重试, packages/backend/lesson_plans/ai_adoption.py 采用事务, packages/backend/lesson_plans/ai_generation.py 生成受理/batch, packages/backend/lesson_plans/ 教案/快照/归档/恢复 (+5 more)

### Community 18 - "US1 M2 认证、授权与身份审计"
Cohesion: 0.18
Nodes (13): packages/backend/audit/ 审计仓储与服务, packages/backend/bootstrap/ init-admin/rotate-ai-keys CLI, packages/backend/identity/ 身份/WebAuthn/会话/限流, packages/contracts/identity.py 身份契约, 班级与教师关联, FR-001 首位管理员初始化凭据与双人带外核验, FR-002 WebAuthn可发现凭据与Refresh family, FR-005 教师仅访问关联班级/管理员只读 (+5 more)

### Community 19 - "一日活动计划 (六栏目/版本/归档)"
Cohesion: 0.20
Nodes (12): packages/backend/integrations/calendar/ 工作日服务, 一日活动计划 (六栏目/版本/归档), 一日活动反思 (highlights/issues/adjustments), FR-022 同园同班同日唯一教案, FR-028 六栏目结构化Schema与反思200上限, FR-030 版本号并发检测, FR-067 五栏完整后显式生成反思, 教案历史快照 (不可变/带原因) (+4 more)

### Community 20 - "Phase 1 Setup (Pre-M1文档门禁与工程初始化)"
Cohesion: 0.22
Nodes (10): packages/backend/settings/ 学期/班级/区域/模型档案, packages/contracts/audit.py 审计契约, packages/contracts/common.py 公共错误/分页/幂等契约, packages/contracts/jobs.py 任务契约, packages/contracts/lesson_plans.py 教案契约, packages/contracts/settings.py 设置契约, 班级区域 (室内/户外有序可启停), FR-011 室内/户外有序区域维护 (+2 more)

### Community 21 - "FastAPI API (apps/api)"
Cohesion: 0.31
Nodes (9): OpenAI-Compatible Model Service, FastAPI API (apps/api), Export Storage Seam, Holiday Adapter, Key Source Seam, PostgreSQL, Redis, NiceGUI Web / BFF (apps/web) (+1 more)

### Community 22 - "IdentityError"
Cohesion: 0.14
Nodes (14): AuditRepository, password_needs_rehash(), IdentityError, IdentityService, ManagedUser, datetime, Exception, UUID (+6 more)

### Community 23 - "Phase 5 US3 模型与提示词配置/异步测试"
Cohesion: 0.25
Nodes (9): packages/backend/integrations/crypto/ai_keys.py 密钥信封, packages/backend/jobs/ai_runner.py AI执行Runner, packages/backend/jobs/retry_policy.py 重试分类/退避, packages/backend/prompts/ 提示词目录/生命周期/渲染, packages/backend/prompts/renderer.py 白名单纯替换渲染器, packages/contracts/prompts.py 提示词契约, FR-019 提示词变量白名单与占位符词法, US3 管理员配置模型与提示词 (P3) (+1 more)

### Community 24 - "后台任务 (权威状态/幂等/retry谱系)"
Cohesion: 0.25
Nodes (8): packages/backend/integrations/ai/ 供应商中立AI客户端/URL策略, AI生成预览 (短期结构化候选), AI模型档案 (地址/密钥密文/能力/revision), 审计事件 (脱敏/保留一年), 后台任务 (权威状态/幂等/retry谱系), FR-037 ai.batch父任务与pending_dispatch, FR-041 显式采用与预览有效性双哈希, 提示词测试记录 (冻结上下文/脱敏摘要)

### Community 25 - "Phase 8 US6 固定Word导出与历史"
Cohesion: 0.29
Nodes (7): apps/worker/ Dramatiq Broker/Actor/Scheduler, packages/contracts/exports.py 导出契约, FR-049 导出同事务冻结快照, FR-054 导出文件名 一日活动计划_{班级}_{YYYY-MM-DD}.docx, US6 教师导出并重新下载固定Word (P6), Word导出记录 (独立副本/哈希), Phase 8 US6 固定Word导出与历史

### Community 26 - "Phase 7 US5 集体活动导入与生成"
Cohesion: 0.33
Nodes (7): packages/backend/integrations/files/docx.py DOCX安全提取, packages/backend/lesson_plans/group_activity_ai.py 集体活动AI, FR-044 集体活动仅文本/.docx来源, FR-047 新增适龄环节结构化标记is_ai_added, 集体活动来源 (文本/.docx 提取记录), US5 教师处理集体活动原始教案 (P5), Phase 7 US5 集体活动导入与生成

### Community 27 - "目标服务架构"
Cohesion: 0.60
Nodes (6): 共同实施路线, 当前仓库与分支状态, Web、API 与 Worker 服务边界, 目标服务架构, 查询记录 2026-07-11 02:19：接下来需要生成什么文件, 查询记录 2026-07-11 02:42：系统架构文档要素

### Community 28 - "routers/settings.py"
Cohesion: 0.10
Nodes (60): AgeGroup, AiModelProfile, AiModelServiceDependency, _age_group(), _ai_model(), _area(), _class(), create_ai_model_profile() (+52 more)

### Community 41 - "actors.py"
Cohesion: 0.09
Nodes (37): Actor, AiJobScopeResolver, AiRunner, build_ai_job_runner(), build_ai_result_repository(), build_prompt_test_executor(), build_word_export_runner(), build_worker_scope_resolver() (+29 more)

### Community 42 - "ContractModel"
Cohesion: 0.07
Nodes (50): ContractModel, BaseModel, AdminCredentialRevocationResult, AuthenticationCredential, AuthenticationCredentialResponse, AuthenticationPublicKey, AuthenticationResult, AuthenticatorSelection (+42 more)

### Community 43 - "AiGenerationService"
Cohesion: 0.26
Nodes (8): ai_generation_service(), AiGenerationService, Any, LessonPlanRepository, SettingsRepository, UUID, validate_prompt_variables(), AiModelProfileRepository

### Community 44 - "Base"
Cohesion: 0.09
Nodes (43): DeclarativeBase, AuditEvent, Base, DailyActivityPlanExport, Word 导出 SQLAlchemy 模型。, AccountInvitation, AccountRecoveryRequest, BackupAuthCredential (+35 more)

### Community 45 - "csrf_headers"
Cohesion: 0.11
Nodes (48): csrf_headers(), _base64url(), _credential(), MonkeyPatch, TestClient, _registration_credential(), test_authentication_options_are_username_less_and_browser_ready(), test_authentication_options_do_not_increment_failure_limit() (+40 more)

### Community 46 - "identity/service.py"
Cohesion: 0.14
Nodes (20): ChallengePurpose, StrEnum, AuthResult, _challenge_digest(), _client_challenge(), _decode_base64url(), _native_url(), Any (+12 more)

### Community 47 - "PromptRepository"
Cohesion: 0.20
Nodes (11): _definition(), prompt_test_input_summary(), PromptDefinitionRecord, PromptRepository, PromptTestRunRecord, PromptVersionRecord, Any, UUID (+3 more)

### Community 48 - "DesktopServices"
Cohesion: 0.12
Nodes (9): DailyPlanContext, DesktopSettingsContext, _setup_complete(), DesktopServices, Any, date, Path, Protocol (+1 more)

### Community 49 - "test_0008_ai_generation_results.py"
Cohesion: 0.13
Nodes (46): _insert_job(), _insert_other_tenant_plan(), _insert_result(), _native_url(), _provision_dependencies(), TestClient, UUID, _result_values() (+38 more)

### Community 50 - "jobs/service.py"
Cohesion: 0.13
Nodes (14): CurrentModelCallProfile, ProfileCallLimiter, PromptTestAuthorizer, PromptTestExecutionContext, PromptTestExecutor, PromptTestRetry, PromptTestStore, datetime (+6 more)

### Community 51 - "ActorFixture"
Cohesion: 0.15
Nodes (33): ActorFixture, prompt_admin_client(), TestClient, test_admin_creates_updates_publishes_and_restores_without_mutating_history(), test_draft_save_and_publish_use_the_same_strict_parser(), test_published_draft_id_is_never_reused_for_the_next_draft(), test_system_catalog_is_seeded_read_only_and_business_effective(), TestClient (+25 more)

### Community 52 - "contracts/prompts.py"
Cohesion: 0.32
Nodes (35): PromptSpec, BaseModel, 固定提示词目录、输入与结果 Schema 路由。, _spec(), AiAreaGame, AiDailyReflection, AiGroupActivity, AiMorningActivity (+27 more)

### Community 53 - "SettingsRepository"
Cohesion: 0.06
Nodes (51): IntegrityError, NoReturn, AgeGroupRecord, _ai_profile(), AiModelProfileRecord, AreaInput, AreaRecord, call_configuration_changed() (+43 more)

### Community 54 - "BootstrapService"
Cohesion: 0.12
Nodes (20): BootstrapService, RuntimeError, StartupError, StartupState, connect_sqlite(), DesktopPaths, Path, resolve_desktop_paths() (+12 more)

### Community 55 - "routers/auth.py"
Cohesion: 0.16
Nodes (58): _allowed_origins(), authenticate_with_password_and_totp(), authentication_start(), authentication_verify(), backup_authentication_status(), bootstrap_options(), bootstrap_verify(), _check_public_throttle() (+50 more)

### Community 56 - "test_webauthn.py"
Cohesion: 0.10
Nodes (33): ChallengeBinding, ChallengeRecord, consume_challenge(), issue_challenge(), IssuedChallenge, datetime, WebAuthn ceremony challenge 的公共领域 seam。, 签发绑定上下文、五分钟有效且只保存摘要的 challenge。 (+25 more)

### Community 57 - "generation_input_sha256"
Cohesion: 0.29
Nodes (9): canonical_json_sha256(), generation_input_sha256(), AiTaskCode, JsonValue, 对 JSON 值进行稳定序列化并计算 SHA-256。, 计算逐任务实际输入哈希。      ``server_input`` 只应包含该任务白名单内的服务端输入。采用预览时，调用方必须复用任务     创建时冻结的, section_sha256(), test_generation_input_hash_reuses_frozen_teacher_context_and_current_server_input() (+1 more)

### Community 58 - "TeacherplanRenderer"
Cohesion: 0.16
Nodes (10): Any, _Cell, DocumentType, Paragraph, Path, ValueError, 固定 teacherplan.docx 副本渲染器。, 只读取固定模板，并在内存副本中替换已确认字段。 (+2 more)

### Community 59 - "AiKeyEnvelope"
Cohesion: 0.10
Nodes (31): AiKeyProvider, UUID, run_rotation(), _aad(), AiKeyEnvelope, decrypt_api_key(), decrypt_api_key_with_provider(), encrypt_api_key() (+23 more)

### Community 60 - "DailyPlanPage"
Cohesion: 0.15
Nodes (10): EditorKind, QDateEdit, QFrame, QLabel, QScrollArea, DailyPlanPage, FieldDefinition, _lines() (+2 more)

### Community 61 - "api/app.py"
Cohesion: 0.10
Nodes (36): FastAPI 应用装配、统一异常转换与健康端点。, _accepted(), create_export(), download_export(), _export(), get_export(), _job(), list_exports() (+28 more)

### Community 62 - "pages/plans.py"
Cohesion: 0.09
Nodes (29): export_file_download(), plan_api_request(), 只通过同源 BFF 访问教案及其任务端点。, 通过同源 fetch 下载受保护文件，并保留 API 错误反馈。, AiSectionAction, preview_title(), 教案 AI 预览的稳定栏目、动作与展示数据。, is_terminal_export_status() (+21 more)

### Community 63 - "routers/users.py"
Cohesion: 0.21
Nodes (31): activate(), create_user(), credential_revoke(), credentials(), deactivate(), get_user(), _invitation(), invitation_issue() (+23 more)

### Community 64 - "test_export_flow.py"
Cohesion: 0.13
Nodes (31): Element, _complete_plan(), _export(), MonkeyPatch, T132 Word 导出保存、确认、轮询、历史与下载 RED 冒烟。, test_download_failure_uses_server_chinese_feedback(), test_download_javascript_failure_logs_only_sanitized_diagnostic(), test_empty_reflection_exports_current_editor_content_polls_and_keeps_two_histories() (+23 more)

### Community 65 - "ai_runner.py"
Cohesion: 0.10
Nodes (20): AiExecutionContext, AiJobAuthorizer, AiJobStore, AiJobStoreProtocol, _log_sanitized_exception(), Any, datetime, Exception (+12 more)

### Community 66 - "test_group_activity_sources.py"
Cohesion: 0.49
Nodes (9): _insert_other_kindergarten_plan(), TestClient, UUID, _source_history_total(), _source_url(), test_confirmed_text_creates_metadata_only_and_each_confirmation_is_retained(), test_cross_kindergarten_plan_identifier_is_not_accepted_as_a_source_target(), test_docx_extraction_requires_explicit_confirmation_before_persisting_metadata() (+1 more)

### Community 67 - "worker/test_prompt_test_jobs.py"
Cohesion: 0.15
Nodes (20): _context(), FakeAuthorizer, FakeClient, FakeStore, _modules(), Any, datetime, UUID (+12 more)

### Community 68 - "test_recovery.py"
Cohesion: 0.14
Nodes (27): 公开身份 ceremony 的来源限流公共 seam。, subject_throttle_source(), hash_password(), password_violations(), Path, verify_password(), _weak_passwords(), _authentication_credential() (+19 more)

### Community 69 - "runner.py"
Cohesion: 0.12
Nodes (14): canonical_export_content_sha256(), Any, _has_valid_frozen_input(), PostgresWordExportStore, Any, datetime, Protocol, RuntimeError (+6 more)

### Community 70 - "JobRepository"
Cohesion: 0.21
Nodes (10): _ai_job(), AiJobRecord, _job(), JobRecord, JobRepository, Any, datetime, PostgreSQL 权威后台任务 Repository。 (+2 more)

### Community 71 - "IdentitySecretKeyProvider"
Cohesion: 0.13
Nodes (22): _aad(), decrypt_totp_secret(), decrypt_totp_secret_with_provider(), encrypt_totp_secret(), encrypt_totp_secret_with_provider(), FileIdentitySecretKeyProvider, Path, UUID (+14 more)

### Community 72 - "TeacherplanRenderer"
Cohesion: 0.17
Nodes (8): _Cell, DocumentType, Paragraph, Path, ValueError, TeacherplanRenderer, TeacherplanTemplateError, Table

### Community 73 - "M3A: Password+TOTP Backup Login"
Cohesion: 0.05
Nodes (76): ADR-0010 Identity Rewrite, ADR-0011 Password+TOTP Backup, API Application, API Dependencies, API OpenAPI Generation, Auth API Router, Exports API Router, Web API Client (+68 more)

### Community 74 - "run_ai_result_maintenance"
Cohesion: 0.19
Nodes (16): Any, 向已注册 actor 投递唯一的 job_id。, RedisJobDispatcher, AiRecoveryStore, AiResultMaintenanceCounts, AiResultMaintenanceRepository, datetime, Protocol (+8 more)

### Community 75 - "MemoryAuthThrottle"
Cohesion: 0.14
Nodes (13): _auth_throttle(), MemoryAuthThrottle, datetime, Redis, timedelta, 按可信来源和 ceremony purpose 分区的确定性滑动窗口替身。, 多进程 API 使用的 Redis 固定窗口实现。, RedisAuthThrottle (+5 more)

### Community 76 - "pages/auth.py"
Cohesion: 0.12
Nodes (28): backup_auth_api_request(), backup_login_api_request(), backup_reauthentication_api_request(), NiceGUI 服务端 BFF 客户端的公开接缝。, 只通过同源 BFF 访问本人备用登录端点。, 以请求正文提交两项备用因素，不把秘密放入 URL。, 为当前备用会话取得仅可新增通行密钥的短时证明。, 读取本人最近 20 条内建安全事件，不产生已读状态。 (+20 more)

### Community 77 - "lesson_plans/service.py"
Cohesion: 0.05
Nodes (53): _calendar_library_available(), map_timor_payload(), AsyncBaseTransport, date, TimorWorkdayClient, WorkdayResult, Any, date (+45 more)

### Community 78 - "provision_editable_plan_context"
Cohesion: 0.25
Nodes (34): SimpleNamespace, provision_editable_plan_context(), date, TestClient, _complete_content(), _headers(), _native_url(), MonkeyPatch (+26 more)

### Community 79 - "create_app"
Cohesion: 0.05
Nodes (65): create_app(), FastAPI, _ai_unconfigured(), build_health_dependencies(), _database_check(), _file_check(), HealthDependencies, _path_check() (+57 more)

### Community 80 - "SensitiveDatabaseUrl"
Cohesion: 0.15
Nodes (12): str, block_external_network(), isolated_database_url(), _LazyTestDatabaseUrl, _native_psycopg_url(), MonkeyPatch, 只在旧 PostgreSQL 测试真正使用 URL 时读取环境配置。, 只允许回环 TCP 和本机 Unix socket。 (+4 more)

### Community 81 - "MemoryLoginThrottle"
Cohesion: 0.17
Nodes (10): _digest(), MemoryLoginThrottle, datetime, Redis, timedelta, Redis 有界窗口实现；测试可使用 MemoryLoginThrottle 确定性替身。, RedisLoginThrottle, ThrottleDecision (+2 more)

### Community 82 - "Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界"
Cohesion: 0.12
Nodes (22): AI 生成与提示词规则 (graphify 源节点), python-docx (Word 导出), Query 2026-07-12: 数据实体/关系/约束/历史/异步/安全边界, age_groups 年龄段, ai_generation_results AI 生成结果预览, audit_events 审计事件, background_jobs PostgreSQL 权威异步任务, class_areas 班级区域(室内/户外) (+14 more)

### Community 83 - "DesktopMainWindow"
Cohesion: 0.16
Nodes (11): ColorScheme, ResolvedTheme, DesktopMainWindow, QWidget, ThemePreference, _validated_theme(), desktop_stylesheet(), ThemePreference (+3 more)

### Community 84 - "test_init_admin_cli.py"
Cohesion: 0.40
Nodes (10): _prepare_last_admin_recovery(), CompletedProcess, MonkeyPatch, UUID, _run_cli(), test_init_admin_activate_requires_two_distinct_pre_registered_approvers(), test_init_admin_cli_exposes_start_activate_and_migration_commands(), test_init_admin_start_creates_pending_account_and_one_time_secret_without_password() (+2 more)

### Community 85 - "test_auth_smoke.py"
Cohesion: 0.12
Nodes (28): login_page_text(), users_page_text(), BrowserContext, candidate_totp_counters(), _counter(), generate_totp(), _hotp(), RFC 6238 TOTP 原语；持久化重放保护由 Repository 完成。 (+20 more)

### Community 86 - "test_backup_authentication.py"
Cohesion: 0.30
Nodes (18): _base64url(), _enable_backup(), _generic_failure_payload(), MonkeyPatch, Response, TestClient, _registration_credential(), _request() (+10 more)

### Community 87 - "ExportStorage"
Cohesion: 0.13
Nodes (19): ExportDownload, build_display_filename(), ExportStorage, new_storage_key(), Path, UUID, 生成不包含内部存储 key 的确定性 Word 下载文件名。, 内部 key 只使用不可猜目录外的 UUID 文件名。 (+11 more)

### Community 88 - "PostgresPromptTestStore"
Cohesion: 0.23
Nodes (6): _native_url(), PostgresPromptTestStore, Any, datetime, UUID, 提示词测试 Worker 的 PostgreSQL 权威状态适配器。

### Community 89 - "test_word_export_job.py"
Cohesion: 0.12
Nodes (21): build_test_broker(), 生产 Redis 与确定性测试消息代理装配。, StubBroker, FailingRenderer, FakeRenderer, FakeStorage, FakeStore, Any (+13 more)

### Community 90 - "issue_secret"
Cohesion: 0.10
Nodes (37): ArgumentParser, activate_initialization(), migrate_passkeys(), _native_url(), datetime, UUID, 首位管理员的部署控制台初始化与双人核验激活。, 仅在通行密钥已登记并完成两位预登记人员核验后激活。 (+29 more)

### Community 91 - "AiGenerationResultRepository"
Cohesion: 0.23
Nodes (12): AiGenerationResultRecord, AiGenerationResultRepository, _json_object(), _optional_uuid(), Any, datetime, 同园隔离的 AI 生成结果 Repository。, 将同园到期预览条件收敛为 expired，不修改结果正文或决策字段。 (+4 more)

### Community 92 - "test_settings_smoke.py"
Cohesion: 0.11
Nodes (20): navigation_for_capabilities(), 按 API capabilities 生成导航。, class_areas_page_text(), prompt_edit_version_id(), prompt_test_record_text(), 刷新时优先恢复未发布草稿，避免用已发布正文覆盖编辑态。, 将服务端已脱敏的测试运行渲染为可读历史记录。, settings_page_text() (+12 more)

### Community 93 - "AiJobRetry"
Cohesion: 0.20
Nodes (16): AiJobRetry, RuntimeError, 通知消息代理按权威任务给出的退避时间重投。, _ai_actor(), FakeRunner, FakeScopeResolver, PartiallyFailingRecoveryStore, datetime (+8 more)

### Community 94 - "daily_plan.py"
Cohesion: 0.22
Nodes (10): BaseException, user_error_message(), Slice 1 结构化一日活动计划编辑页。, build_first_run_daily_plan_window(), build_first_run_page(), QWidget, QWidget, SettingsPage (+2 more)

### Community 95 - "ErrorResponse"
Cohesion: 0.23
Nodes (11): _error_response(), _identity_error_response(), Request, UUID, _request_id(), JSONResponse, ErrorResponse, Pagination (+3 more)

### Community 96 - "routers/prompts.py"
Cohesion: 0.17
Nodes (31): clear_prompt_tests(), create_prompt_test(), _definition(), get_prompt(), get_prompt_test(), get_prompt_version(), _job(), list_prompt_tests() (+23 more)

### Community 97 - "domain/calendar.py"
Cohesion: 0.29
Nodes (9): activity_date_text(), CalendarEvaluation, _chinese_number(), evaluate_calendar(), date, season_for(), teaching_week(), TeachingWeek (+1 more)

### Community 98 - "Dev 跨机器开发交接（2026-07-24）"
Cohesion: 0.11
Nodes (18): 1. 恢复时先确认的基线, 2.1 已完成, 2.2 已验证门禁, 2.3 尚未实现, 2. 当前实现进度, 3. 下一步：只从 T016 开始, 4.1 项目必须项, 4.2 当前主机已发现的工具缺口 (+10 more)

### Community 99 - "RecordingSettingsRepository"
Cohesion: 0.09
Nodes (27): Any, FixedClock, SettingsService, RecordingSettingsRepository, _service(), test_area_failure_rolls_back_whole_aggregate(), test_invalid_first_run_values_are_rejected(), test_minimum_first_run_settings_are_trimmed_and_saved_per_aggregate() (+19 more)

### Community 100 - "test_ai_generation_presave.py"
Cohesion: 0.49
Nodes (9): _generation_headers(), MonkeyPatch, TestClient, test_database_unavailable_returns_503_then_leaves_no_job_or_result(), test_dispatch_failure_after_commit_keeps_202_pending_result(), test_generation_acceptance_creates_pending_result_with_frozen_input(), test_missing_model_configuration_returns_503_and_creates_nothing(), test_single_generation_freezes_the_saved_version_without_mutating_plan() (+1 more)

### Community 101 - "middleware.py"
Cohesion: 0.22
Nodes (7): API 请求 ID 与追踪 ID 中间件。, _request_id(), RequestContextMiddleware, ASGIApp, Receive, Scope, Send

### Community 102 - "._load_content"
Cohesion: 0.33
Nodes (3): Any, _read(), _write()

### Community 103 - "test_backup_auth_isolation.py"
Cohesion: 0.25
Nodes (13): MonkeyPatch, UUID, RecordingConnection, RecordingResult, _seed_backup_repository(), test_admin_role_gate_restricts_and_then_releases_webauthn_sessions(), test_backup_credential_reads_are_scoped_to_kindergarten_and_user(), test_backup_version_change_revokes_only_related_sessions() (+5 more)

### Community 104 - "AiClientError"
Cohesion: 0.09
Nodes (30): BaseTransport, HTTPX (外部 HTTP 客户端), _pinned_url(), ProviderNeutralAiClient, Any, Resolver, OpenAI 兼容、禁止重定向且错误脱敏的供应商中立客户端。, AiClientError (+22 more)

### Community 105 - "api/test_prompt_test_jobs.py"
Cohesion: 0.33
Nodes (17): FailingDispatcher, prompt_job_client(), _provision_model_and_version(), Any, TestClient, _resolver(), test_create_freezes_run_and_job_in_one_transaction_and_returns_202_after_redis_failure(), test_draft_version_can_be_tested_before_publication() (+9 more)

### Community 106 - "backend/observability.py"
Cohesion: 0.22
Nodes (14): merge_request_context(), EventDict, 递归清除日志中的密钥、令牌、认证材料与 URL 凭证。, 将当前请求关联字段合并到真实 structlog 事件。, _redact(), redact_mapping(), _redact_url(), request_context() (+6 more)

### Community 107 - "ReflectionGenerationService"
Cohesion: 0.33
Nodes (4): reflection_generation_service(), _native_url(), Dispatcher, ReflectionGenerationService

### Community 108 - "0008_ai_generation_results.py"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 109 - "test_group_activity_adoption.py"
Cohesion: 0.43
Nodes (15): _complete_preview(), _headers(), _native_url(), _prepare_adopted_split(), Any, TestClient, UUID, _request_generation() (+7 more)

### Community 110 - "proxy_request"
Cohesion: 0.22
Nodes (12): BffResponse, plan_docx_preview_request(), proxy_request(), AsyncBaseTransport, 通过同源 BFF 提取 DOCX，返回待教师确认的临时文本。, 按固定 allowlist 转发请求，并保留响应原始多值头。, MonkeyPatch, test_plan_docx_preview_request_forwards_csrf_cookie_and_multipart() (+4 more)

### Community 111 - "Repository Workflow Reset 2026-07-21"
Cohesion: 0.21
Nodes (17): Repository Workflow Reset 2026-07-21, Codex Agent, dev Branch (Codex implementation branch), Development Flow (需求→docs→Issue→dev→测试→Review→main), docs Branch (single source of truth), M2 Parent Issue #4 (shared parent → dev acceptance entry), M2 Codex Issue #5 (implementation & acceptance evidence), M2 Trae Issue #6 (closed not planned) (+9 more)

### Community 112 - "FakeStore"
Cohesion: 0.35
Nodes (10): _candidate(), FakeStore, _modules(), Any, UUID, test_rotation_cursor_stops_before_a_failed_record_so_resume_retries_it(), test_rotation_dry_run_and_repeated_batch_are_zero_write(), test_rotation_uses_stable_cursor_and_does_not_change_call_revision() (+2 more)

### Community 113 - "web/__main__.py"
Cohesion: 0.25
Nodes (11): main(), 仅绑定回环地址的 NiceGUI Web 入口。, _require_loopback(), _validate_cookie_security(), configure_logging(), EventDict, 递归清除 Web 日志中的凭证和内部 URL。, _redact() (+3 more)

### Community 114 - "_Connection"
Cohesion: 0.05
Nodes (58): migrated_database(), MonkeyPatch, test_identity_migration_creates_tables_extension_and_role_seeds(), test_identity_migration_is_idempotent(), MonkeyPatch, settings_database(), test_age_group_seed_is_fixed_and_idempotent(), test_area_constraints_allow_empty_collections_but_reject_duplicate_names() (+50 more)

### Community 115 - "test_config.py"
Cohesion: 0.25
Nodes (12): AppSettings, global_security_ready(), BaseModel, JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。, MonkeyPatch, settings(), test_api_entrypoint_rejects_insecure_cookie_on_non_loopback(), test_development_insecure_cookie_requires_loopback_binding() (+4 more)

### Community 116 - "require_test_database_url"
Cohesion: 0.31
Nodes (15): MonkeyPatch, Path, test_environment_test_database_url_takes_precedence_over_profile(), test_test_database_profile_must_stay_outside_the_repository(), test_test_database_profile_rejects_group_or_other_access(), test_test_database_url_rejects_nonisolated_or_nonpostgresql_targets(), test_test_database_url_reports_missing_environment_and_profile(), test_test_database_url_uses_secure_repo_external_profile() (+7 more)

### Community 117 - "tasks.md"
Cohesion: 0.33
Nodes (5): 新 docs 基线 SHA：fff6e0908fcb591c927205d53cdbacd35037bce3, 实现代码锚点：cf106e44cb907a4958879a16ee061dccc8c2b1f9, T035–T040：独立 Slice 2A Issue 的 clean RED only，停在 T040, T001–T034 全部已完成，包含 Slice 1 首次启动、设置、保存、重启和当天 Word 闭环, T041 GREEN 在新授权和 Review gate 之前禁止进入

### Community 118 - "实施计划 plan.md"
Cohesion: 0.29
Nodes (14): apps/api FastAPI API, apps/web NiceGUI Web + BFF, apps/worker Dramatiq Worker, BFF 服务端转发层 (Backend for Frontend), packages/backend 领域/应用/Repository, packages/contracts 稳定契约, Phase 1 Setup T001–T008 (graphify 源节点), PostgreSQL (业务与任务权威状态) (+6 more)

### Community 119 - "test_us2_manual_plan_smoke.py"
Cohesion: 0.50
Nodes (3): MonkeyPatch, test_editor_input_debounces_autosave_and_archive_immediately_disables_fields(), test_plan_home_renders_real_views_and_all_frozen_filters()

### Community 120 - "FakeDesktopServices"
Cohesion: 0.26
Nodes (17): _build(), _child(), FakeDesktopServices, Any, LogCaptureFixture, MonkeyPatch, Path, QtBot (+9 more)

### Community 121 - "ExportService"
Cohesion: 0.40
Nodes (3): ExportService, LessonPlanRepository, UUID

### Community 122 - "001 数据模型 data-model.md"
Cohesion: 0.30
Nodes (14): init-admin activate (双人核验后激活), init-admin recover-last-admin (最后管理员 CLI 恢复), init-admin start (首位管理员初始化), Migration 0005 password_totp_backup_login, Migration 0006 lesson_plans, Migration 0007 ai_prompts_jobs, Migration 0008 ai_generation_results, Migration 0009 group_activity_sources (+6 more)

### Community 123 - "contracts/lesson_plans.py"
Cohesion: 0.13
Nodes (15): Any, 新增环节只基于教师已采用并保存的完整当前集体活动。, require_complete_saved_group_activity(), AiGroupActivityStep, GroupActivityStepCandidate, LessonPlanReference, 按任务冻结的过程长度校验索引；越界必须进入结构错误重试。, _require_nonblank() (+7 more)

### Community 124 - "test_backup_maintenance.py"
Cohesion: 0.40
Nodes (12): _change_actor_to_teacher(), _enable_backup(), _identity_service(), _login_with_backup(), _native_url(), TestClient, test_admin_cannot_disable_required_backup_authentication(), test_backup_maintenance_and_security_events_require_authentication() (+4 more)

### Community 125 - "test_ai_prompt_settings_smoke.py"
Cohesion: 0.19
Nodes (7): _job_status_module(), Any, MonkeyPatch, test_controls_have_keyboard_focus_and_error_label_associations(), test_job_status_recovers_configuration_change_with_chinese_action(), test_job_status_refreshes_until_terminal_and_restores_after_page_reload(), test_settings_controls_call_model_prompt_and_job_public_api_seams()

### Community 126 - "test_auth_contract.py"
Cohesion: 0.21
Nodes (7): APIRoute, Any, _resolve(), _runtime_routes(), test_auth_success_and_logout_lock_two_raw_cookie_headers(), test_runtime_auth_router_matches_frozen_passkey_paths(), test_runtime_auth_success_statuses_match_frozen_contract()

### Community 127 - "test_plan_ai_contracts.py"
Cohesion: 0.26
Nodes (12): _children(), _contract(), Any, ModuleType, M6 教案 AI 公共契约的 RED 验收。, test_ai_child_succeeded_is_not_a_valid_batch_completion_state(), test_batch_job_projects_zero_attempts_and_rejects_execution_shape(), test_batch_status_is_derived_only_from_exactly_four_children() (+4 more)

### Community 128 - "IdentityAuditEventCode"
Cohesion: 0.11
Nodes (21): ai_retry_service(), append_ai_event(), Any, UUID, UUID, AiRetryService, _native_url(), Dispatcher (+13 more)

### Community 129 - "test_ai_job_recovery.py"
Cohesion: 0.05
Nodes (59): BackgroundTask, Event, JobMessage, Redis 中唯一允许传递的最小任务消息。, QObject, QRunnable, CommandResult, ErrorCode (+51 more)

### Community 130 - "test_settings_contract.py"
Cohesion: 0.24
Nodes (5): _operation_parameters(), Any, _resolve(), test_age_groups_are_a_fixed_four_item_non_paginated_collection(), test_area_get_uses_default_20_maximum_100_pagination()

### Community 131 - "test_ai_prompt_repositories.py"
Cohesion: 0.30
Nodes (9): _modules(), Any, RecordingConnection, test_all_public_repository_methods_require_explicit_kindergarten_id(), test_call_configuration_change_set_matches_the_frozen_revision_rules(), test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup(), test_model_reads_and_writes_are_tenant_scoped(), test_prompt_run_frozen_fields_cannot_be_updated() (+1 more)

### Community 133 - "users 用户"
Cohesion: 0.16
Nodes (14): cryptography (AES-GCM/Argon2id), account_invitations 账号邀请, ai_model_profile_capabilities 模型能力, ai_model_profiles AI 模型档案, backup_auth_credentials 密码+TOTP 备用材料, backup_auth_enrollments 备用绑定流程, recovery_codes 离线恢复码, refresh_tokens 会话刷新令牌族 (+6 more)

### Community 134 - "exports/service.py"
Cohesion: 0.19
Nodes (13): ExportRecord, ExportRepository, Any, 园所范围 Word 导出 PostgreSQL Repository。, 所有查询和变更都同时约束 ``kindergarten_id``。, _record(), _uuid(), missing_export_sections() (+5 more)

### Community 135 - "workspace.py"
Cohesion: 0.07
Nodes (33): AbstractContextManager, CursorResult, DatabaseSource, create_desktop_window(), _now_utc_ms(), date, Path, QWidget (+25 more)

### Community 136 - "test_teacherplan_renderer.py"
Cohesion: 0.28
Nodes (14): _east_asia_font(), _fixture(), Any, Path, T130 固定 teacherplan.docx 渲染结构与样式 RED。, _render(), _renderer_type(), test_empty_week_and_reflection_keep_fixed_positions_and_three_rows() (+6 more)

### Community 137 - "test_0005_password_totp_backup_login.py"
Cohesion: 0.46
Nodes (7): Script, _backup_revision(), MonkeyPatch, test_backup_auth_migration_creates_isolated_credentials_and_enrollments(), test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(), test_backup_auth_revision_follows_settings_and_precedes_lesson_plans(), test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade()

### Community 138 - "backend/ports.py"
Cohesion: 0.21
Nodes (9): AiClient, Clock, DependencyCheck, JobBroker, datetime, Protocol, UUID, M1 外部边界所需的最小 Protocol。 (+1 more)

### Community 139 - "test_export_repository.py"
Cohesion: 0.55
Nodes (10): _create_pending(), _insert_word_job(), _native_url(), Any, TestClient, UUID, _repository(), test_frozen_context_and_content_cannot_be_updated_after_creation() (+2 more)

### Community 140 - "test_ai_client.py"
Cohesion: 0.44
Nodes (10): _modules(), Any, _resolver(), test_client_caps_retry_after_at_sixty_seconds(), test_client_errors_are_stable_and_never_include_key_or_prompt(), test_client_pins_the_request_to_a_validated_ip_and_preserves_the_tls_origin(), test_client_posts_openai_compatible_request_with_fixed_limits(), test_client_rejects_redirects_without_following_them() (+2 more)

### Community 141 - "hash_refresh_token"
Cohesion: 0.16
Nodes (23): hash_refresh_token(), Access JWT 与 opaque Refresh token 接缝。, _base64url(), _insert_credential(), _native_url(), MonkeyPatch, TestClient, UUID (+15 more)

### Community 142 - "transactional_session"
Cohesion: 0.27
Nodes (7): async_sessionmaker, AsyncSession, 由应用层统一开启事务，并在异常时交给 SQLAlchemy 回滚。, transactional_session(), SessionFactory, Repository 禁止提交与应用事务边界。, test_application_transaction_rolls_back_writes_on_error()

### Community 143 - "resolve_client_ip"
Cohesion: 0.33
Nodes (8): Collection, parse_trusted_bff_peers(), 只接受显式配置的回环 BFF socket peer。, resolve_client_ip(), test_configured_loopback_bff_peer_can_supply_internal_client_ip(), test_non_loopback_peer_cannot_be_configured_as_trusted_bff(), test_trusted_bff_peers_are_empty_until_explicitly_configured(), test_untrusted_peer_cannot_supply_internal_client_ip()

### Community 144 - "test_reflection_service.py"
Cohesion: 0.47
Nodes (8): _complete_content(), _native_url(), PlanContentV1, TestClient, _service(), _session(), test_incomplete_reflection_acceptance_rolls_back_and_key_remains_available(), test_reflection_acceptance_saves_once_without_snapshot_and_replays()

### Community 145 - "T034 Windows 无计时二元验收已完成：首次启动、基础设置、第一份教案、重启读取、当天 Word 在 Windows Microsoft Word 打开均通过"
Cohesion: 0.18
Nodes (13): docs SHA fff6e0908fcb591c927205d53cdbacd35037bce3；实现锚点 cf106e44cb907a4958879a16ee061dccc8c2b1f9；CI run 31392074261 attempt 2 completed/success，headSha=cf106e44cb907a4958879a16ee061dccc8c2b1f9, desktop-slice-1-acceptance.md：桌面 Slice 1 Windows 手工验收证据, T034 Windows 无计时二元验收已完成：首次启动、基础设置、第一份教案、重启读取、当天 Word 在 Windows Microsoft Word 打开均通过, Graphify 查询：通过、未计时、需要计时的事实由来, 历史口径：旧 SC-001 曾要求首次使用五分钟, 历史结论：未计时只证明功能闭环，计时不是当前通过条件, 无需计时：保留首次启动、设置、第一份教案、重启和 Word 打开的五项二元证据, Graphify 查询：不需要计时要求 (+5 more)

### Community 146 - "CancellationToken"
Cohesion: 0.10
Nodes (31): CancellationToken, DailyPlanExportSnapshot, DayRenderer, ExportError, ExportResult, ExportService, Path, Protocol (+23 more)

### Community 147 - "Q: 通过人工测试，后台 PS C:\Users\admin\code\child-manager> uv run python -m kindergarten_manager 输出 QFont::setPointSize: Point size <= 0 (-1), must be greater than 0"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 通过人工测试，后台 PS C:\Users\admin\code\child-manager> uv run python -m kindergarten_manager 输出 QFont::setPointSize: Point size <= 0 (-1), must be greater than 0, Source Nodes

### Community 148 - "test_workday_service.py"
Cohesion: 0.29
Nodes (6): _module(), MonkeyPatch, test_confirmed_and_unavailable_results_use_24_hour_and_5_minute_ttls(), test_local_result_wins_conflict_and_uses_one_hour_cache(), test_timor_client_enforces_one_total_deadline(), test_unsupported_local_calendar_range_softly_falls_back_to_online()

### Community 149 - "查询记录 2026-07-11 02:07：如何撰写 lesson-management PRD"
Cohesion: 0.33
Nodes (11): AI 生成与提示词规则, 班级与教师配置, 一日活动计划, 日期选择与校验, 教案结构化, 园所数据隔离, Word 导出格式控制, Word 模板保护与导出验证 (+3 more)

### Community 150 - "query_service.py"
Cohesion: 0.15
Nodes (19): job_query_service(), JobStatus, BatchJobAggregationRepository, Any, UUID, `ai.batch` 父任务的只读状态投影。, 从恰好四个子任务派生父任务响应，不写入父任务执行字段。, JobQueryService (+11 more)

### Community 151 - "test_group_activity_contract.py"
Cohesion: 0.39
Nodes (8): _contract(), Any, US5 集体活动来源与两阶段 AI 契约 RED。, _source_payload(), test_docx_extraction_preview_is_separate_from_confirmed_source_metadata(), test_source_metadata_is_closed_and_never_exposes_original_text_or_attachment(), test_source_page_is_closed_and_preserves_pagination_metadata(), test_split_and_incremental_add_schemas_are_closed_and_validate_index_bounds()

### Community 152 - "test_openapi_document.py"
Cohesion: 0.36
Nodes (8): load_document(), Any, OpenAPI 3.1 文档与基础机器契约。, test_openapi_declares_confirmation_and_generic_word_export_conflicts(), test_openapi_document_is_valid_31(), test_openapi_keeps_nicegui_as_the_only_browser_entry(), test_openapi_locks_repeated_auth_and_clear_cookies(), test_openapi_locks_two_unavailable_codes()

### Community 153 - "test_local_development_profiles.py"
Cohesion: 0.27
Nodes (8): _compose_config(), Any, Path, 双实现本地开发档位的 Compose 合同。, test_compose_accepts_temporary_image_overrides(), test_compose_uses_selected_local_profile(), test_quality_workflow_provides_an_isolated_postgresql_database(), test_test_database_url_requires_an_explicit_profile()

### Community 154 - "ai_adoption.py"
Cohesion: 0.12
Nodes (18): ai_adoption_service(), AiAdoptionService, _native_url(), AiTaskCode, Any, datetime, JsonValue, LessonPlanRepository (+10 more)

### Community 155 - "test_secret_encryption.py"
Cohesion: 0.39
Nodes (8): _context(), _encryption_module(), Any, Path, test_development_key_provider_requires_owner_only_file_outside_repository(), test_totp_secret_envelope_rejects_ciphertext_or_aad_substitution(), test_totp_secret_envelope_round_trips_with_random_96_bit_nonce(), test_totp_secret_rebinds_from_enrollment_to_credential_with_a_new_nonce()

### Community 156 - "4. 实体"
Cohesion: 0.08
Nodes (25): 1. 建模原则, 2. 关系概览, 3. 通用存储约定, 4.10 `prompt_overrides`, 4.11 `ai_previews`, 4.12 `agent_action_audits`（Agent 写入阶段）, 4.13 `backup_records`, 4.1 `app_profile`（单例） (+17 more)

### Community 157 - "0007_ai_prompts_jobs.py"
Cohesion: 0.36
Nodes (6): Any, Column, 建立 AI 模型、提示词与 PostgreSQL 权威任务基础。, _seed_defaults(), _timestamps(), upgrade()

### Community 159 - "Specification Quality Checklist: 幼儿园管理助手桌面首期"
Cohesion: 0.18
Nodes (8): Content Quality, Feature Readiness, Notes, Requirement Completeness, Specification Quality Checklist: 幼儿园管理助手桌面首期, 验证迭代 6/7：移除首次使用计时，保持编号稳定；T034 为 Windows 验收，T035–T040 为 Slice 2A clean RED，T042 为 AI 凭据实现, Slice 1 断网 Windows 验收：完成首次设置、第一份教案、重启读取和当天 Word，无五分钟限制, SC-001：首次启动流程可完成基础设置并创建第一份教案，无首次使用计时指标

### Community 161 - "test_content_v1.py"
Cohesion: 0.54
Nodes (7): _contracts(), _schemas(), test_completeness_is_independent_from_progressive_schema_validation(), test_empty_v1_content_supports_progressive_manual_editing(), test_reflection_is_nfkc_normalized_and_limited_to_200_codepoints(), test_statement_and_question_punctuation_are_strictly_chinese(), test_unknown_fields_and_unknown_content_versions_are_not_silently_coerced()

### Community 162 - "_module"
Cohesion: 0.39
Nodes (7): _module(), Any, Path, test_ai_key_envelope_rejects_tampering_and_cross_profile_substitution(), test_ai_key_envelope_round_trips_with_random_96_bit_nonce(), test_file_key_provider_requires_owner_only_files_outside_repository(), test_static_key_provider_reads_old_key_but_writes_with_active_key()

### Community 163 - "User Scenarios & Testing *(mandatory)*"
Cohesion: 0.14
Nodes (14): Assumptions, Edge Cases, Feature Specification: 幼儿园管理助手桌面首期, Frozen Future Constraints *(not part of first-release acceptance)*, Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)* (+6 more)

### Community 164 - "_module"
Cohesion: 0.43
Nodes (7): _module(), Any, test_catalog_assigns_task_specific_minimum_variable_whitelists(), test_catalog_freezes_seven_codes_whitelists_schemas_and_hashes(), test_catalog_input_validation_excludes_teacher_identity_and_unknown_fields(), test_catalog_result_schemas_are_strict(), test_catalog_result_schemas_match_the_frozen_openapi_shapes()

### Community 165 - "桌面首期实施后快速验收指南"
Cohesion: 0.09
Nodes (21): 10. Agent 写入阶段, 11.1 实施前 spike 门禁, 11.2 业务验收, 11. Word 批量导出, 12. Windows UI 与 DPI, 13. Windows standalone 与安装器, 14. 后期 MSIX 兼容性（非首期完成门禁）, 15. 完整质量门禁 (+13 more)

### Community 166 - "0002_passkey_expand.py"
Cohesion: 0.52
Nodes (5): Any, Column, _tenant_identity_columns(), _timestamps(), upgrade()

### Community 167 - "schemas.py"
Cohesion: 0.26
Nodes (13): _area_complete(), content_completeness(), EditableContent, _group_activity_complete(), _morning_activity_complete(), _morning_talk_complete(), parse_content_for_editing(), Any (+5 more)

### Community 168 - "_module"
Cohesion: 0.48
Nodes (6): _module(), Any, test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(), test_renderer_fails_for_missing_variable_before_external_call(), test_renderer_rejects_every_non_frozen_placeholder_form(), test_renderer_uses_stable_json_and_never_recursively_renders_values()

### Community 171 - "validate_prompt_result_schema"
Cohesion: 0.21
Nodes (14): prompt_spec(), Any, validate_prompt_result(), validate_prompt_result_schema(), _contract(), Any, ModuleType, M6 AI 固定结果与输入最小化 RED 验收。 (+6 more)

### Community 174 - "_totp_module"
Cohesion: 0.53
Nodes (5): Any, test_totp_matches_rfc6238_and_accepts_only_adjacent_time_steps(), test_totp_rejects_the_same_or_earlier_counter_after_success(), test_totp_secret_is_unique_high_entropy_base32(), _totp_module()

### Community 175 - "Q: 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请将现在的进度以及系统所需要的软件，skill，环境记录在文件中，同步到仓库，我将会切换另一台ubuntu系统继续开发。, Source Nodes

### Community 176 - "Q: M5 完成后到 M4 的当前依赖路径是什么？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: M5 完成后到 M4 的当前依赖路径是什么？, Source Nodes

### Community 177 - "_run"
Cohesion: 0.60
Nodes (4): CompletedProcess, _run(), test_bootstrap_cli_exposes_rotation_without_master_key_arguments(), test_rotation_cli_reports_missing_external_configuration_without_leaking_secrets()

### Community 179 - "lesson_plans/test_calendar.py"
Cohesion: 0.70
Nodes (4): _calendar(), test_activity_date_text_weekday_and_fixed_four_seasons_are_deterministic(), test_out_of_semester_week_number_and_text_are_both_empty(), test_semester_start_week_is_week_one_and_increments_each_monday()

### Community 181 - "test_lesson_plan_contract.py"
Cohesion: 0.83
Nodes (3): _contracts(), test_open_and_write_contracts_do_not_accept_tenant_or_ownership_mutation(), test_plan_snapshot_and_page_contracts_are_bounded_and_stable()

### Community 187 - "configure_logging"
Cohesion: 0.32
Nodes (6): main(), 拒绝在非开发环境或非回环地址关闭 Cookie Secure。, 验证进程启动时的 Cookie 与监听地址组合。, validate_cookie_security(), configure_logging(), 配置 JSON 结构化日志和最终脱敏处理器。

### Community 236 - "受控 Agent Runtime 契约"
Cohesion: 0.13
Nodes (15): 10. 线程契约, 11. 事务与 WRITE 契约, 12. 无长期业务记忆, 13. 验证矩阵, 14. 明确非目标, 1. 目的与适用阶段, 2. 依赖与信任规则, 3. `Runtime` (+7 more)

### Community 237 - "_resolver"
Cohesion: 0.57
Nodes (7): _module(), Any, _resolver(), test_policy_accepts_only_allowlisted_public_https_and_checks_every_address(), test_policy_detects_dns_rebinding_before_connect(), test_policy_rejects_non_https_and_non_public_networks(), test_policy_requires_explicit_server_allowlist()

### Community 238 - "ai_generation.py"
Cohesion: 0.12
Nodes (20): Broker, UUID, 仅投递 job_id 的提示词测试分发边界。, RedisJobDispatcher, AiGenerationAcceptance, dispatch_after_commit(), Dispatcher, _FrozenTask (+12 more)

### Community 239 - "桌面应用服务契约"
Cohesion: 0.13
Nodes (15): 10. `ExportService`, 11. `BackupService`, 12. Qt 运行时桥接, 13. 架构契约测试, 1. 目的, 2. 依赖规则, 3. 共享结果类型, 4. `BootstrapService` (+7 more)

### Community 240 - "决策"
Cohesion: 0.10
Nodes (20): 1. 单 Agent 与 Application Layer, 2. Tool-only 业务访问, 3. 有界 Context 与无长期业务记忆, 4. 分阶段权限与确认写入, 5. 线程、事务与失败语义, 6. Provider port, 7. 固定实施顺序, ADR-0013：受控单 Agent 运行时 (+12 more)

### Community 242 - "ADR-0012：本地优先桌面产品方向重置"
Cohesion: 0.15
Nodes (11): ADR-0012：本地优先桌面产品方向重置, 代价, 使用 PyQt6, 决策, 取舍, 将现有 B/S 系统封装进桌面窗口, 收益, 背景 (+3 more)

### Community 243 - "桌面数据、凭据与备份设计"
Cohesion: 0.15
Nodes (12): 1. 本地数据权威, 2. Schema 迁移, 3. 保存、版本与归档, 4. 凭据存储, 5. 备份包, 6. 备份与恢复流程, 7. 非同步保证, 8. 威胁与验证 (+4 more)

### Community 244 - "0004_settings.py"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 245 - "Implementation Plan: 幼儿园管理助手桌面首期"
Cohesion: 0.15
Nodes (13): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: 幼儿园管理助手桌面首期, Implementation Sequence, Old B/S Reuse and Retirement Matrix, Phase 0 前门禁, Phase 1 后复核 (+5 more)

### Community 246 - "桌面首期技术研究与决策"
Cohesion: 0.15
Nodes (13): 10. WebDAV 与 S3, 11. Windows 构建、安装与后期 MSIX, 12. 旧 B/S 复用原则, 1. Python、PySide6 与界面技术, 2. SQLite、SQLAlchemy 与 Alembic, 3. 数据目录与资源定位, 4. 线程、任务和取消, 5. 模块边界 (+5 more)

### Community 247 - "KMBACKUP1 备份包与恢复契约"
Cohesion: 0.17
Nodes (12): 10. 验证矩阵, 1. 范围, 2. 内部完整包, 3. 一致性快照生成, 4. 加密信封, 5. 凭据存储, 6. 远程对象, 7. 轮换 (+4 more)

### Community 248 - "幼儿园管理助手桌面系统架构"
Cohesion: 0.18
Nodes (8): 1. 目标与边界, 2. 运行结构, 3. 线程与任务, 4. 模块结构目标, 5. 可复用与不可直接迁移, 6. 平台与数据目录, 7. 验证责任, 幼儿园管理助手桌面系统架构

### Community 249 - "Word 导出契约"
Cohesion: 0.18
Nodes (8): 1. 共同不变量, 2. 冻结输入, 3. 单日导出, 4. 批量预览, 5. 批量 DOCX 结构, 6. 进度、取消与原子发布, 7. 验证矩阵, Word 导出契约

### Community 250 - "桌面界面设计系统"
Cohesion: 0.20
Nodes (9): 1. 体验目标, 2. 信息架构, 3. 视觉令牌, 4. 已确认教案编辑布局, 5. 固定状态位置, 6. 可用性与无障碍, 7. 主题行为, Word 导出入口 (+1 more)

### Community 251 - "DailyPlanWorkspace"
Cohesion: 0.14
Nodes (12): DailyPlanWorkspace, _filename_part(), Any, date, LessonPlanService, Path, Protocol, RuntimeError (+4 more)

### Community 252 - "0001_identity_and_audit.py"
Cohesion: 0.53
Nodes (4): Column, datetime, _timestamps(), upgrade()

### Community 253 - "桌面 Slice 1 手工 MVP RED 证据"
Cohesion: 0.22
Nodes (8): Foundation 门禁, Slice 1 RED, 停止边界, 固定基线与授权, 强制 collect-only, 桌面 Slice 1 手工 MVP RED 证据, 环境, 额外完整性检查

### Community 254 - "implemented"
Cohesion: 0.07
Nodes (43): Engine, _apply_sqlite_pragmas(), create_session_factory(), create_sqlite_engine(), Path, sessionmaker, SQLite 同步 Session 工厂。, Path (+35 more)

### Community 255 - "PlanContentV1"
Cohesion: 0.09
Nodes (23): Self, LessonPlanEditorState, LessonPlanError, LessonPlanRepositoryPort, LessonPlanService, date, PlanContentV1, Protocol (+15 more)

### Community 256 - "provision_enabled_ai_model"
Cohesion: 0.08
Nodes (58): ai_model_service(), create_completed_ai_preview(), provision_enabled_ai_model(), TestClient, UUID, _event(), TestClient, test_ai_audit_event_codes_cover_creation_retries_result_reject_and_adopt() (+50 more)

### Community 257 - "test_architecture_boundaries.py"
Cohesion: 0.40
Nodes (9): _imports(), _matches(), _package_for(), Path, test_application_and_domain_dependencies_point_inward(), test_composition_root_only_wires_adapters_and_application_services(), test_desktop_namespace_does_not_import_legacy_runtime(), test_ui_only_reaches_application_boundary() (+1 more)

### Community 258 - "Frozen Architecture Decisions"
Cohesion: 0.25
Nodes (8): 1. 模块与依赖方向, 2. 受控 Agent Runtime, 3. SQLite、事务与 Alembic, 4. 本地目录, 5. Word 单日与批量导出, 6. 备份与恢复, 7. Windows 打包与更新, Frozen Architecture Decisions

### Community 279 - "Alembic 迁移"
Cohesion: 0.07
Nodes (14): Alembic 迁移, Any, Column, _timestamps(), upgrade(), Any, Column, _timestamps() (+6 more)

### Community 281 - "canonical_request_fingerprint"
Cohesion: 0.19
Nodes (16): canonical_request_fingerprint(), 计算覆盖路由、实际资源与语义输入的 canonical SHA-256。, _export_payload(), _job_payload(), Any, UUID, T127 固定 Word 导出公共契约 RED。, _required() (+8 more)

### Community 284 - "0009_group_activity_sources.py"
Cohesion: 0.47
Nodes (4): Any, Column, _timestamps(), upgrade()

### Community 286 - ".require_add_passkey_authorization"
Cohesion: 0.40
Nodes (6): datetime, _session(), test_backup_reauthentication_only_authorizes_add_passkey_for_five_minutes(), test_expired_backup_reauthentication_cannot_add_passkey(), test_recent_webauthn_proof_satisfies_high_risk_identity_boundary(), test_restricted_enrollment_session_cannot_enter_business_routes()

### Community 290 - "Q: desktop gui prototype semester date teacherplan renderer word export 室内区域游戏 下午户外游戏 日期选择与校验：C 周计划工作台、用户选择学期起止日期、集体活动编辑空间与 Word 单层编号应由哪些节点和契约约束？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: desktop gui prototype semester date teacherplan renderer word export 室内区域游戏 下午户外游戏 日期选择与校验：C 周计划工作台、用户选择学期起止日期、集体活动编辑空间与 Word 单层编号应由哪些节点和契约约束？, Source Nodes

### Community 291 - "Q: Windows 下主题颜色白底白字、暗黑模式缺失、缺乏设置选项导致学期无法修改、日期无法一键回到今天，应如何修复？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Windows 下主题颜色白底白字、暗黑模式缺失、缺乏设置选项导致学期无法修改、日期无法一键回到今天，应如何修复？, Source Nodes

### Community 294 - "_render_prompt_test_run_schema"
Cohesion: 1.00
Nodes (3): JsonSchemaValue, _render_prompt_test_run_schema(), _render_union_as_one_of()

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
- **347 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+342 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `日期选择与校验` (4× useful, score=2.469529195)
- `theme.py` (2× useful, score=1.998410688)
- `共同实施路线` (2× useful, score=0.989140147)
- `Web、API 与 Worker 服务边界` (2× useful, score=0.989140147)
- `目标服务架构` (2× useful, score=0.989140147)
- `班级与教师配置` (2× useful, score=0.976730198)
- `教案结构化` (2× useful, score=0.976730198)

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