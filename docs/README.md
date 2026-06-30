# VulnSentinel 文档

本目录用于存放项目文档、架构图和比赛展示截图。

## 目录结构

```
docs/
├── README.md
├── architecture.svg
├── coverage-badge.svg
└── screenshots/
    ├── README.md
    └── finals/
        ├── 01-home.png
        ├── 02-scanning.png
        ├── 03-findings-detail.png
        └── ...
```

## 截图说明

`docs/screenshots/finals/` 已包含比赛展示用截图，覆盖首页、扫描过程、漏洞详情、修复建议、修复前后对比、资产管理、工单和移动端视图。

顶层 `README.md` 当前引用的是 finals 目录中的精选截图：

| 文件 | 内容 |
|---|---|
| `finals/01-home.png` | 产品首页 |
| `finals/03-findings-detail.png` | 扫描报告与漏洞详情 |
| `finals/04-findings-and-fix.png` | 修复建议 |
| `finals/08-fix-compare.png` | 修复前后对比 |

## 重新生成截图

1. 启动 VulnSentinel：
   ```bash
   python3 main.py
   ```
2. 浏览器打开 `http://localhost:8000`，账号 `demo / demo123`。
3. 按 `docs/screenshots/finals/README.md` 中的流程重新截图。
