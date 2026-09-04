"""
SRC 漏洞报告生成模块

提供标准化的安全研究 SRC 漏洞报告生成能力，
支持 Markdown / JSON / HTML 等多种输出格式。
"""

from .generator import (
    generate_executive_summary,
    generate_finding_detail,
    generate_src_report,
    generate_technical_appendix,
)
from .models import (
    ReportFormat,
    ScanExecutiveSummary,
    SRCReport,
    VulnerabilityEvidence,
    VulnerabilityReportItem,
)

__all__ = [
    "generate_src_report",
    "generate_executive_summary",
    "generate_finding_detail",
    "generate_technical_appendix",
    "ReportFormat",
    "SRCReport",
    "ScanExecutiveSummary",
    "VulnerabilityEvidence",
    "VulnerabilityReportItem",
]

__version__ = "11-S"
