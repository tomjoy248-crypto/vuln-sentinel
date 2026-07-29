"""复测验证模块。

提供修复前后扫描结果对比、交叉验证与闭环验证能力。
"""

from app.verification.cross_validator import CrossValidator, VerificationResult
from app.verification.diff_engine import ScanDiffEngine, DiffResult

__all__ = [
    "CrossValidator",
    "VerificationResult",
    "ScanDiffEngine",
    "DiffResult",
]
