-- =============================================
-- 푸드랭크 Supabase DB 스키마
-- Supabase 대시보드 > SQL Editor 에서 전체 실행
-- =============================================

-- 1. 메뉴·브랜드 트렌드 키워드
CREATE TABLE IF NOT EXISTS keyword_trends (
  id              SERIAL PRIMARY KEY,
  keyword         TEXT NOT NULL,
  tab             TEXT NOT NULL          CHECK (tab IN ('menu', 'brand')),
  rank            INT NOT NULL,
  score           FLOAT NOT NULL,
  prev_rank       INT,
  trend_direction TEXT                   CHECK (trend_direction IN ('up_up', 'up', 'stay', 'down', 'new')),
  source_scores   JSONB,
  source_count    INT,
  search_template TEXT,
  collected_at    TIMESTAMPTZ NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 물가 트렌드 (KAMIS)
CREATE TABLE IF NOT EXISTS price_trends (
  id              SERIAL PRIMARY KEY,
  item_name       TEXT NOT NULL,
  rank            INT NOT NULL,
  today_price     INT NOT NULL,
  yesterday_price INT NOT NULL,
  change_rate     FLOAT NOT NULL,
  direction       TEXT NOT NULL          CHECK (direction IN ('up', 'down')),
  search_template TEXT,
  collected_at    TIMESTAMPTZ NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 브랜드 DB
CREATE TABLE IF NOT EXISTS brand_db (
  id              SERIAL PRIMARY KEY,
  brand_name      TEXT NOT NULL UNIQUE,
  category        TEXT,
  peak_rank       INT,
  franchise_count INT,
  first_appeared  TIMESTAMPTZ,
  contact_info    TEXT,
  is_ad_verified  BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 클릭 로그 (익명)
CREATE TABLE IF NOT EXISTS keyword_click_log (
  id              SERIAL PRIMARY KEY,
  keyword         TEXT NOT NULL,
  tab             TEXT NOT NULL,
  rank            INT,
  session_hash    TEXT,
  clicked_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 검색어 템플릿
CREATE TABLE IF NOT EXISTS search_templates (
  id            SERIAL PRIMARY KEY,
  keyword       TEXT NOT NULL,
  tab           TEXT NOT NULL          CHECK (tab IN ('menu', 'brand', 'price')),
  template      TEXT NOT NULL,
  is_active     BOOLEAN DEFAULT TRUE,
  is_verified   BOOLEAN DEFAULT FALSE,
  ctr_rate      FLOAT,
  last_verified DATE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (keyword, tab)
);

-- =============================================
-- RLS (Row Level Security) 설정
-- =============================================

ALTER TABLE keyword_trends    ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_trends      ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_db          ENABLE ROW LEVEL SECURITY;
ALTER TABLE keyword_click_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_templates  ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public read" ON keyword_trends    FOR SELECT USING (true);
CREATE POLICY "public read" ON price_trends      FOR SELECT USING (true);
CREATE POLICY "public read" ON brand_db          FOR SELECT USING (true);
CREATE POLICY "public read" ON search_templates  FOR SELECT USING (true);
CREATE POLICY "server insert" ON keyword_click_log FOR INSERT WITH CHECK (true);

-- =============================================
-- 초기 데모 데이터 (실제 수집 전 UI 확인용)
-- =============================================

INSERT INTO keyword_trends (keyword, tab, rank, score, prev_rank, trend_direction, source_count, search_template, collected_at) VALUES
('마라탕',        'menu', 1,  77.2, 3,    'up_up', 4, '마라탕 유행하는 이유 2025',        NOW()),
('편의점 도시락', 'menu', 2,  71.5, 2,    'stay',  3, '편의점 도시락 트렌드 2025',        NOW()),
('무한리필 고기', 'menu', 3,  68.3, 4,    'up',    3, '무한리필 고기 인기 이유 2025',     NOW()),
('버블티',        'menu', 4,  62.1, 3,    'down',  2, '버블티 유행하는 이유 2025',        NOW()),
('한식 뷔페',     'menu', 5,  58.4, 6,    'up',    2, '한식뷔페 인기 이유 2025',          NOW()),
('스몰비어',      'menu', 6,  54.7, NULL, 'new',   2, '스몰비어 트렌드 2025',             NOW()),
('마라샹궈',      'menu', 7,  51.2, 7,    'stay',  1, '마라샹궈 유행하는 이유 2025',      NOW()),
('파스타',        'menu', 8,  47.8, 7,    'down',  1, '파스타 인기 이유 2025',            NOW()),
('초밥',          'menu', 9,  44.3, 9,    'stay',  1, '초밥 트렌드 2025',                NOW()),
('로제떡볶이',    'menu', 10, 41.0, 11,   'up',    1, '로제떡볶이 유행하는 이유 2025',    NOW()),
('빽다방',        'brand', 1,  79.5, 3,    'up_up', 4, '빽다방 인기 이유 2025',           NOW()),
('맘스터치',      'brand', 2,  73.2, 3,    'up',    3, '맘스터치 인기 이유 2025',         NOW()),
('교촌치킨',      'brand', 3,  70.1, 3,    'stay',  3, '교촌치킨 인기 이유 2025',         NOW()),
('컴포즈커피',    'brand', 4,  65.8, 6,    'up_up', 2, '컴포즈커피 인기 이유 2025',       NOW()),
('노브랜드버거',  'brand', 5,  61.3, 6,    'up',    2, '노브랜드버거 인기 이유 2025',     NOW()),
('고피자',        'brand', 6,  57.4, NULL, 'new',   2, '고피자 인기 이유 2025',           NOW()),
('메가MGC커피',   'brand', 7,  53.2, 7,    'stay',  1, '메가MGC커피 인기 이유 2025',      NOW()),
('청년다방',      'brand', 8,  49.7, 7,    'down',  1, '청년다방 인기 이유 2025',         NOW()),
('투썸플레이스',  'brand', 9,  46.1, 9,    'stay',  1, '투썸플레이스 인기 이유 2025',     NOW()),
('할리스',        'brand', 10, 42.8, 11,   'up',    1, '할리스 인기 이유 2025',           NOW());

INSERT INTO price_trends (item_name, rank, today_price, yesterday_price, change_rate, direction, search_template, collected_at) VALUES
('대파',    1,  2100,  1554,  35.2,  'up',   '대파 가격 급등 이유 오늘',     NOW()),
('상추',    2,  4500,  3496,  28.7,  'up',   '상추 가격 오늘 전망',          NOW()),
('고추',    3,  15000, 19254, -22.1, 'down', '고추 가격 급락 이유',          NOW()),
('양파',    4,  890,   1092,  -18.5, 'down', '양파 가격 급락 이유',          NOW()),
('양배추',  5,  3400,  2838,  19.8,  'up',   '양배추 가격 오늘 전망',        NOW()),
('달걀',    6,  3200,  2849,  12.3,  'up',   '달걀 가격 오늘 전망',          NOW()),
('돼지고기', 7, 12800, 11808, 8.4,   'up',   '돼지고기 가격 오늘 전망',      NOW()),
('감자',    8,  2100,  2450,  -14.3, 'down', '감자 도매가 시세 오늘',        NOW()),
('두부',    9,  1800,  1695,  6.2,   'up',   '두부 가격 오늘 전망',          NOW()),
('마늘',    10, 8200,  9080,  -9.7,  'down', '마늘 도매가 시세 오늘',        NOW());
