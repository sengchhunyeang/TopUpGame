# ELLASTORE – Game Top-up (Flask)

## Run

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python run.py          # http://127.0.0.1:5000
.\.venv\Scripts\python -m pytest       # tests
```

`FLASK_DEBUG=1` enables auto-reload, `PORT` changes the port, `TOPUP_DB` changes the SQLite file (default `instance/topup.db`).

## Structure

```
run.py                       entry point (create_app())
ellastore/
  __init__.py                application factory
  catalog.py                 Game / Product dataclasses + the game list   <- edit games & prices here
  content.py                 site copy: slides, features, payment methods, footer
  db.py                      SQLite connection + schema
  services/                  business logic (no Flask/HTTP)
    players.py  coupons.py  orders.py  subscribers.py
  routes/
    pages.py                 HTML pages:  /  and  /game/<id>
    api.py                   JSON API:    /api/...
  templates/
    base.html                layout
    partials/                header.html, footer.html
    pages/                   home.html, topup.html, 404.html
    components/              reusable Jinja macros (see below)
  static/
    css/style.css
    js/main.js               entry: shared components + current page
    js/lib/                  dom.js, api.js
    js/components/           one module per interactive component
    js/pages/                home.js, topup.js
tests/                       pytest: pages + API
```

## Components

Jinja macros (`templates/components/`), import with `{% from "components/cards.html" import game_card %}`:

| File | Macros |
|---|---|
| `icons.html` | `icon(name, cls)`, `product_icon(kind, color)` |
| `ui.html` | `pill`, `section_head` (call-block for right side), `card` (call-block), `step_heading`, `empty_state`, `text_input`, `payment_badges`, `khmer_flag`, `game_logo`, `game_art` |
| `cards.html` | `game_card`, `feature_card`, `product_card`, `payment_option` |
| `carousel.html` | `carousel(slides, interval)` |
| `topup.html` | `game_hero`, `player_status`, `coupon_field`, `pay_bar`, `mascot` |

JS components (`static/js/components/`) attach behaviour to the markup those macros render:

| Module | Pairs with |
|---|---|
| `carousel.js` → `initCarousel(el)` | `carousel()` |
| `choice-group.js` → `createChoiceGroup(el, {initial, onChange})` | any group of `product_card` / `payment_option` |
| `player-check.js` → `createPlayerCheck(el, getPayload)` | `player_status()` |
| `coupon-field.js` → `createCouponField(el, onChange)` | `coupon_field()` |
| `favorites.js`, `subscribe.js`, `header.js`, `toast.js` | game cards, footer form, header, `#toast` |

Selection and status states are expressed with `aria-pressed` / `data-state` attributes and styled in `style.css`, so the JS only flips attributes.

## Adding a game

Add a `Game(...)` to `GAMES` in `ellastore/catalog.py`. It appears automatically on the home grid, the menu, `/game/<id>`, and the API.

## API

| Method | Path | Body |
|---|---|---|
| GET | `/api/games`, `/api/games/<id>` | |
| POST | `/api/player/check` | `{game_id, uid, server}` |
| POST | `/api/coupon` | `{code}` |
| POST | `/api/orders` | `{game_id, uid, server, item, pay, coupon}` |
| GET | `/api/orders/<id>` | |
| POST | `/api/subscribe` | `{email}` |

Prices and discounts are computed on the server; the client total is never trusted.
The player lookup is still a mock (`services/players.py:lookup_name`) and no payment gateway is connected; orders are saved with status `pending_payment`.
