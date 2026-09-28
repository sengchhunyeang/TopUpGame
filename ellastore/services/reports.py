"""Aggregates for the admin dashboard."""

from datetime import datetime, timedelta, timezone

from ..catalog import all_games, get_game
from ..db import get_db
from .orders import PAID_STATUSES

_PAID = f"status IN ({', '.join('?' * len(PAID_STATUSES))})"


def _today():
    return datetime.now(timezone.utc).date()


def summary():
    db = get_db()
    today = _today().isoformat()
    row = db.execute(
        f"""SELECT
              COUNT(*)                                                   AS orders,
              COALESCE(SUM(CASE WHEN {_PAID} THEN total END), 0)         AS revenue,
              COALESCE(SUM(CASE WHEN {_PAID} THEN 1 END), 0)             AS paid_orders,
              COALESCE(SUM(CASE WHEN status = 'pending_payment' THEN 1 END), 0)     AS pending,
              COALESCE(SUM(CASE WHEN status = 'pending_payment' THEN total END), 0) AS pending_value,
              COALESCE(SUM(CASE WHEN substr(created_at, 1, 10) = ? THEN 1 END), 0)  AS today
            FROM orders""",
        (*PAID_STATUSES, *PAID_STATUSES, today),
    ).fetchone()
    stats = dict(row)
    stats["avg_order"] = stats["revenue"] / stats["paid_orders"] if stats["paid_orders"] else 0.0
    stats["subscribers"] = db.execute("SELECT COUNT(*) FROM subscribers").fetchone()[0]
    return stats


def daily_revenue(days=14):
    """Paid revenue and order count per UTC day, oldest first, gaps filled with 0."""
    end = _today()
    start = end - timedelta(days=days - 1)
    rows = get_db().execute(
        f"""SELECT substr(created_at, 1, 10) AS day, SUM(total) AS revenue, COUNT(*) AS orders
            FROM orders WHERE {_PAID} AND substr(created_at, 1, 10) >= ?
            GROUP BY day""",
        (*PAID_STATUSES, start.isoformat()),
    ).fetchall()
    by_day = {r["day"]: r for r in rows}
    out = []
    for i in range(days):
        d = start + timedelta(days=i)
        r = by_day.get(d.isoformat())
        out.append({"date": d, "revenue": round(r["revenue"], 2) if r else 0.0, "orders": r["orders"] if r else 0})
    return out


def by_game():
    """Per-game totals for every catalog game (zeros included), highest revenue first."""
    rows = get_db().execute(
        f"""SELECT game_id, COUNT(*) AS orders,
                   COALESCE(SUM(CASE WHEN {_PAID} THEN total END), 0) AS revenue
            FROM orders GROUP BY game_id""",
        PAID_STATUSES,
    ).fetchall()
    stats = {r["game_id"]: r for r in rows}
    out = [
        {"game": g, "orders": stats[g.id]["orders"] if g.id in stats else 0,
         "revenue": round(stats[g.id]["revenue"], 2) if g.id in stats else 0.0}
        for g in all_games()
    ]
    return sorted(out, key=lambda r: r["revenue"], reverse=True)


def status_counts():
    rows = get_db().execute("SELECT status, COUNT(*) AS n FROM orders GROUP BY status").fetchall()
    return {r["status"]: r["n"] for r in rows}


def game_name(game_id):
    game = get_game(game_id)
    return game.name if game else game_id
