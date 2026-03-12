# FRD-08 | 리스크 대응
> Feature Requirements Document
> 푸드랭크 — 리스크 항목별 상세 대응 방안
> 2025.03 | v1.0

---

## 1. 문서 목적
이 문서는 PRD §10 리스크 레지스터에 등록된 각 리스크의
구체적인 감지 방법, 즉시 대응 절차, 장기 대응 방안을 정의합니다.

---

## 2. 리스크 레지스터 요약

| ID | 리스크 | 확률 | 영향 |
|----|--------|------|------|
| R1 | pytrends 구글 차단 | 중 | 중 |
| R2 | X API 유료화·제한 | 중 | 낮음 |
| R3 | Supabase 대역폭 초과 | 중 | 중 |
| R4 | 쿠키 거부 → GA4 데이터 손실 | 중 | 중 |
| R5 | GitHub Actions 분 초과 | 낮음 | 낮음 |
| R6 | MAU 5,000 미달성 | 중 | 중 |
| R7 | 구글 AI Overview 미출현 | 중 | 낮음 |
| R8 | PIPA 위반 이슈 | 낮음 | 높음 |

---

## 3. R1 — pytrends 구글 차단

**리스크 설명:** 구글은 pytrends(비공식 라이브러리)의 과도한 요청을 감지하면 IP 차단 또는 429 응답.
Google Trends 공식 API가 없으므로 완전한 해결책이 없음.

### 감지 방법

```python
# 수집 스크립트 내 pytrends 응답 확인
try:
    pytrends_data = fetch_google_trends(keywords)
except Exception as e:
    # 429 또는 연결 오류 → 알림 + fallback 처리
    notify_slack(f"pytrends 수집 실패: {e}")
    pytrends_data = None
```

### 즉시 대응

```python
# FRD-01 §2 redistribute_weights 함수 자동 호출
# 구글 트렌드 실패 시 가중치 재분배
weights = {'naver': 0.35, 'google': 0.25, 'youtube': 0.25, 'x': 0.15}
active_weights = redistribute_weights(weights, failed_sources=['google'])
# → {'naver': 0.467, 'youtube': 0.333, 'x': 0.200}

# keyword_trends 저장 시 source_scores에 구글 제외 기록
# source_count 자동 감소 → UI SourceIndicator 반영
```

### 장기 대응

```
1순위: 요청 간격 조정 (현재 2시간 → 실패 시 4시간으로 자동 전환)
2순위: GitHub Actions IP 순환 (self-hosted runner 또는 프록시)
3순위: Google Trends 대체 데이터 소스 검토
       - SerpAPI Google Trends 엔드포인트 (유료, $50/월~)
       - 대체 도입 시 PRD 데이터 채널 가중치 재설계 필요
```

---

## 4. R2 — X API 유료화·제한

**리스크 설명:** X(구 Twitter) API v2는 이미 무료 플랜이 크게 제한됨.
추가 유료화 또는 정책 변경 시 수집 불가.

### 감지 방법

```
- GitHub Actions 로그에서 X API 401/403/429 응답 감지
- 월 1회 X API 개발자 대시보드 정책 공지 확인
- X 개발자 공지 Twitter 계정(@XDevelopers) 모니터링
```

### 즉시 대응

```python
# R1과 동일한 가중치 재분배 패턴
weights = {'naver': 0.35, 'google': 0.25, 'youtube': 0.25, 'x': 0.15}
active_weights = redistribute_weights(weights, failed_sources=['x'])
# → {'naver': 0.412, 'google': 0.294, 'youtube': 0.294}
```

### 장기 대응

```
X API 가중치 0.15는 의도적으로 낮게 설정됨 → 제거해도 서비스 영향 최소
완전 제거 시:
  - 데이터 채널 3개로 운영 (네이버·구글·유튜브)
  - PRD §3 채널 구성 업데이트
  - source_count MAX 3으로 변경 → SourceIndicator 표시 기준 재검토
```

---

## 5. R3 — Supabase 대역폭 초과

**리스크 설명:** Supabase Free 플랜 대역폭 2GB/월.
MAU 증가 시 REST API 호출량 증가로 초과 가능.

### 감지 방법

```
- Supabase 대시보드 → Settings → Usage 월 1회 확인
- 대역폭 80% 도달 시 Pro 플랜 전환 준비
- GitHub Actions 수집 완료 후 Supabase 사용량 로그 기록
```

### 예방: API 호출 최소화

```javascript
// Next.js ISR 활용 — Supabase 직접 호출 최소화
// revalidate: 600 (10분) → 10분간 동일 응답 캐시

// 필요 컬럼만 SELECT (전체 컬럼 조회 금지)
const { data } = await supabase
  .from('keyword_trends')
  .select('keyword, rank, trend_direction, source_count, search_template, collected_at')
  .eq('tab', tab)
  .order('rank')
  .limit(10);
```

### 즉시 대응 (초과 임박 시)

```
1단계: ISR revalidate 600 → 1800으로 증가 (30분 캐시)
2단계: Supabase Pro 플랜 전환 ($25/월, 대역폭 250GB)
       → MAU 10,000 도달 예상 시점 기준으로 전환 계획

장기: CDN 캐싱 레이어 추가 (Vercel Edge Cache + Supabase 대역폭 절감)
```

---

## 6. R4 — 쿠키 거부 → GA4 데이터 손실

**리스크 설명:** PIPA 준수로 쿠키 동의를 받아야 하나,
거부 사용자의 행동 데이터가 GA4에 수집되지 않아 분석 편향 발생.

### 대응: 이중 수집 체계

```
GA4 (쿠키 동의 사용자)
  + Supabase keyword_click_log (모든 사용자, 익명 해시)

→ 두 데이터를 비교해 동의율 및 수집 편향 추정 가능
```

### 쿠키 거부율 모니터링

```
GA4 → cookie_consent 이벤트 분석
  consent_type = 'all' 건수 / 전체 신규 방문자 = 동의율

목표 동의율: 60% 이상
동의율 50% 미만 시:
  → 쿠키 배너 문구 개선 (가치 설명 강화)
  → 필수만 동의 시에도 서비스 정상 이용 가능함 강조
```

### 서버사이드 로그 보완 항목

```
keyword_click_log 기록 항목:
  keyword, tab, rank, session_hash (일별 salt SHA-256)

GA4 미수집 사용자 행동 보완:
  - 탭별 클릭 분포 (keyword_click_log GROUP BY tab)
  - 순위별 CTR (rank별 클릭 수 / 전체 노출 추정)
  - 주간 활성 키워드 (7일간 클릭량 TOP10)
```

---

## 7. R5 — GitHub Actions 분 초과

**리스크 설명:** Private Repo 월 2,000분 무료. 현재 추정 사용량 1,080분.
수집 스크립트 복잡도 증가 또는 채널 추가 시 초과 가능.

### 감지 방법

```
GitHub → Settings → Billing → Actions usage 월 1회 확인
사용량 1,600분(80%) 도달 시 대응 준비
```

### 즉시 대응

```
1단계: 수집 주기 2시간 → 3시간으로 조정
       월 사용량: 3분 × 8회 × 30일 = 720분으로 감소

2단계: Supabase Edge Functions 전환
       - Python → Deno(TypeScript) 재작성 필요
       - Supabase Free 플랜 내 Edge Functions 500,000건/월 무료
       - GitHub Actions 의존 완전 제거 가능
```

---

## 8. R6 — MAU 5,000 미달성

**리스크 설명:** 3개월 내 MAU 5,000 미달성 시 2단계(앱·수익화) 착수 지연.

### 감지 방법

```
GA4 월간 보고서:
  - MAU 진행률 (3개월 목표 5,000 기준)
  - 신규 vs 재방문 비율
  - 유입 채널별 비중 (검색·직접·소셜)
  - D7 리텐션 (목표 25%)

판단 시점: 런칭 후 6주차 MAU 1,500 미만이면 전략 재검토
```

### 대응 액션

| 시나리오 | 대응 |
|----------|------|
| 신규 유입 부족 | SEO 강화: 키워드별 블로그 포스트 작성, 외식업 커뮤니티(아프니까사장이다 등) 홍보 |
| 재방문율 저조 | D7 리텐션 25% 미달 → 온보딩 개선, 업데이트 주기 알림 (메타태그 OG 이미지 갱신) |
| 탭 사용 편중 | 특정 탭만 사용 → 미사용 탭 UX 개선 또는 컨텐츠 강화 |
| 전반적 정체 | 목표값 재설정 (MAU 5,000 → 3,000으로 조정 후 2단계 착수 기준 재검토) |

---

## 9. R7 — 구글 AI Overview 미출현

**리스크 설명:** 핵심 가치 제안(키워드 클릭 → AI 요약)이 구글 AI Overview 출현에 의존.
검색어 템플릿이 최적화되지 않으면 AI Overview 미출현.

### 감지 방법

```
운영자 주간 검증 프로세스 (FRD-04 §5 참조):
  1. search_templates WHERE is_verified = FALSE OR last_verified < NOW() - 14일
  2. 각 템플릿 구글 직접 검색 → AI Overview 출현 여부 확인
  3. 미출현 시 템플릿 패턴 수정 (FRD-04 §4 AI Overview 최적화 패턴 참조)

CTR 모니터링 (GA4):
  outbound_click / keyword_click 비율이 낮은 키워드
  → 사용자가 클릭 후 즉시 복귀 → AI Overview 미출현 의심
```

### 즉시 대응

```
AI Overview 미출현 패턴 → 높은 출현율 패턴으로 교체:
  NG: "[키워드]" (단순 명사)
  OK: "[키워드] 유행하는 이유 2025"
  OK: "[키워드] 인기 이유 2025"
  OK: "[키워드] 가격 오늘 전망"

is_verified = FALSE → 미출현 템플릿은 빠르게 수정 후 재검증
```

### 장기 대응

```
AI Overview 출현이 구조적으로 어려운 경우 (구글 정책 변경 등):
  - 구글 검색 결과 자체가 충분한 정보 제공 시 가치 유지
  - 뉴스·지식패널 결과가 표시되는 것으로 대체 가치 설명
  - 검색 연결 기능(F2) 가치 메시지 수정: "AI 요약" → "최신 정보 즉시 확인"
```

---

## 10. R8 — PIPA 위반 이슈

**리스크 설명:** 개인정보보호법(PIPA) 위반 시 과징금 또는 서비스 중단 위험.
GA4·Clarity 사용 및 서버사이드 로그 수집이 규제 대상.

### 예방 체계

```
런칭 전 필수 완료:
  □ 개인정보처리방침 /privacy 게시 (FRD-06 §5 필수 항목 전체 포함)
  □ 쿠키 동의 배너 작동 확인 (F5)
  □ GTM Consent Mode v2 연동 — 동의 전 GA4 미수집 확인
  □ keyword_click_log session_hash SHA-256 해시 처리 (원본 IP 미저장 확인)
  □ GA4 IP 익명화 설정 활성화 (GA4 기본 활성화 확인)
  □ Microsoft Clarity 개인정보 마스킹 활성화 확인
```

### 개인정보 삭제 요청 대응 프로세스

```
사용자 삭제 요청 접수 (이메일 또는 /privacy 페이지 내 연락처):
  1. keyword_click_log: session_hash는 일별 salt로 원본 IP 역산 불가
     → "수집된 데이터가 개인을 식별할 수 없는 형태로 처리됨" 안내
  2. GA4: GA4 관리 → 사용자 탐색기에서 Client ID 기반 삭제 요청 제출
  3. Clarity: Clarity 지원팀에 사용자 데이터 삭제 요청
  4. 요청 접수 후 30일 이내 처리 (PIPA 기준)
```

### 법률 자문 체크포인트

```
아래 상황 발생 시 개인정보보호 전문 법률 자문 필요:
  - 방송통신위원회 또는 개인정보보호위원회로부터 조사 통지 수신
  - 일 방문자 5만명 초과 (대규모 정보통신 서비스 기준 강화)
  - 2단계 — 회원가입·로그인 기능 추가 시
  - 광고 타겟팅 데이터 활용 (2단계 수익화) 시작 전
```

---

*FRD-08 RiskResponse | v1.0 | 2025.03*
*상위 문서: PRD_Main_v2.3*
