"""
Google Trends (pytrends) — 한국 실시간 급상승 검색어에서 음식 키워드 동적 수집
비공식 라이브러리 — 차단 가능성 있음 (FRD-08 R1 참조)
필요 환경변수: 없음
"""
import time
from pytrends.request import TrendReq
from food_filter import is_menu_keyword, is_brand_keyword, MENU_KEYWORDS, BRAND_KEYWORDS

CHUNK_SIZE = 5

# trending_searches에서 음식 키워드가 없을 때 사용하는 시드
MENU_SEED_KEYWORDS  = ["음식", "맛집", "외식"]
BRAND_SEED_KEYWORDS = ["치킨", "카페", "버거"]


def _build_pytrends() -> TrendReq:
    return TrendReq(hl="ko-KR", tz=540, timeout=(10, 25))


def _fetch_interest(keywords: list) -> dict:
    """키워드 목록의 Google Trends 관심도 점수 반환 (0~100)"""
    pytrends = _build_pytrends()
    scores = {}
    for i in range(0, len(keywords), CHUNK_SIZE):
        chunk = keywords[i:i + CHUNK_SIZE]
        try:
            pytrends.build_payload(chunk, cat=71, timeframe="now 7-d", geo="KR")
            df = pytrends.interest_over_time()
            if df.empty:
                continue
            for kw in chunk:
                if kw in df.columns:
                    scores[kw] = float(df[kw].iloc[-1])
            time.sleep(2)
        except Exception as e:
            print(f"[GoogleTrends] 관심도 조회 실패 {chunk}: {e}")
    return scores


def _get_trending_keywords(filter_fn) -> list:
    """
    한국 급상승 검색어 → filter_fn 통과한 키워드 반환
    없으면 시드 키워드의 급상승 관련어로 fallback
    """
    pytrends = _build_pytrends()

    # 1차: 한국 실시간 급상승 검색어 필터링
    try:
        trending_df = pytrends.trending_searches(pn="south_korea")
        trending = trending_df[0].tolist()
        found = [kw for kw in trending if filter_fn(kw)]
        if found:
            return found
        print("[GoogleTrends] 급상승 검색어에서 해당 키워드 없음 — related_queries fallback")
    except Exception as e:
        print(f"[GoogleTrends] trending_searches 실패: {e}")

    # 2차 fallback: 시드 키워드의 급상승 관련어
    seeds = MENU_SEED_KEYWORDS if filter_fn == is_menu_keyword else BRAND_SEED_KEYWORDS
    try:
        pytrends.build_payload(seeds, cat=71, timeframe="now 7-d", geo="KR")
        related = pytrends.related_queries()
        rising = []
        for seed in seeds:
            data = related.get(seed, {})
            df = data.get("rising")
            if df is not None and not df.empty:
                rising.extend(df["query"].tolist()[:5])
        found = list(dict.fromkeys(kw for kw in rising if filter_fn(kw)))
        if found:
            return found
    except Exception as e:
        print(f"[GoogleTrends] related_queries fallback 실패: {e}")

    return []


def fetch_menu_scores() -> dict:
    """급상승 검색어 기반 메뉴 키워드 관심도 점수 반환"""
    try:
        keywords = _get_trending_keywords(is_menu_keyword)
        if not keywords:
            print("[GoogleTrends] 수집된 메뉴 키워드 없음")
            return {}
        print(f"[GoogleTrends] 메뉴 후보: {keywords}")
        return _fetch_interest(keywords)
    except Exception as e:
        print(f"[GoogleTrends] 메뉴 수집 실패: {e}")
        return {}


def fetch_brand_scores() -> dict:
    """급상승 검색어 기반 브랜드 키워드 관심도 점수 반환"""
    try:
        keywords = _get_trending_keywords(is_brand_keyword)
        if not keywords:
            print("[GoogleTrends] 수집된 브랜드 키워드 없음")
            return {}
        print(f"[GoogleTrends] 브랜드 후보: {keywords}")
        return _fetch_interest(keywords)
    except Exception as e:
        print(f"[GoogleTrends] 브랜드 수집 실패: {e}")
        return {}
