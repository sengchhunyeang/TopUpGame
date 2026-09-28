from ellastore.catalog import all_games


def test_home_renders_every_game(client):
    html = client.get("/").get_data(as_text=True)
    for game in all_games():
        assert f'href="/game/{game.id}"' in html
    assert "data-carousel" in html


def test_home_search_hides_non_matching(client):
    html = client.get("/?q=genshin").get_data(as_text=True)
    assert 'data-name="genshin impact" class="relative' in html
    assert 'data-name="pubg mobile" class="hidden ' in html


def test_topup_page_renders_products_and_server_field(client):
    html = client.get("/game/genshin").get_data(as_text=True)
    assert "Blessing of the Welkin Moon" in html
    assert "$99.99" in html
    assert 'id="srv"' in html
    assert 'id="sid"' not in html


def test_unknown_game_is_404(client):
    r = client.get("/game/nope")
    assert r.status_code == 404
    assert "Page not found" in r.get_data(as_text=True)
