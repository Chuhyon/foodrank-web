# FRD-03 | 온보딩 (F6)
> Feature Requirements Document
> 푸드랭크 — 최초 방문자 온보딩 UX 상세 명세
> 2025.03 | v1.0

---

## 1. 기능 개요

| 항목 | 내용 |
|------|------|
| 기능 ID | F6 |
| 기능명 | 온보딩 플로우 |
| 목적 | 최초 방문자가 서비스 핵심 가치를 빠르게 이해하고 첫 행동(키워드 클릭)으로 유도 |
| 표시 조건 | 최초 방문 1회만 표시 (localStorage `onboarding_done` 플래그 기준) |

---

## 2. 온보딩 구조 (4단계)

```
[단계 1] 서비스 소개
[단계 2] 탭 기능 설명
[단계 3] 키워드 클릭 사용법
[단계 4] 데이터 신뢰도 설명
         ↓
[완료] 대시보드 진입
```

---

## 3. 각 단계 상세

### 단계 1 — 서비스 소개

```
┌─────────────────────────────────────────┐
│                                         │
│         🔥 푸드랭크에 오신 것을         │
│             환영합니다!                  │
│                                         │
│  외식업·프랜차이즈 종사자를 위한        │
│  실시간 트렌드 대시보드입니다.           │
│                                         │
│  인기 메뉴, 급상승 브랜드,              │
│  식자재 물가를 한눈에 확인하세요.       │
│                                         │
│              [다음 →]                   │
│          [건너뛰기]                     │
└─────────────────────────────────────────┘
```

| 요소 | 내용 |
|------|------|
| 헤드라인 | "🔥 푸드랭크에 오신 것을 환영합니다!" |
| 설명 | "외식업·프랜차이즈 종사자를 위한 실시간 트렌드 대시보드" |
| 보조 설명 | "인기 메뉴, 급상승 브랜드, 식자재 물가를 한눈에 확인하세요." |
| 버튼 | [다음 →] / [건너뛰기] |

---

### 단계 2 — 탭 기능 설명

```
┌─────────────────────────────────────────┐
│                                         │
│         📊 3가지 탭으로 구성됩니다      │
│                                         │
│  🍜 메뉴 트렌드                         │
│     요즘 뜨는 음식 키워드 TOP10         │
│                                         │
│  📈 급상승 브랜드                       │
│     검색량 급등 외식 브랜드 TOP10       │
│                                         │
│  💰 물가 주의보                         │
│     전일 대비 가격 변동 식자재 TOP10    │
│                                         │
│         [← 이전]  [다음 →]             │
└─────────────────────────────────────────┘
```

| 요소 | 내용 |
|------|------|
| 헤드라인 | "📊 3가지 탭으로 구성됩니다" |
| 메뉴 트렌드 | 아이콘 🍜 + "요즘 뜨는 음식 키워드 TOP10" |
| 급상승 브랜드 | 아이콘 📈 + "검색량 급등 외식 브랜드 TOP10" |
| 물가 주의보 | 아이콘 💰 + "전일 대비 가격 변동 식자재 TOP10" |
| 버튼 | [← 이전] / [다음 →] |

---

### 단계 3 — 키워드 클릭 사용법

```
┌─────────────────────────────────────────┐
│                                         │
│      🔍 키워드를 클릭하면?              │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  1  ↑↑  마라탕       ●●●●○      │   │
│  └──────────────────────────────────┘   │
│           ↑ 클릭해보세요!               │
│                                         │
│  구글에서 AI 요약 정보를 바로 확인      │
│  할 수 있습니다.                         │
│                                         │
│  별도 검색 없이 핵심 정보에 즉시 도달! │
│                                         │
│         [← 이전]  [다음 →]             │
└─────────────────────────────────────────┘
```

| 요소 | 내용 |
|------|------|
| 헤드라인 | "🔍 키워드를 클릭하면?" |
| 시각 요소 | 키워드 행 목업 (마라탕 예시) + 화살표 강조 |
| 설명 | "구글에서 AI 요약 정보를 바로 확인할 수 있습니다." |
| 보조 설명 | "별도 검색 없이 핵심 정보에 즉시 도달!" |
| 버튼 | [← 이전] / [다음 →] |

---

### 단계 4 — 데이터 신뢰도 설명

```
┌─────────────────────────────────────────┐
│                                         │
│      ●●●●○ 이 표시는 뭔가요?           │
│                                         │
│  채널 신뢰도 지표입니다.                │
│                                         │
│  네이버·구글·유튜브·X 등               │
│  최대 4개 채널 데이터를 집계합니다.    │
│                                         │
│  도트가 많을수록 더 많은 채널에서      │
│  검증된 트렌드입니다.                   │
│                                         │
│  데이터는 2시간마다 자동 갱신됩니다.   │
│                                         │
│      [← 이전]  [시작하기 🚀]           │
└─────────────────────────────────────────┘
```

| 요소 | 내용 |
|------|------|
| 헤드라인 | "●●●●○ 이 표시는 뭔가요?" |
| 설명 | "채널 신뢰도 지표입니다. 네이버·구글·유튜브·X 등 최대 4개 채널 데이터를 집계합니다." |
| 보조 설명 | "도트가 많을수록 더 많은 채널에서 검증된 트렌드입니다." |
| 갱신 안내 | "데이터는 2시간마다 자동 갱신됩니다." |
| 버튼 | [← 이전] / [시작하기 🚀] |

---

## 4. UI 동작 규칙

### 표시 조건

```javascript
// 최초 방문 판별 (localStorage 기반)
const isFirstVisit = !localStorage.getItem('onboarding_done');

if (isFirstVisit) {
  // 온보딩 모달 표시
  setShowOnboarding(true);
}

// 온보딩 완료 또는 건너뛰기 시
function completeOnboarding() {
  localStorage.setItem('onboarding_done', 'true');
  setShowOnboarding(false);
}
```

### 표시 방식

| 항목 | 결정 사항 |
|------|-----------|
| 형태 | 전체 화면 오버레이 모달 (배경 블러 처리) |
| 진행 표시 | 하단 도트 인디케이터 ●●○○ (현재 단계 표시) |
| 배경 클릭 | 닫힘 없음 (온보딩 완료 전까지 강제) |
| ESC 키 | 건너뛰기로 처리 |
| 건너뛰기 | 1단계에서만 노출, 클릭 시 즉시 완료 처리 |
| 애니메이션 | 단계 전환 시 슬라이드 인 (300ms ease) |

---

## 5. 컴포넌트 구조

```
components/onboarding/
├── OnboardingModal.jsx     ← 모달 컨테이너 + 단계 상태 관리
├── OnboardingStep1.jsx     ← 서비스 소개
├── OnboardingStep2.jsx     ← 탭 기능 설명
├── OnboardingStep3.jsx     ← 키워드 클릭 사용법
├── OnboardingStep4.jsx     ← 채널 신뢰도 설명
└── OnboardingDots.jsx      ← 하단 단계 인디케이터
```

```jsx
// components/onboarding/OnboardingModal.jsx
import { useState, useEffect } from 'react';

export default function OnboardingModal() {
  const [show, setShow] = useState(false);
  const [step, setStep] = useState(1);

  useEffect(() => {
    if (!localStorage.getItem('onboarding_done')) {
      setShow(true);
    }
  }, []);

  function handleNext() {
    if (step < 4) {
      setStep(step + 1);
      pushOnboardingStep(step, 'next');
    } else {
      handleComplete();
    }
  }

  function handlePrev() {
    if (step > 1) setStep(step - 1);
  }

  function handleSkip() {
    pushOnboardingStep(step, 'skip');
    handleComplete();
  }

  function handleComplete() {
    pushOnboardingStep(step, 'close');
    localStorage.setItem('onboarding_done', 'true');
    setShow(false);
  }

  if (!show) return null;

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-modal">
        {/* 현재 단계 컴포넌트 렌더링 */}
        <OnboardingDots total={4} current={step} />
      </div>
    </div>
  );
}

// GTM dataLayer push
function pushOnboardingStep(step, action) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: 'onboarding_step',
    step,
    action, // next | skip | close
  });
}
```

---

## 6. Analytics 연동

FRD-02 기준 `onboarding_step` 이벤트 수집.

| 이벤트 | 파라미터 | 수집 시점 |
|--------|---------|-----------|
| `onboarding_step` | `step: 1~4`, `action: 'next'` | 다음 버튼 클릭 시 |
| `onboarding_step` | `step: 1`, `action: 'skip'` | 건너뛰기 클릭 시 |
| `onboarding_step` | `step: 4`, `action: 'close'` | 시작하기 클릭 시 |

### GA4 퍼널 보고서 설계

```
퍼널 이름: 온보딩 완료율
단계:
  1단계: onboarding_step (step=1, action=next) 발생
  2단계: onboarding_step (step=2, action=next) 발생
  3단계: onboarding_step (step=3, action=next) 발생
  4단계: onboarding_step (step=4, action=close) 발생

목표: 4단계 완료율 60% 이상
이탈 집중 분석: 50% 미만 단계 → UX 개선 우선
```

---

## 7. 테스트 체크리스트

```
□ 최초 방문 시 온보딩 모달 표시 확인
□ 재방문 시 모달 미표시 확인 (localStorage 플래그)
□ 단계 전환 (다음/이전) 정상 동작 확인
□ 건너뛰기 → 즉시 완료 처리 및 모달 닫힘 확인
□ 시작하기 클릭 → 완료 처리 및 대시보드 노출 확인
□ ESC 키 → 건너뛰기 처리 확인
□ GTM Preview에서 각 단계 onboarding_step 이벤트 수신 확인
□ GA4 실시간 보고서에서 onboarding_step 이벤트 확인
□ 모바일(375px) 환경에서 모달 레이아웃 정상 표시 확인
```

---

*FRD-03 Onboarding | v1.0 | 2025.03*
*상위 문서: PRD_Main_v2.3*
