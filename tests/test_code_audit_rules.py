from app.services.code_audit import audit_source, audit_sources


def test_rust_command_execution_is_located():
    findings = audit_source("worker.rs", b"Command::new(\"tool\");", "rust-1")
    assert findings[0]["line"] == 1
    assert findings[0]["severity"] == "high"


def test_sql_dynamic_execution_is_located():
    findings = audit_source("migration.sql", b"EXECUTE IMMEDIATE user_sql;", "sql-1")
    assert findings[0]["line"] == 1
    assert findings[0]["severity"] == "high"


def test_audit_sources_adds_dependency_config_and_cross_file_flow():
    findings = audit_sources({
        "app.py": b"value = request.args.get('q')\n",
        "db.py": b"db.execute(value)\n",
        "requirements.txt": b"PyYAML==5.3\n",
        ".env": b"DATABASE_PASSWORD=plain-secret\n",
        "Dockerfile": b"USER root\n",
    }, "audit-1")
    rules = {item["rule"] for item in findings}
    assert {"cross_file_data_flow", "dependency_advisory", "config_security"} <= rules
    assert any(item.get("code_flow") for item in findings)
