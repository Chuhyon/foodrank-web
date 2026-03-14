"""
YouTube Data API v3 — 음식·외식 관련 급상승 동영상 키워드 수집
API 발급: https://console.cloud.google.com/ → YouTube Data API v3 활성화
필요 환경변수: YOUTUBE_API_KEY
"""
import os
import re
from googleapiclient.discovery import build
from collections import Counter

# 음식 관련 검색어로 키워드 추출 시 사용할 패턴
FOOD_KEYWORDS = [
    "마라탕", "마라샹궈", "훠궈", "버블티", "무한리필", "떡볶이", "로제",
    "삼겹살", "곱창", "막창", "초밥", "라멘", "파스타", "피자", "햄버거",
    "치킨", "순대", "국밥", "냉면", "비빔밥", "갈비", "삼계탕", "보쌈",
    "족발", "스테이크", "타코", "케밥", "쌀국수", "팟타이", "스시", "돈부리",
    "빽다방", "메가커피", "컴포즈", "교촌", "BBQ", "bhc", "맘스터치",
    "노브랜드", "투썸", "할리스", "파리바게뜨", "뚜레쥬르",
]


def _extract_keywords_from_title(title: str) -> list:
    """영상 제목에서 음식 관련 키워드 추출"""
    found = []
    title_lower = title.lower()
    for kw in FOOD_KEYWORDS:
        if kw in title:
            found.append(kw)
    return found


def fetch_menu_scores() -> dict:
    """음식 관련 급상승 YouTube 영상 제목 → 키워드 빈도 점수 반환"""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise EnvironmentError("YOUTUBE_API_KEY 환경변수 필요")

    try:
        youtube = build("youtube", "v3", developerKey=api_key)

        # 급상승 동영상 (한국, 음식 카테고리 26)
        request = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode="KR",
            videoCategoryId="26",  # 음식
            maxResults=50,
        )
        response = request.execute()

        keyword_counter = Counter()
        for item in response.get("items", []):
            title = item["snippet"].get("title", "")
            keywords = _extract_keywords_from_title(title)
            for kw in keywords:
                keyword_counter[kw] += 1

        # 정규화: 최대값 기준 0~100
        if not keyword_counter:
            return {}
        max_count = max(keyword_counter.values())
        return {kw: round(count / max_count * 100, 1) for kw, count in keyword_counter.items()}

    except Exception as e:
        print(f"[YouTube] 메뉴 수집 실패: {e}")
        return {}


def fetch_brand_scores() -> dict:
    """브랜드 관련 YouTube 영상 → 브랜드 빈도 점수 반환"""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise EnvironmentError("YOUTUBE_API_KEY 환경변수 필요")

    try:
        youtube = build("youtube", "v3", developerKey=api_key)

        # 급상승 동영상 전체 (한국)
        request = youtube.videos().list(
            part="snippet",
            chart="mostPopular",
            regionCode="KR",
            maxResults=50,
        )
        response = request.execute()

        brand_keywords = [kw for kw in FOOD_KEYWORDS if any(
            b in kw for b in ["빽다방", "메가커피", "컴포즈", "교촌", "BBQ", "bhc",
                               "맘스터치", "노브랜드", "투썸", "할리스", "파리바게뜨"]
        )]

        keyword_counter = Counter()
        for item in response.get("items", []):
            title = item["snippet"].get("title", "")
            for kw in brand_keywords:
                if kw in title:
                    keyword_counter[kw] += 1

        if not keyword_counter:
            return {}
        max_count = max(keyword_counter.values())
        return {kw: round(count / max_count * 100, 1) for kw, count in keyword_counter.items()}

    except Exception as e:
        print(f"[YouTube] 브랜드 수집 실패: {e}")
        return {}
