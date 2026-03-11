import Head from 'next/head';
import { useState } from 'react';
import KeywordItem from '../components/KeywordItem';
import PriceItem from '../components/PriceItem';
import { menuTrends, brandTrends, priceTrends, collectedAt } from '../data/mockData';

const TABS = [
  { id: 'menu',  label: '🍜 메뉴 트렌드' },
  { id: 'brand', label: '📈 급상승 브랜드' },
  { id: 'price', label: '💰 물가 주의보' },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState('menu');

  return (
    <>
      <Head>
        <title>푸드랭크 — 외식업 트렌드 실시간 순위</title>
        <meta
          name="description"
          content="인기 메뉴·급상승 브랜드·식자재 물가를 실시간으로 확인하세요. 외식업·프랜차이즈 종사자를 위한 트렌드 대시보드."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
            <h1 className="text-xl font-black text-orange-500">🔥 푸드랭크</h1>
            <span className="text-xs text-gray-400">
              데이터 기준: {collectedAt} 수집
            </span>
          </div>
        </header>

        {/* Tab Bar */}
        <nav className="bg-white border-b border-gray-200">
          <div className="max-w-lg mx-auto px-2 flex">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 py-3 text-sm font-medium transition-colors border-b-2 ${
                  activeTab === tab.id
                    ? 'border-orange-500 text-orange-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </nav>

        {/* Content */}
        <main className="flex-1 max-w-lg mx-auto w-full py-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">

            {/* 컬럼 헤더 */}
            {activeTab !== 'price' && (
              <div className="flex items-center gap-3 px-4 py-2 bg-gray-50 border-b border-gray-100 text-xs text-gray-400 font-medium">
                <span className="w-6 text-center">순위</span>
                <span className="w-8 text-center">변동</span>
                <span className="flex-1">키워드</span>
                <span>채널 신뢰도</span>
              </div>
            )}
            {activeTab === 'price' && (
              <div className="flex items-center gap-3 px-4 py-2 bg-gray-50 border-b border-gray-100 text-xs text-gray-400 font-medium">
                <span className="w-6 text-center">순위</span>
                <span className="w-8 text-center">방향</span>
                <span className="flex-1">식자재</span>
                <span className="w-16 text-right">변동률</span>
                <span className="w-28 text-right">오늘 도매가</span>
              </div>
            )}

            {/* 리스트 */}
            <ul>
              {activeTab === 'menu' &&
                menuTrends.map((item) => (
                  <KeywordItem key={item.rank} item={item} tab="menu" />
                ))}
              {activeTab === 'brand' &&
                brandTrends.map((item) => (
                  <KeywordItem key={item.rank} item={item} tab="brand" />
                ))}
              {activeTab === 'price' &&
                priceTrends.map((item) => (
                  <PriceItem key={item.rank} item={item} />
                ))}
            </ul>

            {/* 탭별 하단 안내 문구 */}
            {activeTab === 'brand' && (
              <p className="text-xs text-gray-400 text-center py-3 border-t border-gray-100">
                검색량 기준 순위입니다. 가맹점 수 기준이 아닙니다.
              </p>
            )}
            {activeTab === 'price' && (
              <p className="text-xs text-gray-400 text-center py-3 border-t border-gray-100">
                KAMIS(농수산식품유통공사) 도매가 기준 | 전일 대비
              </p>
            )}
          </div>

          {/* 클릭 안내 */}
          <p className="text-xs text-gray-400 text-center mt-3 px-4">
            키워드를 클릭하면 구글에서 AI 요약 정보를 바로 확인할 수 있습니다.
          </p>
        </main>

        {/* Footer */}
        <footer className="py-4 text-center text-xs text-gray-400 border-t border-gray-100 bg-white mt-4">
          <p>집계 채널: 네이버 · 구글 · 유튜브 · X</p>
          <p className="mt-1">© 2025 푸드랭크</p>
        </footer>
      </div>
    </>
  );
}
