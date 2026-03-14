"""
네이버 데이터랩 API — 음식/브랜드 급상승 검색어 수집
API 신청: https://developers.naver.com/apps/#/register
필요 환경변수: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
"""
import os
import requests
from datetime import datetime, timedelta

NAVER_API_URL = "https://openapi.naver.com/v1/datalab/search"

# 수집 대상 키워드 그룹 (최대 5개 그룹 / 그룹당 최대 5개 키워드)
# groupName = 다른 채널(Google Trends, YouTube)과 매칭되는 대표 키워드명
MENU_KEYWORD_GROUPS = [
    {"groupName": "마라탕",         "keywords": ["마라탕", "마라샹궈", "훠궈"]},
    {"groupName": "버블티",         "keywords": ["버블티", "흑당버블티", "타피오카"]},
    {"groupName": "무한리필 고기",  "keywords": ["무한리필 고기", "삼겹살", "소고기"]},
    {"groupName": "한식뷔페",       "keywords": ["한식뷔페", "무한리필", "뷔페"]},
    {"groupName": "로제떡볶이",     "keywords": ["로제떡볶이", "떡볶이", "순대"]},
]

BRAND_KEYWORD_GROUPS = [
    {"groupName": "빽다방",         "keywords": ["빽다방"]},
    {"groupName": "교촌치킨",       "keywords": ["교촌치킨"]},
    {"groupName": "맘스터치",       "keywords": ["맘스터치"]},
    {"groupName": "컴포즈커피",     "keywords": ["컴포즈커피"]},
    {"groupName": "투썸플레이스",   "keywords": ["투썸플레이스"]},
]


def _fetch_datalab(keyword_groups: list) -> dict:
    """네이버 데이터랩 API 호출 → 키워드별 검색량 지수 반환"""
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise EnvironmentError("NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 환경변수 필요")

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": keyword_groups,
    }
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json",
    }

    resp = requests.post(NAVER_API_URL, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _extract_latest_scores(datalab_result: dict) -> dict:
    """결과에서 각 그룹의 최신 날짜 ratio 값 추출"""
    scores = {}
    for result in datalab_result.get("results", []):
        group_name = result["title"]
        data = result.get("data", [])
        if data:
            scores[group_name] = data[-1]["ratio"]  # 가장 최신 날짜 값
    return scores


def fetch_menu_scores() -> dict:
    """메뉴 탭용 네이버 검색량 지수 반환 {keyword_group_name: ratio}"""
    try:
        result = _fetch_datalab(MENU_KEYWORD_GROUPS)
        return _extract_latest_scores(result)
    except Exception as e:
        print(f"[Naver] 메뉴 수집 실패: {e}")
        return {}


def fetch_brand_scores() -> dict:
    """브랜드 탭용 네이버 검색량 지수 반환 {keyword_group_name: ratio}"""
    try:
        result = _fetch_datalab(BRAND_KEYWORD_GROUPS)
        return _extract_latest_scores(result)
    except Exception as e:
        print(f"[Naver] 브랜드 수집 실패: {e}")
        return {}
