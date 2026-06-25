# 更新日志

所有对漏洞哨兵有意义的变更都会记录在此文件。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [V11.5] - 2026-06-25

### 新增
- AI 顾问接入真实 LLM(OpenAI 兼容,支持 OpenAI/DeepSeek/通义千问/自定义 base_url)
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
- 双击 HTML 即可演示(无需启动后端)

## [V11.3] 及更早

见 git history。
