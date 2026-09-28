def post(client, path, **body):
    r = client.post(path, json=body)
    return r.status_code, r.get_json()


def test_games(client):
    games = client.get("/api/games").get_json()
    assert len(games) == 10
    assert client.get("/api/games/mlbb").get_json()["server"] == "text"
    assert client.get("/api/games/nope").status_code == 404


def test_player_check(client):
    assert post(client, "/api/player/check", game_id="mlbb", uid="123")[1]["error"].startswith("Enter a valid Game ID")
    assert post(client, "/api/player/check", game_id="mlbb", uid="123456")[1]["error"] == "Enter a valid Server ID"
    status, body = post(client, "/api/player/check", game_id="mlbb", uid="123456", server="12")
    assert status == 200 and body["ok"] and body["name"]
    assert post(client, "/api/player/check", game_id="genshin", uid="123456", server="Mars")[1]["error"] == "Choose a valid server"


def test_coupon(client):
    assert post(client, "/api/coupon", code="ella10")[1] == {"ok": True, "code": "ELLA10", "discount": 0.1}
    assert post(client, "/api/coupon", code="nope")[0] == 400


def test_order_uses_server_price_and_discount(client):
    status, body = post(client, "/api/orders", game_id="genshin", uid="888888", server="Asia",
                        item=2, pay="khqr", coupon="ELLA10", total=0.01)
    assert status == 201
    order = body["order"]
    assert order["item"] == "980+110 Genesis Crystals"
    assert order["total"] == 13.49
    assert client.get(f"/api/orders/{order['id']}").get_json()["order"]["total"] == 13.49


def test_order_validation(client):
    assert post(client, "/api/orders", game_id="pubg", uid="888888", item=99, pay="khqr")[1]["error"] == "Please choose a product"
    assert post(client, "/api/orders", game_id="pubg", uid="888888", item=0, pay="wallet")[1]["error"] == "Insufficient wallet balance"
    assert post(client, "/api/orders", game_id="pubg", uid="888888", item=0, pay="khqr", coupon="BAD")[1]["error"] == "Invalid coupon code"


def test_subscribe(client):
    assert post(client, "/api/subscribe", email="a@b.co")[1] == {"ok": True}
    assert post(client, "/api/subscribe", email="bad")[0] == 400


def test_unknown_api_route_is_json_404(client):
    r = client.get("/api/nope")
    assert r.status_code == 404 and r.get_json()["ok"] is False
