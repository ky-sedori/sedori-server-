MERCARI_FEE_RATE = 0.10
YAHUOKU_FEE_RATE = 0.088
AMAZON_REFERRAL_RATE = 0.10
FBA_SMALL_FEE = 350
FBA_MEDIUM_FEE = 600
SHIPPING_TO_FBA = 400
MIN_PROFIT_YEN = 300
MIN_PROFIT_RATE = 0.10
REQUEST_DELAY_MIN = 0.3
REQUEST_DELAY_MAX = 0.8
MAX_ITEMS_PER_SITE = 8
AMAZON_SEARCH_MAX = 5

RANK_VELOCITY = [
    (1_000,   "🔥 超売れ筋",  "200件以上/月"),
    (5_000,   "⚡ 売れ筋",    "50〜200件/月"),
    (20_000,  "📈 普通",      "10〜50件/月"),
    (100_000, "📉 やや遅い",  "1〜10件/月"),
    (float("inf"), "🐌 遅い", "1件未満/月"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
