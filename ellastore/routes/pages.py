"""HTML pages."""

from flask import Blueprint, abort, jsonify, render_template, request

from .. import content
from ..catalog import all_games, get_game, search_games

bp = Blueprint("pages", __name__)


@bp.route("/")
def home():
    q = request.args.get("q", "").strip()
    return render_template(
        "pages/home.html",
        games=all_games(),
        match_ids={g.id for g in search_games(q)},
        query=q,
        slides=content.SLIDES,
        features=content.FEATURES,
    )


@bp.route("/game/<game_id>")
def topup(game_id):
    game = get_game(game_id)
    if game is None:
        abort(404)
    return render_template(
        "pages/topup.html",
        game=game,
        payment_methods=content.PAYMENT_METHODS,
        footer_class="pb-24",  # room for the fixed pay bar
    )


@bp.app_errorhandler(404)
def not_found(_err):
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Not found"}), 404
    return render_template("pages/404.html"), 404
