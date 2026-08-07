# 漏洞哨兵 11-S 生产部署指南

本文档介绍如何将漏洞哨兵 11-S 部署到生产环境，包括 Docker Compose、支付网关配置与 CI/CD 说明。

## 前置条件

- Docker & Docker Compose
- 一个已解析到服务器的域名（用于 HTTPS 与支付回调）
- （可选）Stripe 账号，用于真实收款

## 1. 环境配置

复制示例配置并填写真实值：

```bash
cp .env.example .env
```

关键必填项：

| 变量 | 说明 |
|------|------|
| `JWT_SECRET` | 至少 32 位随机字符串 |
| `ALLOWED_ORIGINS` | 前端域名，如 `https://your-domain.com` |
| `PUBLIC_BASE_URL` | 服务对外地址，用于支付回调 |
| `DATABASE_URL` | 生产建议 PostgreSQL，默认 SQLite |
| `REDIS_URL` | 生产建议启用 Redis |

## 2. Docker Compose 生产部署

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

启动后访问 `http://your-domain:8000`。生产环境建议在容器前部署 Nginx / Traefik 并配置 HTTPS。

## 3. Redis（分布式限流与异步扫描队列）

生产环境建议启用 Redis：

```bash
REDIS_URL=redis://redis:6379/0
```

启用后：
- API 限流中间件会自动切换为 Redis 固定窗口限流，多实例共享计数。
- `/api/scan/async` 异步扫描任务会进入 Redis 队列，由后台 worker 消费。
- 任务结果保留 24 小时，可通过 `/api/scan/tasks/{task_id}` 跨实例查询。
- 支持 `POST /api/scan/tasks/{task_id}/cancel` 取消 pending / running 状态的任务。

## 4. 支付网关配置

### 4.1 Stripe（推荐海外收款）

1. 在 Stripe Dashboard 获取密钥。
2. 在 `.env` 中配置：
   ```
   STRIPE_PUBLISHABLE_KEY=pk_live_xxx
   STRIPE_SECRET_KEY=sk_live_xxx
   STRIPE_WEBHOOK_SECRET=whsec_xxx
   ```
3. 在 Stripe Dashboard 创建 Webhook Endpoint：
   - URL: `https://your-domain.com/api/billing/webhook/stripe`
   - 事件: `checkout.session.completed`
4. 前端在 `window.__STRIPE_PUBLISHABLE_KEY__` 暴露公钥后，购买按钮将自动跳转 Stripe Checkout。

### 4.2 支付宝 / 微信支付

当前已支持创建订单骨架：
- 支付宝：`POST /api/billing/order`（provider=`alipay`）
- 微信：`POST /api/billing/order`（provider=`wechat`）

未配置真实商户参数时，生产环境仅返回 `pending` 订单与空的 `pay_params`，前端不会自动走测试通道；本地联调可使用本地测试模式，生产环境不应开启任何 mock 充值回调。

异步通知回调接口：
- 支付宝：`POST /api/billing/webhook/alipay`
- 微信：`POST /api/billing/webhook/wechat`

接入真实支付时需安装对应 SDK（如 `alipay-sdk-python`、`wechatpayv3`），并在 `app/services/billing_service.py` 中替换签名验证逻辑。
生产环境请确保 `ALIPAY_MOCK`、`WECHAT_MOCK` 和 `MOCK_WEBHOOK_SECRET` 均未启用。

## 5. Sentry 错误追踪（可选）

配置 Sentry DSN 后，FastAPI 异常会自动上报：

```bash
SENTRY_DSN=https://xxx@yyy.ingest.sentry.io/zzz
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

## 6. CI/CD

项目已包含 `.github/workflows/ci.yml`，每次 push / PR 会自动执行：
- Python 质量检查（ruff）
- 安全基线检查
- 依赖漏洞扫描
- 前端构建
- Docker 镜像构建

## 7. 运维命令

```bash
# 查看日志
docker compose -f docker-compose.prod.yml logs -f vuln-sentinel

# 备份数据（PostgreSQL）
docker exec vuln-sentinel-postgres pg_dump -U vulnuser vuln_sentinel > backup.sql

# 更新部署
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## 8. 安全建议

- 不要将 `.env` 提交到版本库（已加入 `.gitignore`）。
- 生产环境必须设置 `JWT_SECRET`、`ALLOWED_ORIGINS`。
- 保持 `TLS_VERIFY=1`，防止中间人攻击。
- 定期运行 `make security-check` 检查依赖漏洞。
