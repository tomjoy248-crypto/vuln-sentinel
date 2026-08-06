# Windows 壳构建约定

## 目录约定

- `frontend/`：现有 Web 前端
- `src-tauri/`：Windows 桌面壳配置与 Rust 入口
- `frontend/dist/`：桌面壳读取的前端构建结果

## 构建顺序

1. `npm --prefix frontend run build`
2. 桌面壳读取 `frontend/dist`
3. Windows 打包输出安装包

## 当前状态

- 前端已可独立构建
- 桌面壳骨架已创建
- 还需要 Rust / Tauri 真正初始化才能进入可编译阶段
