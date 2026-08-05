"""复测验证引擎。

对比修复前后两次扫描结果，生成结构化 diff 报告，支撑修复闭环验证。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FindingSignature:
    """用于对比 finding 的签名（忽略状态、时间等可变字段）。"""

    vuln_type: str
    location_key: str  # url + parameter 组合
    severity: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FindingSignature:
        return cls(
            vuln_type=(data.get("type") or data.get("vuln_type") or "unknown").lower(),
            location_key=_location_key(data),
            severity=(data.get("severity") or "low").lower(),
        )

    def __hash__(self) -> int:
        return hash((self.vuln_type, self.location_key, self.severity))


def _location_key(data: dict[str, Any]) -> str:
    """从 finding 中提取位置标识用于对比。"""
    url = data.get("url") or ""
    param = data.get("parameter") or ""
    loc = data.get("location") or ""
    loc_detail = data.get("location_detail") or {}
    if isinstance(loc_detail, dict):
        url = loc_detail.get("url") or url
        param = loc_detail.get("parameter") or param
    parts = [p for p in [url, param, loc] if p]
    return "|".join(parts) if parts else "unknown"


@dataclass
class FindingChange:
    """单个 finding 的变化记录。"""

    change_type: str  # eliminated / new / retained / severity_changed
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    severity_delta: str | None = None  # e.g. "high -> medium"
    notes: str = ""


@dataclass
class DiffResult:
    """修复前后扫描结果对比报告。"""

    before_scan_id: int | None = None
    after_scan_id: int | None = None
    before_score: int = 0
    after_score: int = 0
    score_delta: int = 0

    eliminated: list[FindingChange] = field(default_factory=list)
    new_findings: list[FindingChange] = field(default_factory=list)
    retained: list[FindingChange] = field(default_factory=list)
    severity_changed: list[FindingChange] = field(default_factory=list)

    summary: dict[str, Any] = field(default_factory=dict)

    def is_verified_fixed(
        self, target_finding_names: list[str] | None = None
    ) -> bool:
        """判断目标漏洞是否已被修复。

        如果提供了 target_finding_names，则检查这些特定漏洞是否已消除；
        否则检查整体评分是否有显著提升且高危漏洞减少。
        """
        if target_finding_names:
            eliminated_names = {
                (c.before or {}).get("name", "") or (c.before or {}).get("title", "")
                for c in self.eliminated
            }
            return all(name in eliminated_names for name in target_finding_names)
        # 默认：评分提升超过 20 分且高危漏洞减少
        return self.score_delta >= 20 and len(self.eliminated) > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "before_scan_id": self.before_scan_id,
            "after_scan_id": self.after_scan_id,
            "before_score": self.before_score,
            "after_score": self.after_score,
            "score_delta": self.score_delta,
            "eliminated": [
                {
                    "change_type": c.change_type,
                    "finding": c.before,
                    "notes": c.notes,
                }
                for c in self.eliminated
            ],
            "new_findings": [
                {
                    "change_type": c.change_type,
                    "finding": c.after,
                    "notes": c.notes,
                }
                for c in self.new_findings
            ],
            "retained": [
                {
                    "change_type": c.change_type,
                    "finding": c.after or c.before,
                    "notes": c.notes,
                }
                for c in self.retained
            ],
            "severity_changed": [
                {
                    "change_type": c.change_type,
                    "before": c.before,
                    "after": c.after,
                    "severity_delta": c.severity_delta,
                    "notes": c.notes,
                }
                for c in self.severity_changed
            ],
            "summary": self.summary,
            "verified_fixed": self.is_verified_fixed(),
        }


class ScanDiffEngine:
    """扫描结果对比引擎。"""

    SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

    @classmethod
    def compare(
        cls,
        before_findings: list[dict[str, Any]],
        after_findings: list[dict[str, Any]],
        before_scan_id: int | None = None,
        after_scan_id: int | None = None,
        before_score: int = 0,
        after_score: int = 0,
    ) -> DiffResult:
        """对比两次扫描结果，生成 diff 报告。"""
        before_map: dict[FindingSignature, dict[str, Any]] = {}
        after_map: dict[FindingSignature, dict[str, Any]] = {}

        for f in before_findings:
            sig = FindingSignature.from_dict(f)
            before_map[sig] = f

        for f in after_findings:
            sig = FindingSignature.from_dict(f)
            after_map[sig] = f

        before_sigs: set[FindingSignature] = set(before_map.keys())
        after_sigs: set[FindingSignature] = set(after_map.keys())

        eliminated_sigs = before_sigs - after_sigs
        new_sigs = after_sigs - before_sigs
        common_sigs = before_sigs & after_sigs

        result = DiffResult(
            before_scan_id=before_scan_id,
            after_scan_id=after_scan_id,
            before_score=before_score,
            after_score=after_score,
            score_delta=after_score - before_score,
        )

        # 已消除
        for sig in eliminated_sigs:
            result.eliminated.append(
                FindingChange(
                    change_type="eliminated",
                    before=before_map[sig],
                    notes="该漏洞在复测中已不再出现",
                )
            )

        # 新增
        for sig in new_sigs:
            result.new_findings.append(
                FindingChange(
                    change_type="new",
                    after=after_map[sig],
                    notes="复测中发现了新的漏洞",
                )
            )

        # 保留（可能 severity 变化）
        for sig in common_sigs:
            before_f = before_map[sig]
            after_f = after_map[sig]
            before_sev = (before_f.get("severity") or "low").lower()
            after_sev = (after_f.get("severity") or "low").lower()

            if before_sev != after_sev:
                delta = f"{before_sev} -> {after_sev}"
                better = cls.SEVERITY_ORDER.get(after_sev, 99) > cls.SEVERITY_ORDER.get(
                    before_sev, 99
                )
                result.severity_changed.append(
                    FindingChange(
                        change_type="severity_changed",
                        before=before_f,
                        after=after_f,
                        severity_delta=delta,
                        notes=f"严重度变化：{delta}（{'改善' if better else '恶化'}）",
                    )
                )
            else:
                result.retained.append(
                    FindingChange(
                        change_type="retained",
                        before=before_f,
                        after=after_f,
                        notes="漏洞仍存在，未发生变化",
                    )
                )

        # 汇总统计
        total_before_high = sum(
            1
            for f in before_findings
            if (f.get("severity") or "").lower() in ("high", "critical")
        )
        total_after_high = sum(
            1
            for f in after_findings
            if (f.get("severity") or "").lower() in ("high", "critical")
        )

        result.summary = {
            "total_before": len(before_findings),
            "total_after": len(after_findings),
            "eliminated_count": len(result.eliminated),
            "new_count": len(result.new_findings),
            "retained_count": len(result.retained),
            "severity_changed_count": len(result.severity_changed),
            "high_critical_before": total_before_high,
            "high_critical_after": total_after_high,
            "high_critical_delta": total_after_high - total_before_high,
            "score_improved": result.score_delta > 0,
            "risk_level_changed": cls._risk_level(before_score)
            != cls._risk_level(after_score),
        }

        return result

    @classmethod
    def _risk_level(cls, score: int) -> str:
        if score < 40:
            return "critical"
        if score < 60:
            return "high"
        if score < 80:
            return "medium"
        return "low"

    @classmethod
    def compare_scans(
        cls,
        before_scan: dict[str, Any],
        after_scan: dict[str, Any],
    ) -> DiffResult:
        """直接对比两次完整扫描结果字典。"""
        return cls.compare(
            before_findings=before_scan.get("findings") or [],
            after_findings=after_scan.get("findings") or [],
            before_scan_id=before_scan.get("scan_id"),
            after_scan_id=after_scan.get("scan_id"),
            before_score=before_scan.get("score") or 0,
            after_score=after_scan.get("score") or 0,
        )
