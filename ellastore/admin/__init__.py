"""Admin panel blueprint (mounted at /admin)."""

from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")

from . import auth, views  # noqa: E402,F401  (register routes)
