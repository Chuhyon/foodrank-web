"""
푸드랭크 데이터 수집 메인 스크립트
GitHub Actions에서 2시간마다 실행

실행 방법:
  python collect_all.py          # 전체 수집
  python collect_all.py --price  # 물가만 수집
  python collect_all.py --trend  # 메뉴·브랜드만 수집
"""
import sys
import os

# 스크립트 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()  # 로컬 테스트 시 .env 파일 로드

from sources import naver, kamis, youtube, google_trends, x_api
from aggregator import aggregate
from supabase_writer import (
    save_keyword_trends,
    save_price_trends,
    get_prev_ranks,
)


def collect_trends():
    """메뉴·브랜드 트렌드 수집 및 저장"""
    print("=" * 50)
    print("[메뉴 트렌드] 수집 시작")

    # 각 채널에서 메뉴 점수 수집 (실패 시 빈 dict 반환)
    naver_menu   = naver.fetch_menu_scores()
    google_menu  = google_trends.fetch_menu_scores()
    youtube_menu = youtube.fetch_menu_scores()
    x_menu       = x_api.fetch_menu_scores()

    print(f"  Naver:  {len(naver_menu)}개 키워드")
    print(f"  Google: {len(google_menu)}개 키워드")
    print(f"  YouTube:{len(youtube_menu)}개 키워드")
    print(f"  X:      {len(x_menu)}개 키워드")

    menu_aggregated = aggregate(naver_menu, google_menu, youtube_menu, x_menu)
    if menu_aggregated:
        prev_menu = get_prev_ranks("menu")
        save_keyword_trends(menu_aggregated, prev_menu, "menu")
    else:
        print("[메뉴 트렌드] 집계 결과 없음 — 저장 건너뜀")

    print("\n[브랜드 트렌드] 수집 시작")

    naver_brand   = naver.fetch_brand_scores()
    google_brand  = google_trends.fetch_brand_scores()
    youtube_brand = youtube.fetch_brand_scores()
    x_brand       = x_api.fetch_brand_scores()

    print(f"  Naver:  {len(naver_brand)}개 키워드")
    print(f"  Google: {len(google_brand)}개 키워드")
    print(f"  YouTube:{len(youtube_brand)}개 키워드")
    print(f"  X:      {len(x_brand)}개 키워드")

    brand_aggregated = aggregate(naver_brand, google_brand, youtube_brand, x_brand)
    if brand_aggregated:
        prev_brand = get_prev_ranks("brand")
        save_keyword_trends(brand_aggregated, prev_brand, "brand")
    else:
        print("[브랜드 트렌드] 집계 결과 없음 — 저장 건너뜀")


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
        # 기본: 전체 수집
        collect_trends()
        collect_prices()

    print("\n✅ 수집 완료")
