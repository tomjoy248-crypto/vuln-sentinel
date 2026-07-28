"""SARIF 2.1.0 导入/导出模块。

SARIF (Static Analysis Results Interchange Format) 是 OASIS 标准，
用于安全工具之间的结果交换。GitHub Code Scanning 原生支持 SARIF 导入。

参考规范: https://docs.oasis.org/opensarif/sarif-spec/v2.1.0/
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("vuln_sentinel.sarif")

# SARIF 严重度级别映射
_SEVERITY_TO_SARIF_LEVEL = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
    "info": "none",
}

# SARIF 规则 ID 生成
def _make_rule_id(finding: dict) -> str:
    """根据漏洞类型和 CWE 生成稳定的规则 ID。"""
    vuln_type = finding.get("type", finding.get("vuln_type", "unknown"))
    cwe = finding.get("cwe_id", "")
    if cwe:
        return f"VS-{cwe.replace('CWE-', '')}"
    return f"VS-{vuln_type.upper()}"


def _finding_to_sarif_result(finding: dict, rule_index_map: dict) -> dict:
    """将单个 finding 转换为 SARIF result 对象。"""
    rule_id = _make_rule_id(finding)
    rule_index = rule_index_map.get(rule_id, 0)

    severity = finding.get("severity", "medium")
    level = _SEVERITY_TO_SARIF_LEVEL.get(severity, "warning")

    # 构建消息
    message_text = finding.get("summary", finding.get("description", finding.get("name", "漏洞")))
    if len(message_text) > 500:
        message_text = message_text[:497] + "..."

    # 构建位置信息
    url = finding.get("url", finding.get("evidence", {}).get("url", ""))
    locations = []
    if url:
        locations.append({
            "physicalLocation": {
                "artifactLocation": {
                    "uri": url,
                },
            },
            "logicalLocations": [
                {
                    "name": finding.get("parameter", finding.get("location", {}).get("target", "")) or "N/A",
                    "kind": "parameter",
                }
            ] if finding.get("parameter") or finding.get("location", {}).get("target") else [],
        })

    # 构建部分指纹（用于去重）
    partial_fingerprints = {
        "primary": f"{rule_id}:{url}:{finding.get('parameter', '')}",
    }

    # 证据
    code_flows = []
    evidence = finding.get("evidence", {})
    if evidence:
        code_flows.append({
            "threadFlows": [
                {
                    "locations": [
                        {
                            "location": {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": url or "unknown"},
                                    "region": {"startLine": 1},
                                },
                                "message": {"text": json.dumps(evidence, ensure_ascii=False)[:1000]},
                            }
                        }
                    ]
                }
            ]
        })

    result: Dict[str, Any] = {
        "ruleId": rule_id,
        "ruleIndex": rule_index,
        "level": level,
        "message": {"text": message_text},
        "locations": locations,
        "partialFingerprints": partial_fingerprints,
    }

    if code_flows:
        result["codeFlows"] = code_flows

    # 修复建议
    fix = finding.get("fix", finding.get("fix_suggestion", ""))
    if fix:
        result["fixes"] = [
            {
                "description": {"text": fix[:1000]},
            }
        ]

    return result


def _build_sarif_rules(findings: List[dict]) -> tuple:
    """从 findings 列表构建 SARIF rules 数组和 rule_index 映射。"""
    rules = []
    rule_index_map = {}
    seen = set()

    for f in findings:
        rule_id = _make_rule_id(f)
        if rule_id in seen:
            continue
        seen.add(rule_id)

        vuln_type = f.get("type", f.get("vuln_type", "unknown"))
        cwe = f.get("cwe_id", "")
        owasp = f.get("owasp", f.get("owasp_category", ""))

        # 规则元数据
        rule: Dict[str, Any] = {
            "id": rule_id,
            "name": vuln_type.replace("_", " ").title()[:100],
            "shortDescription": {
                "text": f.get("name", vuln_type)[:200],
            },
            "fullDescription": {
                "text": f.get("summary", f.get("description", ""))[:1000],
            },
            "helpUri": f"https://cwe.mitre.org/data/definitions/{cwe.replace('CWE-', '')}.html" if cwe else "",
            "defaultConfiguration": {
                "level": _SEVERITY_TO_SARIF_LEVEL.get(f.get("severity", "medium"), "warning"),
            },
            "properties": {
                "tags": [owasp] if owasp else [],
                "precision": "high" if f.get("confidence_level", "高") == "高" else "medium",
                "security-severity": _severity_to_score(f.get("severity", "medium")),
            },
        }

        if cwe:
            rule["properties"]["tags"].append(cwe)

        rule_index_map[rule_id] = len(rules)
        rules.append(rule)

    return rules, rule_index_map


def _severity_to_score(severity: str) -> str:
    """将严重度转换为 SARIF security-severity (0-10)。"""
    mapping = {
        "critical": "9.5",
        "high": "8.0",
        "medium": "5.0",
        "low": "2.5",
        "info": "0.0",
    }
    return mapping.get(severity, "5.0")


def export_to_sarif(scan_data: dict, tool_name: str = "漏洞哨兵 11-S", tool_version: str = "11-S") -> dict:
    """将扫描结果导出为 SARIF 2.1.0 格式。

    Args:
        scan_data: 扫描结果字典，需包含 findings 列表
        tool_name: 工具名称
        tool_version: 工具版本

    Returns:
        SARIF 2.1.0 格式的字典
    """
    findings = scan_data.get("findings", [])
    rules, rule_index_map = _build_sarif_rules(findings)

    results = []
    for f in findings:
        try:
            results.append(_finding_to_sarif_result(f, rule_index_map))
        except Exception as e:
            logger.warning("SARIF result conversion failed for finding: %s", e)

    sarif_report = {
        "$schema": "https://docs.oasis.org/opensarif/sarif-spec/v2.1.0/CS01/schemas/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "version": tool_version,
                        "informationUri": "https://github.com/tomjoy248-crypto/vuln-sentinel",
                        "rules": rules,
                    }
                },
                "results": results,
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "endTimeUtc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                ],
                "properties": {
                    "scanUrl": scan_data.get("url", ""),
                    "scanScore": scan_data.get("score", 0),
                    "scanRiskLevel": scan_data.get("risk_level", ""),
                },
            }
        ]
    }

    return sarif_report


def import_from_sarif(sarif_data: dict) -> List[dict]:
    """从 SARIF 2.1.0 格式导入漏洞结果。

    Args:
        sarif_data: SARIF 格式的字典

    Returns:
        转换后的 findings 列表
    """
    findings = []
    runs = sarif_data.get("runs", [])

    for run in runs:
        # 构建规则查找表
        rules = run.get("tool", {}).get("driver", {}).get("rules", [])
        rule_map = {i: r for i, r in enumerate(rules)}
        rule_map_by_id = {r.get("id", ""): r for r in rules}

        results = run.get("results", [])
        for result in results:
            rule_id = result.get("ruleId", "")
            rule_index = result.get("ruleIndex", 0)
            rule = rule_map.get(rule_index) or rule_map_by_id.get(rule_id, {})

            # SARIF level 转换回严重度
            level = result.get("level", "warning")
            severity = _sarif_level_to_severity(level)

            # 从规则属性获取 security-severity
            sec_severity = rule.get("properties", {}).get("security-severity")
            if sec_severity:
                try:
                    score = float(sec_severity)
                    if score >= 9.0:
                        severity = "critical"
                    elif score >= 7.0:
                        severity = "high"
                    elif score >= 4.0:
                        severity = "medium"
                    else:
                        severity = "low"
                except (ValueError, TypeError):
                    pass

            # 提取位置信息
            locations = result.get("locations", [])
            url = ""
            parameter = ""
            if locations:
                phys = locations[0].get("physicalLocation", {})
                url = phys.get("artifactLocation", {}).get("uri", "")
                logical = locations[0].get("logicalLocations", [])
                if logical:
                    parameter = logical[0].get("name", "")

            # 提取消息
            message = result.get("message", {}).get("text", "")

            # 提取修复建议
            fixes = result.get("fixes", [])
            fix_text = fixes[0].get("description", {}).get("text", "") if fixes else ""

            # 提取证据
            evidence = {}
            code_flows = result.get("codeFlows", [])
            if code_flows:
                thread_flows = code_flows[0].get("threadFlows", [])
                if thread_flows:
                    flow_locs = thread_flows[0].get("locations", [])
                    if flow_locs:
                        evidence_text = flow_locs[0].get("location", {}).get("message", {}).get("text", "")
                        if evidence_text:
                            try:
                                evidence = json.loads(evidence_text)
                            except json.JSONDecodeError:
                                evidence = {"raw": evidence_text}

            # 从规则属性提取标签
            tags = rule.get("properties", {}).get("tags", [])
            owasp = ""
            cwe = ""
            for tag in tags:
                if tag.startswith("A0") or tag.startswith("A1"):
                    owasp = tag
                elif tag.startswith("CWE-"):
                    cwe = tag

            finding = {
                "name": rule.get("shortDescription", {}).get("text", rule.get("name", "未知漏洞")),
                "severity": severity,
                "level": {"critical": "严重", "high": "高风险", "medium": "中风险", "low": "低风险"}.get(severity, "中风险"),
                "owasp": owasp,
                "summary": message,
                "fix": fix_text,
                "type": rule.get("name", "unknown").lower().replace(" ", "_"),
                "evidence": evidence,
                "url": url,
                "parameter": parameter,
                "cwe_id": cwe,
                "confidence_level": "高" if rule.get("properties", {}).get("precision") == "high" else "中",
                "source": "sarif_import",
                "source_tool": run.get("tool", {}).get("driver", {}).get("name", "unknown"),
            }

            findings.append(finding)

    return findings


def _sarif_level_to_severity(level: str) -> str:
    """将 SARIF level 转换回严重度。"""
    mapping = {
        "error": "high",
        "warning": "medium",
        "note": "low",
        "none": "info",
    }
    return mapping.get(level, "medium")
