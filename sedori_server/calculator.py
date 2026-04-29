from dataclasses import dataclass
from typing import Optional
from config import (
    AMAZON_REFERRAL_RATE, FBA_SMALL_FEE, FBA_MEDIUM_FEE,
    SHIPPING_TO_FBA, MIN_PROFIT_YEN, MIN_PROFIT_RATE, RANK_VELOCITY,
)

@dataclass
class ProfitResult:
    buy_price: int
    buy_source: str
    flea_url: str
    flea_title: str
    amazon_price: int
    amazon_title: str
    amazon_url: str
    sales_rank: int
    rank_category: str
    rating: float
    review_count: int
    amazon_referral: int
    fba_fee: int
    fba_shipping: int
    buy_site_fee: int
    profit: int
    profit_rate: float
    velocity_label: str
    monthly_estimate: str
    is_profitable: bool


def get_velocity(sales_rank: int) -> tuple[str, str]:
    if sales_rank <= 0:
        return "❓ 不明", "取得不可"
    for rank_limit, label, monthly in RANK_VELOCITY:
        if sales_rank <= rank_limit:
            return label, monthly
    return "🐌 遅い", "1件未満/月"


def calculate(
    buy_price: int, buy_source: str, flea_url: str, flea_title: str,
    amazon_price: int, amazon_title: str, amazon_url: str,
    sales_rank: int, rank_category: str, rating: float, review_count: int,
    use_fba: bool = True, item_size: str = "small",
) -> Optional[ProfitResult]:
    if amazon_price <= 0 or buy_price <= 0:
        return None
    referral = int(amazon_price * AMAZON_REFERRAL_RATE)
    fba_fee = FBA_SMALL_FEE if item_size == "small" else FBA_MEDIUM_FEE
    fba_shipping = SHIPPING_TO_FBA if use_fba else 0
    profit = amazon_price - referral - fba_fee - buy_price - fba_shipping
    profit_rate = profit / amazon_price if amazon_price > 0 else 0.0
    velocity_label, monthly_estimate = get_velocity(sales_rank)
    is_profitable = profit >= MIN_PROFIT_YEN and profit_rate >= MIN_PROFIT_RATE
    return ProfitResult(
        buy_price=buy_price, buy_source=buy_source, flea_url=flea_url, flea_title=flea_title,
        amazon_price=amazon_price, amazon_title=amazon_title, amazon_url=amazon_url,
        sales_rank=sales_rank, rank_category=rank_category, rating=rating, review_count=review_count,
        amazon_referral=referral, fba_fee=fba_fee, fba_shipping=fba_shipping, buy_site_fee=0,
        profit=profit, profit_rate=profit_rate,
        velocity_label=velocity_label, monthly_estimate=monthly_estimate,
        is_profitable=is_profitable,
    )
