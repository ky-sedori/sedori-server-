import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from scrapers import mercari, yahuoku, amazon
from calculator import calculate, get_velocity

app = FastAPI(title="せどりツール API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ProductResult(BaseModel):
    source: str
    flea_title: str
    flea_url: str
    buy_price: int
    amazon_title: str
    amazon_url: str
    amazon_price: int
    profit: int
    profit_rate: float
    sales_rank: int
    rank_category: str
    velocity_label: str
    monthly_estimate: str
    rating: float
    review_count: int
    is_profitable: bool


class AmazonInfo(BaseModel):
    asin: str
    title: str
    price: int
    sales_rank: int
    rank_category: str
    velocity_label: str
    monthly_estimate: str
    rating: float
    review_count: int
    url: str
    image_url: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/amazon", response_model=Optional[AmazonInfo])
def get_amazon(keyword: str = Query(...)):
    try:
        product = amazon.search_best_match(keyword)
        if not product:
            return None
        v_label, monthly = get_velocity(product.sales_rank)
        return AmazonInfo(
            asin=product.asin, title=product.title, price=product.price,
            sales_rank=product.sales_rank, rank_category=product.rank_category,
            velocity_label=v_label, monthly_estimate=monthly,
            rating=product.rating, review_count=product.review_count,
            url=product.url, image_url=product.image_url,
        )
    except Exception as e:
        print(f"エラー: {e}")
        return None


@app.get("/search", response_model=list[ProductResult])
def search(
    keyword: str = Query(...),
    price_min: int = Query(0),
    price_max: int = Query(0),
    sites: str = Query("mercari,yahuoku"),
    item_size: str = Query("small"),
):
    site_list = [s.strip() for s in sites.split(",")]
    flea_items = []

    if "mercari" in site_list:
        try:
            for it in mercari.search(keyword, price_min, price_max):
                flea_items.append((it.price, it.title, it.url, "メルカリ"))
        except Exception as e:
            print(f"メルカリエラー: {e}")

    if "yahuoku" in site_list:
        try:
            for it in yahuoku.search(keyword, price_min, price_max):
                flea_items.append((it.price, it.title, it.url, "ヤフオク"))
        except Exception as e:
            print(f"ヤフオクエラー: {e}")

    results = []
    seen: set[str] = set()

    for buy_price, flea_title, flea_url, source in flea_items:
        key = flea_title[:20]
        if key in seen:
            continue
        seen.add(key)
        try:
            amz = amazon.search_best_match(flea_title)
        except Exception:
            continue
        if not amz:
            continue
        r = calculate(
            buy_price=buy_price, buy_source=source,
            flea_url=flea_url, flea_title=flea_title,
            amazon_price=amz.price, amazon_title=amz.title, amazon_url=amz.url,
            sales_rank=amz.sales_rank, rank_category=amz.rank_category,
            rating=amz.rating, review_count=amz.review_count, item_size=item_size,
        )
        if r:
            results.append(ProductResult(
                source=source, flea_title=flea_title, flea_url=flea_url,
                buy_price=buy_price, amazon_title=amz.title, amazon_url=amz.url,
                amazon_price=amz.price, profit=r.profit, profit_rate=r.profit_rate,
                sales_rank=amz.sales_rank, rank_category=amz.rank_category,
                velocity_label=r.velocity_label, monthly_estimate=r.monthly_estimate,
                rating=amz.rating, review_count=amz.review_count,
                is_profitable=r.is_profitable,
            ))

    return sorted(results, key=lambda x: x.profit, reverse=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
