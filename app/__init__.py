"""漏洞哨兵 11-S 应用包。

提供模块化基础设施：
- app.core.config: 统一配置管理
- app.core.logging: 结构化日志（structlog）
- app.core.security: JWT / 密码哈希 / 认证依赖
- app.db.session: 数据库连接管理
- app.health: 健康检查路由（live / ready / version）
- app.metrics: Prometheus 指标暴露
- app.middleware: request_id 中间件
"""
