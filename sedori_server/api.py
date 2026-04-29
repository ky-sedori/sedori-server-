import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import uvicorn

from scrapers import mercari, yahuoku, amazon
from calculator import calculate, get_velocity

app = FastAPI(title="せどりツール API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MOBILE_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="せどりツール">
<title>せどりツール</title>
<script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js" async></script>
<style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{font-family:-apple-system,sans-serif;background:#0f1117;color:#e0e0e0;min-height:100vh}
.header{background:linear-gradient(135deg,#1a1f2e,#16213e);padding:16px;text-align:center;position:sticky;top:0;z-index:100;border-bottom:1px solid #2a3050}
.header h1{font-size:20px;color:#60a5fa;font-weight:800}
.header p{font-size:11px;color:#666;margin-top:2px}
.page{display:none;padding:16px;max-width:600px;margin:0 auto}
.page.active{display:block}
.card{background:#13182a;border-radius:16px;padding:16px;margin-bottom:12px;border:1px solid #1e2640}
label{font-size:12px;color:#888;display:block;margin-bottom:6px}
input[type=text],input[type=number]{width:100%;background:#1a2035;color:#e0e0e0;border:1px solid #2a3558;border-radius:10px;padding:12px;font-size:16px;margin-bottom:10px;outline:none}
input:focus{border-color:#3b82f6}
.row{display:flex;gap:8px;align-items:center}
.row input{flex:1}
.sep{color:#555;font-size:14px;flex-shrink:0;margin-bottom:10px}
.btn{width:100%;padding:14px;border-radius:12px;font-size:16px;font-weight:700;border:none;cursor:pointer;transition:opacity .2s}
.btn:active{opacity:.7}
.btn-primary{background:#2563eb;color:#fff;margin-bottom:10px}
.btn-scan{background:#1e1b4b;color:#a5b4fc;border:1px solid #4338ca}
.btn-small{padding:8px 14px;font-size:13px;border-radius:8px;border:none;cursor:pointer;font-weight:600}
.btn-flea{background:#4c1d95;color:#fff}
.btn-amz{background:#78350f;color:#fff}
.loading{text-align:center;padding:40px 20px}
.spinner{width:40px;height:40px;border:3px solid #1e2640;border-top-color:#60a5fa;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto 16px}
@keyframes spin{to{transform:rotate(360deg)}}
.loading p{color:#666;font-size:14px;line-height:1.8}
.stats{display:flex;gap:8px;margin-bottom:12px}
.stat{flex:1;background:#13182a;border-radius:12px;padding:10px;text-align:center;border:1px solid #1e2640}
.stat .val{font-size:22px;font-weight:800;color:#60a5fa}
.stat.green .val{color:#34d399}
.stat.yellow .val{color:#fbbf24}
.stat .lbl{font-size:10px;color:#666;margin-top:2px}
.result-card{background:#13182a;border-radius:14px;padding:14px;margin-bottom:10px;border:1px solid #1e2640}
.result-card.good{border-color:#065f46;background:#0a1f1a}
.badge{display:inline-block;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:700;margin-bottom:8px}
.badge-m{background:#7f1d1d;color:#fca5a5}
.badge-y{background:#1e3a5f;color:#93c5fd}
.result-title{font-size:13px;color:#c0cde0;line-height:1.5;margin-bottom:10px}
.prices{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
.price-box{text-align:center}
.price-box .plbl{font-size:10px;color:#666;margin-bottom:2px}
.price-box .pval{font-size:13px;font-weight:600;color:#ccc}
.price-box .pval.amz{color:#fbbf24}
.price-box .pval.profit{font-size:16px;font-weight:800}
.price-box .pval.profit.good{color:#34d399}
.price-box .pval.profit.ok{color:#60a5fa}
.arrow{color:#444;font-size:18px}
.meta{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
.meta span{font-size:11px;color:#888}
.meta .vel{color:#a78bfa}
.btns{display:flex;gap:8px}
.btns a{flex:1;text-align:center;padding:9px;border-radius:8px;font-size:12px;font-weight:700;text-decoration:none;display:block}
.empty{text-align:center;padding:40px 20px;color:#555}
.cam-area{position:relative;width:100%;border-radius:16px;overflow:hidden;background:#000;margin-bottom:16px}
video{width:100%;display:block}
.cam-frame{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:70%;height:45%}
.cam-frame::before,.cam-frame::after{content:'';position:absolute;width:24px;height:24px;border:3px solid #60a5fa}
.cam-frame::before{top:0;left:0;border-right:none;border-bottom:none}
.cam-frame::after{bottom:0;right:0;border-left:none;border-top:none;right:0}
.cam-corner-br{position:absolute;bottom:0;left:0;width:24px;height:24px;border:3px solid #60a5fa;border-right:none;border-top:none}
.cam-corner-tr{position:absolute;top:0;right:0;width:24px;height:24px;border:3px solid #60a5fa;border-left:none;border-bottom:none}
.cam-guide{text-align:center;color:#aaa;font-size:13px;margin-bottom:12px}
.filter-bar{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.filter-bar input{flex:1;margin:0;margin-right:10px;padding:9px 12px;font-size:14px}
.toggle{display:flex;align-items:center;gap:6px;white-space:nowrap}
.toggle label{font-size:12px;color:#888;margin:0}
input[type=checkbox]{width:16px;height:16px;accent-color:#3b82f6}
.sim-box{background:#1a2035;border-radius:12px;padding:12px;margin-top:12px}
.sim-box h3{font-size:13px;color:#93c5fd;margin-bottom:8px}
.sim-row{display:flex;justify-content:space-between;padding:4px 0;font-size:13px}
.sim-row .k{color:#777}.sim-row .v{color:#aaa}
.sim-profit{font-size:20px;font-weight:800;text-align:center;margin-top:8px;padding-top:8px;border-top:1px solid #2a3558}
.back-btn{background:none;border:none;color:#60a5fa;font-size:14px;cursor:pointer;margin-bottom:12px;padding:4px 0}
</style>
</head>
<body>

<div class="header">
  <h1>🔍 せどりツール</h1>
  <p>フリマ × Amazon 利益計算</p>
</div>

<!-- ホーム画面 -->
<div class="page active" id="page-home">
  <div style="height:16px"></div>

  <button class="btn btn-scan" onclick="showPage('page-scan')">
    📷 バーコードをスキャン
  </button>

  <div style="height:10px"></div>

  <div class="card">
    <label>キーワード検索</label>
    <input type="text" id="keyword" placeholder="例：Nintendo Switch、ポケモン" />

    <label>仕入れ価格帯（円）</label>
    <div class="row">
      <input type="number" id="priceMin" placeholder="最低" />
      <span class="sep">〜</span>
      <input type="number" id="priceMax" placeholder="最高" />
    </div>

    <button class="btn btn-primary" onclick="doSearch()">🔍 利益商材を検索</button>
  </div>

  <div id="home-loading" style="display:none" class="loading">
    <div class="spinner"></div>
    <p>メルカリ・ヤフオクを検索して<br>Amazonと比較中...<br><br>1〜2分かかります</p>
  </div>
</div>

<!-- バーコードスキャン画面 -->
<div class="page" id="page-scan">
  <div style="height:16px"></div>
  <button class="back-btn" onclick="showPage('page-home'); stopCamera()">← 戻る</button>

  <div id="reader" style="width:100%;border-radius:16px;overflow:hidden;margin-bottom:4px;background:#000"></div>
  <p class="cam-guide">バーコードをフレーム内に合わせてください</p>

  <div class="card">
    <label>または JAN コードを手入力</label>
    <input type="number" id="janCode" placeholder="例：4902370548969" />
    <button class="btn btn-primary" onclick="searchByJan()">Amazon価格を調べる</button>
  </div>

  <div id="scan-loading" style="display:none" class="loading">
    <div class="spinner"></div>
    <p>Amazon検索中...</p>
  </div>

  <div id="scan-result"></div>
</div>

<!-- 検索結果画面 -->
<div class="page" id="page-results">
  <div style="height:16px"></div>
  <button class="back-btn" onclick="showPage('page-home')">← 戻る</button>

  <div id="stats-area" class="stats"></div>

  <div class="filter-bar">
    <input type="text" id="filterText" placeholder="絞り込み..." oninput="renderResults()" />
    <div class="toggle">
      <input type="checkbox" id="profitOnly" checked onchange="renderResults()" />
      <label for="profitOnly">利益のみ</label>
    </div>
  </div>

  <div id="results-list"></div>
</div>

<script>
let allResults = [];

function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
}

// ── キーワード検索 ──
async function doSearch() {
  const kw = document.getElementById('keyword').value.trim();
  if (!kw) { alert('キーワードを入力してください'); return; }
  const min = document.getElementById('priceMin').value || 0;
  const max = document.getElementById('priceMax').value || 0;

  document.getElementById('home-loading').style.display = 'block';
  document.querySelector('#page-home .card').style.display = 'none';
  document.querySelector('#page-home .btn-scan').style.display = 'none';

  try {
    const res = await fetch(`/search?keyword=${encodeURIComponent(kw)}&price_min=${min}&price_max=${max}`);
    allResults = await res.json();
    showPage('page-results');
    renderResults();
  } catch(e) {
    alert('エラーが発生しました。もう一度試してください。');
  } finally {
    document.getElementById('home-loading').style.display = 'none';
    document.querySelector('#page-home .card').style.display = 'block';
    document.querySelector('#page-home .btn-scan').style.display = 'block';
  }
}

// ── 結果ルンダリング ──
function renderResults() {
  const profitOnly = document.getElementById('profitOnly').checked;
  const filterText = document.getElementById('filterText').value.toLowerCase();

  const filtered = allResults.filter(r => {
    const matchProfit = !profitOnly || r.is_profitable;
    const matchText = !filterText || r.amazon_title.toLowerCase().includes(filterText) || r.flea_title.toLowerCase().includes(filterText);
    return matchProfit && matchText;
  }).sort((a,b) => b.profit - a.profit);

  const profitCount = allResults.filter(r => r.is_profitable).length;
  const maxProfit = allResults.length ? Math.max(...allResults.map(r => r.profit)) : 0;

  document.getElementById('stats-area').innerHTML = `
    <div class="stat"><div class="val">${allResults.length}</div><div class="lbl">分析</div></div>
    <div class="stat green"><div class="val">${profitCount}</div><div class="lbl">利益商材</div></div>
    <div class="stat yellow"><div class="val">¥${maxProfit.toLocaleString()}</div><div class="lbl">最高利益</div></div>
  `;

  if (filtered.length === 0) {
    document.getElementById('results-list').innerHTML = '<div class="empty">条件に合う商品がありません</div>';
    return;
  }

  document.getElementById('results-list').innerHTML = filtered.map(r => {
    const isGood = r.profit_rate >= 0.3;
    const isOk = r.profit >= 0;
    const profitClass = isGood ? 'good' : isOk ? 'ok' : 'ng';
    const cardClass = isGood ? 'good' : '';
    const badge = r.source === 'メルカリ' ? '<span class="badge badge-m">メルカリ</span>' : '<span class="badge badge-y">ヤフオク</span>';
    const rate = (r.profit_rate * 100).toFixed(0);
    return `
    <div class="result-card ${cardClass}">
      ${badge}
      <div class="result-title">${r.amazon_title || r.flea_title}</div>
      <div class="prices">
        <div class="price-box"><div class="plbl">仕入値</div><div class="pval">¥${r.buy_price.toLocaleString()}</div></div>
        <div class="arrow">→</div>
        <div class="price-box"><div class="plbl">Amazon</div><div class="pval amz">¥${r.amazon_price.toLocaleString()}</div></div>
        <div class="arrow">=</div>
        <div class="price-box"><div class="plbl">利益 ${rate}%</div><div class="pval profit ${profitClass}">¥${r.profit.toLocaleString()}</div></div>
      </div>
      <div class="meta">
        <span class="vel">${r.velocity_label}</span>
        <span>${r.monthly_estimate}</span>
        ${r.sales_rank > 0 ? `<span>ランク ${r.sales_rank.toLocaleString()}</span>` : ''}
        ${r.rating > 0 ? `<span>★${r.rating}(${r.review_count}件)</span>` : ''}
      </div>
      <div class="btns">
        <a href="${r.flea_url}" target="_blank" style="background:#4c1d95;color:#fff">${r.source}で見る</a>
        <a href="${r.amazon_url}" target="_blank" style="background:#78350f;color:#fff">Amazonで見る</a>
      </div>
    </div>`;
  }).join('');
}

// ── バーコードスキャン ──
let html5QrCode = null;

async function startCamera() {
  try {
    html5QrCode = new Html5Qrcode("reader");
    await html5QrCode.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: { width: 260, height: 160 } },
      (code) => {
        document.getElementById('janCode').value = code;
        stopCamera();
        searchByJan();
      },
      () => {}
    );
  } catch(e) {
    console.log('カメリ起動失敗:', e);
    alert('カメラの起動に失敗しました。JANコードを手入力してください。');
  }
}

function stopCamera() {
  if (html5QrCode) {
    html5QrCode.stop().catch(() => {});
    html5QrCode = null;
  }
}

const scanBtn = document.querySelector('[onclick="showPage(\'page-scan\')"]');
if (scanBtn) scanBtn.addEventListener('click', () => { setTimeout(startCamera, 300); });

// ── JAN検索 ──
async function searchByJan() {
  const jan = document.getElementById('janCode').value.trim();
  if (!jan) { alert('JANコードを入力してください'); return; }

  document.getElementById('scan-loading').style.display = 'block';
  document.getElementById('scan-result').innerHTML = '';

  try {
    const res = await fetch(`/amazon?keyword=${encodeURIComponent(jan)}`);
    const product = await res.json();

    if (!product) {
      document.getElementById('scan-result').innerHTML = '<div class="empty">Amazon該当商品なし</div>';
      return;
    }

    document.getElementById('scan-result').innerHTML = `
    <div class="card">
      <div class="result-title" style="font-size:15px;font-weight:700;color:#93c5fd;margin-bottom:12px">${product.title}</div>
      <div style="font-size:28px;font-weight:800;color:#fbbf24;text-align:center;margin-bottom:16px">¥${product.price.toLocaleString()}</div>
      <div class="meta" style="justify-content:center">
        <span class="vel">${product.velocity_label}</span>
        <span>${product.monthly_estimate}</span>
        ${product.sales_rank > 0 ? `<span>ランク ${product.sales_rank.toLocaleString()}</span>` : ''}
        ${product.rating > 0 ? `<span>★${product.rating}(${product.review_count}件)</span>` : ''}
      </div>
      <div class="sim-box">
        <h3>📱 利益シミュレーター</h3>
        <input type="number" id="simPrice" placeholder="仕入れ価格を入力（円）" oninput="calcSim(${product.price})" />
        <div id="sim-result"></div>
      </div>
      <div class="btns" style="margin-top:12px">
        <a href="${product.url}" target="_blank" style="background:#78350f;color:#fff">Amazonで見る</a>
      </div>
    </div>`;
  } catch(e) {
    alert('エラーが発生しました');
  } finally {
    document.getElementById('scan-loading').style.display = 'none';
  }
}

function calcSim(amazonPrice) {
  const buyPrice = parseInt(document.getElementById('simPrice').value) || 0;
  const referral = Math.floor(amazonPrice * 0.1);
  const fba = 350;
  const ship = 400;
  const profit = amazonPrice - referral - fba - ship - buyPrice;
  const rate = (profit / amazonPrice * 100).toFixed(1);
  const color = profit >= 300 ? '#34d399' : profit >= 0 ? '#60a5fa' : '#f87171';
  document.getElementById('sim-result').innerHTML = `
    <div class="sim-row"><span class="k">Amazon紹介料</span><span class="v">¥${referral.toLocaleString()}</span></div>
    <div class="sim-row"><span class="k">FBA手数料</span><span class="v">¥${fba}</span></div>
    <div class="sim-row"><span class="k">FBA送料</span><span class="v">¥${ship}</span></div>
    <div class="sim-profit" style="color:${color}">利益 ¥${profit.toLocaleString()}（${rate}%）</div>`;
}
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def mobile_ui():
    return MOBILE_HTML


class ProductResult(BaseModel):
    source: str; flea_title: str; flea_url: str; buy_price: int
    amazon_title: str; amazon_url: str; amazon_price: int
    profit: int; profit_rate: float; sales_rank: int; rank_category: str
    velocity_label: str; monthly_estimate: str; rating: float; review_count: int; is_profitable: bool

class AmazonInfo(BaseModel):
    asin: str; title: str; price: int; sales_rank: int; rank_category: str
    velocity_label: str; monthly_estimate: str; rating: float; review_count: int; url: str; image_url: str


@app.get("/health")
def health(): return {"status": "ok"}


@app.get("/amazon", response_model=Optional[AmazonInfo])
def get_amazon(keyword: str = Query(...)):
    try:
        p = amazon.search_best_match(keyword)
        if not p: return None
        v, m = get_velocity(p.sales_rank)
        return AmazonInfo(asin=p.asin, title=p.title, price=p.price, sales_rank=p.sales_rank,
                          rank_category=p.rank_category, velocity_label=v, monthly_estimate=m,
                          rating=p.rating, review_count=p.review_count, url=p.url, image_url=p.image_url)
    except Exception as e:
        print(f"エラー: {e}"); return None


@app.get("/search", response_model=list[ProductResult])
def search(keyword: str = Query(...), price_min: int = Query(0), price_max: int = Query(0),
           sites: str = Query("mercari,yahuoku"), item_size: str = Query("small")):
    site_list = [s.strip() for s in sites.split(",")]
    flea_items = []
    if "mercari" in site_list:
        try:
            for it in mercari.search(keyword, price_min, price_max):
                flea_items.append((it.price, it.title, it.url, "メルカリ"))
        except Exception as e: print(f"メルカリ: {e}")
    if "yahuoku" in site_list:
        try:
            for it in yahuoku.search(keyword, price_min, price_max):
                flea_items.append((it.price, it.title, it.url, "ヤフオク"))
        except Exception as e: print(f"ヤフオク: {e}")

    seen = set(); unique_items = []
    for item in flea_items:
        key = item[1][:20]
        if key not in seen:
            seen.add(key); unique_items.append(item)

    def lookup(item):
        buy_price, flea_title, flea_url, source = item
        try:
            amz = amazon.search_best_match(flea_title)
            if not amz: return None
            r = calculate(buy_price=buy_price, buy_source=source, flea_url=flea_url, flea_title=flea_title,
                          amazon_price=amz.price, amazon_title=amz.title, amazon_url=amz.url,
                          sales_rank=amz.sales_rank, rank_category=amz.rank_category,
                          rating=amz.rating, review_count=amz.review_count, item_size=item_size)
            if not r: return None
            return ProductResult(source=source, flea_title=flea_title, flea_url=flea_url,
                buy_price=buy_price, amazon_title=amz.title, amazon_url=amz.url, amazon_price=amz.price,
                profit=r.profit, profit_rate=r.profit_rate, sales_rank=amz.sales_rank,
                rank_category=amz.rank_category, velocity_label=r.velocity_label,
                monthly_estimate=r.monthly_estimate, rating=amz.rating, review_count=amz.review_count,
                is_profitable=r.is_profitable)
        except: return None

    results = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(lookup, item): item for item in unique_items}
        for f in as_completed(futures):
            r = f.result()
            if r: results.append(r)
    return sorted(results, key=lambda x: x.profit, reverse=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
