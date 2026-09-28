"""Order creation, lookup and admin management."""

import uuid

from ..db import get_db, now_iso
from . import ValidationError, coupons, players

PAY_METHODS = ("khqr", "wallet")

# Order lifecycle. Revenue counts only PAID_STATUSES.
STATUSES = ("pending_payment", "paid", "delivered", "cancelled", "refunded")
PAID_STATUSES = ("paid", "delivered")


def create(game, uid, server, product_index, pay, coupon=None):
    uid, server = players.validate(game, uid, server)

    try:
        product = game.product(int(product_index))
    except (TypeError, ValueError):
        product = None
    if product is None:
        raise ValidationError("Please choose a product")

    if pay not in PAY_METHODS:
        raise ValidationError("Choose a payment method")

    code, disc = coupons.redeem(coupon) if coupons.normalise(coupon) else (None, 0.0)

    # Prices are always computed server-side; never trust the client total.
    total = round(product.price * (1 - disc), 2)

    if pay == "wallet":
        raise ValidationError("Insufficient wallet balance")

    order = {
        "id": uuid.uuid4().hex[:12].upper(),
        "game_id": game.id,
        "player_id": uid,
        "server": server,
        "player_name": players.lookup_name(uid),
        "item": product.title,
        "subtotal": product.price,
        "discount": disc,
        "total": total,
        "coupon": code,
        "pay_method": pay,
        "status": "pending_payment",
        "created_at": now_iso(),
    }
    db = get_db()
    db.execute(
        f"INSERT INTO orders ({', '.join(order)}) VALUES ({', '.join('?' * len(order))})",
        list(order.values()),
    )
    db.commit()
    return order


def get(order_id):
    row = get_db().execute("SELECT * FROM orders WHERE id = ?", (str(order_id).upper(),)).fetchone()
    return dict(row) if row else None


def search(status=None, game_id=None, q=None, page=1, per_page=20):
    """Filtered, newest-first page of orders. Returns (rows, total_count)."""
    where, args = [], []
    if status:
        where.append("status = ?")
        args.append(status)
    if game_id:
        where.append("game_id = ?")
        args.append(game_id)
    if q:
        where.append("(id LIKE ? OR player_id LIKE ? OR player_name LIKE ?)")
        args += [f"%{q.strip().upper()}%", f"%{q.strip()}%", f"%{q.strip()}%"]
    clause = f"WHERE {' AND '.join(where)}" if where else ""

    db = get_db()
    total = db.execute(f"SELECT COUNT(*) FROM orders {clause}", args).fetchone()[0]
    rows = db.execute(
        f"SELECT * FROM orders {clause} ORDER BY created_at DESC, id LIMIT ? OFFSET ?",
        args + [per_page, (max(page, 1) - 1) * per_page],
    ).fetchall()
    return [dict(r) for r in rows], total


def update_status(order_id, status):
    if status not in STATUSES:
        raise ValidationError("Unknown status")
    db = get_db()
    cur = db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, str(order_id).upper()))
    db.commit()
    if cur.rowcount == 0:
        raise ValidationError("Order not found")
