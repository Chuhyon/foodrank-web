// 데모용 목업 데이터 — 실제 서비스에서는 Supabase API로 교체
// collected_at: 가장 최근 2시간 단위 수집 시각

export const collectedAt = '2025.03.09 14:00';

export const menuTrends = [
  { rank: 1, prev_rank: 3,  trend_direction: 'up_up', keyword: '마라탕',        source_count: 4, search_template: '마라탕 유행하는 이유 2025' },
  { rank: 2, prev_rank: 2,  trend_direction: 'stay',  keyword: '편의점 도시락', source_count: 3, search_template: '편의점 도시락 트렌드 2025' },
  { rank: 3, prev_rank: 4,  trend_direction: 'up',    keyword: '무한리필 고기', source_count: 3, search_template: '무한리필 고기 인기 이유 2025' },
  { rank: 4, prev_rank: 3,  trend_direction: 'down',  keyword: '버블티',        source_count: 2, search_template: '버블티 유행하는 이유 2025' },
  { rank: 5, prev_rank: 6,  trend_direction: 'up',    keyword: '한식 뷔페',     source_count: 2, search_template: '한식뷔페 인기 이유 2025' },
  { rank: 6, prev_rank: null, trend_direction: 'new', keyword: '스몰비어',      source_count: 2, search_template: '스몰비어 트렌드 2025' },
  { rank: 7, prev_rank: 7,  trend_direction: 'stay',  keyword: '마라샹궈',      source_count: 1, search_template: '마라샹궈 유행하는 이유 2025' },
  { rank: 8, prev_rank: 7,  trend_direction: 'down',  keyword: '파스타',        source_count: 1, search_template: '파스타 인기 이유 2025' },
  { rank: 9, prev_rank: 9,  trend_direction: 'stay',  keyword: '초밥',          source_count: 1, search_template: '초밥 트렌드 2025' },
  { rank: 10, prev_rank: 11, trend_direction: 'up',   keyword: '로제떡볶이',    source_count: 1, search_template: '로제떡볶이 유행하는 이유 2025' },
];

export const brandTrends = [
  { rank: 1, prev_rank: 3,  trend_direction: 'up_up', keyword: '빽다방',        source_count: 4, search_template: '빽다방 인기 이유 2025' },
  { rank: 2, prev_rank: 3,  trend_direction: 'up',    keyword: '맘스터치',      source_count: 3, search_template: '맘스터치 인기 이유 2025' },
  { rank: 3, prev_rank: 3,  trend_direction: 'stay',  keyword: '교촌치킨',      source_count: 3, search_template: '교촌치킨 인기 이유 2025' },
  { rank: 4, prev_rank: 6,  trend_direction: 'up_up', keyword: '컴포즈커피',    source_count: 2, search_template: '컴포즈커피 인기 이유 2025' },
  { rank: 5, prev_rank: 6,  trend_direction: 'up',    keyword: '노브랜드버거',  source_count: 2, search_template: '노브랜드버거 인기 이유 2025' },
  { rank: 6, prev_rank: null, trend_direction: 'new', keyword: '고피자',        source_count: 2, search_template: '고피자 인기 이유 2025' },
  { rank: 7, prev_rank: 7,  trend_direction: 'stay',  keyword: '메가MGC커피',   source_count: 1, search_template: '메가MGC커피 인기 이유 2025' },
  { rank: 8, prev_rank: 7,  trend_direction: 'down',  keyword: '청년다방',      source_count: 1, search_template: '청년다방 인기 이유 2025' },
  { rank: 9, prev_rank: 9,  trend_direction: 'stay',  keyword: '투썸플레이스',  source_count: 1, search_template: '투썸플레이스 인기 이유 2025' },
  { rank: 10, prev_rank: 11, trend_direction: 'up',   keyword: '할리스',        source_count: 1, search_template: '할리스 인기 이유 2025' },
];

export const priceTrends = [
  { rank: 1,  keyword: '대파',    direction: 'up',   change_rate: 35.2,  today_price: 2100,  unit: 'kg' },
  { rank: 2,  keyword: '상추',    direction: 'up',   change_rate: 28.7,  today_price: 4500,  unit: '100g' },
  { rank: 3,  keyword: '고추',    direction: 'down', change_rate: -22.1, today_price: 15000, unit: 'kg' },
  { rank: 4,  keyword: '양파',    direction: 'down', change_rate: -18.5, today_price: 890,   unit: 'kg' },
  { rank: 5,  keyword: '양배추',  direction: 'up',   change_rate: 19.8,  today_price: 3400,  unit: '통' },
  { rank: 6,  keyword: '달걀',    direction: 'up',   change_rate: 12.3,  today_price: 3200,  unit: '30개' },
  { rank: 7,  keyword: '돼지고기', direction: 'up',  change_rate: 8.4,   today_price: 12800, unit: 'kg' },
  { rank: 8,  keyword: '감자',    direction: 'down', change_rate: -14.3, today_price: 2100,  unit: 'kg' },
  { rank: 9,  keyword: '두부',    direction: 'up',   change_rate: 6.2,   today_price: 1800,  unit: '모' },
  { rank: 10, keyword: '마늘',    direction: 'down', change_rate: -9.7,  today_price: 8200,  unit: 'kg' },
];

// 물가 탭 검색 템플릿 (변동률 기반)
export function getPriceTemplate(keyword, direction, changeRate) {
  const abs = Math.abs(changeRate);
  if (direction === 'up' && abs >= 20) return `${keyword} 가격 급등 이유 오늘`;
  if (direction === 'up') return `${keyword} 가격 오늘 전망`;
  if (direction === 'down' && abs >= 20) return `${keyword} 가격 급락 이유`;
  return `${keyword} 도매가 시세 오늘`;
}
