# 漏洞哨兵 11-S - 决赛 Demo 截图集

本目录包含 12 张精选截图，覆盖 11-S 的全部核心流程。
可直接用于：TRAE 比赛帖、PPT 演示、产品介绍、复盘材料。

## 📸 截图清单

| # | 文件 | 场景 | 核心信息点 | 建议使用位置 |
|---|------|------|----------|------------|
| 01 | `01-home.png` | 产品首页 | 品牌定位、4 大特性（真实扫描/账号隔离/PDF/可分享）、3 个一键演示目标（example.com / iana.org / httpbin.org） | 帖子的"产品概览" |
| 02 | `02-scanning.png` | 扫描进行中 | 实时扫描公开测试站、按钮 loading 状态 | 帖子的"功能演示"第一张 |
| 03 | `03-findings-detail.png` | 报告-详细问题 | 7 项详细漏洞（HSTS/CSP/X-Frame-Options/X-Content-Type-Options/Referrer-Policy/Permissions-Policy/Server 信息泄露）、P1-P3 优先级、OWASP 分类 | 帖子的"扫描结果" |
| 04 | `04-findings-and-fix.png` | 报告-修复建议 | 8 种平台修复建议 tab（Nginx/Apache/Express/Flask/Spring Boot/Cloudflare/Node.js/Python）、可复制代码 | 帖子的"修复建议" |
| 05 | `05-score-compare.png` | 报告-操作面板 | "用 AI 修复器生成补丁" / "一键应用修复" 操作按钮 | 帖子的"工作流闭环" |
| 06 | `06-fix-generator.png` | 修复器-首页 | 粘贴配置文件、AI 智能检测、6 步使用流程 | 帖子的"配置修复器模块" |
| 07 | `07-fix-diff.png` | 修复器-检测结果 | 4 高 + 2 中 + 2 低 严重度分布、修复点清单 | 帖子的"AI 修复能力" |
| 08 | `08-fix-compare.png` | 修复器-代码对比 | 修复前/修复后 side-by-side 对比、Diff 高亮（绿+红） | 帖子的"修复可视化" |
| 09 | `09-assets-empty.png` | 资产管理 | 添加资产表单、空状态引导 | 帖子的"资产管理模块" |
| 10 | `10-tickets.png` | 修复工单 | 待修复/修复中/已修复/已忽略 4 状态流转、批量操作 | 帖子的"工单跟踪" |
| 11 | `11-mobile.png` | 移动端视图 | 响应式布局、底部 tab 导航、卡片堆叠 | 帖子的"全平台适配" |
| 12 | `12-iana-report.png` | 反例对比 | iana.org 96 分、0 高 0 中 2 低、关键安全头全配 | 帖子的"误报率低" |

## 🎯 推荐组合（用于决赛帖）

### 方案 A：完整闭环演示（6 张）
1. 01-home → 02-scanning → 03-findings-detail → 04-findings-and-fix → 08-fix-compare → 12-iana-report

### 方案 B：技术深度展示（8 张）
1. 01-home → 03-findings-detail → 04-findings-and-fix → 06-fix-generator → 07-fix-diff → 08-fix-compare → 10-tickets → 12-iana-report

### 方案 C：差异化亮点（5 张）
1. 01-home → 04-findings-and-fix（8 平台 tab）→ 07-fix-diff（4 高 2 中 2 低）→ 08-fix-compare（Diff 高亮）→ 12-iana-report（高安全 96 分）

## 📊 截图元数据

- **尺寸**：1280×自动（响应式）
- **格式**：PNG
- **总大小**：约 1.2 MB
- **拍摄日期**：2026-06-24
- **目标用户**：比赛评委 / 用户 / 投资人
- **登录账号**：demo / demo123

## 🔄 重新生成

```bash
# 启动服务
cd /workspace/v11.4
python3 main.py &

# 用浏览器/Playwright 打开 http://localhost:8000/?v=6
# 按顺序点击：
# 1. 立即扫描 example.com → 等待 1-3 秒
# 2. 截报告
# 3. 点修复器 → 加载示例 → 分析配置 → 截对比
# 4. 点资产/工单 → 截
# 5. 模拟移动端 → 截
```
