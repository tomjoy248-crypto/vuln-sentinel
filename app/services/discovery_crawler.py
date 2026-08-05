"""轻量级端点发现爬虫，用于扩大插件化扫描的覆盖范围。

设计原则：
- 只访问同域链接，避免跨域风险。
- 严格限制页面数、请求数和总耗时，不阻塞主扫描流程。
- 发现链接、表单和通用参数入口，为检测器提供更多上下文。
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlencode, urljoin, urlparse, urlunparse

import httpx

logger = logging.getLogger("vuln_sentinel.discovery_crawler")


@dataclass
class DiscoveredEndpoint:
    """发现的一个扫描入口。"""

    url: str
    method: str = "GET"
    body: str = ""
    parameter_names: list[str] = field(default_factory=list)
    source: str = "homepage"  # homepage / link / form / sitemap / robots / param_fuzz


class _LinkExtractor(HTMLParser):
    """极简 HTML 链接/表单提取器，不依赖第三方库。"""

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.links: set[str] = set()
        self.forms: list[dict[str, Any]] = []
        self._current_form: dict[str, Any] | None = None
        self._current_inputs: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple]) -> None:
        attr_map = {k.lower(): v for k, v in attrs}

        if tag.lower() == "a":
            href = attr_map.get("href")
            if href:
                self.links.add(urljoin(self.base_url, href))

        if tag.lower() in ("form",):
            action = attr_map.get("action") or self.base_url
            method = attr_map.get("method", "GET").upper()
            self._current_form = {
                "action": urljoin(self.base_url, action),
                "method": method,
            }
            self._current_inputs = []

        if tag.lower() == "input" and self._current_form is not None:
            name = attr_map.get("name")
            if name:
                self._current_inputs.append(
                    {
                        "name": name,
                        "type": attr_map.get("type", "text"),
                        "value": attr_map.get("value", ""),
                    }
                )

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "form" and self._current_form is not None:
            self._current_form["inputs"] = self._current_inputs
            self.forms.append(self._current_form)
            self._current_form = None
            self._current_inputs = []


def _same_origin(url1: str, url2: str) -> bool:
    p1, p2 = urlparse(url1), urlparse(url2)
    return p1.scheme == p2.scheme and p1.netloc.lower() == p2.netloc.lower()


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    # 丢弃 fragment，避免重复
    return urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, "")
    )


def _is_interesting_path(path: str) -> bool:
    """过滤掉静态资源和不必要的文件。"""
    skip_extensions = (
        ".css",
        ".js",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
        ".mp4",
        ".mp3",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".otf",
        ".xml",
        ".json",
    )
    lower = path.lower()
    if any(lower.endswith(ext) for ext in skip_extensions):
        return False
    # 常见的退出/注销链接不应测试
    if any(kw in lower for kw in ("/logout", "/signout", "/exit", "/unsubscribe")):
        return False
    return True


def _build_form_body(inputs: list[dict[str, str]]) -> str:
    """为表单构建一个占位请求体，用于后续检测器识别参数。"""
    params = {}
    for inp in inputs:
        name = inp.get("name")
        if not name:
            continue
        value = inp.get("value") or "test"
        params[name] = value
    return urlencode(params)


class DiscoveryCrawler:
    """轻量级同域端点发现器。"""

    def __init__(
        self,
        max_pages: int = 10,
        request_timeout: float = 5.0,
        total_timeout: float = 20.0,
        max_forms: int = 8,
    ) -> None:
        self.max_pages = max_pages
        self.request_timeout = request_timeout
        self.total_timeout = total_timeout
        self.max_forms = max_forms

    async def discover(
        self, start_url: str, headers: dict[str, str] | None = None
    ) -> list[DiscoveredEndpoint]:
        """从起始 URL 开始发现同域端点。"""
        parsed_start = urlparse(start_url)
        if not parsed_start.scheme or not parsed_start.netloc:
            logger.warning("Invalid start URL for discovery: %s", start_url)
            return []

        endpoints: list[DiscoveredEndpoint] = []
        visited: set[str] = set()
        queue: list[str] = [start_url]

        request_headers = headers or {"User-Agent": "VulnSentinel-Discovery/1.0"}

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(self.request_timeout, connect=3.0),
                follow_redirects=True,
                headers=request_headers,
            ) as client:
                deadline = asyncio.get_event_loop().time() + self.total_timeout

                # 1. 尝试 robots.txt / sitemap.xml
                await self._discover_from_robots(client, start_url, endpoints, visited)

                while (
                    queue
                    and len(visited) < self.max_pages
                    and asyncio.get_event_loop().time() < deadline
                ):
                    current = queue.pop(0)
                    current = _normalize_url(current)
                    if current in visited:
                        continue
                    visited.add(current)

                    try:
                        resp = await client.get(current)
                        if resp.status_code >= 400:
                            continue
                        content_type = resp.headers.get("content-type", "")
                        if "text/html" not in content_type.lower():
                            continue
                        body = resp.text
                    except Exception as exc:
                        logger.debug(
                            "Discovery request failed for %s: %s", current, exc
                        )
                        continue

                    extractor = _LinkExtractor(current)
                    try:
                        extractor.feed(body)
                    except Exception:
                        pass

                    # 当前页面本身作为一个入口
                    endpoints.append(DiscoveredEndpoint(url=current, source="homepage"))

                    # 发现表单
                    for idx, form in enumerate(extractor.forms):
                        if idx >= self.max_forms:
                            break
                        action = form["action"]
                        method = form["method"]
                        if not _same_origin(start_url, action):
                            continue
                        body_str = _build_form_body(form.get("inputs", []))
                        endpoints.append(
                            DiscoveredEndpoint(
                                url=action,
                                method=method,
                                body=body_str,
                                parameter_names=[
                                    i["name"]
                                    for i in form.get("inputs", [])
                                    if i.get("name")
                                ],
                                source="form",
                            )
                        )

                    # 收集新链接
                    for link in extractor.links:
                        link = _normalize_url(link)
                        if not _same_origin(start_url, link):
                            continue
                        parsed = urlparse(link)
                        if not _is_interesting_path(parsed.path):
                            continue
                        if link not in visited and link not in queue:
                            queue.append(link)
        except Exception as exc:
            logger.warning("Discovery crawler failed gracefully: %s", exc)

        # 去重：相同 URL+method 保留一个
        seen: set[str] = set()
        unique: list[DiscoveredEndpoint] = []
        for ep in endpoints:
            key = f"{ep.method}:{_normalize_url(ep.url)}"
            if key in seen:
                continue
            seen.add(key)
            unique.append(ep)

        logger.info(
            "Discovery crawler finished: %d endpoints from %s", len(unique), start_url
        )
        return unique

    async def _discover_from_robots(
        self,
        client: httpx.AsyncClient,
        start_url: str,
        endpoints: list[DiscoveredEndpoint],
        visited: set[str],
    ) -> None:
        """从 robots.txt 和 sitemap.xml 中提取路径。"""
        parsed = urlparse(start_url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        try:
            robots_resp = await client.get(f"{base}/robots.txt")
            if robots_resp.status_code == 200:
                for line in robots_resp.text.splitlines():
                    line = line.strip()
                    if line.lower().startswith("sitemap:"):
                        sitemap_url = line.split(":", 1)[1].strip()
                        await self._parse_sitemap(
                            client, sitemap_url, start_url, endpoints, visited
                        )
        except Exception:
            pass

        # 同时尝试根 sitemap
        await self._parse_sitemap(
            client, f"{base}/sitemap.xml", start_url, endpoints, visited
        )

    async def _parse_sitemap(
        self,
        client: httpx.AsyncClient,
        sitemap_url: str,
        start_url: str,
        endpoints: list[DiscoveredEndpoint],
        visited: set[str],
    ) -> None:
        """从 sitemap 中提取 URL。"""
        try:
            resp = await client.get(sitemap_url)
            if resp.status_code != 200:
                return
            urls = re.findall(r"<loc>([^<]+)</loc>", resp.text)
            for u in urls:
                u = u.strip()
                if not _same_origin(start_url, u):
                    continue
                u = _normalize_url(u)
                if _is_interesting_path(urlparse(u).path):
                    endpoints.append(DiscoveredEndpoint(url=u, source="sitemap"))
        except Exception:
            pass
