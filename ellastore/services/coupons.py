"""Coupon codes."""

from . import ValidationError

# Coupon code -> discount fraction
COUPONS = {"ELLA10": 0.10}


def normalise(code):
    return str(code or "").strip().upper()


def redeem(code):
    """Return (code, discount) or raise ValidationError."""
    code = normalise(code)
    if not code:
        raise ValidationError("Enter a coupon code")
    if code not in COUPONS:
        raise ValidationError("Invalid coupon code")
    return code, COUPONS[code]
