"""pytest 全局配置。

确保测试数据库在任何测试运行前完成初始化。
"""

import os
import sys

# 设置测试数据库路径（必须在导入 main 之前设置）
os.environ.setdefault("DB_DIR", "/tmp/v11-test")
os.environ.setdefault("DB_NAME", "test.db")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 导入 main 并初始化数据库
import main  # noqa: E402,F401

try:
    main.init_db()
except Exception:
    pass
