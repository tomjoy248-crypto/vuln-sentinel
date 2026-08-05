"""扫描质量评估与误报控制模块。

提供：
- 误报过滤器：基于启发式规则降低低置信度 finding 的权重
- 扫描质量评分：评估单次扫描的覆盖度和可靠性
- Finding 去重与关联：减少重复报告
"""

from app.quality.fp_control import FalsePositiveControl, filter_findings
from app.quality.quality_assessment import ScanQualityAssessment, assess_scan_quality

__all__ = [
    "FalsePositiveControl",
    "filter_findings",
    "ScanQualityAssessment",
    "assess_scan_quality",
]
