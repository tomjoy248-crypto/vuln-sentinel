import os
import sys

os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402
from app.reporting import generate_src_report  # noqa: E402
from app.reporting.grouping import group_findings  # noqa: E402


def _sample_findings():
    return [
        {
            "id": "VULN-001",
            "title": "敏感路径暴露",
            "type": "backup_exposure",
            "severity": "high",
            "verification_status": "verified",
        },
        {
            "id": "VULN-002",
            "title": "缺少 CSP",
            "type": "header_missing",
            "severity": "medium",
            "verification_status": "unverified",
        },
        {
            "id": "VULN-003",
            "title": "API 入口面暴露",
            "type": "api_surface_exposure",
            "severity": "medium",
            "verification_status": "verified",
        },
        {
            "id": "VULN-004",
            "title": "第三方前端资源未固定版本",
            "type": "supply_chain_exposure",
            "severity": "low",
            "verification_status": "unverified",
        },
    ]


def test_group_findings_returns_stable_risk_surfaces():
    grouped = group_findings(_sample_findings())

    labels = [group["label"] for group in grouped]
    assert "公开暴露面" in labels
    assert "配置与响应头" in labels
    assert "组件与供应链" in labels


def test_markdown_report_includes_grouped_section_once():
    report = main.generate_src_markdown_report(
        {"url": "https://example.com", "findings": _sample_findings()}
    )

    assert report.count("## 风险面分组") == 1
    assert "风险面总览" in report
    assert "公开暴露面" in report
    assert "配置与响应头" in report


def test_html_report_includes_grouped_section_once():
    html = main.generate_html_report(
        {
            "url": "https://example.com",
            "score": 88,
            "risk_level": "High",
            "time": "2026-08-31 12:00:00",
            "findings": _sample_findings(),
        }
    )

    assert html.count("按风险面分组") == 1
    assert "风险面总览" in html
    assert "公开暴露面" in html
    assert "配置与响应头" in html


def test_src_report_includes_grouped_section():
    report = generate_src_report({"findings": _sample_findings()}, format="markdown")

    assert "## 二.4 按风险面分组" in report
    assert "风险面总览" in report
    assert "公开暴露面" in report
    assert "配置与响应头" in report
    assert "组件与供应链" in report
    assert "管理层关注" in report
    assert "修复优先级路线" in report
