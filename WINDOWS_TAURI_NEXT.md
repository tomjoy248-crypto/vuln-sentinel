# Tauri 桌面壳下一步执行清单

## 目标

把当前 Web 版复用到 Windows 桌面壳里，先形成一个能启动、能加载前端、能打包的最小版本。

## 本地准备

- 安装 Rust 工具链
- 安装 Tauri CLI
- 确认 Node.js 和 npm 可用
- 确认 `frontend/` 能正常构建

## 第一步：初始化依赖

```bash
cd src-tauri
cargo init --bin --name vuln-sentinel-desktop
```

如果已经有 `Cargo.toml`，则直接安装 Tauri 相关依赖并补齐配置。

## 第二步：接入前端

- 让桌面壳的 dev 模式指向 `frontend` 的 Vite 服务
- 让 build 模式读取 `frontend/dist`
- 保持 API 地址与 Web 版一致

## 第三步：验证启动

- 先跑 `npm --prefix frontend run build`
- 再跑桌面壳 dev
- 确认首页、扫描页、结果页、套餐页可打开

## 第四步：打包 Windows 程序

- 生成 `msi` 安装包
- 检查应用图标和窗口标题
- 确认版本号显示正确

## 第五步：后续增强

- 自动更新
- 系统托盘
- 启动页
- 离线提示
- 本地缓存
