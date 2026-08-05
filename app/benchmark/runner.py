"""基准测试运行器。

对每个已知漏洞靶场目标执行扫描，收集结果并与预期漏洞对比，生成混淆矩阵
（TP/FP/TN/FN）和检测指标（精确率、召回率、F1、准确率、误报率）。

混淆矩阵模型（每个检查点为一个评估单元）：

    - **TP (真正例)**: 预期漏洞被正确检出。
    - **FN (假反例/漏报)**: 预期漏洞未被检出。
    - **FP (假正例/误报)**: 报告了不存在的漏洞（命中负向检查或未预期的 finding）。
    - **TN (真反例)**: 负向检查未被违反（正确判定无该漏洞）。

匹配流程：

    1. 对每个预期漏洞，在 findings 中查找匹配项 → 命中记 TP 并消费该 finding，
       未命中记 FN。
    2. 对每个负向检查，在剩余（未消费）findings 中查找匹配项 → 命中记 FP
       并消费该 finding，未命中记 TN。
    3. 剩余未消费的 findings 均为未预期发现 → 每条记一个 FP。

如此每个 finding 恰好归入一类结果，混淆矩阵保持自洽：

    - 正例总数 = TP + FN = 预期漏洞数
    - 负例总数 = FP + TN = 负向检查数 + 未预期发现数

指标定义：

    - 精确率 (Precision) = TP / (TP + FP)
    - 召回率 (Recall)    = TP / (TP + FN)
    - F1 Score           = 2 * Precision * Recall / (Precision + Recall)
    - 准确率 (Accuracy)  = (TP + TN) / (TP + FP + TN + FN)
    - 误报率 (FPR)        = FP / (FP + TN)
"""

from __future__ import annotations

import asyncio
import logging
import os
import socket
import ssl
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx

from app.benchmark.targets import (
    BENCHMARK_TARGETS,
    BenchmarkTarget,
    ExpectedVulnerability,
    NegativeCheck,
)

logger = logging.getLogger("vuln_sentinel.benchmark")

# 扫描函数类型：与 app.services.scan_service.run_plugin_scan 签名一致
# (url, headers, is_https, ssl_info, waf, deep, body) -> scan_result_dict
ScanFunc = Callable[..., Awaitable[dict[str, Any]]]


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------


@dataclass
class ConfusionMatrix:
    """混淆矩阵计数。

    Attributes:
        tp: 真正例数（正确检出预期漏洞）。
        fp: 假正例数（误报）。
        tn: 真反例数（正确判定无漏洞）。
        fn: 假反例数（漏报预期漏洞）。
    """

    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0

    def __add__(self, other: ConfusionMatrix) -> ConfusionMatrix:
        """矩阵逐元素相加，用于聚合多个目标的结果。"""
        return ConfusionMatrix(
            tp=self.tp + other.tp,
            fp=self.fp + other.fp,
            tn=self.tn + other.tn,
            fn=self.fn + other.fn,
        )

    @property
    def total(self) -> int:
        """总评估单元数。"""
        return self.tp + self.fp + self.tn + self.fn

    def to_dict(self) -> dict[str, int]:
        return {"tp": self.tp, "fp": self.fp, "tn": self.tn, "fn": self.fn}


@dataclass
class Metrics:
    """检测指标。

    当分母为 0 时对应指标返回 0.0，避免除零异常。
    """

    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    accuracy: float = 0.0
    fpr: float = 0.0  # 误报率 (False Positive Rate)

    def to_dict(self) -> dict[str, float]:
        return {
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "accuracy": round(self.accuracy, 4),
            "fpr": round(self.fpr, 4),
        }


def compute_metrics(matrix: ConfusionMatrix) -> Metrics:
    """根据混淆矩阵计算检测指标。

    Args:
        matrix: 混淆矩阵。

    Returns:
        包含精确率、召回率、F1、准确率、误报率的 ``Metrics``。
    """
    tp, fp, tn, fn = matrix.tp, matrix.fp, matrix.tn, matrix.fn

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    return Metrics(
        precision=precision,
        recall=recall,
        f1=f1,
        accuracy=accuracy,
        fpr=fpr,
    )


@dataclass
class CheckResult:
    """单个检查点的对比结果。

    Attributes:
        kind: 检查类型 —— ``expected``（预期漏洞）/ ``negative``（负向检查）
            / ``unexpected``（未预期发现）。
        verdict: 判定结果 —— ``TP``/``FP``/``TN``/``FN``。
        vuln_type: 漏洞类型（用于统计）。
        description: 检查点描述。
        severity: 预期严重级别（仅 expected 有意义）。
        finding: 匹配到的 finding（若无则为 ``None``）。
        note: 说明文字。
    """

    kind: str
    verdict: str
    vuln_type: str
    description: str = ""
    severity: str = ""
    finding: dict[str, Any] | None = None
    note: str = ""


@dataclass
class TargetResult:
    """单个靶场目标的基准测试结果。

    Attributes:
        target: 靶场目标定义。
        findings: 扫描引擎实际产出的 findings。
        check_results: 每个检查点的对比结果列表。
        matrix: 该目标的混淆矩阵。
        metrics: 该目标的检测指标。
        duration_ms: 扫描耗时（毫秒）。
        error: 扫描错误信息（无错误时为 ``None``）。
        scanned_at: 扫描时间（ISO 格式）。
    """

    target: BenchmarkTarget
    findings: list[dict[str, Any]] = field(default_factory=list)
    check_results: list[CheckResult] = field(default_factory=list)
    matrix: ConfusionMatrix = field(default_factory=ConfusionMatrix)
    metrics: Metrics = field(default_factory=Metrics)
    duration_ms: int = 0
    error: str | None = None
    scanned_at: str = ""
    ignored_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target.id,
            "target_name": self.target.name,
            "url": self.target.url,
            "category": self.target.category,
            "findings_count": len(self.findings),
            "ignored_count": self.ignored_count,
            "matrix": self.matrix.to_dict(),
            "metrics": self.metrics.to_dict(),
            "duration_ms": self.duration_ms,
            "error": self.error,
            "scanned_at": self.scanned_at,
            "check_results": [
                {
                    "kind": c.kind,
                    "verdict": c.verdict,
                    "vuln_type": c.vuln_type,
                    "description": c.description,
                    "severity": c.severity,
                    "finding_title": (c.finding or {}).get("title", ""),
                    "finding_severity": (c.finding or {}).get("severity", ""),
                    "note": c.note,
                }
                for c in self.check_results
            ],
        }


@dataclass
class BenchmarkReport:
    """完整基准测试报告。

    Attributes:
        targets: 各靶场目标的测试结果。
        matrix: 聚合混淆矩阵。
        metrics: 聚合检测指标。
        generated_at: 报告生成时间（ISO 格式）。
        total_targets: 目标总数。
        successful_targets: 成功扫描的目标数。
    """

    targets: list[TargetResult] = field(default_factory=list)
    matrix: ConfusionMatrix = field(default_factory=ConfusionMatrix)
    metrics: Metrics = field(default_factory=Metrics)
    generated_at: str = ""
    total_targets: int = 0
    successful_targets: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "total_targets": self.total_targets,
            "successful_targets": self.successful_targets,
            "matrix": self.matrix.to_dict(),
            "metrics": self.metrics.to_dict(),
            "targets": [t.to_dict() for t in self.targets],
        }


# ---------------------------------------------------------------------------
# 运行器
# ---------------------------------------------------------------------------


class BenchmarkRunner:
    """基准测试运行器。

    对每个靶场目标执行扫描，对比预期漏洞与实际发现，生成混淆矩阵与指标。

    Args:
        deep: 是否启用深度扫描（启用端点发现与参数 fuzz）。
        scan_timeout: 单目标扫描总超时（秒）。
        request_timeout: 单次 HTTP 请求超时（秒）。
        max_concurrency: 并发扫描目标数。
        scan_func: 自定义扫描函数（用于测试或替换扫描引擎）。
            默认使用 ``app.services.scan_service.run_plugin_scan``。
        targets: 自定义靶场目标列表，默认使用 ``BENCHMARK_TARGETS``。
    """

    def __init__(
        self,
        deep: bool = False,
        scan_timeout: float = 90.0,
        request_timeout: float = 12.0,
        max_concurrency: int = 2,
        scan_func: ScanFunc | None = None,
        targets: list[BenchmarkTarget] | None = None,
    ) -> None:
        self.deep = deep
        self.scan_timeout = scan_timeout
        self.request_timeout = request_timeout
        self.max_concurrency = max(1, max_concurrency)
        self.targets = targets if targets is not None else list(BENCHMARK_TARGETS)
        # 延迟加载默认扫描函数，避免导入期副作用
        self._scan_func = scan_func
        # 本地 httpx 客户端（仅在无法复用项目全局客户端时创建）
        self._local_client: httpx.AsyncClient | None = None
        self._owns_local_client = False
        # TLS 校验：与项目配置保持一致
        self._tls_verify = os.environ.get("TLS_VERIFY", "true").strip().lower() not in (
            "0",
            "false",
            "no",
            "off",
        )

    # ------------------------------------------------------------------
    # HTTP 客户端管理
    # ------------------------------------------------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        """获取 httpx 异步客户端。

        优先复用项目全局客户端 (``main.get_httpx_client``)，无法获取时创建本地客户端。
        """
        try:
            import main as _main  # type: ignore[import-not-found]

            return _main.get_httpx_client()
        except Exception:
            pass

        if self._local_client is None:
            self._local_client = httpx.AsyncClient(
                verify=self._tls_verify,
                timeout=self.request_timeout,
                follow_redirects=True,
            )
            self._owns_local_client = True
        return self._local_client

    async def _close_local_client(self) -> None:
        """关闭本地创建的 httpx 客户端（若存在）。"""
        if self._owns_local_client and self._local_client is not None:
            await self._local_client.aclose()
            self._local_client = None
            self._owns_local_client = False

    # ------------------------------------------------------------------
    # 预扫描上下文采集
    # ------------------------------------------------------------------

    async def _gather_context(
        self, url: str
    ) -> tuple[dict[str, str], bool, dict[str, Any]]:
        """采集目标的预扫描上下文：响应头、是否 HTTPS、SSL 信息。

        Args:
            url: 目标 URL。

        Returns:
            ``(headers, is_https, ssl_info)`` 元组。请求失败时 headers 为空字典。
        """
        is_https = url.lower().startswith("https://")
        headers: dict[str, str] = {}
        client = await self._get_client()
        try:
            resp = await client.get(
                url, timeout=self.request_timeout, follow_redirects=True
            )
            headers = {k: v for k, v in resp.headers.items()}
        except Exception as exc:
            logger.warning("采集 %s 响应头失败: %s", url, exc)

        ssl_info: dict[str, Any] = {}
        if is_https:
            ssl_info = await self._get_ssl_info(url)
        else:
            ssl_info = {"has_cert": False}

        return headers, is_https, ssl_info

    async def _get_ssl_info(self, url: str) -> dict[str, Any]:
        """获取 HTTPS 目标的 SSL 证书信息（简化版）。

        优先复用项目 ``main.get_ssl_info``，否则在线程中执行同步 SSL 握手。
        """
        try:
            import main as _main  # type: ignore[import-not-found]

            parsed = urlparse(url)
            hostname = parsed.hostname or ""
            port = parsed.port or 443
            if hostname:
                return await _main.get_ssl_info(hostname, port)
        except Exception:
            pass

        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        if not hostname:
            return {"has_cert": False}

        def _do_ssl() -> dict[str, Any]:
            try:
                ctx = ssl.create_default_context()
                with socket.create_connection((hostname, 443), timeout=5) as sock:
                    with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert() or {}
                        return {
                            "has_cert": True,
                            "valid": True,
                            "issuer": dict(x[0] for x in cert.get("issuer", [])),
                            "not_after": cert.get("notAfter", ""),
                        }
            except ssl.SSLError as exc:
                return {"has_cert": False, "valid": False, "error": str(exc)}
            except Exception as exc:
                return {"has_cert": False, "valid": False, "error": str(exc)}

        try:
            return await asyncio.to_thread(_do_ssl)
        except Exception:
            return {"has_cert": False}

    # ------------------------------------------------------------------
    # 扫描执行
    # ------------------------------------------------------------------

    async def _default_scan_func(
        self,
        url: str,
        headers: dict[str, str],
        is_https: bool,
        ssl_info: dict[str, Any],
        deep: bool = False,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        """默认扫描函数：调用项目插件化扫描引擎。"""
        from app.services.scan_service import run_plugin_scan

        return await run_plugin_scan(
            url=url,
            headers=headers,
            is_https=is_https,
            ssl_info=ssl_info,
            waf=None,
            deep=deep,
            body="",
            enable_verification=False,  # 基准测试关闭交叉验证以评估原始检出能力
        )

    async def _scan_target(self, target: BenchmarkTarget) -> TargetResult:
        """扫描单个靶场目标并生成对比结果。

        扫描失败时记录错误，findings 为空，所有预期漏洞计为 FN。
        """
        scanned_at = datetime.now(timezone.utc).isoformat()
        start_ts = time.time()
        findings: list[dict[str, Any]] = []
        error: str | None = None

        try:
            headers, is_https, ssl_info = await self._gather_context(target.url)
            scan_func = self._scan_func or self._default_scan_func
            result = await asyncio.wait_for(
                scan_func(
                    url=target.url,
                    headers=headers,
                    is_https=is_https,
                    ssl_info=ssl_info,
                    deep=self.deep,
                ),
                timeout=self.scan_timeout,
            )
            findings = list(result.get("findings") or [])
        except asyncio.TimeoutError:
            error = f"扫描超时（{self.scan_timeout}s）"
            logger.warning("目标 %s 扫描超时", target.id)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            logger.warning("目标 %s 扫描失败: %s", target.id, exc)

        duration_ms = int((time.time() - start_ts) * 1000)
        check_results = self._compare(target, findings)
        matrix = self._tally(check_results)
        metrics = compute_metrics(matrix)
        ignored_count = sum(
            1 for f in findings if self._is_ignored_finding(target, f)
        )

        return TargetResult(
            target=target,
            findings=findings,
            check_results=check_results,
            matrix=matrix,
            metrics=metrics,
            duration_ms=duration_ms,
            error=error,
            scanned_at=scanned_at,
            ignored_count=ignored_count,
        )

    # ------------------------------------------------------------------
    # 对比与混淆矩阵
    # ------------------------------------------------------------------

    @staticmethod
    def _find_match(
        spec: ExpectedVulnerability | NegativeCheck,
        findings: list[dict[str, Any]],
        consumed: set[int],
    ) -> int | None:
        """在未消费的 findings 中查找首个匹配 spec 的索引。"""
        for idx, finding in enumerate(findings):
            if idx in consumed:
                continue
            if spec.matches(finding):
                return idx
        return None

    @staticmethod
    def _is_ignored_finding(target: BenchmarkTarget, finding: dict[str, Any]) -> bool:
        """判断 finding 是否属于目标的范围外类型（ignore_types）。"""
        if not target.ignore_types:
            return False
        f_type = str(finding.get("type", "")).lower()
        return any(f_type == it.lower() for it in target.ignore_types)

    def _compare(
        self, target: BenchmarkTarget, findings: list[dict[str, Any]]
    ) -> list[CheckResult]:
        """将扫描结果与预期漏洞对比，生成检查点结果列表。

        范围外类型 (``ignore_types``) 的 findings 在对比前被排除：既不计入
        正例 (TP/FN)，也不计入误报 (FP)，用于聚焦评估特定漏洞类型。

        匹配流程参见模块文档字符串。
        """
        consumed: set[int] = set()
        results: list[CheckResult] = []

        # 0. 标记范围外 findings 为已消费，使其不参与后续匹配与误报统计
        for idx, finding in enumerate(findings):
            if self._is_ignored_finding(target, finding):
                consumed.add(idx)

        # 1. 正例：预期漏洞
        for exp in target.expected_vulns:
            idx = self._find_match(exp, findings, consumed)
            if idx is not None:
                consumed.add(idx)
                results.append(
                    CheckResult(
                        kind="expected",
                        verdict="TP",
                        vuln_type=exp.vuln_type,
                        description=exp.description,
                        severity=exp.severity,
                        finding=findings[idx],
                        note="正确检出预期漏洞",
                    )
                )
            else:
                results.append(
                    CheckResult(
                        kind="expected",
                        verdict="FN",
                        vuln_type=exp.vuln_type,
                        description=exp.description,
                        severity=exp.severity,
                        finding=None,
                        note="漏报了预期漏洞",
                    )
                )

        # 2. 负例：不应出现的漏洞
        for neg in target.negative_checks:
            idx = self._find_match(neg, findings, consumed)
            if idx is not None:
                consumed.add(idx)
                results.append(
                    CheckResult(
                        kind="negative",
                        verdict="FP",
                        vuln_type=neg.vuln_type,
                        description=neg.description,
                        finding=findings[idx],
                        note="负向检查被违反：报告了不存在的漏洞（误报）",
                    )
                )
            else:
                results.append(
                    CheckResult(
                        kind="negative",
                        verdict="TN",
                        vuln_type=neg.vuln_type,
                        description=neg.description,
                        finding=None,
                        note="正确判定无该漏洞",
                    )
                )

        # 3. 剩余未消费 findings：未预期发现，均计为 FP
        for idx, finding in enumerate(findings):
            if idx in consumed:
                continue
            results.append(
                CheckResult(
                    kind="unexpected",
                    verdict="FP",
                    vuln_type=str(finding.get("type", "unknown")),
                    description=str(finding.get("description", ""))[:200],
                    severity=str(finding.get("severity", "")),
                    finding=finding,
                    note="报告了未预期的漏洞（误报）",
                )
            )

        return results

    @staticmethod
    def _tally(results: list[CheckResult]) -> ConfusionMatrix:
        """统计检查点结果，生成混淆矩阵。"""
        matrix = ConfusionMatrix()
        for r in results:
            if r.verdict == "TP":
                matrix.tp += 1
            elif r.verdict == "FP":
                matrix.fp += 1
            elif r.verdict == "TN":
                matrix.tn += 1
            elif r.verdict == "FN":
                matrix.fn += 1
        return matrix

    # ------------------------------------------------------------------
    # 批量执行
    # ------------------------------------------------------------------

    async def run_all(self) -> BenchmarkReport:
        """对所有靶场目标执行基准测试并生成聚合报告。

        使用信号量限制并发数，逐目标采集结果后聚合混淆矩阵与指标。

        Returns:
            完整的 ``BenchmarkReport``。
        """
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def _bounded_scan(target: BenchmarkTarget) -> TargetResult:
            async with semaphore:
                logger.info("开始基准测试: %s (%s)", target.id, target.url)
                return await self._scan_target(target)

        tasks = [_bounded_scan(t) for t in self.targets]
        target_results = await asyncio.gather(*tasks, return_exceptions=True)

        results: list[TargetResult] = []
        for i, res in enumerate(target_results):
            if isinstance(res, TargetResult):
                results.append(res)
            else:
                # gather 返回异常时构造失败结果
                failed_target = self.targets[i]
                logger.error("目标 %s 执行异常: %s", failed_target.id, res)
                results.append(
                    TargetResult(
                        target=failed_target,
                        error=f"{type(res).__name__}: {res}",
                        scanned_at=datetime.now(timezone.utc).isoformat(),
                    )
                )

        # 聚合混淆矩阵
        agg_matrix = ConfusionMatrix()
        for tr in results:
            agg_matrix = agg_matrix + tr.matrix

        successful = sum(1 for tr in results if tr.error is None)

        report = BenchmarkReport(
            targets=results,
            matrix=agg_matrix,
            metrics=compute_metrics(agg_matrix),
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_targets=len(self.targets),
            successful_targets=successful,
        )

        await self._close_local_client()
        return report
