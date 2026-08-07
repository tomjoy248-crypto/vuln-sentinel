# 可编译 Tauri 工程下一步

要把 `src-tauri/` 从骨架变成可编译工程，还需要补齐这些内容：

## 1. 安装依赖

- Rust toolchain
- `tauri-cli`
- Tauri JavaScript 依赖

## 2. 补齐工程文件

- `src-tauri/Cargo.toml` 中加入 `tauri` 依赖
- `src-tauri/build.rs` 中加入 `tauri_build`（当前已补齐）
- `src-tauri/src/main.rs` 中创建应用窗口（当前已补齐）
- `src-tauri/tauri.conf.json` 中补齐打包参数（当前已切到 `NSIS` / `currentUser`）

## 3. 接入前端

- 让 dev 模式加载 `frontend` 的 Vite 服务
- 让 build 模式加载 `frontend/dist`
- 让桌面壳与 Web 版共用同一套 API

## 4. Windows 打包

- 生成 `NSIS` 安装包（当前用户安装）
- 检查图标和版本号
- 校验安装、卸载、更新流程

## 5. 先做什么最划算

当前最划算的顺序是：

1. Web 商业版再稳一点
2. Tauri 工程补齐可编译配置
3. Windows 打包

