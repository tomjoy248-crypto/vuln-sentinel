import main


def test_passive_exposure_reports_each_signal_on_same_page():
    findings = main._extract_passive_exposure_findings(
        "https://authorized.example",
        [{
            "url": "https://authorized.example/",
            "title": "API documentation",
            "signals": ["api_docs", "source_map", "directory_index"],
        }],
    )

    assert {finding["name"] for finding in findings} == {
        "暴露 API 文档入口",
        "暴露源码映射文件",
        "目录列表暴露",
    }
    assert all(finding["evidence"]["url"] == "https://authorized.example/" for finding in findings)


def test_passive_exposure_deduplicates_repeated_pages():
    page = {"url": "https://authorized.example/docs", "signals": ["api_docs"]}

    findings = main._extract_passive_exposure_findings(
        "https://authorized.example",
        [page, dict(page)],
    )

    assert len(findings) == 1
    assert findings[0]["confidence_level"] == "高"
