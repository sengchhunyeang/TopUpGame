"""Player ID validation and lookup (lookup is a deterministic demo mock)."""

import re

from . import ValidationError

UID_RE = re.compile(r"^\d{5,}$")
SID_RE = re.compile(r"^\d{2,}$")

DEMO_NAMES = ("ShadowNinja_99", "PRO_Gamer_KH", "DragonSlayer_X", "NightWolf_07",
              "KhmerKing_88", "StormRider_23", "PhantomAce", "SkyHunter_KH")


def validate(game, uid, server):
    """Return a normalised (uid, server) or raise ValidationError."""
    uid = str(uid or "").strip()
    server = str(server or "").strip()
    if not uid:
        raise ValidationError("Please enter your Game ID")
    if not UID_RE.match(uid):
        raise ValidationError("Enter a valid Game ID (digits only, 5+)")
    if game.server == "text" and not SID_RE.match(server):
        raise ValidationError("Enter a valid Server ID")
    if game.server == "select" and server not in game.servers:
        raise ValidationError("Choose a valid server")
    return uid, (server if game.server else None)


def lookup_name(uid):
    """Replace with a real provider API call."""
    h = 0
    for c in uid:
        h = (h * 31 + int(c)) % 997
    return DEMO_NAMES[h % len(DEMO_NAMES)]
