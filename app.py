from __future__ import annotations

import json
import os
import random
from html import escape
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from flask import Flask, Response, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PRODUCTS_PATH = DATA_DIR / "products.json"

app = Flask(__name__)


CATALOG_SEEDS = [
    {
        "category": "패션",
        "keyword": "minimal canvas tote bag",
        "name": "캔버스 토트백",
        "tone": "가볍게 들고 나가는 무드",
    },
    {
        "category": "패션",
        "keyword": "retro running sneakers",
        "name": "러닝 스니커즈",
        "tone": "걷고 싶어지는 산뜻함",
    },
    {
        "category": "디지털",
        "keyword": "wireless headphones product photo",
        "name": "무선 헤드폰",
        "tone": "집중을 켜는 조용한 장치",
    },
    {
        "category": "디지털",
        "keyword": "wireless charging pad product photo",
        "name": "무선 충전 패드",
        "tone": "책상 위 전원을 정리하는 장치",
    },
    {
        "category": "리빙",
        "keyword": "black aluminium cup product photo",
        "name": "블랙 알루미늄 컵",
        "tone": "오후를 천천히 잡아주는 컵",
    },
    {
        "category": "리빙",
        "keyword": "linen bedding set product photo",
        "name": "린넨 침구",
        "tone": "하루를 정리하는 부드러움",
    },
    {
        "category": "뷰티",
        "keyword": "face lotion product photo",
        "name": "페이스 로션",
        "tone": "가볍게 시작하는 스킨케어 루틴",
    },
    {
        "category": "뷰티",
        "keyword": "solid perfume compact product photo",
        "name": "솔리드 퍼퓸",
        "tone": "작게 남기는 선명한 향",
    },
    {
        "category": "리빙",
        "keyword": "family tree photo frame product photo",
        "name": "포토 프레임",
        "tone": "책상 위 기억을 세우는 프레임",
    },
    {
        "category": "문구",
        "keyword": "desk lamp product photo",
        "name": "데스크 램프",
        "tone": "밤 작업의 작은 스위치",
    },
    {
        "category": "푸드",
        "keyword": "specialty coffee package",
        "name": "커피 패키지",
        "tone": "집에서 여는 작은 카페",
    },
    {
        "category": "푸드",
        "keyword": "lunch box product photo",
        "name": "런치 박스",
        "tone": "가볍게 채우는 간식 시간",
    },
    {
        "category": "취미",
        "keyword": "studio camera product photo",
        "name": "스튜디오 카메라",
        "tone": "장면을 또렷하게 남기는 취미",
    },
    {
        "category": "취미",
        "keyword": "tennis racket product photo",
        "name": "테니스 라켓",
        "tone": "몸을 가볍게 깨우는 취미",
    },
]

ADJECTIVES = [
    "제로",
    "루프",
    "클리어",
    "모먼트",
    "스탠다드",
    "라이트",
    "비비드",
    "스튜디오",
    "픽셀",
    "오프라인",
]

BENEFITS = [
    "실제 구매 없이 장바구니 만족감만 남겨요.",
    "결제 전 단계에서 멈추도록 설계된 가상 상품이에요.",
    "오늘의 기분을 기록하듯 담아둘 수 있어요.",
    "새로고침할 때마다 다른 이미지로 다시 만나요.",
    "가격은 체험용이며 실제 청구가 발생하지 않아요.",
    "충동구매 대신 탐색의 재미를 남기는 아이템이에요.",
]

PALETTE = {
    "패션": ("#1167d8", "#f8485e"),
    "디지털": ("#111827", "#35c2ff"),
    "리빙": ("#0f766e", "#f5b942"),
    "뷰티": ("#c026d3", "#fb7185"),
    "문구": ("#7c3aed", "#22c55e"),
    "푸드": ("#ea580c", "#16a34a"),
    "취미": ("#2563eb", "#f97316"),
}


OPEN_PRODUCT_IMAGE_IDS = {
    "minimal canvas tote bag": 176,
    "retro running sneakers": 92,
    "wireless headphones product photo": 101,
    "wireless charging pad product photo": 102,
    "black aluminium cup product photo": 49,
    "linen bedding set product photo": 11,
    "face lotion product photo": 120,
    "solid perfume compact product photo": 6,
    "family tree photo frame product photo": 44,
    "desk lamp product photo": 47,
    "specialty coffee package": 34,
    "lunch box product photo": 65,
    "studio camera product photo": 112,
    "tennis racket product photo": 152,
}

OPEN_PRODUCT_FALLBACK_IMAGES = {
    "minimal canvas tote bag": "https://cdn.dummyjson.com/product-images/womens-bags/women-handbag-black/thumbnail.webp",
    "retro running sneakers": "https://cdn.dummyjson.com/product-images/mens-shoes/sports-sneakers-off-white-red/thumbnail.webp",
    "wireless headphones product photo": "https://cdn.dummyjson.com/product-images/mobile-accessories/apple-airpods-max-silver/thumbnail.webp",
    "wireless charging pad product photo": "https://cdn.dummyjson.com/product-images/mobile-accessories/apple-airpower-wireless-charger/thumbnail.webp",
    "black aluminium cup product photo": "https://cdn.dummyjson.com/product-images/kitchen-accessories/black-aluminium-cup/thumbnail.webp",
    "linen bedding set product photo": "https://cdn.dummyjson.com/product-images/furniture/annibale-colombo-bed/thumbnail.webp",
    "face lotion product photo": "https://cdn.dummyjson.com/product-images/skin-care/vaseline-men-body-and-face-lotion/thumbnail.webp",
    "solid perfume compact product photo": "https://cdn.dummyjson.com/product-images/fragrances/calvin-klein-ck-one/thumbnail.webp",
    "family tree photo frame product photo": "https://cdn.dummyjson.com/product-images/home-decoration/family-tree-photo-frame/thumbnail.webp",
    "desk lamp product photo": "https://cdn.dummyjson.com/product-images/home-decoration/table-lamp/thumbnail.webp",
    "specialty coffee package": "https://cdn.dummyjson.com/product-images/groceries/nescafe-coffee/thumbnail.webp",
    "lunch box product photo": "https://cdn.dummyjson.com/product-images/kitchen-accessories/lunch-box/thumbnail.webp",
    "studio camera product photo": "https://cdn.dummyjson.com/product-images/mobile-accessories/tv-studio-camera-pedestal/thumbnail.webp",
    "tennis racket product photo": "https://cdn.dummyjson.com/product-images/sports-accessories/tennis-racket/thumbnail.webp",
}


PRICE_BANDS = [
    ("초저가", 1_000, 4_500, 500),
    ("알뜰가", 5_000, 9_000, 1_000),
    ("저가", 10_000, 19_000, 1_000),
    ("중저가", 20_000, 39_000, 1_000),
    ("중가", 40_000, 69_000, 1_000),
    ("고가", 70_000, 99_000, 1_000),
    ("프리미엄", 100_000, 159_000, 1_000),
    ("하이엔드", 160_000, 249_000, 1_000),
]


def money(price_band: tuple[str, int, int, int]) -> int:
    _, low, high, step = price_band
    return random.randrange(low, high + step, step)


def fetch_open_product_images() -> dict[int, str]:
    request = urllib.request.Request(
        "https://dummyjson.com/products?limit=200&select=id,thumbnail",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return {}

    return {
        int(product["id"]): product["thumbnail"]
        for product in payload.get("products", [])
        if product.get("id") and product.get("thumbnail")
    }


def image_url(keyword: str, api_images: dict[int, str]) -> str:
    product_id = OPEN_PRODUCT_IMAGE_IDS.get(keyword)
    if product_id and product_id in api_images:
        return api_images[product_id]
    return OPEN_PRODUCT_FALLBACK_IMAGES.get(keyword, "/api/placeholder/missing.svg")


def generate_products(mood: str = "zero market") -> dict[str, Any]:
    DATA_DIR.mkdir(exist_ok=True)
    items = []
    seeds = random.sample(CATALOG_SEEDS, k=12)
    api_images = fetch_open_product_images()

    for index, seed_data in enumerate(seeds, start=1):
        uid = uuid4().hex[:8]
        adjective = random.choice(ADJECTIVES)
        price_band = PRICE_BANDS[(index - 1) % len(PRICE_BANDS)]
        price = money(price_band)
        product_seed = f"{uid}-{index}"
        benefit = random.sample(BENEFITS, k=3)
        category = seed_data["category"]

        items.append(
            {
                "id": uid,
                "name": f"{adjective} {seed_data['name']}",
                "category": category,
                "keyword": seed_data["keyword"],
                "price": price,
                "priceTier": price_band[0],
                "virtualPrice": f"{price:,}원",
                "tone": seed_data["tone"],
                "description": (
                    f"{seed_data['tone']}을 담은 가상 상품입니다. "
                    "상품을 살펴보고 장바구니에 담을 수 있지만 실제 구매는 진행되지 않습니다."
                ),
                "features": benefit,
                "image": image_url(seed_data["keyword"], api_images),
                "seed": product_seed,
                "accent": PALETTE.get(category, ("#1167d8", "#f8485e")),
                "inventory": random.randint(6, 34),
                "rating": round(random.uniform(4.1, 4.9), 1),
            }
        )

    payload = {
        "brand": "Zero Market",
        "subtitle": "소비 없는 소비 경험",
        "mood": mood,
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "items": items,
    }
    PRODUCTS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_products() -> dict[str, Any]:
    if not PRODUCTS_PATH.exists():
        return generate_products()
    return json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))


def product_illustration(name: str, category: str, color_a: str, color_b: str) -> str:
    common = f"""
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{color_a}"/>
      <stop offset="1" stop-color="{color_b}"/>
    </linearGradient>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#121318" flood-opacity="0.18"/>
    </filter>
  </defs>
  <rect width="900" height="900" fill="#f7f7fb"/>
  <path d="M0 150 C210 60 315 190 520 105 C650 52 775 80 900 22 V900 H0 Z" fill="url(#g)" opacity="0.14"/>
  <rect x="96" y="104" width="708" height="622" rx="42" fill="#ffffff" filter="url(#soft)"/>
"""
    label = f"""
  <text x="450" y="790" text-anchor="middle" font-family="Arial, sans-serif" font-size="38" font-weight="800" fill="#121318">{escape(name)}</text>
  <text x="450" y="838" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#6b7280">{escape(category)} · virtual item</text>
"""
    if "토트백" in name:
        art = """
  <path d="M292 384 C305 292 364 244 450 244 C536 244 595 292 608 384" fill="none" stroke="#121318" stroke-width="30" stroke-linecap="round"/>
  <rect x="250" y="350" width="400" height="274" rx="34" fill="url(#g)"/>
  <path d="M326 408 H574" stroke="#ffffff" stroke-width="18" stroke-linecap="round" opacity="0.45"/>
"""
    elif "스니커즈" in name:
        art = """
  <path d="M238 501 C328 482 382 405 466 420 C548 435 572 500 664 511 C705 516 731 544 725 583 C720 617 690 632 635 632 H286 C237 632 204 606 214 568 C220 545 225 520 238 501 Z" fill="url(#g)"/>
  <path d="M342 483 L458 573 M408 455 L524 583" stroke="#ffffff" stroke-width="18" stroke-linecap="round" opacity="0.65"/>
  <path d="M244 584 H716" stroke="#121318" stroke-width="18" stroke-linecap="round" opacity="0.18"/>
"""
    elif "헤드폰" in name:
        art = """
  <path d="M286 444 C286 306 354 236 450 236 C546 236 614 306 614 444" fill="none" stroke="#121318" stroke-width="38" stroke-linecap="round"/>
  <rect x="226" y="414" width="116" height="190" rx="46" fill="url(#g)"/>
  <rect x="558" y="414" width="116" height="190" rx="46" fill="url(#g)"/>
  <path d="M342 598 C380 632 520 632 558 598" fill="none" stroke="#121318" stroke-width="22" stroke-linecap="round" opacity="0.22"/>
"""
    elif "키보드" in name:
        art = """
  <rect x="214" y="330" width="472" height="256" rx="34" fill="url(#g)"/>
  <g fill="#ffffff" opacity="0.78">
    <rect x="262" y="384" width="58" height="42" rx="10"/><rect x="340" y="384" width="58" height="42" rx="10"/><rect x="418" y="384" width="58" height="42" rx="10"/><rect x="496" y="384" width="58" height="42" rx="10"/><rect x="574" y="384" width="58" height="42" rx="10"/>
    <rect x="278" y="456" width="58" height="42" rx="10"/><rect x="356" y="456" width="58" height="42" rx="10"/><rect x="434" y="456" width="58" height="42" rx="10"/><rect x="512" y="456" width="58" height="42" rx="10"/>
    <rect x="324" y="528" width="252" height="34" rx="12"/>
  </g>
"""
    elif "머그" in name:
        art = """
  <path d="M312 358 H548 V552 C548 612 500 648 430 648 C360 648 312 612 312 552 Z" fill="url(#g)"/>
  <path d="M548 414 H598 C648 414 674 447 674 492 C674 540 642 570 594 570 H548" fill="none" stroke="#121318" stroke-width="30" stroke-linecap="round"/>
  <path d="M366 270 C336 305 388 318 356 350 M452 260 C420 302 478 318 444 356 M532 276 C500 310 558 324 522 360" fill="none" stroke="#121318" stroke-width="18" stroke-linecap="round" opacity="0.22"/>
"""
    elif "침구" in name:
        art = """
  <rect x="214" y="348" width="472" height="238" rx="32" fill="url(#g)"/>
  <rect x="254" y="292" width="170" height="92" rx="24" fill="#ffffff" stroke="#121318" stroke-width="14" opacity="0.92"/>
  <rect x="476" y="292" width="170" height="92" rx="24" fill="#ffffff" stroke="#121318" stroke-width="14" opacity="0.92"/>
  <path d="M214 494 H686" stroke="#ffffff" stroke-width="20" opacity="0.45"/>
"""
    elif "세럼" in name:
        art = """
  <rect x="360" y="242" width="180" height="392" rx="42" fill="url(#g)"/>
  <rect x="392" y="194" width="116" height="70" rx="20" fill="#121318"/>
  <rect x="386" y="418" width="128" height="96" rx="22" fill="#ffffff" opacity="0.35"/>
  <circle cx="450" cy="466" r="28" fill="#ffffff" opacity="0.75"/>
"""
    elif "퍼퓸" in name:
        art = """
  <rect x="300" y="316" width="300" height="280" rx="70" fill="url(#g)"/>
  <circle cx="450" cy="456" r="86" fill="#ffffff" opacity="0.26"/>
  <path d="M392 456 H508 M450 398 V514" stroke="#ffffff" stroke-width="20" stroke-linecap="round" opacity="0.66"/>
"""
    elif "노트" in name:
        art = """
  <rect x="306" y="246" width="304" height="420" rx="24" fill="url(#g)"/>
  <path d="M360 246 V666" stroke="#121318" stroke-width="16" opacity="0.24"/>
  <path d="M406 362 H548 M406 430 H548 M406 498 H528" stroke="#ffffff" stroke-width="18" stroke-linecap="round" opacity="0.56"/>
"""
    elif "램프" in name:
        art = """
  <path d="M360 310 H540 L606 462 H294 Z" fill="url(#g)"/>
  <path d="M450 462 V624 M350 624 H550" stroke="#121318" stroke-width="28" stroke-linecap="round"/>
  <circle cx="450" cy="390" r="44" fill="#ffffff" opacity="0.34"/>
"""
    elif "원두" in name:
        art = """
  <path d="M320 260 H580 L620 636 H280 Z" fill="url(#g)"/>
  <path d="M346 318 H554" stroke="#ffffff" stroke-width="18" opacity="0.5"/>
  <ellipse cx="410" cy="478" rx="44" ry="68" fill="#121318" opacity="0.22"/>
  <ellipse cx="500" cy="498" rx="44" ry="68" fill="#ffffff" opacity="0.42"/>
  <path d="M408 424 C382 470 420 505 410 532 M498 444 C472 490 512 526 500 552" stroke="#ffffff" stroke-width="10" opacity="0.7"/>
"""
    elif "스낵" in name:
        art = """
  <rect x="290" y="274" width="320" height="350" rx="36" fill="url(#g)"/>
  <path d="M326 342 H574 M326 554 H574" stroke="#ffffff" stroke-width="20" opacity="0.5"/>
  <circle cx="408" cy="458" r="46" fill="#ffffff" opacity="0.32"/>
  <circle cx="498" cy="458" r="46" fill="#121318" opacity="0.2"/>
"""
    elif "카메라" in name:
        art = """
  <rect x="242" y="332" width="416" height="250" rx="40" fill="url(#g)"/>
  <rect x="318" y="286" width="132" height="62" rx="20" fill="#121318"/>
  <circle cx="450" cy="460" r="88" fill="#ffffff" opacity="0.4"/>
  <circle cx="450" cy="460" r="50" fill="#121318" opacity="0.34"/>
  <circle cx="584" cy="388" r="24" fill="#ffffff" opacity="0.74"/>
"""
    else:
        art = """
  <path d="M354 314 C286 360 262 466 310 550 C358 636 480 650 560 590 C620 546 653 460 610 380 C562 290 432 260 354 314 Z" fill="url(#g)"/>
  <circle cx="394" cy="394" r="28" fill="#ffffff" opacity="0.62"/>
  <circle cx="496" cy="374" r="32" fill="#ffffff" opacity="0.42"/>
  <circle cx="540" cy="486" r="36" fill="#ffffff" opacity="0.36"/>
  <path d="M360 562 C420 512 472 640 548 572" fill="none" stroke="#ffffff" stroke-width="24" stroke-linecap="round" opacity="0.62"/>
"""
    return common + art + label


def studio_photo_fallback(name: str, category: str, color_a: str, color_b: str) -> str:
    return f"""
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#f8fafc"/>
      <stop offset="0.52" stop-color="#eef3f9"/>
      <stop offset="1" stop-color="#e8edf6"/>
    </linearGradient>
    <linearGradient id="object" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{color_a}"/>
      <stop offset="1" stop-color="{color_b}"/>
    </linearGradient>
    <radialGradient id="light" cx="42%" cy="24%" r="72%">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.78"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
    <filter id="shadow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="20"/>
      <feOffset dx="0" dy="24" result="offset"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.22"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="900" height="900" fill="url(#bg)"/>
  <rect width="900" height="900" fill="url(#light)"/>
  <path d="M-30 676 C166 566 316 602 486 510 C648 422 766 468 930 350 V900 H-30 Z" fill="{color_a}" opacity="0.12"/>
  <ellipse cx="458" cy="662" rx="250" ry="48" fill="#111827" opacity="0.13"/>
  <g filter="url(#shadow)">
    <rect x="296" y="244" width="308" height="348" rx="58" fill="url(#object)"/>
    <path d="M296 330 C364 285 468 292 604 254 V244 H354 C322 244 296 270 296 302 Z" fill="#ffffff" opacity="0.28"/>
    <rect x="348" y="416" width="204" height="112" rx="28" fill="#ffffff" opacity="0.3"/>
    <rect x="376" y="454" width="148" height="18" rx="9" fill="#ffffff" opacity="0.64"/>
    <rect x="396" y="492" width="108" height="14" rx="7" fill="#ffffff" opacity="0.45"/>
  </g>
  <text x="450" y="748" text-anchor="middle" font-family="Arial, sans-serif" font-size="36" font-weight="800" fill="#111827">{escape(name)}</text>
  <text x="450" y="796" text-anchor="middle" font-family="Arial, sans-serif" font-size="23" fill="#64748b">{escape(category)} 대체 상품 이미지</text>
"""


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/products")
def products() -> Response:
    return jsonify(load_products())


@app.post("/api/regenerate")
def regenerate() -> Response:
    payload = request.get_json(silent=True) or {}
    mood = str(payload.get("mood") or "zero market").strip()[:40]
    return jsonify(generate_products(mood=mood or "zero market"))


@app.post("/api/checkout")
def checkout() -> Response:
    payload = request.get_json(silent=True) or {}
    cart = payload.get("cart") or []
    products_by_id = {item["id"]: item for item in load_products()["items"]}
    total = 0
    count = 0

    for line in cart:
        product = products_by_id.get(line.get("id"))
        qty = max(0, int(line.get("qty", 0)))
        if product and qty:
            total += product["price"] * qty
            count += qty

    return jsonify(
        {
            "orderId": f"ZERO-{uuid4().hex[:6].upper()}",
            "itemCount": count,
            "total": total,
            "message": "가상 결제가 완료되었습니다. 실제 결제나 배송은 발생하지 않습니다.",
            "completedAt": datetime.now().isoformat(timespec="seconds"),
        }
    )


@app.get("/api/placeholder/<product_id>.svg")
def placeholder(product_id: str) -> Response:
    products_by_id = {item["id"]: item for item in load_products()["items"]}
    product = products_by_id.get(product_id)
    name = product["name"] if product else "Zero Market"
    category = product["category"] if product else "가상 상품"
    color_a, color_b = product["accent"] if product else ("#1167d8", "#f8485e")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 900" '
        f'role="img" aria-label="{escape(name)}">'
        f"{studio_photo_fallback(name, category, color_a, color_b)}</svg>"
    )
    return Response(svg, mimetype="image/svg+xml")


generate_products()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=True, host="0.0.0.0", port=port)
