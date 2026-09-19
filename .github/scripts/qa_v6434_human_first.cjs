const { chromium } = require('playwright');

const BASE = 'http://127.0.0.1:4173';
const routes = [
  '/', '/diagnostico-iri/', '/metodo/', '/presencial/', '/hibrido/', '/online/', '/sobre-iberfit/', '/contacto/',
  '/en/', '/en/iri-assessment/', '/en/method/', '/en/in-person/', '/en/hybrid/', '/en/online/', '/en/about/', '/en/contact/'
];

const expected = {
  '/': ['Entrenamiento personal con criterio.', 'Quiero saber por dónde empezar'],
  '/diagnostico-iri/': ['Antes de decirte qué entrenar, queremos entender cómo estás hoy.', 'Quiero entender mi punto de partida'],
  '/metodo/': ['Tu plan puede cambiar. El criterio no.', 'Ver cómo empezamos'],
  '/presencial/': ['Si te ayuda tener a alguien a tu lado, entrenamos contigo.', 'Quiero saber si hay cobertura para mí'],
  '/hibrido/': ['No tienes que elegir entre acompañamiento y flexibilidad.', 'Quiero saber si el híbrido encaja conmigo'],
  '/online/': ['Entrenar a distancia no debería sentirse como entrenar solo.', 'Quiero saber cómo sería mi plan online'],
  '/sobre-iberfit/': ['Detrás de IBERFIT hay método, pero también una forma muy humana de acompañarte.', 'Conocer cómo trabajamos'],
  '/contacto/': ['Cuéntanos qué buscas. No hace falta que sepas qué modalidad necesitas.', 'Cuéntanos tu situación'],
  '/en/': ['Personal training. With purpose.', 'Help me understand where to start'],
  '/en/iri-assessment/': ['Before we tell you what to train, we want to understand where you are today.', 'Help me understand my starting point'],
  '/en/method/': ['Your plan can change. The reasoning should not.', 'See how we start'],
  '/en/in-person/': ['If having someone beside you helps, we train with you.', 'Check whether I am in the coverage area'],
  '/en/hybrid/': ['You do not have to choose between support and flexibility.', 'See if hybrid could fit me'],
  '/en/online/': ['Training remotely should not feel like training alone.', 'See what my online plan could look like'],
  '/en/about/': ['There is a method behind IBERFIT, but also a very human way of supporting you.', 'See how we work'],
  '/en/contact/': ['Tell us what you are looking for. You do not need to know which format you need.', 'Tell us about your situation'],
};

function assert(cond, msg) { if (!cond) throw new Error(msg); }

async function autoScroll(page) {
  await page.evaluate(async () => {
    await new Promise(resolve => {
      let y = 0;
      const step = 600;
      const timer = setInterval(() => {
        window.scrollBy(0, step);
        y += step;
        if (y >= document.body.scrollHeight + innerHeight) {
          clearInterval(timer);
          window.scrollTo(0, 0);
          resolve();
        }
      }, 20);
    });
  });
  await page.waitForTimeout(250);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const evidenceDir = '/tmp/v6434-evidence';
  require('fs').mkdirSync(evidenceDir, { recursive: true });
  try {
    for (const width of [1440, 390]) {
      const height = width === 1440 ? 1000 : 844;
      for (const route of routes) {
        const context = await browser.newContext({ viewport: { width, height } });
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', e => errors.push(String(e)));
        const response = await page.goto(BASE + route, { waitUntil: 'networkidle', timeout: 25000 });
        assert(response && response.ok(), `${route} ${width}: HTTP failure`);
        const [h1Expected, ctaExpected] = expected[route];
        const state = await page.evaluate(({h1Expected, ctaExpected}) => {
          const h1 = document.querySelector('.hero-text h1');
          const primary = document.querySelector('.hero-actions .btn-primary');
          const doc = document.documentElement;
          const pr = primary?.getBoundingClientRect();
          const hero = document.querySelector('.hero-text');
          const heroRect = hero?.getBoundingClientRect();
          return {
            h1: h1?.textContent.trim(),
            primary: primary?.textContent.trim(),
            pageOverflow: doc.scrollWidth - doc.clientWidth,
            primaryWidth: pr?.width || 0,
            primaryHeight: pr?.height || 0,
            heroRight: heroRect?.right || 0,
            viewport: innerWidth,
          };
        }, {h1Expected, ctaExpected});
        assert(state.h1 === h1Expected, `${route} ${width}: hero mismatch: ${state.h1}`);
        assert(state.primary === ctaExpected, `${route} ${width}: primary CTA mismatch: ${state.primary}`);
        assert(state.pageOverflow <= 2, `${route} ${width}: horizontal overflow ${state.pageOverflow}px`);
        assert(state.primaryHeight >= 44, `${route} ${width}: primary CTA height ${state.primaryHeight}`);
        assert(state.primaryWidth >= 44, `${route} ${width}: primary CTA width ${state.primaryWidth}`);
        assert(state.heroRight <= state.viewport + 2, `${route} ${width}: hero exceeds viewport`);
        assert(errors.length === 0, `${route} ${width}: page errors ${errors.join(' | ')}`);

        await autoScroll(page);

        if (route.includes('online')) {
          const img = page.locator('.app-screen--plan img');
          await img.scrollIntoViewIfNeeded();
          await page.waitForFunction(() => {
            const el = document.querySelector('.app-screen--plan img');
            return !!el && el.complete && el.naturalWidth > 0;
          });
          const natural = await img.evaluate(el => [el.naturalWidth, el.naturalHeight]);
          assert(natural[0] === 760 && natural[1] === 387, `${route} ${width}: online plan image not loaded correctly ${natural}`);
        }

        if (route.endsWith('/contacto/') || route.endsWith('/contact/')) {
          const select = page.locator('[data-step="1"] select[required]');
          await select.evaluate(el => {
            el.selectedIndex = 1;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
          });
          const selectedValue = await select.inputValue();
          assert(selectedValue !== '', `${route} ${width}: orientador required select did not update`);
          await page.locator('[data-step="1"] [data-next-step]').click();
          const step2 = page.locator('[data-step="2"]');
          assert(await step2.isVisible(), `${route} ${width}: orientador did not advance to step 2`);
        }

        if (width === 390 && ['/', '/diagnostico-iri/', '/metodo/', '/presencial/', '/hibrido/', '/online/', '/sobre-iberfit/', '/contacto/'].includes(route)) {
          const name = route === '/' ? 'home' : route.split('/').filter(Boolean)[0];
          await page.goto(BASE + route, { waitUntil: 'networkidle' });
          await autoScroll(page);
          await page.screenshot({ path: `${evidenceDir}/${name}-mobile.png`, fullPage: true });
        }
        if (width === 1440 && ['/', '/presencial/', '/hibrido/', '/online/', '/contacto/'].includes(route)) {
          const name = route === '/' ? 'home' : route.split('/').filter(Boolean)[0];
          await page.goto(BASE + route, { waitUntil: 'networkidle' });
          await autoScroll(page);
          await page.screenshot({ path: `${evidenceDir}/${name}-desktop.png`, fullPage: true });
        }
        console.log(JSON.stringify({ route, width, h1: state.h1, primary: state.primary, overflow: state.pageOverflow }));
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
})().catch(err => { console.error(err.stack || err); process.exit(1); });
