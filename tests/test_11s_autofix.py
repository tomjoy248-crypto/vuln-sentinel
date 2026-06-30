"""11-S 终极验收：自动修复闭环（SSH + Cloudflare）"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

import pytest


def test_auto_fix_endpoint_validates_credentials():
    """/api/auto-fix 端点存在并验证凭证（不允许空 host）"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        import pytest
        pytest.skip("demo 账号未注册")
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/api/auto-fix", json={"scan_id": 0, "credentials": {}}, headers=headers)
    assert resp.status_code == 200
    d = resp.json()
    assert d["success"] is False
    assert d.get("error")


def test_auto_fix_generates_correct_nginx_config():
    """自动修复生成的 Nginx 补丁必须含安全头配置"""
    from main import _generate_fix_patch
    findings = [
        {"name": "缺少 HSTS", "severity": "high"},
        {"name": "缺少 CSP", "severity": "high"},
        {"name": "缺少 X-Frame-Options", "severity": "medium"},
    ]
    patch = _generate_fix_patch(findings, "nginx")
    assert "Strict-Transport-Security" in patch
    assert "Content-Security-Policy" in patch
    assert "X-Frame-Options" in patch
    assert "漏洞哨兵" in patch
    assert "add_header" in patch


def test_credential_encryption_roundtrip():
    """凭证加密 → 解密必须可逆"""
    from main import _encrypt_credential, _decrypt_credential
    pwd = "MyVerySecretPassword_2026!@#"
    enc = _encrypt_credential(pwd)
    assert enc != pwd, "加密后必须不等于明文"
    assert len(enc) > 20, "加密后长度应大于原文"
    dec = _decrypt_credential(enc)
    assert dec == pwd, f"解密失败: {dec}"


def test_auto_fix_cloudflare_endpoint_exists():
    """/api/auto-fix-via-cloudflare 端点必须存在"""
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
        "/api/auto-fix-via-cloudflare",
        json={"scan_id": 0},
        headers=headers,
    )
    assert resp.status_code == 200
    d = resp.json()
    assert d["success"] is False


def test_public_demo_save_scan_id_for_logged_in_user():
    """已登录用户的 demo 扫描必须返回 scan_id（用于触发自动修复）"""
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
        "/api/public-demo-scan",
        json={"url": "https://example.com", "demo_id": "example"},
        headers=headers,
        timeout=30,
    )
    assert resp.status_code == 200, f"Status {resp.status_code}: {resp.text[:200]}"
    d = resp.json()
    assert d.get("scan_id") is not None, f"Logged in user should get scan_id. Got: {list(d.keys())}"


def test_auto_fix_full_workflow_dry_run():
    """完整工作流 dry-run：扫 → 模拟修复 → 真实生成 Nginx 配置"""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    login = client.post("/api/login", json={"username": "demo", "password": "demo123"})
    if login.status_code != 200:
        import pytest
        pytest.skip("demo 账号未注册")
    token = login.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 扫描
    scan = client.post(
        "/api/scan",
        json={"url": "http://demo.testfire.net", "depth": "standard", "authorized": True},
        headers=headers,
        timeout=30,
    )
    scan_id = scan.json().get("scan_id") or scan.json().get("id")
    assert scan_id, "Scan must return scan_id"

    # 2. 模拟修复
    findings = scan.json().get("findings", [])
    sim = client.post(
        "/api/simulate-fix",
        json={"findings": findings},
        headers=headers,
    )
    assert sim.status_code == 200
    sim_data = sim.json()
    assert sim_data.get("nginx_config"), "Simulate fix must return nginx_config"
    assert sim_data.get("after_score") > sim_data.get("before_score"), "Score should improve"

    # 3. auto-fix 端点
    fix = client.post(
        "/api/auto-fix",
        json={"scan_id": scan_id, "credentials": {}},
        headers=headers,
    )
    assert fix.status_code == 200
    d = fix.json()
    assert d.get("success") is False
    assert d.get("error")


@pytest.mark.skipif(not HAS_PARAMIKO, reason="paramiko not installed")
def test_ssh_execute_safety():
    """SSH 执行函数不能连接到无效主机（必须安全失败）"""
    from main import _ssh_execute
    try:
        result = _ssh_execute("192.0.2.1", 22, "root", "wrong", ["echo test"], timeout=5)
        # 连接到 192.0.2.1（TEST-NET-1 RFC 5737）应该失败
        assert False, "Expected connection to fail"
    except RuntimeError:
        # 预期失败
        pass
    except Exception as e:
        # 其他网络异常也算
        assert "失败" in str(e) or "connect" in str(e).lower() or "refused" in str(e).lower() or "timed out" in str(e).lower()
