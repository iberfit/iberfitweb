const { chromium } = require('playwright');
const fs = require('fs');

const base = 'http://127.0.0.1:4173';
const evidence = '/tmp/v6435-polish-evidence';
fs.mkdirSync(evidence, { recursive: true });

const routes = [
  '/', '/diagnostico-iri/', '/metodo/', '/presencial/', '/hibrido/', '/online/', '/sobre-iberfit/', '/contacto/', '/privacidad/',
  '/entrenador-personal-las-condes/', '/entrenador-personal-vitacura/', '/entrenamiento-personal-providencia/', '/entrenador-personal-lo-barnechea/', '/personal-trainer-nunoa/', '/entrenador-personal-la-reina/', '/entrenador-personal-penalolen/',
  '/en/', '/en/iri-assessment/', '/en/method/', '/en/in-person/', '/en/hybrid/', '/en/online/', '/en/about/', '/en/contact/', '/en/privacy/',
  '/en/personal-trainer-las-condes/', '/en/personal-trainer-vitacura/', '/en/personal-training-providencia/', '/en/personal-trainer-lo-barnechea/', '/en/personal-trainer-nunoa/', '/en/personal-trainer-la-reina/', '/en/personal-trainer-penalolen/'
];
if (routes.length !== 32) throw new Error(`Expected 32 routes, got ${routes.length}`);

const rails = [
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

const railSelectors = [
  '.evidence-process-media--v6435', '.system-rail', '.method-cycle', '.week-flow',
  '.continuity-rail', '.brand-journey--editorial', '.app-story-stage'
].join(',');

async function loadLazyAndReset(page) {
  await page.evaluate(async (selector) => {
    const images = [...document.images];
    for (const img of images) {
      if (img.loading === 'lazy') img.scrollIntoView({block:'center', inline:'nearest'});
    }
    await new Promise(r => setTimeout(r, 220));
    document.querySelectorAll(selector).forEach(el => { el.scrollLeft = 0; });
    window.scrollTo(0, 0);
    await new Promise(r => setTimeout(r, 100));
  }, railSelectors);
}

(async () => {
  const browser = await chromium.launch({ headless:true });
  const errors = [];

  // Consent-first mobile experience at the narrow acceptance width.
  const consentContext = await browser.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:1 });
  const consentPage = await consentContext.newPage();
  consentPage.on('pageerror', e => errors.push(`consent pageerror:${e.message}`));
  await consentPage.goto(base + '/', {waitUntil:'networkidle'});
  const banner = consentPage.locator('.consent-banner');
  if (await banner.count() !== 1) errors.push('consent banner missing on fresh context');
  else {
    const metrics = await banner.evaluate(el => {
      const r = el.getBoundingClientRect();
      const buttons = [...el.querySelectorAll('button')].map(b => {
        const x = b.getBoundingClientRect();
        return {label:b.textContent.trim(), width:x.width, height:x.height, visible:!!(x.width && x.height)};
      });
      return {height:r.height, width:r.width, bottom:innerHeight-r.bottom, buttons};
    });
    if (metrics.height > 300) errors.push(`consent banner too tall: ${metrics.height}`);
    if (metrics.width > 380) errors.push(`consent banner too wide: ${metrics.width}`);
    if (metrics.buttons.length !== 4) errors.push(`consent actions ${metrics.buttons.length}/4`);
    for (const b of metrics.buttons) {
      if (!b.visible || b.height < 44) errors.push(`consent target too small: ${b.label} ${b.width}x${b.height}`);
    }
    const audience = consentPage.locator('[data-consent-audience]');
    const necessary = consentPage.locator('[data-consent-necessary]');
    const aBox = await audience.boundingBox();
    const nBox = await necessary.boundingBox();
    if (!aBox || !nBox || Math.abs(aBox.y-nBox.y) > 3) errors.push('audience/necessary are not sharing a compact row');
  }
  await consentPage.screenshot({path:`${evidence}/home-es-consent-390.png`, fullPage:false});

  // Preferences remain fully usable and fit in the viewport.
  await consentPage.locator('[data-consent-settings]').click();
  const dialog = consentPage.locator('.consent-dialog');
  if (await dialog.count() !== 1) errors.push('consent preferences dialog missing');
  else {
    const d = await dialog.boundingBox();
    if (!d || d.height > 820 || d.y < 8) errors.push(`consent dialog geometry ${JSON.stringify(d)}`);
    const close = consentPage.locator('.consent-close');
    const c = await close.boundingBox();
    if (!c || c.width < 44 || c.height < 44) errors.push(`consent close target ${JSON.stringify(c)}`);
    const activeClass = await consentPage.evaluate(() => document.activeElement?.className || '');
    if (!String(activeClass).includes('consent-close')) errors.push(`consent dialog initial focus ${activeClass}`);
  }
  await consentPage.keyboard.press('Escape');
  if (await consentPage.locator('.consent-modal').count()) errors.push('consent modal did not close on Escape');

  // Necessary-only is still explicit, persistent and removes the banner.
  await consentPage.locator('[data-consent-necessary]').click();
  await consentPage.waitForTimeout(80);
  if (await consentPage.locator('.consent-banner').count()) errors.push('consent banner remained after necessary-only');
  const stored = await consentPage.evaluate(() => {
    try { return JSON.parse(localStorage.getItem('iberfit_consent_v2') || 'null'); } catch { return null; }
  });
  if (!stored || stored.analytics !== false || stored.marketing !== false) errors.push(`necessary consent storage invalid ${JSON.stringify(stored)}`);
  await consentContext.close();

  // Global mobile/desktop regression after consent choice.
  for (const viewport of [{name:'mobile',width:390,height:844},{name:'desktop',width:1440,height:1000}]) {
    const context = await browser.newContext({viewport:{width:viewport.width,height:viewport.height},deviceScaleFactor:1});
    for (const route of routes) {
      const page = await context.newPage();
      const runtimeErrors = [];
      page.on('pageerror', e => runtimeErrors.push(`pageerror:${e.message}`));
      page.on('console', msg => { if (msg.type()==='error') runtimeErrors.push(`console:${msg.text()}`); });
      const response = await page.goto(base+route,{waitUntil:'domcontentloaded',timeout:30000});
      if (!response || response.status() !== 200) errors.push(`${viewport.name} ${route} status ${response && response.status()}`);
      await page.waitForTimeout(90);
      const geometry = await page.evaluate(() => ({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth}));
      if (geometry.sw > geometry.cw + 2) errors.push(`${viewport.name} ${route} page overflow ${geometry.sw}-${geometry.cw}`);
      if (await page.locator('link[href="/assets/mobile.v6435.css"]').count() !== 1) errors.push(`${viewport.name} ${route} mobile CSS count`);
      if (runtimeErrors.length) errors.push(`${viewport.name} ${route} ${runtimeErrors.join(' | ')}`);
      await page.close();
    }
    await context.close();
  }

  // Purposeful rails: initial position, next-card peek and real horizontal movement.
  const railContext = await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1});
  for (const [route, selector, children] of rails) {
    const page = await railContext.newPage();
    await page.goto(base+route,{waitUntil:'domcontentloaded'});
    const rail = page.locator(selector);
    if (await rail.count() !== 1) { errors.push(`rail missing ${route} ${selector}`); await page.close(); continue; }
    await rail.scrollIntoViewIfNeeded();
    await page.waitForTimeout(80);
    const before = await rail.evaluate(el => {
      const r=el.getBoundingClientRect(); const kids=[...el.children];
      return {left:el.scrollLeft,sw:el.scrollWidth,cw:el.clientWidth,count:kids.length,snap:getComputedStyle(el).scrollSnapType,flow:getComputedStyle(el).gridAutoFlow,secondLeft:kids[1]?.getBoundingClientRect().left,railRight:r.right};
    });
    if (before.count !== children) errors.push(`rail children ${route} ${before.count}/${children}`);
    if (before.left > 2) errors.push(`rail initial position drift ${route} ${selector}: ${before.left}`);
    if (before.sw <= before.cw + 24) errors.push(`rail not scrollable ${route} ${selector}`);
    if (!before.snap.includes('x')) errors.push(`rail snap ${route} ${selector}: ${before.snap}`);
    if (before.flow !== 'column') errors.push(`rail flow ${route} ${selector}: ${before.flow}`);
    if (!(before.secondLeft < before.railRight && before.secondLeft > 0)) errors.push(`rail next-card peek ${route} ${selector}`);
    await rail.evaluate(el => {el.scrollLeft=Math.min(el.scrollWidth-el.clientWidth,Math.max(180,el.clientWidth*.7));});
    await page.waitForTimeout(100);
    if (await rail.evaluate(el => el.scrollLeft) < 20) errors.push(`rail did not move ${route} ${selector}`);
    await page.close();
  }
  await railContext.close();

  // Final visual evidence with consent dismissed and rails reset to the true initial state.
  const visual = await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1});
  let consentSeeded = false;
  for (const [route,name] of [['/','home-es'],['/metodo/','method-es'],['/online/','online-es'],['/presencial/','inperson-es'],['/sobre-iberfit/','about-es'],['/en/','home-en']]) {
    const page = await visual.newPage();
    await page.goto(base+route,{waitUntil:'networkidle'});
    if (!consentSeeded && await page.locator('[data-consent-necessary]').count()) {
      await page.locator('[data-consent-necessary]').click();
      await page.waitForTimeout(70);
      consentSeeded = true;
    }
    await loadLazyAndReset(page);
    const positions = await page.evaluate(sel => [...document.querySelectorAll(sel)].map(el=>el.scrollLeft), railSelectors);
    if (positions.some(x => x > 2)) errors.push(`visual rail reset failed ${route}: ${positions.join(',')}`);
    await page.screenshot({path:`${evidence}/${name}-mobile-full.png`,fullPage:true});
    await page.close();
  }
  await visual.close();

  await browser.close();
  if (errors.length) {
    console.error(JSON.stringify({ok:false,errors},null,2));
    process.exit(1);
  }
  console.log(JSON.stringify({ok:true,routes:routes.length,rails:rails.length,consentMaxHeight:300,evidenceDir:evidence},null,2));
})().catch(err=>{console.error(err);process.exit(1)});
