"""
네이버 쇼핑 검색 API — 식품 카테고리 검색량으로 키워드 인기도 측정
필요 환경변수: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
"""
import os
import requests
from .food_filter import MENU_KEYWORDS, BRAND_KEYWORDS

NAVER_SHOP_URL = "https://openapi.naver.com/v1/search/shop.json"

# 쇼핑에서 의미있는 식품 키워드 풀 (배달·밀키트·식재료 중심)
MENU_KEYWORD_POOL = [
    "마라탕", "마라샹궈", "훠궈", "버블티", "떡볶이", "로제떡볶이",
    "삼겹살", "갈비", "불고기", "곱창", "족발", "보쌈",
    "초밥", "라멘", "파스타", "스테이크",
    "냉면", "비빔밥", "삼계탕", "국밥",
    "밀키트", "편의점 도시락", "도시락",
    "한식뷔페", "무한리필",
]

BRAND_KEYWORD_POOL = [
    "빽다방", "메가커피", "컴포즈커피",
    "교촌치킨", "BBQ", "bhc",
    "맘스터치", "노브랜드버거",
    "투썸플레이스", "할리스",
    "파리바게뜨", "뚜레쥬르",
]


def _get_headers() -> dict:
    return {
        "X-Naver-Client-Id":     os.environ.get("NAVER_CLIENT_ID", ""),
        "X-Naver-Client-Secret": os.environ.get("NAVER_CLIENT_SECRET", ""),
    }


def _get_shopping_total(keyword: str) -> int:
    """키워드의 쇼핑 검색 결과 총 건수 반환"""
    params = {"query": keyword, "display": 1, "sort": "sim"}
    try:
        resp = requests.get(NAVER_SHOP_URL, headers=_get_headers(), params=params, timeout=8)
        resp.raise_for_status()
        return resp.json().get("total", 0)
    except Exception:
        return 0


def _fetch_scores(keyword_pool: list) -> dict:
    """키워드 풀 전체 쇼핑 검색량 조회 후 정규화 점수 반환"""
    raw = {}
    for kw in keyword_pool:
        total = _get_shopping_total(kw)
        if total > 0:
            raw[kw] = total

    if not raw:
        return {}

    max_val = max(raw.values())
    return {k: round(v / max_val * 100, 1) for k, v in raw.items()}


def fetch_menu_scores() -> dict:
    """식품 쇼핑 검색량 기반 메뉴 키워드 점수 반환"""
    try:
        result = _fetch_scores(MENU_KEYWORD_POOL)
        print(f"[NaverShopping] 메뉴 {len(result)}개 키워드 수집")
        return result
    except Exception as e:
        print(f"[NaverShopping] 메뉴 수집 실패: {e}")
        return {}


def fetch_brand_scores() -> dict:
    """브랜드 쇼핑 검색량 기반 브랜드 키워드 점수 반환"""
    try:
        result = _fetch_scores(BRAND_KEYWORD_POOL)
        print(f"[NaverShopping] 브랜드 {len(result)}개 키워드 수집")
        return result
    except Exception as e:
        print(f"[NaverShopping] 브랜드 수집 실패: {e}")
        return {}
