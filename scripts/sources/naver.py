"""
네이버 데이터랩 API — 다른 채널에서 발견된 상위 키워드 검색량 검증(validator)
API 신청: https://developers.naver.com/apps/#/register
필요 환경변수: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
"""
import os
import requests
from datetime import datetime, timedelta

NAVER_API_URL = "https://openapi.naver.com/v1/datalab/search"
BATCH_SIZE = 5  # DataLab API 최대 그룹 수


def _get_headers() -> dict:
    return {
        "X-Naver-Client-Id":     os.environ.get("NAVER_CLIENT_ID", ""),
        "X-Naver-Client-Secret": os.environ.get("NAVER_CLIENT_SECRET", ""),
        "Content-Type": "application/json",
    }


def _fetch_datalab(keyword_groups: list) -> dict:
    """네이버 데이터랩 API 호출"""
    end_date   = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    payload = {
        "startDate":    start_date,
        "endDate":      end_date,
        "timeUnit":     "date",
        "keywordGroups": keyword_groups,
    }
    resp = requests.post(NAVER_API_URL, json=payload, headers=_get_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json()


def _extract_latest_scores(datalab_result: dict) -> dict:
    """각 그룹의 최신 날짜 ratio 값 추출"""
    scores = {}
    for result in datalab_result.get("results", []):
        group_name = result["title"]
        data = result.get("data", [])
        if data:
            scores[group_name] = data[-1]["ratio"]
    return scores


def _normalize_batch(scores: dict) -> dict:
    """배치 내 점수를 0~100으로 정규화"""
    if not scores:
        return {}
    max_val = max(scores.values())
    if max_val == 0:
        return scores
    return {k: round(v / max_val * 100, 1) for k, v in scores.items()}


def validate_keywords(keywords: list) -> dict:
    """
    다른 채널에서 발견된 키워드들의 네이버 검색량 점수 반환
    5개씩 배치 처리 후 배치별 정규화로 합산
    """
    if not keywords:
        return {}

    all_scores = {}
    for i in range(0, len(keywords), BATCH_SIZE):
        batch = keywords[i:i + BATCH_SIZE]
        groups = [{"groupName": kw, "keywords": [kw]} for kw in batch]
        try:
            result = _fetch_datalab(groups)
            raw = _extract_latest_scores(result)
            normalized = _normalize_batch(raw)
            all_scores.update(normalized)
        except Exception as e:
            print(f"[Naver] 배치 검증 실패 {batch}: {e}")

    return all_scores


# collect_all.py 호환 인터페이스 — validate_keywords를 직접 호출
def fetch_menu_scores(candidates: list) -> dict:
    """메뉴 키워드 후보 검증"""
    try:
        return validate_keywords(candidates)
    except Exception as e:
        print(f"[Naver] 메뉴 검증 실패: {e}")
        return {}


def fetch_brand_scores(candidates: list) -> dict:
    """브랜드 키워드 후보 검증"""
    try:
        return validate_keywords(candidates)
    except Exception as e:
        print(f"[Naver] 브랜드 검증 실패: {e}")
        return {}
