# Vuln Sentinel

![CI](https://github.com/tomjoy248-crypto/vuln-sentinel/actions/workflows/ci.yml/badge.svg)

Vuln Sentinel 是一款面向中小团队的安全体检与修复交付工具，强调真实证据、可复测结果、建议复核分层和可直接交付的客户报告。

## 当前状态

- [查看当前软件状态](STATUS.md)
- [查看能力边界](PRODUCT_CAPABILITY_MATRIX.md)
- [查看 Windows 构建与启动说明](WINDOWS_DESKTOP_BUILD_AND_START.md)

## 下载
- GitHub Release：优先下载最新版本 <https://github.com/tomjoy248-crypto/vuln-sentinel/releases/latest>
- Windows 安装包：如果本地构建，可在 `artifacts/windows/` 找到对应安装包；发布时以 Releases 页显示的最新包名为准

## 产品定位
- 输入授权目标后执行安全体检
- 结果按 `已确认 / 建议复核 / 待人工复核` 分层展示，并附带证据等级、误报提示和复核建议
- 输出修复建议、复测验证和交付摘要，便于直接进入客户沟通
- 适合客户沟通、交付前复测与持续巡检
- 当前更适合基础安全体检、证据展示、复测验证和修复跟踪，不承诺全漏洞覆盖或零误报

## 能力边界
- 更适合基础安全体检、证据展示、修复建议和复测验证
- 不承诺“扫全网、扫全漏洞、零误报”
- 对 WAF、CDN、软 404、强登录态和复杂业务流，仍可能需要人工复核
- 当前重点是压误报、保可用、保可复测

## 适用场景
- 独立开发者 / 个人站长
- 中小企业技术负责人
- 乙方交付团队
- 运维 / DevOps

## 快速开始
1. 从 GitHub Releases 下载最新版 Windows 安装包并安装。
2. 打开应用，输入目标网址。
3. 查看结果、修复建议、建议复核项与复测信息。

## 安全提示
- 仅对已授权目标执行扫描。
- 生产环境请配置 `JWT_SECRET`、`ALLOWED_ORIGINS`、`PUBLIC_BASE_URL`。
- `PUBLIC_DEMO_ENABLED` 默认关闭，如需公开演示请明确开启。

## 相关文件
- [安全策略](SECURITY.md)
- [生产部署指南](docs/deployment.md)
- [Windows 验收清单](docs/windows-acceptance-checklist.md)
- [当前状态](STATUS.md)
