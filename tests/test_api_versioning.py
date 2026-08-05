"""API 版本化中间件测试。

覆盖：
- /api/v1/<endpoint> 经中间件内部重写为 /api/<endpoint>，行为与旧端点一致
- /api/v1/ 响应携带 X-API-Version: v1 头
- 旧 /api/ 路径标记为 v0 并附加 X-API-Deprecation 弃用提示头
- 非 API 路径（如首页 /）不携带版本相关头
"""
import os
import sys

from fastapi.testclient import TestClient

# 强制使用临时 DB，避免污染用户数据（必须在导入 main 之前设置）
os.environ["DB_DIR"] = "/tmp/v11-test"
os.environ["DB_NAME"] = "test.db"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main  # noqa: E402

os.makedirs("/tmp/v11-test", exist_ok=True)
main.init_db()

client = TestClient(main.app)


def test_v1_health_matches_legacy_health():
    """/api/v1/health 经重写后应与 /api/health 返回一致（忽略每次请求变化的字段）。"""
    r_v1 = client.get("/api/v1/health")
    r_legacy = client.get("/api/health")

    assert r_v1.status_code == 200
    assert r_legacy.status_code == 200

    body_v1 = r_v1.json()
    body_legacy = r_legacy.json()

    # request_id 与 uptime_sec 随每次请求/时间变化，比较时剔除
    for key in ("request_id", "uptime_sec"):
        body_v1.pop(key, None)
        body_legacy.pop(key, None)

    assert body_v1 == body_legacy


def test_v1_version_matches_legacy_version():
    """/api/v1/version 经重写后应与 /api/version 返回完全一致（确定性响应）。"""
    r_v1 = client.get("/api/v1/version")
    r_legacy = client.get("/api/version")

    assert r_v1.status_code == 200
    assert r_legacy.status_code == 200
    assert r_v1.json() == r_legacy.json()


def test_v1_response_has_version_header():
    """/api/v1/ 路径的响应应携带 X-API-Version: v1 头。"""
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.headers.get("X-API-Version") == "v1"


def test_v1_info_endpoint():
    """/api/v1/ 版本根端点应返回 API 版本信息且标记为 v1（不弃用）。"""
    r = client.get("/api/v1/")
    assert r.status_code == 200
    body = r.json()
    assert body["api_version"] == "v1"
    assert body["version"] == main.settings.app_version
    assert r.headers.get("X-API-Version") == "v1"
    # 版本根端点不应标记为弃用
    assert "X-API-Deprecation" not in r.headers


def test_v1_without_trailing_slash():
    """/api/v1（无尾斜杠）也应被识别为 v1 版本根端点。"""
    r = client.get("/api/v1")
    assert r.status_code == 200
    assert r.json()["api_version"] == "v1"
    assert r.headers.get("X-API-Version") == "v1"


def test_legacy_api_has_deprecation_header():
    """旧 /api/ 路径应标记为 v0 并附加 X-API-Deprecation 弃用提示。"""
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.headers.get("X-API-Version") == "v0"
    assert "X-API-Deprecation" in r.headers
    assert "/api/v1/" in r.headers["X-API-Deprecation"]


def test_non_api_path_has_no_version_headers():
    """非 API 路径（如首页 /）不应携带版本相关头。"""
    r = client.get("/")
    assert r.status_code == 200
    assert "X-API-Version" not in r.headers
    assert "X-API-Deprecation" not in r.headers
