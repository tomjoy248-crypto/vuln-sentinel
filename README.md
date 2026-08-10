# Vuln Sentinel

Vuln Sentinel 是一款面向中小团队的安全扫描与修复工具，强调真实证据、可复测结果和可交付报告。

## 下载
- GitHub Release: <https://github.com/tomjoy248-crypto/vuln-sentinel/releases/latest>
- Windows 安装包: `Vuln Sentinel_1.0.6_x64-setup.exe`

## 产品定位
- 输入目标网址后执行授权扫描
- 结果按 `已确认 / 可疑 / 待复核` 分层展示
- 输出修复建议、复测验证和交付摘要
- 适合内测、演示、交付前复测与持续巡检

## 能力边界
- 更适合基础安全体检、证据展示、修复建议和复测验证
- 不承诺“扫全网、扫全漏洞、零误报”
- 对 WAF、CDN、软 404、强登录态和复杂业务流，仍可能需要人工复核

## 适用场景
- 独立开发者 / 个人站长
- 中小企业技术负责人
- 乙方交付团队
- 运维 / DevOps

## 快速开始
1. 下载 Windows 安装包并安装。
2. 打开应用，输入目标网址。
3. 查看结果、修复建议与复测信息。

## 安全提示
- 仅对已授权目标执行扫描
- 生产环境请设置 `JWT_SECRET`、`ALLOWED_ORIGINS`、`PUBLIC_BASE_URL`
- `PUBLIC_DEMO_ENABLED` 默认关闭，如需公开演示请明确开启

## 相关文档
- [安全策略](SECURITY.md)
- [生产部署指南](docs/deployment.md)
- [Windows 验收清单](docs/windows-acceptance-checklist.md)
