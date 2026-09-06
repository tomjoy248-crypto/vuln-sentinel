from app.services.code_audit import audit_source


def test_rust_command_execution_is_located():
    findings = audit_source("worker.rs", b"Command::new(\"tool\");", "rust-1")
    assert findings[0]["line"] == 1
    assert findings[0]["severity"] == "high"


def test_sql_dynamic_execution_is_located():
    findings = audit_source("migration.sql", b"EXECUTE IMMEDIATE user_sql;", "sql-1")
    assert findings[0]["line"] == 1
    assert findings[0]["severity"] == "high"
