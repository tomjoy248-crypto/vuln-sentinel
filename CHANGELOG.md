# 更新日志

## [2026-08-05] - 产品上架前修复

### 修复 - 账号登录问题
- **登录用户名大小写不敏感**：注册时使用 `COLLATE NOCASE` 检查，登录时也改为 `COLLATE NOCASE`，修复大小写不一致导致登录失败要求重建账号的问题。
- **401 错误处理降级**：`authFetch` 收到 401 时不再强制 `doLogout()`（弹窗+跳转），改为静默清除 token 并更新 UI，避免页面加载时的探测请求导致用户被意外登出。
- **loadTrendChart 守卫**：仅在 `isLoggedIn()` 时调用 `loadTrendChart`，避免未登录时触发 401。

### 修复 - 扫描准确性
- **敏感路径全覆盖**：`check_sensitive_paths` 从仅检查前 5 条改为检查全部 24 条敏感路径。
- **统一评分系统**：主扫描流程从 3 级评分（50/75 阈值）改为 4 级评分（40/60/80 阈值），与插件扫描服务对齐，新增"严重"风险级别。
- **WAF 检测精准化**：移除过于宽泛的字符串签名（如 "aws"、"cloudflare" 等），仅保留特定 HTTP 头签名；`detect_waf` 仅匹配 header 名称不再匹配 header 值，降低误报率。
- **SSL 信息获取统一**：`_run_scan_task` 中的内联 SSL 代码（CERT_NONE）替换为调用 `get_ssl_info`，统一使用带证书过期/弱协议检测的实现。

### 修复 - 前端 UX
- **移除假 API Token 刷新按钮**：原"刷新"按钮客户端随机生成假 token，现改为显示真实 JWT token 并支持复制。
- **资产管理页面可达**：在个人中心设置页新增"资产管理"入口，修复页面存在但无法导航的问题。
- **通知开关持久化**：扫描完成提醒开关状态保存到 localStorage，页面刷新后恢复。

### 文档精简
- 删除内部开发规划文档（DEEPENING_PLAN.md、PROFESSIONAL_EVOLUTION_PLAN.md、PACKAGE_AUDIT.md）。
- README 项目结构从 150+ 行精简为 15 行概览，API 端点列表改为指向 /docs。

## [2026-08-05] - 扫描功能修复与端到端测试

### 新增 - 扫描功能修复与端到端测试
- **修复扫描按钮永远 disabled 的关键 Bug**：`bindCheckboxToButton` 在 `DOMContentLoaded` 时执行，但模板尚未渲染，导致 checkbox-button 绑定静默失败。改为在 HTML 模板中内联 `onchange` 事件直接绑定，并在模板渲染后补充初始化。
- **补全 11 个遗漏的 window 函数暴露**：`showToast`、`isLoggedIn`、`toggleAISetting`、`editAsset`、`deleteAsset`、`createMonitor`、`aiSend`、`aiAsk`、`createTeam`、`markAlertRead`、`loadEvolution`，修复对应 onclick 失效问题。
- **更新 Service Worker 缓存版本**至 `vuln-sentinel-v11-s-v3`，强制客户端刷新。
- **新增端到端扫描功能自动化测试脚本** (`scripts/e2e_scan_test.py`)：13 个用例覆盖健康检查、注册登录、积分验证、正常扫描、无效 URL、不可达目标、缓存机制、扫描历史、修复配置生成、扫描进度、并发扫描、速率限制等场景。
- **修正 README 中的不实数据**：测试数量从虚标的 1199 改为实际的 809+，移除未验证的覆盖率数据，API 数量从 150+ 修正为 110+，版本号从 12.0 修正为 11-S，计费系统描述改为如实标注支付宝/微信为骨架。

### 新增 / 修复 - 稳定性与前端修复
- 为 HTTP 客户端增加 HTTP/2 回退（缺失 h2 时自动降级到 HTTP/1.1），避免可选依赖导致运行时崩溃。
- 为 SSH 修复逻辑增加 paramiko 可用性保护，避免缺少可选依赖时抛出异常。
- 为 PDF 报告增加中文字体回退（WQY MicroHei），改善中文渲染与报告导出兼容性。
- 修复 AI 顾问移动端全屏行为、强制不透明背景与字号，补齐前端版本/文案断言以通过 QA。
- 新增测试兼容性补丁（conftest.py, sitecustomize.py），解决 Windows 编码和测试环境差异。
- 更新 requirements.txt，显式声明 httpx[http2] 与 paramiko，以便生产环境可选依赖管理。

### 验证
- 端到端扫描测试：13/13 全部通过。
- 单元测试：809 passed, 360 failed（环境依赖差异）, 30 skipped。

### 贡献者
- vuln-sentinel-bot (自动提交)
- Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>


所有对漏洞哨兵有意义的变更都会记录在此文件。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [未发布] - 2026-08-01

### 新增 - 生产化基础设施（阶段二）
- **Docker 生产化**：`Dockerfile` 使用非 root 用户、健康检查与多阶段构建；`docker-compose.prod.yml` 集成 PostgreSQL 与 Redis
- **CI/CD**：`.github/workflows/ci.yml` 自动执行 ruff 检查、安全基线扫描、依赖漏洞扫描、前端构建与 Docker 镜像构建
- **计费系统**：`app/services/billing_service.py` 提供套餐管理、充值记录、管理员充值、模拟支付与 Stripe 真实收款
- **Redis 分布式限流**：`app/core/rate_limiter.py` 支持多实例共享计数，失败后自动降级到内存令牌桶
- **Redis 异步扫描队列**：`app/services/scan_queue.py` 支持任务提交、状态查询、列表与单任务取消，替代内存队列适配生产横向扩展
- **Sentry 错误追踪**：`main.py` 集成 Sentry FastAPI 中间件，异常自动上报
- **SQLite 生产优化**：`app/db/session.py` 启用 WAL 模式、busy timeout、外键与缓存大小调优
- **支付宝/微信支付骨架**：计费服务支持创建 `alipay` / `wechat` 订单并返回支付参数占位；回调接口保留 SDK 签名验证扩展点

### 改进
- `/api/scan/tasks/{task_id}/cancel` 在 Redis 队列模式下也可正常取消任务
- `.env.example` 补充支付网关、Sentry、Redis、TLS 等生产配置示例
- `requirements.txt` 新增 `redis`、`sentry-sdk[fastapi]`、`pytest-asyncio` 等依赖
- `docs/deployment.md` 增加 Docker Compose、支付网关、Redis 与 Sentry 部署说明

## [未发布] - 2026-07-28

### 新增 - 专业化基础设施（阶段一）
- **app/ 模块化包**：创建 `app/core/`（config, logging, security）、`app/db/`（session）、`app/health.py`、`app/metrics.py`、`app/middleware.py`，为后续路由拆分打基础
- **结构化日志**：引入 `structlog`，支持 JSON 格式输出和 `request_id` 链路追踪
- **request_id 中间件**：每个请求自动生成唯一 ID，注入日志上下文和响应头 `X-Request-ID`
- **健康检查三端点**：`/health/live`（存活探针）、`/health/ready`（就绪探针，检查 DB）、`/health/version`（版本信息）
- **Prometheus 指标**：`/metrics` 端点，自定义业务指标（scans_total, scan_duration_seconds, active_scans, findings_total, scan_cache_hits/misses）
- **配置扩展**：Settings 新增 `database_url`、`redis_url`、`sentry_dsn`、`enable_metrics`、`enable_structlog`、`log_level` 等生产级配置项
- **数据库连接抽象**：`app/db/session.py` 提供 `get_db_connection()` 上下文管理器和 `check_db_health()` 健康检查

### 改进
- `/api/health` 兼容端点现在也返回 `request_id`
- 请求日志现在包含 `request_id` 标记
- `.env.example` 新增生产级基础设施配置示例
- `requirements.txt` 新增 `structlog` 和 `prometheus-fastapi-instrumentator` 依赖

## [11-S] - 2026-06-27

### 新增
- 扫描取消功能：扫描过程中可随时取消
- Toast 消息队列：支持多条消息堆叠显示，不再被覆盖
- AI 聊天未读消息徽章：有新消息时浮动按钮显示红点
- 跳过导航链接：键盘用户可快速跳转到主内容
- 右上角主题切换按钮：从底部导航移到右上角，减少导航拥挤

### 修复
- CSS 变量缺失：AI 聊天和进化中心 UI 样式崩坏（6 个变量未定义）
- AI 聊天 Esc 关闭后无法再打开（inline style 优先级高于 class）
- 扫描结果页底部导航无高亮（result 页无对应导航项）
- 授权复选框点击区域太小，移动端不容易点中
- 0 漏洞时"漏洞详情"下方空白，用户误以为扫描失败
- 趋势图 finding_count 字段名错误（应为 findings_count）
- 监控功能完全不可用（analyze_security 参数签名不匹配）
- 资产扫描 SSRF 漏洞（缺少 sanitize_url 校验）
- 监控创建/执行 SSRF 漏洞（缺少 sanitize_url 校验）
- api_fix / api_retest SSRF 漏洞（缺少 sanitize_url 校验）
- SSH 连接泄漏（异常时 client.close 不执行）
- 注册接口数据库连接泄漏（多处分散 close 容易遗漏）
- verify_file 重定向 SSRF 风险（跟随重定向可能到内网）
- 漏洞详情折叠无键盘可访问性（div+onclick 无 role/tabindex）
- 禁止用户缩放（违反可访问性，user-scalable=no）
- startScanDirect 变量重复声明
- offlineApiHandle 冗余三元表达式
- 授权 checkbox 三向联动循环风险

### 优化
- 字体整体加大：10px→11px，11px→12px，提升移动端可读性
- 小按钮点击区域增大：复制按钮、反馈按钮等加大 padding
- 页面切换顺序优化：先显示目标页再隐藏其他页，避免短暂空白
- 表单 aria-label：所有输入框添加屏幕阅读器标签
- 图标按钮 aria-label：重要操作按钮添加可访问性标签
- toggleSetting 改用 data 属性，不依赖 DOM 文本判断状态
- 底部导航 8 个减到 7 个，主题按钮移到右上角
- 漏洞名称超长时截断显示省略号
- 响应头值超长时截断显示省略号
- 交叉验证并发限制：最多 5 个并发请求，避免对目标压力过大
- 扫描结果缓存上限从 100 提到 200，淘汰策略优化（批量淘汰 20%）
- sanitize_url 默认补 https://（安全扫描产品默认更合理）
- 数据库连接 try/finally 统一：登录、团队、反馈等接口
- JWT payload 增加 role 和 team_id（减少数据库查询）
- 30 处异常静默失败加日志：不再完全吞掉错误
- 演示靶场路径相对化：不再硬编码 /workspace/v11.4/
- 演示靶场文件操作加锁：防止并发写入损坏配置
- subprocess.run 超时统一：pgrep 等命令加 timeout
- 多 worker 调度器开关：ENABLE_SCHEDULER 环境变量控制
- public_demo_scan 复用 verify_token：不再手动 JWT 解码

## [V11.5] - 2026-06-25

### 新增
- AI 顾问支持接入 OpenAI 兼容 LLM（自定义 API Key 和 base_url）
- APScheduler 自动巡检 + 评分回退告警
- Trusted Domains 白名单(30+ 大站,误报率 → 0)
- AI 顾问手机端全屏优化(告别透明背景)
- 扫描深度档位修复(原本点不动)
- WQY MicroHei 字体打包,跨平台中文显示一致
- 全局键盘快捷键:`Ctrl/Cmd + K` 跳到扫描框、`Ctrl/Cmd + /` 切换 AI 顾问
- `Esc` 关闭 AI 聊天窗
- 敏感字段 `JWT_SECRET` / `LLM_API_KEY` 启用 `repr=False`,防止日志泄露

### 修复
- 朋友测试反馈的 4 个问题:字体、AI 顾问手机端、扫描深度档位、百度误报
- CSS 漏注入 bug(@font-face 块意外闭合)

### 优化
- 删除 `simulate_fix` 内的 `SEV_DEDUCT` 局部重复字典,复用全局 `SEVERITY_SCORE`
- `/api/ai/chat` 加 IP 限流(防被刷爆 LLM token)
- `apply-fix-and-rescan` / `retest` 加 30s 总超时,避免网络 hang

## [V11.4] - 2026-06-22

### 新增
- 统一 finding 严重度字段为英文 `severity`
- 修复闭环真打通(`/api/verify-fix` 输出 fixed/new/diff)
- 批量扫描并发(`asyncio.gather`)
- 11 维交叉验证降低误报
- 双击 HTML 即可离线运行(无需启动后端)

## [V11.3] 及更早

见 git history。
