# Graph Report - child-manager  (2026-07-15)

## Corpus Check
- 156 files · ~83,138 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2245 nodes · 1995 edges · 710 communities (177 shown, 533 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 31 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `796200aa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Child Manager 产品与工程路线图
- M0 阻塞项统一修复执行方案（Codex + Trae）
- Child Manager 2026-07-14 编码前审查解决方案
- Tasks: 首期一日活动计划完整闭环
- Child Manager Agent 开发规则
- Phase 1 数据模型：首期一日活动计划完整闭环
- Phase 0 研究：首期一日活动计划完整闭环
- README.md
- Child Manager 项目上下文
- 正文
- Functional Requirements
- Tasks: [FEATURE NAME]
- SKILL.md
- Child Manager 幼儿园教育管理系统
- README.md
- 5. 端点目录
- Child Manager 双 Agent 独立开发协议
- 6. 浏览器验收路径
- common.sh
- Execution Steps
- Implementation Plan: 首期一日活动计划完整闭环
- Child Manager 一日活动计划 OpenAPI 3.1
- ADR-0003：PostgreSQL 保存任务权威状态，Dramatiq 与 Redis 负责异步执行
- Child Manager 数据模型设计
- Child Manager 幼儿园教育管理系统
- ADR-0005：AI 供应商中立，并建立管理员专用提示词系统
- D1 历史隐私清理完成并关闭 M0-G7
- Child Manager 系统架构设计
- Feature Specification: [FEATURE NAME]
- ADR-0006：一日活动计划采用固定 Word 模板导出边界
- ADR-0008：日期与外部服务采用本地优先和软降级
- Child Manager 双实现本地开发环境
- Core Principles
- 后台任务状态机与 AI 采用契约
- SKILL.md
- SKILL.md
- SKILL.md
- ADR-0002：采用独立 Web、API、Worker 运行单元的模块化单体
- ADR-0004：采用同源入口、HttpOnly Cookie 与 API 统一授权
- Child Manager PostgreSQL 数据库 Schema
- 教案管理 PRD（首期：一日活动计划）
- Core Principles
- AI 预览与教师采用
- 生产部署延后
- Child Manager 文档交叉审计合并结论
- 右侧列
- 这是一份word表格
- 18. 验收标准
- Implementation Plan: [FEATURE]
- SKILL.md
- Child Manager OpenAPI v1
- SKILL.md
- SKILL.md
- 3. 总体建模原则
- 9. 一日活动计划模型
- CERNET 用户级 uv 镜像
- 3. 二十六项问题的最终结论
- 3.9 Codex 交叉审计事项
- 10. 教案栏目与格式
- 13. AI 生成流程
- 右侧列
- 右侧列
- 右侧列
- 右侧列为两行：
- 右侧列为两行：
- 完整 SDD 工作流
- 共同实施路线
- 5. 园所与身份模型
- 6. 教学设置模型
- 3. PostgreSQL 物理约定
- 5. 园所与身份 Schema
- 6. 教学设置 Schema
- 9. 一日活动计划 Schema
- 9. 后台任务架构
- 12. AI 模型与提示词管理
- 7. 首期必要设置
- 9. 日期与上下文规则
- SKILL.md
- SKILL.md
- 21. 测试与验收
- 5. 代码组织与依赖方向
- 8. 数据架构
- main codex trae 分支所有权
- 3.2 模板说明与业务规则
- 4. 项目文档更新矩阵
- 11. 计划管理流程
- 14. Word 导出
- 17. 非功能要求
- Q: 请阅读以上内容和现有的AGENTS.MD,还有ywyz/kindergartenManager.git的AGENTS.MD，你认为i还需要再加入点什么？
- Q: 请阅读以上内容和现有的README.md,AGENTS.md,还有ywyz/kindergartenManager.git的文档，你认为CONTEXT.md需要再加入点什么？
- Q: 请根据现有文档，和旧仓库的文件思考如何撰写 docs/PRD/lesson-management.md
- Q: 接下来需要生成什么文件呢
- Q: 系统架构文档应如何定义目标服务架构、服务边界、共享契约、部署拓扑与首期实施顺序？
- Q: 哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？
- Q: 一日活动计划系统的数据实体、关系、唯一约束、历史版本、异步任务和安全边界是什么？
- Q: 请使用/graphify update. 进行更新，同时使用子代理进行语义更新，然后思考还需要完成什么任务
- Base
- create-new-feature.sh
- [CHECKLIST TYPE] Checklist: [FEATURE NAME]
- 15. 数据快照边界
- 22. 后续扩展边界
- 2. 设计来源与旧系统取舍
- 8. 提示词模型
- 8. 提示词 Schema
- 10. AI 与提示词架构
- 6. 请求、认证与授权
- 3.3 数据模型、保留与任务关系
- 3.7 API 与页面信息架构
- 5. 用户与权限
- 8. 核心业务对象
- 11. 后台任务与 AI 结果
- 16. 外键与删除行为
- 4. 模型总览
- 7. AI 模型档案
- 10. 后台任务与 AI 结果 Schema
- 12. 系统支撑 Schema
- 2. 事实来源与旧仓库取舍
- 7. AI 模型档案 Schema
- 11. Word 与文件架构
- 13. 配置、密钥与安全
- 15. 生产部署延后边界
- 4. 架构总览
- 7. API 与契约
- 3.4 加密与密钥
- 3.6 测试与可访问性
- 3.8 编辑与 AI 采用
- 15. 安全、隐私与审计
- 4. 产品目标
- test_config.py
- check-prerequisites.sh
- setup-plan.sh
- setup-tasks.sh
- 检测与分析报告
- 需求与任务语义清单
- Spec Kit 跨制品分析
- 澄清焦点与生成清单
- 需求写作的单元测试
- Spec Kit 需求检查清单
- 歧义与覆盖扫描
- 逐问逐答与增量回写
- Spec Kit 规格澄清
- Spec Kit 宪章维护
- 宪章同步影响报告
- 语义版本与依赖模板同步
- 只追加收敛任务
- 意图清单与代码差距评估
- Spec Kit 实现收敛
- 实施前检查清单门禁
- 分阶段任务执行与验证
- 阶段一数据模型、契约与验证指南
- 阶段零研究与消歧
- 规格质量清单迭代验证
- 功能目录与可测试规格生成
- 依赖、并行与独立验收校验
- 按用户故事生成可执行任务
- 规范化 Issue 创建
- GitHub 远端匹配与任务去重门禁
- Spec Kit 任务转 GitHub Issue
- 真实验证证据与生产部署延后
- 服务、园所与事务边界
- 教师控制、AI 与 Word 保真
- 检查清单模板
- 项目宪章模板
- 宪章检查与两阶段设计门禁
- 实施计划模板
- 功能规格模板
- 用户故事、需求与可度量结果
- 设置、基础、故事与收尾阶段
- 用户故事任务模板
- AI 预览显式采用
- 归档只读与恢复编辑
- 审计只记录必要元数据
- 同班同日唯一当前教案
- 日期校验只软提示
- 确定性与风险相称测试
- AI Key 加密与数据最小化
- 事实来源冲突时停止固化实现
- 固定 Word 模板完整性
- graphify、Spec Kit 与工程技能规则
- Repository 园所隔离
- 最小实现边界
- 一键生成四栏目
- 乐观锁禁止静默覆盖
- 生产部署延后至功能验收后
- 提示词白名单与发布版本
- 历史快照触发边界
- 教师班级权限与管理员全园访问
- 教学周按周一递增
- Web、API、Worker 依赖方向
- 实现分支授权边界
- Cloud-only 首期范围
- 生产部署延后至 M9
- 园所数据隔离边界
- M0 complete 与 M1 ready
- Web API Worker 服务边界
- 避免日期专用文档提交
- Codex 实现子 Issue
- 共同基线分支创建
- 冲突冻结
- 双 Agent 启动前检查清单
- GitHub Issue 创建阶段
- graphify 完整性验收
- graphify 工作区修改处置
- 独立授权边界
- 实时基线证据
- M1 出口门禁
- M1 Issue 结构
- 非破坏性工作区保留
- 生产部署非目标
- 只读交叉评审
- 推荐执行顺序
- 共享文档同步
- M1 共享父 Issue
- 启动清单循环措辞澄清
- 执行停止条件
- T003 共享授权与分支门禁
- T004-T020 实现任务
- TDD 驱动的 M1 实现
- Trae 实现子 Issue
- 2026-07-14 只读编码前收敛审查报告
- 分支操作授权门禁
- Canonical 阶段状态一致性
- 当前不能进入编码
- combined-audit.md
- 有条件进入 M1 Issue 设计与草拟阶段
- 宪章约束已进入计划与任务
- CONTEXT.md
- 双 Agent 开发协议
- Git 与 GitHub 基线
- 新报告 Graphify 语义更新待确认
- 既有 Graphify 工作区修改
- I-01 Issue 粒度与任务映射
- I-02 启动清单循环措辞
- I-03 工作区基线清洁
- I-04 状态日期
- 实现授权门禁
- GitHub Issue 操作授权门禁
- M0-G1 至 M0-G8 已关闭
- M1 Codex 实现子 Issue
- M1 父子 Issue 层级
- M1 共享父 Issue
- M1 Trae 实现子 Issue
- M9 生产部署延后
- plan.md
- 双 Agent 只读交叉评审
- docs/ROADMAP.md
- spec.md
- Spec Kit 需求与任务完整覆盖
- T003 双实现分支任务
- T004 至 T020 有序执行清单
- tasks.md
- 仅允许本地开发与测试最小依赖
- 继续有效的安全结果
- age_groups
- ai_generation_results
- ai_model_profile_capabilities
- ai_model_profiles
- AI 模型档案
- audit_events
- background_jobs
- class_areas
- class_teachers
- classes
- daily_activity_plan_snapshots
- daily_activity_plans
- 园所与身份模型
- 停用、归档与不可变历史
- PostgreSQL 权威后台任务
- 后台任务状态集合
- kindergartens
- lesson_plan_sources
- Alembic 迁移顺序
- 总体建模原则
- 学期外教学周次双空
- 关系表头与 JSONB 正文
- 教案六大正文栏目
- AI 结构化预览与采用
- prompt_definitions
- 提示词模型
- prompt_test_runs
- prompt_versions
- 文档目的
- refresh_tokens
- 数据保留与清理
- roles
- JSONB Schema 演进
- semesters
- 教案、AI、审计与日志快照边界
- 首期 24 张表总览
- 教学设置模型
- 园所隔离与组合外键
- 时间与日期语义
- user_roles
- users
- UUIDv7 主键
- 数据模型测试与验收
- Word 导出模型
- workday_cache
- Schema 验收测试
- age_groups
- ai_generation_results
- ai_model_profile_capabilities
- ai_model_profiles
- Alembic 迁移序列
- 审计只插入约束
- audit_events
- background_jobs
- class_areas
- class_teachers
- classes
- daily_activity_plan_authors
- daily_activity_plan_exports
- daily_activity_plan_snapshots
- daily_activity_plans
- 导出快照、文件与状态约束
- 园所组合外键矩阵
- 后台任务状态、幂等与租约约束
- kindergartens
- lesson_plan_sources
- 学期外周次双空检查约束
- 部分唯一索引与排他约束
- PostgreSQL 物理约定
- 教案乐观锁更新
- PostgreSQL 与 SQLite 验证矩阵
- AI 结果采用、拒绝与清理约束
- prompt_definitions
- prompt_test_runs
- prompt_versions
- refresh_tokens
- roles
- 24 表 Schema 总览
- semesters
- 园所组合外键规则
- 应用事务不变量
- user_roles
- users
- workday_cache
- 供应商中立 AI 适配器
- AI 预览采用边界
- API 与共享契约
- 架构目标
- 架构级验证
- 同源 Web BFF
- 工作日与日期服务
- 深模块用例接口
- 后端模块单向依赖
- 生产部署延后边界
- 投递、租约、幂等与恢复扫描
- DOCX 上传与立即清理
- Dramatiq Worker 运行单元
- 故障与降级矩阵
- FastAPI API 运行单元
- 实施顺序 M1–M8
- 最小跨进程任务契约
- 后台任务状态机
- 逻辑架构视图
- NiceGUI Web 运行单元
- 可观测性与审计
- PostgreSQL 权威存储
- 提示词服务与确定性渲染
- Redis 投递协调
- 配置、密钥与安全边界
- Cookie 会话、CSRF 与来源信任
- 1–2 秒短轮询
- 园所与班级授权
- 事务所有权
- Word 模板、临时文件与原子输出
- 冲突与高影响歧义共同冻结
- M1 编码前有序启动流程
- 独立实现子 Issue
- 共享文档独立提交同步
- 共享父 Issue
- M1 Codex 实现子 Issue
- 确定性测试边界
- 既有 graphify 修改处置记录
- Issue 分支实现独立授权门禁
- live ready 健康语义
- 本地 PostgreSQL 与 Redis 依赖基线
- M1 工程骨架
- M1 共享父 Issue
- M1 质量基线
- 红灯绿灯最小实现循环
- T003 共同分支基线
- T004 至 T020 权威任务
- Web API Worker 三个运行单元
- M1 Trae 实现子 Issue
- Web API 依赖方向
- 审计事实来源链
- 文档交叉审计合并结论
- M0-G1 至 M0-G8 已关闭
- 审计结论不授权后续操作
- Q1 至 Q26 最终结论
- 模板脱敏与历史清理边界
- AI 重试分类与三次上限
- 归档教案仍占唯一键
- 审计至少保留一年
- 集体活动先拆分后新增
- 导出前必须成功保存
- 首期容量与响应目标
- 历史恢复保留恢复前内容
- 独立导出历史与私有副本
- 最后一个有效管理员不可停用
- 班级区域有序且分类校验
- Redis 故障时保留 pending_dispatch
- 创建后活动日期不可修改
- 预览仅随实际输入变化失效
- 生产恢复指标延后验收
- 反思三字段与 200 码点限制
- 管理员与教师权限矩阵
- 七个稳定任务级提示词
- 里程碑门禁证据
- M0 共享设计基线
- M1 工程骨架与质量基线
- M7 固定 Word 导出与历史
- M9 生产安全与部署复审
- 内容门禁与操作授权分离
- combined-audit 审计事实基线
- 最终 docs-only main 共享基线
- Child Manager 20260713 编码前审查报告
- FR-031 快照原因码与恢复顺序
- Git 历史隐私清理
- M0 complete
- M0-G1 至 M0-G8 门禁体系
- M1 ready
- Q13 客户端幂等 scope 与 fingerprint
- T002 Pre-M1 一致性审查
- T003 双 Agent 同基线分支流程
- 模板说明契约一致性
- 内容门禁与操作授权分离
- 模板、FR-031 与 Q13 契约对齐
- M0 阻塞项统一修复执行方案
- 历史隐私清理与最终 docs-only 基线
- M0 分阶段修复闭环
- T003 双 Agent 同基线分支流程
- Spec Kit 与 graphify 专项验证门禁
- AI 生成边界
- 班级与教师配置
- 日期选择与校验
- 需要直接比较文件
- AGENTS.md 补充建议查询
- Word 格式边界
- AI 教案结构化
- 配置
- 区分已确认设计与已实现状态
- 日期选择与校验
- CONTEXT.md 补充建议查询
- 集成式 NiceGUI 架构
- 不继承旧仓库架构
- 本地优先架构
- MySQL
- Word 导出格式控制
- 一日活动计划 PRD 范围结论
- 一日活动计划 PRD 查询记录
- 下一份文档查询记录
- 系统架构文档作为下一步
- 系统架构定义查询记录
- Web API Worker 架构与实施顺序
- 旧图谱未覆盖最新架构
- ADR 划分查询记录
- 修正后的一日活动计划数据模型结论
- 数据模型边界查询记录
- 规格质量检查清单
- 五轮一致性验证记录
- 待确认、采用、拒绝与过期
- ai.batch 父任务聚合
- 受理、投递、租约与恢复
- 执行状态机
- 集体活动部分成功
- 任务幂等契约
- 各任务输入快照
- 任务类型
- AI 预览有效性
- 模型调用与重试分类
- Web 轮询契约
- 统一响应与错误
- 提示词测试冻结输入 Schema
- Cookie 安全方案
- 教案快照 Schema
- 审计端点
- 认证与用户端点
- 分页、错误与 Request ID
- 契约演进
- Cookie、令牌与 CSRF
- Word 导出端点
- Idempotency-Key 契约
- 任务与 AI 预览端点
- 乐观锁契约
- 权限矩阵
- 教案端点
- 提示词端点
- 设置端点
- 稳定错误码
- ai_generation_results 预览
- AI 模型与提示词实体组
- audit_events 白名单元数据
- background_jobs 任务头
- 通用数据规则
- daily_activity_plan_exports 导出快照
- 必测数据行为
- 园所与身份实体组
- 六阶段迁移顺序
- 学期外周次双空
- PlanContentV1 六栏目
- 24 表关系总览
- Phase 1 数据模型
- 教学设置实体组
- 快照创建与不可变规则
- 关键事务不变量
- workday_cache 三类 TTL
- AI 结构化预览与教师采用
- 客户端幂等 scope 与 fingerprint
- pending_dispatch 恢复机制
- PostgreSQL 权威状态
- NiceGUI 同源 BFF
- T003 双实现分支授权
- 可靠 AI 任务与栏目采用验收
- API 契约快速检查
- 数据库迁移与首次初始化
- 工作日、审计与降级验收
- 集体活动与安全 DOCX 验收
- 锁定安装与本地依赖
- M8 完整验收记录
- 纯手工教案浏览器验收
- 前提与反目标
- 自动化质量门禁
- 反思事务验收
- Phase 1 Quickstart 与验收合同
- Web API Worker 三进程启动
- Word 导出与历史验收
- AI Key Envelope 与 SSRF 防护
- 区域按目标栏目校验
- 密码、Token、CSRF 与 BFF 来源
- 作者署名与当前授权分离
- 一键、反思与集体部分成功
- Pre-M1 canonical 文档同步
- 研究方法与决策优先级
- 生产部署与未来子系统排除
- 故障隔离矩阵
- PostgreSQL 权威任务与恢复
- 白名单确定性渲染
- 栏目级预览有效性
- 异步提示词测试冻结配置
- Phase 0 研究决策
- 当前学期与学期外日期
- 七个稳定提示词
- M1–M8 单一 Feature
- 快照只表达可恢复变化
- 固定结构化 AI 结果
- Python 3.14 技术基线
- 独立运行单元与模块化单体
- 固定 Word 模板与导出快照
- 工作日来源与三类缓存 TTL
- 集体活动拆分与新增环节流程
- 首期一日活动计划功能规格
- M0 complete M1 ready 规格状态
- 一键四栏目 AI 批任务
- 纯手工教案闭环
- 安全审计与降级要求
- 教案快照原因码
- 固定 Word 模板保真
- 执行授权边界与 RED seam 门禁
- 首期一日活动计划完整闭环任务清单
- Foundational 先写失败测试
- Foundational T009–T020
- Foundation 并行示例
- US1 / US2 并行示例
- US3 / US4 / US5 并行示例
- US6 / US7 / Polish 并行示例
- Phase 3: US1 管理员安全初始化与必要设置
- Phase 4: US2 教师纯手工教案闭环
- Phase 5: US3 管理员配置模型与提示词
- Phase 6: US4 教师按栏目使用 AI 并保留决定权
- Phase 7: US5 教师处理集体活动原始教案
- Phase 8: US6 教师导出并重新下载固定 Word
- Phase 9: US7 管理员审计与可降级服务
- Polish T155–T165
- 可收集且业务断言失败的 RED 门禁
- Setup T001–T008
- 用户故事专项回归与 graphify 门禁
- T002 最终候选基线 Pre-M1 一致性审查
- T003 双实现分支授权门禁
- US1 T021–T041
- US2 T042–T057
- US3 T058–T082
- US4 T083–T106
- US5 T107–T122
- US6 T123–T137
- US7 T138–T154
- 表格第二行：星期与日期
- 表格第七行：下午户外游戏
- 文件第二行：班级与教师
- 表格第八行：一日活动反思
- 表格第五行：集体活动
- 表格第六行：室内区域游戏
- 编号、句号、问号与换行格式
- 表格第三大行：晨间活动
- 表格第四行：晨间谈话
- 仅 AI 新增集体环节标红
- 一日活动计划 Word 系统说明
- 表格第一行：教学周次
- 文件第一行：园所与学期月份范围
- 右侧列
- 右侧列为两行：
- 填写说明
- 左侧列
- 第一行：
- 第二行：
- BaseModel
- main.py
- settings.py
- common.py
- jobs.py
- prompts.py
- identity.py
- exports.py
- models.py
- audit.py
- 一日活动计划业务不变量
- 园所数据隔离
- Web API Worker 服务边界
- 权威文档阅读顺序
- 双 Agent 独立开发协议
- 只读交叉评审
- 容器镜像 shell 变量覆盖
- 双实现本地开发环境
- 外部网络确定性测试替身
- 锁定的 Python 质量门禁工具链
- 本地服务仅绑定回环地址
- PostgreSQL 与 Redis 最小 Compose 依赖
- 下载加速不等于外部服务连通性
- 锁定官方容器镜像默认值
- 官方 PyPI 临时回退
- 生产部署延后至 M9
- 当前应用无需 npm 或 Node.js 安装链
- 工作树端口数据运行时隔离
- 固定本地档位与运行时隔离
- 技术栈与中国大陆网络边界
- Codex 与 Trae 工作树隔离
- M1 工程骨架与质量基线 Issue 草稿
- 共享父 Issue 与实现子 Issue 模型
- M1 工程骨架与质量基线
- M6 AI 异步生成与人工采用
- M0 至 M9 里程碑依赖链
- 产品与工程路线图
- child-manager
- Cloud-only 三服务架构
- 固定 Word 模板导出
- API v1 契约总则
- BFF 与可信上下文
- Cookie CSRF 会话契约
- 幂等异步任务契约
- 乐观锁与预览失效校验
- 首期一日活动计划实现计划
- PostgreSQL 权威任务状态
- 用户故事纵向切片策略
- 首期实现与验收合同
- 浏览器端到端验收路径
- 首期实现任务清单
- 先 RED 后实现的执行顺序
- US1 至 US7 交付依赖链
- test_openapi_document.py
- MockAiClient
- MockCalendar
- MockRedisClient
- 0000_foundation.py
- Docker 镜像构建延后到 M9 并由新部署 ADR 定义
- M1 至 M8 每次推送门禁：依赖锁定、Ruff、Pyright、Pytest
- redact_dict

## God Nodes (most connected - your core abstractions)
1. `Settings` - 24 edges
2. `Child Manager 数据模型设计` - 24 edges
3. `教案管理 PRD（首期：一日活动计划）` - 22 edges
4. `Child Manager 系统架构设计` - 22 edges
5. `Child Manager Agent 开发规则` - 20 edges
6. `Child Manager PostgreSQL 数据库 Schema` - 19 edges
7. `Child Manager 产品与工程路线图` - 18 edges
8. `Tasks: 首期一日活动计划完整闭环` - 17 edges
9. `create_app()` - 15 edges
10. `Child Manager 项目上下文` - 15 edges

## Surprising Connections (you probably didn't know these)
- `_make_dependencies()` --references--> `HealthDependencies`  [EXTRACTED]
  tests/api/test_health.py → apps/api/main.py
- `mock_health_dependencies()` --references--> `HealthDependencies`  [EXTRACTED]
  tests/test_health_endpoints.py → apps/api/main.py
- `test_500_returns_chinese_internal_error()` --indirect_call--> `_request_context_middleware()`  [INFERRED]
  tests/api/test_error_handling.py → apps/api/main.py
- `test_http_exception_400_returns_chinese_envelope()` --indirect_call--> `_request_context_middleware()`  [INFERRED]
  tests/api/test_error_handling.py → apps/api/main.py
- `test_error_responses_include_request_id()` --indirect_call--> `_request_context_middleware()`  [INFERRED]
  tests/unit/test_observability.py → apps/api/main.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **M1 并行实现结构** — docs_development_m1_issue_drafts_m1_shared_parent_issue, docs_development_m1_issue_drafts_codex_implementation_issue, docs_development_m1_issue_drafts_trae_implementation_issue, docs_development_m1_issue_drafts_t003_shared_branch_baseline [EXTRACTED 1.00]
- **M1 基础质量门禁** — docs_development_m1_issue_drafts_quality_baseline, docs_development_m1_issue_drafts_live_ready_health_semantics, docs_development_m1_issue_drafts_web_api_dependency_direction, docs_development_m1_issue_drafts_deterministic_test_boundaries [EXTRACTED 1.00]
- **M1 共享父子 Issue 结构** — docs______20260714_____m1_shared_parent_issue, docs______20260714_____m1_codex_child_issue, docs______20260714_____m1_trae_child_issue [EXTRACTED 1.00]
- **M1 独立授权门禁序列** — docs______20260714_____issue_operation_authorization, docs______20260714_____branch_operation_authorization, docs______20260714_____implementation_authorization [EXTRACTED 1.00]
- **Canonical 阶段状态证据链** — docs______20260714_____roadmap, docs______20260714_____context, docs______20260714_____spec, docs______20260714_____plan, docs______20260714_____tasks, docs______20260714_____combined_audit [EXTRACTED 1.00]
- **M1 一父两子 Issue 结构** — docs_20260714_shared_parent_issue, docs_20260714_codex_implementation_child_issue, docs_20260714_trae_implementation_child_issue [EXTRACTED 1.00]
- **Issue 分支编码独立授权流** — docs_20260714_github_issue_creation_stage, docs_20260714_common_baseline_branch_creation, docs_20260714_tdd_m1_implementation [EXTRACTED 1.00]
- **M0 修复到 M1 启动的授权转换** — docs_shenchabaogao_20260713bianmaqianshenchabaogaoxiufufangan_validation_gate, docs_shenchabaogao_20260713bianmaqianshenchabaogaoxiufufangan_history_and_baseline, docs_shenchabaogao_20260713bianmaqianshenchabaogaoxiufufangan_t003_dual_agent_branches, docs_shenchabaogao_20260713bianmaqianshenchabaogaoxiufufangan_authorization_separation [EXTRACTED 1.00]
- **可靠 AI 生成与人工采用流程** — docs_roadmap_m6_async_ai, specs_001_daily_activity_plan_plan_postgresql_authoritative_state, specs_001_daily_activity_plan_plan_pending_dispatch_recovery, specs_001_daily_activity_plan_plan_ai_preview_adoption, specs_001_daily_activity_plan_spec_four_column_ai_batch [INFERRED 0.85]
- **实现前授权边界** — context_branch_authorization_boundary, docs_faq_combined_audit_operation_authorization_boundary, specs_001_daily_activity_plan_plan_t003_dual_branch_authorization [INFERRED 0.95]
- **运行单元与权威状态** — docs_design_system_architecture_nicegui_web, docs_design_system_architecture_fastapi_api, docs_design_system_architecture_dramatiq_worker, docs_design_system_architecture_postgresql, docs_design_system_architecture_redis [EXTRACTED 1.00]
- **Word 一日活动计划栏目** — templates_teacherplan_morning_activity, templates_teacherplan_morning_talk, templates_teacherplan_group_activity, templates_teacherplan_indoor_area_game, templates_teacherplan_afternoon_outdoor_game, templates_teacherplan_daily_reflection [EXTRACTED 1.00]
- **Specify Plan Tasks Implement 全周期** — _agents_skills_speckit_specify_skill_speckit_specify, _agents_skills_speckit_plan_skill_speckit_plan, _agents_skills_speckit_tasks_skill_speckit_tasks, _agents_skills_speckit_implement_skill_speckit_implement [EXTRACTED 1.00]
- **宪章到规格计划任务模板的治理传播** — _specify_templates_plan_template_plan_template, _specify_templates_spec_template_spec_template, _specify_templates_tasks_template_tasks_template [INFERRED 0.85]
- **一日活动计划范围、架构与数据边界知识链** — graphify_out_memory_query_20260711_020708_docs_prd_lesson_management_m_prd_scope, graphify_out_memory_query_20260711_024218_service_architecture_sequence, graphify_out_memory_query_20260712_071357_corrected_data_model [INFERRED 0.75]
- **AI 预览与教师最终控制** — agents_ai_preview_explicit_adoption, docs_prd_lesson_management_preview_validity_by_actual_inputs, docs_prd_lesson_management_ai_retry_taxonomy [EXTRACTED 1.00]
- **教案任务预览快照导出持久化链路** — docs_design_data_model_daily_activity_plans, docs_design_data_model_background_jobs, docs_design_data_model_ai_generation_results, docs_design_data_model_daily_activity_plan_snapshots [EXTRACTED 1.00]
- **NiceGUI Web FastAPI API Worker 三运行单元** — agents_service_boundaries, readme_cloud_only_architecture, specs_001_daily_activity_plan_contracts_readme_bff_trust_boundary, specs_001_daily_activity_plan_plan_implementation_plan [INFERRED 0.95]
- **双 Agent M1 协作治理** — docs_roadmap_m1_engineering_foundation, docs_development_dual_agent_development_branch_ownership, docs_development_local_development_environments_runtime_isolation, docs_development_m1_issue_drafts_parent_child_issue_model [INFERRED 0.95]
- **一日活动计划设计实现验收合同** — specs_001_daily_activity_plan_plan_implementation_plan, specs_001_daily_activity_plan_contracts_readme_api_v1_contract, specs_001_daily_activity_plan_contracts_openapi_openapi_v1, specs_001_daily_activity_plan_quickstart_acceptance_contract, specs_001_daily_activity_plan_tasks_implementation_tasks [INFERRED 0.95]
- **双实现本地运行隔离合同** — docs_development_local_development_environments_worktree_isolation, docs_development_local_development_environments_runtime_profile_isolation, docs_development_local_development_environments_loopback_binding, docs_development_local_development_environments_minimal_compose_dependencies [EXTRACTED 1.00]
- **中国大陆依赖下载与官方回退策略** — docs_development_local_development_environments_cernet_uv_mirror, docs_development_local_development_environments_official_pypi_fallback, docs_development_local_development_environments_container_image_override, docs_development_local_development_environments_official_image_default [EXTRACTED 1.00]

## Communities (710 total, 533 thin omitted)

### Community 0 - "Child Manager 产品与工程路线图"
Cohesion: 0.04
Nodes (49): 10. M4：AI 模型与提示词基础, 11. M5：无 AI 教案手工闭环, 12. M6：AI 异步生成与人工采用, 13. M7：固定 Word 导出与历史, 14. M8：首期功能验收, 15. M9：生产安全与部署复审, 16. 当前状态快照, 17. Roadmap 更新规则 (+41 more)

### Community 1 - "M0 阻塞项统一修复执行方案（Codex + Trae）"
Cohesion: 0.05
Nodes (42): 1. 联合结论, 2.1 文档状态, 2.2 已确认满足的规则, 2. 当前文档与已满足规则, 3.1 模型与契约, 3.2 模板说明, 3.3 状态、证据与分支流程, 3.4 静态验证、图谱、历史与最终基线 (+34 more)

### Community 2 - "Child Manager 2026-07-14 编码前审查解决方案"
Cohesion: 0.05
Nodes (41): 1. 结论, 2.1 Git 与 GitHub, 2.2 当前阶段状态, 2.3 M0-G1～G8 最终汇总, 2. 审查基线, 3.1 指标, 3.2 覆盖与宪章, 3. Spec Kit 非破坏性一致性审查 (+33 more)

### Community 3 - "Tasks: 首期一日活动计划完整闭环"
Cohesion: 0.05
Nodes (43): Dependencies & Execution Order, Foundation, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation for User Story 4, Implementation for User Story 5, Implementation for User Story 6 (+35 more)

### Community 4 - "Child Manager Agent 开发规则"
Cohesion: 0.06
Nodes (35): 10. 一日活动计划业务不变量, 11.1 模型访问, 11.2 提示词管理, 11.3 生成行为, 11. AI 与提示词规则, 12. Word 模板与导出, 13. 安全与隐私硬性规则, 14. 审计、日志与错误处理 (+27 more)

### Community 5 - "Phase 1 数据模型：首期一日活动计划完整闭环"
Cohesion: 0.05
Nodes (37): 10. 迁移顺序, 11. 必测数据行为, 1. 通用规则, 2. 关系总览, 3.1 `kindergartens`, 3.2 `users`, 3.3 `roles`, 3.4 `user_roles` (+29 more)

### Community 6 - "Phase 0 研究：首期一日活动计划完整闭环"
Cohesion: 0.05
Nodes (37): 10. 已排除范围, 1. 研究方法与决策优先级, 2.1 首期使用一套 Spec Kit 文档, 2.2 独立运行单元与模块化单体, 2.3 技术基线与依赖, 2. Feature 与架构, 3.1 当前学期和学期外日期, 3.2 区域按目标栏目校验 (+29 more)

### Community 7 - "README.md"
Cohesion: 0.16
Nodes (10): Child Manager 架构决策记录, 与旧仓库 ADR 的关系, 决策索引, 新增 ADR 的判断标准, 状态约定, Content Quality, Feature Readiness, Notes (+2 more)

### Community 8 - "Child Manager 项目上下文"
Cohesion: 0.06
Nodes (31): 10. 当前共同下一步, 11.1 文档职责与工具基线, 11. 高风险点, 12. 系统架构基线, 13. 验证基线, 14. CONTEXT 更新规则, 1. 本文档的用途, 2. 固定阅读顺序 (+23 more)

### Community 9 - "正文"
Cohesion: 0.06
Nodes (31): 0. 草稿基线与 graphify 处置记录, 1. 共享父 Issue 草稿, 2. Codex 实现子 Issue 草稿, 3. Trae 实现子 Issue 草稿, 4. 草稿只读复核清单, M1 工程骨架与质量基线 Issue 草稿与执行记录, T004～T020 有序执行清单, T004～T020 有序执行清单 (+23 more)

### Community 10 - "Functional Requirements"
Cohesion: 0.07
Nodes (29): AI 模型与提示词, Assumptions, Clarifications, Dependencies, Edge Cases, Feature Specification: 首期一日活动计划完整闭环, Functional Requirements, Key Entities (+21 more)

### Community 11 - "Tasks: [FEATURE NAME]"
Cohesion: 0.07
Nodes (26): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation Strategy, Incremental Delivery, MVP First (User Story 1 Only) (+18 more)

### Community 12 - "SKILL.md"
Cohesion: 0.08
Nodes (25): 1. Initialize Analysis Context, 2. Load Artifacts (Progressive Disclosure), 3. Build Semantic Models, 4. Detection Passes (Token-Efficient Analysis), 5. Severity Assignment, 6. Produce Compact Analysis Report, 7. Provide Next Actions, 8. Offer Remediation (+17 more)

### Community 13 - "Child Manager 幼儿园教育管理系统"
Cohesion: 0.10
Nodes (21): 1. 产品只交付 Cloud 版本, 2. 首期一个运行实例只服务一所幼儿园, 3. 从首期保留园所隔离边界, 4. Cloud 不等于公网开放, 5. 生产数据语义统一采用 PostgreSQL, ADR-0001：只交付 Cloud 版本，首期单园运行并保留园所隔离边界, Cloud 版本必须直接开放公网, 代价与风险 (+13 more)

### Community 14 - "README.md"
Cohesion: 0.10
Nodes (21): 备选方案, 背景, 首期接入云厂商密钥管理服务, 后果, 决策, ADR-0007：采用 Caddy、Docker Compose 与文件挂载 Secrets, 将所有 Secrets 放入 .env, 实施约束 (+13 more)

### Community 15 - "5. 端点目录"
Cohesion: 0.10
Nodes (21): 1. 边界与可信上下文, 2. Cookie、令牌与 CSRF, 3.1 Request ID, 3.2 分页, 3.3 统一错误, 3.4 乐观锁, 3.5 Idempotency-Key, 3. 通用请求与响应 (+13 more)

### Community 16 - "Child Manager 双 Agent 独立开发协议"
Cohesion: 0.10
Nodes (20): 10. 禁止事项, 11. 启动前检查清单, 1. 文档目的, 2. 事实来源与优先级, 3. 分支模型与所有权, 4.1 共享父 Issue, 4.2 实现子 Issue, 4.3 纵向拆分 (+12 more)

### Community 17 - "6. 浏览器验收路径"
Cohesion: 0.11
Nodes (18): 1. 前提与反目标, 2. 锁定安装与本地依赖, 3. 数据库与首次初始化, 4. 启动三个独立进程, 5. 自动化质量门禁, 6.1 初始化、登录与会话, 6.2 必要设置与权限, 6.3 纯手工教案 (+10 more)

### Community 18 - "common.sh"
Cohesion: 0.13
Nodes (5): get_feature_paths(), get_repo_root(), _persist_feature_json(), resolve_specify_init_dir(), common.sh script

### Community 19 - "Execution Steps"
Cohesion: 0.12
Nodes (15): 1. Initialize Convergence Context, 2. Load Artifacts (Progressive Disclosure), 3. Build the Intent Inventory, 4. Assess the Codebase and Classify Findings, 5. Assign Severity, 6. Present the In-Session Findings Summary, 7. Append Convergence Tasks (or report converged), 8. Provide Next Actions (Handoff) (+7 more)

### Community 20 - "Implementation Plan: 首期一日活动计划完整闭环"
Cohesion: 0.12
Nodes (16): API 与任务契约, Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: 首期一日活动计划完整闭环, Milestone Gates, Phase 0: Research, Phase 1: Design & Contracts (+8 more)

### Community 21 - "Child Manager 一日活动计划 OpenAPI 3.1"
Cohesion: 0.13
Nodes (15): Audit API, 脱敏审计 Schema, Auth API, 不可变导出输入与文件 Schema, Exports API, Health API, Job 与 batch 投影 Schema, Jobs API (+7 more)

### Community 22 - "ADR-0003：PostgreSQL 保存任务权威状态，Dramatiq 与 Redis 负责异步执行"
Cohesion: 0.14
Nodes (13): ADR-0003：PostgreSQL 保存任务权威状态，Dramatiq 与 Redis 负责异步执行, API 同步执行 AI 和 Word, Celery + Redis, PostgreSQL 直接充当轮询任务队列, Redis 作为任务最终状态存储, 决策, 后果, 备选方案 (+5 more)

### Community 23 - "Child Manager 数据模型设计"
Cohesion: 0.14
Nodes (14): 10. JSONB Schema 演进, 12.1 `daily_activity_plan_exports`, 12. Word 导出模型, 13.1 `workday_cache`, 13. 工作日缓存, 14.1 `audit_events`, 14. 审计模型, 17. 索引原则 (+6 more)

### Community 24 - "Child Manager 幼儿园教育管理系统"
Cohesion: 0.09
Nodes (23): AI 提示词管理子系统, AI 生成规则, Child Manager 幼儿园教育管理系统, Word 导出, 一键生成与分栏目生成, 分支协作规范, 后续子系统, 基本规则 (+15 more)

### Community 25 - "ADR-0005：AI 供应商中立，并建立管理员专用提示词系统"
Cohesion: 0.15
Nodes (12): ADR-0005：AI 供应商中立，并建立管理员专用提示词系统, AI 直接写入教案当前内容, 允许提示词定义输出 Schema, 决策, 只配置一个全局模型, 后果, 备选方案, 复审触发条件 (+4 more)

### Community 26 - "D1 历史隐私清理完成并关闭 M0-G7"
Cohesion: 0.17
Nodes (13): ApiClient, BffResponse, main(), proxy_request(), Any, register_web(), _require_loopback(), AsyncBaseTransport (+5 more)

### Community 27 - "Child Manager 系统架构设计"
Cohesion: 0.15
Nodes (13): 12. 节假日与日期服务, 14. 可观测性与审计, 16. 性能与扩展, 17. 故障与降级, 18. 测试与架构验证, 19. 关键架构决策摘要, 1. 文档目的, 20. 实施顺序 (+5 more)

### Community 28 - "Feature Specification: [FEATURE NAME]"
Cohesion: 0.15
Nodes (12): Assumptions, Edge Cases, Feature Specification: [FEATURE NAME], Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+4 more)

### Community 29 - "ADR-0006：一日活动计划采用固定 Word 模板导出边界"
Cohesion: 0.17
Nodes (11): ADR-0006：一日活动计划采用固定 Word 模板导出边界, UI 直接修改模板并下载, 从零生成 Word 排版, 决策, 只向浏览器返回临时文件, 后果, 备选方案, 复审触发条件 (+3 more)

### Community 30 - "ADR-0008：日期与外部服务采用本地优先和软降级"
Cohesion: 0.17
Nodes (11): ADR-0008：日期与外部服务采用本地优先和软降级, 决策, 后果, 在线节假日 API 优先, 备选方案, 复审触发条件, 外部服务失败时默认普通工作日, 实施约束 (+3 more)

### Community 31 - "Child Manager 双实现本地开发环境"
Cohesion: 0.17
Nodes (12): 1. 文档目的, 2. 事实来源与边界, 3. 工作树隔离, 4.1 Codex 档位, 4.2 Trae 档位, 4. 固定本地档位, 5. Compose、数据与文件隔离, 6. 技术栈与中国大陆网络边界 (+4 more)

### Community 32 - "Core Principles"
Cohesion: 0.17
Nodes (11): Child Manager 项目宪章, Core Principles, Governance, I. 事实来源与范围忠实, II. 服务边界与单向依赖, III. 园所隔离与服务端授权（NON-NEGOTIABLE）, IV. 权威状态、事务与可恢复性, V. 教师控制、AI 与 Word 保真 (+3 more)

### Community 33 - "后台任务状态机与 AI 采用契约"
Cohesion: 0.17
Nodes (11): 10. Web 轮询契约, 1. 任务类型, 2. 状态定义, 3. 受理、投递与租约, 4. 模型调用与重试分类, 5. 幂等契约, 6. AI 预览有效性, 7. 各任务输入快照 (+3 more)

### Community 34 - "SKILL.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, Key rules, Mandatory Post-Execution Hooks, Outline, Phase 0: Outline & Research, Phase 1: Design & Contracts, Phases (+2 more)

### Community 35 - "SKILL.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, For AI Generation, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, Quick Guidelines, Section Requirements (+2 more)

### Community 36 - "SKILL.md"
Cohesion: 0.18
Nodes (10): Checklist Format (REQUIRED), Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Phase Structure, Pre-Execution Checks, Task Generation Rules (+2 more)

### Community 37 - "ADR-0002：采用独立 Web、API、Worker 运行单元的模块化单体"
Cohesion: 0.18
Nodes (11): ADR-0002：采用独立 Web、API、Worker 运行单元的模块化单体, NiceGUI 一体化进程, React/TypeScript 独立前端, 从首期开始全面微服务化, 决策, 前端直接访问数据库或共享 Repository, 后果, 备选方案 (+3 more)

### Community 38 - "ADR-0004：采用同源入口、HttpOnly Cookie 与 API 统一授权"
Cohesion: 0.18
Nodes (11): ADR-0004：采用同源入口、HttpOnly Cookie 与 API 统一授权, Web 自行维护独立权限系统, 决策, 后果, 备选方案, 复审触发条件, 实施约束, 浏览器使用 localStorage 保存 Bearer Token (+3 more)

### Community 39 - "Child Manager PostgreSQL 数据库 Schema"
Cohesion: 0.18
Nodes (11): 11.1 `daily_activity_plan_exports`, 11. Word 导出 Schema, 13. 组合外键矩阵, 14. 应用事务不变量, 15. Alembic 迁移顺序, 16. PostgreSQL 与 SQLite 验证矩阵, 17. 必须实现的 Schema 验收测试, 18. 实现时禁止的捷径 (+3 more)

### Community 40 - "教案管理 PRD（首期：一日活动计划）"
Cohesion: 0.18
Nodes (11): 16. 异常与降级, 19. 风险与缓解, 1. 文档目的, 20. 实施依赖, 21. 架构设计引用, 2. 事实来源, 3. 产品背景, 6.1 包含范围 (+3 more)

### Community 41 - "Core Principles"
Cohesion: 0.18
Nodes (10): Core Principles, Governance, [PRINCIPLE_1_NAME], [PRINCIPLE_2_NAME], [PRINCIPLE_3_NAME], [PRINCIPLE_4_NAME], [PRINCIPLE_5_NAME], [PROJECT_NAME] Constitution (+2 more)

### Community 44 - "Child Manager 文档交叉审计合并结论"
Cohesion: 0.20
Nodes (10): 1. 合并范围与事实来源, 2. 状态与操作类别, 5. M0 阻断项, 6. 建议执行顺序, 7. 验证要求, 8.1 已完成的检查面, 8.2 敏感信息处理边界, 8.3 操作与交付边界 (+2 more)

### Community 45 - "右侧列"
Cohesion: 0.20
Nodes (10): 右侧列, 填写说明, 左侧列, 第一行, 第三行：, 第二行：, 第五行：, 第六行： (+2 more)

### Community 46 - "这是一份word表格"
Cohesion: 0.20
Nodes (10): 填写说明, 填写说明：, 填写说明：, 填写说明：, 文件第一行, 文件第二行, 注意事项：, 表格第一行 (+2 more)

### Community 47 - "18. 验收标准"
Cohesion: 0.22
Nodes (9): 18.1 账号与权限, 18.2 设置, 18.3 教案管理, 18.4 日期规则, 18.5 提示词与 AI, 18.6 集体活动, 18.7 Word 导出, 18.8 运维与安全 (+1 more)

### Community 48 - "Implementation Plan: [FEATURE]"
Cohesion: 0.22
Nodes (8): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: [FEATURE], Project Structure, Source Code (repository root), Summary, Technical Context

### Community 49 - "SKILL.md"
Cohesion: 0.25
Nodes (7): Anti-Examples: What NOT To Do, Checklist Purpose: "Unit Tests for English", Example Checklist Types & Sample Items, Execution Steps, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 50 - "Child Manager OpenAPI v1"
Cohesion: 0.50
Nodes (4): 认证与用户 API, Child Manager OpenAPI v1, 教案任务与导出 API, 设置与提示词 API

### Community 51 - "SKILL.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 52 - "SKILL.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 53 - "3. 总体建模原则"
Cohesion: 0.29
Nodes (7): 3.1 PostgreSQL 是生产事实来源, 3.2 UUIDv7 主键, 3.3 园所隔离, 3.4 时间与日期, 3.5 字符串、枚举和规范化, 3.6 停用、归档与不可变历史, 3. 总体建模原则

### Community 54 - "9. 一日活动计划模型"
Cohesion: 0.29
Nodes (7): 9.1 关系表头与 JSONB 正文, 9.2 `daily_activity_plans`, 9.3 `content` 结构边界, 9.4 `daily_activity_plan_authors`, 9.5 `daily_activity_plan_snapshots`, 9.6 `lesson_plan_sources`, 9. 一日活动计划模型

### Community 56 - "3. 二十六项问题的最终结论"
Cohesion: 0.29
Nodes (7): 3.1 文档命名与 ADR 状态, 3.5 API、任务状态与幂等, 3. 二十六项问题的最终结论, Q12：任务状态机缺少 `expired`, Q13：幂等键定义, Q1：ADR-0001 文件命名, Q2：ADR-0007 被 ADR-0009 取代的标记

### Community 57 - "3.9 Codex 交叉审计事项"
Cohesion: 0.29
Nodes (7): 3.9 Codex 交叉审计事项, Q21：Word 模板真实个人信息, Q22：canonical 数据模型与 Spec Kit 漂移, Q23：生产备份和部署, Q24：对象存储接口预建, Q25：M0 与实现分支启动, Q26：首期时区权限

### Community 58 - "10. 教案栏目与格式"
Cohesion: 0.29
Nodes (7): 10.1 晨间活动, 10.2 晨间谈话, 10.3 集体活动, 10.4 室内区域游戏, 10.5 下午户外游戏, 10.6 一日活动反思, 10. 教案栏目与格式

### Community 59 - "13. AI 生成流程"
Cohesion: 0.29
Nodes (7): 13.1 一键生成, 13.2 分栏目生成, 13.3 集体活动, 13.4 输入上下文, 13.5 异步状态, 13.6 重试策略, 13. AI 生成流程

### Community 60 - "右侧列"
Cohesion: 0.29
Nodes (7): 一日活动反思填写说明, 右侧列, 左侧列, 第一行, 第三行, 第二行, 表格第八行

### Community 61 - "右侧列"
Cohesion: 0.29
Nodes (7): 右侧列, 填写说明, 左侧列, 第一行, 第三行, 第二行, 表格第六行

### Community 62 - "右侧列"
Cohesion: 0.29
Nodes (7): 右侧列, 填写说明, 左侧列, 第一行, 第三行, 第二行, 表格第七行

### Community 63 - "右侧列为两行："
Cohesion: 0.29
Nodes (7): 右侧列为两行：, 填写说明, 填写说明：, 左侧列, 第一行：, 第二行：, 表格第三大行

### Community 64 - "右侧列为两行："
Cohesion: 0.29
Nodes (7): 右侧列为两行：, 填写说明：, 填写说明：, 左侧列, 第一行：, 第二行：, 表格第四行：

### Community 65 - "完整 SDD 工作流"
Cohesion: 0.33
Nodes (6): Spec Kit 任务实施, Spec Kit 实施规划, Spec Kit 功能规格生成, Spec Kit 任务生成, 规格与计划评审门禁, 完整 SDD 工作流

### Community 67 - "5. 园所与身份模型"
Cohesion: 0.33
Nodes (6): 5.1 `kindergartens`, 5.2 `users`, 5.3 `roles`, 5.4 `user_roles`, 5.5 `refresh_tokens`, 5. 园所与身份模型

### Community 68 - "6. 教学设置模型"
Cohesion: 0.33
Nodes (6): 6.1 `age_groups`, 6.2 `classes`, 6.3 `class_teachers`, 6.4 `semesters`, 6.5 `class_areas`, 6. 教学设置模型

### Community 69 - "3. PostgreSQL 物理约定"
Cohesion: 0.33
Nodes (6): 3.1 Schema、扩展与命名, 3.2 通用类型与默认值, 3.3 园所隔离与组合外键, 3.4 规范化列与状态代码, 3.5 不可变与不使用触发器, 3. PostgreSQL 物理约定

### Community 70 - "5. 园所与身份 Schema"
Cohesion: 0.33
Nodes (6): 5.1 `kindergartens`, 5.2 `users`, 5.3 `roles`, 5.4 `user_roles`, 5.5 `refresh_tokens`, 5. 园所与身份 Schema

### Community 71 - "6. 教学设置 Schema"
Cohesion: 0.33
Nodes (6): 6.1 `age_groups`, 6.2 `classes`, 6.3 `class_teachers`, 6.4 `semesters`, 6.5 `class_areas`, 6. 教学设置 Schema

### Community 72 - "9. 一日活动计划 Schema"
Cohesion: 0.33
Nodes (6): 9.1 `daily_activity_plans`, 9.2 `daily_activity_plan_authors`, 9.3 `daily_activity_plan_snapshots`, 9.4 `lesson_plan_sources`, 9.5 `content` JSONB 物理边界, 9. 一日活动计划 Schema

### Community 73 - "9. 后台任务架构"
Cohesion: 0.33
Nodes (6): 9.1 选型与用途, 9.2 状态机, 9.3 投递、幂等与恢复, 9.4 AI 重试与反馈, 9.5 状态获取, 9. 后台任务架构

### Community 74 - "12. AI 模型与提示词管理"
Cohesion: 0.33
Nodes (6): 12.1 七个任务级提示词, 12.2 系统默认提示词, 12.3 自定义提示词生命周期, 12.4 变量白名单, 12.5 提示词测试运行, 12. AI 模型与提示词管理

### Community 75 - "7. 首期必要设置"
Cohesion: 0.33
Nodes (6): 7.1 幼儿园信息, 7.2 学期管理, 7.3 班级与教师, 7.4 班级区域, 7.5 AI 模型档案, 7. 首期必要设置

### Community 76 - "9. 日期与上下文规则"
Cohesion: 0.33
Nodes (6): 9.1 活动日期, 9.2 学期与周次, 9.3 星期与日期格式, 9.4 季节, 9.5 工作日, 9. 日期与上下文规则

### Community 77 - "SKILL.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 78 - "SKILL.md"
Cohesion: 0.40
Nodes (4): Outline, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 79 - "21. 测试与验收"
Cohesion: 0.40
Nodes (5): 21.1 单元测试, 21.2 Repository 与 PostgreSQL 集成测试, 21.3 迁移测试, 21.4 安全测试, 21. 测试与验收

### Community 80 - "5. 代码组织与依赖方向"
Cohesion: 0.40
Nodes (5): 5.1 建议目录, 5.2 后端模块内部方向, 5.3 模块边界, 5.4 深模块接口, 5. 代码组织与依赖方向

### Community 81 - "8. 数据架构"
Cohesion: 0.40
Nodes (5): 8.1 数据所有权, 8.2 一致性边界, 8.3 事务所有权, 8.4 SQLite 使用边界, 8. 数据架构

### Community 83 - "3.2 模板说明与业务规则"
Cohesion: 0.40
Nodes (5): 3.2 模板说明与业务规则, Q3：集体活动新增环节标记, Q4：反思结构与长度, Q5：自然周起始日, Q6：学期首周边界

### Community 84 - "4. 项目文档更新矩阵"
Cohesion: 0.40
Nodes (5): 4.1 必须更新的事实来源, 4.2 Spec Kit 与契约同步, 4.3 只需核验或增加导航的事项, 4.4 FAQ 整理, 4. 项目文档更新矩阵

### Community 85 - "11. 计划管理流程"
Cohesion: 0.40
Nodes (5): 11.1 首页与查询, 11.2 创建或打开计划, 11.3 保存, 11.4 归档, 11. 计划管理流程

### Community 86 - "14. Word 导出"
Cohesion: 0.40
Nodes (5): 14.1 导出前检查, 14.2 模板规则, 14.3 文件名与存储, 14.4 导出历史, 14. Word 导出

### Community 87 - "17. 非功能要求"
Cohesion: 0.40
Nodes (5): 17.1 容量与性能, 17.2 生产可用性与恢复（延后验收）, 17.3 兼容性, 17.4 可测试性, 17. 非功能要求

### Community 88 - "Q: 请阅读以上内容和现有的AGENTS.MD,还有ywyz/kindergartenManager.git的AGENTS.MD，你认为i还需要再加入点什么？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请阅读以上内容和现有的AGENTS.MD,还有ywyz/kindergartenManager.git的AGENTS.MD，你认为i还需要再加入点什么？, Source Nodes

### Community 89 - "Q: 请阅读以上内容和现有的README.md,AGENTS.md,还有ywyz/kindergartenManager.git的文档，你认为CONTEXT.md需要再加入点什么？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请阅读以上内容和现有的README.md,AGENTS.md,还有ywyz/kindergartenManager.git的文档，你认为CONTEXT.md需要再加入点什么？, Source Nodes

### Community 90 - "Q: 请根据现有文档，和旧仓库的文件思考如何撰写 docs/PRD/lesson-management.md"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请根据现有文档，和旧仓库的文件思考如何撰写 docs/PRD/lesson-management.md, Source Nodes

### Community 91 - "Q: 接下来需要生成什么文件呢"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 接下来需要生成什么文件呢, Source Nodes

### Community 92 - "Q: 系统架构文档应如何定义目标服务架构、服务边界、共享契约、部署拓扑与首期实施顺序？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 系统架构文档应如何定义目标服务架构、服务边界、共享契约、部署拓扑与首期实施顺序？, Source Nodes

### Community 93 - "Q: 哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？, Source Nodes

### Community 94 - "Q: 一日活动计划系统的数据实体、关系、唯一约束、历史版本、异步任务和安全边界是什么？"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 一日活动计划系统的数据实体、关系、唯一约束、历史版本、异步任务和安全边界是什么？, Source Nodes

### Community 95 - "Q: 请使用/graphify update. 进行更新，同时使用子代理进行语义更新，然后思考还需要完成什么任务"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: 请使用/graphify update. 进行更新，同时使用子代理进行语义更新，然后思考还需要完成什么任务, Source Nodes

### Community 96 - "Base"
Cohesion: 0.06
Nodes (36): ABC, datetime, AIClientPort, AuditPort, CalendarPort, ClockPort, CryptoPort, DatabaseSessionPort (+28 more)

### Community 98 - "[CHECKLIST TYPE] Checklist: [FEATURE NAME]"
Cohesion: 0.40
Nodes (4): [Category 1], [Category 2], [CHECKLIST TYPE] Checklist: [FEATURE NAME], Notes

### Community 99 - "15. 数据快照边界"
Cohesion: 0.50
Nodes (4): 15.1 教案展示快照, 15.2 AI 输入快照, 15.3 快照不是重复日志, 15. 数据快照边界

### Community 100 - "22. 后续扩展边界"
Cohesion: 0.50
Nodes (4): 22.1 年级组长和园级检查, 22.2 照片与视觉子系统, 22.3 多园 SaaS, 22. 后续扩展边界

### Community 101 - "2. 设计来源与旧系统取舍"
Cohesion: 0.50
Nodes (4): 2.1 事实来源, 2.2 从旧系统吸收的经验, 2.3 明确不继承的旧模型, 2. 设计来源与旧系统取舍

### Community 102 - "8. 提示词模型"
Cohesion: 0.50
Nodes (4): 8.1 `prompt_definitions`, 8.2 `prompt_versions`, 8.3 `prompt_test_runs`, 8. 提示词模型

### Community 103 - "8. 提示词 Schema"
Cohesion: 0.50
Nodes (4): 8.1 `prompt_definitions`, 8.2 `prompt_versions`, 8.3 `prompt_test_runs`, 8. 提示词 Schema

### Community 104 - "10. AI 与提示词架构"
Cohesion: 0.50
Nodes (4): 10.1 AI 适配器, 10.2 提示词服务, 10.3 结果采用边界, 10. AI 与提示词架构

### Community 105 - "6. 请求、认证与授权"
Cohesion: 0.50
Nodes (4): 6.1 同源访问, 6.2 会话链路, 6.3 园所与班级隔离, 6. 请求、认证与授权

### Community 106 - "3.3 数据模型、保留与任务关系"
Cohesion: 0.50
Nodes (4): 3.3 数据模型、保留与任务关系, Q7：历史恢复快照原因, Q8：AI 结果清理与一年审计, Q9：后台任务父子与重试外键

### Community 107 - "3.7 API 与页面信息架构"
Cohesion: 0.50
Nodes (4): 3.7 API 与页面信息架构, Q16：API 端点文档, Q17：前端页面信息架构, Q18：前端 `kindergarten_id`

### Community 108 - "5. 用户与权限"
Cohesion: 0.50
Nodes (4): 5.1 角色, 5.2 账号规则, 5.3 教师与班级, 5. 用户与权限

### Community 109 - "8. 核心业务对象"
Cohesion: 0.50
Nodes (4): 8.1 一日活动计划, 8.2 历史快照, 8.3 导出记录, 8. 核心业务对象

### Community 110 - "11. 后台任务与 AI 结果"
Cohesion: 0.67
Nodes (3): 11.1 `background_jobs`, 11.2 `ai_generation_results`, 11. 后台任务与 AI 结果

### Community 111 - "16. 外键与删除行为"
Cohesion: 0.67
Nodes (3): 16.1 数据库删除规则, 16.2 跨行事务不变量, 16. 外键与删除行为

### Community 112 - "4. 模型总览"
Cohesion: 0.67
Nodes (3): 4.1 首期表清单, 4.2 核心关系图, 4. 模型总览

### Community 113 - "7. AI 模型档案"
Cohesion: 0.67
Nodes (3): 7.1 `ai_model_profiles`, 7.2 `ai_model_profile_capabilities`, 7. AI 模型档案

### Community 114 - "10. 后台任务与 AI 结果 Schema"
Cohesion: 0.67
Nodes (3): 10.1 `background_jobs`, 10.2 `ai_generation_results`, 10. 后台任务与 AI 结果 Schema

### Community 115 - "12. 系统支撑 Schema"
Cohesion: 0.67
Nodes (3): 12.1 `workday_cache`, 12.2 `audit_events`, 12. 系统支撑 Schema

### Community 116 - "2. 事实来源与旧仓库取舍"
Cohesion: 0.67
Nodes (3): 2.1 事实来源, 2.2 旧仓库经验, 2. 事实来源与旧仓库取舍

### Community 117 - "7. AI 模型档案 Schema"
Cohesion: 0.67
Nodes (3): 7.1 `ai_model_profiles`, 7.2 `ai_model_profile_capabilities`, 7. AI 模型档案 Schema

### Community 118 - "11. Word 与文件架构"
Cohesion: 0.67
Nodes (3): 11.1 导出流程, 11.2 上传 `.docx`, 11. Word 与文件架构

### Community 119 - "13. 配置、密钥与安全"
Cohesion: 0.67
Nodes (3): 13.1 配置分级, 13.2 安全边界, 13. 配置、密钥与安全

### Community 120 - "15. 生产部署延后边界"
Cohesion: 0.67
Nodes (3): 15.1 当前阶段, 15.2 功能完成后的复审, 15. 生产部署延后边界

### Community 121 - "4. 架构总览"
Cohesion: 0.67
Nodes (3): 4.1 逻辑视图, 4.2 运行单元, 4. 架构总览

### Community 122 - "7. API 与契约"
Cohesion: 0.67
Nodes (3): 7.1 API 原则, 7.2 跨进程任务契约, 7. API 与契约

### Community 123 - "3.4 加密与密钥"
Cohesion: 0.67
Nodes (3): 3.4 加密与密钥, Q10：AI Key 加密算法, Q11：主加密密钥来源

### Community 124 - "3.6 测试与可访问性"
Cohesion: 0.67
Nodes (3): 3.6 测试与可访问性, Q14：并发、故障和恢复测试, Q15：WCAG 覆盖范围

### Community 125 - "3.8 编辑与 AI 采用"
Cohesion: 0.67
Nodes (3): 3.8 编辑与 AI 采用, Q19：新增集体活动环节的插入位置, Q20：自动保存失败

### Community 126 - "15. 安全、隐私与审计"
Cohesion: 0.67
Nodes (3): 15.1 敏感数据, 15.2 审计事件, 15. 安全、隐私与审计

### Community 127 - "4. 产品目标"
Cohesion: 0.67
Nodes (3): 4.1 首期目标, 4.2 成功标准, 4. 产品目标

### Community 128 - "test_config.py"
Cohesion: 0.15
Nodes (20): BaseSettings, Settings, test_allowed_hosts(), test_cookie_security_non_loopback(), test_cookie_security_production(), test_cookie_security_validation(), test_database_url(), test_jwt_settings() (+12 more)

### Community 607 - "BaseModel"
Cohesion: 0.21
Nodes (17): DailyReflection, LessonPlan, PlanArchiveRequest, PlanAuthor, PlanAutoSaveRequest, PlanContentV1, PlanCreateRequest, PlanListResponse (+9 more)

### Community 608 - "main.py"
Cohesion: 0.09
Nodes (45): _ai_unconfigured(), build_health_dependencies(), _calendar_library_available(), create_app(), custom_openapi(), _error_response(), HealthDependencies, _http_exception_handler() (+37 more)

### Community 609 - "settings.py"
Cohesion: 0.33
Nodes (10): ChangePasswordRequest, LoginRequest, LoginResponse, BaseModel, Role, TokenRefreshResponse, User, UserCreate (+2 more)

### Community 610 - "common.py"
Cohesion: 0.10
Nodes (34): canonical_fingerprint(), ErrorResponse, FieldError, HealthCheckResult, HealthResponse, idempotency_key_from_fingerprint(), IdempotencyKey, PaginatedResponse (+26 more)

### Community 611 - "jobs.py"
Cohesion: 0.27
Nodes (11): AIAdoptRequest, AIResult, Job, JobBatchCreateRequest, JobCreateRequest, JobListResponse, JobRetryRequest, JobStatus (+3 more)

### Community 612 - "prompts.py"
Cohesion: 0.30
Nodes (11): Prompt, PromptCapability, PromptCreateRequest, PromptPublishRequest, PromptResultSchema, PromptTestRequest, PromptTestRun, PromptUpdateRequest (+3 more)

### Community 613 - "identity.py"
Cohesion: 0.16
Nodes (13): DeclarativeBase, get_database_url(), Alembic 迁移环境。  模块级代码需兼容两种导入方式： 1. alembic.command.upgrade/downgrade 调用时，context., run_migrations_offline(), run_migrations_online(), Base, get_db_session(), get_db_session 应该在成功时提交 (+5 more)

### Community 614 - "exports.py"
Cohesion: 0.14
Nodes (18): build_deterministic_test_broker(), build_redis_broker(), Broker, main(), Broker, Event, serve(), Event (+10 more)

### Community 615 - "models.py"
Cohesion: 0.33
Nodes (8): ModelCapability, ModelProfile, ModelProfileCreateRequest, ModelProfileEnableRequest, ModelProfileListResponse, ModelProfileUpdateRequest, BaseModel, StrEnum

### Community 616 - "audit.py"
Cohesion: 0.17
Nodes (11): downgrade(), upgrade(), block_external_network(), isolated_database_url(), _native_psycopg_url(), MonkeyPatch, require_test_database_url(), MonkeyPatch (+3 more)

### Community 702 - "0000_foundation.py"
Cohesion: 0.30
Nodes (16): _always_false(), _always_true(), client_factory(), _error_schema(), _health_schema(), _make_dependencies(), 健康检查端点权威行为覆盖。  验证运行时 /health/live 和 /health/ready 响应符合静态 OpenAPI 契约， 而非仅验证 YAML, test_live_response_has_no_extra_fields() (+8 more)

### Community 705 - "redact_dict"
Cohesion: 0.12
Nodes (26): EventDict, configure_logging(), Any, 结构化日志配置与脱敏处理器。  将 redaction 模块接入 structlog 处理链，确保日志中的敏感字段 （密钥、密码、令牌、Cookie 等）在输出, structlog 处理器：递归脱敏事件字典中的敏感字段。, 配置 structlog 处理链，包含脱敏处理器。, redaction_processor(), _is_sensitive_key() (+18 more)

## Knowledge Gaps
- **1350 isolated node(s):** `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script`, `setup-plan.sh script`, `setup-tasks.sh script` (+1345 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **533 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Work-memory lessons

**Preferred sources** — corroborated by past sessions; start here.
- `班级与教师配置` (2× useful, score=1.881901363)

**Known dead ends** — questions that led nowhere; don't re-derive.
- "哪些关键架构决策需要独立 ADR，哪些已经确认，决策之间有什么依赖？" -> `需要直接比较文件`

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `教案管理 PRD（首期：一日活动计划）` connect `教案管理 PRD（首期：一日活动计划）` to `README.md`, `12. AI 模型与提示词管理`, `7. 首期必要设置`, `5. 用户与权限`, `8. 核心业务对象`, `9. 日期与上下文规则`, `18. 验收标准`, `11. 计划管理流程`, `14. Word 导出`, `17. 非功能要求`, `10. 教案栏目与格式`, `13. AI 生成流程`, `15. 安全、隐私与审计`, `4. 产品目标`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `Child Manager PostgreSQL 数据库 Schema` connect `Child Manager PostgreSQL 数据库 Schema` to `3. PostgreSQL 物理约定`, `5. 园所与身份 Schema`, `README.md`, `6. 教学设置 Schema`, `8. 提示词 Schema`, `9. 一日活动计划 Schema`, `10. 后台任务与 AI 结果 Schema`, `12. 系统支撑 Schema`, `2. 事实来源与旧仓库取舍`, `7. AI 模型档案 Schema`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `Child Manager 数据模型设计` connect `Child Manager 数据模型设计` to `15. 数据快照边界`, `22. 后续扩展边界`, `2. 设计来源与旧系统取舍`, `5. 园所与身份模型`, `README.md`, `6. 教学设置模型`, `8. 提示词模型`, `11. 后台任务与 AI 结果`, `16. 外键与删除行为`, `21. 测试与验收`, `4. 模型总览`, `7. AI 模型档案`, `3. 总体建模原则`, `9. 一日活动计划模型`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **What connects `check-prerequisites.sh script`, `common.sh script`, `create-new-feature.sh script` to the rest of the system?**
  _1350 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Child Manager 产品与工程路线图` be split into smaller, more focused modules?**
  _Cohesion score 0.04081632653061224 - nodes in this community are weakly interconnected._
- **Should `M0 阻塞项统一修复执行方案（Codex + Trae）` be split into smaller, more focused modules?**
  _Cohesion score 0.045454545454545456 - nodes in this community are weakly interconnected._
- **Should `Child Manager 2026-07-14 编码前审查解决方案` be split into smaller, more focused modules?**
  _Cohesion score 0.046511627906976744 - nodes in this community are weakly interconnected._