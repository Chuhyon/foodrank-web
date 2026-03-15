// FRD-02 기준 — GTM dataLayer 이벤트 헬퍼
// GTM 컨테이너가 없으면 아무것도 하지 않음 (안전 fallback)

function push(data) {
  if (typeof window === 'undefined') return;
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push(data);
}

/** 탭 전환 */
export function trackTabSwitch(tabFrom, tabTo) {
  push({ event: 'tab_switch', tab_from: tabFrom, tab_to: tabTo });
}

/** 키워드 클릭 + 구글 검색 이탈 */
export function trackKeywordClick({ keyword, tab, rank, trendDirection, sourceCount, searchTemplate }) {
  push({
    event: 'keyword_click',
    keyword,
    tab,
    rank,
    trend_direction: trendDirection,
    source_count:    sourceCount,
    search_template: searchTemplate,
  });
  push({
    event: 'outbound_click',
    keyword,
    search_template: searchTemplate,
  });
}

/** 쿠키 동의 — 전체 허용 */
export function grantAllConsent() {
  push({ event: 'consent_update', analytics_storage: 'granted' });
  push({ event: 'cookie_consent', consent_type: 'all' });
  try { localStorage.setItem('foodrank_consent', 'all'); } catch (_) {}
}

/** 쿠키 동의 — 필수만 */
export function grantEssentialOnly() {
  push({ event: 'cookie_consent', consent_type: 'essential_only' });
  try { localStorage.setItem('foodrank_consent', 'essential_only'); } catch (_) {}
}

/** 저장된 동의 상태 조회 */
export function getSavedConsent() {
  try { return localStorage.getItem('foodrank_consent'); } catch (_) { return null; }
}
