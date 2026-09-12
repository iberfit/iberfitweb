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

  await page.close();
  await context.close();
}

await browser.close();

if (findings.length) {
  console.error(JSON.stringify(findings, null, 2));
  process.exit(1);
}

console.log('Accesibilidad V6.28: PASS · 7 rutas · WCAG A/AA · 0 violaciones automáticas');
