# Vuln Sentinel 桌面壳启动说明

## 默认启动体验

- 窗口标题：`Vuln Sentinel - 安全扫描与交付平台`
- 默认进入 Web 版首页
- 保持与 Web 版一致的扫描、结果、套餐和审计入口

## 说明

Tauri 官方推荐的结构里，`src-tauri/` 负责 Rust 与打包配置，前端则通过 `devUrl` 和 `frontendDist` 接入。
