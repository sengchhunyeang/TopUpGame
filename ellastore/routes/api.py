"""JSON API."""

from flask import Blueprint, jsonify, request

from ..catalog import all_games, get_game
from ..services import ValidationError, coupons, orders, players, subscribers

bp = Blueprint("api", __name__, url_prefix="/api")


def error(msg, code=400):
    return jsonify({"ok": False, "error": msg}), code


@bp.errorhandler(ValidationError)
def handle_validation(err):
    return error(str(err))


def payload():
    return request.get_json(silent=True) or {}


def game_from(data):
    game = get_game(data.get("game_id"))
    if game is None:
        raise ValidationError("Game not found")
    return game


@bp.get("/games")
def list_games():
    return jsonify([g.to_dict() for g in all_games()])


@bp.get("/games/<game_id>")
def game_detail(game_id):
    game = get_game(game_id)
    return jsonify(game.to_dict()) if game else error("Game not found", 404)


@bp.post("/player/check")
def check_player():
    data = payload()
    game = game_from(data)
    uid, _server = players.validate(game, data.get("uid"), data.get("server"))
    return jsonify({"ok": True, "name": players.lookup_name(uid)})


@bp.post("/coupon")
def redeem_coupon():
    code, disc = coupons.redeem(payload().get("code"))
    return jsonify({"ok": True, "code": code, "discount": disc})


@bp.post("/orders")
def create_order():
    data = payload()
    order = orders.create(
        game_from(data), data.get("uid"), data.get("server"),
        data.get("item"), data.get("pay"), data.get("coupon"),
    )
    return jsonify({"ok": True, "order": order}), 201


@bp.get("/orders/<order_id>")
def order_detail(order_id):
    order = orders.get(order_id)
    return jsonify({"ok": True, "order": order}) if order else error("Order not found", 404)


@bp.post("/subscribe")
def subscribe():
    subscribers.subscribe(payload().get("email"))
    return jsonify({"ok": True})
