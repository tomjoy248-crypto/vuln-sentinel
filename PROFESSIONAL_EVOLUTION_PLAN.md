# 漏洞哨兵 11-S 专业化进化计划

## 一、整体判断

`v11-s-vuln-sentinel` 已从“扫描 demo”进化为具备真实检测能力（响应头、SSL、敏感路径、SQLi/XSS/命令注入/目录遍历/SSRF/反序列化/开放重定向/SRI/过时组件等）、JWT 认证、工单、资产监控、告警、SRC 报告、AI 修复建议的 Web 平台，测试基线 182 passed。

但代码仍高度集中在 `main.py` 与 `src_scanner.py` 中，数据库直接复用 `sqlite3` 裸 SQL，缺少数据库迁移、分布式任务队列、生产级可观测性与企业级多租户隔离。专业化进化的核心工作是把“单文件 FastAPI 应用”拆分为“可运维、可扩展、可计费的商业 SaaS 基础架构”。

---

## 二、当前代码库现状与主要缺口

### 1. 工程化与架构

| 维度 | 当前现状 | 主要缺口 | 关键文件 |
|---|---|---|---|
| 代码组织 | 后端核心逻辑集中在 `main.py`（约 11k+ 行），扫描引擎在 `src_scanner.py`；Pydantic 模型在 `models.py`；工具函数在 `utils.py` | 缺少按 domain 路由（auth/scan/asset/ticket/report/ai/team/admin）的拆分；业务逻辑、数据访问、HTTP 层未分离；单文件维护成本高 | `main.py`、`src_scanner.py` |
| 数据库 | 使用 `sqlite3` 裸 SQL + 启动时 `init_db()` 建表；通过 `ALTER TABLE` 做运行时迁移 | 无版本化迁移工具；无 ORM/Repository 层；无法平滑切换到 PostgreSQL/MySQL；多 worker 写 SQLite 存在并发与损坏风险 | `main.py` 中 `init_db()` |
| CI/CD | `.github/workflows/ci.yml` 已能跑测试、启动服务、做公开 demo 扫描、PR 评论 | 无代码格式/静态检查（ruff/black/mypy）；Python 版本未矩阵化；无 Docker 镜像构建/推送；无 release 自动化；测试使用 `--break-system-packages` | `.github/workflows/ci.yml` |
| 容器化 | 已有单阶段 `Dockerfile` 与 `render.yaml` | 缺少 `docker-compose.yml`、多阶段构建、non-root 运行、HEALTHCHECK、Nginx/Traefik 反向代理配置；SQLite 不适合容器多副本 | `Dockerfile`、`render.yaml` |
| 配置管理 | 使用 `pydantic_settings` + `.env`；`.env.example` 较完整 | 生产 secret 仍建议从文件/外部 KMS 读取；缺少配置校验与启动时依赖检查 | `.env.example`、`main.py` `Settings` |

### 2. 安全与合规

| 维度 | 当前现状 | 主要缺口 | 关键文件 |
|---|---|---|---|
| 认证授权 | JWT + bcrypt；token 中携带 `role`/`team_id`；支持 admin/member/viewer 三种团队角色 | 角色校验只在团队相关接口使用，扫描/资产/工单等接口未做细粒度权限检查；缺少权限矩阵与统一依赖 | `main.py` `require_login`、团队路由 |
| 审计日志 | 仅有 `/api/scan-auth-log` 把授权时间打到普通 logger | 无结构化审计表；无法追溯谁、何时、对哪条数据做了什么操作；无保留策略 | `main.py` `/api/scan-auth-log` |
| 密钥管理 | `JWT_SECRET`、`SMTP_PASSWORD`、`LLM_API_KEY`、`CREDENTIAL_ENCRYPT_KEY` 通过环境变量传入；开发环境会落盘 `.jwt_secret` | 敏感配置可能进日志/报错堆栈；`CREDENTIAL_ENCRYPT_KEY` 未看到实际使用；缺少密钥轮换 | `main.py`、`.env.example` |
| 数据保护 | SQLite 明文存储；扫描结果、邮箱、webhook 等未加密 | 缺少静态加密/字段级加密；无数据保留与删除策略；未做 PII 脱敏 | 数据库模型 |
| 多租户隔离 | 用户表有 `team_id`，资源按 `user_id` 过滤 | 无项目/工作区概念；团队级资源未统一按 `team_id` 过滤；未来企业客户需要组织级隔离 | `main.py` 用户/扫描/资产表 |
| 合规映射 | findings 已带 OWASP/CWE/CVSS 字段；README 提到等保自查 | 缺少与等保 2.0、ISO 27001、GDPR 的映射表；合规报告模板未成体系 | `src_scanner.py`、`README.md` |

### 3. 可观测性

| 维度 | 当前现状 | 主要缺口 | 关键文件 |
|---|---|---|---|
| 日志 | 标准库 `logging`，请求中间件记录 IP/方法/状态/耗时 | 非结构化文本日志；无 correlation ID；日志未分级写入文件；敏感信息可能泄露 | `main.py` 日志配置、请求中间件 |
| 指标 | 仅有内存中的扫描缓存命中率统计 | 无 Prometheus/Metrics 端点；无扫描数/修复数/错误率/延迟分位值 | `main.py` `_SCAN_CACHE_HITS` |
| 健康检查 | `/api/health` 返回 DB 状态与 uptime | 缺少 `/health/live`（存活）与 `/health/ready`（就绪，含外部依赖） | `main.py` `/api/health` |
| 错误追踪 | 全局异常处理器返回 `{success:false, code:INTERNAL_ERROR}` | 未接入 Sentry 等错误追踪；生产问题定位靠 tail 日志 | `main.py` 异常处理器 |

### 4. 可扩展性

| 维度 | 当前现状 | 主要缺口 | 关键文件 |
|---|---|---|---|
| 扫描调度 | 扫描在请求协程中同步执行；APScheduler 在进程内跑定时任务 | 长扫描会阻塞 HTTP worker；无任务队列；多副本会重复调度 | `main.py` `api_scan`、scheduler |
| 并发资产扫描 | 批量扫描最多 5 URL 顺序/少量并发 | 无资产级并发控制；无每个租户/任务的并发配额；大资产列表会打爆连接池 | `main.py` `BatchScanRequest` |
| 插件化引擎 | 检测规则硬编码在 `main.py`/`src_scanner.py` | 无插件注册表；无法动态加载自定义检测器；企业客户无法定制规则 | `main.py`、`src_scanner.py` |
| SARIF/API 集成 | 可导出 PDF/Markdown；无 SARIF | 缺少 SARIF 2.1.0 导入/导出；无法与 GitHub Code Scanning/企业安全中台对接 | `main.py` `/api/report/src-export` |
| 缓存/限流 | 内存 LRU 缓存 + 内存滑动窗口限流 | 多实例部署时限流失效；无 Redis 集中缓存 | `main.py` `RateLimiter` |

### 5. 用户体验

| 维度 | 当前现状 | 主要缺口 | 关键文件 |
|---|---|---|---|
| 文档 | README 详细；有架构图与截图 | 缺少面向最终用户的操作手册、管理员部署手册、API 集成指南 | `README.md`、`docs/` |
| Onboarding | 前端有授权复选框与 localStorage 记忆 | 缺少首次使用引导、空状态说明、交互式教程 | `frontend/src/main.js` |
| 报告模板 | PDF 通过 reportlab 生成；Markdown 报告 | 缺少 HTML 报告、可定制品牌模板、SARIF/CSV 导出 | `main.py` `/api/report/*` |
| 响应式 | 前端使用 Vite + 原生 JS，有 CSS 变量 | 桌面安全工具风格为主，移动端适配不足；缺少亮色主题切换 | `frontend/src/style.css`、`frontend/src/pages/` |

### 6. 商业化基础

| 维度 | 当前现状 | 主要缺口 | 关键文件 |
|---|---|---|---|
| 团队/项目 | 用户可创建/加入团队，role=admin/member/viewer | 无项目/工作区层级；团队资源未统一隔离；缺少组织（organization）模型 | `main.py` 团队路由 |
| 许可证/订阅 | README 列出免费/专业/团队/企业价格 | 无订阅表、feature flags、配额控制；无法阻止免费用户无限扫描 | `README.md` |
| API 限流与计费 | 按 IP/用户内存限流；扫描缓存按 user+url+depth | 缺少 API Key 体系、按订阅配额的限流、计费事件埋点、使用量统计 | `main.py` `RateLimiter` |

---

## 三、分阶段实施路线图

> 说明：以下按“先打地基、再补生产、最后企业级”排序。每个阶段内按依赖关系编排，不包含时间排期。

### 阶段一：MVP 可用（可维护、可部署、基本安全）

**目标**：把单文件应用拆成可维护的模块；引入迁移与基础 CI 质量门；补齐审计、权限过滤、日志与健康检查，使产品达到“可交付给早期付费用户”的水平。

| 关键任务 | 涉及文件/模块 | 验收标准 |
|---|---|---|
| 1.1 后端模块拆分 | 新建 `app/` 包：`routers/`、`services/`、`repositories/`、`core/`、`models/`、`schemas/`；将 `main.py` 的路由迁移到 `routers/`，业务逻辑下沉到 `services/`，SQL 操作下沉到 `repositories/` | `main.py` 仅保留 FastAPI 工厂、中间件注册、lifespan；`pytest tests/` 仍 182 passed；新增模块间无循环导入 |
| 1.2 引入 Alembic 数据库迁移 | 新增 `alembic/`、`migrations/`；用 Alembic 重写现有表结构；保留 SQLite 默认，但表结构由迁移文件定义 | 新环境执行 `alembic upgrade head` 即可建表；旧数据库能通过迁移脚本升级；CI 校验迁移文件与模型一致 |
| 1.3 统一配置与 secret 管理 | 扩展 `.env.example`；`Settings` 增加 `database_url`、`redis_url`、`sentry_dsn` 等；生产模式拒绝弱 secret | 启动时若关键配置缺失则清晰报错；敏感配置不进入日志 |
| 1.4 完善 CI 质量门 | 更新 `.github/workflows/ci.yml`：矩阵 Python 3.10/3.11/3.12；增加 ruff、black、pytest-cov；移除 `--break-system-packages` | CI 失败时阻止合并；覆盖率基线 ≥ 当前水平 |
| 1.5 审计日志表与中间件 | 新增 `audit_logs` 表与 `audit_log()` 依赖；记录登录、扫描、导出、角色变更、敏感数据删除 | 任何写操作可在审计表查到 user/action/resource/timestamp；保留 90 天 |
| 1.6 资源所有权与团队过滤 | 所有扫描/资产/工单/告警查询统一加上 `user_id`/`team_id` 过滤；新增 `require_role` 依赖 | 测试验证 A 用户无法读取 B 用户扫描记录；viewer 角色无法创建扫描 |
| 1.7 结构化日志与健康检查 | 引入 `structlog`（JSON 输出）；新增 `/health/live`、`/health/ready`、`/health/version` | 日志可输出到 stdout 并被日志平台解析；ready 探针失败时 K8s 不接入流量 |
| 1.8 前端响应式与错误兜底 | 优化 `frontend/src/style.css` 媒体查询；保持全局错误兜底 | 在 375px 宽度下首页、报告页可正常浏览无横向滚动 |

### 阶段二：生产可用（可运维、可扩展、可计费）

**目标**：引入任务队列与独立 worker、集中缓存、PostgreSQL 支持、可观测性栈、SARIF/API 集成、项目级隔离与使用量计费，支撑公开 SaaS 运营。

| 关键任务 | 涉及文件/模块 | 验收标准 |
|---|---|---|
| 2.1 异步扫描任务队列 | 引入 Celery + Redis；`api_scan` 改为提交任务并返回 `job_id`；新增 `/api/jobs/{job_id}` 查询结果；APScheduler 改为 Celery beat | 扫描 10 秒以上任务不阻塞 HTTP；worker 崩溃可重试；支持 `/api/scan-progress/{token}` 继续显示进度 |
| 2.2 分布式限流与缓存 | Redis 实现 `RateLimiter` 与扫描结果缓存；按用户/订阅计划设置配额 | 多实例部署时同用户仍被正确限流；缓存命中率可观测 |
| 2.3 支持 PostgreSQL | 在 repository 层抽象数据库连接；通过 `DATABASE_URL` 切换 Postgres/SQLite；生产推荐 Postgres | 切换数据库后所有测试通过；使用连接池 |
| 2.4 可观测性栈 | Prometheus `/metrics`（`prometheus-fastapi-instrumentator` 或 `starlette_exporter`）；Sentry 集成；Grafana 仪表盘 | 可查看 `http_request_duration_seconds`、`scans_total`、`scan_errors_total` 等指标 |
| 2.5 插件化检测引擎 | 定义 `BaseVulnDetector` 接口；新增 `plugins/` 目录与注册表；把现有检测拆分为插件；支持自定义规则 YAML/JSON | 新增插件无需修改核心代码；插件加载失败不影响整体启动 |
| 2.6 SARIF 导入/导出 | 新增 `/api/report/sarif-export`、`/api/report/sarif-import`；输出符合 SARIF 2.1.0 | GitHub Code Scanning 可成功导入导出文件 |
| 2.7 项目/工作区隔离 | 新增 `projects` 表；扫描/资产/工单归属到 `project_id`；用户可在团队下创建多个项目 | 项目 A 成员无法看到项目 B 的资源 |
| 2.8 订阅配额与 API Key | 新增 `plans`、`subscriptions`、`api_keys`、`usage_records` 表；按 plan 限制每月扫描数/AI 调用数/成员数 | 免费用户达上限后接口返回 `429` 并提示升级；支持按 API Key 调用 |
| 2.9 文档与 Onboarding | 用 MkDocs/Docusaurus 搭建用户文档站；前端增加首次登录引导与空状态说明 | 新用户 5 分钟内完成首次扫描并理解报告含义 |
| 2.10 容器编排 | 新增 `docker-compose.yml`（app + postgres + redis + worker）；Dockerfile 改为多阶段、non-root、HEALTHCHECK | `docker compose up` 可一键拉起完整环境 |

### 阶段三：企业就绪（合规、可审计、可集成）

**目标**：满足中大型企业与安全团队的合规、审计、集成、定制需求，支持私有化部署与 SLA。

| 关键任务 | 涉及文件/模块 | 验收标准 |
|---|---|---|
| 3.1 企业级 RBAC | 引入基于资源/操作的权限模型（如 `scan:create`、`asset:delete`）；支持自定义角色 | 可在界面上为角色勾选权限集合 |
| 3.2 SSO/SAML/OIDC | 集成 OAuth2/OIDC（GitHub/Google/企业 IdP）；支持 SAML 2.0 | 企业客户可通过自有 IdP 登录并自动映射角色 |
| 3.3 高级合规映射与报告 | 新增合规框架表（等保 2.0、ISO 27001、GDPR）；报告可按框架筛选；支持审计报告导出 | 等保相关 findings 能映射到具体控制点 |
| 3.4 审计与数据保留策略 | 审计日志不可删除；支持按法规设置数据保留期；支持数据导出与删除（GDPR 被遗忘权） | 管理员可导出指定用户全部数据；过期数据自动归档 |
| 3.5 高可用与水平扩展 | 无状态化设计；多个 worker 消费同一队列；会话进 Redis；数据库读写分离可选 | 单实例故障不影响扫描任务执行 |
| 3.6 插件市场与企业规则 | 插件支持热加载、版本管理、签名校验；企业可上传私有检测插件 | 私有插件仅本组织可见 |
| 3.7 计费与发票 | 集成 Stripe/支付宝/微信支付；生成账单、发票、使用量明细 | 用户可在账单页查看每月明细 |
| 3.8 SLA 监控与告警 | 定义并监控 API 可用性、扫描完成时间；异常时通过 PagerDuty/Slack/飞书告警 | SLA 低于阈值时自动触发告警 |
| 3.9 安全加固与渗透测试 | 第三方渗透测试；修复高危漏洞；引入依赖安全扫描（`pip-audit`/`safety`）、SBOM | 无高危漏洞；CI 中阻塞存在已知 CVE 的依赖 |
| 3.10 私有化部署包 | 提供 Helm Chart / kustomize；离线安装文档；License 校验机制 | 客户在内网可完成部署并激活 License |

---

## 四、推荐立即开始的 1-2 个任务

### 任务 A：后端模块化 + Alembic 迁移（阶段一 1.1 & 1.2）

这是所有后续工作的前置条件。不拆分模块，任何可观测性、多租户、插件化都会直接改到同一份 `main.py`，风险极高。

**具体做法**：
1. 创建 `app/` 目录结构：
   - `app/core/config.py`：迁移 `Settings`。
   - `app/core/security.py`：JWT、密码哈希、依赖。
   - `app/db/session.py`：数据库连接与 session。
   - `app/repositories/*.py`：users、scans、assets、tickets、alerts 等 CRUD。
   - `app/services/*.py`：扫描服务、修复服务、AI 服务、工单服务。
   - `app/routers/*.py`：对应 HTTP 路由。
   - `app/models.py` / `app/schemas.py`：数据库模型与请求/响应 schema。
   - `app/main.py`：FastAPI 工厂。
2. 用 SQLAlchemy 2.0 声明模型，并配置 Alembic；将现有 `init_db()` 中的 `CREATE TABLE` 与 `ALTER TABLE` 迁移脚本化。
3. 保持现有 SQLite 为默认，但模型设计兼容 PostgreSQL。

**验收标准**：`pytest tests/` 仍 182 passed；`alembic upgrade head` 可创建与当前一致的数据库；`main.py` 行数降至 500 行以内。

### 任务 B：结构化日志 + 健康检查 + Prometheus 指标（阶段一 1.7 & 阶段二 2.4 的基础）

这是“生产可用”的最小可观测性集合，投入小、见效快，能让部署和排障从“盲跑”变成“可监控”。

**具体做法**：
1. 引入 `structlog`，输出 JSON；替换所有 `logger.info(f"...")` 为 `logger.info("event", key=value)`；添加 `request_id` 中间件。
2. 将 `/api/health` 拆为 `/health/live`、`/health/ready`、`/health/version`；ready 检查数据库连接。
3. 引入 `prometheus-fastapi-instrumentator`，暴露 `/metrics`，并自定义 `scans_total{status}`、`scan_duration_seconds`、`scan_cache_hit_rate` 等指标。
4. 增加 Sentry 初始化（可选但推荐），在全局异常处理器中上报。

**验收标准**：`docker logs` 输出 JSON 可被解析；`/health/ready` 在数据库断开时返回 503；`/metrics` 可被 Prometheus 抓取并看到请求延迟直方图。

---

## 五、保存建议

将以上内容整理后保存为：

```text
/workspace/v11-s-vuln-sentinel/PROFESSIONAL_EVOLUTION_PLAN.md
```

---

## 六、补充说明

- 所有路径均指向当前项目目录。
- 阶段划分采用“能力成熟度”而非“日历周期”，便于根据实际资源灵活调整节奏。
- 建议先完成 **任务 A** 再进入 **任务 B**，因为日志/健康/指标本身也需要挂在拆分后的模块上。
