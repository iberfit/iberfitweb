const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve('candidate/v628');
const BASE = 'http://127.0.0.1:4173';
const OUT = '/tmp/v6433-evidence';
fs.mkdirSync(OUT, { recursive: true });

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((ent) => {
    const full = path.join(dir, ent.name);
    return ent.isDirectory() ? walk(full) : [full];
  });
}
function routeFor(file) {
  let rel = path.relative(ROOT, file).replace(/\\/g, '/');
  if (rel === 'index.html') return '/';
  if (rel.endsWith('/index.html')) return '/' + rel.slice(0, -'index.html'.length);
  return '/' + rel;
}
function assert(cond, msg) { if (!cond) throw new Error(msg); }

const htmlFiles = walk(ROOT).filter((f) => f.endsWith('.html'));
assert(htmlFiles.length === 33, `Expected 33 HTML files, got ${htmlFiles.length}`);
const ctaRoutes = htmlFiles.filter((f) => fs.readFileSync(f, 'utf8').includes('cta-panel-inner')).map(routeFor);
assert(ctaRoutes.length >= 20, `Expected broad CTA coverage, got ${ctaRoutes.length}`);

(async () => {
  const browser = await chromium.launch({ headless: true });
  const report = { htmlRoutes: htmlFiles.length, ctaRoutes: ctaRoutes.length, checks: [] };
  try {
    for (const viewport of [
      { name: 'desktop', width: 1440, height: 1000 },
      { name: 'mobile', width: 390, height: 844 },
    ]) {
      const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height } });
      const page = await context.newPage();
      let currentErrors = [];
      page.on('pageerror', (err) => currentErrors.push(String(err)));

      for (const route of ctaRoutes) {
        currentErrors = [];
        const res = await page.goto(BASE + route, { waitUntil: 'networkidle', timeout: 20000 });
        assert(res && res.ok(), `${viewport.name} ${route}: HTTP failure`);
        await page.waitForTimeout(50);
        const result = await page.evaluate(() => {
          const doc = document.documentElement;
          const panel = document.querySelector('.cta-panel-inner');
          const copy = panel && panel.querySelector(':scope > div');
          const button = panel && panel.querySelector(':scope > .btn');
          const heading = panel && panel.querySelector('h2');
          if (!panel || !copy || !button || !heading) return { missing: true };
          const pr = panel.getBoundingClientRect();
          const cr = copy.getBoundingClientRect();
          const br = button.getBoundingClientRect();
          const style = getComputedStyle(panel);
          const hs = getComputedStyle(heading);
          return {
            missing: false,
            overflow: doc.scrollWidth - doc.clientWidth,
            display: style.display,
            panel: { left: pr.left, right: pr.right, width: pr.width },
            copy: { left: cr.left, width: cr.width },
            button: { left: br.left, right: br.right, width: br.width, top: br.top },
            headingFont: parseFloat(hs.fontSize),
          };
        });
        assert(!result.missing, `${viewport.name} ${route}: CTA structure missing`);
        assert(result.overflow <= 2, `${viewport.name} ${route}: page overflow ${result.overflow}px`);
        assert(result.display === 'grid', `${viewport.name} ${route}: CTA is not grid`);
        assert(result.panel.left >= -1 && result.panel.right <= viewport.width + 1, `${viewport.name} ${route}: CTA outside viewport`);
        assert(Math.abs(result.button.left - result.copy.left) <= 3, `${viewport.name} ${route}: CTA button detached from copy`);
        assert(result.headingFont <= 58, `${viewport.name} ${route}: CTA heading still oversized (${result.headingFont}px)`);
        if (viewport.name === 'mobile') {
          assert(result.button.width >= result.copy.width * 0.95, `${route}: mobile CTA button is not integrated/full width`);
        }
        assert(currentErrors.length === 0, `${viewport.name} ${route}: page errors ${currentErrors.join(' | ')}`);
        report.checks.push({ viewport: viewport.name, route, overflow: result.overflow, headingFont: result.headingFont });
      }
      await context.close();
    }

    // Focused Online proof: corrected crop, safe composition and no intermediate-width clipping.
    for (const width of [1440, 1180, 1024, 820, 390]) {
      const context = await browser.newContext({ viewport: { width, height: width <= 500 ? 844 : 1000 } });
      const page = await context.newPage();
      await page.goto(BASE + '/online/', { waitUntil: 'networkidle' });
      const online = await page.evaluate(() => {
        const img = document.querySelector('.app-screen--plan img');
        const section = document.querySelector('.app-story-section');
        const story = document.querySelector('.app-story');
        const stage = document.querySelector('.app-story-stage');
        const copy = document.querySelector('.app-story-copy');
        const doc = document.documentElement;
        const sr = section.getBoundingClientRect();
        const cr = copy.getBoundingClientRect();
        return {
          src: img.getAttribute('src'), naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight,
          sectionLeft: sr.left, sectionRight: sr.right, copyLeft: cr.left,
          pageOverflow: doc.scrollWidth - doc.clientWidth,
          stageOverflow: stage.scrollWidth - stage.clientWidth,
          columns: getComputedStyle(story).gridTemplateColumns,
        };
      });
      assert(online.src === '/assets/app-online-plan-v6433.webp', `online ${width}: wrong plan asset`);
      assert(online.naturalWidth === 760 && online.naturalHeight === 387, `online ${width}: unexpected plan dimensions`);
      assert(online.pageOverflow <= 2, `online ${width}: page overflow ${online.pageOverflow}`);
      assert(online.copyLeft >= -1, `online ${width}: copy clipped on the left`);
      assert(online.sectionLeft >= -1 && online.sectionRight <= width + 1, `online ${width}: section outside viewport`);
      if (width > 640) assert(online.stageOverflow <= 2, `online ${width}: stage overflow ${online.stageOverflow}`);
      await context.close();
    }

    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();
    await page.goto(BASE + '/sobre-iberfit/', { waitUntil: 'networkidle' });
    const bodyEs = await page.locator('body').innerText();
    assert(bodyEs.includes('pasión por el entrenamiento') && bodyEs.includes('inquietud constante por la salud'), 'Spanish origin rewrite missing');
    await page.goto(BASE + '/en/about/', { waitUntil: 'networkidle' });
    const bodyEn = await page.locator('body').innerText();
    assert(bodyEn.includes('passion for training') && bodyEn.includes('curiosity about health'), 'English origin rewrite missing');
    await context.close();

    const shots = [
      ['/online/', 'online'], ['/hibrido/', 'hibrido'], ['/sobre-iberfit/', 'sobre-iberfit'], ['/metodo/', 'metodo']
    ];
    for (const viewport of [
      { name: 'desktop', width: 1440, height: 1000 },
      { name: 'mobile', width: 390, height: 844 },
    ]) {
      const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height } });
      const page = await context.newPage();
      for (const [route, name] of shots) {
        await page.goto(BASE + route, { waitUntil: 'networkidle' });
        await page.screenshot({ path: `${OUT}/${name}-${viewport.name}.png`, fullPage: true });
      }
      await context.close();
    }

    fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify({ ok: true, htmlRoutes: report.htmlRoutes, ctaRoutes: report.ctaRoutes, checks: report.checks.length }));
  } finally {
    await browser.close();
  }
})().catch((err) => { console.error(err.stack || err); process.exit(1); });
