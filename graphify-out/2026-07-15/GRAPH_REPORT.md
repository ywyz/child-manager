# Graph Report - .  (2026-07-15)

## Corpus Check
- 164 files · ~85,412 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 551 nodes · 856 edges · 70 communities (61 shown, 9 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 22
- Community 23
- Community 24
- Community 26
- Community 28
- Community 29
- Community 30
- Community 58

## God Nodes (most connected - your core abstractions)
1. `Settings` - 25 edges
2. `create_app()` - 20 edges
3. `HealthDependencies` - 17 edges
4. `_load_spec()` - 13 edges
5. `_runtime_schemas()` - 13 edges
6. `_request_context_middleware()` - 12 edges
7. `Scheduler` - 12 edges
8. `redaction_processor()` - 12 edges
9. `_make_dependencies()` - 12 edges
10. `_make_client()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `HealthDependencies` --uses--> `ErrorResponse`  [INFERRED]
  apps/api/main.py → packages/contracts/common.py
- `HealthDependencies` --uses--> `HealthResponse`  [INFERRED]
  apps/api/main.py → packages/contracts/common.py
- `create_app()` --indirect_call--> `HealthResponse`  [INFERRED]
  apps/api/main.py → packages/contracts/common.py
- `_make_dependencies()` --references--> `HealthDependencies`  [EXTRACTED]
  tests/api/test_health.py → apps/api/main.py
- `mock_health_dependencies()` --references--> `HealthDependencies`  [EXTRACTED]
  tests/test_health_endpoints.py → apps/api/main.py

## Import Cycles
- None detected.

## Communities (70 total, 9 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (54): HealthDependencies, _load_spec(), Any, OpenAPI 契约锁定测试。  读取静态 openapi.yaml 并锁定关键结构，防止后续实现漂移。 增加运行时 OpenAPI 与静态契约的一致性门禁。, 退出必须清除两条独立 Set-Cookie。, page >= 1, page_size 1–100。, 获取运行时 OpenAPI 的 components/schemas。, 运行时 Error schema 必须包含 code/message/request_id/field_errors。 (+46 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (43): canonical_fingerprint(), ErrorResponse, FieldError, HealthResponse, idempotency_key_from_fingerprint(), IdempotencyKey, PaginatedResponse, Any (+35 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (39): process_export_job(), process_generation_job(), process_retry_job(), build_deterministic_test_broker(), build_redis_broker(), Broker, main(), Broker (+31 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (42): _ai_unconfigured(), build_health_dependencies(), _calendar_library_available(), create_app(), custom_openapi(), _error_response(), _http_exception_handler(), _live_handler() (+34 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (34): EventDict, configure_logging(), 结构化日志配置。  调用共享脱敏模块，确保日志中的敏感字段 （密钥、密码、令牌、Cookie 等）在输出前被脱敏。, 配置 structlog 处理链，包含脱敏处理器。, _is_sensitive_key(), Any, 共享脱敏模块。  提供敏感字段脱敏函数和 structlog 脱敏处理器， 供 API、Web、Worker 等所有运行单元使用。, structlog 处理器：递归脱敏事件字典中的敏感字段。 (+26 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (16): ABC, datetime, AIClientPort, AuditPort, CalendarPort, ClockPort, CryptoPort, DatabaseSessionPort (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (22): BaseSettings, Settings, environment 必须拒绝非 production/development/test 的值。, test_allowed_hosts(), test_cookie_security_non_loopback(), test_cookie_security_production(), test_cookie_security_validation(), test_database_url() (+14 more)

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (13): DeclarativeBase, get_database_url(), Alembic 迁移环境。  模块级代码需兼容两种导入方式： 1. alembic.command.upgrade/downgrade 调用时，context., run_migrations_offline(), run_migrations_online(), Base, get_db_session(), get_db_session 应该在成功时提交 (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.21
Nodes (17): DailyReflection, LessonPlan, PlanArchiveRequest, PlanAuthor, PlanAutoSaveRequest, PlanContentV1, PlanCreateRequest, PlanListResponse (+9 more)

### Community 9 - "Community 9"
Cohesion: 0.17
Nodes (13): ApiClient, BffResponse, main(), proxy_request(), Any, register_web(), _require_loopback(), AsyncBaseTransport (+5 more)

### Community 10 - "Community 10"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 11 - "Community 11"
Cohesion: 0.30
Nodes (16): _always_false(), _always_true(), client_factory(), _error_schema(), _health_schema(), _make_dependencies(), 健康检查端点权威行为覆盖。  验证运行时 /health/live 和 /health/ready 响应符合静态 OpenAPI 契约， 而非仅验证 YAML, test_live_response_has_no_extra_fields() (+8 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (11): downgrade(), upgrade(), block_external_network(), isolated_database_url(), _native_psycopg_url(), MonkeyPatch, require_test_database_url(), MonkeyPatch (+3 more)

### Community 13 - "Community 13"
Cohesion: 0.25
Nodes (14): AgeGroup, Area, AreaCreate, AreaUpdate, Class, ClassCreate, ClassTeacher, ClassUpdate (+6 more)

### Community 14 - "Community 14"
Cohesion: 0.30
Nodes (11): Prompt, PromptCapability, PromptCreateRequest, PromptPublishRequest, PromptResultSchema, PromptTestRequest, PromptTestRun, PromptUpdateRequest (+3 more)

### Community 15 - "Community 15"
Cohesion: 0.33
Nodes (10): ChangePasswordRequest, LoginRequest, LoginResponse, BaseModel, Role, TokenRefreshResponse, User, UserCreate (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.33
Nodes (8): ModelCapability, ModelProfile, ModelProfileCreateRequest, ModelProfileEnableRequest, ModelProfileListResponse, ModelProfileUpdateRequest, BaseModel, StrEnum

### Community 17 - "Community 17"
Cohesion: 0.38
Nodes (6): AuditEvent, AuditEventType, AuditListResponse, AuditQueryRequest, BaseModel, StrEnum

### Community 18 - "Community 18"
Cohesion: 0.73
Nodes (5): _is_sensitive_key(), Any, redact(), redact_dict(), redact_value()

## Knowledge Gaps
- **6 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `configure_logging()` connect `Community 4` to `Community 2`, `Community 3`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `create_app()` connect `Community 3` to `Community 0`, `Community 1`, `Community 11`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Why does `HealthDependencies` connect `Community 0` to `Community 11`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `create_app()` (e.g. with `_http_exception_handler()` and `_live_handler()`) actually correct?**
  _`create_app()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `HealthDependencies` (e.g. with `ErrorResponse` and `HealthResponse`) actually correct?**
  _`HealthDependencies` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05576441102756892 - nodes in this community are weakly interconnected._