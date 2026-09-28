"""ELLASTORE - game top-up web app (Flask application factory)."""

import os

from flask import Flask

from . import content, db
from .catalog import all_games


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.environ.get("TOPUP_DB") or os.path.join(app.instance_path, "topup.db"),
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)
    app.json.sort_keys = False

    db.init_app(app)

    from .routes import api, pages
    app.register_blueprint(pages.bp)
    app.register_blueprint(api.bp)

    app.add_template_filter(lambda n: f"${n:,.2f}", "money")

    @app.context_processor
    def inject_globals():
        # Available in every template (header menu, footer, etc.)
        return {"store": content.STORE, "nav_games": all_games()}

    return app
