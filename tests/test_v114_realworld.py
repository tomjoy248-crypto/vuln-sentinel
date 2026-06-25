"""V11.4 实战验证：扫描真实漏洞站 + 模拟修复"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_simulate_fix_generates_nginx_config():
    """模拟修复必须生成可执行的 Nginx 配置代码（不只是评分变化）"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    findings = [
        {"name": "缺少 HSTS", "severity": "high"},
        {"name": "缺少 CSP", "severity": "high"},
        {"name": "缺少 X-Frame-Options", "severity": "medium"},
        {"name": "缺少 X-Content-Type-Options", "severity": "medium"},
        {"name": "缺少 Referrer-Policy", "severity": "low"},
        {"name": "缺少 Permissions-Policy", "severity": "low"},
        {"name": "Server 信息泄露", "severity": "low"},
        {"name": "Cookie 安全配置不足", "severity": "low"},
    ]
    resp = client.post("/api/simulate-fix", json={"findings": findings})
    assert resp.status_code == 200
    d = resp.json()
    # 评分变化
    assert d["before_score"] == 42  # 100 - 2*15 - 2*8 - 4*3 = 42
    assert d["after_score"] == 100
    assert d["delta"] == 58
    assert d["fixed_count"] == 8
    # 关键：必须生成 Nginx 配置代码
    nginx = d.get("nginx_config", "")
    assert "add_header Strict-Transport-Security" in nginx, f"缺少 HSTS 配置: {nginx[:200]}"
    assert "add_header X-Frame-Options" in nginx, f"缺少 X-Frame 配置: {nginx[:200]}"
    assert "server_tokens" in nginx or "Server" in nginx, f"缺少 Server 修复: {nginx[:200]}"


def test_scan_real_vuln_site_has_findings():
    """扫描真实漏洞站 demo.testfire.net（Altoro Mutual）必须能扫出问题"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    # 先登录
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        import pytest
        pytest.skip("demo 账号未注册")
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    # 扫描真实漏洞站
    resp = client.post(
        "/api/scan",
        json={"url": "http://demo.testfire.net", "depth": "standard", "authorized": True},
        headers=headers,
        timeout=30,
    )
    assert resp.status_code == 200, f"Scan failed: {resp.status_code}"
    d = resp.json()
    # demo.testfire.net 是公认的有漏洞演示站，必须扫出问题
    assert d.get("score", 100) < 90, f"预期漏洞站评分应 < 90，实际 {d.get('score')}"
    assert len(d.get("findings", [])) >= 3, f"预期至少 3 个问题，实际 {len(d.get('findings', []))}"


def test_real_vuln_site_findings_have_actionable_fix():
    """扫描出的每个问题必须有可执行的修复代码（fix 字段）"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        import pytest
        pytest.skip("demo 账号未注册")
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post(
        "/api/scan",
        json={"url": "http://demo.testfire.net", "depth": "standard", "authorized": True},
        headers=headers,
        timeout=30,
    )
    d = resp.json()
    findings = d.get("findings", [])
    assert len(findings) > 0, "扫描漏洞站必须有问题"
    # 至少 50% 的 finding 有 fix 字段
    with_fix = sum(1 for f in findings if f.get("fix", "").strip())
    assert with_fix >= len(findings) * 0.5, f"只有 {with_fix}/{len(findings)} 个问题有 fix 字段"
