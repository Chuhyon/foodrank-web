"""
네이버 블로그 검색 API — 최근 맛집·음식 블로그에서 키워드 동적 추출
필요 환경변수: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
"""
import os
import requests
from collections import Counter
from food_filter import MENU_KEYWORDS, BRAND_KEYWORDS, extract_menu_keywords, extract_brand_keywords

NAVER_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"

MENU_QUERIES  = ["맛집 추천", "요즘 뜨는 음식", "외식 추천", "음식 트렌드", "핫플 맛집", "신메뉴 후기"]
BRAND_QUERIES = ["프랜차이즈 추천", "브랜드 맛집", "치킨 맛집", "카페 추천", "버거 맛집", "신규 매장"]


def _get_headers() -> dict:
    return {
        "X-Naver-Client-Id":     os.environ.get("NAVER_CLIENT_ID", ""),
        "X-Naver-Client-Secret": os.environ.get("NAVER_CLIENT_SECRET", ""),
    }


def _search_blog(query: str, display: int = 50) -> list:
    """블로그 검색 결과 제목 리스트 반환"""
    params = {"query": query, "display": display, "sort": "date"}
    try:
        resp = requests.get(NAVER_BLOG_URL, headers=_get_headers(), params=params, timeout=10)
        resp.raise_for_status()
        return [item.get("title", "") for item in resp.json().get("items", [])]
    except Exception as e:
        print(f"[NaverBlog] 검색 실패 ({query}): {e}")
        return []


def _count_from_titles(titles: list, extract_fn) -> dict:
    """제목 리스트에서 키워드 등장 횟수 집계"""
    counter = Counter()
    for title in titles:
        clean = title.replace("<b>", "").replace("</b>", "")
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
    """맛집·음식 블로그에서 메뉴 키워드 빈도 점수 반환"""
    try:
        titles = []
        for query in MENU_QUERIES:
            titles.extend(_search_blog(query))
        counts = _count_from_titles(titles, extract_menu_keywords)
        result = _normalize(counts)
        print(f"[NaverBlog] 메뉴 {len(result)}개 키워드 수집")
        return result
    except Exception as e:
        print(f"[NaverBlog] 메뉴 수집 실패: {e}")
        return {}


def fetch_brand_scores() -> dict:
    """맛집·카페 블로그에서 브랜드 키워드 빈도 점수 반환"""
    try:
        titles = []
        for query in BRAND_QUERIES:
            titles.extend(_search_blog(query))
        counts = _count_from_titles(titles, extract_brand_keywords)
        result = _normalize(counts)
        print(f"[NaverBlog] 브랜드 {len(result)}개 키워드 수집")
        return result
    except Exception as e:
        print(f"[NaverBlog] 브랜드 수집 실패: {e}")
        return {}
