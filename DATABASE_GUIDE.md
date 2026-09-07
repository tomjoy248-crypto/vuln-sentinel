# 本地数据库说明

## Windows 桌面版

默认 SQLite 文件位置：

`%LOCALAPPDATA%\\Vuln Sentinel\\scans.db`

通常对应：

`C:\\Users\\你的用户名\\AppData\\Local\\Vuln Sentinel\\scans.db`

软件首次启动并完成数据库初始化后，该文件会自动创建。也可以在资源管理器地址栏输入 `%LOCALAPPDATA%\\Vuln Sentinel` 打开目录。

## DataGrip 连接

选择 SQLite 数据源，将 Database file 指向上述 `scans.db` 文件，然后点击测试连接。

## 其他部署

- 设置 `DB_DIR` 可以覆盖 SQLite 目录。
- 设置 `DB_NAME` 可以覆盖文件名。
- 设置 `DATABASE_URL` 可以切换 PostgreSQL。
- Docker Compose 默认使用 `/data`，数据由 Docker volume 持久化。

数据库可能包含账号、扫描目标、审计日志和漏洞证据，请勿提交到 GitHub 或发送到公开位置。
