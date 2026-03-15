"""
다중 채널 가중치 집계 — FRD-01 §5 통합 집계 공식 구현
채널: naver(validator), google, blog, news, shopping, youtube, x
"""
from typing import Optional

BASE_WEIGHTS = {
    "naver":    0.20,  # 네이버 데이터랩 (상위 키워드 검색량 검증)
    "google":   0.20,  # Google Trends 급상승 검색어
    "blog":     0.15,  # 네이버 블로그 (맛집 포스트 언급량)
    "youtube":  0.15,  # YouTube 인기 영상 언급량
    "news":     0.10,  # 네이버 뉴스 (외식·식품 기사 언급량)
    "shopping": 0.10,  # 네이버 쇼핑 검색량
    "x":        0.10,  # X(Twitter) 언급량
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
    diff = prev_rank - current_rank
    if diff >= 3:
        return "up_up"
    if diff >= 1:
        return "up"
    if diff == 0:
        return "stay"
    return "down"


def aggregate(
    naver_scores:    dict = None,
    google_scores:   dict = None,
    blog_scores:     dict = None,
    youtube_scores:  dict = None,
    news_scores:     dict = None,
    shopping_scores: dict = None,
    x_scores:        dict = None,
) -> list:
    """
    7개 채널 점수를 가중치 합산하여 TOP30 순위 반환
    None이거나 빈 dict인 채널은 실패로 간주해 가중치 재분배
    반환: [{"keyword", "score", "source_scores", "source_count"}, ...]
    """
    channel_data = {
        "naver":    naver_scores    or {},
        "google":   google_scores   or {},
        "blog":     blog_scores     or {},
        "youtube":  youtube_scores  or {},
        "news":     news_scores     or {},
        "shopping": shopping_scores or {},
        "x":        x_scores        or {},
    }

    failed = [ch for ch, scores in channel_data.items() if not scores]
    if failed:
        print(f"[Aggregator] 실패 채널: {failed} → 가중치 재분배")

    weights = redistribute_weights(BASE_WEIGHTS, failed)
    if not weights:
        print("[Aggregator] 모든 채널 수집 실패 — 집계 불가")
        return []

    # 채널별 정규화
    norm = {ch: normalize_scores(scores) for ch, scores in channel_data.items()}

    # 전체 키워드 유니온
    all_keywords: set = set()
    for scores in channel_data.values():
        all_keywords.update(scores.keys())

    results = []
    for keyword in all_keywords:
        weighted_sum = 0.0
        source_scores = {}
        source_count = 0

        for ch, weight in weights.items():
            raw = channel_data[ch]
            if keyword in raw:
                normalized = norm[ch].get(keyword, 0)
                weighted_sum += normalized * weight
                source_scores[ch] = round(raw[keyword], 1)
                source_count += 1

        results.append({
            "keyword":       keyword,
            "score":         round(weighted_sum, 2),
            "source_scores": source_scores,
            "source_count":  source_count,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:30]
