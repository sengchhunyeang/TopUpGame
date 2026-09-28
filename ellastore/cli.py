"""Flask CLI commands:  flask --app ellastore <command>"""

import os
import random
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import click
from flask import current_app
from werkzeug.security import generate_password_hash

from .catalog import all_games
from .db import get_db
from .services import players
from .services.orders import STATUSES

# Relative order volume per game and status mix for demo data.
DEMO_POPULARITY = {"mlbb": 30, "freefire": 20, "pubg": 12, "genshin": 10, "bloodstrike": 8, "hok": 6, "magicchess": 5}
DEMO_STATUS_MIX = {"delivered": 55, "paid": 15, "pending_payment": 18, "cancelled": 8, "refunded": 4}
assert set(DEMO_STATUS_MIX) <= set(STATUSES)


@click.command("init-admin")
@click.option("--username", default="admin", show_default=True)
@click.password_option()
def init_admin(username, password):
    """Write admin credentials and a SECRET_KEY to instance/config.py."""
    path = os.path.join(current_app.instance_path, "config.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Local secrets - do not commit (instance/ is gitignored)\n")
        f.write(f"SECRET_KEY = {secrets.token_hex(32)!r}\n")
        f.write(f"ADMIN_USERNAME = {username!r}\n")
        f.write(f"ADMIN_PASSWORD_HASH = {generate_password_hash(password)!r}\n")
    click.echo(f"Admin '{username}' saved to {path}. Restart the server to apply.")


@click.command("seed-demo")
@click.option("--count", default=80, show_default=True, help="Number of demo orders.")
@click.option("--days", default=30, show_default=True, help="Spread orders over the last N days.")
def seed_demo(count, days):
    """Insert random demo orders and subscribers (development only)."""
    rng = random.Random()
    games = all_games()
    popularity = [DEMO_POPULARITY.get(g.id, 3) for g in games]
    statuses, status_weights = zip(*DEMO_STATUS_MIX.items())
    now = datetime.now(timezone.utc)
    db = get_db()
    for _ in range(count):
        game = rng.choices(games, weights=popularity)[0]
        product = rng.choice(game.products)
        uid = str(rng.randint(10_000_000, 999_999_999))
        disc = 0.10 if rng.random() < 0.15 else 0.0
        created = now - timedelta(days=rng.random() * days)
        db.execute(
            """INSERT INTO orders (id, game_id, player_id, server, player_name, item, subtotal, discount,
                                   total, coupon, pay_method, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (uuid.uuid4().hex[:12].upper(), game.id, uid,
             str(rng.randint(1000, 9999)) if game.server == "text" else (rng.choice(game.servers) if game.servers else None),
             players.lookup_name(uid), product.title, product.price, disc,
             round(product.price * (1 - disc), 2), "ELLA10" if disc else None, "khqr",
             rng.choices(statuses, weights=status_weights)[0], created.isoformat(timespec="seconds")),
        )
    for i in range(12):
        db.execute("INSERT OR IGNORE INTO subscribers (email, created_at) VALUES (?, ?)",
                   (f"demo{i + 1}@example.com", (now - timedelta(days=rng.random() * days)).isoformat(timespec="seconds")))
    db.commit()
    click.echo(f"Inserted {count} demo orders and 12 demo subscribers.")


def init_app(app):
    app.cli.add_command(init_admin)
    app.cli.add_command(seed_demo)
