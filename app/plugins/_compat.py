"""兼容层：将旧版 SRC finding 字典转换为新版 Finding 对象。"""

from __future__ import annotations

import uuid
from typing import Any

from app.plugins import Evidence, Finding, FixSuggestion, VulnLocation


def old_finding_to_finding(data: dict[str, Any]) -> Finding:
    """把 src_scanner.build_finding 产出的字典转为插件化 Finding。"""
    evidence = data.get("evidence") or {}

    location_str = str(data.get("location") or "")
    parameter_type = "query"
    if "请求体" in location_str or "Body" in location_str:
        parameter_type = "body"
    elif "响应头" in location_str or "HTTP 响应头" in location_str:
        parameter_type = "header"
    elif "Cookie" in location_str:
        parameter_type = "cookie"
    elif "路径" in location_str or "path" in location_str.lower():
        parameter_type = "path"

    fix_code = data.get("fix_code") or {}
    if not fix_code and data.get("fixes_by_platform"):
        fix_code = data["fixes_by_platform"]

    fix = FixSuggestion(
        generic=data.get("fix") or data.get("fix_suggestion") or "",
        by_platform=fix_code,
        risk_note="",
    )

    finding_id = data.get("id") or ""
    if not finding_id:
        finding_id = f"VS-{str(uuid.uuid4())[:8].upper()}"

    return Finding(
        id=finding_id,
        title=data.get("title") or data.get("name") or "未命名漏洞",
        type=data.get("type") or "unknown",
        severity=(data.get("severity") or "medium").lower(),
        confidence=data.get("confidence") or "high",
        cvss_score=data.get("cvss_score"),
        severity_score=data.get("severity_score"),
        cvss_vector=data.get("cvss_vector") or "",
        cwe_id=data.get("cwe_id") or "",
        owasp_category=data.get("owasp_category") or data.get("owasp") or "",
        description=data.get("description") or data.get("summary") or "",
        impact=data.get("impact") or data.get("description") or "",
        url=data.get("url") or "",
        parameter=data.get("parameter") or "",
        location=VulnLocation(
            url=data.get("url") or "",
            method="GET",
            parameter=data.get("parameter") or "",
            parameter_type=parameter_type,
            snippet=location_str,
        ),
        evidence=Evidence(
            request_raw=evidence.get("request") or evidence.get("request_raw") or "",
            response_raw=evidence.get("response") or evidence.get("response_raw") or "",
            matched_signature=evidence.get("matched_signature") or "",
            payload=evidence.get("payload") or "",
            notes=evidence.get("notes") or "",
            screenshot=evidence.get("screenshot"),
            extra={
                k: v
                for k, v in evidence.items()
                if k
                not in {
                    "request",
                    "response",
                    "request_raw",
                    "response_raw",
                    "matched_signature",
                    "payload",
                    "notes",
                    "screenshot",
                }
            },
        ),
        raw_evidence={
            k: v
            for k, v in data.items()
            if k
            not in {
                "id",
                "title",
                "name",
                "type",
                "severity",
                "severity_score",
                "cvss_score",
                "cvss_vector",
                "confidence",
                "cwe_id",
                "owasp_category",
                "owasp",
                "description",
                "summary",
                "impact",
                "url",
                "parameter",
                "location",
                "evidence",
                "fix",
                "fix_suggestion",
                "fix_code",
                "fixes_by_platform",
                "reproduce_steps",
                "references",
                "discovered_at",
                "status",
            }
        },
        fix_suggestion=data.get("fix") or data.get("fix_suggestion") or "",
        fix=fix,
        fix_code=fix_code,
        reproduce_steps=data.get("reproduce_steps") or [],
        references=data.get("references") or [],
        discovered_at=data.get("discovered_at") or "",
        status=data.get("status") or "open",
    )


def findings_to_old_list(findings: list[Finding]) -> list[dict[str, Any]]:
    """将 Finding 对象列表转回旧版字典列表（用于兼容既有 API）。"""
    return [f.to_dict() for f in findings]
