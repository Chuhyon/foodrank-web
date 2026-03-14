"""
Google Trends (pytrends) — 음식·브랜드 검색량 급등 키워드 수집
비공식 라이브러리 — 차단 가능성 있음 (FRD-08 R1 참조)
필요 환경변수: 없음 (비공식 API, 인증 불필요)
"""
import time
from pytrends.request import TrendReq

MENU_KEYWORDS = [
    "마라탕", "버블티", "무한리필 고기", "한식뷔페", "로제떡볶이",
    "마라샹궈", "편의점 도시락", "스몰비어", "파스타", "초밥",
]

BRAND_KEYWORDS = [
    "빽다방", "맘스터치", "교촌치킨", "컴포즈커피", "노브랜드버거",
    "메가MGC커피", "청년다방", "투썸플레이스", "할리스", "고피자",
]

# pytrends는 한 번에 최대 5개 키워드 비교 가능
CHUNK_SIZE = 5


def _fetch_interest(keywords: list) -> dict:
    """pytrends로 키워드 관심도 수집 → {keyword: score} 반환"""
    pytrends = TrendReq(hl="ko-KR", tz=540, timeout=(10, 25))
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
            time.sleep(2)  # 차단 방지 딜레이
        except Exception as e:
            print(f"[GoogleTrends] chunk 수집 실패 {chunk}: {e}")
            continue

    return scores


def fetch_menu_scores() -> dict:
    """메뉴 트렌드 키워드 관심도 점수 반환"""
    try:
        return _fetch_interest(MENU_KEYWORDS)
    except Exception as e:
        print(f"[GoogleTrends] 메뉴 수집 실패: {e}")
        return {}


def fetch_brand_scores() -> dict:
    """브랜드 트렌드 키워드 관심도 점수 반환"""
    try:
        return _fetch_interest(BRAND_KEYWORDS)
    except Exception as e:
        print(f"[GoogleTrends] 브랜드 수집 실패: {e}")
        return {}
