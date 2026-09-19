const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const root = path.resolve('candidate/v628');
const files = [];
(function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) walk(full);
    else if (name.endsWith('.html')) files.push(full);
  }
})(root);

const routeOf = file => {
  const rel = path.relative(root, file).replaceAll('\\', '/');
  if (rel === 'index.html') return '/';
  if (rel === '404.html') return '/404.html';
  return '/' + rel.replace(/index\.html$/, '');
};
const events = async page => page.evaluate(() =>
  Array.from(window.dataLayer || [], x => Array.from(x))
    .filter(x => x[0] === 'event')
    .map(x => ({ name: x[1], params: x[2] || {} }))
);

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(() => {
    localStorage.setItem('iberfit_consent_v2', JSON.stringify({
      version: '2026-07-12-v2', analytics: true, marketing: false, updatedAt: new Date().toISOString()
    }));
    document.addEventListener('click', event => {
      const a = event.target.closest?.('a');
      if (a && (a.href.includes('wa.me') || a.href.startsWith('mailto:') || a.closest('.intent-router') || a.classList.contains('review-source-link'))) {
        event.preventDefault();
      }
    }, true);
  });
  await ctx.route('https://www.googletagmanager.com/**', route => route.abort());

  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  for (const file of files.sort()) {
    const route = routeOf(file);
    const response = await page.goto('http://127.0.0.1:4173' + route, { waitUntil: 'domcontentloaded' });
    if (!response?.ok()) throw new Error(`HTTP ${route}:${response?.status()}`);
    await page.waitForTimeout(50);
    const state = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      analytics643: [...document.scripts].filter(x => x.src.includes('/assets/analytics.v643.js')).length,
      analytics632: [...document.scripts].filter(x => x.src.includes('/assets/analytics.v632.js')).length,
      menu642: [...document.scripts].filter(x => x.src.includes('/assets/menu.v642.js')).length,
      hardening630: [...document.scripts].filter(x => x.src.includes('/assets/hardening.v630.js')).length,
    }));
    if (state.overflow > 2 || state.analytics643 !== 1 || state.analytics632 !== 0 || state.menu642 !== 1 || state.hardening630 !== 0) {
      throw new Error(`BASIC ${route} ${JSON.stringify(state)}`);
    }
  }
  if (errors.length) throw new Error('PAGEERROR ' + errors.join(' | '));

  await page.goto('http://127.0.0.1:4173/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(100);
  for (const selector of [
    '[data-track="funnel_iri_start"]',
    '[data-track="funnel_compare_formats"]',
    '[data-track="funnel_guide_start"]',
    '[data-track="cta_hero_secondary"]',
    '[data-track="cta_iri_footer"]'
  ]) {
    await page.locator(selector).click();
    await page.waitForTimeout(25);
  }
  let ev = await events(page);
  const names = ev.map(x => x.name);
  for (const expected of ['funnel_iri_start','funnel_compare_formats','funnel_guide_start','cta_hero_secondary','cta_iri_footer','whatsapp_click','contact_intent','generate_lead']) {
    if (!names.includes(expected)) throw new Error('MISSING_EVENT ' + expected);
  }
  if (names.filter(x => x === 'contact_intent').length !== 2) throw new Error('CONTACT_INTENT_COUNT');
  if (names.filter(x => x === 'generate_lead').length !== 1) throw new Error('GENERATE_LEAD_DEDUPE');
  const lead = ev.find(x => x.name === 'generate_lead');
  if (!lead || lead.params.lead_source !== 'whatsapp') throw new Error('LEAD_SOURCE');

  await page.goto('http://127.0.0.1:4173/contacto/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(100);
  const form = page.locator('[data-orientador-form]');
  const steps = page.locator('[data-step]');
  const count = await steps.count();
  for (let i = 0; i < count; i++) {
    const active = page.locator('[data-step].active');
    const choice = active.locator('.choice-chip').first();
    if (await choice.count()) await choice.click();
    if (i < count - 1) {
      const next = active.locator('[data-next-step]');
      if (await next.count()) await next.click();
    }
  }
  await form.locator('button[type="submit"]').first().click();
  await page.waitForTimeout(100);
  await page.locator('[data-track="cta_guide_whatsapp"]').click();
  await page.waitForTimeout(30);
  ev = await events(page);
  const contactNames = ev.map(x => x.name);
  for (const expected of ['format_guide_complete','cta_guide_whatsapp','format_guide_whatsapp_open','whatsapp_click','contact_intent']) {
    if (!contactNames.includes(expected)) throw new Error('GUIDE_EVENT ' + expected);
  }
  const lastIntent = [...ev].reverse().find(x => x.name === 'contact_intent');
  if (!lastIntent || lastIntent.params.cta_position !== 'guide_result') throw new Error('GUIDE_ATTRIBUTION ' + JSON.stringify(lastIntent));

  for (const [name, width, height] of [['tablet',820,1180], ['desktop',1440,1000]]) {
    const c = await browser.newContext({ viewport: { width, height } });
    const p = await c.newPage();
    const pageErrors = [];
    p.on('pageerror', e => pageErrors.push(String(e)));
    for (const route of ['/', '/contacto/', '/diagnostico-iri/', '/online/', '/entrenador-personal-las-condes/']) {
      const response = await p.goto('http://127.0.0.1:4173' + route, { waitUntil: 'domcontentloaded' });
      if (!response?.ok()) throw new Error(`${name} HTTP ${route}`);
      const overflow = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      if (overflow > 2) throw new Error(`${name} overflow ${route}:${overflow}`);
    }
    if (pageErrors.length) throw new Error(`${name} PAGEERROR ${pageErrors.join(' | ')}`);
    await c.close();
  }

  fs.mkdirSync('/tmp/v643-evidence', { recursive: true });
  fs.writeFileSync('/tmp/v643-evidence/events.json', JSON.stringify({ home: names, contact: contactNames }, null, 2));
  await ctx.close();
  await browser.close();
  console.log(JSON.stringify({ routes: files.length, events: 'ok', leadDedupe: 'ok', privacy: 'consent-gated', mobile: 'ok', tablet: 'ok', desktop: 'ok' }));
})().catch(error => {
  console.error(error);
  process.exit(1);
});
