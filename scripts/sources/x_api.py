"""
X(Twitter) API v2 — 음식·외식 관련 급증 언급 키워드 수집
API 신청: https://developer.twitter.com/en/portal/dashboard
필요 환경변수: X_BEARER_TOKEN
가중치: 0.10 (낮음 — 정책 변동 대비)
"""
import os
import requests
from collections import Counter
from food_filter import extract_menu_keywords, extract_brand_keywords

SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

MENU_QUERIES  = ["마라탕 맛집", "버블티 맛있는", "무한리필 추천", "로제떡볶이", "편의점 도시락"]
BRAND_QUERIES = ["빽다방", "교촌치킨", "맘스터치", "컴포즈커피", "메가MGC커피"]


def _search_tweets(query: str, max_results: int = 100) -> list:
    bearer_token = os.environ.get("X_BEARER_TOKEN")
    if not bearer_token:
        raise EnvironmentError("X_BEARER_TOKEN 환경변수 필요")

    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {
        "query":       f"{query} lang:ko -is:retweet",
        "max_results": max_results,
        "tweet.fields": "public_metrics",
    }
    resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return [t.get("text", "") for t in resp.json().get("data", [])]


def _count_keywords(texts: list, extract_fn) -> dict:
    counter = Counter()
    for text in texts:
        for kw in extract_fn(text):
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
    """메뉴 관련 X 언급량 점수 반환"""
    try:
        texts = []
        for query in MENU_QUERIES:
            texts.extend(_search_tweets(query, max_results=100))
        result = _normalize(_count_keywords(texts, extract_menu_keywords))
        print(f"[X_API] 메뉴 {len(result)}개 키워드 수집")
        return result
    except Exception as e:
        print(f"[X_API] 메뉴 수집 실패: {e}")
        return {}


def fetch_brand_scores() -> dict:
    """브랜드 관련 X 언급량 점수 반환"""
    try:
        texts = []
        for query in BRAND_QUERIES:
            texts.extend(_search_tweets(query, max_results=100))
        result = _normalize(_count_keywords(texts, extract_brand_keywords))
        print(f"[X_API] 브랜드 {len(result)}개 키워드 수집")
        return result
    except Exception as e:
        print(f"[X_API] 브랜드 수집 실패: {e}")
        return {}
