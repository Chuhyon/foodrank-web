# FRD-02 | Analytics
> Feature Requirements Document
> 푸드랭크 — GTM·GA4·Clarity 이벤트 스키마·보고서 설계·런칭 체크리스트
> 2025.03 | v1.0

---

## 1. 문서 목적
이 문서는 푸드랭크의 Analytics 스택 설계 상세를 정의합니다.
GTM 컨테이너 구조, GA4 이벤트 스키마, Microsoft Clarity 설정,
보고서 설계, 런칭 전 세팅 체크리스트를 포함합니다.

> ⚠️ Analytics는 **S1(1~3주차)에서 세팅 필수**
> 런칭 후 세팅 시 초기 사용자 데이터 영구 손실

---

## 2. 툴 스택 역할 분담

| 도구 | 역할 | 도입 시점 |
|------|------|-----------|
| Google Tag Manager (GTM) | 모든 태그 중앙 관리 — 코드 배포 없이 태그 추가·수정 | S1 |
| GA4 | 사용자 행동·전환·리텐션·코호트 분석 | S1 |
| Microsoft Clarity | 히트맵·세션 레코딩·클릭 패턴 시각화 | S1 |
| Google Search Console | SEO 검색 유입 추적·색인 관리 | S1 |
| Firebase Analytics | 앱 스트림 → GA4 연결 | 2단계 |

---

## 3. GTM 컨테이너 구조

### 컨테이너 설정

```
컨테이너 이름: FoodRank Web
컨테이너 ID: GTM-XXXXXXX (발급 후 기재)
환경: Production / Preview (개발 검증용)
```

### 태그 목록

| 태그 이름 | 태그 유형 | 트리거 |
|-----------|-----------|--------|
| GA4 Configuration | GA4 Configuration | All Pages |
| Clarity Configuration | Custom HTML | All Pages |
| GA4 - tab_switch | GA4 Event | tab_switch 커스텀 이벤트 |
| GA4 - keyword_click | GA4 Event | keyword_click 커스텀 이벤트 |
| GA4 - outbound_click | GA4 Event | outbound_click 커스텀 이벤트 |
| GA4 - onboarding_step | GA4 Event | onboarding_step 커스텀 이벤트 |
| GA4 - cookie_consent | GA4 Event | cookie_consent 커스텀 이벤트 |

### dataLayer 구조 예시

```javascript
// 탭 전환
window.dataLayer.push({
  event: 'tab_switch',
  tab_from: 'menu',   // 이전 탭
  tab_to: 'brand',    // 이동한 탭
});

// 키워드 클릭 (FRD-04 참조 — handleKeywordClick에서 push)
window.dataLayer.push({
  event: 'keyword_click',
  keyword: '마라탕',
  tab: 'menu',
  rank: 1,
  trend_direction: 'up_up',
  source_count: 4,
  search_template: '마라탕 유행하는 이유 2025',
});

// 구글 검색 이탈
window.dataLayer.push({
  event: 'outbound_click',
  keyword: '마라탕',
  search_template: '마라탕 유행하는 이유 2025',
});

// 온보딩 단계
window.dataLayer.push({
  event: 'onboarding_step',
  step: 2,             // 1~4
  action: 'next',      // next | skip | close
});

// 쿠키 동의
window.dataLayer.push({
  event: 'cookie_consent',
  consent_type: 'all', // all | essential_only
});
```

---

## 4. GA4 이벤트 스키마

### 핵심 이벤트

| 이벤트명 | 목적 | 파라미터 |
|---------|------|---------|
| `tab_switch` | 탭 사용 패턴 파악 | `tab_from`, `tab_to` |
| `keyword_click` | 키워드 CTR (핵심 지표) | `keyword`, `tab`, `rank`, `trend_direction`, `source_count`, `search_template` |
| `outbound_click` | 구글 검색 이탈 추적 | `keyword`, `search_template` |
| `onboarding_step` | 온보딩 퍼널 이탈 지점 | `step`, `action` |
| `cookie_consent` | 동의 전환율 측정 | `consent_type` |

### GA4 맞춤 측정기준 (Custom Dimensions)

| 이름 | 범위 | 설명 |
|------|------|------|
| `keyword` | 이벤트 | 클릭된 키워드명 |
| `tab` | 이벤트 | 메뉴·브랜드·물가 |
| `rank` | 이벤트 | 클릭 시 순위 (1~10) |
| `trend_direction` | 이벤트 | 순위 변동 방향 |
| `source_count` | 이벤트 | 집계 채널 수 |
| `search_template` | 이벤트 | 구글 검색 연결 템플릿 |
| `consent_type` | 사용자 | 쿠키 동의 유형 |

### GA4 전환 이벤트 설정

| 전환 이름 | 기준 이벤트 | 전환 조건 |
|-----------|------------|-----------|
| `keyword_click` | `keyword_click` | 이벤트 발생 = 전환 |
| `outbound_click` | `outbound_click` | 이벤트 발생 = 전환 |

---

## 5. Microsoft Clarity 설정

### 기본 설정

```
프로젝트 이름: FoodRank
추적 코드: GTM 태그로 삽입 (Custom HTML 태그)
데이터 마스킹: 개인정보 입력 필드 자동 마스킹 활성화
```

### 주요 활용 목적

| 기능 | 활용 방법 |
|------|-----------|
| 히트맵 | 탭별 키워드 클릭 분포 확인 — 상위/하위 순위 클릭 비율 비교 |
| 세션 레코딩 | 온보딩 이탈 구간 파악, 혼란 UX 발견 |
| Dead Click | 클릭 가능해 보이지만 반응 없는 UI 요소 식별 |
| Rage Click | 반복 클릭 발생 구간 — 오류 또는 느린 응답 의심 |
| Scroll Depth | 키워드 리스트 하단 노출 여부 확인 |

### GA4 연동

```
Clarity → GA4 연동 활성화 (Clarity 설정에서 GA4 Measurement ID 입력)
→ GA4 세션에서 Clarity 세션 레코딩 바로가기 링크 제공
```

---

## 6. 보고서 설계

### 주간 운영 보고서 (GA4 탐색 보고서)

| 보고서명 | 측정항목 | 측정기준 | 목적 |
|---------|---------|---------|------|
| 탭별 전환 현황 | 이벤트 수, 사용자 수 | tab, tab_to | 탭 인기도 파악 |
| 키워드 CTR 순위 | keyword_click 이벤트 수 / 세션 | keyword, tab, rank | 인기 키워드 & 저CTR 발견 |
| 온보딩 퍼널 | 각 단계 사용자 수, 이탈률 | onboarding step | 이탈 지점 개선 |
| 리텐션 코호트 | D7·D14·D30 리텐션 | 첫 방문 주차 | 서비스 재방문율 |

### 핵심 KPI 대시보드 (GA4 개요 보고서 커스텀)

```
MAU (월간 활성 사용자)          → 목표: 5,000 (3개월)
키워드 CTR (탭당 평균)          → 목표: 20% 이상
D7 리텐션                       → 목표: 25% 이상
평균 세션 시간                  → 목표: 1분 30초 이상
온보딩 완료율                   → 목표: 60% 이상
```

---

## 7. 쿠키 동의와 Analytics 연동

PIPA(개인정보보호법) 준수를 위한 GA4·Clarity 조건부 로드.

```javascript
// GTM — Consent Mode v2 설정
// 쿠키 동의 전: analytics_storage = denied
// 쿠키 동의 후: analytics_storage = granted

// 초기 기본값 설정 (페이지 로드 시)
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'consent_default',
  analytics_storage: 'denied',
  ad_storage: 'denied',
});

// 전체 동의 시
function grantAllConsent() {
  window.dataLayer.push({
    event: 'consent_update',
    analytics_storage: 'granted',
  });
  window.dataLayer.push({
    event: 'cookie_consent',
    consent_type: 'all',
  });
}

// 필수만 동의 시
function grantEssentialOnly() {
  window.dataLayer.push({
    event: 'cookie_consent',
    consent_type: 'essential_only',
  });
  // analytics_storage 는 denied 유지
}
```

> 📌 쿠키 거부 사용자의 GA4 데이터 손실은 Supabase 서버사이드 클릭 로그(keyword_click_log)로 보완.
> FRD-01 §7 스키마 참조.

---

## 8. 런칭 전 세팅 체크리스트

### GTM 설정

```
□ GTM 컨테이너 생성 및 스니펫 Next.js _document.js 삽입 확인
□ GA4 Configuration 태그 발행 및 All Pages 트리거 연결
□ Clarity 태그 발행 및 All Pages 트리거 연결
□ 각 커스텀 이벤트 태그(tab_switch, keyword_click, outbound_click, onboarding_step, cookie_consent) 생성 완료
□ GTM Preview 모드에서 각 이벤트 dataLayer 수신 확인
□ GTM 컨테이너 최종 퍼블리시
```

### GA4 설정

```
□ GA4 속성 생성, Measurement ID 발급
□ 맞춤 측정기준 6개 등록 (keyword, tab, rank, trend_direction, source_count, search_template)
□ keyword_click, outbound_click 전환 이벤트 등록
□ GA4 실시간 보고서에서 tab_switch, keyword_click 이벤트 수신 확인
□ Google Search Console 속성 연결
□ Consent Mode v2 작동 확인 (denied 상태에서 GA4 미수집 확인)
```

### Clarity 설정

```
□ Clarity 프로젝트 생성, 추적 코드 GTM 태그로 삽입
□ GA4 Measurement ID 연동 설정
□ 개인정보 마스킹 활성화 확인
□ 첫 세션 레코딩 수집 확인
```

### 검증

```
□ 실제 브라우저에서 탭 전환 → GA4 실시간에서 tab_switch 수신
□ 키워드 클릭 → GA4 실시간에서 keyword_click + outbound_click 동시 수신
□ 새 탭(구글 검색) 팝업 차단 없이 열림 확인 (iOS Safari / Chrome)
□ 쿠키 동의 전 GA4 미수집, 동의 후 수집 전환 확인
□ Supabase keyword_click_log 레코드 생성 확인
```

---

*FRD-02 Analytics | v1.0 | 2025.03*
*상위 문서: PRD_Main_v2.3*
