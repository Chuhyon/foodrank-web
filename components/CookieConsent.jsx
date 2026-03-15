import { useEffect, useState } from 'react';
import { grantAllConsent, grantEssentialOnly, getSavedConsent } from '../utils/analytics';

export default function CookieConsent() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // 이미 동의한 경우 표시 안 함
    if (!getSavedConsent()) {
      setVisible(true);
    }
  }, []);

  if (!visible) return null;

  function handleAll() {
    grantAllConsent();
    setVisible(false);
  }

  function handleEssential() {
    grantEssentialOnly();
    setVisible(false);
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-lg">
      <div className="max-w-lg mx-auto px-4 py-3 flex flex-col gap-2">
        <p className="text-xs text-gray-600">
          이 사이트는 서비스 개선을 위해 쿠키를 사용합니다.
          <span className="text-gray-400 ml-1">(개인정보보호법 준수)</span>
        </p>
        <div className="flex gap-2 justify-end">
          <button
            onClick={handleEssential}
            className="px-3 py-1.5 text-xs text-gray-500 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
          >
            필수만
          </button>
          <button
            onClick={handleAll}
            className="px-3 py-1.5 text-xs text-white bg-orange-500 rounded hover:bg-orange-600 transition-colors"
          >
            전체 동의
          </button>
        </div>
      </div>
    </div>
  );
}
