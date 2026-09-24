import { chromium } from 'playwright';

const routes = [
  '/', '/presencial/', '/hibrido/', '/online/', '/contacto/',
  '/en/', '/en/in-person/', '/en/hybrid/', '/en/online/', '/en/contact/'
];
const browser = await chromium.launch({ headless: true });
for (const width of [390, 768, 1440]) {
  const context = await browser.newContext({ viewport: { width, height: 1000 } });
  for (const route of routes) {
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    const response = await page.goto('http://127.0.0.1:4173' + route, { waitUntil: 'networkidle' });
    if (!response?.ok()) throw new Error(`HTTP ${route}: ${response?.status()}`);
    const state = await page.evaluate(() => {
      const root = document.documentElement;
      const primary = document.querySelector('.hero-actions .btn-primary');
      const rect = primary?.getBoundingClientRect();
      return {
        overflow: root.scrollWidth - root.clientWidth,
        ctaW: rect?.width || 0,
        ctaH: rect?.height || 0,
        h1: (document.querySelector('h1')?.textContent || '').trim(),
        meta: (document.querySelector('.hero-meta')?.textContent || '').trim(),
      };
    });
    if (state.overflow > 2) throw new Error(`overflow ${route} ${width}: ${state.overflow}`);
    if (state.ctaW < 44 || state.ctaH < 44) throw new Error(`CTA ${route} ${width}: ${state.ctaW}x${state.ctaH}`);
    if (!state.h1) throw new Error(`missing h1 ${route}`);
    if (errors.length) throw new Error(`pageerror ${route}: ${errors.join(' | ')}`);
    if ((route === '/presencial/' || route === '/en/in-person/') && !state.meta.includes('Las Condes')) {
      throw new Error(`service certainty missing in hero meta: ${route}`);
    }
    if (width !== 768) {
      const slug = route === '/' ? 'home' : route.replace(/^\/+|\/+$/g, '').replaceAll('/', '-');
      await page.screenshot({ path: `/tmp/v64319-screens/${slug}-${width}.png`, fullPage: true });
    }
    await page.close();
  }
  await context.close();
}
await browser.close();
console.log('BROWSER_CERT_OK');
