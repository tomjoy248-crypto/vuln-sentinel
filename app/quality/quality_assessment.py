"""扫描质量评估模块。

为每次扫描生成质量评分，帮助用户判断扫描结果的可信度。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScanQualityAssessment:
    """扫描质量评估结果。"""

    overall_score: int = 0  # 0-100
    coverage_score: int = 0  # 覆盖度 0-100
    reliability_score: int = 0  # 可靠性 0-100
    depth_score: int = 0  # 深度 0-100

    coverage_breakdown: dict[str, Any] = field(default_factory=dict)
    reliability_breakdown: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "coverage_score": self.coverage_score,
            "reliability_score": self.reliability_score,
            "depth_score": self.depth_score,
            "coverage_breakdown": self.coverage_breakdown,
            "reliability_breakdown": self.reliability_breakdown,
            "recommendations": self.recommendations,
        }


def assess_scan_quality(
    findings: list[dict[str, Any]],
    scan_duration_ms: int = 0,
    depth: str = "standard",
    target_url: str = "",
) -> ScanQualityAssessment:
    """评估单次扫描的质量。

    评估维度：
    1. 覆盖度：检测了多少种漏洞类型、参数覆盖率
    2. 可靠性：误报率、置信度分布
    3. 深度：扫描时长、请求数量、检测深度
    """
    assessment = ScanQualityAssessment()

    # ---------- 覆盖度评分 ----------
    vuln_types = set()
    total_findings = len(findings)
    high_confidence = 0
    fp_count = 0

    for f in findings:
        vuln_types.add(f.get("type", "unknown"))
        conf = f.get("adjusted_confidence", f.get("confidence", "high")).lower()
        if conf in ("high", "critical"):
            high_confidence += 1
        if f.get("is_likely_fp"):
            fp_count += 1

    # 漏洞类型覆盖（期望至少覆盖 5 种基础类型）
    expected_types = {"sqli", "xss", "header_missing", "info_leak", "csrf", "ssl", "cors_misconfig", "open_redirect", "cmdi", "ssrf", "traversal", "xxe", "idor", "file_upload", "logic_bypass", "auth_weakness", "bruteforce_protection", "api_auth_missing", "sensitive_config_exposure", "clickjacking"}
    type_coverage = len(vuln_types & expected_types) / max(1, len(expected_types))
    type_bonus = min(30, len(vuln_types) * 3)

    coverage_score = int(min(100, type_coverage * 50 + type_bonus))
    assessment.coverage_score = coverage_score
    assessment.coverage_breakdown = {
        "types_detected": sorted(vuln_types),
        "type_count": len(vuln_types),
        "expected_type_coverage": round(type_coverage, 2),
        "total_findings": total_findings,
    }

    # ---------- 可靠性评分 ----------
    if total_findings > 0:
        fp_rate = fp_count / total_findings
        high_conf_rate = high_confidence / total_findings
    else:
        fp_rate = 0.0
        high_conf_rate = 0.0

    # 误报率越低越好，高置信度比例越高越好
    reliability_score = int(max(0, min(100, (1 - fp_rate) * 60 + high_conf_rate * 40)))
    assessment.reliability_score = reliability_score
    assessment.reliability_breakdown = {
        "fp_count": fp_count,
        "fp_rate": round(fp_rate, 2),
        "high_confidence_count": high_confidence,
        "high_confidence_rate": round(high_conf_rate, 2),
    }

    # ---------- 深度评分 ----------
    depth_multiplier = {"quick": 0.6, "standard": 1.0, "deep": 1.3}
    multiplier = depth_multiplier.get(depth, 1.0)

    # 扫描时长评分（5-30 秒为合理范围）
    duration_sec = scan_duration_ms / 1000.0
    if duration_sec < 3:
        duration_score = 30
    elif duration_sec < 10:
        duration_score = 60
    elif duration_sec < 30:
        duration_score = 85
    else:
        duration_score = 100

    depth_score = int(min(100, duration_score * multiplier))
    assessment.depth_score = depth_score

    # ---------- 总体评分 ----------
    assessment.overall_score = int(
        coverage_score * 0.4 + reliability_score * 0.4 + depth_score * 0.2
    )

    # ---------- 建议 ----------
    recommendations: list[str] = []
    if type_coverage < 0.5:
        recommendations.append("建议启用深度扫描模式，并补充更多端点、参数和漏洞类型覆盖")
    if fp_rate > 0.3:
        recommendations.append(
            "检测到较高比例的潜在误报，建议人工复核低置信度项并收紧判定阈值"
        )
    if duration_sec < 5 and depth != "quick":
        recommendations.append(
            "扫描完成速度较快，可能目标响应异常或网络受限，建议检查连接质量与反爬/WAF 拦截"
        )
    if total_findings == 0:
        recommendations.append(
            "未检测到漏洞，建议确认目标是否可访问、页面是否存在反爬或 WAF 拦截，并补充登录态页面/深层路径测试"
        )
    if not recommendations:
        recommendations.append("当前结果可信度较高，建议优先关注高危及以上 finding，并按修复清单逐项复测")

    assessment.recommendations = recommendations
    return assessment
