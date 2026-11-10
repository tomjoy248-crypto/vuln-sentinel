# Vuln Sentinel 文档索引

本目录集中存放项目文档。仓库根目录只保留 `README.md`、`CHANGELOG.md` 和 `SECURITY.md`（GitHub 惯例），其余文档按下述分类归档于此。

## 状态与规划

| 文档 | 内容 |
|---|---|
| [当前状态](STATUS.md) | 软件现在能做什么、还不稳定什么、下一步看哪里 |
| [落地路线图](ROADMAP.md) | PWA / 桌面壳阶段规划 |
| [当前交付状态](DELIVERY_STATUS.md) | 交付物完成度总览 |
| [v12 交付状态](v12-readiness.md) | v12.0.0 交付状态与外部验收清单 |
| [v12 评审核对](review-reconciliation-v12.md) | v12.0.0 评审清单逐项对账 |

## 能力与基准

| 文档 | 内容 |
|---|---|
| [产品能力矩阵](PRODUCT_CAPABILITY_MATRIX.md) | 按场景列明支持程度与边界 |
| [误报率基准报告](BENCHMARK.md) | 基准测试结果（数据见 `benchmark_report.json`、`benchmark_chart.png`） |
| [注入准确性基准](injection-accuracy-baseline-v12.md) | V12.0.2 注入与高风险输入检出契约 |

## 部署与使用

| 文档 | 内容 |
|---|---|
| [生产部署指南](deployment.md) | 生产环境部署与配置 |
| [本地数据库说明](DATABASE_GUIDE.md) | SQLite 存储位置与查看方式 |
| [Windows 客户端初始化](WINDOWS_CLIENT_SETUP.md) | 客户端首次运行步骤 |
| [Windows 桌面壳打包](WINDOWS_DESKTOP_BUILD_AND_START.md) | 本地构建与启动流程 |
| [PDF 交付说明](pdf-delivery-guide.md) | PDF 交付物的生成与检查 |

## 验收与交付

| 文档 | 内容 |
|---|---|
| [Windows 人工验收清单](WINDOWS_MANUAL_ACCEPTANCE.md) | 干净环境人工验收步骤 |
| [Windows 实机验收清单](windows-acceptance-checklist.md) | 实机验收检查项 |
| [Windows 一页验收](windows-delivery-acceptance.md) | 面向交付的一页式验收 |
| [外部环境验收记录](EXTERNAL_ACCEPTANCE_TEMPLATE.md) | 外部实测证据记录模板 |
| [外部验收闭环](external-acceptance-plan.md) | 外部验收的组织流程 |

## 政策与声明

| 文档 | 内容 |
|---|---|
| [授权声明](AUTHORIZATION_NOTICE.md) | 扫描授权要求 |
| [隐私政策](PRIVACY_POLICY.md) | 数据处理方式 |
| [使用协议](TERMS_OF_USE.md) | 使用条款 |

## 对外文章

| 文档 | 内容 |
|---|---|
| [v12.0.1 发布文章](csdn-vuln-sentinel-v12.0.1.md) | CSDN 发布用版本介绍稿 |

## 项目资料

- `漏洞哨兵_项目计划书.docx` / `Vuln-Sentinel_Project_Plan.docx` — 项目计划书
- `architecture.svg` — 架构图

## 截图与归档

- [screenshots/](screenshots/) — 产品截图；精选集见 [finals/](screenshots/finals/)（12 张核心流程截图）
- [archive/](archive/) — 早期阶段的历史文档（Web 交付边界、Tauri 壳方案等），仅供追溯，不再维护
