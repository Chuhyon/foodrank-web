import SourceIndicator from './SourceIndicator';
import { handleKeywordClick } from '../utils/searchConnect';

const TREND_LABELS = {
  up_up: { text: '↑↑', cls: 'trend-up-up' },
  up:    { text: '↑',  cls: 'trend-up' },
  stay:  { text: '→',  cls: 'trend-stay' },
  down:  { text: '↓',  cls: 'trend-down' },
  new:   { text: '🆕', cls: 'trend-new' },
};

export default function KeywordItem({ item, tab }) {
  const trend = TREND_LABELS[item.trend_direction] ?? TREND_LABELS.stay;

  return (
    <li
      className="keyword-row flex items-center gap-3 px-4 py-3 cursor-pointer border-b border-gray-100 last:border-0 transition-colors"
      onClick={() =>
        handleKeywordClick({
          keyword:       item.keyword,
          tab,
          rank:          item.rank,
          searchTemplate: item.search_template,
          trendDirection: item.trend_direction,
          sourceCount:    item.source_count,
        })
      }
    >
      {/* 순위 */}
      <span className="w-6 text-center text-sm font-bold text-gray-500">
        {item.rank}
      </span>

      {/* 변동 */}
      <span className={`w-8 text-center text-sm ${trend.cls}`}>
        {trend.text}
      </span>

      {/* 키워드 */}
      <span className="flex-1 font-medium text-gray-900">{item.keyword}</span>

      {/* 채널 신뢰도 */}
      <SourceIndicator count={item.source_count} />
    </li>
  );
}
