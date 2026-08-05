"""
SRC 漏洞报告数据模型
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReportFormat(str, Enum):
    """报告输出格式枚举"""

    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"
    PDF = "pdf"


@dataclass
class VulnerabilityEvidence:
    """漏洞证据数据模型"""

    request: str = ""
    response: str = ""
    payload: str = ""
    screenshots: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "response": self.response,
            "payload": self.payload,
            "screenshots": self.screenshots,
            "notes": self.notes,
        }


@dataclass
class VulnerabilityReportItem:
    """单个漏洞报告项数据模型"""

    id: str = ""
    title: str = ""
    type: str = ""
    severity: str = "Medium"
    confidence: str = "Tentative"
    verification_status: str = "Unverified"
    description: str = ""
    impact: str = ""
    reproduction_steps: list[str] = field(default_factory=list)
    evidence: VulnerabilityEvidence = field(default_factory=VulnerabilityEvidence)
    fix_recommendation: str = ""
    cwe_id: str = ""
    owasp_category: str = ""
    references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "severity": self.severity,
            "confidence": self.confidence,
            "verification_status": self.verification_status,
            "description": self.description,
            "impact": self.impact,
            "reproduction_steps": self.reproduction_steps,
            "evidence": self.evidence.to_dict(),
            "fix_recommendation": self.fix_recommendation,
            "cwe_id": self.cwe_id,
            "owasp_category": self.owasp_category,
            "references": self.references,
        }


@dataclass
class ScanExecutiveSummary:
    """扫描执行摘要数据模型"""

    target_url: str = ""
    scan_time: str = ""
    overall_score: int = 0
    risk_level: str = "Informational"
    total_findings: int = 0
    verified_count: int = 0
    unverified_count: int = 0
    false_positive_count: int = 0
    scan_duration_ms: int = 0
    scanner_version: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_url": self.target_url,
            "scan_time": self.scan_time,
            "overall_score": self.overall_score,
            "risk_level": self.risk_level,
            "total_findings": self.total_findings,
            "verified_count": self.verified_count,
            "unverified_count": self.unverified_count,
            "false_positive_count": self.false_positive_count,
            "scan_duration_ms": self.scan_duration_ms,
            "scanner_version": self.scanner_version,
        }


@dataclass
class SRCReport:
    """完整 SRC 报告数据模型"""

    summary: ScanExecutiveSummary = field(default_factory=ScanExecutiveSummary)
    findings: list[VulnerabilityReportItem] = field(default_factory=list)
    methodology: str = ""
    limitations: str = ""
    appendices: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "findings": [f.to_dict() for f in self.findings],
            "methodology": self.methodology,
            "limitations": self.limitations,
            "appendices": self.appendices,
        }
