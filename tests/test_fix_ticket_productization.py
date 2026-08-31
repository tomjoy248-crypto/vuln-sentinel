from test_main_endpoints import (
    _auth_headers,
    _create_scan_record,
    _demo_user_id,
    client,
)
from test_routers import _make_team_with_member


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
            "owner": "demo",
        },
        headers=headers,
    )
    assert create.status_code == 200
    ticket_id = create.json()["data"]["ticket_id"]

    listing = client.get("/api/fix-tickets", headers=headers)
    assert listing.status_code == 200
    assert any(
        ticket["id"] == ticket_id and ticket["owner"] == "demo"
        for ticket in listing.json()["data"]["tickets"]
    )

    patch = client.patch(
        f"/api/fix-tickets/{ticket_id}",
        json={
            "status": "confirmed",
            "notes": "已安排网关策略变更",
            "owner": "demo",
        },
        headers=headers,
    )
    assert patch.status_code == 200

    timeline = client.get(f"/api/fix-tickets/{ticket_id}/timeline", headers=headers)
    assert timeline.status_code == 200
    payload = timeline.json()["data"]
    assert payload["ticket"]["owner"] == "demo"
    assert any(item["event_type"] == "note" for item in payload["activities"])

    exported = client.get(
        f"/api/fix-tickets/{ticket_id}/export?format=markdown",
        headers=headers,
    )
    assert exported.status_code == 200
    assert "markdown" in exported.headers.get("content-type", "")
    assert "负责人：demo" in exported.text
    assert "操作历史" in exported.text


def test_fix_ticket_supports_assignee_and_reviewer_with_team_validation():
    admin_token, admin_id, _member_token, member_id = _make_team_with_member()
    headers = {"Authorization": f"Bearer {admin_token}"}
    team_resp = client.get("/api/team", headers=headers)
    assert team_resp.status_code == 200
    members = team_resp.json()["members"]
    admin_name = next(item["username"] for item in members if item["user_id"] == admin_id)
    member_name = next(item["username"] for item in members if item["user_id"] == member_id)

    scan_id = _create_scan_record(admin_id)
    create = client.post(
        "/api/fix-tickets",
        json={
            "scan_id": scan_id,
            "finding_name": "管理接口匿名可访问",
            "severity": "critical",
            "owner": admin_name,
            "assignee": member_name,
            "reviewer": admin_name,
        },
        headers=headers,
    )
    assert create.status_code == 200
    ticket_id = create.json()["data"]["ticket_id"]

    detail = client.get(f"/api/fix-tickets/{ticket_id}", headers=headers)
    assert detail.status_code == 200
    ticket = detail.json()["data"]["ticket"]
    assert ticket["assignee"] == member_name
    assert ticket["reviewer"] == admin_name

    timeline = client.get(f"/api/fix-tickets/{ticket_id}/timeline", headers=headers)
    assert timeline.status_code == 200
    activities = timeline.json()["data"]["activities"]
    assert any(item["event_type"] == "assignee" for item in activities)
    assert any(item["event_type"] == "reviewer" for item in activities)


def test_fix_ticket_rejects_non_team_actor():
    headers = _auth_headers()
    scan_id = _create_scan_record(_demo_user_id())
    create = client.post(
        "/api/fix-tickets",
        json={
            "scan_id": scan_id,
            "finding_name": "用户数据接口匿名可访问",
            "severity": "high",
            "owner": "外部成员",
        },
        headers=headers,
    )
    assert create.status_code == 400
    assert "当前团队成员" in create.json()["error"]
