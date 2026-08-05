"""用户反馈闭环。

把用户对 finding 的误报/确认反馈应用到新的扫描结果中，
实现"越用越准"的持续改进效果。
"""

from __future__ import annotations

import logging
from typing import Any

from app.db.session import get_db_connection

logger = logging.getLogger("vuln_sentinel.feedback_loop")


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
        new_f = dict(f)
        name = new_f.get("title") or new_f.get("name") or ""
        fb = feedback_map.get(name)

        if fb:
            new_f["user_feedback"] = fb
            if fb.get("is_false_positive"):
                new_f["adjusted_confidence"] = "low"
                new_f["feedback_note"] = "该漏洞此前被您标记为误报，已降低置信度"
                new_f["is_likely_fp"] = True
            elif fb.get("is_confirmed"):
                new_f["adjusted_confidence"] = "high"
                new_f["feedback_note"] = "该漏洞此前被您确认有效，已提升置信度"
        else:
            new_f["user_feedback"] = None

        enriched.append(new_f)

    return enriched
