"""V11.5 优化点回归测试
- 1) simulate_fix 不再定义局部 SEV_DEDUCT
- 2) /api/ai/chat 走 limiter_ai(防被刷)
- 3) apply-fix-and-rescan / retest 加 30s wait_for 超时
- 4) jwt_secret / llm_api_key 启用 repr=False
- 5) AI 聊天窗 Esc 关闭 + Ctrl+/ 快捷键绑定
- 6) .env.example / requirements.txt / CHANGELOG / LICENSE / SECURITY.md 完整
"""
import re
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

import main as M

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client():
    return TestClient(M.app)


# ============================================================
# 1) SEV_DEDUCT 不再重复定义
# ============================================================
def test_simulate_fix_no_local_sev_deduct():
    """simulate_fix 函数体不应再有 SEV_DEDUCT 局部定义"""
    src = open(str(ROOT / "main.py")).read()
    # 找 simulate_fix 函数体
    m = re.search(r"async def simulate_fix.*?(?=\nasync def |\n@app\.)", src, re.DOTALL)
    assert m, "simulate_fix function not found"
    body = m.group(0)
    assert "SEV_DEDUCT" not in body, "should not redefine SEV_DEDUCT"
    # 应该用全局
    assert "SEVERITY_SCORE" in body


# ============================================================
# 2) /api/ai/chat 限流
# ============================================================
def test_ai_chat_has_limiter_check():
    src = open(str(ROOT / "main.py")).read()
    m = re.search(r"async def api_ai_chat.*?(?=\nasync def |\n@app\.)", src, re.DOTALL)
    assert m, "api_ai_chat not found"
    body = m.group(0)
    assert "limiter_ai" in body, "should use limiter_ai"
    assert "is_allowed" in body, "should call is_allowed"


# ============================================================
# 3) 30s 超时包裹
# ============================================================
def test_apply_fix_rescan_has_30s_timeout():
    src = open(str(ROOT / "main.py")).read()
    m = re.search(r"async def apply_fix_and_rescan.*?(?=\nasync def |\n@app\.)", src, re.DOTALL)
    assert m
    body = m.group(0)
    assert "asyncio.wait_for" in body
    assert "timeout=30" in body


def test_api_retest_has_30s_timeout():
    src = open(str(ROOT / "main.py")).read()
    m = re.search(r"async def api_retest.*?(?=\nasync def |\n@app\.)", src, re.DOTALL)
    assert m
    body = m.group(0)
    assert "asyncio.wait_for" in body
    assert "asyncio.TimeoutError" in body


# ============================================================
# 4) repr=False 防止敏感字段泄露
# ============================================================
def test_jwt_secret_has_repr_false():
    src = open(str(ROOT / "main.py")).read()
    m = re.search(r"jwt_secret:.*", src)
    assert m
    assert "repr=False" in m.group(0)


def test_llm_api_key_has_repr_false():
    src = open(str(ROOT / "main.py")).read()
    m = re.search(r"llm_api_key:.*", src)
    assert m
    assert "repr=False" in m.group(0)


def test_settings_repr_does_not_leak_secrets():
    """repr(settings) 不应包含 jwt_secret / llm_api_key 实际值"""
    s = repr(M.settings)
    # 默认值都是空字符串,repr 出来应仍是 '' 而非明文
    if M.settings.jwt_secret:
        assert M.settings.jwt_secret not in s
    if M.settings.llm_api_key:
        assert M.settings.llm_api_key not in s


# ============================================================
# 5) 前端快捷键
# ============================================================
def test_index_html_esc_closes_ai_chat():
    html = open(str(ROOT / "static/index.html")).read()
    assert "ai-chat" in html
    # Esc 处理块应包含 ai-chat
    esc_block = re.search(r"if \(e\.key === 'Escape'\).*?return;\s*\}", html, re.DOTALL)
    assert esc_block
    assert "ai-chat" in esc_block.group(0)


def test_index_html_has_ctrl_slash_shortcut():
    html = open(str(ROOT / "static/index.html")).read()
    assert "Ctrl/Cmd + /" in html or 'e.key === "/"' in html


# ============================================================
# 6) 文档与配置完整
# ============================================================
def test_env_example_has_all_keys():
    txt = open(str(ROOT / ".env.example")).read()
    for key in [
        "JWT_SECRET", "JWT_EXPIRE_SECONDS", "DB_DIR", "DB_NAME",
        "SCAN_TIMEOUT", "RATE_LIMIT_GLOBAL_PER_MINUTE",
        "ALLOWED_ORIGINS", "TLS_VERIFY",
        "LLM_ENABLED", "LLM_API_KEY", "LLM_MODEL",
        "PATROL_INTERVAL_HOURS", "PATROL_SCORE_REGRESSION_THRESHOLD",
        "PUBLIC_DEMO_ENABLED",
    ]:
        assert key in txt, f".env.example missing {key}"


def test_requirements_has_cryptography():
    txt = open(str(ROOT / "requirements.txt")).read()
    assert "cryptography" in txt


def test_changelog_exists_and_has_v115():
    txt = open(str(ROOT / "CHANGELOG.md")).read()
    assert "V11.5" in txt


def test_license_exists():
    txt = open(str(ROOT / "LICENSE")).read()
    assert "MIT" in txt


def test_security_md_exists():
    txt = open(str(ROOT / "SECURITY.md")).read()
    assert "漏洞" in txt or "安全" in txt


# ============================================================
# 7) 回归：健康检查 + 已知 URL
# ============================================================
def test_health():
    r = TestClient(M.app).get("/api/health")
    assert r.status_code == 200
