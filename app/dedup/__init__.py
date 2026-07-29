"""Finding 去重与关联模块。

提供 Finding 去重、合并、关联聚簇与排序能力，用于精简扫描结果、
识别同源漏洞簇。

使用方式:
    from app.dedup import FindingDeduplicator, DedupStats

    deduper = FindingDeduplicator()
    merged, stats = deduper.deduplicate(findings)
"""

from app.dedup.finding_dedup import (
    CONFIDENCE_ORDER,
    SEVERITY_ORDER,
    DedupStats,
    FindingDeduplicator,
    deduplicate_findings,
)

__all__ = [
    "FindingDeduplicator",
    "DedupStats",
    "deduplicate_findings",
    "SEVERITY_ORDER",
    "CONFIDENCE_ORDER",
]
