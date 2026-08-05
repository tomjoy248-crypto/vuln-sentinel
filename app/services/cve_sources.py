"""多源 CVE 情报适配器。

统一接口聚合 NVD、本地缓存以及可扩展的第三方 CVE 源，
为扫描结果提供更稳定的漏洞情报支撑。
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

from app.services import vuln_intel_service

logger = logging.getLogger("vuln_sentinel.cve_sources")


class CVESource(ABC):
    """CVE 情报源抽象基类。"""

    name: str = ""

    @abstractmethod
    async def fetch_cve(self, cve_id: str) -> dict[str, Any] | None:
        """查询单个 CVE。"""
        ...

    @abstractmethod
    async def search(
        self, keyword: str, limit: int = 20
    ) -> tuple[list[dict[str, Any]], int]:
        """关键词搜索 CVE，返回 (records, total)。"""
        ...


class NVDSource(CVESource):
    """NVD 官方源。"""

    name = "nvd"

    async def fetch_cve(self, cve_id: str) -> dict[str, Any] | None:
        return await vuln_intel_service.fetch_nvd_cve(cve_id)

    async def search(
        self, keyword: str, limit: int = 20
    ) -> tuple[list[dict[str, Any]], int]:
        return await vuln_intel_service.search_nvd_cves(keyword, results_per_page=limit)


class LocalCacheSource(CVESource):
    """本地 SQLite 缓存源。"""

    name = "local_cache"

    async def fetch_cve(self, cve_id: str) -> dict[str, Any] | None:
        return vuln_intel_service.get_cve_from_cache(cve_id)

    async def search(
        self, keyword: str, limit: int = 20
    ) -> tuple[list[dict[str, Any]], int]:
        records = vuln_intel_service.search_cve_cache(keyword, limit=limit)
        return records, len(records)


class CIRCLSource(CVESource):
    """CIRCL CVE 搜索（无需 API Key，作为 NVD 备用）。"""

    name = "circl"
    _base_url = "https://cve.circl.lu/api"

    async def fetch_cve(self, cve_id: str) -> dict[str, Any] | None:
        import httpx

        cve_id = (cve_id or "").strip().upper()
        if not cve_id.startswith("CVE-"):
            return None
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
                resp = await client.get(f"{self._base_url}/cve/{cve_id}")
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                data = resp.json()
                return self._normalize(data)
        except Exception as e:
            logger.debug("CIRCL fetch %s failed: %s", cve_id, e)
            return None

    async def search(
        self, keyword: str, limit: int = 20
    ) -> tuple[list[dict[str, Any]], int]:
        import httpx

        keyword = (keyword or "").strip()
        if not keyword:
            return [], 0
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
                resp = await client.get(
                    f"{self._base_url}/search/{keyword}",
                    params={"limit": min(limit, 100)},
                )
                if resp.status_code == 404:
                    return [], 0
                resp.raise_for_status()
                data = resp.json()
                items = data if isinstance(data, list) else data.get("results", [])
                records = [r for r in (self._normalize(i) for i in items) if r]
                return records[:limit], len(records)
        except Exception as e:
            logger.debug("CIRCL search %s failed: %s", keyword, e)
            return [], 0

    def _normalize(self, data: dict[str, Any]) -> dict[str, Any] | None:
        cve_id = data.get("id", "")
        if not cve_id.startswith("CVE-"):
            return None
        summary = data.get("summary", "") or data.get("description", "")
        return {
            "cve_id": cve_id,
            "description": summary,
            "severity": (data.get("severity") or "unknown").lower(),
            "cvss_score": data.get("cvss") or 0.0,
            "cvss_vector": "",
            "published_date": data.get("Published", ""),
            "last_modified_date": data.get("Modified", ""),
            "references": data.get("references", []),
            "cpe_matches": [],
            "source": "circl",
        }


class CVEAggregator:
    """CVE 情报聚合器：优先本地缓存，未命中再请求外部源。"""

    def __init__(self) -> None:
        self.sources: list[CVESource] = [
            LocalCacheSource(),
            NVDSource(),
            CIRCLSource(),
        ]

    async def fetch_cve(self, cve_id: str) -> dict[str, Any] | None:
        """按优先级查询单个 CVE。"""
        for source in self.sources:
            try:
                record = await source.fetch_cve(cve_id)
                if record:
                    record["source"] = source.name
                    return record
            except Exception as e:
                logger.debug("Source %s fetch %s failed: %s", source.name, cve_id, e)
        return None

    async def search(
        self, keyword: str, limit: int = 20
    ) -> tuple[list[dict[str, Any]], int]:
        """优先搜索本地缓存；未命中再请求外部源。"""
        local = self.sources[0]
        records, total = await local.search(keyword, limit=limit)
        if records:
            for r in records:
                r["source"] = local.name
            return records, total

        # 本地未命中，并行请求外部源
        external_sources = self.sources[1:]
        tasks = [s.search(keyword, limit=limit) for s in external_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        merged: list[dict[str, Any]] = []
        seen: set = set()
        for source, res in zip(external_sources, results):
            if isinstance(res, Exception):
                logger.debug("Source %s search failed: %s", source.name, res)
                continue
            recs, _ = res
            for r in recs:
                if r["cve_id"] in seen:
                    continue
                seen.add(r["cve_id"])
                r["source"] = source.name
                merged.append(r)

        return merged[:limit], len(merged)


# 全局聚合器实例
_aggregator: CVEAggregator | None = None


def get_aggregator() -> CVEAggregator:
    """获取全局 CVE 聚合器。"""
    global _aggregator
    if _aggregator is None:
        _aggregator = CVEAggregator()
    return _aggregator
