# 푸드랭크 개발 진행 현황

최종 업데이트: 2026-03-15 (v2 — 동적 수집 파이프라인 + 채널 확장)

---

## 서비스 개요

- **서비스명**: 푸드랭크 (FoodRank)
- **컨셉**: 외식업 전문 트렌드 대시보드 — "네이버 실검 대체"
- **라이브 URL**: https://web-alpha-eight-41.vercel.app
- **GitHub**: https://github.com/Chuhyon/foodrank-web

---

## 완료된 작업

### 1단계 — 문서 정비 (완료)

| 파일 | 내용 | 상태 |
|------|------|------|
| PRD_Main_v2.3.md | 제품 요구사항 전체 | 완료 |
| FRD-01_DataPipeline.md | 데이터 수집·집계·저장 파이프라인 | 완료 |
| FRD-02_Analytics.md | GTM/GA4/Clarity 이벤트 스키마 | 완료 (신규 작성) |
| FRD-03_Onboarding.md | 4단계 온보딩, localStorage 플래그 | 완료 (신규 작성) |
| FRD-04_SearchConnect.md | 키워드 클릭 → 구글 검색 연결 | 완료 |
| FRD-05_DashboardUI.md | 대시보드 UI 컴포넌트 스펙 | 완료 |
| FRD-06_Infrastructure.md | 인프라·보안·SEO·비용·스프린트 | 완료 (신규 작성) |
| FRD-07_Monetization.md | 수익화 모델 | 완료 |
| FRD-08_RiskResponse.md | R1~R8 리스크 대응 | 완료 (신규 작성) |
| REVIEW_SUMMARY.md | 검토 이슈 수정 기록 | 완료 |

---

### 2단계 — 웹 앱 구축 및 배포 (완료)

#### Next.js 웹 앱
- Pages Router + ISR (revalidate: 600초)
- 탭 구성: 메뉴 트렌드 / 브랜드 트렌드 / 물가 주의보
- 키워드 클릭 → 구글 검색 팝업
- SourceIndicator: 채널 신뢰도 5점 표시 (●●●○○)
- "데이터 수집 중" 빈 상태 처리

#### Vercel 배포
- GitHub 연동 → main 브랜드 push 시 자동 배포
- 라이브: https://web-alpha-eight-41.vercel.app

#### Supabase 연결
- DB 스키마 생성 (`doc/supabase_schema.sql`)
- 테이블: `keyword_trends`, `price_trends`, `brand_db`, `keyword_click_log`, `search_templates`
- RLS: public SELECT 허용
- Anon Key로 프론트엔드 읽기 / Service Role Key로 Python 쓰기

---

### 3단계 — 데이터 수집 파이프라인 (완료)

#### Python 수집 스크립트 (`scripts/`)
| 파일 | 역할 |
|------|------|
| `collect_all.py` | 메인 실행 (전체 수집 또는 --price / --trend) |
| `sources/naver.py` | 네이버 데이터랩 API → 메뉴·브랜드 검색 지수 |
| `sources/google_trends.py` | pytrends → 키워드 관심도 |
| `sources/youtube.py` | YouTube Search API → 제목 기반 멘션 수 |
| `sources/x_api.py` | X(Twitter) Bearer Token → 트윗 멘션 수 |
| `sources/kamis.py` | KAMIS 농산물 물가 TOP10 |
| `aggregator.py` | 다채널 점수 → 가중 합산 → 순위·source_count 계산 |
| `supabase_writer.py` | Supabase upsert (keyword_trends, price_trends) |

#### GitHub Actions 워크플로우
- `collect_data.yml`: 2시간 주기 cron (`0 */2 * * *`) + 수동 실행
- `run_migration.yml`: DB 스키마 마이그레이션 (1회성, 수동)

#### 등록된 GitHub Secrets
`NEXT_PUBLIC_SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`, `YOUTUBE_API_KEY`, `SUPABASE_DB_PASSWORD`

---

### 4단계 — 버그 수정 (완료)

#### 키워드 클릭 시 구글 검색어 "null" 표시 버그 (ERR-007)
- **원인**: `supabase_writer.py`가 `keyword_trends` 저장 시 `search_template` 누락 + `searchConnect.js`에서 null 처리 없음
- **수정**: `searchConnect.js`에 `searchTemplate || keyword` fallback 추가, `supabase_writer.py`에 기본 템플릿 생성 추가

#### 채널 신뢰도(source_count) 항상 1 표시 버그 (ERR-006)
- **원인**: `naver.py`의 `groupName`이 카테고리명("마라탕류")을 사용해 다른 채널("마라탕")과 키 불일치
- **수정**: `groupName`을 Google Trends/YouTube와 동일한 대표 키워드명으로 변경

  | 수정 전 | 수정 후 |
  |---------|---------|
  | `"마라탕류"` | `"마라탕"` |
  | `"버블티류"` | `"버블티"` |
  | `"고기류"` | `"무한리필 고기"` |
  | `"뷔페류"` | `"한식뷔페"` |
  | `"분식류"` | `"로제떡볶이"` |
  | `"커피"` (다중 브랜드) | `"빽다방"` 등 개별 브랜드 |

- **결과**: 같은 키워드가 2개 이상 채널에서 수집되면 source_count 증가

---

---

### 5단계 — 동적 수집 파이프라인 + 채널 확장 (완료, 2026-03-15)

#### 구조 변경: 고정 키워드 → 동적 키워드 발견

| 구분 | 변경 전 | 변경 후 |
|------|---------|---------|
| 키워드 발견 방식 | 소스별 고정 키워드 목록 | 각 채널이 실시간 트렌드에서 동적으로 키워드 발굴 |
| 네이버 역할 | 고정 5개 그룹 검색량 조회 | 다른 채널 TOP10 키워드 검색량 검증(validator) |
| Google Trends | 고정 10개 키워드 점수 조회 | `trending_searches('south_korea')` → 음식 필터링 |
| 채널 수 | 4개 | 7개 (+블로그, +뉴스, +쇼핑) |

#### 2단계 수집 파이프라인

```
Phase 1 (동적 발견):
  Google Trends → 급상승 검색어 음식 필터링 → 관심도 점수
  YouTube      → 인기 음식 영상 제목 → 키워드 추출 → 빈도 점수
  X(Twitter)   → 음식 쿼리 트윗 → 키워드 추출 → 언급량 점수
  네이버 블로그 → 맛집 포스트 제목 → 키워드 추출 → 빈도 점수  ← NEW
  네이버 뉴스  → 외식 기사 제목/요약 → 키워드 추출 → 빈도 점수  ← NEW
  네이버 쇼핑  → 식품 키워드 쇼핑 검색량 → 점수화  ← NEW

Phase 2 (네이버 검증):
  Phase 1 집계 TOP 10 키워드 → 네이버 DataLab → 검색량 점수

Phase 3 (최종 집계):
  7채널 가중 합산 → TOP30 → DB 저장
```

#### 채널별 가중치 (7채널 합계 1.0)

| 채널 | 가중치 | 역할 |
|------|--------|------|
| 네이버 DataLab | 0.20 | 상위 키워드 검색량 검증 |
| Google Trends | 0.20 | 급상승 검색어 발견 |
| 네이버 블로그 | 0.15 | 맛집 포스트 언급량 |
| YouTube | 0.15 | 음식 영상 언급량 |
| 네이버 뉴스 | 0.10 | 외식 기사 언급량 |
| 네이버 쇼핑 | 0.10 | 식품 쇼핑 검색량 |
| X(Twitter) | 0.10 | SNS 언급량 |

#### 신규·수정 파일

| 파일 | 변경 |
|------|------|
| `sources/food_filter.py` | 신규 — 공통 음식 키워드 필터·추출 유틸리티 |
| `sources/google_trends.py` | 수정 — 동적 trending_searches + related_queries fallback |
| `sources/naver.py` | 수정 — validator 역할로 전환 |
| `sources/naver_blog.py` | 신규 — 네이버 블로그 검색 API |
| `sources/naver_news.py` | 신규 — 네이버 뉴스 검색 API |
| `sources/naver_shopping.py` | 신규 — 네이버 쇼핑 검색 API |
| `sources/youtube.py` | 수정 — food_filter 공통 키워드 사용 |
| `sources/x_api.py` | 수정 — food_filter 공통 키워드 사용 |
| `aggregator.py` | 수정 — 7채널 지원, keyword argument 방식 |
| `collect_all.py` | 수정 — 2단계 파이프라인 |

---

## 진행 중 / 남은 작업

| 항목 | 상태 | 비고 |
|------|------|------|
| KAMIS API 키 | 신청 중 | 승인 후 GitHub Secrets 등록 필요 |
| X(Twitter) API | 미등록 | X_BEARER_TOKEN 발급 필요 |
| Google Trends 안정성 | 모니터링 | pytrends 비공식 API — 차단 가능성 있음 (FRD-08 R1) |
| 애널리틱스 (GTM/GA4) | 미구현 | FRD-02 참조 |
| 온보딩 UI | 미구현 | FRD-03 참조 |
| 수익화 (리드 폼) | 미구현 | FRD-07 참조 |

---

## 아키텍처 메모

- ISR 10분 / 데이터 갱신 2시간 → UI는 `collected_at` 기준 "n시간 전 수집" 표시
- `window.open()` 반드시 `fetch()` 전에 호출 (팝업 차단 방지)
- `search_templates` 테이블: FRD-01/FRD-04 공통 단일 진실
- SourceIndicator MAX=5 (채널 4개지만 5칸으로 여백 표시)
- aggregator 가중치: 네이버 0.4 / Google 0.3 / YouTube 0.2 / X 0.1
