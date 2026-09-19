const { chromium } = require('playwright');

const BASE = 'http://127.0.0.1:4173';
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
          };
        });
        assert(!result.missing, `${route} ${width}: plan card missing`);
        assert(Math.abs(result.gap) <= 2, `${route} ${width}: empty card tail ${result.gap}px`);
        assert(result.pageOverflow <= 2, `${route} ${width}: page overflow ${result.pageOverflow}px`);
        assert(result.alignItems === 'start', `${route} ${width}: rail does not align items to start`);
        assert(errors.length === 0, `${route} ${width}: page errors ${errors.join(' | ')}`);
        console.log(JSON.stringify({ route, width, ...result }));
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
})().catch(err => { console.error(err.stack || err); process.exit(1); });
