"""漏洞哨兵 11-S API 负载测试。

使用方法：
    pip install locust
    locust -f tests/locustfile.py --host=http://localhost:8000

测试场景：
- 首页访问
- 健康检查
- 公开 API（/api/config, /api/billing/plans）
- 登录 + 扫描（需要测试账号）
"""
from locust import HttpUser, between, task


class VulnSentinelUser(HttpUser):
    """模拟普通用户行为。"""

    wait_time = between(1, 3)

    @task(3)
    def visit_home(self):
        self.client.get("/")

    @task(2)
    def health_check(self):
        self.client.get("/health/live")

    @task(2)
    def get_config(self):
        self.client.get("/api/config")

    @task(1)
    def get_plans(self):
        self.client.get("/api/billing/plans")

    @task(1)
    def login_and_scan(self):
        """登录并提交扫描（需要测试账号）。"""
        resp = self.client.post("/api/login", json={
            "username": "demo",
            "password": "demo123",
        })
        if resp.status_code == 200:
            token = resp.json().get("token", "")
            headers = {"Authorization": f"Bearer {token}"}
            self.client.get("/api/me/credits", headers=headers)
