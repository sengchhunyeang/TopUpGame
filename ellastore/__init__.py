"""ELLASTORE - game top-up web app (Flask application factory)."""

import os
from datetime import datetime, timedelta

from flask import Flask
from werkzeug.security import generate_password_hash

from . import cli, content, db
from .catalog import all_games


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.environ.get("TOPUP_DB") or os.path.join(app.instance_path, "topup.db"),
        ADMIN_USERNAME="admin",
        # Default login admin / admin123; override with `flask --app ellastore init-admin`
        ADMIN_PASSWORD_HASH=generate_password_hash("admin123"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )
    # Local secrets (SECRET_KEY, admin credentials) written by `init-admin`.
    app.config.from_pyfile("config.py", silent=True)
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)
    app.json.sort_keys = False

    db.init_app(app)
    cli.init_app(app)

    from .admin import bp as admin_bp
    from .routes import api, pages
    app.register_blueprint(pages.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(admin_bp)

    app.add_template_filter(lambda n: f"${n:,.2f}", "money")
    app.add_template_filter(lambda s: datetime.fromisoformat(s).strftime("%d %b %Y, %H:%M"), "datetime")
    app.add_template_filter(lambda s: (s or "").replace("_", " ").capitalize(), "humanize")

    @app.context_processor
    def inject_globals():
        # Available in every template (header menu, footer, etc.)
        return {"store": content.STORE, "nav_games": all_games()}

    return app
