"""Admin pages."""

import csv
import io
import math

from flask import Response, abort, flash, redirect, render_template, request, url_for

from ..catalog import all_games, get_game
from ..services import ValidationError, orders, reports, subscribers
from . import bp
from .auth import login_required

PER_PAGE = 20


@bp.app_template_filter("game_name")
def game_name_filter(game_id):
    return reports.game_name(game_id)


@bp.app_template_filter("nice_ceil")
def nice_ceil(value):
    """Round a chart maximum up to a clean axis value (1, 2, 2.5, 5 x 10^n)."""
    if not value or value <= 0:
        return 10
    exp = 10 ** math.floor(math.log10(value))
    for step in (1, 2, 2.5, 5, 10):
        if value <= step * exp:
            return step * exp
    return 10 * exp


@bp.context_processor
def inject_admin_nav():
    return {"pending_count": reports.status_counts().get("pending_payment", 0)}


@bp.route("/")
@login_required
def dashboard():
    daily = reports.daily_revenue(14)
    return render_template(
        "admin/dashboard.html",
        stats=reports.summary(),
        daily=daily,
        daily_total=sum(d["revenue"] for d in daily),
        games=reports.by_game(),
        recent=orders.search(per_page=8)[0],
    )


@bp.route("/orders")
@login_required
def order_list():
    status = request.args.get("status") or None
    game_id = request.args.get("game") or None
    q = request.args.get("q", "").strip() or None
    page = max(request.args.get("page", 1, type=int), 1)
    rows, total = orders.search(status, game_id, q, page, PER_PAGE)
    filters = {"status": status or "", "game": game_id or "", "q": q or ""}
    return render_template(
        "admin/orders.html",
        orders=rows,
        total=total,
        page=page,
        pages=max(math.ceil(total / PER_PAGE), 1),
        filters=filters,
        query_args={k: v for k, v in filters.items() if v},
        status_counts=reports.status_counts(),
        statuses=orders.STATUSES,
        games=all_games(),
    )


@bp.route("/orders/<order_id>")
@login_required
def order_detail(order_id):
    order = orders.get(order_id)
    if order is None:
        abort(404)
    return render_template("admin/order_detail.html", order=order, game=get_game(order["game_id"]),
                           statuses=orders.STATUSES)


@bp.post("/orders/<order_id>/status")
@login_required
def order_status(order_id):
    try:
        orders.update_status(order_id, request.form.get("status"))
        flash(f"Order {order_id} marked as {request.form['status'].replace('_', ' ')}", "success")
    except ValidationError as err:
        flash(str(err), "error")
    return redirect(url_for("admin.order_detail", order_id=order_id))


@bp.route("/subscribers")
@login_required
def subscriber_list():
    return render_template("admin/subscribers.html", subscribers=subscribers.all_subscribers())


@bp.route("/subscribers.csv")
@login_required
def subscriber_csv():
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["email", "subscribed_at"])
    for s in subscribers.all_subscribers():
        writer.writerow([s["email"], s["created_at"]])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=subscribers.csv"})


@bp.route("/games")
@login_required
def game_list():
    return render_template("admin/games.html", rows=reports.by_game())
