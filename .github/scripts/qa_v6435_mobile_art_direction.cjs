const { chromium } = require('playwright');
const fs = require('fs');

const base = 'http://127.0.0.1:4173';
const evidence = '/tmp/v6435-evidence';
fs.mkdirSync(evidence, { recursive: true });

const coreRoutes = [
  '/', '/diagnostico-iri/', '/metodo/', '/presencial/', '/hibrido/', '/online/', '/sobre-iberfit/', '/contacto/',
  '/en/', '/en/iri-assessment/', '/en/method/', '/en/in-person/', '/en/hybrid/', '/en/online/', '/en/about/', '/en/contact/'
];
const allRoutes = [
  '/', '/diagnostico-iri/', '/metodo/', '/presencial/', '/hibrido/', '/online/', '/sobre-iberfit/', '/contacto/', '/privacidad/',
  '/entrenador-personal-las-condes/', '/entrenador-personal-vitacura/', '/entrenamiento-personal-providencia/', '/entrenador-personal-lo-barnechea/', '/personal-trainer-nunoa/', '/entrenador-personal-la-reina/', '/entrenador-personal-penalolen/',
  '/en/', '/en/iri-assessment/', '/en/method/', '/en/in-person/', '/en/hybrid/', '/en/online/', '/en/about/', '/en/contact/', '/en/privacy/',
  '/en/personal-trainer-las-condes/', '/en/personal-trainer-vitacura/', '/en/personal-training-providencia/', '/en/personal-trainer-lo-barnechea/', '/en/personal-trainer-nunoa/', '/en/personal-trainer-la-reina/', '/en/personal-trainer-penalolen/'
];
if (allRoutes.length !== 32) throw new Error(`Expected 32 sitemap routes, got ${allRoutes.length}`);

const focusedRails = [
  ['/', '.evidence-process-media--v6435', 3],
  ['/', '.system-rail', 4],
  ['/metodo/', '.method-cycle', 6],
  ['/presencial/', '.week-flow', 3],
  ['/online/', '.continuity-rail', 4],
  ['/sobre-iberfit/', '.brand-journey--editorial', 4],
  ['/en/', '.evidence-process-media--v6435', 3],
  ['/en/', '.system-rail', 4],
  ['/en/method/', '.method-cycle', 6],
  ['/en/in-person/', '.week-flow', 3],
  ['/en/online/', '.continuity-rail', 4],
  ['/en/about/', '.brand-journey--editorial', 4],
];

async function waitImages(page, selector = 'body') {
  await page.locator(selector).scrollIntoViewIfNeeded().catch(() => {});
  await page.waitForTimeout(120);
  await page.evaluate((sel) => Promise.all([...document.querySelectorAll(`${sel} img`)].map(img => img.complete && img.naturalWidth ? true : new Promise(resolve => { img.addEventListener('load', resolve, {once:true}); img.addEventListener('error', resolve, {once:true}); }))), selector);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const errors = [];

  for (const viewport of [{name:'mobile', width:390, height:844}, {name:'desktop', width:1440, height:1000}]) {
    const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, deviceScaleFactor: 1 });
    for (const route of allRoutes) {
      const page = await context.newPage();
      const pageErrors = [];
      page.on('pageerror', e => pageErrors.push(`pageerror:${e.message}`));
      page.on('console', msg => { if (msg.type() === 'error') pageErrors.push(`console:${msg.text()}`); });
      const response = await page.goto(base + route, { waitUntil: 'domcontentloaded', timeout: 30000 });
      if (!response || response.status() !== 200) errors.push(`${viewport.name} ${route} status ${response && response.status()}`);
      await page.waitForTimeout(80);
      const geom = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
      if (geom.sw > geom.cw + 2) errors.push(`${viewport.name} ${route} page overflow ${geom.sw}-${geom.cw}`);
      const cssCount = await page.locator('link[href="/assets/mobile.v6435.css"]').count();
      if (cssCount !== 1) errors.push(`${viewport.name} ${route} mobile css count ${cssCount}`);
      if (pageErrors.length) errors.push(`${viewport.name} ${route} ${pageErrors.join(' | ')}`);
      await page.close();
    }
    await context.close();
  }

  const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  for (const [route, selector, expectedChildren] of focusedRails) {
    const page = await mobile.newPage();
    await page.goto(base + route, { waitUntil: 'domcontentloaded' });
    const rail = page.locator(selector);
    if (await rail.count() !== 1) {
      errors.push(`rail missing ${route} ${selector}`);
      await page.close();
      continue;
    }
    await rail.scrollIntoViewIfNeeded();
    await waitImages(page, selector);
    const before = await rail.evaluate((el) => ({
      scrollWidth: el.scrollWidth,
      clientWidth: el.clientWidth,
      scrollLeft: el.scrollLeft,
      children: el.children.length,
      snap: getComputedStyle(el).scrollSnapType,
      flow: getComputedStyle(el).gridAutoFlow,
      firstWidth: el.children[0]?.getBoundingClientRect().width || 0,
      secondLeft: el.children[1]?.getBoundingClientRect().left || 0,
      railRight: el.getBoundingClientRect().right,
    }));
    if (before.children !== expectedChildren) errors.push(`rail child count ${route} ${selector}: ${before.children}/${expectedChildren}`);
    if (before.scrollWidth <= before.clientWidth + 24) errors.push(`rail not horizontally scrollable ${route} ${selector}`);
    if (!before.snap.includes('x')) errors.push(`rail snap missing ${route} ${selector}: ${before.snap}`);
    if (before.flow !== 'column') errors.push(`rail auto flow ${route} ${selector}: ${before.flow}`);
    if (!(before.secondLeft < before.railRight && before.secondLeft > 0)) errors.push(`next-card peek missing ${route} ${selector}`);
    await rail.evaluate(el => { el.scrollLeft = Math.min(el.scrollWidth - el.clientWidth, Math.max(180, el.clientWidth * .72)); });
    await page.waitForTimeout(120);
    const after = await rail.evaluate(el => el.scrollLeft);
    if (after < 20) errors.push(`rail did not scroll ${route} ${selector}`);
    await page.close();
  }

  for (const [route, name] of [['/', 'home-es'], ['/en/', 'home-en'], ['/metodo/', 'method-es'], ['/online/', 'online-es'], ['/presencial/', 'inperson-es'], ['/sobre-iberfit/', 'about-es']]) {
    const page = await mobile.newPage();
    await page.goto(base + route, { waitUntil: 'networkidle' });
    await page.evaluate(async () => {
      const imgs = [...document.images];
      for (const img of imgs) {
        if (img.loading === 'lazy') img.scrollIntoView({ block: 'center' });
      }
      await new Promise(r => setTimeout(r, 180));
      window.scrollTo(0,0);
    });
    await page.screenshot({ path: `${evidence}/${name}-mobile.png`, fullPage: true });
    await page.close();
  }
  await mobile.close();

  const desktop = await browser.newContext({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  for (const [route, name] of [['/', 'home-es'], ['/en/', 'home-en']]) {
    const page = await desktop.newPage();
    await page.goto(base + route, { waitUntil: 'networkidle' });
    await page.screenshot({ path: `${evidence}/${name}-desktop.png`, fullPage: true });
    await page.close();
  }
  await desktop.close();

  const homeMobile = await browser.newContext({ viewport: { width:390, height:844 }, deviceScaleFactor: 1 });
  const hp = await homeMobile.newPage();
  await hp.goto(base + '/', { waitUntil:'domcontentloaded' });
  const hero = await hp.locator('.editorial-hero-media img').evaluate(img => ({w:img.getBoundingClientRect().width,h:img.getBoundingClientRect().height,nw:img.naturalWidth,nh:img.naturalHeight}));
  if (hero.nw <= 0 || hero.nh <= 0) errors.push('home hero image failed to load');
  const ratio = hero.w / hero.h;
  if (ratio < 1.20 || ratio > 1.30) errors.push(`home mobile hero ratio unexpected ${ratio.toFixed(3)}`);
  await hp.close();
  await homeMobile.close();

  await browser.close();
  if (errors.length) {
    console.error(JSON.stringify({ ok:false, errors }, null, 2));
    process.exit(1);
  }
  console.log(JSON.stringify({ ok:true, routes:allRoutes.length, focusedRails:focusedRails.length, evidenceDir:evidence }, null, 2));
})().catch(err => { console.error(err); process.exit(1); });
