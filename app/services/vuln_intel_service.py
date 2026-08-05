"""漏洞情报服务：接入 NVD (National Vulnerability Database) 真实 CVE 数据源。

提供：
- 单个 CVE 查询（带本地 SQLite 缓存）
- 关键词搜索 CVE
- 增量同步最近公开的 CVE
- 与扫描结果中的 outdated_component finding 关联

NVD API 文档：https://nvd.nist.gov/developers/vulnerabilities
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.db.session import get_db_connection

logger = logging.getLogger("vuln_sentinel.intel")

NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_API_KEY = ""

# NVD 建议未认证请求间隔 6 秒；API Key 可提高到 0.6 秒
NVD_REQUEST_INTERVAL_SECONDS = 6.0

# 最近一次 NVD 请求时间戳（进程内限流）
_last_nvd_request_at: float = 0.0
_last_nvd_lock = asyncio.Lock()


def _init_cve_table(conn: sqlite3.Connection) -> None:
    """初始化 CVE 缓存表与组件索引表。"""
    conn.execute(
        """CREATE TABLE IF NOT EXISTS cve_records (
            cve_id TEXT PRIMARY KEY,
            description TEXT,
            severity TEXT,
            cvss_score REAL,
            cvss_vector TEXT,
            published_date TEXT,
            last_modified_date TEXT,
            references_json TEXT DEFAULT '[]',
            cpe_matches_json TEXT DEFAULT '[]',
            fetched_at TEXT
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_cve_records_severity ON cve_records(severity)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_cve_records_published ON cve_records(published_date)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_cve_records_fetched_at ON cve_records(fetched_at)"
    )

    # 组件级 CVE 索引：加速按组件名/版本的关联查询
    conn.execute(
        """CREATE TABLE IF NOT EXISTS cve_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cve_id TEXT NOT NULL,
            vendor TEXT DEFAULT '',
            product TEXT NOT NULL,
            version_start TEXT DEFAULT '',
            version_end TEXT DEFAULT '',
            UNIQUE(cve_id, product)
        )"""
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_cve_components_product ON cve_components(product)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_cve_components_cve_id ON cve_components(cve_id)"
    )
    conn.commit()


def ensure_cve_table() -> None:
    """确保 CVE 表存在（供 main.py 启动时调用）。"""
    try:
        with get_db_connection() as conn:
            _init_cve_table(conn)
    except Exception as e:
        logger.warning("CVE table initialization failed: %s", e)


async def _rate_limited_nvd_request(
    client: httpx.AsyncClient, url: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """带进程内限流的 NVD 请求。"""
    global _last_nvd_request_at
    async with _last_nvd_lock:
        elapsed = asyncio.get_event_loop().time() - _last_nvd_request_at
        if elapsed < NVD_REQUEST_INTERVAL_SECONDS:
            await asyncio.sleep(NVD_REQUEST_INTERVAL_SECONDS - elapsed)
        try:
            resp = await client.get(url, params=params, timeout=30.0)
            _last_nvd_request_at = asyncio.get_event_loop().time()
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.warning(
                "NVD API error: %s %s", e.response.status_code, e.response.text[:200]
            )
            raise
        except Exception as e:
            logger.warning("NVD request failed: %s", e)
            raise


def _parse_cve_item(item: dict[str, Any]) -> dict[str, Any] | None:
    """从 NVD API 返回的 vulnerabilities[].cve 解析标准化记录。"""
    cve_data = item.get("cve") or item
    cve_id = cve_data.get("id", "")
    if not cve_id or not cve_id.startswith("CVE-"):
        return None

    descriptions = cve_data.get("descriptions", [])
    description = ""
    for d in descriptions:
        if d.get("lang") == "en":
            description = d.get("value", "")
            break
    if not description and descriptions:
        description = descriptions[0].get("value", "")

    metrics = cve_data.get("metrics", {})
    severity = "unknown"
    cvss_score: float | None = None
    cvss_vector = ""
    # 优先 CVSS v3
    for metric_key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        metric_list = metrics.get(metric_key)
        if metric_list:
            cvss_data = metric_list[0].get("cvssData", {})
            severity = (
                metric_list[0].get("baseSeverity")
                or cvss_data.get("baseSeverity")
                or severity
            ).lower()
            cvss_score = cvss_data.get("baseScore")
            cvss_vector = cvss_data.get("vectorString", "")
            break

    references = []
    for ref in cve_data.get("references", []):
        references.append(
            {
                "url": ref.get("url", ""),
                "source": ref.get("source", ""),
                "tags": ref.get("tags", []),
            }
        )

    cpe_matches = []
    for config in cve_data.get("configurations", []):
        for node in config.get("nodes", []):
            for match in node.get("cpeMatch", []):
                cpe_matches.append(
                    {
                        "criteria": match.get("criteria", ""),
                        "vulnerable": match.get("vulnerable", False),
                        "version_start": match.get("versionStartIncluding", ""),
                        "version_end": match.get("versionEndExcluding", ""),
                    }
                )

    return {
        "cve_id": cve_id,
        "description": description,
        "severity": severity,
        "cvss_score": cvss_score or 0.0,
        "cvss_vector": cvss_vector,
        "published_date": cve_data.get("published", ""),
        "last_modified_date": cve_data.get("lastModified", ""),
        "references_json": json.dumps(references, ensure_ascii=False),
        "cpe_matches_json": json.dumps(cpe_matches, ensure_ascii=False),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _parse_cpe_product(criteria: str) -> tuple[str, str]:
    """从 CPE 2.3 criteria 中解析 vendor:product。"""
    try:
        parts = criteria.split(":")
        if len(parts) >= 5 and parts[0] == "cpe":
            return parts[3], parts[4]
    except Exception:
        pass
    return "", ""


def _save_cve_records(records: list[dict[str, Any]]) -> int:
    """批量保存 CVE 记录到本地缓存，并维护组件索引。"""
    if not records:
        return 0
    with get_db_connection() as conn:
        _init_cve_table(conn)
        inserted = 0
        for rec in records:
            try:
                conn.execute(
                    """INSERT INTO cve_records
                    (cve_id, description, severity, cvss_score, cvss_vector,
                     published_date, last_modified_date, references_json, cpe_matches_json, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(cve_id) DO UPDATE SET
                        description=excluded.description,
                        severity=excluded.severity,
                        cvss_score=excluded.cvss_score,
                        cvss_vector=excluded.cvss_vector,
                        published_date=excluded.published_date,
                        last_modified_date=excluded.last_modified_date,
                        references_json=excluded.references_json,
                        cpe_matches_json=excluded.cpe_matches_json,
                        fetched_at=excluded.fetched_at""",
                    (
                        rec["cve_id"],
                        rec["description"],
                        rec["severity"],
                        rec["cvss_score"],
                        rec["cvss_vector"],
                        rec["published_date"],
                        rec["last_modified_date"],
                        rec["references_json"],
                        rec["cpe_matches_json"],
                        rec["fetched_at"],
                    ),
                )
                # 维护组件索引
                cpe_matches = json.loads(rec.get("cpe_matches_json") or "[]")
                for match in cpe_matches:
                    criteria = match.get("criteria", "")
                    vendor, product = _parse_cpe_product(criteria)
                    if product:
                        conn.execute(
                            """INSERT OR IGNORE INTO cve_components
                            (cve_id, vendor, product, version_start, version_end)
                            VALUES (?, ?, ?, ?, ?)""",
                            (
                                rec["cve_id"],
                                vendor,
                                product,
                                match.get("version_start", ""),
                                match.get("version_end", ""),
                            ),
                        )
                inserted += 1
            except Exception as e:
                logger.debug("Save CVE %s failed: %s", rec.get("cve_id"), e)
        conn.commit()
    return inserted


def _record_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """将数据库行转换为字典。"""
    return {
        "cve_id": row["cve_id"],
        "description": row["description"],
        "severity": row["severity"],
        "cvss_score": row["cvss_score"],
        "cvss_vector": row["cvss_vector"],
        "published_date": row["published_date"],
        "last_modified_date": row["last_modified_date"],
        "references": json.loads(row["references_json"] or "[]"),
        "cpe_matches": json.loads(row["cpe_matches_json"] or "[]"),
        "fetched_at": row["fetched_at"],
    }


async def fetch_nvd_cve(cve_id: str) -> dict[str, Any] | None:
    """从 NVD 获取单个 CVE 并缓存。

    返回标准化字典，失败时返回 None。
    """
    cve_id = (cve_id or "").strip().upper()
    if not re.fullmatch(r"CVE-\d{4}-\d+", cve_id):
        return None

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            data = await _rate_limited_nvd_request(
                client, NVD_BASE_URL, params={"cveId": cve_id}
            )
    except Exception:
        return None

    items = data.get("vulnerabilities", [])
    if not items:
        return None

    record = _parse_cve_item(items[0])
    if record:
        _save_cve_records([record])
    return record


async def search_nvd_cves(
    keyword: str,
    results_per_page: int = 20,
    start_index: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    """通过关键词搜索 NVD CVE。

    返回 (records, total_results)。
    """
    keyword = (keyword or "").strip()
    if not keyword:
        return [], 0

    params: dict[str, Any] = {
        "keywordSearch": keyword,
        "resultsPerPage": min(max(results_per_page, 1), 100),
        "startIndex": max(start_index, 0),
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            data = await _rate_limited_nvd_request(client, NVD_BASE_URL, params=params)
    except Exception:
        return [], 0

    items = data.get("vulnerabilities", [])
    total = data.get("totalResults", len(items))
    records = [r for r in (_parse_cve_item(i) for i in items) if r]
    if records:
        _save_cve_records(records)
    return records, total


async def sync_recent_nvd_cves(days: int = 30) -> tuple[int, int]:
    """增量同步最近 N 天的 NVD CVE。

    返回 (saved_count, total_count)。
    """
    start_dt = datetime.now(timezone.utc) - timedelta(days=max(1, days))
    start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S.000")

    total_saved = 0
    total_fetched = 0
    start_index = 0
    page_size = 100

    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        while True:
            params = {
                "lastModStartDate": start_str,
                "lastModEndDate": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.000"
                ),
                "resultsPerPage": page_size,
                "startIndex": start_index,
            }
            try:
                data = await _rate_limited_nvd_request(
                    client, NVD_BASE_URL, params=params
                )
            except Exception:
                break

            items = data.get("vulnerabilities", [])
            total = data.get("totalResults", 0)
            if not items:
                break

            records = [r for r in (_parse_cve_item(i) for i in items) if r]
            saved = _save_cve_records(records)
            total_saved += saved
            total_fetched += len(items)

            start_index += len(items)
            if start_index >= total:
                break

    logger.info(
        "NVD sync complete: %d fetched, %d saved/updated", total_fetched, total_saved
    )
    return total_saved, total_fetched


def get_cve_from_cache(cve_id: str) -> dict[str, Any] | None:
    """从本地缓存查询 CVE。"""
    cve_id = (cve_id or "").strip().upper()
    if not cve_id:
        return None
    try:
        with get_db_connection() as conn:
            _init_cve_table(conn)
            row = conn.execute(
                "SELECT * FROM cve_records WHERE cve_id = ?", (cve_id,)
            ).fetchone()
            if row:
                return _record_to_dict(row)
    except Exception as e:
        logger.warning("Query CVE cache failed: %s", e)
    return None


def search_cve_cache(keyword: str, limit: int = 20) -> list[dict[str, Any]]:
    """在本地缓存中搜索 CVE。"""
    keyword = (keyword or "").strip()
    if not keyword:
        return []
    try:
        with get_db_connection() as conn:
            _init_cve_table(conn)
            rows = conn.execute(
                """SELECT * FROM cve_records
                   WHERE cve_id LIKE ? OR description LIKE ?
                   ORDER BY cvss_score DESC, published_date DESC
                   LIMIT ?""",
                (f"%{keyword}%", f"%{keyword}%", min(limit, 100)),
            ).fetchall()
            return [_record_to_dict(r) for r in rows]
    except Exception as e:
        logger.warning("Search CVE cache failed: %s", e)
    return []


def get_cves_for_component(
    component_name: str, version: str | None = None
) -> list[dict[str, Any]]:
    """根据组件名和版本查询相关 CVE（优先本地缓存，使用组件索引加速）。"""
    results: list[dict[str, Any]] = []
    try:
        with get_db_connection() as conn:
            _init_cve_table(conn)
            product = component_name.lower().strip()
            # 通过组件索引表快速定位 CVE
            rows = conn.execute(
                """SELECT r.* FROM cve_records r
                   JOIN cve_components c ON r.cve_id = c.cve_id
                   WHERE c.product = ? OR c.product LIKE ?
                   ORDER BY r.cvss_score DESC LIMIT 50""",
                (product, f"%{product}%"),
            ).fetchall()
            results = [_record_to_dict(r) for r in rows]
    except Exception as e:
        logger.warning("Query CVE by component failed: %s", e)
    return results


def get_cve_stats() -> dict[str, Any]:
    """返回本地 CVE 缓存统计。"""
    try:
        with get_db_connection() as conn:
            _init_cve_table(conn)
            total = conn.execute("SELECT COUNT(*) FROM cve_records").fetchone()[0]
            by_severity = {}
            for row in conn.execute(
                "SELECT severity, COUNT(*) AS cnt FROM cve_records GROUP BY severity"
            ).fetchall():
                by_severity[row["severity"] or "unknown"] = row["cnt"]
            latest = conn.execute(
                "SELECT cve_id, published_date FROM cve_records ORDER BY published_date DESC LIMIT 1"
            ).fetchone()
            return {
                "total_cached": total,
                "by_severity": by_severity,
                "latest_cached": {
                    "cve_id": latest["cve_id"],
                    "published_date": latest["published_date"],
                }
                if latest
                else None,
            }
    except Exception as e:
        logger.warning("CVE stats failed: %s", e)
    return {"total_cached": 0, "by_severity": {}, "latest_cached": None}
