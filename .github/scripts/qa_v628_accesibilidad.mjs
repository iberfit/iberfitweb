import { chromium } from 'playwright';
import path from 'node:path';

const base = process.env.BASE_URL || 'http://127.0.0.1:4173';
const routes = ['/', '/diagnostico-iri/', '/metodo/', '/presencial/', '/hibrido/', '/online/', '/contacto/'];
const axePath = path.resolve('node_modules/axe-core/axe.min.js');

const browser = await chromium.launch({ headless: true });
const findings = [];

for (const route of routes) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, locale: 'es-CL' });
  const page = await context.newPage();
  const response = await page.goto(base + route, { waitUntil: 'networkidle', timeout: 30000 });

  if (!response || !response.ok()) {
    findings.push({ route, id: 'http', impact: 'critical', description: response ? String(response.status()) : 'sin respuesta' });
    await page.close();
    await context.close();
    continue;
  }

  await page.addScriptTag({ path: axePath });
  const results = await page.evaluate(async () => window.axe.run(document, {
    runOnly: {
      type: 'tag',
      values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']
    },
    resultTypes: ['violations']
  }));

  for (const violation of results.violations) {
    findings.push({
      route,
      id: violation.id,
      impact: violation.impact,
      description: violation.description,
      help: violation.help,
      nodes: violation.nodes.map(node => node.target),
    });
  }

  if (route === '/contacto/') {
    const status = page.locator('[data-orientador-status]');
    if (await status.count() !== 1 || await status.getAttribute('aria-live') !== 'polite') {
      findings.push({ route, id:'orientador-live-region', impact:'serious', description:'El orientador debe exponer una región viva accesible.' });
    }

    const firstGoal = page.locator('[data-step="1"] .choice-chip').first();
    if (await firstGoal.count() !== 1) {
      findings.push({ route, id:'orientador-choice-chip', impact:'serious', description:'No se generaron opciones táctiles accesibles.' });
    } else {
      await firstGoal.click();
      if (await firstGoal.getAttribute('aria-pressed') !== 'true') {
        findings.push({ route, id:'orientador-aria-pressed', impact:'serious', description:'La opción seleccionada no refleja aria-pressed=true.' });
      }
      await page.locator('[data-step="1"] [data-next-step]').click();
      await page.waitForTimeout(60);
      const step2 = page.locator('[data-step="2"]');
      const liveText = (await status.textContent() || '').trim();
      if (!(await step2.evaluate(el => el.classList.contains('active'))) || await step2.getAttribute('aria-hidden') !== 'false') {
        findings.push({ route, id:'orientador-step-state', impact:'serious', description:'El paso 2 no expone correctamente su estado activo.' });
      }
      if (!liveText.includes('Paso 2 de 3')) {
        findings.push({ route, id:'orientador-step-announcement', impact:'moderate', description:'El cambio de paso no se anuncia correctamente.' });
      }

      await page.locator('[data-step="2"] [data-next-step]').click();
      await page.locator('[data-step="3"] button[type="submit"]').click();
      await page.waitForTimeout(60);
      const result = page.locator('[data-orientador-result]');
      if (await result.isHidden() || await result.getAttribute('role') !== 'region' || await result.getAttribute('aria-live') !== 'polite') {
        findings.push({ route, id:'orientador-result', impact:'serious', description:'El resultado no se expone como región accesible.' });
      }
    }
  }

  await page.close();
  await context.close();
}

await browser.close();

if (findings.length) {
  console.error(JSON.stringify(findings, null, 2));
  process.exit(1);
}

console.log('Accesibilidad V6.28: PASS · 7 rutas · WCAG A/AA · 0 violaciones automáticas');
