# 푸드랭크 문서 검토 결과 요약

> **상태: 전체 수정 완료 (2025.03)**
> 아래 이슈는 모두 각 FRD v1.1 / PRD v2.3에 반영됨.

---

## 수정 완료 이슈

| 심각도 | 위치 | 이슈 | 수정 내용 | 반영 버전 |
|--------|------|------|-----------|-----------|
| 🔴 Critical | FRD-04 | `handleKeywordClick` async + await 후 `window.open()` → 팝업 차단 | 동기 함수로 변환, `window.open()`을 fetch 전으로 이동 | v1.1 |
| 🟠 High | FRD-01 | `search_templates` 스키마에 `is_verified`, `updated_at`, `UNIQUE(keyword, tab)` 누락 | FRD-04 기준으로 통일 | v1.1 |
| 🟠 High | FRD-05 | `SourceIndicator MAX = 4` — UI 목업(5칸) 및 설명("5점 만점")과 불일치 | `MAX = 5`로 수정, 표시 규칙 설명 명확화 | v1.1 |
| 🟡 Medium | FRD-07 | §3 시뮬레이션에 배너 광고 수익 포함되나 §2에 모델 정의 없음 | §2에 모델 C(디스플레이 배너 광고) 추가 | v1.1 |
| 🟡 Medium | FRD-07 | MAU 5,000 리드 건수 "월 9건" 오표기 (0.34/일 × 30 = 10.2건) | "월 10건"으로 수정 | v1.1 |
| 🟢 Low | PRD | "실검" 약어 최초 사용 시 미정의 | "실시간 검색어(실검)" 형식으로 수정 | v2.3 |
| 🟢 Low | FRD-05 | `source_count / 4 × 5` 수식 불명확 | "5칸 중 source_count개 채움" 방식으로 설명 변경 | v1.1 |
