"""Admin login, session guard and CSRF protection."""

import hmac
import secrets
from functools import wraps
from urllib.parse import urlparse

from flask import abort, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from . import bp


def is_configured():
    return bool(current_app.config.get("ADMIN_PASSWORD_HASH"))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin.login", next=request.full_path.rstrip("?")))
        return view(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------------- CSRF
def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


@bp.app_context_processor
def inject_csrf():
    return {"csrf_token": csrf_token}


@bp.before_request
def check_csrf():
    if request.method == "POST":
        sent = request.form.get("csrf_token", "")
        if not hmac.compare_digest(sent, session.get("csrf", "")):
            abort(400, "Invalid CSRF token")


# ---------------------------------------------------------------- views
def _safe_next(target):
    """Only allow redirects back into the admin panel."""
    parsed = urlparse(target or "")
    if not parsed.netloc and not parsed.scheme and parsed.path.startswith("/admin"):
        return target
    return url_for("admin.dashboard")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST" and is_configured():
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user_ok = hmac.compare_digest(username, current_app.config.get("ADMIN_USERNAME", "admin"))
        pass_ok = check_password_hash(current_app.config["ADMIN_PASSWORD_HASH"], password)
        if user_ok and pass_ok:
            session.clear()
            session["admin"] = username
            session.permanent = True
            return redirect(_safe_next(request.args.get("next")))
        flash("Invalid username or password", "error")

    return render_template("admin/login.html", configured=is_configured())


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))
