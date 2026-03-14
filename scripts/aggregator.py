"""
다중 채널 가중치 집계 — FRD-01 §5 통합 집계 공식 구현
"""
from typing import Optional

BASE_WEIGHTS = {
    "naver":  0.35,
    "google": 0.25,
    "youtube": 0.25,
    "x":      0.15,
}


def redistribute_weights(weights: dict, failed_sources: list) -> dict:
    """수집 실패 채널의 가중치를 나머지에 비율 재분배 — FRD-01 §2"""
    active = {k: v for k, v in weights.items() if k not in failed_sources}
    total = sum(active.values())
    if total == 0:
        return {}
    return {k: round(v / total, 4) for k, v in active.items()}


def normalize_scores(scores: dict) -> dict:
    """채널 내 점수를 0~100으로 정규화"""
    if not scores:
        return {}
    values = list(scores.values())
    min_val, max_val = min(values), max(values)
    if max_val == min_val:
        return {k: 100.0 for k in scores}
    return {
        k: round((v - min_val) / (max_val - min_val) * 100, 2)
        for k, v in scores.items()
    }


def calculate_trend_direction(current_rank: int, prev_rank: Optional[int]) -> str:
    """순위 변동 방향 계산 — FRD-01 §5"""
    if prev_rank is None:
        return "new"
    diff = prev_rank - current_rank  # 양수 = 상승
    if diff >= 3:
        return "up_up"
    if diff >= 1:
        return "up"
    if diff == 0:
        return "stay"
    return "down"


def aggregate(
    naver_scores: dict,
    google_scores: dict,
    youtube_scores: dict,
    x_scores: dict,
) -> list:
    """
    4개 채널 점수를 가중치 합산하여 TOP30 순위 반환
    반환: [{"keyword", "score", "source_scores", "source_count"}, ...]
    """
    # 실패 채널 파악
    failed = []
    if not naver_scores:   failed.append("naver")
    if not google_scores:  failed.append("google")
    if not youtube_scores: failed.append("youtube")
    if not x_scores:       failed.append("x")

    weights = redistribute_weights(BASE_WEIGHTS, failed)
    if not weights:
        print("[Aggregator] 모든 채널 수집 실패 — 집계 불가")
        return []

    # 채널별 정규화
    norm = {
        "naver":   normalize_scores(naver_scores),
        "google":  normalize_scores(google_scores),
        "youtube": normalize_scores(youtube_scores),
        "x":       normalize_scores(x_scores),
    }

    # 전체 키워드 유니온
    all_keywords = set()
    for scores in [naver_scores, google_scores, youtube_scores, x_scores]:
        all_keywords.update(scores.keys())

    results = []
    for keyword in all_keywords:
        weighted_sum = 0.0
        source_scores = {}
        source_count = 0

        for source, weight in weights.items():
            raw = {"naver": naver_scores, "google": google_scores,
                   "youtube": youtube_scores, "x": x_scores}[source]
            if keyword in raw:
                normalized = norm[source].get(keyword, 0)
                weighted_sum += normalized * weight
                source_scores[source] = round(raw[keyword], 1)
                source_count += 1

        results.append({
            "keyword": keyword,
            "score": round(weighted_sum, 2),
            "source_scores": source_scores,
            "source_count": source_count,
        })

    # 점수 내림차순 정렬 → TOP30
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:30]
