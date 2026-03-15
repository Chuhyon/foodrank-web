"""
Google Trends (pytrends) — 한국 실시간 급상승 검색어에서 음식 키워드 동적 수집
비공식 라이브러리 — 차단 가능성 있음 (FRD-08 R1 참조)
필요 환경변수: 없음
"""
import time
from pytrends.request import TrendReq
from .food_filter import MENU_KEYWORDS, BRAND_KEYWORDS, extract_food_term

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


def _extract_unique_food_terms(phrases: list) -> list:
    """
    구절 목록에서 핵심 음식 키워드만 추출 (중복 제거)
    "마라탕 맛집 추천" → "마라탕" / "광양 맛집" → 제외 / "평양 냉면" → "냉면"
    반드시 MENU_KEYWORDS 또는 BRAND_KEYWORDS 사전에 있는 단어만 반환
    """
    seen = set()
    result = []
    for phrase in phrases:
        term = extract_food_term(phrase)  # MENU/BRAND 사전에 있는 단어만 추출
        if term and term not in seen:
            seen.add(term)
            result.append(term)
    return result


def _get_trending_keywords(seeds: list) -> list:
    """
    한국 급상승 검색어 → 핵심 음식/브랜드 키워드 반환
    seeds: 시드 키워드 (메뉴용 vs 브랜드용 구분)
    """
    pytrends = _build_pytrends()

    # 1차: 실시간 급상승 검색어 (realtime → daily 순)
    for method in ["realtime", "daily"]:
        try:
            if method == "realtime":
                df = pytrends.realtime_trending_searches(pn="KR")
                phrases = df["title"].tolist() if "title" in df.columns else []
            else:
                df = pytrends.trending_searches(pn="south_korea")
                phrases = df[0].tolist()

            found = _extract_unique_food_terms(phrases)
            if found:
                print(f"[GoogleTrends] {method} trending에서 {len(found)}개 발견")
                return found
            print(f"[GoogleTrends] {method} trending에서 해당 키워드 없음")
        except Exception as e:
            print(f"[GoogleTrends] {method} trending 실패: {e}")

    # 2차 fallback: 시드 키워드의 급상승 관련어에서 음식 키워드 추출
    try:
        pytrends.build_payload(seeds, cat=71, timeframe="now 7-d", geo="KR")
        related = pytrends.related_queries()
        rising_phrases = []
        for seed in seeds:
            data = related.get(seed, {})
            df = data.get("rising")
            if df is not None and not df.empty:
                rising_phrases.extend(df["query"].tolist()[:10])
        found = _extract_unique_food_terms(rising_phrases)
        if found:
            print(f"[GoogleTrends] related_queries fallback에서 {len(found)}개 발견: {found}")
            return found
    except Exception as e:
        print(f"[GoogleTrends] related_queries fallback 실패: {e}")

    return []


def fetch_menu_scores() -> dict:
    """급상승 검색어 기반 메뉴 키워드 관심도 점수 반환"""
    try:
        keywords = _get_trending_keywords(MENU_SEED_KEYWORDS)
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
        keywords = _get_trending_keywords(BRAND_SEED_KEYWORDS)
        if not keywords:
            print("[GoogleTrends] 수집된 브랜드 키워드 없음")
            return {}
        print(f"[GoogleTrends] 브랜드 후보: {keywords}")
        return _fetch_interest(keywords)
    except Exception as e:
        print(f"[GoogleTrends] 브랜드 수집 실패: {e}")
        return {}
