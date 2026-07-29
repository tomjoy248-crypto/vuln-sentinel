"""扫描服务：基于插件注册表的扫描调度与结果聚合。

集成完整的扫描后处理流水线：
  插件检测 → 误报控制 → Finding 去重与关联 → 交叉验证 → 质量评估
"""

from __future__ import annotations

import logging
import random
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.dedup import FindingDeduplicator
from app.plugins import DetectorRegistry, EvidenceStore, ScanContext
from app.plugins._compat import findings_to_old_list
from app.plugins.builtin import register_builtin_detectors
from app.quality.fp_control import FalsePositiveControl
from app.quality.quality_assessment import assess_scan_quality

logger = logging.getLogger("vuln_sentinel.scan_service")


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

    后处理流水线：
      1. 插件检测器并行执行
      2. 误报控制：启发式分析并标记潜在误报
      3. Finding 去重与关联：合并重复 finding，标注关联组
      4. 质量评估：生成扫描质量评分
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

    # 1. 插件检测器并行执行
    results = await DetectorRegistry.run_all(context)
    plugin_findings: List[Any] = []
    for detector_findings in results.values():
        plugin_findings.extend(detector_findings)
    findings = findings_to_old_list(plugin_findings)

    # 2. 误报控制
    fp_controller = FalsePositiveControl(threshold=0.3)
    findings = fp_controller.analyze_batch(findings)
    fp_marked = sum(1 for f in findings if f.get("is_likely_fp"))
    if fp_marked > 0:
        logger.info("FP control: %d findings flagged as likely false positive", fp_marked)

    # 3. Finding 去重与关联
    deduper = FindingDeduplicator()
    findings, dedup_stats = deduper.deduplicate(findings)
    if dedup_stats.duplicate_count > 0:
        logger.info(
            "Dedup: %d -> %d findings (%d duplicates removed, %d correlation groups)",
            dedup_stats.original_count,
            dedup_stats.deduplicated_count,
            dedup_stats.duplicate_count,
            dedup_stats.correlation_groups,
        )

    # 4. 质量评估
    duration_ms = int((time.time() - start_ts) * 1000)
    quality = assess_scan_quality(
        findings=findings,
        scan_duration_ms=duration_ms,
        depth="deep" if deep else "standard",
        target_url=url,
    )

    stats = _calculate_score(findings)

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
        "quality": quality.to_dict(),
        "dedup_stats": dedup_stats.to_dict(),
    }
