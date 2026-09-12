# 外部验收闭环

以下项目不能仅由 CI 伪造完成，必须注入真实资源后执行：

1. WAF/CDN、软 404、强登录态：设置 `TARGET_BASE_URL`，仅对明确授权目标做回归。
2. 全站/深度 XSS、SQLi、业务逻辑：设置扫描范围、授权窗口和测试账号，默认仍是有限覆盖。
3. Windows、Redis、双账号：提供 Windows runner/电脑、`REDIS_URL`、`TEST_ACCOUNT_A/B`。
4. 支付签名：提供真实供应商 webhook 测试凭据和 `PAYMENT_WEBHOOK_SECRET`；禁止生产 mock。
5. Vault/AWS：提供 `VAULT_ADDR` 或 `AWS_REGION` 及最小权限身份，禁止把令牌写入仓库。
6. LLM：提供 `LLM_BASE_URL`、`LLM_API_KEY` 和模型名称，验收响应质量与限流。
7. Windows 签名：提供 `WINDOWS_CERTIFICATE_BASE64` 与密码 Secret，验收 Authenticode。

运行只读资源检查：

```bash
python scripts/external_acceptance_check.py
```

输出中的 `BLOCKED` 是真实缺失资源，不代表代码测试失败；脚本不会发起攻击、支付或打印密钥。
