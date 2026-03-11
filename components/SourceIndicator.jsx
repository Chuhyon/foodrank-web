// 채널 신뢰도 표시 — ●●●●○ (5칸 중 source_count개 채움)
// MAX=5, 채널은 최대 4개 → 만점 미표시로 여백 제공
export default function SourceIndicator({ count }) {
  const MAX = 5;
  return (
    <span className="text-sm tracking-wider" title={`${count}개 채널 집계`}>
      {Array.from({ length: MAX }, (_, i) => (
        <span key={i} className={i < count ? 'dot-filled' : 'dot-empty'}>
          {i < count ? '●' : '○'}
        </span>
      ))}
    </span>
  );
}
