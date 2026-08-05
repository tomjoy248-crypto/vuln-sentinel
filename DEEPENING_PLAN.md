# 漏洞哨兵 11-S 软件深化实施规划

## 说明

本规划面向将 `v11-s-vuln-sentinel` 从现有 demo 形态深化为可实战应用的安全平台。当前代码主干仍集中在 `main.py`（约 11k 行）与 `src_scanner.py`，检测插件框架已存在于 `app/plugins/` 但尚未完全承接全部检测能力；前端已具备暗色风格基础。本规划围绕精准定位、可执行修复、修复闭环、流程追溯、UI 专业化、引擎扩展性与准确性七个核心诉求展开。

---

## 一、整体架构设计建议

### 1.1 分层架构

将后端从单文件拆分为四层结构：

| 层级 | 职责 | 对应目录 |
|---|---|---|
| 接入层 | HTTP 路由、认证鉴权、限流、参数校验 | `app/routers/` |
| 核心引擎层 | 扫描调度、检测插件、修复生成、复测验证 | `app/services/`, `app/plugins/`, `app/remediation/`, `app/verification/` |
| 数据层 | 扫描记录、资产、工单、用户数据持久化 | `app/repositories/`, `app/db/` |
| 平台层 | 任务队列、审计日志、健康检查、Prometheus 指标、配置中心 | `app/core/`, `app/audit/`, `app/metrics/`, `app/health/` |

### 1.2 核心数据流

```
扫描请求 -> 接入层 -> 扫描调度器 -> 检测插件并发执行 -> 证据链构建 -> Finding 模型
                                          |
修复模板引擎 <- 修复工单系统 <- 修复方案生成 <- 交叉验证引擎
       |
配置包应用 -> 复测验证 -> 差异对比 -> 闭环报告
```

### 1.3 关键设计原则

- **领域拆分优先**：先把 `main.py` 中的路由、业务逻辑、SQL 操作分离，再引入更复杂功能。
- **Finding 是核心实体**：每个漏洞发现必须携带 URL、参数、请求/响应片段、代码位置、置信度、CWE/OWASP 映射。
- **插件化是默认形态**：所有新增检测器必须继承 `BaseVulnDetector`，通过注册表加载。
- **修复方案可落地**：修复模板按服务器类型（nginx/apache/express/flask/spring_boot/cloudflare）组织，支持配置包导出与 SSH 应用。
- **闭环可追溯**：扫描、确认、修复、验证、报告五个环节均生成状态事件并写入审计。

---

## 二、分阶段实施路线图

### 阶段一：工程骨架与精准定位

目标：把单文件应用拆成可维护结构，建立统一的 Finding 模型和证据链，使漏洞定位能力达到 URL/参数/请求响应片段级别。

1. **后端模块拆分**：将 `main.py` 中的路由、服务、数据访问分别迁移到 `app/routers/`、`app/services/`、`app/repositories/`。
2. **统一 Finding 数据模型**：定义包含 `location`、`request_snippet`、`response_snippet`、`code_location`、`confidence`、`cwe_id`、`owasp_category` 的标准模型。
3. **检测器全面插件化**：把仍内嵌在 `main.py` 与 `src_scanner.py` 中的检测逻辑迁移到 `app/plugins/detectors`。
4. **证据链与请求/响应片段捕获**：在 HTTP 客户端层统一记录原始请求与响应片段，关联到每个 Finding。
5. **Burp 风格 UI 基础组件库**：建立可复用的暗色主题表格、请求/响应查看器、Severity Badge、Finding 详情面板。

### 阶段二：修复工程化与闭环

目标：让修复方案从文本建议升级为可直接应用的配置代码，并打通扫描->确认->修复->验证的完整闭环。

1. **修复模板引擎重构**：按漏洞类型 x 服务器类型组织模板，支持变量注入与条件渲染。
2. **修复工单工作流**：扩展 `fix_tickets` 表，支持 pending/confirmed/applying/fixed/failed/rolled_back 状态流转。
3. **修复应用与回滚机制**：完善 `api/auto-fix` 的 SSH 路径，增加配置备份、原子写入、回滚能力。
4. **复测验证引擎**：对比修复前后两次扫描的 findings 集合差异与评分变化，生成结构化 diff。
5. **修复闭环可视化**：前端增加闭环时间线，展示每个环节状态与操作人。

### 阶段三：检测能力扩展与准确性

目标：降低误报，支持快速新增漏洞类型，建立交叉验证与反馈学习机制。

1. **插件注册表与热加载**：支持从 `rules/` 目录与数据库动态加载插件配置，无需重启。
2. **交叉验证引擎**：对同一个潜在漏洞使用多种技术手段验证（错误回显 + 时间延迟 + 响应差异）。
3. **误报反馈与学习**：用户可以标记误报，系统记录并用于调整检测规则置信度。
4. **新检测器开发框架**：提供 `BaseVulnDetector` 模板、单元测试模板、fixtures，使新增一种检测器的工作量控制在 1 个文件 + 1 个测试。
5. **检测知识库**：维护 payload 库、签名库、已知 CVE 组件库，支持版本化更新。

### 阶段四：生产化与可观测性

目标：支撑多用户、长时间运行、可运维部署。

1. **异步扫描任务队列**：将同步扫描改为 Celery/ARQ 异步任务，HTTP 层只负责任务提交与进度查询。
2. **数据库迁移与 PostgreSQL 支持**：引入 Alembic，保留 SQLite 开发模式，生产推荐 PostgreSQL。
3. **可观测性栈**：完善 `/health/live`、`/health/ready`、`/metrics`，接入 Sentry。
4. **安全加固与权限模型**：细化 RBAC、资源所有权校验、审计日志不可删除、敏感配置外部化。

---

## 三、第一阶段具体任务清单与验收标准

### 任务 1.1 后端模块拆分

**目标**：将 `main.py` 中混杂的路由、业务、数据访问代码拆分到标准目录。

**涉及文件与目录**：
- 新增：`app/routers/auth.py`、`app/routers/scan.py`、`app/routers/asset.py`、`app/routers/ticket.py`、`app/routers/report.py`、`app/routers/ai.py`
- 新增：`app/services/scan_service.py`、`app/services/remediation_service.py`、`app/services/asset_service.py`
- 新增：`app/repositories/user_repo.py`、`app/repositories/scan_repo.py`、`app/repositories/asset_repo.py`、`app/repositories/ticket_repo.py`
- 改造：`main.py` 仅保留 FastAPI 工厂、中间件注册、lifespan。

**验收标准**：
- `main.py` 行数降至 1000 行以内。
- `pytest tests/` 仍保持 182 passed、7 skipped。
- 新增模块间无循环导入。
- 所有现有 API 端点行为与返回值不变。

### 任务 1.2 统一 Finding 数据模型

**目标**：建立全平台统一的漏洞发现实体，支持精准定位与证据展示。

**字段定义**：

```python
class Finding(BaseModel):
    id: str                      # VS-UUID
    title: str
    type: str                    # sqli / xss / csrf / ...
    severity: str                # critical / high / medium / low / info
    confidence: str              # high / medium / low
    cvss_score: Optional[float]
    cwe_id: str
    owasp_category: str

    location: VulnLocation       # URL、参数、代码位置
    evidence: Evidence           # 请求/响应片段、匹配文本、截图
    fix: FixSuggestion           # 多平台修复代码
    status: str = "open"         # open / confirmed / false_positive / fixed
```

**验收标准**：
- 所有现有 detection 路径返回的 finding 均符合新模型。
- 前端 `result.js` 与 `fixer.js` 能正常展示新字段。
- 数据库 `findings_json` 字段与新模型 JSON 序列化兼容。

### 任务 1.3 检测器全面插件化迁移

**目标**：让 `app/plugins/` 承接全部检测能力，新增检测器不改动核心代码。

**涉及文件**：
- 改造：`app/plugins/builtin.py`
- 改造：`app/plugins/detectors/__init__.py`
- 新增：`app/plugins/detectors/sqli.py`、`xss.py`、`csrf.py`、`ssrf.py`、`idor.py`、`file_upload.py`、`path_traversal.py`、`cmdi.py`、`deserialization.py`、`info_leak.py`、`outdated_component.py`、`open_redirect.py`、`xxe.py`
- 改造：`src_scanner.py` 中常量保留为插件内部数据

**验收标准**：
- 原有 10+ 种漏洞检测能力不丢失。
- 新增一种检测器只需在 `app/plugins/detectors/` 新建文件并在 `builtin.py` 注册。
- 单个插件异常不影响整体扫描流程。

### 任务 1.4 证据链与请求/响应片段捕获

**目标**：每个 finding 都能追溯到具体请求和响应片段，支撑人工研判与报告输出。

**涉及文件**：
- 新增：`app/core/http_recorder.py`
- 改造：`app/services/scan_service.py` 中的 HTTP 调用层
- 改造：`app/plugins/__init__.py` 的 `ScanContext`

**验收标准**：
- 任意 SQLi/XSS finding 必须包含触发该发现的完整 URL、参数、payload、请求片段、响应片段。
- 响应片段中不再出现完整 session cookie。
- 证据存储大小可控，单条 finding 证据不超过 50KB。

### 任务 1.5 Burp 风格 UI 基础组件库

**目标**：前端向 Burp Suite 专业暗色工作台靠拢，提高信息密度与操作效率。

**涉及文件**：
- 新增：`frontend/src/components/burp/` 目录
- 改造：`frontend/src/style.css`

**组件清单**：
- `BurpTable`：紧凑表格，行高 28px，选中行高亮，支持排序与过滤。
- `RequestViewer`：左右分栏展示原始请求与响应，支持高亮匹配片段。
- `SeverityBadge`：critical/high/medium/low/info 五色标签。
- `FindingPanel`：finding 详情面板，包含 Location/Evidence/Fix 三个 Tab。
- `WorkbenchLayout`：顶部工具栏 + 左侧导航 + 主内容区 + 底部状态栏。

**验收标准**：
- 首页、扫描结果页、漏洞详情页完成 Burp 风格改造。
- 在 1440x900 分辨率下，结果页一屏可见至少 12 条 finding。
- 暗色主题色值统一使用 CSS 变量，不引入动画与阴影。

---

## 四、需要新增/重构的关键模块

### 4.1 新增模块

| 模块 | 路径 | 作用 |
|---|---|---|
| Finding 模型 | `app/models/finding.py` | 统一漏洞发现实体 |
| HTTP 记录器 | `app/core/http_recorder.py` | 捕获请求/响应片段 |
| 修复模板引擎 | `app/remediation/template_engine.py` | 按平台生成可执行配置 |
| 修复应用服务 | `app/remediation/applier.py` | SSH 应用、备份、回滚 |
| 复测验证引擎 | `app/verification/diff_engine.py` | 对比修复前后扫描结果 |
| 交叉验证引擎 | `app/verification/cross_validator.py` | 多技术路线验证漏洞 |
| 插件注册表 | `app/plugins/registry.py` | 动态加载与生命周期管理 |
| Burp UI 组件 | `frontend/src/components/burp/` | 专业暗色主题组件 |
| 知识库 | `app/knowledge/signatures.py` | payload、签名、CVE 组件库 |

### 4.2 重构模块

| 模块 | 当前问题 | 重构目标 |
|---|---|---|
| `main.py` | 约 11k 行，路由/业务/数据混杂 | 仅保留 FastAPI 工厂与中间件注册 |
| `src_scanner.py` | 检测逻辑与常量耦合 | 迁移为插件，文件转为辅助库 |
| `app/plugins/__init__.py` | `Finding` 字段不够丰富 | 扩展为完整模型 |
| `generate_fixes()` | 修复代码分散、扩展性差 | 接入模板引擎 |
| `api/auto-fix` | 仅支持 nginx，缺少回滚 | 支持多平台、备份、回滚 |
| 前端 CSS/JS | 组件化程度低 | 按 Burp 风格组件化 |

---

## 五、风险评估与注意事项

### 5.1 主要风险

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| `main.py` 拆分过程中测试回归 | 现有 182 个测试失败 | 每次只迁移一个 router/service，保持测试并行运行 |
| Finding 模型变更导致历史数据不兼容 | 旧扫描记录无法读取 | 新模型保持对旧 JSON 的向后兼容读取 |
| SSH 自动修复误改生产配置 | 服务中断 | 必须先在非生产环境验证，所有写入先备份并支持回滚 |
| 扫描目标未授权 | 法律风险 | 强制 authorized=true，域名验证后才能深度扫描 |
| 插件化后性能下降 | 扫描耗时增加 | 插件并发执行，单个插件增加超时控制 |
| 修复模板生成错误配置 | 应用后反而降低安全性 | 模板内置风险说明，应用前强制人工确认 |

### 5.2 注意事项

1. **保持测试基线**：任何重构完成后，`pytest tests/` 必须仍通过。
2. **小步快跑**：不要试图在一个 PR 中完成 `main.py` 全量拆分，按 router 逐次迁移。
3. **凭证安全**：SSH 密码等凭证仅允许在内存中使用，禁止落入数据库或日志。
4. **扫描授权**：所有扫描行为必须可追溯到已登录用户，保留审计日志。
5. **性能预算**：标准扫描耗时控制在 5 秒以内，深度扫描控制在 30 秒以内。
6. **前端构建**：每次后端静态资源更新时，需要重新执行 `npm run build` 并将产物同步到 `static/`。
7. **数据保留**：扫描证据与审计日志需要设定保留策略，避免磁盘无限增长。

---

创建日期：2026-07-28
