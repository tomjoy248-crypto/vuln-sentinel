# VulnSentinel 文档

本目录用于存放项目相关文档与展示资源。

## 目录结构

```
docs/
├── README.md           # 本文件
└── screenshots/        # 产品截图（占位）
    ├── home.png        # 首页：产品定位 / 入口
    ├── report.png      # 扫描报告：三区分层 + 评分
    └── fix.png         # 修复包下载：一键生成的可部署配置
```

## docs/screenshots/ 说明

`docs/screenshots/` 目录用于放置 README 顶部"产品截图"区域引用的三张图片：

| 文件名 | 建议内容 | 推荐尺寸 |
|---|---|---|
| `home.png` | 首页主界面，体现产品定位、登录入口、快速扫描按钮 | 1200×750 |
| `report.png` | 扫描报告页：左侧三区分层（风险/扫描/修复）、中间评分仪表盘、右侧证据与建议 | 1200×750 |
| `fix.png` | 修复包下载页：Nginx/Apache/Express/Flask/Spring Boot/Cloudflare 多平台配置 | 1200×750 |

### 如何贡献截图

1. 启动 VulnSentinel：
   ```bash
   cd v11-s-vuln-sentinel
   pip3 install -r requirements.txt --break-system-packages
   python3 main.py
   ```
2. 浏览器打开 `http://localhost:8000`，账号 `demo / demo123`。
3. 截取首页、扫描报告页、修复包下载页三张图。
4. 将图片分别保存为 `docs/screenshots/home.png`、`docs/screenshots/report.png`、`docs/screenshots/fix.png`。
5. 提交 PR 后，README 顶部的截图占位就会自动渲染。

### 当前状态

- README 中已通过相对路径引用三张占位图。
- 在真实截图提交前，图片链接会显示为 GitHub 的 "image not loaded" 提示，**不影响其他 Markdown 渲染**。
- 欢迎社区贡献者补齐这三张图，让产品说明更直观。
