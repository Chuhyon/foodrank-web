# 푸드랭크 에러 이력 및 수정 기록

> 버그 발생 시 이 문서에 추가해두세요.
> 다음 기능 수정 시 동일 패턴의 실수를 예방합니다.

---

## ERR-001 | Supabase DNS 미해결 (WSL 환경)

- **발생**: 2026-03 초기 개발
- **증상**: WSL 터미널에서 `djlfngujhpvoyystmosc.supabase.co` DNS 조회 실패
- **원인**: WSL2 네트워크 DNS 설정이 Supabase 커스텀 도메인을 해석 못함
- **해결**: Supabase SQL Editor(웹)에서 직접 SQL 실행 (`doc/supabase_schema.sql`)
- **교훈**: WSL에서 외부 DB 직접 연결이 필요한 경우 브라우저 기반 콘솔 우선 사용

---

## ERR-002 | Vercel 배포 후 "데이터 수집 중입니다" 계속 표시

- **발생**: 2026-03 초기 배포 직후
- **증상**: Supabase에 데이터가 있는데도 웹에서 빈 상태 메시지 표시
- **원인**: Next.js ISR 캐시가 빈 데이터로 빌드된 후 갱신 안 됨 (revalidate: 600)
- **해결**: Vercel 강제 재배포 → ISR 캐시 초기화 후 새 데이터로 재빌드
- **교훈**: DB 초기 데이터 삽입 후 반드시 재배포 필요. 또는 `revalidate` 시간 단축 고려

---

## ERR-003 | package.json JSON 파싱 오류

- **발생**: 2026-03
- **증상**: `npm install` 시 `Unexpected token` JSON 파싱 에러
- **원인**: `libsodium-wrappers` 등 패키지 삭제 후 빈 줄이 남아 JSON 형식 깨짐
- **해결**: `package.json` 전체 재작성
- **교훈**: JSON 파일 수동 편집 후 반드시 유효성 검사 (`node -e "require('./package.json')"`)

---

## ERR-004 | Vercel 환경변수 등록 실패 (ENV_CONFLICT)

- **발생**: 2026-03
- **증상**: `vercel env add` 실행 시 409 Conflict 에러
- **원인**: 해당 환경변수가 이미 Vercel에 등록되어 있었음
- **해결**: 기존 값 확인 후 재등록 불필요 판단 — 그대로 사용
- **교훈**: 환경변수 등록 전 `vercel env ls`로 기존 등록 여부 확인

---

## ERR-005 | YouTube API 잘못된 자격증명 유형

- **발생**: 2026-03
- **증상**: YouTube API 호출 시 인증 실패
- **원인**: OAuth 2.0 Client ID/Secret을 API Key로 혼동하여 입력
- **해결**: GCP 콘솔 → API 및 서비스 → 사용자 인증정보 → **API 키** (`AIzaSy...` 형식) 사용
- **교훈**: YouTube Data API는 서버 사이드 단순 조회에 OAuth 불필요. API Key만 사용

---

## ERR-006 | 채널 신뢰도(source_count) 항상 1 표시

- **발생**: 2026-03 데이터 수집 파이프라인 가동 후
- **증상**: 홈페이지에서 모든 키워드의 채널 신뢰도가 ●○○○○ (1점)으로만 표시
- **원인**: `scripts/sources/naver.py`의 `groupName`이 카테고리명("마라탕류", "고기류")을 사용해 다른 채널(Google Trends: "마라탕", "무한리필 고기")과 키 불일치 → `aggregator.py`의 exact match에서 항상 1 채널만 인식
- **수정 파일**: `scripts/sources/naver.py`
- **수정 내용**:

  | 수정 전 groupName | 수정 후 groupName |
  |------------------|------------------|
  | `"마라탕류"` | `"마라탕"` |
  | `"버블티류"` | `"버블티"` |
  | `"고기류"` | `"무한리필 고기"` |
  | `"뷔페류"` | `"한식뷔페"` |
  | `"분식류"` | `"로제떡볶이"` |
  | `"커피"` (다중 브랜드 묶음) | `"빽다방"` 등 개별 브랜드명 |

- **교훈**: 다채널 집계 시 모든 소스의 키 이름이 정확히 일치해야 함. 신규 채널 추가 시 기존 키 이름 목록과 대조 필수

---

## ERR-007 | 키워드 클릭 시 구글 검색어에 "null" 표시

- **발생**: 2026-03
- **증상**: 메뉴·브랜드 키워드 클릭 시 구글 검색창에 "null" 이라는 단어로 검색됨
- **원인 1**: `supabase_writer.py`의 `save_keyword_trends()`에서 `keyword_trends` 테이블 저장 시 `search_template` 컬럼 누락 → DB에 `null` 저장
- **원인 2**: `utils/searchConnect.js`에서 `encodeURIComponent(null)` = 문자열 `"null"` 처리
- **수정 파일**: `utils/searchConnect.js`, `scripts/supabase_writer.py`
- **수정 내용**:
  - `searchConnect.js`: `const query = searchTemplate || keyword` — null 시 키워드 그대로 사용
  - `supabase_writer.py`: keyword 저장 시 `search_template` 추가 (메뉴: `{keyword} 맛집`, 브랜드: `{keyword} 매장`)
- **교훈**: DB nullable 컬럼을 프론트에서 그대로 사용할 경우 반드시 null 체크/fallback 처리 필요

---

---

## ARCH-001 | 고정 키워드 → 동적 키워드 수집 구조 전환 (2026-03-15)

- **배경**: 고정 키워드 목록은 실제 실시간 트렌드를 반영하지 못함
- **변경 내용**:
  - Google Trends: `trending_searches('south_korea')` 로 실시간 급상승어 발견
  - 네이버 DataLab: 고정 5그룹 → 다른 채널 TOP10 키워드 검증(validator)으로 역할 변경
  - 신규 채널 3개 추가: 네이버 블로그·뉴스·쇼핑 (기존 API 키 재사용)
  - `food_filter.py`: 공통 음식 키워드 필터·추출 로직 분리
  - `aggregator.py`: 4채널 → 7채널, positional args → keyword args
  - `collect_all.py`: 단일 단계 → 2단계 파이프라인 (발견 → 검증 → 집계)
- **주의사항**:
  - Google Trends `trending_searches` 는 일 단위 갱신 (시간당 변경 없음)
  - 음식 트렌드가 실시간 급상승에 없으면 `related_queries` fallback 사용
  - 네이버 쇼핑 쇼핑 검색 total 값은 재고 수량 포함 — 순수 트렌드 지표 아님 (보조 신호)
  - 신규 채널 추가 시 `BASE_WEIGHTS` 합계 1.0 유지 필수

---

## 체크리스트 — 신규 기능 개발 시

- [ ] DB nullable 컬럼은 프론트에서 반드시 fallback 처리
- [ ] 다채널 집계 시 소스별 키 이름 일치 여부 확인
- [ ] 환경변수 변경 후 Vercel 재배포 확인
- [ ] `window.open()` 은 반드시 `fetch()` 전에 호출 (팝업 차단 방지)
- [ ] ISR 캐시 갱신이 필요한 변경 시 강제 재배포
- [ ] JSON 파일 편집 후 유효성 검사
