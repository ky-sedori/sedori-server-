import requests, re, time, random, urllib.parse
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
from config import HEADERS, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, AMAZON_SEARCH_MAX

@dataclass
class AmazonProduct:
    asin: str; title: str; price: int; sales_rank: int; rank_category: str
    rating: float; review_count: int; url: str; image_url: str = ""

_session = requests.Session()
_session.headers.update(HEADERS)

def _sleep(): time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

def search_best_match(keyword: str) -> Optional[AmazonProduct]:
    for asin in _search_asins(keyword)[:AMAZON_SEARCH_MAX]:
        p = get_product(asin)
        if p and p.price > 0: return p
        _sleep()
    return None

def _search_asins(keyword):
    url = f"https://www.amazon.co.jp/s?k={urllib.parse.quote(keyword)}&language=ja_JP"
    asins = []
    try:
        _sleep()
        resp = _session.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for r in soup.select('[data-component-type="s-search-result"]'):
            asin = r.get("data-asin", "")
            if asin and len(asin) == 10: asins.append(asin)
        if not asins:
            for a in soup.find_all("a", href=True):
                m = re.search(r"/dp/([A-Z0-9]{10})", a["href"])
                if m: asins.append(m.group(1))
            asins = list(dict.fromkeys(asins))
    except Exception as e: print(f"[Amazon検索] {e}")
    return asins[:AMAZON_SEARCH_MAX]

def get_product(asin: str) -> Optional[AmazonProduct]:
    url = f"https://www.amazon.co.jp/dp/{asin}?language=ja_JP"
    try:
        _sleep()
        resp = _session.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = _title(soup); price = _price(soup)
        rank, cat = _rank(soup); rating, count = _reviews(soup)
        if price == 0 and not title: return None
        return AmazonProduct(asin=asin, title=title, price=price, sales_rank=rank,
                             rank_category=cat, rating=rating, review_count=count, url=url)
    except Exception as e: print(f"[Amazon商品] {e}"); return None

def _title(soup):
    el = soup.select_one("#productTitle") or soup.select_one("#title")
    return el.get_text(strip=True) if el else ""

def _price(soup):
    for sel in ["#price_inside_buybox","#priceblock_ourprice","#priceblock_dealprice",
                ".a-price .a-offscreen","#price",".priceToPay .a-offscreen","#corePrice_feature_div .a-offscreen"]:
        el = soup.select_one(sel)
        if el:
            nums = re.sub(r"[^\d]", "", el.get_text(strip=True))
            if nums: return int(nums)
    return 0

def _rank(soup):
    for row in soup.select("#detailBulletsWrapper_feature_div li, #productDetails_db_sections tr"):
        text = row.get_text()
        if "ランキング" in text or "売れ筋" in text:
            m = re.search(r"([\d,]+)\s*位", text)
            if m:
                cat_m = re.search(r"の\s*(.+?)\s*(?:部門|カテゴリ|（|\(|$)", text)
                return int(m.group(1).replace(",", "")), (cat_m.group(1).strip() if cat_m else "")
    rank_el = soup.select_one("#SalesRank")
    if rank_el:
        m = re.search(r"([\d,]+)\s*位", rank_el.get_text())
        if m: return int(m.group(1).replace(",", "")), ""
    return 0, ""

def _reviews(soup):
    rating, count = 0.0, 0
    el = soup.select_one("#acrPopover")
    if el:
        m = re.search(r"([\d.]+)", el.get("title", el.get_text()))
        if m:
            try: rating = float(m.group(1))
            except: pass
    el2 = soup.select_one("#acrCustomerReviewText")
    if el2:
        nums = re.sub(r"[^\d]", "", el2.get_text())
        if nums: count = int(nums)
    return rating, count
