// FRD-04 기준 구현
// ⚠️ window.open()은 반드시 fetch 전에 호출 (팝업 차단 방지)

export function handleKeywordClick({ keyword, tab, rank, searchTemplate }) {
  // 1. 구글 검색 새 탭 즉시 실행 (동기 흐름 내에서 호출)
  // search_template이 null/undefined면 keyword 그대로 사용
  const query = searchTemplate || keyword;
  const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
  const newTab = window.open(url, '_blank', 'noopener,noreferrer');

  // window.open이 차단된 경우 fallback
  if (!newTab) {
    window.location.href = url;
  }
}
