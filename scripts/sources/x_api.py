"""
X(Twitter) API v2 — 음식·외식 관련 급증 언급 키워드 수집
API 신청: https://developer.twitter.com/en/portal/dashboard
필요 환경변수: X_BEARER_TOKEN
가중치: 0.15 (낮음 — 정책 변동 대비)
"""
import os
import requests
from collections import Counter

SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

MENU_QUERIES = ["마라탕 맛집", "버블티 맛있는", "무한리필 추천", "로제떡볶이", "편의점 도시락"]
BRAND_QUERIES = ["빽다방", "교촌치킨", "맘스터치", "컴포즈커피", "메가MGC커피"]

FOOD_KEYWORDS = [
    "마라탕", "마라샹궈", "버블티", "무한리필", "떡볶이", "로제",
    "초밥", "파스타", "편의점 도시락", "한식뷔페", "스몰비어",
    "빽다방", "교촌", "맘스터치", "컴포즈", "메가커피", "노브랜드",
]


def _search_tweets(query: str, max_results: int = 100) -> list:
    bearer_token = os.environ.get("X_BEARER_TOKEN")
    if not bearer_token:
        raise EnvironmentError("X_BEARER_TOKEN 환경변수 필요")

    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {
        "query": f"{query} lang:ko -is:retweet",
        "max_results": max_results,
        "tweet.fields": "public_metrics",
    }

    resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("data", [])


def _extract_keyword_scores(tweets: list) -> dict:
    """트윗 텍스트에서 키워드 언급 횟수 집계"""
    counter = Counter()
    for tweet in tweets:
        text = tweet.get("text", "")
        for kw in FOOD_KEYWORDS:
            if kw in text:
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
        all_tweets = []
        for query in MENU_QUERIES:
            all_tweets.extend(_search_tweets(query, max_results=100))
        return _normalize(_extract_keyword_scores(all_tweets))
    except Exception as e:
        print(f"[X_API] 메뉴 수집 실패: {e}")
        return {}


def fetch_brand_scores() -> dict:
    """브랜드 관련 X 언급량 점수 반환"""
    try:
        all_tweets = []
        for query in BRAND_QUERIES:
            all_tweets.extend(_search_tweets(query, max_results=100))
        return _normalize(_extract_keyword_scores(all_tweets))
    except Exception as e:
        print(f"[X_API] 브랜드 수집 실패: {e}")
        return {}
