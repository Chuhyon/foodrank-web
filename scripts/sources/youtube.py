"""
YouTube Data API v3 — 한국 인기 음식 영상에서 키워드 동적 추출
API 발급: https://console.cloud.google.com/ → YouTube Data API v3 활성화
필요 환경변수: YOUTUBE_API_KEY
"""
import os
from googleapiclient.discovery import build
from collections import Counter
from .food_filter import extract_menu_keywords, extract_brand_keywords


def _build_youtube():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise EnvironmentError("YOUTUBE_API_KEY 환경변수 필요")
    return build("youtube", "v3", developerKey=api_key)


def _get_popular_titles(youtube, category_id: str = "26", max_results: int = 50) -> list:
    """한국 인기 동영상 제목 리스트 반환"""
    request = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        regionCode="KR",
        videoCategoryId=category_id,
        maxResults=max_results,
    )
    response = request.execute()
    return [item["snippet"].get("title", "") for item in response.get("items", [])]


def _count_keywords(titles: list, extract_fn) -> dict:
    counter = Counter()
    for title in titles:
        for kw in extract_fn(title):
            counter[kw] += 1
    return dict(counter)


def _normalize(scores: dict) -> dict:
    if not scores:
        return {}
    max_val = max(scores.values())
    if max_val == 0:
        return {}
    return {kw: round(count / max_val * 100, 1) for kw, count in scores.items()}


def fetch_menu_scores() -> dict:
    """인기 음식 영상 제목에서 메뉴 키워드 빈도 점수 반환"""
    try:
        youtube = _build_youtube()
        # 음식 카테고리(26) 인기 영상 + 전체 카테고리 인기 영상(먹방 포함)
        titles = _get_popular_titles(youtube, category_id="26", max_results=50)
        titles += _get_popular_titles(youtube, category_id="1",  max_results=50)  # 엔터테인먼트(먹방)
        counts = _count_keywords(titles, extract_menu_keywords)
        result = _normalize(counts)
        print(f"[YouTube] 메뉴 {len(result)}개 키워드 수집")
        return result
    except Exception as e:
        print(f"[YouTube] 메뉴 수집 실패: {e}")
        return {}


def fetch_brand_scores() -> dict:
    """인기 영상 제목에서 브랜드 키워드 빈도 점수 반환"""
    try:
        youtube = _build_youtube()
        titles = _get_popular_titles(youtube, max_results=50)
        counts = _count_keywords(titles, extract_brand_keywords)
        result = _normalize(counts)
        print(f"[YouTube] 브랜드 {len(result)}개 키워드 수집")
        return result
    except Exception as e:
        print(f"[YouTube] 브랜드 수집 실패: {e}")
        return {}
