import { handleKeywordClick } from '../utils/searchConnect';
import { getPriceTemplate } from '../data/mockData';

export default function PriceItem({ item }) {
  const isUp = item.direction === 'up';
  const sign = isUp ? '+' : '';
  const searchTemplate = getPriceTemplate(item.keyword, item.direction, item.change_rate);

  return (
    <li
      className="keyword-row flex items-center gap-3 px-4 py-3 cursor-pointer border-b border-gray-100 last:border-0 transition-colors"
      onClick={() =>
        handleKeywordClick({
          keyword: item.keyword,
          tab: 'price',
          rank: item.rank,
          searchTemplate,
        })
      }
    >
      {/* 순위 */}
      <span className="w-6 text-center text-sm font-bold text-gray-500">
        {item.rank}
      </span>

      {/* 방향 */}
      <span className={`w-8 text-center text-sm font-bold ${isUp ? 'text-red-500' : 'text-blue-500'}`}>
        {isUp ? '↑' : '↓'}
      </span>

      {/* 식자재명 */}
      <span className="flex-1 font-medium text-gray-900">{item.keyword}</span>

      {/* 변동률 */}
      <span className={`text-sm font-bold w-16 text-right ${isUp ? 'text-red-500' : 'text-blue-500'}`}>
        {sign}{item.change_rate.toFixed(1)}%
      </span>

      {/* 오늘 도매가 */}
      <span className="text-sm text-gray-500 w-28 text-right">
        ₩{item.today_price.toLocaleString()}/{item.unit}
      </span>
    </li>
  );
}
