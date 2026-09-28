"""Site copy and static content used by the templates."""

STORE = {
    "name": "Ella Store",
    "tagline": "Ella Store - Official Partner",
    "blurb": "Reliable game top-ups. Fast delivery.",
    "year": 2026,
    "developer": "MorganRapidAPI",
    "top_products": ("mlbb", "freefire", "bloodstrike", "magicchess"),
    "about_links": ("About Us", "Visions", "Polices"),
    "socials": ("discord", "twitter", "facebook", "youtube"),
}

# Home carousel. `theme` maps to a .banner-* CSS class.
SLIDES = (
    {"theme": "a", "title": "បង្កើនពេលវេលា", "highlight": "ELLAST4RE.COM",
     "lines": ("អ្នកលក់ទុកចិត្តបាន ទូទាត់រហ័ស ១០០%", "សេវាកម្មពិសេស តម្លៃសមរម្យ")},
    {"theme": "b", "title": "TOP UP", "highlight": "INSTANTLY",
     "lines": ("Direct to your Player ID in seconds", "Pay with ABA KHQR")},
    {"theme": "c", "title": "BEST PRICES", "highlight": "EVERY DAY",
     "lines": ("Lowest rates for popular games", "24/7 customer support")},
)

FEATURES = (
    {"icon": "bolt", "title": "Instant Delivery", "text": "Direct to Player ID immediately."},
    {"icon": "shield-badge", "title": "Secure Payment", "text": "100% safe & protected."},
    {"icon": "headset", "title": "24/7 Support", "text": "Always here to help you."},
    {"icon": "tag", "title": "Best Prices", "text": "Lowest rates for games."},
)

PAYMENT_METHODS = (
    {"id": "khqr", "title": "ABA KHQR", "text": "Scan with any Bakong-supported app"},
    {"id": "wallet", "title": "Wallet balance", "text": "Balance: $0.00"},
)
