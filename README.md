# 漏洞哨兵 (Vuln Sentinel)

[![Tests](https://img.shields.io/badge/tests-1199%20passed-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-66.88%25-brightgreen)](htmlcov/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Security](https://img.shields.io/badge/bandit-0%20high%2Fmedium-brightgreen)]()

> **让中小团队在 30 秒内知道自己网站的安全风险，并直接拿到能上线的修复配置。**

**在线体验**: https://vuln-sentinel-v11-s.onrender.com

---

## 我们解决什么问题

中小企业和独立开发者上线网站后，通常面临三个现实困境：

- **没有安全团队**：请不起专职安全工程师，安全测试长期处于空白。
- **工具门槛高**：OWASP ZAP、Nikto 等专业工具安装复杂、报告难读。
- **报告无法落地**：传统扫描工具只告诉你"有问题"，不会告诉你"怎么修"。

漏洞哨兵把完整的安全检测流程压缩成三步：**输入网址 → 查看风险 → 复制修复配置**。不需要安装软件，不需要安全背景，3 秒出结果。

---

## 谁适合使用

| 用户类型 | 典型场景 |
|---|---|
| **独立开发者 / 个人站长** | 产品上线前快速自检，避免基础安全配置疏漏 |
| **中小企业技术负责人** | 低成本满足等保 / 数据安全法的基础自查要求 |
| **乙方交付团队** | 给客户交付前做初筛，生成专业 PDF 报告 |
| **运维 / DevOps** | 批量监控多个站点安全状态，跟踪修复闭环 |

---

## 核心能力

| 能力 | 说明 |
|---|---|
| **OWASP Top 10 扫描** | 全 10 大类风险覆盖，15 个检测维度，多维交叉验证降低误报 |
| **智能评分** | 100 分制安全评分 + WAF 加权，风险等级一目了然 |
| **多平台修复配置** | 一键生成 Nginx / Apache / Express / Flask / Spring Boot / Cloudflare 配置 |
| **AI 安全顾问** | 基于扫描结果给出修复位置、上线风险、修复优先级 |
| **修复前后对比** | 重新扫描后自动对比差异，验证修复效果 |
| **PDF 报告** | 专业报告，含封面、总览、评分明细、证据链、修复建议 |
| **工单管理** | 高危问题自动建单，跟踪修复状态 |
| **资产监控** | 添加站点资产后定时巡检，状态变化自动告警 |
| **GDPR 合规** | 数据导出、账号删除、数据匿名化、保留策略自动清理 |
| **计费系统** | 套餐购买、积分管理、Stripe/支付宝/微信支付对接 |
| **团队协作** | 创建团队、成员管理、角色权限（admin/member/viewer）|
| **免费试用** | 无需注册即可扫描白名单站点，体验完整报告 |

---

## 实际扫描效果

| 目标 | 评分 | 风险等级 | 漏洞数 | WAF |
|---|---:|---|---:|---|
| https://www.baidu.com | **66** | 中风险 | 8 | baidu (bfe) |
| https://example.com | **61** | 中风险 | 8 | cloudflare |
| https://httpbin.org | **50** | 中风险 | 10 | 无 |
| https://www.iana.org | **89** | 低风险 | 4 | 无 |

---

## 定价

| 版本 | 价格 | 包含内容 |
|---|---:|---|
| **免费版** | ￥0 / 月 | 每月 5 次扫描、查看报告、公开站点试用 |
| **专业版** | ￥99 / 月 | 无限扫描、修复配置生成、PDF 导出、AI 顾问 |
| **团队版** | ￥499 / 月 | 多成员、资产监控、工单系统、批量扫描、优先支持 |
| **企业版** | 按需求报价 | 私有化部署、自定义检测规则、SLA、专属客户成功 |

---

## 快速启动

### 方式 A：Docker Compose（推荐生产环境）

```bash
# 开发环境
docker-compose up -d

# 生产环境（PostgreSQL + 安全加固）
docker-compose -f docker-compose.prod.yml up -d
```

### 方式 B：Docker 单容器

```bash
docker build -t vulnsentinel .
docker run -p 8000:8000 vulnsentinel
```

### 方式 C：本地启动

```bash
pip install -r requirements.txt --break-system-packages
python main.py
```

浏览器打开 http://localhost:8000

### 方式 D：一键脚本

```bash
# Linux / macOS
./start.sh

# macOS
./start.command

# Windows
start.bat
```

### 方式 E：Render 云部署

```bash
# render.yaml 已配置好
# 1. Fork 本仓库
# 2. 在 Render 创建 Web Service，连接你的 fork
# 3. Render 自动识别 render.yaml 并部署
```

---

## 使用流程

1. **注册账号** 或直接使用免费试用扫描白名单站点
2. 输入目标 URL（如 `https://example.com`），勾选授权确认
3. 查看扫描报告：评分、风险等级、漏洞证据、修复建议
4. 生成修复配置（Nginx / Apache / Node.js / Python / Java / Cloudflare）
5. 查看修复前后评分对比（预估效果）
6. 验证修复效果：重新扫描并输出差异
7. 导出 PDF 报告

---

## 项目结构

```
vuln-sentinel/
├── main.py                      # FastAPI 后端主程序（150+ API）
├── src_scanner.py               # SRC 级扫描引擎
├── models.py                    # Pydantic 数据模型
├── constants.py                 # 全局常量与安全配置
├── utils.py                     # 工具函数（SSRF 防护、DNS pinning）
├── alembic/                     # 数据库迁移
│   ├── env.py
│   └── versions/
│       └── 001_baseline.py      # 基线迁移（13 表、27 索引）
├── app/
│   ├── core/                    # 核心基础设施
│   │   ├── config.py            # 配置管理
│   │   ├── exceptions.py        # 统一异常处理
│   │   ├── response.py          # 统一响应格式
│   │   ├── security.py          # 安全工具
│   │   ├── security_headers.py  # CSP/安全头配置
│   │   ├── rate_limiter.py      # IP 限流器
│   │   ├── input_validation.py  # 输入校验
│   │   ├── sanitization.py      # 输出消毒
│   │   ├── compliance.py        # 合规校验
│   │   ├── resilience.py        # 弹性容错
│   │   ├── secrets_manager.py   # 密钥管理
│   │   └── logging.py           # 结构化日志
│   ├── routers/                 # 领域路由（从 main.py 拆分）
│   │   ├── auth.py              # 认证（注册/登录/邮箱验证/密码重置）
│   │   ├── user.py              # 用户信息与积分
│   │   ├── billing.py           # 计费套餐与支付
│   │   ├── gdpr.py              # 数据合规
│   │   ├── team.py              # 团队管理
│   │   └── admin.py             # 审计日志
│   ├── schemas/
│   │   └── responses.py         # Pydantic 响应模型（OpenAPI 文档）
│   ├── services/                # 业务服务层
│   │   ├── billing_service.py   # 套餐购买与支付订单
│   │   ├── credits_service.py   # 积分管理
│   │   ├── gdpr_service.py      # 数据导出/删除/匿名化
│   │   ├── data_retention.py    # 数据保留策略
│   │   ├── scan_service.py      # 扫描服务
│   │   ├── scan_queue.py        # 异步扫描队列
│   │   ├── email_service.py     # 邮件发送
│   │   ├── user_lifecycle.py    # 用户生命周期
│   │   ├── vuln_intel_service.py # 漏洞情报
│   │   ├── discovery_crawler.py # 资产发现
│   │   ├── fuzz_engine.py       # 模糊测试
│   │   └── cve_sources.py       # CVE 数据源
│   ├── repositories/            # 数据访问层
│   │   ├── scan_repository.py
│   │   └── ticket_repository.py
│   ├── db/
│   │   └── session.py           # SQLAlchemy 会话（SQLite/PostgreSQL）
│   ├── knowledge/               # 检测知识库
│   │   ├── components.py        # 组件指纹
│   │   ├── payloads.py          # Payload 库
│   │   └── signatures.py        # 漏洞签名
│   ├── verification/            # 交叉验证引擎
│   │   ├── cross_validator.py
│   │   └── diff_engine.py
│   ├── quality/                 # 质量控制
│   │   ├── fp_control.py        # 误报控制
│   │   ├── quality_assessment.py # 质量评估
│   │   └── feedback_loop.py     # 反馈闭环
│   ├── dedup/
│   │   └── finding_dedup.py     # 去重引擎
│   ├── remediation/
│   │   └── template_engine.py   # 修复模板引擎
│   ├── reporting/
│   │   ├── generator.py         # 报告生成
│   │   ├── templates.py         # 报告模板
│   │   └── models.py            # 报告数据模型
│   ├── plugins/                 # 插件系统
│   │   ├── builtin.py
│   │   ├── rule_engine.py
│   │   └── detectors/
│   ├── tasks/
│   │   └── manager.py           # 异步任务管理
│   ├── audit.py                 # 审计日志
│   ├── health.py                # 健康检查
│   ├── metrics.py               # 指标采集
│   ├── middleware.py            # 中间件
│   └── sarif.py                 # SARIF 输出
├── frontend/                    # 前端（Vite + 原生 JS）
│   ├── src/
│   │   ├── main.js              # 应用入口
│   │   ├── api.js               # API 封装
│   │   ├── store.js             # 状态管理
│   │   ├── utils.js             # 工具函数
│   │   ├── templates.js         # 模板
│   │   ├── style.css            # Burp Suite 暗色主题
│   │   ├── pages/               # 页面模块
│   │   │   ├── home.js
│   │   │   ├── scan.js
│   │   │   ├── result.js
│   │   │   ├── fixer.js
│   │   │   ├── tickets.js
│   │   │   ├── assets.js
│   │   │   ├── profile.js
│   │   │   ├── billing.js
│   │   │   └── evolution.js
│   │   ├── components/          # 可复用组件
│   │   └── services/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── tests/                       # pytest 测试套件（1199+ 用例）
│   ├── conftest.py              # 测试夹具
│   ├── test_main.py             # 主程序端点
│   ├── test_routers.py          # 路由模块
│   ├── test_services.py         # 服务层
│   ├── test_billing.py          # 计费
│   ├── test_gdpr.py             # GDPR
│   ├── test_credits.py          # 积分
│   ├── test_verification.py     # 验证引擎
│   ├── test_scan_services.py    # 扫描服务
│   ├── test_scan_probes.py      # 扫描探针
│   ├── test_scan_queue.py       # 扫描队列
│   ├── test_utils_core.py       # 工具函数
│   ├── test_main_endpoints.py   # 端点扩展
│   ├── test_main_extended.py    # 主程序扩展
│   ├── test_sanitization.py     # 消毒
│   ├── test_user_lifecycle.py   # 用户生命周期
│   ├── test_data_retention.py   # 数据保留
│   ├── test_api_versioning.py   # API 版本
│   ├── locustfile.py            # 性能测试
│   └── test_v11*.py             # 历史回归测试
├── scripts/                     # 运维脚本
│   ├── backup_db.py             # 数据库备份
│   ├── dependency_security_scan.py
│   └── security_baseline_check.py
├── docs/                        # 文档 + 截图 + 架构图
├── rules/                       # 自定义检测规则
├── .github/workflows/           # CI 配置
├── Dockerfile                   # Docker 镜像构建
├── docker-compose.yml           # 开发环境编排
├── docker-compose.prod.yml      # 生产环境编排（PostgreSQL）
├── alembic.ini                  # 数据库迁移配置
├── Makefile                     # 构建/测试/部署命令
├── pyproject.toml               # 项目配置
├── .pre-commit-config.yaml      # 预提交钩子
├── render.yaml                  # Render 部署配置
├── requirements.txt             # Python 依赖
├── pytest.ini                   # pytest 配置
├── start.sh / start.command / start.bat  # 一键启动脚本
└── README.md                    # 本文件
```

---

## 技术栈

| 层 | 技术 |
|---|---|
| 后端框架 | FastAPI + Pydantic |
| 数据库 | SQLite（开发）/ PostgreSQL（生产）+ SQLAlchemy |
| 数据库迁移 | Alembic（13 表、27 索引基线）|
| 扫描引擎 | SRC 级漏洞检测（SQLI / XSS / 信息泄露 / CSRF / 敏感路径 / 组件漏洞）|
| 认证 | JWT (PyJWT) + bcrypt |
| 前端 | Vite + 原生 JS + 模块化组件（前后端分离）|
| PDF 报告 | reportlab |
| 定时任务 | apscheduler |
| 安全扫描 | bandit（CI 集成）|
| 代码检查 | ruff |
| 测试框架 | pytest + pytest-cov |
| 部署 | Docker / Docker Compose / Render / 本地 Python |

---

## 安全特性

| 特性 | 说明 |
|---|---|
| **SSRF 防护** | URL 白名单校验 + DNS pinning，防止 DNS 重绑定攻击 |
| **CSP 加固** | object-src 'none'、base-uri 'self'、form-action 'self' |
| **限流** | 注册/登录/密码重置端点 IP 限流，防止暴力破解 |
| **SQL 注入防护** | 参数化查询 + 表名白名单校验 |
| **TrustedHost** | 生产环境强制 Host 头校验 |
| **输入消毒** | 全链路输入校验与输出消毒 |
| **密钥管理** | 凭证加密密钥可配置，生产环境 JWT Secret 强制校验 |
| **审计日志** | 关键操作审计记录，管理员可查询 |
| **GDPR 合规** | 数据导出、账号删除、数据匿名化、保留策略自动清理 |

---

## API 端点

### 认证（`app/routers/auth.py`）

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/register` | POST | 用户注册 |
| `/api/login` | POST | 用户登录 |
| `/api/auth/verify-email` | POST | 邮箱验证 |
| `/api/auth/resend-verification` | POST | 重发验证邮件 |
| `/api/auth/password-reset/request` | POST | 密码重置请求 |
| `/api/auth/password-reset/confirm` | POST | 密码重置确认 |

### 用户（`app/routers/user.py`）

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/me` | GET | 当前用户信息 |
| `/api/me/credits` | GET | 积分余额 |
| `/api/usage` | GET | 积分使用日志 |

### 计费（`app/routers/billing.py`）

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/billing/plans` | GET | 套餐列表 |
| `/api/billing/purchase` | POST | 购买套餐 |
| `/api/billing/recharges` | GET | 充值记录 |
| `/api/billing/order` | POST | 创建支付订单 |
| `/api/billing/order/{id}` | GET | 查询订单状态 |
| `/api/billing/webhook/{provider}` | POST | 支付回调（Stripe/支付宝/微信）|
| `/api/admin/recharge` | POST | 管理员充值 |

### GDPR 合规（`app/routers/gdpr.py`）

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/me/export` | GET | 导出个人数据 |
| `/api/me/account` | DELETE | 删除账号 |
| `/api/me/anonymize` | POST | 匿名化数据 |
| `/api/admin/data-retention/run` | POST | 触发保留策略清理 |

### 团队（`app/routers/team.py`）

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/team` | GET | 团队成员列表 |
| `/api/team/create` | POST | 创建团队 |
| `/api/team/join` | POST | 加入团队 |
| `/api/team/{id}/role` | POST | 修改成员角色 |

### 管理员（`app/routers/admin.py`）

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/admin/audit-logs` | GET | 审计日志查询 |

### 扫描与报告（`main.py`）

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/scan` | POST | 执行安全扫描 |
| `/api/history` | GET | 扫描历史 |
| `/api/dashboard` | GET | 用户统计 |
| `/api/fix` | POST | 生成修复配置 |
| `/api/ai-advisor` | POST | AI 安全顾问 |
| `/api/report/{id}` | GET | 下载 PDF 报告 |
| `/api/share/{id}` | GET | 公开分享结果 |
| `/api/batch-scan` | POST | 批量扫描（最多 5 URL）|
| `/api/compare` | POST | 两次扫描对比 |
| `/api/public-demo-scan` | POST | 免费试用扫描 |
| `/api/health` | GET | 健康检查 |

完整 OpenAPI 文档：访问 `/docs` (Swagger UI)

---

## 测试

```bash
# 运行全部测试
python -m pytest tests/ -v

# 运行测试并生成覆盖率报告
python -m pytest --cov=. --cov-report=html

# 代码检查
ruff check .

# 安全扫描
bandit -r . -q --exclude './tests,./.venv,./htmlcov,./alembic'
```

当前测试结果：**1199 passed, 1 failed, 6 skipped**

| 指标 | 数值 |
|---|---|
| 测试用例总数 | 1206 |
| 通过 | 1199 |
| 覆盖率 | 66.88% |
| Ruff 检查 | 0 errors |
| Bandit 安全扫描 | 0 medium / 0 high |

---

## 内网目标扫描

```bash
ALLOWED_INTERNAL_HOSTS="192.168.1.100,10.0.0.5,pikachu.local" python main.py
```

---

## 数据库迁移

```bash
# 生成新迁移
alembic revision --autogenerate -m "描述变更"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---

## 功能边界

| 功能 | 状态 | 说明 |
|---|---|---|
| 安全扫描（HTTP响应头/SSL/敏感路径） | 已实现 | 真实 HTTP 请求，结果入库 |
| 修复建议生成（6种平台） | 已实现 | 基于 findings 真实计算 |
| 修复前后对比（模拟评分） | 已实现 | 预估效果，非真实修改目标站 |
| 验证修复（重新扫描） | 已实现 | 真实重新扫描并对比差异 |
| PDF/HTML 报告导出 | 已实现 | reportlab 真实生成 |
| 历史记录 & 分享 | 已实现 | SQLite/PostgreSQL 持久化 |
| 批量扫描 | 已实现 | 最多 5 URL 并发 |
| 工单系统 | 已实现 | 完整 CRUD |
| 资产 & 监控 | 已实现 | 定时扫描 + 告警 |
| GDPR 合规 | 已实现 | 数据导出/删除/匿名化/保留策略 |
| 计费系统 | 已实现 | 套餐购买 + Stripe/支付宝/微信对接 |
| 团队协作 | 已实现 | 团队创建/加入/角色管理 |
| 积分系统 | 已实现 | 积分扣减/充值/使用日志 |
| 审计日志 | 已实现 | 关键操作记录与管理员查询 |
| AI 安全顾问 | 规则引擎 | 配置 LLM API Key 后接入真实大模型 |
| SSH 应用修复配置 | 可选 | 需安装 paramiko，配置服务器凭证 |
| 免费试用扫描 | 已实现 | 白名单站点无需注册 |

---

## 架构

![架构图](docs/architecture.svg)

---

## 贡献

欢迎提交 Issue 和 PR！

开发流程：

```bash
# 安装开发依赖
pip install -r requirements.txt --break-system-packages
pip install ruff bandit pytest pytest-cov --break-system-packages

# 提交前检查
ruff check . && bandit -r . -q --exclude './tests,./.venv,./htmlcov,./alembic' -ll && pytest --tb=short -q
```

---

## 许可证

MIT License

---

## 版本

**12.0** · 2026-08-05

### 主要更新

**安全加固**
- 修复 SSRF DNS 重绑定漏洞，增加 IP 验证与 DNS pinning
- 修复认证缺口，加强 CSP 配置
- 密码重置端点限流，SQL 表名白名单校验
- 生产环境 TrustedHostMiddleware 保护

**架构升级**
- 单体 main.py 拆分为 6 个领域路由模块
- 新增 Alembic 数据库迁移（13 表、27 索引基线）
- PostgreSQL/SQLAlchemy 连接池支持
- 统一异常处理与响应格式

**新增服务**
- 计费系统（套餐购买、支付订单、Stripe/支付宝/微信回调）
- GDPR 合规（数据导出、账号删除、数据匿名化、保留策略）
- 积分管理、审计日志、团队协作
- 异步扫描队列、漏洞情报聚合、资产发现爬虫、模糊测试引擎

**质量保障**
- 测试覆盖率从 16% 提升至 66.88%（1199+ 测试用例）
- 全端点 Pydantic response_model，OpenAPI 文档完整
- Ruff 代码检查 0 errors，Bandit 安全扫描 0 medium/high

---

## 联系方式

- GitHub: https://github.com/tomjoy248-crypto/vuln-sentinel
- 在线环境: https://vuln-sentinel-v11-s.onrender.com
