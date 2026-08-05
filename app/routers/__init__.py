"""API 路由模块。

将 main.py 中的端点按业务领域拆分到独立路由文件。
每个路由文件创建自己的 APIRouter 实例，由 main.py 在启动时注册。

路由文件通过 `from main import ...` 获取共享依赖（get_db、require_login 等）。
这要求 main.py 在文件末尾导入路由模块，确保所有共享函数已定义。
"""
