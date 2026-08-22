"""扫描服务：基于插件注册表的扫描调度与结果聚合。

集成完整的扫描后处理流水线：
  插件检测 → 误报控制 → Finding 去重与关联 → 交叉验证 → 质量评估
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import random
import time
from datetime import datetime, timezone
from typing import Any

from app.dedup import FindingDeduplicator
from app.plugins import DetectorRegistry, EvidenceStore, ScanContext
from app.plugins._compat import findings_to_old_list
from app.plugins.builtin import register_builtin_detectors
from app.quality.fp_control import FalsePositiveControl
from app.quality.quality_assessment import assess_scan_quality
from app.services.discovery_crawler import DiscoveryCrawler
from app.services.fuzz_engine import FuzzEngine, fuzz_results_to_findings
from app.verification.cross_validator import CrossValidator

logger = logging.getLogger("vuln_sentinel.scan_service")

_CV_CACHE: dict[str, tuple[float, list[dict[str, Any]]]] = {}
_CV_CACHE_TTL = 600.0
_CV_CACHE_MAX = 256


def _cv_cache_key(findings: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for finding in findings:
        parts.append(
            "|".join(
                [
                    str(finding.get("name", "")),
                    str(finding.get("severity", "")),
                    str(finding.get("confidence", "")),
                    str(finding.get("url", "")),
                    str(finding.get("parameter", "")),
                    str(finding.get("location", "")),
                    str(finding.get("evidence", {}).get("matched_signature", "")),
                ]
            )
        )
    digest = hashlib.sha256("\n".join(sorted(parts)).encode("utf-8", errors="ignore")).hexdigest()
    return digest


def _get_cached_cv(findings: list[dict[str, Any]]) -> list[dict[str, Any]] | None:
    now = time.time()
    key = _cv_cache_key(findings)
    cached = _CV_CACHE.get(key)
    if not cached:
        return None
    created_at, payload = cached
    if now - created_at > _CV_CACHE_TTL:
        _CV_CACHE.pop(key, None)
        return None
    return payload


def _set_cached_cv(findings: list[dict[str, Any]], payload: list[dict[str, Any]]) -> None:
    key = _cv_cache_key(findings)
    if len(_CV_CACHE) >= _CV_CACHE_MAX:
        oldest_key = min(_CV_CACHE.items(), key=lambda item: item[1][0])[0]
        _CV_CACHE.pop(oldest_key, None)
    _CV_CACHE[key] = (time.time(), payload)


def _ensure_plugins_registered() -> None:
    """确保内置插件至少注册一次。"""
    if not DetectorRegistry.list():
        register_builtin_detectors()


def _calculate_score(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """根据 findings 计算参考评分与汇总。

    评分偏保守：高置信度高危项影响更大，低置信度项影响更小，
    避免单条弱证据把结果拉得过低。"""
    score = 100
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0, "total": 0}
    severity_weights = {"critical": 25, "high": 15, "medium": 8, "low": 3, "info": 0}
    confidence_multipliers = {"critical": 1.0, "high": 1.0, "medium": 0.7, "low": 0.4, "info": 0.2}
    verification_multipliers = {"confirmed": 1.0, "probable": 0.85, "suspected": 0.6}
    for finding in findings:
        sev = str(finding.get("severity", "info")).lower()
        conf_value = finding.get("adjusted_confidence") or finding.get("confidence") or ""
        conf = str(conf_value).lower()
        summary[sev] = summary.get(sev, 0) + 1
        summary["total"] += 1
        weight = severity_weights.get(sev, 0)
        multiplier = confidence_multipliers.get(conf, 1.0)
        verification = str(finding.get("verification_status", "")).lower()
        multiplier *= verification_multipliers.get(verification, 1.0)
        if finding.get("is_likely_fp"):
            multiplier *= 0.5
        if conf == 'info':
            multiplier *= 0.6
        score -= int(round(weight * multiplier))
    if summary["total"] == 0:
        risk_level = "low"
    else:
        score = max(10, min(100, score))
        risk_level = (
            "critical"
            if score < 40
            else "high"
            if score < 60
            else "medium"
            if score < 80
            else "low"
        )
    return {"score": score, "risk_level": risk_level, "summary": summary}


async def _run_cross_validation(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """对 findings 执行交叉验证，失败时返回原始结果不阻塞主流程。"""
    cached = _get_cached_cv(findings)
    if cached is not None:
        logger.info("Cross-validation cache hit for %d findings", len(findings))
        return cached
    validator = CrossValidator()
    try:
        enriched = await validator.validate_finding_batch(findings)
        verified_count = sum(
            1 for f in enriched if f.get("verification_status") == "confirmed"
        )
        probable_count = sum(
            1 for f in enriched if f.get("verification_status") == "probable"
        )
        suspected_count = sum(
            1 for f in enriched if f.get("verification_status") == "suspected"
        )
        logger.info(
            "Cross-validation: %d confirmed, %d probable, %d suspected (total %d)",
            verified_count,
            probable_count,
            suspected_count,
            len(enriched),
        )
        _set_cached_cv(findings, enriched)
        return enriched
    except Exception as exc:
        logger.warning("Cross-validation failed, returning original findings: %s", exc)
        return findings


async def run_plugin_scan(
    url: str,
    headers: dict[str, str],
    is_https: bool,
    ssl_info: dict[str, Any],
    waf: str | None = None,
    deep: bool = False,
    body: str = "",
    enable_verification: bool = True,
) -> dict[str, Any]:
    """使用插件化检测引擎执行扫描。

    返回结构与 src_scanner.run_src_scan 保持一致，确保前端与测试兼容。

    后处理流水线：
      1. 插件检测器并行执行
      2. 误报控制：启发式分析并标记潜在误报
      3. Finding 去重与关联：合并重复 finding，标注关联组
      4. 交叉验证：对关键漏洞类型进行多技术验证（可配置）
      5. 质量评估：生成扫描质量评分
    """
    import src_scanner

    _ensure_plugins_registered()
    start_ts = time.time()
    phase_timings: dict[str, float] = {}  # phase_name -> elapsed_ms

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

    # 1. 插件检测器并行执行（首页上下文）
    _phase_start = time.time()
    results = await DetectorRegistry.run_all(context)
    plugin_findings: list[Any] = []
    for detector_findings in results.values():
        plugin_findings.extend(detector_findings)
    phase_timings["plugin_detection"] = (time.time() - _phase_start) * 1000

    # 1.5 端点发现：扩大覆盖面（仅在 deep 模式下开启，避免 standard 超时）
    endpoints: list[Any] = []
    if deep:
        _phase_start = time.time()
        try:
            crawler = DiscoveryCrawler(
                max_pages=15 if deep else 8,
                request_timeout=4.0,
                total_timeout=15.0 if deep else 8.0,
                max_forms=10 if deep else 5,
            )
            endpoints = await crawler.discover(url, headers=context.headers)
            logger.info("Running detectors on %d discovered endpoints", len(endpoints))

            async def _run_on_endpoint(ep: Any) -> list[Any]:
                sub_ctx = ScanContext(
                    url=ep.url,
                    headers=context.headers,
                    body=ep.body or "",
                    is_https=is_https,
                    ssl_info=ssl_info or {},
                    waf_list=context.waf_list,
                    depth="deep" if deep else "standard",
                    evidence_store=store,
                )
                sub_results = await DetectorRegistry.run_all(sub_ctx)
                collected: list[Any] = []
                for detector_findings in sub_results.values():
                    for finding in detector_findings:
                        # 记录发现来源，方便后续定位
                        finding.url = ep.url
                        finding.location.url = ep.url
                        if ep.method != "GET":
                            finding.location.method = ep.method
                        collected.append(finding)
                return collected

            if endpoints:
                endpoint_tasks = [_run_on_endpoint(ep) for ep in endpoints]
                endpoint_results = await asyncio.gather(
                    *endpoint_tasks, return_exceptions=True
                )
                for res in endpoint_results:
                    if isinstance(res, list):
                        plugin_findings.extend(res)
                    elif isinstance(res, Exception):
                        logger.warning("Endpoint detection error: %s", res)
        except Exception as exc:
            logger.warning("Endpoint discovery disabled or failed: %s", exc)
        phase_timings["endpoint_discovery"] = (time.time() - _phase_start) * 1000

    # 2. 参数 fuzz：对发现的端点执行定向注入测试（deep 模式启用）
    if deep:
        _phase_start = time.time()
        try:
            fuzzer = FuzzEngine(
                techniques=[
                    "sqli",
                    "xss",
                    "ssti",
                    "cmdi",
                    "traversal",
                    "ssrf",
                    "open_redirect",
                    "xxe",
                    "crlf",
                ],
                request_timeout=6.0,
                max_params=12,
            )
            fuzz_targets = [url]
            fuzz_payloads: list[tuple[str, str, str]] = []
            if endpoints:
                for ep in endpoints:
                    if not ep.url:
                        continue
                    if "?" in ep.url:
                        fuzz_targets.append(ep.url)
                    if getattr(ep, "body", "") and getattr(ep, "parameter_names", None):
                        fuzz_payloads.append((ep.url, ep.body or "", getattr(ep, "method", "GET")))
            fuzz_targets = list(dict.fromkeys(fuzz_targets))[:20]  # 去重并限制数量

            fuzz_results_map = await fuzzer.fuzz_multiple(
                urls=fuzz_targets,
                headers=context.headers,
                max_concurrency=3,
            )
            fuzz_count = 0
            for target_url, fuzz_results in fuzz_results_map.items():
                if fuzz_results:
                    converted = fuzz_results_to_findings(fuzz_results, target_url)
                    plugin_findings.extend(converted)
                    fuzz_count += len(converted)

            if fuzz_payloads:
                async with httpx.AsyncClient(
                    timeout=fuzzer.request_timeout + 2,
                    follow_redirects=fuzzer.follow_redirects,
                    headers=context.headers,
                ) as fuzz_client:
                    for target_url, body, method in fuzz_payloads[:10]:
                        if method.upper() != "POST":
                            continue
                        try:
                            extra_results = await fuzzer.fuzz_url(
                                fuzz_client,
                                target_url,
                                headers=context.headers,
                                body=body,
                                content_type="application/x-www-form-urlencoded",
                                method=method,
                            )
                        except Exception as exc:
                            logger.debug("Form fuzz failed for %s: %s", target_url, exc)
                            continue
                        if extra_results:
                            converted = fuzz_results_to_findings(extra_results, target_url)
                            plugin_findings.extend(converted)
                            fuzz_count += len(converted)
            if fuzz_count > 0:
                logger.info("Fuzzing found %d potential injection issues", fuzz_count)
        except Exception as exc:
            logger.warning("Fuzzing engine failed: %s", exc)
        phase_timings["fuzzing"] = (time.time() - _phase_start) * 1000

    findings = findings_to_old_list(plugin_findings)

    # 2. 误报控制
    _phase_start = time.time()
    fp_controller = FalsePositiveControl(threshold=0.35)
    findings = fp_controller.analyze_batch(findings)
    fp_marked = sum(1 for f in findings if f.get("is_likely_fp"))
    if fp_marked:
        logger.info("False-positive control marked %d findings", fp_marked)
    phase_timings["fp_control"] = (time.time() - _phase_start) * 1000

    # 3. Finding 去重与关联
    _phase_start = time.time()
    deduper = FindingDeduplicator()
    findings, dedup_stats = deduper.deduplicate(findings)
    phase_timings["dedup"] = (time.time() - _phase_start) * 1000

    # 4. 交叉验证（standard/deep 默认开启，quick 可关闭）
    _phase_start = time.time()
    verification_stats = {
        "enabled": bool(enable_verification),
        "confirmed": 0,
        "probable": 0,
        "suspected": 0,
    }
    if enable_verification and findings:
        findings = await _run_cross_validation(findings)
        verification_stats["confirmed"] = sum(
            1 for f in findings if f.get("verification_status") == "confirmed"
        )
        verification_stats["probable"] = sum(
            1 for f in findings if f.get("verification_status") == "probable"
        )
        verification_stats["suspected"] = sum(
            1 for f in findings if f.get("verification_status") == "suspected"
        )
    phase_timings["cross_validation"] = (time.time() - _phase_start) * 1000

    # 5. 质量评估
    _phase_start = time.time()
    duration_ms = int((time.time() - start_ts) * 1000)
    quality = assess_scan_quality(
        findings=findings,
        scan_duration_ms=duration_ms,
        depth="deep" if deep else "standard",
        target_url=url,
    )
    phase_timings["quality_assessment"] = (time.time() - _phase_start) * 1000

    stats = _calculate_score(findings)

    # 生成与 run_src_scan 兼容的 report_share_id
    report_id = (
        f"RPT-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))}"
    )

    src_scanner.clear_evidence_store()

    # 最终汇总日志：各阶段耗时 breakdown（始终打印）
    _total_ms = time.time() - start_ts
    _breakdown = " ".join(
        f"{k}={v:.0f}ms" for k, v in sorted(phase_timings.items(), key=lambda x: -x[1])
    )
    logger.info(
        "Scan complete: url=%s depth=%s total=%.0fms findings=%d score=%d risk=%s | %s",
        url,
        "deep" if deep else "standard",
        _total_ms * 1000,
        len(findings),
        stats["score"],
        stats["risk_level"],
        _breakdown,
    )
    # 超过 3 秒的阶段单独告警
    for _pname, _pms in phase_timings.items():
        if _pms > 3000:
            logger.warning(
                "Slow phase '%s': %.0fms for url=%s",
                _pname,
                _pms,
                url,
            )

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
        "verification_stats": verification_stats,
        "phase_timings_ms": phase_timings,
    }
