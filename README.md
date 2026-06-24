# 漏洞哨兵 V11.4

[![Coverage](docs/coverage-badge.svg)](docs/coverage_html/)
[![Tests](https://img.shields.io/badge/tests-84%20passed-brightgreen)](tests/)

> AI 驱动的 Web 安全配置扫描与修复建议平台

## 产品截图

| 首页 | 扫描报告 | 修复建议 | 修复前后对比 |
|:---:|:---:|:---:|:---:|
| ![首页](docs/screenshots/finals/01-home.png) | ![报告](docs/screenshots/finals/03-findings-detail.png) | ![修复](docs/screenshots/finals/04-findings-and-fix.png) | ![对比](docs/screenshots/finals/08-fix-compare.png) |

> 截图说明：首页展示产品定位；扫描报告展示 7 项漏洞详情+OWASP 分类；修复建议展示 8 种平台配置代码；修复前后对比展示 Diff 高亮+一键复制。

## 核心能力

- 真实扫描：HTTP 响应头、SSL 证书、敏感路径、Cookie 安全、CORS
- 风险评分：100 分制 + 5 维度雷达图（OWASP Top 10）
- 修复建议：6 种部署环境（Nginx/Apache/Express/Flask/Spring Boot/Cloudflare）
- 攻击模拟：CSRF / XSS / 点击劫持 一键演示
- AI 顾问：读取当前扫描结果，给出修复计划 + 配置位置 + 上线风险
- PDF 报告：封面 + 风险总览 + 评分明细 + 证据列 + 修复建议
- 多层防护：SSRF / 域名归属验证 / 授权确认 / 深度扫描门槛

## 快速启动

### 方式 A：一键启动

```bash
./start.command
```

### 方式 B：手动启动

```bash
pip3 install -r requirements.txt --break-system-packages
python3 main.py
```

浏览器打开 http://localhost:8000

### 方式 C：离线演示（免后端）

双击 `static/index.html`，账号 `demo / demo123`

## 测试账号

| 用户名 | 密码 |
|---|---|
| demo | demo123 |

## 部署

```bash
docker build -t vulnsentinel:v11.4 .
docker run -p 8000:8000 vulnsentinel:v11.4
```

## 内网靶场扫描

```bash
ALLOWED_INTERNAL_HOSTS="192.168.1.100,10.0.0.5,pikachu.local" python3 main.py
```

## 测试

```bash
python3 -m pytest tests/ -v
```

## 架构

- 后端：FastAPI + SQLite + httpx + dnspython
- 前端：单文件 HTML（无框架依赖，离线可用）
- 认证：JWT + bcrypt
- 报告：reportlab
- 定时：apscheduler

## 架构

![架构图](docs/architecture.svg)

## 版本

v11.4 · 2026-06-22
