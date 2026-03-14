import { supabase } from '../../lib/supabase';

export default async function handler(req, res) {
  const results = {};

  // 1. 환경변수 확인
  results.env = {
    url: process.env.NEXT_PUBLIC_SUPABASE_URL ? '✅ 설정됨' : '❌ 없음',
    anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? '✅ 설정됨' : '❌ 없음',
  };

  // 2. keyword_trends 테이블 쿼리
  const { data: menuData, error: menuError } = await supabase
    .from('keyword_trends')
    .select('keyword, rank, tab')
    .eq('tab', 'menu')
    .limit(3);

  results.keyword_trends = {
    data: menuData,
    error: menuError?.message ?? null,
    count: menuData?.length ?? 0,
  };

  // 3. price_trends 테이블 쿼리
  const { data: priceData, error: priceError } = await supabase
    .from('price_trends')
    .select('item_name, rank')
    .limit(3);

  results.price_trends = {
    data: priceData,
    error: priceError?.message ?? null,
    count: priceData?.length ?? 0,
  };

  res.status(200).json(results);
}
