const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const base = 'http://127.0.0.1:4173';
const routes = [
  { path: '/online/', expectedScreens: 3, marker: 'Tu entrenamiento no vive en un PDF.' },
  { path: '/hibrido/', expectedScreens: 1, marker: 'Lo presencial continúa cuando te vas.' },
  { path: '/en/online/', expectedScreens: 3, marker: 'Your training does not live in a PDF.' },
  { path: '/en/hybrid/', expectedScreens: 1, marker: 'In-person work continues after you leave.' },
];
const viewports = [
  { name: 'desktop', width: 1440, height: 1050 },
  { name: 'tablet', width: 820, height: 1080 },
  { name: 'mobile', width: 390, height: 844 },
];
const evidenceDir = '/tmp/v6432-evidence';
fs.mkdirSync(evidenceDir, { recursive: true });

function fail(message) {
  throw new Error(message);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const report = [];
  try {
    for (const viewport of viewports) {
      const context = await browser.newContext({ viewport });
      for (const route of routes) {
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', err => errors.push(`pageerror: ${err.message}`));
        page.on('console', msg => {
          if (msg.type() === 'error') errors.push(`console: ${msg.text()}`);
        });
        const response = await page.goto(base + route.path, { waitUntil: 'networkidle' });
        if (!response || response.status() !== 200) fail(`${route.path} ${viewport.name}: HTTP ${response && response.status()}`);
        await page.locator('body').waitFor({ state: 'visible' });

        const result = await page.evaluate(({ marker, expectedScreens }) => {
          const html = document.documentElement;
          const visualLinks = [...document.querySelectorAll('link[rel="stylesheet"]')].filter(x => x.getAttribute('href') === '/assets/visual.v6432.css').length;
          const special = [...document.querySelectorAll('img[src^="/assets/app-online-"], img[src="/assets/app-hybrid-feedback.webp"]')];
          const badImages = [...document.images].filter(img => !img.complete || img.naturalWidth < 1).map(img => img.getAttribute('src'));
          const bodyText = document.body.innerText;
          const aeoCount = document.querySelectorAll('.answer-section [data-aeo-answer]').length;
          const overflow = Math.max(document.body.scrollWidth, html.scrollWidth) - window.innerWidth;
          const appSection = document.querySelector('.app-story-section, .hybrid-continuity-section');
          return {
            visualLinks,
            specialCount: special.length,
            specialSources: special.map(img => img.getAttribute('src')),
            badImages,
            marker: bodyText.includes(marker),
            aeoCount,
            overflow,
            hasAppSection: Boolean(appSection),
            hasQaText: /Cliente QA|Cliente Prueba IBERFIT|Coach QA/i.test(bodyText),
          };
        }, { marker: route.marker, expectedScreens: route.expectedScreens });

        if (result.visualLinks !== 1) fail(`${route.path} ${viewport.name}: visual CSS link count ${result.visualLinks}`);
        if (result.specialCount !== route.expectedScreens) fail(`${route.path} ${viewport.name}: expected ${route.expectedScreens} app screens, got ${result.specialCount}`);
        if (result.badImages.length) fail(`${route.path} ${viewport.name}: failed images ${result.badImages.join(', ')}`);
        if (!result.marker || !result.hasAppSection) fail(`${route.path} ${viewport.name}: visual story marker missing`);
        if (result.aeoCount < 4) fail(`${route.path} ${viewport.name}: AEO answers were lost`);
        if (result.overflow > 2) fail(`${route.path} ${viewport.name}: horizontal body overflow ${result.overflow}px`);
        if (result.hasQaText) fail(`${route.path} ${viewport.name}: QA identity leaked into rendered text`);
        if (errors.length) fail(`${route.path} ${viewport.name}: ${errors.join(' | ')}`);

        const safe = route.path.replace(/^\/+|\/+$/g, '').replace(/\//g, '-') || 'home';
        const shot = path.join(evidenceDir, `${safe}-${viewport.name}.png`);
        await page.screenshot({ path: shot, fullPage: true });
        report.push({ route: route.path, viewport: viewport.name, overflow: result.overflow, screens: result.specialSources, aeoCount: result.aeoCount });
        await page.close();
      }
      await context.close();
    }
  } finally {
    await browser.close();
  }
  fs.writeFileSync(path.join(evidenceDir, 'report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ ok: true, cases: report.length, report }, null, 2));
})().catch(err => {
  console.error(err.stack || err.message || err);
  process.exit(1);
});
