import { Html, Head, Main, NextScript } from 'next/document';

const GTM_ID = process.env.NEXT_PUBLIC_GTM_ID;

export default function Document() {
  return (
    <Html lang="ko">
      <Head>
        {GTM_ID && (
          <>
            {/* Consent Mode v2 기본값 + GTM 로드 */}
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  window.dataLayer = window.dataLayer || [];
                  window.dataLayer.push({
                    'gtm.start': new Date().getTime(),
                    event: 'gtm.js',
                    analytics_storage: 'denied',
                    ad_storage: 'denied',
                  });
                `,
              }}
            />
            <script
              async
              src={`https://www.googletagmanager.com/gtm.js?id=${GTM_ID}`}
            />
          </>
        )}
      </Head>
      <body>
        {GTM_ID && (
          <noscript>
            <iframe
              src={`https://www.googletagmanager.com/ns.html?id=${GTM_ID}`}
              height="0"
              width="0"
              style={{ display: 'none', visibility: 'hidden' }}
            />
          </noscript>
        )}
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
