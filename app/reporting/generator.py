"""
SRC 漏洞报告生成器

将扫描数据转换为标准化的 SRC 漏洞报告。
支持 Markdown 输出，并提供执行摘要、漏洞详情、技术附录等片段生成能力。
"""

import json
from datetime import datetime
from typing import Any

from .models import (
    ReportFormat,
    ScanExecutiveSummary,
    SRCReport,
    VulnerabilityEvidence,
    VulnerabilityReportItem,
)
from .templates import (
    APPENDIX_TEMPLATE,
    DISCLAIMER_TEMPLATE,
    EXECUTIVE_SUMMARY_TEMPLATE,
    FINDING_DETAIL_TEMPLATE,
    FINDINGS_SUMMARY_TEMPLATE,
    LIMITATION_ITEM,
    LIMITATIONS_TEMPLATE,
    METHODOLOGY_TEMPLATE,
    REFERENCE_ITEM,
    REPRODUCTION_STEP_ITEM,
    RISK_MATRIX_TEMPLATE,
    TITLE_TEMPLATE,
    TOOL_ITEM,
)

# 严重级别排序权重
SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "informational": 0,
    "info": 0,
}


def _normalize_severity(severity: str) -> str:
    """统一严重级别字符串为标题格式。"""
    mapping = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "informational": "Informational",
        "info": "Informational",
    }
    return mapping.get(severity.lower(), severity.capitalize())


def _format_duration(ms: int) -> str:
    """将毫秒格式化为可读字符串。"""
    if ms < 1000:
        return f"{ms} ms"
    seconds = ms / 1000.0
    if seconds < 60:
        return f"{seconds:.2f} s"
    minutes = seconds / 60.0
    if minutes < 60:
        return f"{minutes:.2f} min"
    hours = minutes / 60.0
    return f"{hours:.2f} h"


def _get_risk_level(score: int) -> str:
    """根据综合评分返回风险等级。"""
    if score >= 90:
        return "Critical"
    if score >= 75:
        return "High"
    if score >= 50:
        return "Medium"
    if score >= 20:
        return "Low"
    return "Informational"


def _normalize_verification_status(status: str) -> str:
    """统一验证状态展示口径。"""
    mapping = {
        "verified": "已验证",
        "confirmed": "已验证",
        "unverified": "待复核",
        "probable": "可能存在",
        "suspected": "待人工复核",
        "false positive": "误报",
        "false_positive": "误报",
    }
    key = (status or "").strip().lower().replace("_", " ")
    return mapping.get(key, status or "待复核")


def _build_summary_from_scan_data(scan_data: dict[str, Any]) -> ScanExecutiveSummary:
    """从原始扫描数据构建执行摘要对象。"""
    summary_data = scan_data.get("summary", {})
    if isinstance(summary_data, ScanExecutiveSummary):
        return summary_data

    target_url = summary_data.get("target_url", scan_data.get("target_url", "未知目标"))
    scan_time = summary_data.get(
        "scan_time", scan_data.get("scan_time", datetime.now().isoformat())
    )
    overall_score = int(
        summary_data.get("overall_score", scan_data.get("overall_score", 0))
    )
    risk_level = summary_data.get(
        "risk_level", scan_data.get("risk_level", _get_risk_level(overall_score))
    )

    findings = scan_data.get("findings", [])
    verified_count = int(
        summary_data.get("verified_count", scan_data.get("verified_count", 0))
    )
    unverified_count = int(
        summary_data.get("unverified_count", scan_data.get("unverified_count", 0))
    )
    false_positive_count = int(
        summary_data.get(
            "false_positive_count", scan_data.get("false_positive_count", 0)
        )
    )

    if not any([verified_count, unverified_count, false_positive_count]) and findings:
        verified_count = sum(
            1
            for f in findings
            if f.get("verification_status", "").lower() in {"verified", "confirmed"}
        )
        unverified_count = sum(
            1
            for f in findings
            if f.get("verification_status", "").lower() in {"unverified", "probable"}
        )
        false_positive_count = sum(
            1
            for f in findings
            if f.get("verification_status", "").lower() in {"false positive", "false_positive", "suspected"}
        )

    return ScanExecutiveSummary(
        target_url=target_url,
        scan_time=scan_time,
        overall_score=overall_score,
        risk_level=risk_level,
        total_findings=len(findings),
        verified_count=verified_count,
        unverified_count=unverified_count,
        false_positive_count=false_positive_count,
        scan_duration_ms=int(
            summary_data.get("scan_duration_ms", scan_data.get("scan_duration_ms", 0))
        ),
        scanner_version=summary_data.get(
            "scanner_version",
            scan_data.get("scanner_version", "v11-s-vuln-sentinel/1.0.10"),
        ),
    )


def _build_findings_from_scan_data(
    scan_data: dict[str, Any],
) -> list[VulnerabilityReportItem]:
    """从原始扫描数据构建漏洞列表。"""
    raw_findings = scan_data.get("findings", [])
    findings: list[VulnerabilityReportItem] = []

    for idx, raw in enumerate(raw_findings, start=1):
        if isinstance(raw, VulnerabilityReportItem):
            findings.append(raw)
            continue

        evidence_raw = raw.get("evidence", {})
        evidence = VulnerabilityEvidence(
            request=evidence_raw.get("request", ""),
            response=evidence_raw.get("response", ""),
            payload=evidence_raw.get("payload", ""),
            screenshots=evidence_raw.get("screenshots", []),
            notes=evidence_raw.get("notes", ""),
        )

        finding = VulnerabilityReportItem(
            id=raw.get("id", raw.get("finding_id", f"VULN-{idx:03d}")),
            title=raw.get("title", "未命名漏洞"),
            type=raw.get("type", raw.get("vulnerability_type", "其他")),
            severity=_normalize_severity(raw.get("severity", "Medium")),
            confidence=raw.get("confidence", "Tentative"),
            verification_status=_normalize_verification_status(raw.get("verification_status", "Unverified")),
            description=raw.get("description", ""),
            impact=raw.get("impact", ""),
            reproduction_steps=raw.get("reproduction_steps", []),
            evidence=evidence,
            fix_recommendation=raw.get(
                "fix_recommendation", raw.get("remediation", "")
            ),
            cwe_id=raw.get("cwe_id", ""),
            owasp_category=raw.get("owasp_category", ""),
            references=raw.get("references", []),
        )
        findings.append(finding)

    findings.sort(
        key=lambda f: SEVERITY_ORDER.get(f.severity.lower(), -1), reverse=True
    )
    return findings


def _severity_counts(findings: list[VulnerabilityReportItem]) -> dict[str, int]:
    """统计各严重级别数量。"""
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "informational": 0}
    for finding in findings:
        key = finding.severity.lower()
        if key in counts:
            counts[key] += 1
        else:
            counts["informational"] += 1
    return counts


def _escape_md_table_cell(text: str) -> str:
    """转义 Markdown 表格单元格中的特殊字符。"""
    return str(text).replace("|", "\\|").replace("\n", " ")


def generate_executive_summary(scan_data: dict[str, Any]) -> str:
    """生成 Markdown 执行摘要章节。"""
    summary = _build_summary_from_scan_data(scan_data)
    intro = (
        f"本报告面向客户交付、上线前验收与复扫留档。"
        f"本次扫描共发现 {summary.total_findings} 项安全问题，"
        f"建议优先处理已验证与高危项，并将待人工复核项作为后续验证清单。"
    )
    summary_block = (
        f"### 0.1 客户摘要\n\n"
        f"- 目标地址：`{summary.target_url}`\n"
        f"- 安全评分：{summary.overall_score} / 100\n"
        f"- 风险等级：{summary.risk_level}\n"
        f"- 发现问题：{summary.total_findings} 项\n"
        f"- 已验证：{summary.verified_count} 项，待人工复核：{summary.unverified_count} 项，误报：{summary.false_positive_count} 项\n"
        f"- 扫描时长：{_format_duration(summary.scan_duration_ms)}\n"
    )
    return intro + "\n\n" + summary_block + "\n" + EXECUTIVE_SUMMARY_TEMPLATE.format(
        target_url=_escape_md_table_cell(summary.target_url),
        total_findings=summary.total_findings,
        verified_count=summary.verified_count,
        unverified_count=summary.unverified_count,
        false_positive_count=summary.false_positive_count,
        overall_score=summary.overall_score,
        risk_level=summary.risk_level,
        scan_duration=_format_duration(summary.scan_duration_ms),
        scanner_version=summary.scanner_version,
    )


def generate_finding_detail(finding: dict[str, Any], index: int) -> str:
    """生成单个漏洞的 SRC 风格详细 writeup。"""
    if isinstance(finding, VulnerabilityReportItem):
        item = finding
    else:
        item = _build_findings_from_scan_data({"findings": [finding]})[0]

    reproduction_steps = (
        "\n".join(
            REPRODUCTION_STEP_ITEM.format(step_number=i + 1, step_description=step)
            for i, step in enumerate(item.reproduction_steps)
        )
        or "未提供具体复现步骤。"
    )

    references = (
        "\n".join(REFERENCE_ITEM.format(title=ref, url=ref) for ref in item.references)
        or "无。"
    )

    screenshots = (
        "\n".join(
            f"- ![截图]({s})"
            if s.startswith(("http://", "https://", "/"))
            else f"- {s}"
            for s in item.evidence.screenshots
        )
        or "无截图。"
    )

    return FINDING_DETAIL_TEMPLATE.format(
        index=index,
        finding_id=item.id,
        title=_escape_md_table_cell(item.title),
        type=_escape_md_table_cell(item.type),
        severity=item.severity,
        confidence=item.confidence,
        verification_status=item.verification_status,
        cwe_id=item.cwe_id or "未分类",
        owasp_category=item.owasp_category or "未分类",
        description=item.description or "未提供描述。",
        impact=item.impact or "未评估影响。",
        reproduction_steps=reproduction_steps,
        payload=item.evidence.payload or "无",
        request=item.evidence.request or "无",
        response=item.evidence.response or "无",
        screenshots=screenshots,
        notes=item.evidence.notes or "无",
        fix_recommendation=item.fix_recommendation or "暂无修复建议。",
        references=references,
    )


def _generate_findings_summary(
    findings: list[VulnerabilityReportItem], summary: ScanExecutiveSummary
) -> str:
    """生成漏洞汇总章节。"""
    counts = _severity_counts(findings)

    rows = []
    for finding in findings:
        rows.append(
            f"| {finding.id} | {_escape_md_table_cell(finding.title)} | {_escape_md_table_cell(finding.type)} | {finding.severity} | {finding.verification_status} | {finding.confidence} |"
        )

    return FINDINGS_SUMMARY_TEMPLATE.format(
        critical_count=counts["critical"],
        high_count=counts["high"],
        medium_count=counts["medium"],
        low_count=counts["low"],
        info_count=counts["informational"],
        verified_count=summary.verified_count,
        unverified_count=summary.unverified_count,
        false_positive_count=summary.false_positive_count,
        findings_table_rows="\n".join(rows)
        if rows
        else "| - | 未发现漏洞 | - | - | - | - |",
    )


def _generate_detailed_findings(findings: list[VulnerabilityReportItem]) -> str:
    """生成详细漏洞章节。"""
    if not findings:
        return "## 三、详细漏洞分析\n\n本次扫描未发现需要详细说明的安全问题。\n\n"

    sections = ["## 三、详细漏洞分析\n"]
    for idx, finding in enumerate(findings, start=1):
        sections.append(generate_finding_detail(finding, idx))
    return "\n".join(sections)


def _default_tools() -> list[dict[str, str]]:
    """返回默认工具列表。"""
    return [
        {
            "name": "v11-s-vuln-sentinel",
            "description": "本项目自研扫描引擎，负责目标发现、漏洞探测与证据收集。",
        },
        {
            "name": "Burp Suite / OWASP ZAP",
            "description": "用于手动/半自动化的 HTTP 流量分析与漏洞验证。",
        },
        {"name": "nmap", "description": "端口扫描与服务指纹识别。"},
        {"name": "sslscan / testssl.sh", "description": "SSL/TLS 配置与证书检测。"},
        {
            "name": "自定义 Payload 字典",
            "description": "针对目标技术栈构造的注入、XSS、路径遍历等测试用例。",
        },
    ]


def _default_limitations() -> list[str]:
    """返回默认限制说明列表。"""
    return [
        "测试时间窗口有限，未覆盖全部业务场景与接口。",
        "部分接口需要特定账号权限，测试可能未能深入所有角色视角。",
        "生产环境存在防护设备，部分深度利用行为未执行以避免业务影响。",
        "漏洞验证基于测试时刻的应用版本与配置，后续迭代可能改变漏洞存在状态。",
    ]


def generate_technical_appendix(scan_data: dict[str, Any]) -> str:
    """生成测试方法论、限制说明与附录章节。"""
    appendices = scan_data.get("appendices", {})
    if isinstance(appendices, dict):
        raw_headers = appendices.get(
            "raw_headers", scan_data.get("raw_headers", "未收集")
        )
        ssl_info = appendices.get("ssl_info", scan_data.get("ssl_info", "未收集"))
        extra = {
            k: v for k, v in appendices.items() if k not in ("raw_headers", "ssl_info")
        }
    else:
        raw_headers = scan_data.get("raw_headers", "未收集")
        ssl_info = scan_data.get("ssl_info", "未收集")
        extra = {}

    tools = scan_data.get("tools", _default_tools())
    tools_list = "\n".join(
        TOOL_ITEM.format(
            tool_name=t.get("name", "未知工具"),
            tool_description=t.get("description", ""),
        )
        for t in tools
    )

    limitations = scan_data.get("limitations", _default_limitations())
    if isinstance(limitations, str):
        limitations = [limitations] if limitations.strip() else _default_limitations()
    limitations_list = "\n".join(
        LIMITATION_ITEM.format(limitation_text=lim) for lim in limitations
    )

    extra_lines = []
    for key, value in extra.items():
        extra_lines.append(f"- **{key}**: {value}")
    extra_appendices = "\n".join(extra_lines) or "无额外附录数据。"

    methodology = METHODOLOGY_TEMPLATE.format(tools_list=tools_list)
    limitations_section = LIMITATIONS_TEMPLATE.format(limitations_list=limitations_list)
    appendix = APPENDIX_TEMPLATE.format(
        raw_headers=raw_headers,
        ssl_info=ssl_info,
        extra_appendices=extra_appendices,
    )
    return f"{methodology}\n{limitations_section}\n{RISK_MATRIX_TEMPLATE}\n{appendix}"


def generate_src_report(scan_data: dict[str, Any], format: str = "markdown") -> str:
    """生成完整的 SRC 漏洞报告。

    参数:
        scan_data: 扫描结果字典，可包含 summary / findings / appendices / tools / limitations 等字段。
        format: 输出格式，支持 markdown / json / html，默认 markdown。

    返回:
        对应格式的报告字符串。
    """
    fmt = ReportFormat(format.lower())

    summary = _build_summary_from_scan_data(scan_data)
    findings = _build_findings_from_scan_data(scan_data)

    report_model = SRCReport(
        summary=summary,
        findings=findings,
        methodology="",
        limitations="",
        appendices=scan_data.get("appendices", {}),
    )

    if fmt == ReportFormat.JSON:
        return json.dumps(report_model.to_dict(), ensure_ascii=False, indent=2)

    if fmt == ReportFormat.HTML:
        import html

        md = generate_src_report(scan_data, format="markdown")
        escaped = html.escape(md)
        wrapped = "<pre>" + escaped + "</pre>"
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>SRC 安全测试报告 - {html.escape(summary.target_url)}</title>
</head>
<body>
{wrapped}
</body>
</html>"""

    # Markdown 默认流程
    title = TITLE_TEMPLATE.format(
        target_url=summary.target_url,
        scan_time=summary.scan_time,
        scanner_version=summary.scanner_version,
        risk_level=summary.risk_level,
        overall_score=summary.overall_score,
    )

    client_summary = (
        "## 0. 客户摘要\n\n"
        f"- 目标地址：`{summary.target_url}`\n"
        f"- 扫描时间：{summary.scan_time}\n"
        f"- 安全评分：{summary.overall_score} / 100\n"
        f"- 风险等级：{summary.risk_level}\n"
        f"- 发现问题：{summary.total_findings} 项\n"
        f"- 已验证：{summary.verified_count}，待人工复核：{summary.unverified_count}，误报：{summary.false_positive_count}\n"
        f"- 扫描时长：{_format_duration(summary.scan_duration_ms)}\n\n"
        "### 0.1 交付结论\n\n"
        "> 本次结果可直接用于客户沟通、上线验收和复扫留档。建议优先关闭高危与已验证项，再复测中低风险项并保留证据链。\n\n"
        "### 0.2 后续动作\n\n"
        "1. 优先关闭高危与已验证问题。\n"
        "2. 复测中低风险项，确认修复是否生效。\n"
        "3. 归档结论、证据和变更记录，形成交付闭环。\n\n"
        "### 0.3 交付摘要\n\n"
        "建议将 PDF 与工单、复测结果、修复记录一并归档，便于后续客户复盘、版本追踪和责任分工。\n\n"
        "### 0.4 客户阅读顺序\n\n"
        "1. 先看客户摘要，快速确认目标、评分和风险等级。\n"
        "2. 再看执行摘要，判断是否需要优先处理高危项。\n"
        "3. 查看漏洞清单与单项详情，核对证据、复现步骤和修复建议。\n"
        "4. 最后查看技术附录，保留测试范围、限制与原始证据。"
    )

    parts = [
        title,
        DISCLAIMER_TEMPLATE,
        client_summary,
        generate_executive_summary(scan_data),
        _generate_findings_summary(findings, summary),
        _generate_detailed_findings(findings),
        generate_technical_appendix(scan_data),
    ]

    return "\n".join(parts)

