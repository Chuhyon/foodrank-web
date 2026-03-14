"""
KAMIS(농수산식품유통공사) 공공 오픈API — 식자재 도매가 수집
API 신청: https://www.kamis.or.kr/customer/reference/openapi_list.do
필요 환경변수: KAMIS_CERT_KEY, KAMIS_CERT_ID
"""
import os
import requests
from datetime import datetime, timedelta

KAMIS_URL = "https://www.kamis.or.kr/service/price/xml.do"

# 수집 대상 식자재 카테고리 코드 (KAMIS 기준)
CATEGORY_CODES = [
    "100",  # 식량작물 (쌀, 잡곡)
    "200",  # 채소류 (배추, 무, 대파, 양파, 상추, 고추)
    "300",  # 특용작물 (마늘, 생강)
    "400",  # 과일류
    "500",  # 축산물 (돼지고기, 달걀)
    "600",  # 수산물
]


def _fetch_daily_price(category_code: str) -> list:
    """KAMIS 카테고리별 전일 대비 도매가 수집"""
    cert_key = os.environ.get("KAMIS_CERT_KEY")
    cert_id = os.environ.get("KAMIS_CERT_ID")

    if not cert_key or not cert_id:
        raise EnvironmentError("KAMIS_CERT_KEY, KAMIS_CERT_ID 환경변수 필요")

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    params = {
        "action": "dailyPriceByCategoryList",
        "p_product_cls_code": "02",   # 도매
        "p_country_code": "1101",     # 서울 가락시장
        "p_regday": today,
        "p_convert_kg_yn": "Y",
        "p_item_category_code": category_code,
        "p_cert_key": cert_key,
        "p_cert_id": cert_id,
        "p_returntype": "json",
    }

    resp = requests.get(KAMIS_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    items = data.get("data", {}).get("item", [])
    return items if isinstance(items, list) else []


def fetch_price_top10() -> list:
    """
    전일 대비 도매가 변동률 기준 TOP10 식자재 반환
    반환 형식: [{"item_name", "today_price", "yesterday_price", "change_rate", "direction"}, ...]
    """
    all_items = []

    for category_code in CATEGORY_CODES:
        try:
            items = _fetch_daily_price(category_code)
            for item in items:
                try:
                    today_price = float(str(item.get("dpr1", "0")).replace(",", ""))
                    yesterday_price = float(str(item.get("dpr2", "0")).replace(",", ""))

                    if yesterday_price <= 0 or today_price <= 0:
                        continue

                    change_rate = (today_price - yesterday_price) / yesterday_price * 100
                    all_items.append({
                        "item_name": item.get("itemname", ""),
                        "today_price": int(today_price),
                        "yesterday_price": int(yesterday_price),
                        "change_rate": round(change_rate, 1),
                        "direction": "up" if change_rate > 0 else "down",
                    })
                except (ValueError, ZeroDivisionError):
                    continue
        except Exception as e:
            print(f"[KAMIS] 카테고리 {category_code} 수집 실패: {e}")
            continue

    # 절댓값 기준 정렬 → TOP10
    sorted_items = sorted(all_items, key=lambda x: abs(x["change_rate"]), reverse=True)
    return sorted_items[:10]
