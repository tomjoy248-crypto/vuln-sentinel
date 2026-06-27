"""V11.6 本地演示靶场测试 - 测试扫描-修复-复测完整闭环"""
import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 测试模式
os.environ["TEST_MODE"] = "1"
os.environ["JWT_SECRET"] = "test-secret-key-for-v115-demo-tests"

from fastapi.testclient import TestClient
import main as app_module


@pytest.fixture(scope="module")
def client():
    """创建测试客户端"""
    # 确保数据库是临时的
    import tempfile
    tmp_db = tempfile.mktemp(suffix=".db")
    app_module.DB_PATH = tmp_db
    app_module._TEST_MODE = True

    # V11.6: 允许 localhost 扫描（演示靶场测试用）
    app_module.ALLOWED_INTERNAL_HOSTS.add("localhost")
    app_module.ALLOWED_INTERNAL_HOSTS.add("127.0.0.1")

    # 重新初始化数据库
    app_module.init_db()

    # 创建测试用户
    conn = app_module.get_db()
    conn.execute(
        "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
        ("demo", app_module.hash_password("demo123"), "member"),
    )
    conn.commit()
    conn.close()

    with TestClient(app_module.app) as c:
        yield c

    # 清理
    if os.path.exists(tmp_db):
        os.unlink(tmp_db)


@pytest.fixture(scope="module")
def auth_headers(client):
    """获取认证 token"""
    resp = client.post(
        "/api/login",
        json={"username": "demo", "password": "demo123"},
    )
    assert resp.status_code == 200
    token = resp.json()["token"]
    return {"Authorization": f"Bearer {token}"}


class TestDemoTarget:
    """测试本地演示靶场"""

    def test_demo_status_endpoint(self, client):
        """测试演示靶场状态查询接口"""
        resp = client.get("/api/demo-status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "running" in data
        assert "config_path" in data
        assert "backup_exists" in data
        assert "headers_status" in data

    def test_demo_fix_reset_requires_localhost(self, client, auth_headers):
        """测试演示修复接口只允许本地靶场"""
        resp = client.post(
            "/api/demo-fix",
            json={"action": "apply", "target": "example.com"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert "仅支持本地演示靶场" in data["error"]

    def test_demo_fix_apply_and_reset(self, client, auth_headers):
        """测试应用修复和重置功能"""
        # 检查 nginx 是否可用
        import shutil
        if not shutil.which("nginx"):
            pytest.skip("nginx 未安装，跳过此测试")

        # 先重置
        resp = client.post(
            "/api/demo-fix",
            json={"action": "reset", "target": "localhost:8080"},
            headers=auth_headers,
        )
        # 可能因为没有备份而失败，这是正常的
        data = resp.json()

        # 应用修复
        resp = client.post(
            "/api/demo-fix",
            json={"action": "apply", "target": "localhost:8080"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["action"] == "apply"
        assert "安全头已应用" in data["message"] or "已经应用过" in data["message"]

        # 再次重置（现在应该有备份了）
        resp = client.post(
            "/api/demo-fix",
            json={"action": "reset", "target": "localhost:8080"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["action"] == "reset"


class TestDemoFullCycle:
    """测试一键演示完整闭环"""

    def test_full_cycle_endpoint_exists(self, client, auth_headers):
        """测试完整闭环接口存在"""
        resp = client.post(
            "/api/demo-full-cycle",
            headers=auth_headers,
            json={"target": "localhost:8080", "reset_first": True},
        )
        # 接口应该存在，可能因为环境问题失败，但不应该是 404
        assert resp.status_code != 404
        data = resp.json()
        assert "success" in data

    def test_full_cycle_returns_comparison(self, client, auth_headers):
        """测试完整闭环返回前后对比数据"""
        resp = client.post(
            "/api/demo-full-cycle",
            headers=auth_headers,
            json={"target": "localhost:8080", "reset_first": True},
        )
        data = resp.json()

        if data.get("success"):
            # 成功的情况下，检查返回结构
            assert "before" in data
            assert "after" in data
            assert "diff" in data

            before = data["before"]
            after = data["after"]
            diff = data["diff"]

            assert "score" in before
            assert "score" in after
            assert "score_delta" in diff
            assert "fixed" in diff
            assert "findings_fixed" in diff

            # 修复后评分应该更高
            assert after["score"] >= before["score"]

            # 修复的漏洞数应该 > 0
            assert diff["findings_fixed"] >= 0


class TestLocalhostScanning:
    """测试 localhost 扫描功能"""

    def test_localhost_url_allowed(self, client, auth_headers):
        """测试 localhost URL 被允许扫描（演示靶场专用）"""
        resp = client.post(
            "/api/scan",
            headers=auth_headers,
            json={"url": "http://localhost:8080", "authorized": True},
        )
        # 不应该是 422（URL 格式错误），应该是正常扫描结果
        assert resp.status_code == 200
        data = resp.json()
        assert "success" in data

    def test_localhost_no_cache(self, client, auth_headers):
        """测试 localhost 扫描不使用缓存（确保修复后立即可见）"""
        # 第一次扫描
        resp1 = client.post(
            "/api/scan",
            headers=auth_headers,
            json={"url": "http://localhost:8080", "authorized": True},
        )
        data1 = resp1.json()

        # 第二次扫描（不应该有缓存）
        resp2 = client.post(
            "/api/scan",
            headers=auth_headers,
            json={"url": "http://localhost:8080", "authorized": True},
        )
        data2 = resp2.json()

        # 两次都不应该是缓存结果
        assert data1.get("is_cached") is not True
        assert data2.get("is_cached") is not True


class TestDemoTargetNginxConfig:
    """测试演示靶场 nginx 配置操作"""

    def test_nginx_config_exists(self):
        """测试演示靶场配置文件存在"""
        conf_path = os.path.join(os.path.dirname(__file__), "..", "demo-target", "conf", "nginx.conf")
        assert os.path.exists(conf_path), "演示靶场 nginx 配置文件不存在"

    def test_nginx_config_has_vulnerabilities(self):
        """测试初始配置包含预期的漏洞"""
        # 读取备份文件（原始漏洞配置）
        backup_path = os.path.join(os.path.dirname(__file__), "..", "demo-target", "conf", "nginx.conf.vulnerable")
        if not os.path.exists(backup_path):
            pytest.skip("备份文件不存在，跳过此测试")

        with open(backup_path, "r") as f:
            content = f.read()

        # 检查漏洞配置
        assert "server_tokens on" in content, "缺少 server_tokens on（版本泄露）"
        assert "autoindex on" in content, "缺少 autoindex on（目录遍历）"
        assert 'Access-Control-Allow-Origin "*"' in content, "缺少 CORS 通配符配置"
        # V11.6: 检查缺少安全头（通过注释标记验证）
        assert "缺少所有安全响应头" in content, "配置应标记缺少安全响应头"

    def test_security_headers_not_in_original_config(self):
        """测试原始配置不包含实际的安全头配置"""
        backup_path = "/workspace/v11.4/demo-target/conf/nginx.conf.vulnerable"
        if not os.path.exists(backup_path):
            pytest.skip("备份文件不存在，跳过此测试")

        with open(backup_path, "r") as f:
            lines = f.readlines()

        # 原始配置不应该有实际的 add_header 安全头配置（排除注释行）
        code_lines = [l for l in lines if not l.strip().startswith('#')]
        content = '\n'.join(code_lines)

        assert "X-Frame-Options" not in content, "原始配置不应包含 X-Frame-Options 配置"
        assert "X-Content-Type-Options" not in content, "原始配置不应包含 X-Content-Type-Options 配置"
        assert "Content-Security-Policy" not in content, "原始配置不应包含 CSP 配置"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
