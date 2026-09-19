const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const root = path.resolve('candidate/v628');
const files = [];
(function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    const file = path.join(dir, name);
    const stat = fs.statSync(file);
    if (stat.isDirectory()) walk(file);
    else if (name.endsWith('.html')) files.push(file);
  }
})(root);

const routeOf = file => {
  const rel = path.relative(root, file).replaceAll('\\', '/');
  if (rel === 'index.html') return '/';
  if (rel === '404.html') return '/404.html';
  return '/' + rel.replace(/index\.html$/, '');
};

(async () => {
  if (files.length !== 33) throw new Error(`EXPECTED_33_HTML_GOT_${files.length}`);
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(String(error)));

  for (const file of files.sort()) {
    const route = routeOf(file);
    const response = await page.goto('http://127.0.0.1:4173' + route, { waitUntil: 'domcontentloaded' });
    if (!response?.ok()) throw new Error(`HTTP_${response?.status()}_${route}`);
    const state = await page.evaluate(() => ({
      sheet: document.querySelectorAll('link[href="/assets/a11y.v6431.css"]').length,
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      versionedAnalytics: document.querySelectorAll('script[src="/assets/analytics.v643.js"]').length,
      hardeningJs: document.querySelectorAll('script[src="/assets/hardening.v630.js"]').length,
    }));
    if (state.sheet !== 1) throw new Error(`A11Y_STYLESHEET_${route}_${state.sheet}`);
    if (state.overflow > 2) throw new Error(`OVERFLOW_${route}_${state.overflow}`);
    if (state.versionedAnalytics !== 1) throw new Error(`ANALYTICS_REGRESSION_${route}_${state.versionedAnalytics}`);
    if (state.hardeningJs !== 0) throw new Error(`HARDENING_JS_REGRESSION_${route}`);
  }

  await page.goto('http://127.0.0.1:4173/', { waitUntil: 'domcontentloaded' });
  const colors = await page.evaluate(() => {
    const colorOf = selector => {
      const el = document.querySelector(selector);
      if (!el) throw new Error(`MISSING_${selector}`);
      return getComputedStyle(el).color;
    };
    return {
      heroEyebrow: colorOf('.editorial-hero .eyebrow'),
      evidenceKicker: colorOf('.evidence-process-section .kicker'),
      goldTextVar: getComputedStyle(document.documentElement).getPropertyValue('--gold-text').trim(),
    };
  });
  if (colors.goldTextVar.toLowerCase() !== '#806216') throw new Error(`GOLD_TEXT_VAR_${colors.goldTextVar}`);
  if (colors.heroEyebrow !== 'rgb(128, 98, 22)') throw new Error(`HERO_EYEBROW_COLOR_${colors.heroEyebrow}`);
  if (colors.evidenceKicker !== 'rgb(217, 181, 104)') throw new Error(`DARK_KICKER_COLOR_${colors.evidenceKicker}`);

  if (pageErrors.length) throw new Error('PAGE_ERRORS_' + pageErrors.join(' | '));
  await browser.close();
  console.log(JSON.stringify({ routes: files.length, overflow: 'ok', pageErrors: 0, colors }));
})().catch(error => {
  console.error(error);
  process.exit(1);
});
