# 漏洞哨兵 (Vuln Sentinel)

[![Tests](https://img.shields.io/badge/tests-800%2B%20passed-brightgreen)](tests/)
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
| **智能评分** | 100 分制安全评分 + WAF 加权，四级风险等级（严重/高风险/中风险/低风险）|
| **多平台修复配置** | 一键生成 Nginx / Apache / Express / Flask / Spring Boot / Cloudflare 配置 |
| **AI 安全顾问** | 基于扫描结果给出修复位置、上线风险、修复优先级 |
| **修复前后对比** | 重新扫描后自动对比差异，验证修复效果 |
| **PDF 报告** | 专业报告，含封面、总览、评分明细、证据链、修复建议 |
| **工单管理** | 高危问题自动建单，跟踪修复状态 |
| **资产监控** | 添加站点资产后定时巡检，状态变化自动告警 |
| **GDPR 合规** | 数据导出、账号删除、数据匿名化、保留策略自动清理 |
| **计费系统** | 套餐购买、积分管理、Stripe 真实收款、支付宝/微信支付骨架（待接入 SDK）|
| **团队协作** | 创建团队、成员管理、角色权限（admin/member/viewer）|
| **免费试用** | 无需注册即可扫描白名单站点，体验完整报告 |

---

## 实际扫描效果

> 以下为 2026-08-05 端到端测试实际扫描结果（评分随目标站点配置变化可能波动）：

| 目标 | 评分 | 风险等级 | 漏洞数 | WAF |
|---|---:|---|---:|---|
| https://httpbin.org | **64** | 中风险 | 7 | 无 |
| https://example.com | **67** | 中风险 | 6 | cloudflare |

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
├── main.py              # FastAPI 后端主程序
├── src_scanner.py       # SRC 级扫描引擎
├── constants.py         # 全局常量与安全配置
├── app/                 # 模块化后端（routers/services/core/db/plugins）
├── frontend/            # 前端（Vite + 原生 JS）
├── tests/               # pytest 测试套件
├── alembic/             # 数据库迁移
├── scripts/             # 运维脚本
├── docs/                # 文档与截图
├── Dockerfile           # Docker 镜像构建
├── docker-compose.yml   # 开发环境编排
└── docker-compose.prod.yml  # 生产环境编排（PostgreSQL）
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

完整 OpenAPI 文档：启动服务后访问 `/docs` (Swagger UI)

主要端点分类：认证、用户、扫描、修复、报告、计费、GDPR、团队、管理员。

---

## 测试

```bash
# 运行全部单元测试
python -m pytest tests/ -v

# 运行测试并生成覆盖率报告
python -m pytest --cov=. --cov-report=html

# 端到端扫描功能测试（需先启动后端服务）
python main.py &
python scripts/e2e_scan_test.py --host localhost --port 8000

# 代码检查
ruff check .

# 安全扫描
bandit -r . -q --exclude './tests,./.venv,./htmlcov,./alembic'
```

当前测试结果（2026-08-05 本地运行）：

| 指标 | 数值 |
|---|---|
| 测试用例总数 | 1200+ |
| 端到端扫描测试 | 13/13 全部通过 |
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

**11-S** · 2026-08-05

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
- 计费系统（套餐购买、支付订单、Stripe 真实收款、支付宝/微信支付骨架）
- GDPR 合规（数据导出、账号删除、数据匿名化、保留策略）
- 积分管理、审计日志、团队协作
- 异步扫描队列、漏洞情报聚合、资产发现爬虫、模糊测试引擎

**质量保障**
- 测试套件 1206 用例，800+ 通过，端到端扫描测试 13/13 全部通过
- 全端点 Pydantic response_model，OpenAPI 文档完整
- Ruff 代码检查 0 errors，Bandit 安全扫描 0 medium/high

---

## 联系方式

- GitHub: https://github.com/tomjoy248-crypto/vuln-sentinel
- 在线环境: https://vuln-sentinel-v11-s.onrender.com
