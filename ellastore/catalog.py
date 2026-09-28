"""Game catalog.

Put your OFFICIAL, licensed image URLs in `cover`, `icon` and `banner` (and
`image` on a Product). When a URL is empty or fails to load, a styled
fallback is shown automatically.

Product kinds: diamond, pass, coin, crystal.
"""

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Product:
    title: str
    price: float
    kind: str = "diamond"
    image: str = ""


@dataclass(frozen=True)
class Game:
    id: str
    name: str
    logo: tuple[str, ...]          # logo text, one entry per line
    grad: str                      # CSS background used as fallback art
    color: str                     # accent colour for product icons
    unit: str
    products: tuple[Product, ...]
    server: str | None = None      # None | "text" (zone id input) | "select"
    servers: tuple[str, ...] = ()
    flag: bool = False             # show Cambodian flag badge
    cover: str = ""
    icon: str = ""
    banner: str = ""

    def to_dict(self):
        return asdict(self)

    def product(self, index):
        return self.products[index] if 0 <= index < len(self.products) else None


def _products(*rows):
    return tuple(Product(*row) for row in rows)


MLBB_PRODUCTS = _products(
    ("86 Diamonds", 1.20), ("172 Diamonds", 2.40), ("257 Diamonds", 3.55),
    ("344 Diamonds", 4.70), ("429 Diamonds", 5.85), ("514 Diamonds", 7.00),
    ("706 Diamonds", 9.40), ("Weekly Diamond Pass", 1.45, "pass"), ("Twilight Pass", 7.90, "pass"),
)
MLBB_GRAD = "linear-gradient(135deg,#1b2a6b,#e8a12b 70%,#3b6fd8)"
MLBB_LOGO = ("MOBILE", "LEGENDS")


def _mlbb(id, name):
    return Game(id, name, MLBB_LOGO, MLBB_GRAD, "#3b82f6", "Diamonds", MLBB_PRODUCTS, server="text")


GAMES = (
    _mlbb("mlbb", "Mobile Legends"),
    Game("freefire", "Free Fire", ("FREE FIRE",), "linear-gradient(135deg,#2b1748,#5c3ea8 60%,#1a1a2e)", "#f59e0b", "Diamonds",
         _products(("100 Diamonds", 0.95), ("310 Diamonds", 2.85), ("520 Diamonds", 4.75), ("1060 Diamonds", 9.50),
                   ("2180 Diamonds", 19.00), ("Weekly Membership", 1.60, "pass"), ("Monthly Membership", 8.00, "pass")),
         flag=True),
    Game("bloodstrike", "Blood Strike", ("BLOOD STRIKE",), "linear-gradient(135deg,#1a1a2e,#c2185b 60%,#4a1d96)", "#ef4444", "Gold",
         _products(("100 Gold", 0.99, "coin"), ("310 Gold", 2.99, "coin"), ("520 Gold", 4.99, "coin"),
                   ("1050 Gold", 9.99, "coin"), ("2180 Gold", 19.99, "coin"), ("Weekly Pass", 1.99, "pass"))),
    Game("pubg", "PUBG Mobile", ("PUBG", "MOBILE"), "linear-gradient(180deg,#5a4a3a,#1c1610)", "#f59e0b", "UC",
         _products(("60 UC", 0.99, "coin"), ("325 UC", 4.99, "coin"), ("660 UC", 9.99, "coin"),
                   ("1800 UC", 24.99, "coin"), ("3850 UC", 49.99, "coin"), ("8100 UC", 99.99, "coin"))),
    _mlbb("mlbb-ph", "MLBB PH"),
    _mlbb("mlbb-my", "MLBB MY"),
    _mlbb("mlbb-id", "MLBB ID"),
    Game("genshin", "Genshin Impact", ("GENSHIN", "IMPACT"), "linear-gradient(135deg,#7fc4e8,#2b5f8c 70%,#1a2c48)", "#8b5cf6",
         "Genesis Crystals",
         _products(("60 Genesis Crystals", 0.99, "crystal"), ("300+30 Genesis Crystals", 4.99, "crystal"),
                   ("980+110 Genesis Crystals", 14.99, "crystal"), ("1980+260 Genesis Crystals", 29.99, "crystal"),
                   ("3280+600 Genesis Crystals", 49.99, "crystal"), ("6480+1600 Genesis Crystals", 99.99, "crystal"),
                   ("Blessing of the Welkin Moon", 4.99, "pass")),
         server="select", servers=("Asia", "America", "Europe", "TW, HK, MO")),
    Game("hok", "Honor Of Kings", ("HONOR", "OF KINGS"), "linear-gradient(135deg,#d94a4a,#3b6fb0 70%,#1c2a45)", "#f59e0b", "Tokens",
         _products(("16 Tokens", 0.25, "coin"), ("80 Tokens", 1.20, "coin"), ("240 Tokens", 3.60, "coin"),
                   ("400 Tokens", 6.00, "coin"), ("800 Tokens", 12.00, "coin"), ("1200 Tokens", 18.00, "coin"))),
    Game("magicchess", "Magic Chess", ("MAGIC CHESS", "GO GO"), "linear-gradient(135deg,#f0c9a0,#7a8db8 60%,#232a44)", "#3b82f6",
         "Diamonds",
         _products(("86 Diamonds", 1.20), ("172 Diamonds", 2.40), ("257 Diamonds", 3.55), ("344 Diamonds", 4.70),
                   ("706 Diamonds", 9.40), ("Weekly Pass", 1.45, "pass")),
         server="text"),
)

_BY_ID = {game.id: game for game in GAMES}


def all_games():
    return GAMES


def get_game(game_id):
    return _BY_ID.get(game_id)


def search_games(query):
    q = (query or "").strip().lower()
    return [g for g in GAMES if q in g.name.lower()]
