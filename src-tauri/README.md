# Tauri 桌面壳骨架

这是 `Vuln Sentinel` 的 Windows 桌面壳最小目录。

## 作用

- 复用现有 `frontend/` Web 版
- 后续可直接接入 `Tauri`
- 先把配置、启动命令和打包目标放好

## 当前结构

- `Cargo.toml`：Rust 包配置占位
- `build.rs`：构建触发占位
- `tauri.conf.json`：Tauri 应用配置
- `src/main.rs`：桌面壳入口占位
- `icons/`：桌面图标目录占位

## 还没做的事

- Rust / Tauri 依赖安装
- 实际桌面窗口事件
- 自动更新
- 系统托盘
- 文件选择和本地存储增强

## 下一步

1. 安装 Rust
2. 安装 `tauri-cli`
3. 初始化 `src-tauri` 依赖
4. 让桌面壳加载 `frontend/dist`
5. 打包 `msi`
