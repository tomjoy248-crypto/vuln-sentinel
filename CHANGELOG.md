# 更新日志

所有对漏洞哨兵有意义的变更都会记录在此文件。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

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
