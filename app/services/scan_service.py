"""扫描服务：基于插件注册表的扫描调度与结果聚合。"""

from __future__ import annotations

import random
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.plugins import DetectorRegistry, EvidenceStore, ScanContext
from app.plugins._compat import findings_to_old_list
from app.plugins.builtin import register_builtin_detectors


def _ensure_plugins_registered() -> None:
    """确保内置插件至少注册一次。"""
    if not DetectorRegistry.list():
        register_builtin_detectors()


def _calculate_score(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """根据 findings 计算评分与汇总。"""
    score = 100
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0, "total": 0}
    severity_weights = {"critical": 25, "high": 15, "medium": 8, "low": 3, "info": 0}
    for f in findings:
        sev = f.get("severity", "info")
        summary[sev] = summary.get(sev, 0) + 1
        summary["total"] += 1
        score -= severity_weights.get(sev, 0)
    score = max(10, min(100, score))
    risk_level = "critical" if score < 40 else "high" if score < 60 else "medium" if score < 80 else "low"
    return {"score": score, "risk_level": risk_level, "summary": summary}


async def run_plugin_scan(
    url: str,
    headers: Dict[str, str],
    is_https: bool,
    ssl_info: Dict[str, Any],
    waf: Optional[str] = None,
    deep: bool = False,
    body: str = "",
) -> Dict[str, Any]:
    """使用插件化检测引擎执行扫描。

    返回结构与 src_scanner.run_src_scan 保持一致，确保前端与测试兼容。
    """
    import src_scanner

    _ensure_plugins_registered()
    start_ts = time.time()

    store = EvidenceStore(max_entries=50)
    src_scanner.set_evidence_store(store)
    context = ScanContext(
        url=url,
        headers={k.lower(): v for k, v in (headers or {}).items()},
        body=body or "",
        is_https=is_https,
        ssl_info=ssl_info or {},
        waf_list=[{"name": waf}] if waf else [],
        depth="deep" if deep else "standard",
        evidence_store=store,
    )

    results = await DetectorRegistry.run_all(context)
    plugin_findings: List[Any] = []
    for detector_findings in results.values():
        plugin_findings.extend(detector_findings)
    findings = findings_to_old_list(plugin_findings)

    stats = _calculate_score(findings)
    duration_ms = int((time.time() - start_ts) * 1000)

    # 生成与 run_src_scan 兼容的 report_share_id
    report_id = f"RPT-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))}"

    src_scanner.clear_evidence_store()

    return {
        "success": True,
        "scan_id": int(time.time()),
        "url": url,
        "score": stats["score"],
        "risk_level": stats["risk_level"],
        "summary": stats["summary"],
        "findings": findings,
        "headers": headers,
        "waf": waf,
        "ssl": ssl_info,
        "duration_ms": duration_ms,
        "report_share_id": report_id,
        "discovered_at": datetime.now(timezone.utc).isoformat(),
        "scan_engine": "plugin",
    }
