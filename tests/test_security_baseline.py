"""Regression tests for the source-level security baseline checks."""

from scripts.security_baseline_check import _scan_for_hardcoded_secrets


def test_security_baseline_ignores_password_related_ui_flags() -> None:
    """UI flags containing ``password`` must not be reported as credentials."""
    content = 'has_password = \'type="password"\'\npassword_field = \'type=password\''

    assert _scan_for_hardcoded_secrets(content) == []


def test_security_baseline_detects_standalone_credential_assignment() -> None:
    """Standalone credential assignments remain visible to the baseline."""
    content = 'password = "hard-coded-value"\napi_key = "hard-coded-key"'

    findings = _scan_for_hardcoded_secrets(content)

    assert findings == ["credential assignment"]
