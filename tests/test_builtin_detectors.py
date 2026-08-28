from app.plugins import ScanContext
from app.plugins.builtin import DirectoryListingDetector, TraceMethodDetector


def test_directory_listing_detector_finds_index_pages():
    detector = DirectoryListingDetector()
    context = ScanContext(
        url="https://example.com/files/",
        headers={"Content-Type": "text/html; charset=utf-8"},
        body="<html><head><title>Index of /files/</title></head><body><h1>Index of /files/</h1><a href='../'>Parent Directory</a></body></html>",
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].type == "directory_listing"
    assert findings[0].severity == "medium"


def test_trace_method_detector_flags_allow_trace():
    detector = TraceMethodDetector()
    context = ScanContext(
        url="https://example.com/",
        headers={"Allow": "GET, HEAD, OPTIONS, TRACE"},
        body="",
    )

    findings = __import__("asyncio").run(detector.detect(context))

    assert len(findings) == 1
    assert findings[0].type == "trace_method"
    assert findings[0].title == "HTTP TRACE 方法可用"
