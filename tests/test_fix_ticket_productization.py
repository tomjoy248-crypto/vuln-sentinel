from test_main_endpoints import (
    _auth_headers,
    _create_scan_record,
    _demo_user_id,
    client,
)


def test_fix_ticket_owner_timeline_and_export():
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    create = client.post(
        "/api/fix-tickets",
        json={
            "scan_id": scan_id,
            "finding_name": "后台管理入口暴露",
            "severity": "critical",
            "notes": "先限制匿名访问",
            "owner": "平台安全",
        },
        headers=headers,
    )
    assert create.status_code == 200
    ticket_id = create.json()["data"]["ticket_id"]

    listing = client.get("/api/fix-tickets", headers=headers)
    assert listing.status_code == 200
    assert any(
        ticket["id"] == ticket_id and ticket["owner"] == "平台安全"
        for ticket in listing.json()["data"]["tickets"]
    )

    patch = client.patch(
        f"/api/fix-tickets/{ticket_id}",
        json={
            "status": "confirmed",
            "notes": "已安排网关策略变更",
            "owner": "边界防护组",
        },
        headers=headers,
    )
    assert patch.status_code == 200

    timeline = client.get(f"/api/fix-tickets/{ticket_id}/timeline", headers=headers)
    assert timeline.status_code == 200
    payload = timeline.json()["data"]
    assert payload["ticket"]["owner"] == "边界防护组"
    assert any(item["event_type"] == "note" for item in payload["activities"])
    assert any(item["event_type"] == "owner" for item in payload["activities"])

    exported = client.get(
        f"/api/fix-tickets/{ticket_id}/export?format=markdown",
        headers=headers,
    )
    assert exported.status_code == 200
    assert "markdown" in exported.headers.get("content-type", "")
    assert "负责人：边界防护组" in exported.text
    assert "操作历史" in exported.text
