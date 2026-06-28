# 交付包审计报告

## 审计时间
2026-06-28

## 审计结果
已确认最终交付包不包含以下敏感文件：

| 文件 | 状态 | 说明 |
|------|------|------|
| .jwt_secret | 不存在 | JWT 密钥由运行时环境变量生成 |
| *.db（scans.db、test.db）| 不存在 | 数据库由运行时创建 |
| .pytest_cache/ | 不存在 | 测试缓存已清理 |
| .coverage | 不存在 | 覆盖率数据已清理 |
| server.key / server.crt | 不存在 | 演示 HTTPS 自签名证书由运行时 `openssl` 自动生成，不随包携带 |
| logs/* | 不存在 | 日志已清理 |
| __pycache__/ | 不存在 | Python 缓存已清理 |
| *.pyc | 不存在 | 编译缓存已清理 |
| .env | 不存在 | 环境变量文件不包含在交付包 |
| config.ini | 不存在 | 配置由运行时生成 |

## 包含的文件
- 源代码（main.py）
- 前端资源（static/）
- 测试用例（tests/）
- 文档（README.md、REVIEW_GUIDE.md、CHANGELOG.md、ONE_LINER.md）
- 部署配置（Dockerfile、render.yaml、requirements.txt）
- 演示靶场配置模板（demo-target/）

## 敏感信息处理
- JWT 密钥：运行时通过环境变量 `JWT_SECRET` 注入，未硬编码
- API Key：用户 LLM API Key 仅存储在浏览器 localStorage，后端不持久化
- SMTP 凭证：运行时通过环境变量注入，不包含在代码中
- 演示靶场证书：首次启动/测试时由 `_ensure_demo_target_ready()` 调用 `openssl` 自动生成 localhost 自签名证书

## 测试状态
`python3 -m pytest tests/ -q` 结果：**186 passed, 3 skipped, 0 failed**
