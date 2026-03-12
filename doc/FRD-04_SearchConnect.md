# FRD-04 | 구글 검색 연결 (F2)
> Feature Requirements Document
> 푸드랭크 — 구글 검색 연결 상세 구현 명세
> 2025.03 | v1.1

---

## 1. 기능 개요

| 항목 | 내용 |
|------|------|
| 기능 ID | F2 |
| 기능명 | 구글 검색 연결 |
| 목적 | 키워드 클릭 시 최적화된 검색어로 구글 AI Overview 제공 |
| 핵심 가치 | 스크래핑 없이 AI 분석 효과 동일 구현 |

---

## 2. 동작 흐름

```
사용자: 키워드 클릭
    ↓
1. GTM dataLayer push → GA4 keyword_click 이벤트 수집
2. GTM dataLayer push → GA4 outbound_click 이벤트 수집
3. 구글 검색 새 탭 즉시 실행  ← 사용자 클릭 직후에 실행해야 팝업 차단 방지
4. Supabase 서버사이드 클릭 로그 (익명 해시) — 비동기, 새 탭 실행 후 처리
    ↓
구글 검색 → AI Overview + 뉴스 표시
```

> ⚠️ **팝업 차단 방지 원칙**
> `window.open()`은 사용자가 직접 클릭한 동기 흐름(synchronous context) 내에서 호출해야 합니다.
> `await fetch(...)` 이후에 `window.open()`을 호출하면 브라우저가 사용자 상호작용으로 인식하지 않아
> iOS Safari, Chrome 등에서 팝업 차단기에 의해 새 탭이 열리지 않을 수 있습니다.
> 반드시 서버사이드 로그 전송 **전에** `window.open()`을 호출합니다.

---

## 3. 구현 코드

### 클릭 핸들러 (Next.js)

```javascript
// utils/searchConnect.js

export function handleKeywordClick({
  keyword,
  tab,
  rank,
  trendDirection,
  sourceCount,
  searchTemplate,
}) {
  // 1. GTM dataLayer push (GA4 자동 수집)
  window.dataLayer = window.dataLayer || [];

  dataLayer.push({
    event: 'keyword_click',
    keyword,
    tab,
    rank,
    trend_direction: trendDirection,
    source_count: sourceCount,
    search_template: searchTemplate,
  });

  dataLayer.push({
    event: 'outbound_click',
    keyword,
    search_template: searchTemplate,
  });

  // 2. 구글 검색 새 탭 즉시 실행
  // ⚠️ 반드시 await fetch() 호출 전에 실행해야 팝업 차단 방지
  const url = `https://www.google.com/search?q=${encodeURIComponent(searchTemplate)}`;
  const newTab = window.open(url, '_blank', 'noopener,noreferrer');

  // window.open이 차단된 경우 fallback (일부 브라우저 설정)
  if (!newTab) {
    window.location.href = url;
  }

  // 3. 서버사이드 클릭 로그 — fire-and-forget (새 탭 실행 후 비동기 전송)
  fetch('/api/log-click', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ keyword, tab, rank }),
  }).catch(() => {
    // 로그 전송 실패는 사용자 경험에 영향 없음 — 무시
  });
}
```

> 📌 **함수를 `async`로 선언하지 않는 이유**
> `async` 함수 내에서 `await`를 사용하면 `window.open()` 호출 시점이 비동기 태스크 이후로 밀립니다.
> 브라우저는 이를 사용자의 직접 상호작용으로 보지 않아 팝업 차단기가 동작합니다.
> fetch는 Promise를 반환하지만 결과를 기다리지 않아도 전송은 정상 처리됩니다.

### 컴포넌트 적용 예시

```jsx
// components/KeywordItem.jsx
import { handleKeywordClick } from '@/utils/searchConnect';

export default function KeywordItem({ item }) {
  return (
    <li
      className="keyword-item cursor-pointer"
      onClick={() => handleKeywordClick({
        keyword: item.keyword,
        tab: item.tab,
        rank: item.rank,
        trendDirection: item.trend_direction,
        sourceCount: item.source_count,
        searchTemplate: item.search_template,
      })}
    >
      <span className="rank">{item.rank}</span>
      <span className="trend">{TREND_ICONS[item.trend_direction]}</span>
      <span className="keyword">{item.keyword}</span>
      <SourceIndicator count={item.source_count} />
    </li>
  );
}

const TREND_ICONS = {
  up_up: '↑↑',
  up: '↑',
  stay: '→',
  down: '↓',
  new: '🆕',
};
```

---

## 4. 검색어 템플릿 설계

### AI Overview 출현 최적화 패턴

| 패턴 | 예시 | 출현율 |
|------|------|--------|
| `[키워드] + 유행하는 이유 + 연도` | "마라탕 유행하는 이유 2025" | 높음 |
| `[키워드] + 인기 이유 + 연도` | "빽다방 인기 이유 2025" | 높음 |
| `[키워드] + 가격 오늘 전망` | "대파 가격 오늘 전망" | 높음 |
| `[키워드] + 트렌드 전망` | "편의점 도시락 트렌드 전망" | 높음 |
| `[키워드] + 창업 전망 + 연도` | "한식뷔페 창업 전망 2025" | 중간 |
| `[키워드] + 도매가 오르는 이유` | "양파 도매가 오르는 이유" | 높음 |

**AI Overview가 잘 안 뜨는 패턴:**
- 단순 명사 단독 ("마라탕", "대파") → 쇼핑/지식백과 결과만 노출

### 탭별 기본 템플릿 규칙

```python
# 탭별 기본 템플릿 자동 생성 규칙 (search_templates 미등록 키워드에 적용)

TEMPLATE_RULES = {
    'menu': '{keyword} 유행하는 이유 2025',
    'brand': '{keyword} 인기 이유 2025',
    'price': '{keyword} 가격 오늘 전망',
}

def generate_default_template(keyword: str, tab: str) -> str:
    rule = TEMPLATE_RULES.get(tab, '{keyword} 트렌드 2025')
    return rule.format(keyword=keyword)
```

---

## 5. 검색어 품질 관리 프로세스

### 1단계: 자동 생성 (신규 키워드 진입 시)
```
새 키워드 TOP10 진입
  → search_templates 테이블 확인
  → 미등록 시 기본 템플릿 자동 생성 + is_verified = FALSE
  → Slack/이메일 운영자 알림 (미검증 키워드 발생)
```

### 2단계: 운영자 수동 검증 (주 1회, 약 30분)

```
1. SELECT * FROM search_templates
   WHERE is_verified = FALSE OR last_verified < NOW() - INTERVAL '14 days'

2. 각 템플릿 → 구글 직접 검색 → AI Overview 출현 확인

3. 출현 O → is_verified = TRUE, last_verified = TODAY
   출현 X → 템플릿 수정 후 재확인

4. 검증 완료 후 ctr_rate 초기화 (다음 GA4 집계 대기)
```

### 3단계: CTR 기반 자동 최적화 (월 1회)

```
GA4 → keyword_click 이벤트 → search_template별 CTR 계산
  → search_templates.ctr_rate 업데이트
  → CTR 하위 20% → is_active = FALSE (노출 중단)
  → CTR 상위 3개 패턴 분석 → 신규 키워드 템플릿 규칙 반영
```

---

## 6. Supabase search_templates 테이블

> ⚠️ FRD-01과 동일 스키마 — 두 문서 모두 이 정의를 기준으로 구현

```sql
CREATE TABLE search_templates (
  id            SERIAL PRIMARY KEY,
  keyword       TEXT NOT NULL,
  tab           TEXT NOT NULL          CHECK (tab IN ('menu', 'brand', 'price')),
  template      TEXT NOT NULL,          -- 구글 검색 쿼리
  is_active     BOOLEAN DEFAULT TRUE,
  is_verified   BOOLEAN DEFAULT FALSE,  -- 운영자 AI Overview 확인 여부
  ctr_rate      FLOAT,                  -- GA4 집계 CTR (%)
  last_verified DATE,                   -- 마지막 검증일
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (keyword, tab)
);
```

---

## 7. 물가 탭 키워드 → 검색어 템플릿 변환

물가 탭은 KAMIS에서 "대파", "양파" 같은 식자재명이 키워드로 들어옴.
가격 변동 방향에 따라 템플릿을 다르게 적용.

```python
def generate_price_template(item_name: str, direction: str, change_rate: float) -> str:
    abs_rate = abs(change_rate)

    if direction == 'up' and abs_rate >= 20:
        return f"{item_name} 가격 급등 이유 오늘"
    elif direction == 'up':
        return f"{item_name} 가격 오늘 전망"
    elif direction == 'down' and abs_rate >= 20:
        return f"{item_name} 가격 급락 이유"
    else:
        return f"{item_name} 도매가 시세 오늘"
```

---

## 8. 테스트 체크리스트

```
□ 키워드 클릭 시 새 탭에서 구글 열리는지 확인
□ iOS Safari에서 새 탭 팝업 차단 없이 열리는지 확인
□ Chrome 팝업 차단 설정 상태에서도 새 탭 열리는지 확인
□ window.open 반환값이 null일 때 location.href fallback 동작 확인
□ GA4 실시간 이벤트에서 keyword_click 수신 확인
□ GA4 실시간 이벤트에서 outbound_click 수신 확인
□ Supabase keyword_click_log 레코드 생성 확인 (새 탭 열린 후 비동기 저장)
□ 검색어 템플릿이 올바르게 적용되는지 확인
□ 모바일(Android) 환경에서 새 탭 열림 확인
```

---

*FRD-04 SearchConnect | v1.1 | 2025.03*
*상위 문서: PRD_Main_v2.3*
*변경: handleKeywordClick에서 async/await 제거, window.open을 fetch 전으로 이동 (팝업 차단 버그 수정). fallback 로직 추가. search_templates 스키마에 CHECK 제약 추가 (FRD-01 통일).*
