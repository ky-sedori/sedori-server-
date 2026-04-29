import requests, re, time, random, urllib.parse
from bs4 import BeautifulSoup
from dataclasses import dataclass
from config import HEADERS, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, MAX_ITEMS_PER_SITE

@dataclass
class YahuokuItem:
    title: str; price: int; url: str; image_url: str; bids: int; time_left: str; is_buynow: bool; source: str = "ヤフオク"

def _sleep(): time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

def _parse_price(text):
    nums = re.sub(r"[^\d]", "", text)
    try: return int(nums)
    except: return 0

def search(keyword, price_min=0, price_max=0):
    items = []
    for page in range(1, 4):
        batch = _fetch_page(keyword, price_min, price_max, page)
        if not batch: break
        items.extend(batch)
        if len(items) >= MAX_ITEMS_PER_SITE: break
    return items[:MAX_ITEMS_PER_SITE]

def _fetch_page(keyword, price_min, price_max, page):
    params = {"p": keyword, "va": keyword, "b": str(1+(page-1)*20), "n": "20",
              "s1": "new", "o1": "d", "mode": "0", "fixed": "1"}
    if price_min > 0: params["min"] = str(price_min); params["price_type"] = "currentprice"
    if price_max > 0: params["max"] = str(price_max); params["price_type"] = "currentprice"
    url = "https://auctions.yahoo.co.jp/search/search?" + urllib.parse.urlencode(params)
    try:
        _sleep()
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return _parse_page(resp.text)
    except Exception as e:
        print(f"[ヤフオク] {e}")
        return []

def _parse_page(html):
    items = []
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("li.Product") or soup.select(".Product") or soup.select('[class*="Product"]')
    for card in cards:
        try:
            title_el = card.select_one(".Product__title a") or card.select_one("h3 a") or card.select_one("a[data-auction-title]")
            if not title_el: continue
            title = title_el.get_text(strip=True)
            url = title_el.get("href", "")
            price_el = card.select_one(".Product__price") or card.select_one("[class*='price']")
            if not price_el: continue
            price = _parse_price(price_el.get_text(strip=True))
            if price <= 0: continue
            img_el = card.select_one("img")
            image_url = img_el.get("src", "") if img_el else ""
            if image_url.startswith("//"): image_url = "https:" + image_url
            items.append(YahuokuItem(title=title, price=price, url=url, image_url=image_url,
                                     bids=0, time_left="", is_buynow=True))
        except Exception: continue
    return items
