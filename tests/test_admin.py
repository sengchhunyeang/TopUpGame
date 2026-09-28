import pytest
from werkzeug.security import generate_password_hash

from ellastore import create_app

PASSWORD = "test-pass-123"


@pytest.fixture
def app(tmp_path):
    return create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "test.db"),
        "SECRET_KEY": "test",
        "ADMIN_USERNAME": "admin",
        "ADMIN_PASSWORD_HASH": generate_password_hash(PASSWORD),
    })


def csrf(client):
    """Render a page that embeds a CSRF token and return it."""
    client.get("/admin/", follow_redirects=True)
    with client.session_transaction() as s:
        return s["csrf"]


def login(client, password=PASSWORD):
    return client.post("/admin/login", data={"username": "admin", "password": password, "csrf_token": csrf(client)})


def place_order(client, **kw):
    body = {"game_id": "pubg", "uid": "888888", "item": 1, "pay": "khqr", **kw}
    return client.post("/api/orders", json=body).get_json()["order"]


def test_admin_requires_login(client):
    for path in ("/admin/", "/admin/orders", "/admin/games", "/admin/subscribers", "/admin/subscribers.csv"):
        r = client.get(path)
        assert r.status_code == 302 and "/admin/login" in r.headers["Location"]


def test_login_rejects_bad_password_and_missing_csrf(client):
    assert b"Invalid username or password" in login(client, "wrong").data
    r = client.post("/admin/login", data={"username": "admin", "password": PASSWORD})
    assert r.status_code == 400


def test_login_redirect_stays_inside_admin(client):
    token = csrf(client)
    r = client.post("/admin/login?next=https://evil.example/", data={"username": "admin", "password": PASSWORD, "csrf_token": token})
    assert r.headers["Location"] == "/admin/"


def test_dashboard_reports_paid_revenue(client):
    order = place_order(client)                 # $4.99, pending
    login(client)
    token = csrf(client)
    client.post(f"/admin/orders/{order['id']}/status", data={"status": "paid", "csrf_token": token})
    place_order(client)                         # second one stays pending

    html = client.get("/admin/").get_data(as_text=True)
    assert "$4.99" in html                      # revenue = only the paid order
    assert "1 paid orders" in html
    assert f"#{order['id']}" in html


def test_order_filters_and_detail(client):
    a = place_order(client)
    b = place_order(client, game_id="genshin", server="Asia", item=0)
    login(client)
    html = client.get("/admin/orders?game=genshin").get_data(as_text=True)
    assert b["id"] in html and a["id"] not in html
    assert a["id"] in client.get(f"/admin/orders?q={a['id'][:6]}").get_data(as_text=True)
    assert "Update status" in client.get(f"/admin/orders/{a['id']}").get_data(as_text=True)
    assert client.get("/admin/orders/NOPE").status_code == 404


def test_status_update_validates(client):
    order = place_order(client)
    login(client)
    token = csrf(client)
    r = client.post(f"/admin/orders/{order['id']}/status", data={"status": "bogus", "csrf_token": token}, follow_redirects=True)
    assert b"Unknown status" in r.data
    r = client.post(f"/admin/orders/{order['id']}/status", data={"status": "delivered"})  # no CSRF token
    assert r.status_code == 400


def test_subscribers_csv(client):
    client.post("/api/subscribe", json={"email": "fan@example.com"})
    login(client)
    r = client.get("/admin/subscribers.csv")
    assert r.mimetype == "text/csv" and b"fan@example.com" in r.data


def test_default_admin_login(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "x.db")})
    client = app.test_client()
    client.get("/admin/login")
    with client.session_transaction() as s:
        token = s["csrf"]
    r = client.post("/admin/login", data={"username": "admin", "password": "admin123", "csrf_token": token})
    assert r.status_code == 302 and client.get("/admin/").status_code == 200


def test_logout(client):
    login(client)
    client.post("/admin/logout", data={"csrf_token": csrf(client)})
    assert client.get("/admin/").status_code == 302
