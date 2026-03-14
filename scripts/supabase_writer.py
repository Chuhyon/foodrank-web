"""
Supabase 저장 모듈 — 집계 결과를 DB에 UPSERT
"""
import os
import requests
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL", "")
SERVICE_KEY  = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}


def _rest(method: str, table: str, data) -> None:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.request(method, url, headers=HEADERS, json=data, timeout=15)
    if not resp.ok:
        print(f"[Supabase] {table} 저장 실패 {resp.status_code}: {resp.text[:200]}")
        resp.raise_for_status()


def save_keyword_trends(aggregated: list, prev_ranks: dict, tab: str) -> None:
    """
    keyword_trends 테이블 UPSERT
    aggregated: aggregator.aggregate() 반환값
    prev_ranks: {keyword: prev_rank} 이전 순위 맵
    tab: 'menu' | 'brand'
    """
    from aggregator import calculate_trend_direction

    collected_at = datetime.now(timezone.utc).isoformat()
    rows = []

    for rank, item in enumerate(aggregated[:10], start=1):
        keyword = item["keyword"]
        prev_rank = prev_ranks.get(keyword)

        rows.append({
            "keyword":         keyword,
            "tab":             tab,
            "rank":            rank,
            "score":           item["score"],
            "prev_rank":       prev_rank,
            "trend_direction": calculate_trend_direction(rank, prev_rank),
            "source_scores":   item["source_scores"],
            "source_count":    item["source_count"],
            "collected_at":    collected_at,
        })

    if rows:
        # 기존 데이터 삭제 후 재삽입 (간단한 UPSERT 대안)
        del_url = f"{SUPABASE_URL}/rest/v1/keyword_trends?tab=eq.{tab}"
        requests.delete(del_url, headers=HEADERS, timeout=10)
        _rest("POST", "keyword_trends", rows)
        print(f"[Supabase] keyword_trends ({tab}) {len(rows)}개 저장 완료")


def save_price_trends(price_top10: list) -> None:
    """price_trends 테이블 갱신"""
    from sources.kamis import fetch_price_top10

    collected_at = datetime.now(timezone.utc).isoformat()

    rows = []
    for rank, item in enumerate(price_top10, start=1):
        abs_rate = abs(item["change_rate"])
        direction = item["direction"]
        if direction == "up" and abs_rate >= 20:
            template = f"{item['item_name']} 가격 급등 이유 오늘"
        elif direction == "up":
            template = f"{item['item_name']} 가격 오늘 전망"
        elif direction == "down" and abs_rate >= 20:
            template = f"{item['item_name']} 가격 급락 이유"
        else:
            template = f"{item['item_name']} 도매가 시세 오늘"

        rows.append({
            "item_name":       item["item_name"],
            "rank":            rank,
            "today_price":     item["today_price"],
            "yesterday_price": item["yesterday_price"],
            "change_rate":     item["change_rate"],
            "direction":       item["direction"],
            "search_template": template,
            "collected_at":    collected_at,
        })

    if rows:
        requests.delete(f"{SUPABASE_URL}/rest/v1/price_trends", headers=HEADERS, timeout=10)
        _rest("POST", "price_trends", rows)
        print(f"[Supabase] price_trends {len(rows)}개 저장 완료")


def get_prev_ranks(tab: str) -> dict:
    """현재 DB에서 이전 순위 맵 {keyword: rank} 조회"""
    url = f"{SUPABASE_URL}/rest/v1/keyword_trends?tab=eq.{tab}&select=keyword,rank"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if not resp.ok:
        return {}
    return {row["keyword"]: row["rank"] for row in resp.json()}
