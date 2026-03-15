// FRD-04 기준 구현
// ⚠️ window.open()은 반드시 fetch 전에 호출 (팝업 차단 방지)
import { trackKeywordClick } from './analytics';

export function handleKeywordClick({ keyword, tab, rank, searchTemplate, trendDirection, sourceCount }) {
  // 1. 구글 검색 새 탭 즉시 실행 (동기 흐름 내에서 호출)
  const query = searchTemplate || keyword;
  const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
  const newTab = window.open(url, '_blank', 'noopener,noreferrer');

  if (!newTab) {
    window.location.href = url;
  }

  // 2. Analytics 이벤트 (window.open 이후 — 팝업 차단 방지 준수)
  trackKeywordClick({ keyword, tab, rank, trendDirection, sourceCount, searchTemplate: query });
}
