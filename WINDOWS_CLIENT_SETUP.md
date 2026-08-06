# Windows 客户端初始化步骤

> 目标：把当前 Web 版复用成 Windows 桌面应用。

## 1. 安装基础环境

- 安装 Node.js
- 安装 Rust toolchain
- 安装 Tauri CLI

## 2. 初始化桌面壳

```bash
cd src-tauri
cargo init --bin --name vuln-sentinel-desktop
```

如果仓库里已经存在 `Cargo.toml`，则只需要补齐依赖并继续。

## 3. 安装 Tauri 依赖

```bash
cargo add tauri@2 tauri-build@2 serde serde_json
```

## 4. 准备前端构建

```bash
npm --prefix frontend run build
```

## 5. 本地开发

- 启动前端 Vite 服务
- 让 Tauri 指向 `http://localhost:5173`
- 打开桌面窗口验证首页、扫描页、结果页、套餐页

## 6. 打包 Windows 程序

```bash
cargo tauri build
```

## 7. 上线前检查

- 图标是否正常
- 窗口标题是否正常
- 版本号是否正确
- 支付与扫描流程是否一致
- 安装和卸载是否顺畅

## 8. 当前限制

- 目前仓库已有骨架，但没有真正运行 Rust/Tauri 依赖
- 要完成可编译版本，还需要安装系统环境后继续补最后一层
