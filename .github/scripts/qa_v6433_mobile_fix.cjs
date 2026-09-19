const { chromium } = require('playwright');
const fs = require('fs');

const BASE = 'http://127.0.0.1:4173';
const OUT = '/tmp/v6433-evidence';
fs.mkdirSync(OUT, { recursive: true });
function assert(cond, msg) { if (!cond) throw new Error(msg); }

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const route of ['/online/', '/en/online/']) {
      for (const width of [390, 430, 640]) {
        const context = await browser.newContext({ viewport: { width, height: 900 } });
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', e => errors.push(String(e)));
        const res = await page.goto(BASE + route, { waitUntil: 'networkidle', timeout: 20000 });
        assert(res && res.ok(), `${route} ${width}: HTTP failure`);

        const figure = page.locator('.app-screen--plan');
        await figure.scrollIntoViewIfNeeded();
        await page.waitForFunction(() => {
          const img = document.querySelector('.app-screen--plan img');
          return !!img && img.complete && img.naturalWidth === 760 && img.naturalHeight === 387;
        }, null, { timeout: 10000 });
        await page.waitForTimeout(120);

        const result = await page.evaluate(() => {
          const figure = document.querySelector('.app-screen--plan');
          const img = figure && figure.querySelector('img');
          const stage = document.querySelector('.app-story-stage');
          const doc = document.documentElement;
          if (!figure || !img || !stage) return { missing: true };
          const fr = figure.getBoundingClientRect();
          const ir = img.getBoundingClientRect();
          return {
            missing: false,
            figureHeight: fr.height,
            imageHeight: ir.height,
            gap: fr.height - ir.height,
            pageOverflow: doc.scrollWidth - doc.clientWidth,
            alignItems: getComputedStyle(stage).alignItems,
            alignSelf: getComputedStyle(figure).alignSelf,
            complete: img.complete,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight,
          };
        });
        assert(!result.missing, `${route} ${width}: plan card missing`);
        assert(result.complete && result.naturalWidth === 760 && result.naturalHeight === 387, `${route} ${width}: real plan image not loaded`);
        assert(Math.abs(result.gap) <= 2, `${route} ${width}: empty card tail ${result.gap}px`);
        assert(result.pageOverflow <= 2, `${route} ${width}: page overflow ${result.pageOverflow}px`);
        assert(result.alignItems === 'start', `${route} ${width}: rail does not align items to start`);
        assert(errors.length === 0, `${route} ${width}: page errors ${errors.join(' | ')}`);

        if (route === '/online/' && width === 390) {
          await page.locator('.app-story-section').screenshot({ path: `${OUT}/online-mobile-loaded-section.png` });
        }
        console.log(JSON.stringify({ route, width, ...result }));
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
})().catch(err => { console.error(err.stack || err); process.exit(1); });
