"""用户反馈闭环。

把用户对 finding 的误报/确认反馈应用到新的扫描结果中，
实现"越用越准"的持续改进效果。
"""

from __future__ import annotations

import logging
from typing import Any

from app.db.session import get_db_connection

logger = logging.getLogger("vuln_sentinel.feedback_loop")


def enrich_finding_status(finding: dict[str, Any]) -> dict[str, Any]:
    """Attach one stable lifecycle status and a compact evidence summary."""
    result = dict(finding)
    feedback = result.get("user_feedback") or {}
    if feedback.get("is_false_positive"):
        status = "excluded"
    elif feedback.get("is_confirmed"):
        status = "confirmed"
    elif result.get("is_likely_fp"):
        status = "suspected"
    else:
        status = str(result.get("finding_status") or result.get("verification_status") or "unverified")
        if status not in {"unverified", "suspected", "confirmed", "excluded"}:
            status = "unverified"
    result["finding_status"] = status
    result["status_label"] = {
        "unverified": "未验证",
        "suspected": "疑似",
        "confirmed": "已确认",
        "excluded": "已排除",
    }[status]
    evidence = result.get("evidence")
    if isinstance(evidence, dict):
        result["evidence_summary"] = {
            "has_request": bool(evidence.get("request")),
            "has_response": bool(evidence.get("response")),
            "has_headers": bool(evidence.get("response_headers") or evidence.get("headers")),
            "basis": list(result.get("fp_reasons") or []),
        }
    return result


def get_user_feedback_for_findings(
    user_id: int, finding_names: list[str]
) -> dict[str, dict[str, Any]]:
    """查询用户对指定 finding 名称的最新反馈。

    返回：finding_name -> {"is_false_positive": bool, "is_confirmed": bool}
    """
    if not user_id or not finding_names:
        return {}

    try:
        with get_db_connection() as conn:
            placeholders = ",".join("?" for _ in finding_names)
            rows = conn.execute(
                f"""SELECT finding_name, is_false_positive, is_confirmed
                    FROM finding_feedback
                    WHERE user_id=? AND finding_name IN ({placeholders})
                    ORDER BY created_at ASC""",  # nosec B608 - placeholders 仅含 ? 占位符，值通过参数化查询传递
                (user_id, *finding_names),
            ).fetchall()

            result: dict[str, dict[str, Any]] = {}
            for row in rows:
                name = row["finding_name"]
                result[name] = {
                    "is_false_positive": bool(row["is_false_positive"]),
                    "is_confirmed": bool(row["is_confirmed"]),
                }
            return result
    except Exception as e:
        logger.warning("get_user_feedback_for_findings failed: %s", e)
        return {}


def apply_user_feedback(
    findings: list[dict[str, Any]],
    user_id: int,
) -> list[dict[str, Any]]:
    """将用户历史反馈应用到当前扫描结果。

    规则：
    - 若 finding 被同一用户标记为误报，则 confidence 降为 low，并附加 feedback 标记
    - 若 finding 被同一用户标记为确认，则 confidence 提升为 high，并附加 feedback 标记
    - 无论是否命中，都补充 user_feedback 字段供前端展示
    """
    if not user_id or not findings:
        return findings

    names = [f.get("title") or f.get("name") or "" for f in findings]
    names = [n for n in names if n]
    feedback_map = get_user_feedback_for_findings(user_id, names)

    enriched: list[dict[str, Any]] = []
    for f in findings:
        new_f = enrich_finding_status(f)
        name = new_f.get("title") or new_f.get("name") or ""
        fb = feedback_map.get(name)

        if fb:
            new_f["user_feedback"] = fb
            if fb.get("is_false_positive"):
                new_f["adjusted_confidence"] = "low"
                new_f["feedback_note"] = "该漏洞此前被您标记为误报，已降低置信度"
                new_f["is_likely_fp"] = True
                new_f["finding_status"] = "excluded"
                new_f["status_label"] = "已排除"
            elif fb.get("is_confirmed"):
                new_f["adjusted_confidence"] = "high"
                new_f["feedback_note"] = "该漏洞此前被您确认有效，已提升置信度"
                new_f["finding_status"] = "confirmed"
                new_f["status_label"] = "已确认"
        else:
            new_f["user_feedback"] = None

        enriched.append(new_f)

    return enriched
