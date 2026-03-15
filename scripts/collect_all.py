"""
푸드랭크 데이터 수집 메인 스크립트
GitHub Actions에서 2시간마다 실행

수집 파이프라인 (2단계):
  Phase 1: Google Trends·YouTube·X·네이버블로그·뉴스·쇼핑에서 동적 키워드 수집
  Phase 2: Phase 1 상위 키워드를 네이버 데이터랩으로 검색량 검증 후 최종 집계

실행 방법:
  python collect_all.py          # 전체 수집
  python collect_all.py --price  # 물가만 수집
  python collect_all.py --trend  # 메뉴·브랜드만 수집
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from sources import naver, naver_blog, naver_news, naver_shopping, youtube, google_trends, x_api
from sources import kamis
from aggregator import aggregate
from supabase_writer import save_keyword_trends, save_price_trends, get_prev_ranks

TOP_N_FOR_NAVER = 10  # 네이버 DataLab 검증에 넘길 상위 키워드 수


def _collect_channel_scores(fetch_fn_map: dict) -> dict:
    """각 채널의 fetch 함수 실행, 실패 시 빈 dict 반환"""
    results = {}
    for name, fn in fetch_fn_map.items():
        try:
            results[name] = fn()
        except Exception as e:
            print(f"[{name}] 수집 예외: {e}")
            results[name] = {}
    return results


def _pre_aggregate_top(scores_map: dict, n: int) -> list:
    """네이버 제외 1차 집계로 상위 키워드 추출"""
    pre = aggregate(
        google_scores   = scores_map.get("google"),
        blog_scores     = scores_map.get("blog"),
        youtube_scores  = scores_map.get("youtube"),
        news_scores     = scores_map.get("news"),
        shopping_scores = scores_map.get("shopping"),
        x_scores        = scores_map.get("x"),
    )
    return [item["keyword"] for item in pre[:n]]


def collect_trends():
    """메뉴·브랜드 트렌드 수집 및 저장"""

    for tab, fetch_map, naver_fn in [
        (
            "menu",
            {
                "google":   google_trends.fetch_menu_scores,
                "blog":     naver_blog.fetch_menu_scores,
                "news":     naver_news.fetch_menu_scores,
                "shopping": naver_shopping.fetch_menu_scores,
                "youtube":  youtube.fetch_menu_scores,
                "x":        x_api.fetch_menu_scores,
            },
            naver.fetch_menu_scores,
        ),
        (
            "brand",
            {
                "google":   google_trends.fetch_brand_scores,
                "blog":     naver_blog.fetch_brand_scores,
                "news":     naver_news.fetch_brand_scores,
                "shopping": naver_shopping.fetch_brand_scores,
                "youtube":  youtube.fetch_brand_scores,
                "x":        x_api.fetch_brand_scores,
            },
            naver.fetch_brand_scores,
        ),
    ]:
        label = "메뉴" if tab == "menu" else "브랜드"
        print("=" * 50)
        print(f"[{label} 트렌드] Phase 1 수집 시작")

        # Phase 1: 동적 채널 수집
        scores = _collect_channel_scores(fetch_map)
        for name, data in scores.items():
            print(f"  {name}: {len(data)}개 키워드")

        # Phase 2: 상위 후보 추출 → 네이버 DataLab 검증
        top_candidates = _pre_aggregate_top(scores, TOP_N_FOR_NAVER)
        print(f"\n[{label} 트렌드] Phase 2 네이버 검증 대상: {top_candidates}")

        naver_scores = naver_fn(top_candidates) if top_candidates else {}
        print(f"  Naver DataLab: {len(naver_scores)}개 검증 완료")

        # Phase 3: 최종 집계 (7채널)
        aggregated = aggregate(
            naver_scores    = naver_scores,
            google_scores   = scores.get("google"),
            blog_scores     = scores.get("blog"),
            youtube_scores  = scores.get("youtube"),
            news_scores     = scores.get("news"),
            shopping_scores = scores.get("shopping"),
            x_scores        = scores.get("x"),
        )

        if aggregated:
            prev = get_prev_ranks(tab)
            save_keyword_trends(aggregated, prev, tab)
        else:
            print(f"[{label} 트렌드] 집계 결과 없음 — 저장 건너뜀")


def collect_prices():
    """물가 데이터 수집 및 저장"""
    print("=" * 50)
    print("[물가 주의보] 수집 시작")

    price_top10 = kamis.fetch_price_top10()
    print(f"  KAMIS: {len(price_top10)}개 식자재")

    if price_top10:
        save_price_trends(price_top10)
    else:
        print("[물가 주의보] 수집 결과 없음 — 저장 건너뜀")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--price" in args:
        collect_prices()
    elif "--trend" in args:
        collect_trends()
    else:
        collect_trends()
        collect_prices()

    print("\n✅ 수집 완료")
