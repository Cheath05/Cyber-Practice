from conftest import HDR


def first_item(client, pid="01"):
    from cyber_tracker.repo_parser import parse_repo
    from conftest import REPO
    return next(p for p in parse_repo(REPO) if p.id == pid).items[0]


def test_pages_render(client):
    r = client.get("/")
    assert r.status_code == 200 and "Overall progress" in r.text
    r = client.get("/project/07")
    assert r.status_code == 200 and "Active Directory" in r.text
    assert client.get("/project/99").status_code == 404
    assert client.get("/healthz").json()["projects"] == 14


def test_security_headers(client):
    r = client.get("/")
    assert "default-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-frame-options"] == "DENY"


def test_check_toggle_updates_progress(client):
    item = first_item(client)
    r = client.post("/api/check", json={"key": item.key, "checked": True}, headers=HDR)
    assert r.status_code == 200
    assert r.json()["project"]["done"] == 1
    assert r.json()["overall"]["done"] == 1
    r = client.post("/api/check", json={"key": item.key, "checked": False}, headers=HDR)
    assert r.json()["project"]["done"] == 0


def test_milestone_check(client):
    r = client.post("/api/check", json={"key": "ms-cp1", "checked": True}, headers=HDR)
    assert r.status_code == 200
    ms = {m["id"]: m for m in client.get("/api/summary").json()["milestones"]}
    assert ms["cp1"]["done"] is True


def test_unknown_item_rejected(client):
    r = client.post("/api/check", json={"key": "nope", "checked": True}, headers=HDR)
    assert r.status_code == 404


def test_csrf_header_required(client):
    item = first_item(client)
    r = client.post("/api/check", json={"key": item.key, "checked": True})
    assert r.status_code == 403
    r = client.delete("/api/hours/1")
    assert r.status_code == 403


def test_json_content_type_required(client):
    r = client.post("/api/tasks", content="text=hi", headers={**HDR, "Content-Type": "application/x-www-form-urlencoded"})
    assert r.status_code == 415


def test_hours_flow_and_validation(client):
    # P06's final milestone is months away, so logged time makes it "in progress"
    r = client.post("/api/hours", json={"project": "06", "day": "2026-11-18", "hours": 2.5, "note": "juice shop"}, headers=HDR)
    assert r.status_code == 200
    entry_id = r.json()["id"]
    s = client.get("/api/summary").json()
    p06 = next(p for p in s["projects"] if p["id"] == "06")
    assert p06["hours_logged"] == 2.5 and p06["status"] == "in-progress"
    assert s["overall"]["hours_logged"] == 2.5
    assert sum(w["hours"] for w in s["weekly_hours"]) == 2.5
    for bad in ({"project": "02", "hours": 0}, {"project": "02", "hours": 30},
                {"project": "99", "hours": 1}, {"project": "02", "hours": 1, "day": "not-a-date"}):
        assert client.post("/api/hours", json=bad, headers=HDR).status_code in (400, 404)
    assert client.delete(f"/api/hours/{entry_id}", headers=HDR).status_code == 200
    assert client.delete(f"/api/hours/{entry_id}", headers=HDR).status_code == 404


def test_status_behind_and_complete(client):
    # CT_TODAY is 2026-11-20: P01 (due 2026-11-08) with nothing done is behind
    s = client.get("/api/summary").json()
    p01 = next(p for p in s["projects"] if p["id"] == "01")
    assert p01["status"] == "behind"
    from cyber_tracker.repo_parser import parse_repo
    from conftest import REPO
    for item in next(p for p in parse_repo(REPO) if p.id == "01").items:
        client.post("/api/check", json={"key": item.key, "checked": True}, headers=HDR)
    p01 = next(p for p in client.get("/api/summary").json()["projects"] if p["id"] == "01")
    assert p01["status"] == "complete" and p01["pct"] == 100


def test_rating_and_interest_chart(client):
    assert client.post("/api/rating", json={"project": "08", "enjoyed": 5, "natural": 4, "want_more": True}, headers=HDR).status_code == 200
    assert client.post("/api/rating", json={"project": "08", "enjoyed": 9}, headers=HDR).status_code == 400
    s = client.get("/api/summary").json()
    assert [p["id"] for p in s["interest"]] == ["08"]
    assert "Career interest" in client.get("/").text


def test_tasks_crud(client):
    r = client.post("/api/tasks", json={"text": "Register for NCL spring"}, headers=HDR)
    tid = r.json()["id"]
    assert client.post(f"/api/tasks/{tid}", json={"done": True}, headers=HDR).status_code == 200
    assert "Register for NCL spring" in client.get("/").text
    assert client.post("/api/tasks", json={"text": ""}, headers=HDR).status_code == 400
    assert client.delete(f"/api/tasks/{tid}", headers=HDR).status_code == 200


def test_html_is_escaped(client):
    client.post("/api/tasks", json={"text": "<script>alert(1)</script>"}, headers=HDR)
    body = client.get("/").text
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;" in body


def test_export(client):
    client.post("/api/tasks", json={"text": "backup me"}, headers=HDR)
    data = client.get("/api/export").json()
    assert set(data) == {"checks", "hours", "ratings", "tasks"}
    assert data["tasks"][0]["text"] == "backup me"


def test_tailscale_allowlist(tmp_path, monkeypatch):
    monkeypatch.setenv("CT_DB", str(tmp_path / "d.db"))
    monkeypatch.setenv("CT_ALLOWED_LOGINS", "me@example.com")
    from fastapi.testclient import TestClient
    from cyber_tracker.main import create_app
    from conftest import REPO
    c = TestClient(create_app(repo=REPO, db_path=tmp_path / "t.db"))
    assert c.get("/").status_code == 403
    assert c.get("/", headers={"Tailscale-User-Login": "someone@else.com"}).status_code == 403
    assert c.get("/", headers={"Tailscale-User-Login": "Me@Example.com"}).status_code == 200
    assert c.get("/healthz").status_code == 200
