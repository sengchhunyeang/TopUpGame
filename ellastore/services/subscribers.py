"""Newsletter subscribers."""

import re

from ..db import get_db, now_iso
from . import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def subscribe(email):
    email = str(email or "").strip().lower()
    if not EMAIL_RE.match(email):
        raise ValidationError("Please enter a valid email")
    db = get_db()
    db.execute("INSERT OR IGNORE INTO subscribers (email, created_at) VALUES (?, ?)", (email, now_iso()))
    db.commit()
    return email


def all_subscribers():
    rows = get_db().execute("SELECT email, created_at FROM subscribers ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]
