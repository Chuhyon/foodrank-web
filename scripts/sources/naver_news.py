"""
네이버 뉴스 검색 API — 최근 식품·외식 뉴스에서 키워드 동적 추출
필요 환경변수: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
"""
import os
import requests
from collections import Counter
from .food_filter import extract_menu_keywords, extract_brand_keywords

NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"

MENU_QUERIES  = ["음식 트렌드", "맛집 인기", "외식 트렌드", "푸드 트렌드", "신메뉴 출시"]
BRAND_QUERIES = ["프랜차이즈 트렌드", "외식 브랜드", "식음료 업계", "외식 신규 오픈"]


def _get_headers() -> dict:
    return {
        "X-Naver-Client-Id":     os.environ.get("NAVER_CLIENT_ID", ""),
        "X-Naver-Client-Secret": os.environ.get("NAVER_CLIENT_SECRET", ""),
    }


def _search_news(query: str, display: int = 50) -> list:
    """뉴스 검색 결과 제목 리스트 반환"""
    params = {"query": query, "display": display, "sort": "date"}
    try:
        resp = requests.get(NAVER_NEWS_URL, headers=_get_headers(), params=params, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        return [item.get("title", "") + " " + item.get("description", "") for item in items]
    except Exception as e:
        print(f"[NaverNews] 검색 실패 ({query}): {e}")
        return []


def _count_from_texts(texts: list, extract_fn) -> dict:
    counter = Counter()
    for text in texts:
        clean = text.replace("<b>", "").replace("</b>", "")
        for kw in extract_fn(clean):
            counter[kw] += 1
    return dict(counter)


def _normalize(scores: dict) -> dict:
    if not scores:
        return {}
    max_val = max(scores.values())
    if max_val == 0:
        return {}
    return {k: round(v / max_val * 100, 1) for k, v in scores.items()}


def fetch_menu_scores() -> dict:
    """외식·음식 뉴스에서 메뉴 키워드 빈도 점수 반환"""
    try:
        texts = []
        for query in MENU_QUERIES:
            texts.extend(_search_news(query))
        counts = _count_from_texts(texts, extract_menu_keywords)
        result = _normalize(counts)
        print(f"[NaverNews] 메뉴 {len(result)}개 키워드 수집")
        return result
    except Exception as e:
        print(f"[NaverNews] 메뉴 수집 실패: {e}")
        return {}


def fetch_brand_scores() -> dict:
    """외식·브랜드 뉴스에서 브랜드 키워드 빈도 점수 반환"""
    try:
        texts = []
        for query in BRAND_QUERIES:
            texts.extend(_search_news(query))
        counts = _count_from_texts(texts, extract_brand_keywords)
        result = _normalize(counts)
        print(f"[NaverNews] 브랜드 {len(result)}개 키워드 수집")
        return result
    except Exception as e:
        print(f"[NaverNews] 브랜드 수집 실패: {e}")
        return {}
