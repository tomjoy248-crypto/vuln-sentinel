# 评委评审指南

## 项目概述
漏洞哨兵是面向中小企业的 AI Web 安全扫描与修复建议平台。
通过自动化扫描发现安全配置问题，生成多平台修复配置，并提供复测验证闭环。

## 一分钟体验路径

### 步骤 1：登录
- 账号：demo / demo123
- 在线地址：https://vuln-sentinel-v11.onrender.com

### 步骤 2：扫描目标
- 输入 https://example.com（或选择快速演示）
- 点击"开始安全扫描"
- 等待 3-5 秒出结果

### 步骤 3：查看漏洞
- 查看安全评分和风险等级
- 展开漏洞详情，查看修复建议和验证步骤

### 步骤 4：生成修复配置
- 点击"一键应用修复"查看修复前后评分对比
- 切换平台（Nginx / Apache / Node.js 等）查看对应配置

### 步骤 5：验证修复
- 点击"验证修复效果"重新扫描
- 对比修复前后评分变化

### 步骤 6：导出报告
- 点击"下载PDF报告"获取完整安全报告

## 核心能力

### 已实现（真实运行）
| 能力 | 说明 |
|------|------|
| 安全响应头扫描 | HSTS、CSP、X-Frame-Options 等 15 个检测维度 |
| SSL/TLS 证书检查 | 证书有效期、协议版本、密码套件 |
| 敏感路径检测 | .env、.git、/admin 等常见敏感路径 |
| Cookie/CORS 检测 | HttpOnly、Secure、SameSite、CORS 配置 |
| 域名归属验证 | DNS TXT / HTTP 文件验证 |
| 修复配置生成 | Nginx / Apache / Node.js / Python / Java / Cloudflare |
| 修复后复测 | 真实重新扫描并对比修复前后差异 |
| PDF 报告导出 | 7 页专业安全报告 |
| 代码层漏洞检测 | SQL 注入 / XSS / 命令注入 / 目录遍历 fuzzing |
| AI 安全顾问 | 支持接入 OpenAI / DeepSeek / 通义千问 |
| 告警通知 | 邮件 SMTP + 钉钉 / 企业微信 / 飞书 Webhook |

### 演示模式（需要外部配置）
| 能力 | 说明 |
|------|------|
| GitHub PR 自动提交 | 需配置 GitHub Token |
| 远程服务器自动写入配置 | 需配置 SSH 凭证 |
| AI 大模型对话 | 需配置 LLM API Key |

## 测试方式
```bash
pip install -r requirements.txt
python -m pytest tests/ -q
```

## 安全边界
- 不进行攻击利用：只检测配置和探测性请求，不执行破坏性操作
- 不扫描未授权站点：扫描前必须勾选授权确认
- 深度扫描需域名验证：通过 DNS TXT 或 HTTP 文件验证域名归属
- SSRF 防护：所有外部请求入口统一拦截内网地址
- API Key 不持久化：用户的 LLM API Key 仅保存在浏览器本地

## 技术架构
| 层 | 技术 |
|---|---|
| 后端 | FastAPI + SQLite + httpx |
| 前端 | 原生 HTML + CSS + JS（无框架，可离线运行）|
| 认证 | JWT + bcrypt |
| 代码检测 | 异步 fuzzing（SQLi / XSS / CMDi / 目录遍历）|
| 报告 | reportlab PDF 生成 |
| 部署 | Docker / Render / 本地 Python |
