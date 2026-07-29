"""Finding 去重与关联引擎。

对扫描产出的 finding 列表进行去重、合并、关联与排序，减少重复报告并
识别同源漏洞簇，提升结果可读性与可信度。

核心能力:
    1. 指纹去重：以 (漏洞类型, 规范化 URL, 参数, 严重度) 作为指纹，
       合并重复 finding，保留最高置信度项并聚合证据。
    2. 关联分析：按 URL 聚簇，为同一 URL 下的多个 finding 标注关联组。
    3. 结果排序：按严重度（critical > high > medium > low > info），
       再按置信度（high > medium > low）稳定排序。
    4. 统计追踪：记录原始数量、去重后数量、重复数量、关联组数量及分类型计数。

使用方式:
    from app.dedup import FindingDeduplicator

    deduper = FindingDeduplicator()
    merged, stats = deduper.deduplicate(findings)
    print(stats.to_dict())
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
from urllib.parse import urlsplit, urlunsplit

__all__ = ["FindingDeduplicator", "DedupStats", "deduplicate_findings"]


# 严重度排序权重：数值越小优先级越高
SEVERITY_ORDER: Dict[str, int] = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}

# 置信度排序权重：数值越小优先级越高
CONFIDENCE_ORDER: Dict[str, int] = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


@dataclass
class DedupStats:
    """去重与关联统计结果。

    字段说明:
        original_count: 输入的原始 finding 数量
        deduplicated_count: 去重合并后的 finding 数量
        duplicate_count: 被合并掉的重复 finding 数量（original - deduplicated）
        correlation_groups: 关联组数量（同一 URL 下存在 2 个及以上 finding 的簇）
        by_type: 去重后按漏洞类型统计的计数
    """

    original_count: int = 0
    deduplicated_count: int = 0
    duplicate_count: int = 0
    correlation_groups: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，便于序列化与日志输出。"""
        return {
            "original_count": self.original_count,
            "deduplicated_count": self.deduplicated_count,
            "duplicate_count": self.duplicate_count,
            "correlation_groups": self.correlation_groups,
            "by_type": dict(self.by_type),
        }


class FindingDeduplicator:
    """Finding 去重与关联引擎。

    工作流程（deduplicate 主入口）:
        1. 计算指纹 -> 按指纹分组
        2. 合并同组 finding（保留最高置信度，聚合证据）
        3. 按 URL 关联聚簇，标注 correlation_group
        4. 按严重度 + 置信度排序
        5. 汇总统计

    设计原则:
        - 无副作用：输入列表与其中字典均不被修改，内部统一浅拷贝。
        - 向后兼容：合并后的 finding 保留原始字段结构，仅追加聚合字段。
        - 稳定排序：同优先级下保持原始相对顺序。
    """

    def __init__(
        self,
        severity_order: Dict[str, int] = SEVERITY_ORDER,
        confidence_order: Dict[str, int] = CONFIDENCE_ORDER,
    ) -> None:
        """
        Args:
            severity_order: 严重度排序权重表，可由外部覆盖。
            confidence_order: 置信度排序权重表，可由外部覆盖。
        """
        self._severity_order = dict(severity_order)
        self._confidence_order = dict(confidence_order)

    # ------------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------------
    def deduplicate(
        self, findings: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], DedupStats]:
        """对 finding 列表执行去重、合并、关联与排序。

        Args:
            findings: 原始 finding 字典列表（兼容 scan_service 的字典格式）

        Returns:
            (merged_findings, stats)：
            - merged_findings: 去重合并、关联标注并排序后的 finding 列表
            - stats: DedupStats 统计信息
        """
        original_count = len(findings)

        # 1. 按指纹分组
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for finding in findings:
            fingerprint = self._compute_fingerprint(finding)
            groups.setdefault(fingerprint, []).append(finding)

        # 2. 合并每组重复 finding
        merged: List[Dict[str, Any]] = [
            self._merge_findings(group) for group in groups.values()
        ]

        # 3. 关联分析（按 URL 聚簇并标注关联组）
        merged = self.correlate(merged)

        # 4. 排序（严重度 -> 置信度）
        merged = self._sort_findings(merged)

        # 5. 统计
        by_type: Dict[str, int] = {}
        for finding in merged:
            vuln_type = (finding.get("type") or "unknown").lower()
            by_type[vuln_type] = by_type.get(vuln_type, 0) + 1

        correlation_group_ids = {
            finding.get("correlation_group")
            for finding in merged
            if finding.get("correlation_group")
        }

        stats = DedupStats(
            original_count=original_count,
            deduplicated_count=len(merged),
            duplicate_count=max(0, original_count - len(merged)),
            correlation_groups=len(correlation_group_ids),
            by_type=by_type,
        )
        return merged, stats

    # ------------------------------------------------------------------
    # 指纹与合并
    # ------------------------------------------------------------------
    def _compute_fingerprint(self, finding: Dict[str, Any]) -> str:
        """计算 finding 的去重指纹。

        指纹由 (漏洞类型, 规范化 URL, 参数, 严重度) 四元组构成，
        四元组完全一致即视为同一漏洞的重复报告。

        Args:
            finding: finding 字典

        Returns:
            形如 ``sqli|http://example.com/login|username|high`` 的指纹字符串
        """
        vuln_type = (finding.get("type") or "unknown").strip().lower()
        normalized_url = self._normalize_url(finding.get("url") or "")
        parameter = (finding.get("parameter") or "").strip().lower()
        severity = (finding.get("severity") or "info").strip().lower()
        return f"{vuln_type}|{normalized_url}|{parameter}|{severity}"

    def _merge_findings(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并一组重复 finding。

        合并策略:
            - 以最高置信度的 finding 作为基准（同优先级取组内首个，保持稳定）。
            - 聚合所有 finding 的 payload / 命中签名 / 备注为列表（去重保序）。
            - 记录被合并的 finding id 列表与合并数量。

        Args:
            findings: 同一指纹下的 finding 列表

        Returns:
            合并后的 finding 字典（追加 merged_count、duplicate_ids 及
            evidence.payloads / evidence.matched_signatures / evidence.notes_list 字段）
        """
        if len(findings) == 1:
            return dict(findings[0])

        # 按置信度排序取最高（稳定排序保持原序作为平局打破）
        ordered = sorted(
            findings,
            key=lambda f: self._confidence_rank(self._extract_confidence(f)),
        )
        base = dict(ordered[0])

        payloads: List[str] = []
        signatures: List[str] = []
        notes: List[str] = []
        duplicate_ids: List[str] = []

        for finding in findings:
            evidence = finding.get("evidence") or {}
            if not isinstance(evidence, dict):
                evidence = {}

            payload = evidence.get("payload") or ""
            signature = evidence.get("matched_signature") or ""
            note = evidence.get("notes") or ""

            if payload and payload not in payloads:
                payloads.append(payload)
            if signature and signature not in signatures:
                signatures.append(signature)
            if note and note not in notes:
                notes.append(note)

            finding_id = finding.get("id") or ""
            if finding_id and finding_id not in duplicate_ids:
                duplicate_ids.append(finding_id)

        # 聚合证据：保留基准字段以兼容旧消费方，同时追加列表形式
        merged_evidence = dict(base.get("evidence") or {})
        if not isinstance(merged_evidence, dict):
            merged_evidence = {}
        merged_evidence["payloads"] = payloads
        merged_evidence["matched_signatures"] = signatures
        merged_evidence["notes_list"] = notes
        base["evidence"] = merged_evidence

        base["merged_count"] = len(findings)
        base["duplicate_ids"] = duplicate_ids
        return base

    # ------------------------------------------------------------------
    # 关联分析
    # ------------------------------------------------------------------
    def correlate(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按 URL 关联聚簇，为同源 finding 标注关联组。

        规则: 以规范化 URL 作为聚簇键，同一 URL 下存在 2 个及以上 finding
        时视为一个关联组，为组内每个 finding 写入:
            - correlation_group: 关联组标识（CG-XXXXXXXX）
            - correlation_size: 关联组内 finding 数量

        Args:
            findings: finding 字典列表

        Returns:
            带关联组标注的 finding 列表（浅拷贝，不修改输入）
        """
        if not findings:
            return []

        url_groups: Dict[str, List[int]] = {}
        for idx, finding in enumerate(findings):
            normalized_url = self._normalize_url(finding.get("url") or "")
            if not normalized_url:
                continue
            url_groups.setdefault(normalized_url, []).append(idx)

        result: List[Dict[str, Any]] = [dict(finding) for finding in findings]
        for normalized_url, indices in url_groups.items():
            if len(indices) < 2:
                # 单一 finding 不构成关联，跳过
                continue
            group_id = self._build_group_id(normalized_url)
            for idx in indices:
                result[idx]["correlation_group"] = group_id
                result[idx]["correlation_size"] = len(indices)

        return result

    # ------------------------------------------------------------------
    # URL 规范化
    # ------------------------------------------------------------------
    def _normalize_url(self, url: str) -> str:
        """规范化 URL 用于比对。

        处理步骤:
            - 去除首尾空白
            - 补全缺失的 scheme 以便正确解析 netloc
            - scheme 与 host 统一小写
            - 去除 query 参数与 fragment
            - 去除末尾斜杠

        Args:
            url: 原始 URL

        Returns:
            规范化后的 URL，例如
            ``HTTPS://Example.com/a/b?x=1#top`` -> ``https://example.com/a/b``
        """
        if not url:
            return ""

        url = url.strip()
        if not url:
            return ""

        # 缺失 scheme 时补全，确保 netloc 能被正确解析
        if "://" not in url:
            url = "http://" + url

        try:
            parts = urlsplit(url)
        except ValueError:
            # 解析失败的兜底：手动裁剪 query 并小写
            return url.lower().split("?", 1)[0].split("#", 1)[0].rstrip("/")

        scheme = parts.scheme.lower()
        netloc = parts.netloc.lower()
        path = parts.path.rstrip("/")

        normalized = urlunsplit((scheme, netloc, path, "", ""))
        return normalized

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    def _sort_findings(
        self, findings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """按严重度（升优先级）再按置信度（升优先级）稳定排序。"""
        return sorted(
            findings,
            key=lambda f: (
                self._severity_rank(f.get("severity") or "info"),
                self._confidence_rank(self._extract_confidence(f)),
            ),
        )

    def _severity_rank(self, severity: str) -> int:
        """获取严重度排序权重，未知值降级为最低优先级。"""
        return self._severity_order.get((severity or "").strip().lower(), len(self._severity_order))

    def _confidence_rank(self, confidence: str) -> int:
        """获取置信度排序权重，未知值降级为 medium。"""
        return self._confidence_order.get((confidence or "").strip().lower(), 1)

    @staticmethod
    def _extract_confidence(finding: Dict[str, Any]) -> str:
        """从 finding 中提取置信度，兼容 confidence / confidence_level 字段。"""
        return (
            finding.get("confidence")
            or finding.get("confidence_level")
            or "medium"
        )

    @staticmethod
    def _build_group_id(normalized_url: str) -> str:
        """基于规范化 URL 生成稳定的关联组标识。"""
        digest = hashlib.md5(normalized_url.encode("utf-8")).hexdigest()[:8].upper()
        return f"CG-{digest}"


def deduplicate_findings(
    findings: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], DedupStats]:
    """便捷函数：使用默认配置对 finding 列表执行去重与关联。

    Args:
        findings: 原始 finding 字典列表

    Returns:
        (merged_findings, stats)
    """
    deduper = FindingDeduplicator()
    return deduper.deduplicate(findings)
