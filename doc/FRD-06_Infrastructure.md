# FRD-06 | 인프라·보안·SEO
> Feature Requirements Document
> 푸드랭크 — 인프라 구성·보안 정책·SEO 구현·비용 구조·개발 스프린트 상세
> 2025.03 | v1.0

---

## 1. 문서 목적
이 문서는 푸드랭크의 인프라 구성, 보안·개인정보 정책, SEO 구현 명세,
비용 구조, 14주 개발 스프린트 세부 태스크를 정의합니다.

---

## 2. 인프라 구성

### 전체 아키텍처

```
[사용자 브라우저]
        ↓ HTTPS
[Vercel — Next.js (ISR)]
        ↓ REST API
[Supabase — PostgreSQL]
        ↑
[GitHub Actions — Python 수집 스크립트 (2시간 주기)]
        ↑
[외부 API: 네이버 데이터랩 / pytrends / YouTube / X API / KAMIS]
```

### 서비스별 역할

| 서비스 | 역할 | 플랜 |
|--------|------|------|
| Vercel | Next.js 호스팅 + 자동 배포 (main 브랜치 push) | Hobby (Free) |
| Supabase | PostgreSQL DB + REST API + Auth (미사용 예정) | Free (500MB, 2GB 대역폭) |
| GitHub Actions | 2시간마다 Python 수집 스크립트 실행 | 월 2,000분 무료 |
| Google Tag Manager | 태그 관리 | Free |
| GA4 | 사용자 분석 | Free |
| Microsoft Clarity | 히트맵·세션 레코딩 | Free |
| Google Search Console | SEO 모니터링 | Free |

### GitHub Actions 분 계산

```
수집 스크립트 1회 실행 시간: 약 3분 (추정)
하루 실행 횟수: 24시간 / 2시간 = 12회
월 사용 분: 3분 × 12회 × 30일 = 1,080분
월 무료 한도: 2,000분 (Private Repo)
여유 분: 920분 → 한도 내 운영 가능

⚠️ 초과 시 대응: Supabase Edge Functions 전환 (FRD-08 §8 참조)
```

### Next.js ISR 캐싱 전략

```
revalidate: 600  (10분 캐시)

이유:
  - 데이터는 2시간마다 실제 갱신 — ISR 10분은 UI 서버 캐시
  - Vercel 무료 플랜 함수 실행 비용 최소화
  - 사용자에게 노출되는 "데이터 기준" 시각은 DB collected_at 기준 (UI 혼동 방지)

적용 페이지:
  - / (메인 대시보드) → revalidate: 600
  - /privacy → revalidate: 86400 (정적 페이지, 하루 캐시)
```

---

## 3. Supabase 설정

### 테이블 Row Level Security (RLS) 정책

```sql
-- keyword_trends: 읽기 전용 공개
ALTER TABLE keyword_trends ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public read" ON keyword_trends FOR SELECT USING (true);

-- price_trends: 읽기 전용 공개
ALTER TABLE price_trends ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public read" ON price_trends FOR SELECT USING (true);

-- brand_db: 읽기 전용 공개
ALTER TABLE brand_db ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public read" ON brand_db FOR SELECT USING (true);

-- keyword_click_log: 삽입 전용 (서버사이드 API Route에서만)
ALTER TABLE keyword_click_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "server insert only" ON keyword_click_log
  FOR INSERT WITH CHECK (true);
-- SELECT 정책 없음 — 운영자만 Supabase 대시보드 직접 접근

-- search_templates: 읽기 전용 공개
ALTER TABLE search_templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public read" ON search_templates FOR SELECT USING (true);
```

### API 키 관리

```
SUPABASE_URL          → Vercel 환경변수 (Public — Next.js 클라이언트)
SUPABASE_ANON_KEY     → Vercel 환경변수 (Public — 읽기 전용)
SUPABASE_SERVICE_KEY  → Vercel 환경변수 (Secret — 서버사이드 전용)

⚠️ SERVICE_KEY는 절대 클라이언트 코드에 노출 금지
   API Route(/api/log-click 등)에서만 사용
```

### 대역폭 초과 대응

```
무료 플랜 한도: 2GB/월

최적화 방법:
  1. Next.js ISR: Supabase 직접 호출 최소화 (10분 캐시)
  2. API Response: 필요 컬럼만 SELECT (SELECT *)  사용 금지
  3. 모니터링: Supabase 대시보드 월 1회 대역폭 확인

⚠️ MAU 10,000 도달 예상 시점에 Pro 플랜 전환 검토 ($25/월)
```

---

## 4. 보안 정책

### API Route 보안 (/api/log-click)

```javascript
// pages/api/log-click.js (Next.js API Route)

import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY  // 서버사이드 전용
);

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).end();
  }

  const { keyword, tab, rank } = req.body;

  // 입력값 검증
  if (!keyword || !tab || typeof rank !== 'number') {
    return res.status(400).end();
  }

  // session_hash: 일별 salt + IP SHA-256 (개인식별 불가)
  const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress || '';
  const sessionHash = crypto
    .createHash('sha256')
    .update(`${today}:${ip}`)
    .digest('hex');

  await supabase.from('keyword_click_log').insert({
    keyword,
    tab,
    rank,
    session_hash: sessionHash,
  });

  return res.status(200).end();
}
```

### HTTP 보안 헤더 (next.config.js)

```javascript
// next.config.js
const securityHeaders = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-XSS-Protection', value: '1; mode=block' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://clarity.ms",
      "img-src 'self' data: https:",
      "connect-src 'self' https://*.supabase.co https://www.google-analytics.com",
      "frame-src 'none'",
    ].join('; '),
  },
];

module.exports = {
  async headers() {
    return [{ source: '/(.*)', headers: securityHeaders }];
  },
};
```

---

## 5. 쿠키 동의 배너 구현 (F5, PIPA 준수)

### 배너 UI 명세

```
┌───────────────────────────────────────────────────────┐
│  🍪 이 웹사이트는 서비스 개선을 위해 쿠키를 사용합니다. │
│  GA4, Microsoft Clarity 분석 쿠키가 포함됩니다.         │
│                                                         │
│          [필수만 동의]        [전체 동의]               │
│          개인정보처리방침                               │
└───────────────────────────────────────────────────────┘
```

| 항목 | 결정 사항 |
|------|-----------|
| 표시 위치 | 하단 고정 배너 |
| 표시 조건 | localStorage `cookie_consent` 없을 때 |
| 필수만 동의 | GA4·Clarity 미로드, 서버사이드 로그만 수집 |
| 전체 동의 | GA4·Clarity 로드 허용 |
| 개인정보처리방침 | `/privacy` 페이지 링크 |
| 동의 저장 | localStorage `cookie_consent: 'all' | 'essential'` |

### 개인정보처리방침 필수 항목

```
/privacy 페이지 런칭 전 필수 게시 항목:
  □ 수집하는 개인정보 항목 (IP 해시, 쿠키)
  □ 수집 목적 (서비스 통계 분석)
  □ 보유 기간 (1년, 이후 파기)
  □ 제3자 제공 여부 (Google Analytics, Microsoft에 처리 위탁)
  □ 정보주체 권리 (열람·삭제 요청 방법)
  □ 개인정보 보호책임자 연락처
```

---

## 6. SEO 구현

### 메타태그 (Next.js Head)

```jsx
// pages/index.js
import Head from 'next/head';

export default function Home() {
  return (
    <>
      <Head>
        <title>푸드랭크 — 외식업 트렌드 실시간 순위</title>
        <meta
          name="description"
          content="인기 메뉴·급상승 브랜드·식자재 물가를 실시간으로 확인하세요. 외식업·프랜차이즈 종사자를 위한 트렌드 대시보드."
        />
        <meta property="og:title" content="푸드랭크 — 외식업 트렌드 실시간 순위" />
        <meta
          property="og:description"
          content="인기 메뉴·급상승 브랜드·식자재 물가 TOP10. 키워드 클릭 시 구글 AI 요약 즉시 확인."
        />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://foodrank.kr" />
        <link rel="canonical" href="https://foodrank.kr" />
      </Head>
      {/* ... */}
    </>
  );
}
```

### 구조화 데이터 (JSON-LD)

```jsx
// 트렌드 순위 리스트 구조화 데이터
const structuredData = {
  '@context': 'https://schema.org',
  '@type': 'ItemList',
  name: '외식업 인기 메뉴 트렌드 TOP10',
  description: '다중 채널 검색량 기반 인기 음식 키워드 순위',
  itemListElement: trendData.map((item, idx) => ({
    '@type': 'ListItem',
    position: idx + 1,
    name: item.keyword,
  })),
};
```

### Sitemap & robots.txt

```
// public/robots.txt
User-agent: *
Allow: /
Disallow: /api/
Sitemap: https://foodrank.kr/sitemap.xml

// pages/sitemap.xml.js (동적 생성)
// 정적 페이지: /, /privacy
// 동적 페이지: 추후 브랜드 상세 페이지 추가 시 확장
```

### Google Search Console 설정

```
□ 속성 추가: https://foodrank.kr
□ 소유권 확인: HTML 태그 방식 (Next.js Head에 삽입)
□ Sitemap 제출: https://foodrank.kr/sitemap.xml
□ GA4 연결 (Search Console → GA4 속성 연결)
□ 색인 요청: 첫 배포 후 URL 검사 → 색인 생성 요청
```

---

## 7. 비용 구조

### MVP 단계 월 비용

| 서비스 | 사용량 | 월 비용 |
|--------|--------|---------|
| Vercel (Hobby) | 무제한 배포, 함수 실행 제한 있음 | $0 |
| Supabase (Free) | DB 500MB, 대역폭 2GB | $0 |
| GitHub Actions | ~1,080분/월 (한도 2,000분) | $0 |
| GTM / GA4 / Clarity | — | $0 |
| Google Search Console | — | $0 |
| **MVP 합계** | | **$0/월** |

### 비용 발생 트리거

| 트리거 | 서비스 | 전환 플랜 | 예상 비용 |
|--------|--------|-----------|-----------|
| MAU 10,000 도달 | Supabase | Pro | $25/월 |
| GitHub Actions 분 초과 | GitHub Actions | Supabase Edge Functions 전환 | $0 (Supabase Free 내) |
| Vercel 함수 초과 | Vercel | Pro | $20/월 |

---

## 8. 개발 스프린트 세부 태스크 (14주)

### S1 (1~3주차) — Analytics + DB + 핵심 API

| 태스크 | 담당 | 완료 기준 |
|--------|------|-----------|
| GTM 컨테이너 생성 + Next.js 스니펫 삽입 | FE | GTM Preview에서 All Pages 트리거 확인 |
| GA4 속성 생성 + 맞춤 측정기준 6개 등록 | FE | GA4 실시간 페이지뷰 수신 |
| Microsoft Clarity 설치 + GA4 연동 | FE | Clarity 세션 레코딩 최초 수집 |
| Supabase 프로젝트 생성 + 전체 스키마 생성 | BE | 모든 테이블 생성 + RLS 정책 적용 |
| 네이버 데이터랩 API 연동 + 수집 스크립트 | BE | 키워드 수집 → Supabase 저장 확인 |
| KAMIS API 연동 + 물가 수집 스크립트 | BE | 식자재 가격 수집 → Supabase 저장 확인 |
| GitHub Actions cron 설정 (2시간 주기) | BE | Actions 자동 실행 + 로그 확인 |

### S2 (4~6주차) — 전체 채널 연동 + 집계 파이프라인

| 태스크 | 담당 | 완료 기준 |
|--------|------|-----------|
| Google Trends (pytrends) 수집 스크립트 | BE | 수집 + 실패 시 fallback 가중치 재분배 동작 |
| YouTube Data API v3 연동 | BE | 급상승 동영상 키워드 수집 확인 |
| X API v2 연동 | BE | 언급량 키워드 수집 확인 |
| 채널별 점수 정규화 + 가중치 합산 로직 | BE | TOP30 산출 결과 검증 |
| 순위 변동 방향 계산 로직 (↑↑/↑/→/↓/🆕) | BE | 이전 순위 비교 정확도 확인 |
| search_templates 자동 생성 로직 | BE | 신규 키워드 → 기본 템플릿 자동 등록 확인 |

### S3 (7~9주차) — 대시보드 UI 개발 + Vercel 배포

| 태스크 | 담당 | 완료 기준 |
|--------|------|-----------|
| 전체 레이아웃 (Header / TabBar / Footer) | FE | 반응형 3개 브레이크포인트 정상 표시 |
| TrendList / KeywordItem 컴포넌트 | FE | Supabase 데이터 연결 + 순위 표시 |
| PriceList / PriceItem 컴포넌트 | FE | KAMIS 데이터 + 변동률 표시 |
| SourceIndicator (●●●●○) 컴포넌트 | FE | MAX=5, source_count 반영 정확 |
| TrendBadge (↑↑/↑/→/↓/🆕) 컴포넌트 | FE | 각 방향 아이콘 정상 표시 |
| UpdateTimestamp 컴포넌트 | FE | DB collected_at 기준 시각 표시 |
| Vercel 배포 + 도메인 연결 | FE | https 접근 + 자동 배포 확인 |
| Next.js ISR revalidate 600 설정 | FE | 캐시 갱신 동작 확인 |
| 에러 상태 UI (이전 데이터 표시) | FE | Supabase 오류 시 이전 데이터 + 메시지 표시 |

### S4 (10~12주차) — GTM 이벤트 + 검색 연결 + 쿠키 배너

| 태스크 | 담당 | 완료 기준 |
|--------|------|-----------|
| GTM 이벤트 태그 4개 발행 (tab_switch 등) | FE | GA4 실시간에서 각 이벤트 수신 |
| handleKeywordClick 구현 (FRD-04 기준) | FE | iOS Safari 팝업 차단 없이 새 탭 열림 |
| /api/log-click API Route 구현 | FE/BE | 클릭 로그 Supabase 저장 + SHA-256 해시 확인 |
| 쿠키 동의 배너 컴포넌트 | FE | 전체 동의/필수만 동의 동작 + localStorage 저장 |
| GTM Consent Mode v2 연동 | FE | 동의 전 GA4 미수집, 동의 후 수집 전환 확인 |
| 개인정보처리방침 (/privacy) 페이지 | FE | 필수 항목 전체 포함 확인 |
| HTTP 보안 헤더 적용 (next.config.js) | FE | Security Headers 확인 |

### S5 (13~14주차) — QA + 운영자 검증 + 소프트 런칭

| 태스크 | 담당 | 완료 기준 |
|--------|------|-----------|
| 전체 기능 QA (FRD-04 테스트 체크리스트) | QA | 모든 항목 통과 |
| 모바일 (iOS Safari / Android Chrome) QA | QA | 팝업 차단 없이 동작 확인 |
| PageSpeed Insights 검증 | FE | 모바일 85점 이상 |
| search_templates 초기 데이터 운영자 검증 | OP | TOP30 키워드 템플릿 검증 완료 |
| Google Search Console 색인 요청 | OP | 주요 페이지 색인 등록 확인 |
| Supabase 대역폭·Actions 분 사용량 확인 | BE | 한도 내 운영 확인 |
| 소프트 런칭 (지인 테스트) | ALL | 치명적 버그 없음 확인 |

---

*FRD-06 Infrastructure | v1.0 | 2025.03*
*상위 문서: PRD_Main_v2.3*
