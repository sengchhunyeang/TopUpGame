# ELLASTORE – Game Top-up (Flask)

## Run

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python run.py          # http://127.0.0.1:5000
.\.venv\Scripts\python -m pytest       # tests
```

`FLASK_DEBUG=1` enables auto-reload, `PORT` changes the port, `TOPUP_DB` changes the SQLite file (default `instance/topup.db`).

## Admin panel

```powershell
.\.venv\Scripts\flask --app ellastore init-admin          # set username/password (writes instance/config.py)
.\.venv\Scripts\flask --app ellastore seed-demo --count 90 # optional: fake orders for development
```

Restart the server, then open http://127.0.0.1:5000/admin.

- **Dashboard**: revenue, average order value, awaiting-payment total, orders today, 14-day revenue chart, top games, recent orders
- **Orders**: status tabs, search by order # / player ID / name, filter by game, pagination; detail page with status update
- **Games**: catalog with product counts, price ranges, orders and revenue per game
- **Subscribers**: list and CSV export

Revenue counts only `paid` and `delivered` orders. Order statuses: `pending_payment → paid → delivered`, or `cancelled` / `refunded`.
Security: hashed password, 8-hour session cookie (HttpOnly, SameSite=Lax), CSRF token on every admin form, `next` redirects restricted to `/admin`.
`instance/config.py` also holds a generated `SECRET_KEY`; in production set `SECRET_KEY` there or via the environment and put the app behind HTTPS.

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
  admin/                     admin blueprint (/admin): auth.py (login, CSRF), views.py
  services/reports.py        dashboard aggregates
  cli.py                     init-admin, seed-demo
  templates/admin/           admin layout, pages and components.html (stat_tile, panel,
                             status_badge, orders_table, revenue_chart, game_bars, pagination)
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
