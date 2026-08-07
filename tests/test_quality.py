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


from app.services import billing_service
import main


def test_production_blocks_mock_payment(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("PRODUCTION", "1")
    monkeypatch.setenv("ALIPAY_MOCK", "1")
    monkeypatch.setenv("WECHAT_MOCK", "1")
    monkeypatch.setenv("MOCK_WEBHOOK_SECRET", "secret")
    monkeypatch.setattr(billing_service, "_IS_PRODUCTION", True)
    monkeypatch.setattr(billing_service, "get_plan", lambda plan_id: {"active": True, "price_cents": 990, "credits": 20, "name": "体验包", "description": "", "currency": "CNY"})
    monkeypatch.setattr(billing_service, "create_recharge_record", lambda **kwargs: {"id": 1, "transaction_id": "T-1", "status": "pending"})
    monkeypatch.setattr(billing_service, "_provider_enabled", lambda provider: True)

    try:
        billing_service.create_payment_order(user_id=1, plan_id=1, provider="mock")
    except billing_service.BusinessException as exc:
        assert "生产环境不允许使用 mock 支付渠道" in str(exc)
    else:
        raise AssertionError("expected BusinessException")


def test_production_config_flags_mock_payment(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("PRODUCTION", "1")
    monkeypatch.setenv("ALIPAY_MOCK", "1")
    monkeypatch.setenv("WECHAT_MOCK", "1")
    monkeypatch.setenv("MOCK_WEBHOOK_SECRET", "secret")
    monkeypatch.setattr(main, "_IS_PRODUCTION", True)

    issues = main.validate_production_config()
    assert any("ALIPAY_MOCK" in item for item in issues)
    assert any("WECHAT_MOCK" in item for item in issues)
    assert any("MOCK_WEBHOOK_SECRET" in item for item in issues)
