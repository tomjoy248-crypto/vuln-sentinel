# Windows 桌面壳打包说明

## 启动目标

- 默认打开 `Vuln Sentinel - 安全扫描与交付平台`
- 默认进入 Web 首页
- 保持登录、扫描、结果、套餐、审计入口一致

## 打包目标

- 首先打通 `cargo check`
- 然后打通 `cargo tauri build`
- 最后生成 Windows 安装包 `msi`

## 图标与品牌

- 图标放在 `src-tauri/icons/`
- Windows 下使用 `icon.ico`
- macOS 下使用 `icon.icns`
- Linux / Windows 通用图标使用 `png`

## 交付注意

- 桌面壳只负责承载 Web 版
- 核心业务逻辑仍由现有后端与前端提供
- Windows 版发布前要确认 Build Tools、WebView2 和签名流程
