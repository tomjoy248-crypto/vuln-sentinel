import pytest

from types import SimpleNamespace

import main
from app.core.rate_limiter import get_client_ip


def test_get_client_ip_prefers_x_forwarded_for():
    request = SimpleNamespace(
        headers={"X-Forwarded-For": "203.0.113.10, 10.0.0.2", "X-Real-IP": "198.51.100.7"},
        client=SimpleNamespace(host="127.0.0.1"),
    )
    assert get_client_ip(request) == "203.0.113.10"


def test_get_client_ip_falls_back_to_real_ip():
    request = SimpleNamespace(headers={"X-Real-IP": "198.51.100.7"}, client=SimpleNamespace(host="127.0.0.1"))
    assert get_client_ip(request) == "198.51.100.7"


def test_validate_production_config_flags_bad_settings(monkeypatch):
    monkeypatch.setattr(main, "_IS_PRODUCTION", True)
    monkeypatch.setattr(main.settings, "jwt_secret", "x" * 32, raising=False)
    monkeypatch.setattr(main.settings, "cors_origins", "*", raising=False)
    monkeypatch.setattr(main.settings, "public_demo_enabled", True, raising=False)
    monkeypatch.setattr(main.settings, "database_url", "", raising=False)
    monkeypatch.setenv("PUBLIC_BASE_URL", "")
    monkeypatch.setattr(main.settings, "db_dir", "/tmp", raising=False)
    monkeypatch.setattr(main.settings, "enable_metrics", True, raising=False)
    monkeypatch.setattr(main.settings, "env", "production", raising=False)
    monkeypatch.setattr(main.settings, "sentry_dsn", "", raising=False)
    monkeypatch.setattr(main.settings, "redis_url", "", raising=False)
    with pytest.raises(RuntimeError) as excinfo:
        main.validate_production_config()
    message = str(excinfo.value)
    assert "CORS_ORIGINS" in message
    assert "PUBLIC_BASE_URL" in message
