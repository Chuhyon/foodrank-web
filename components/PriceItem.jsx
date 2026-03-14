import { handleKeywordClick } from '../utils/searchConnect';

function getPriceTemplate(itemName, direction, changeRate) {
  const abs = Math.abs(changeRate);
  if (direction === 'up' && abs >= 20) return `${itemName} 가격 급등 이유 오늘`;
  if (direction === 'up') return `${itemName} 가격 오늘 전망`;
  if (direction === 'down' && abs >= 20) return `${itemName} 가격 급락 이유`;
  return `${itemName} 도매가 시세 오늘`;
}

export default function PriceItem({ item }) {
  const isUp = item.direction === 'up';
  const sign = isUp ? '+' : '';
  // Supabase에서 search_template이 있으면 사용, 없으면 자동 생성
  const searchTemplate =
    item.search_template || getPriceTemplate(item.item_name, item.direction, item.change_rate);

  // 단위 추정 (item_name 기반)
  const unitMap = { 달걀: '30개', 두부: '모', 양배추: '통' };
  const unit = unitMap[item.item_name] ?? 'kg';

  return (
    <li
      className="keyword-row flex items-center gap-3 px-4 py-3 cursor-pointer border-b border-gray-100 last:border-0 transition-colors"
      onClick={() =>
        handleKeywordClick({
          keyword: item.item_name,
          tab: 'price',
          rank: item.rank,
          searchTemplate,
        })
      }
    >
      <span className="w-6 text-center text-sm font-bold text-gray-500">{item.rank}</span>
      <span className={`w-8 text-center text-sm font-bold ${isUp ? 'text-red-500' : 'text-blue-500'}`}>
        {isUp ? '↑' : '↓'}
      </span>
      <span className="flex-1 font-medium text-gray-900">{item.item_name}</span>
      <span className={`text-sm font-bold w-16 text-right ${isUp ? 'text-red-500' : 'text-blue-500'}`}>
        {sign}{item.change_rate.toFixed(1)}%
      </span>
      <span className="text-sm text-gray-500 w-28 text-right">
        ₩{item.today_price.toLocaleString()}/{unit}
      </span>
    </li>
  );
}
