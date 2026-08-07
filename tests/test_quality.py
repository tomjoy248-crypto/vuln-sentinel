from app.quality.fp_control import FalsePositiveControl, filter_findings
from app.quality.quality_assessment import assess_scan_quality


def test_fp_control_marks_challenge_like_responses_as_likely_fp():
    controller = FalsePositiveControl(threshold=0.35)
    finding = {
        "type": "sqli",
        "confidence": "high",
        "evidence": {
            "request": "GET /login HTTP/1.1\nHost: example.com",
            "response": "HTTP/1.1 403 Forbidden\nServer: cloudflare\nAccess denied",
            "response_headers": "Server: cloudflare\n",
        },
    }

    result = controller.analyze(finding)

    assert result["fp_score"] >= 0.35
    assert result["is_likely_fp"] is True
    assert result["adjusted_confidence"] in {"medium", "low", "info"}


def test_filter_findings_can_keep_low_confidence_items():
    findings = [
        {
            "type": "xss",
            "confidence": "high",
            "evidence": {
                "request": "GET /static/app.js HTTP/1.1\nHost: example.com",
                "response": "HTTP/1.1 404 Not Found\n",
                "response_headers": "",
            },
        }
    ]

    kept = filter_findings(findings, threshold=0.9, drop_fp=False)

    assert len(kept) == 1
    assert "fp_score" in kept[0]
    assert "is_likely_fp" in kept[0]


def test_quality_assessment_penalizes_high_fp_rates():
    findings = [
        {"type": "xss", "confidence": "high", "is_likely_fp": True},
        {"type": "sqli", "confidence": "high", "is_likely_fp": True},
    ]

    assessment = assess_scan_quality(findings, scan_duration_ms=12000, depth="standard")

    assert assessment.reliability_score < 60
    assert assessment.overall_score < 70
