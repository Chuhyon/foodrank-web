# FRD-01 | 데이터 파이프라인
> **Feature Requirements Document**
> 푸드랭크 — 데이터 수집·집계·저장 상세 명세
> 2025년 3월 | v1.1

---

## 1. 문서 목적
이 문서는 푸드랭크의 핵심 엔진인 **데이터 수집→집계→저장→제공 파이프라인**의
상세 구현 명세를 정의합니다.

---

## 2. 메뉴 트렌드 탭 (F1-A)

### 정의
다중 채널의 음식·외식 관련 검색어 데이터를 채널별 가중치로 통합 집계한 인기 음식 키워드 TOP10.

### 채널 구성

| 채널 | 가중치 | 수집 방법 | 주기 |
|------|--------|-----------|------|
| 네이버 데이터랩 | 0.35 | 공식 API — 음식/외식 카테고리 급상승 검색어 | 2시간 |
| 구글 트렌드 | 0.25 | pytrends — 음식 카테고리 키워드 급등 | 2시간 |
| YouTube Data API v3 | 0.25 | 음식·요리 관련 급상승 동영상 키워드 | 일간 |
| X API v2 | 0.15 | 음식·외식 관련 급증 언급 키워드 | 일간 |

### 수집 실패 시 Fallback 처리

```python
# 채널 수집 실패 시 해당 채널 가중치를 나머지에 비율 재분배
def redistribute_weights(weights: dict, failed_sources: list) -> dict:
    active = {k: v for k, v in weights.items() if k not in failed_sources}
    total = sum(active.values())
    return {k: round(v / total, 4) for k, v in active.items()}

# 예시: 구글 트렌드 실패 시
weights = {'naver': 0.35, 'google': 0.25, 'youtube': 0.25, 'x': 0.15}
failed = ['google']
# → {'naver': 0.467, 'youtube': 0.333, 'x': 0.200}
```

---

## 3. 급상승 브랜드 탭 (F1-B)

### 정의
다중 채널에서 외식 브랜드명 검색량·언급량이 급상승한 브랜드 TOP10.
(기준: "검색량 급상승" — "가맹점 증가"와 혼동 방지를 위해 UI에 명시)

### 채널 구성

| 채널 | 가중치 | 수집 방법 | 주기 |
|------|--------|-----------|------|
| 네이버 데이터랩 | 0.35 | 브랜드 카테고리 검색량 급등 | 2시간 |
| 구글 트렌드 | 0.25 | 외식 브랜드 키워드 급등 | 2시간 |
| YouTube Data API v3 | 0.25 | 외식 브랜드 관련 영상 급상승 | 일간 |
| X API v2 | 0.15 | 외식 브랜드 언급량 급증 | 일간 |

### 보조 지표 (순위 산정에 미포함, 상세 화면 표시용)

| 채널 | 활용 방법 | 주기 |
|------|-----------|------|
| 공정위 가맹사업거래 오픈API | 브랜드 가맹점 수 표시 (참고용) | 주간 |
| 마이프차 (Playwright) | 신규 가맹점 오픈 동향 (참고용) | 주간 |

> ⚠️ 마이프차 수집은 이용약관 회색지대. 정기적으로 ToS 확인 필요.

---

## 4. 물가 주의보 탭 (F1-C)

### 정의
KAMIS(농수산식품유통공사) 공공 오픈API에서 수집한
**전일 대비 도매가 변동률이 큰 식자재 TOP10**.

> 📌 물가 탭은 검색량 기반 집계 방식 미적용.
> 가격 데이터는 KAMIS 공공 API 단독 사용. 신뢰도·정확성 최우선.

### 수집 및 집계

```python
# KAMIS API 수집 → 변동률 계산 → TOP10 추출
def get_price_top10(kamis_data: list) -> list:
    items = []
    for item in kamis_data:
        change_rate = (item['today'] - item['yesterday']) / item['yesterday'] * 100
        items.append({
            'name': item['itemName'],
            'today_price': item['today'],
            'yesterday_price': item['yesterday'],
            'change_rate': round(change_rate, 1),  # 소수 1자리
            'direction': 'up' if change_rate > 0 else 'down'
        })
    # 절댓값 기준 정렬 (상승·하락 모두 포함)
    return sorted(items, key=lambda x: abs(x['change_rate']), reverse=True)[:10]
```

---

## 5. 통합 집계 공식

### 기본 공식

```
최종 점수 = Σ (채널별 정규화 점수 × 가중치)

정규화: 각 채널의 원시 지수값을 0~100으로 변환
  normalized = (raw_score - min) / (max - min) * 100
```

### 계산 예시 (마라탕)

```
  네이버 데이터랩  : 정규화 87 × 0.35 = 30.45
  구글 트렌드      : 정규화 72 × 0.25 = 18.00
  YouTube          : 정규화 91 × 0.25 = 22.75
  X (트위터)       : 정규화 40 × 0.15 =  6.00
  ───────────────────────────────────────────
  최종 점수: 77.20 → 순위 산출
```

### 순위 변동 방향 정의

| 기호 | 의미 | 조건 |
|------|------|------|
| ↑↑ | 급상승 | 이전 대비 3순위 이상 상승 |
| ↑  | 상승  | 이전 대비 1~2순위 상승 |
| →  | 유지  | 순위 동일 |
| ↓  | 하락  | 이전 대비 1순위 이상 하락 |
| 🆕 | 신규 진입 | 이전 TOP10 외 진입 |

---

## 6. 전체 파이프라인 흐름

```
[수집 레이어 — GitHub Actions, 2시간 주기]
  네이버 데이터랩 API  →  키워드 + 검색량 지수
  구글 트렌드 (pytrends) →  키워드 + 검색량 지수
  YouTube Data API v3  →  키워드 + 조회수
  X API v2             →  키워드 + 언급량
  KAMIS API            →  식자재 도매가 (물가 탭 전용)
  공정위 API (주간)    →  브랜드 가맹점 수 (보조)
  마이프차 (주간)      →  신규 가맹점 동향 (보조)
        ↓
[집계 레이어 — Python]
  채널별 수집 성공 여부 확인 → 실패 채널 가중치 자동 재분배
  채널별 점수 정규화 (0~100)
  가중치 적용 및 합산 → 탭별 TOP30 산출
  이전 순위 비교 → 변동 방향 계산
  물가 탭: KAMIS 단독 변동률 계산 → TOP10
        ↓
[저장 레이어 — Supabase]
  keyword_trends 테이블 UPSERT
  brand_db 신규 브랜드 자동 INSERT
  price_trends 테이블 UPDATE (물가)
  수집 완료 시각 기록 (UI 표시용)
        ↓
[서비스 레이어 — Next.js + Vercel]
  Supabase REST API 호출
  Next.js ISR 캐싱 (10분) — UI 렌더링 최적화
  "데이터 기준: YYYY.MM.DD HH:00 수집" 표시
```

> 📌 ISR 10분 vs 데이터 2시간 관계
> ISR은 UI 서버 렌더링 캐시 시간. 데이터는 2시간마다 실제 갱신.
> 사용자에게는 Supabase에 기록된 **데이터 수집 완료 시각**만 노출.
> ISR 캐시 내 "마지막 업데이트" 시각 표시는 DB의 `collected_at` 필드 값 사용.

---

## 7. Supabase DB 스키마

```sql
-- 메뉴·브랜드 트렌드 키워드
CREATE TABLE keyword_trends (
  id              SERIAL PRIMARY KEY,
  keyword         TEXT NOT NULL,
  tab             TEXT NOT NULL          CHECK (tab IN ('menu', 'brand')),
  rank            INT NOT NULL,           -- 1~10
  score           FLOAT NOT NULL,         -- 가중치 합산 점수
  prev_rank       INT,                    -- 직전 순위
  trend_direction TEXT                   CHECK (trend_direction IN ('up_up', 'up', 'stay', 'down', 'new')),
  source_scores   JSONB,                  -- {"naver":87, "google":72, ...}
  source_count    INT,                    -- 데이터 있는 채널 수
  search_template TEXT,                   -- 구글 검색 연결 템플릿
  collected_at    TIMESTAMPTZ NOT NULL,   -- 데이터 수집 완료 시각 (UI 표시용)
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 물가 트렌드 (KAMIS 단독)
CREATE TABLE price_trends (
  id              SERIAL PRIMARY KEY,
  item_name       TEXT NOT NULL,          -- 식자재명
  rank            INT NOT NULL,
  today_price     INT NOT NULL,           -- 오늘 도매가 (원/kg)
  yesterday_price INT NOT NULL,           -- 전일 도매가
  change_rate     FLOAT NOT NULL,         -- 변동률 (%)
  direction       TEXT NOT NULL          CHECK (direction IN ('up', 'down')),
  search_template TEXT,
  collected_at    TIMESTAMPTZ NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 브랜드 DB (수익화 핵심 자산 — 자동 축적)
CREATE TABLE brand_db (
  id              SERIAL PRIMARY KEY,
  brand_name      TEXT NOT NULL UNIQUE,
  category        TEXT,                   -- 치킨|카페|한식 등
  peak_rank       INT,                    -- 역대 최고 순위
  franchise_count INT,                    -- 공정위 가맹점 수
  first_appeared  TIMESTAMPTZ,            -- 최초 TOP10 진입일
  contact_info    TEXT,                   -- 공개 연락처 (브랜드 공식)
  is_ad_verified  BOOLEAN DEFAULT FALSE,  -- 광고 제안용 연락처 검증 여부
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 클릭 이벤트 서버사이드 로그 (GA4 보완, 익명 처리)
CREATE TABLE keyword_click_log (
  id              SERIAL PRIMARY KEY,
  keyword         TEXT NOT NULL,
  tab             TEXT NOT NULL,
  rank            INT,
  session_hash    TEXT,                   -- SHA-256 해시 (일별 salt, 개인식별 불가)
  clicked_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 검색어 템플릿 관리 (운영자 관리 테이블)
-- ⚠️ FRD-04와 동일 스키마 — 두 문서 모두 이 정의를 기준으로 구현
CREATE TABLE search_templates (
  id              SERIAL PRIMARY KEY,
  keyword         TEXT NOT NULL,
  tab             TEXT NOT NULL          CHECK (tab IN ('menu', 'brand', 'price')),
  template        TEXT NOT NULL,          -- 구글 검색 연결 쿼리
  is_active       BOOLEAN DEFAULT TRUE,
  is_verified     BOOLEAN DEFAULT FALSE,  -- 운영자 AI Overview 확인 여부
  ctr_rate        FLOAT,                  -- GA4에서 집계한 CTR (%)
  last_verified   DATE,                   -- 운영자 검증일
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (keyword, tab)
);
```

---

## 8. 검색어 품질 관리 프로세스

### 1차: 자동 추출 (2시간)
```
다중 채널 집계 → TOP30 후보 → Supabase keyword_trends 저장
→ search_templates 미등록 키워드 → 자동 기본 템플릿 생성
   기본 템플릿: "{keyword} 인기 이유 2025"
   is_verified = FALSE (운영자 검증 대기)
```

### 2차: 운영자 검증 (주 1회, 약 30분)
```
1. search_templates 미검증(is_verified = FALSE) 또는 14일 이상 미갱신 항목 조회
2. 운영자 구글 직접 검색 → AI Overview 출현 여부 확인
3. 템플릿 수정 또는 확정 → is_verified = TRUE, last_verified 업데이트
```

### 3차: CTR 기반 자동 최적화 (월 1회)
```
GA4 keyword_click 이벤트 → search_template별 CTR 계산
→ search_templates.ctr_rate 업데이트
→ CTR 하위 20% → is_active = FALSE (자동 탈락)
→ CTR 상위 패턴 분석 → 신규 키워드 기본 템플릿 개선
```

---

*FRD-01 DataPipeline | v1.1 | 2025.03*
*상위 문서: PRD_Main_v2.3*
*변경: search_templates 스키마에 is_verified, updated_at, UNIQUE(keyword, tab) 추가 (FRD-04 통일). CHECK 제약 추가. is_ad_verified 주석 명확화.*
