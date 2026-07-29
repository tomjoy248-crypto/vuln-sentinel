"""复测验证模块。

提供修复前后扫描结果对比与闭环验证能力。
"""

from app.verification.diff_engine import ScanDiffEngine, DiffResult

__all__ = ["ScanDiffEngine", "DiffResult"]
