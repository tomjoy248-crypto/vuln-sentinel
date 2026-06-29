# Render 在线环境配置指南

## 目标
让在线演示 https://vuln-sentinel-v11-s.onrender.com 默认使用真实 DeepSeek 大模型，而非规则引擎。

---

## 步骤一：注册 DeepSeek API（5 分钟）

1. 打开 https://platform.deepseek.com/
2. 用手机号或邮箱注册
3. 进入「API Keys」页面，点击「创建 API Key」
4. 复制生成的 Key（格式如 `sk-xxxxxxxxxxxxxxxx`）

> DeepSeek 对新用户有免费额度，通常够评委体验用。

---

## 步骤二：Render 控制台改 Service Name（2 分钟）

1. 打开 https://dashboard.render.com/
2. 找到你的 Web Service（当前名称可能是 `vuln-sentinel-v11`）
3. 点击 Service 名称旁的齿轮图标 → Settings
4. 在「Name」字段，把 `vuln-sentinel-v11` 改成 `vuln-sentinel-v11-s`
5. 点击 Save
6. Render 会自动重新部署，新域名为 `https://vuln-sentinel-v11-s.onrender.com`

> 旧域名 `vuln-sentinel-v11.onrender.com` 会在几分钟后失效，记得更新 README 中的链接。

---

## 步骤三：添加 DeepSeek 环境变量（2 分钟）

1. 在 Render Dashboard，进入你的 Service → Environment
2. 点击「Add Environment Variable」，依次添加：

| Key | Value | 说明 |
|---|---|---|
| `LLM_ENABLED` | `true` | 启用真实 LLM |
| `LLM_PROVIDER` | `deepseek` | 指定使用 DeepSeek |
| `LLM_API_KEY` | `sk-xxxxxxxxxxxxxxxx` | 你刚才复制的 API Key |
| `LLM_MODEL` | `deepseek-chat` | DeepSeek 对话模型（可选，不填也自动识别） |

3. 点击 Save Changes，Render 会自动重新部署

---

## 步骤四：验证（1 分钟）

部署完成后（约 2-3 分钟），访问：

```
https://vuln-sentinel-v11-s.onrender.com/api/ai/status
```

应返回：
```json
{
  "success": true,
  "llm_enabled": true,
  "provider": "deepseek",
  "model": "deepseek-chat",
  "api_key_configured": true
}
```

然后进入首页，打开 AI 顾问，问「HSTS 是什么」，回复应来自真实 DeepSeek 模型（通常更长、更自然，且会包含具体的 Nginx 配置代码）。

---

## 备选：通义千问（阿里云）

如果 DeepSeek 注册不了，也可以用通义千问：

1. 打开 https://dashscope.aliyun.com/ 注册
2. 创建 API Key
3. Render 环境变量改为：
   - `LLM_PROVIDER` = `qwen`
   - `LLM_API_KEY` = 你的 DashScope Key
   - `LLM_MODEL` = `qwen-turbo`

---

## 常见问题

**Q: 配了 Key 但 AI 顾问还是规则引擎回复？**
- 检查环境变量是否拼写正确（全大写，下划线）
- 检查 `LLM_ENABLED` 是否为 `true`（不是 `True` 或 `1`）
- 部署后等 2 分钟再试

**Q: DeepSeek API 报错或超时？**
- DeepSeek 高峰期可能慢，刷新重试即可
- 代码已有自动降级：LLM 失败时会回到规则引擎，不会崩溃

**Q: 费用问题？**
- DeepSeek 新用户有 5000 万 tokens 免费额度
- 评委体验一次对话约消耗 500 tokens，几乎免费
