"""Order creation and lookup."""

import uuid

from ..db import get_db, now_iso
from . import ValidationError, coupons, players

PAY_METHODS = ("khqr", "wallet")


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
