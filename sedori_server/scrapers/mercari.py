import requests, json, time, random, urllib.parse
from dataclasses import dataclass
from typing import Optional
from config import HEADERS, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, MAX_ITEMS_PER_SITE

@dataclass
class MercariItem:
    title: str; price: int; url: str; image_url: str; condition: str; item_id: str; source: str = "メルカリ"

def _sleep(): time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))

def search(keyword: str, price_min: int = 0, price_max: int = 0) -> list[MercariItem]:
    items = _fetch_via_api(keyword, price_min, price_max)
    if not items:
        items = _fetch_via_web(keyword, price_min, price_max)
    return items[:MAX_ITEMS_PER_SITE]

def _fetch_via_api(keyword, price_min, price_max):
    items = []
    endpoint = "https://api.mercari.jp/v2/entities:search"
    headers = {"User-Agent": "mercari-jp/android 6.0.0", "Accept": "application/json", "X-Platform": "android"}
    payload = {"pageSize": MAX_ITEMS_PER_SITE, "searchCondition": {
        "keyword": keyword, "status": ["STATUS_ON_SALE"],
        "priceMin": price_min if price_min > 0 else 0,
        "priceMax": price_max if price_max > 0 else 0,
    }}
    try:
        _sleep()
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            for r in resp.json().get("items", []):
                item = _parse(r)
                if item: items.append(item)
    except Exception: pass
    return items

def _fetch_via_web(keyword, price_min, price_max):
    items = []
    params = {"keyword": keyword, "status": "on_sale", "sort": "price", "order": "asc"}
    if price_min > 0: params["price_min"] = price_min
    if price_max > 0: params["price_max"] = price_max
    url = "https://jp.mercari.com/search?" + urllib.parse.urlencode(params)
    try:
        _sleep()
        resp = requests.get(url, headers=HEADERS, timeout=15)
        html = resp.text
        start = html.find("__NEXT_DATA__")
        if start != -1:
            js_start = html.find("{", start)
            depth, end = 0, js_start
            for i, ch in enumerate(html[js_start:], js_start):
                if ch == "{": depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0: end = i; break
            try:
                data = json.loads(html[js_start:end+1])
                items = _extract(data)
            except Exception: pass
    except Exception: pass
    return items

def _extract(data):
    items = []
    def find(obj, depth=0):
        if depth > 6: return []
        found = []
        if isinstance(obj, list):
            for i in obj:
                if isinstance(i, dict) and "price" in i and "name" in i: found.append(i)
                else: found.extend(find(i, depth+1))
        elif isinstance(obj, dict):
            if "price" in obj and "name" in obj: found.append(obj)
            else:
                for v in obj.values(): found.extend(find(v, depth+1))
        return found
    for r in find(data):
        item = _parse(r)
        if item: items.append(item)
    return items

def _parse(r):
    try:
        price = int(str(r.get("price", 0)).replace(",", "").replace("¥", ""))
        item_id = str(r.get("id", ""))
        title = r.get("name", r.get("title", ""))
        url = f"https://jp.mercari.com/item/{item_id}" if item_id else ""
        if price > 0 and title:
            return MercariItem(title=title, price=price, url=url, image_url="", condition="", item_id=item_id)
    except Exception: pass
    return None
