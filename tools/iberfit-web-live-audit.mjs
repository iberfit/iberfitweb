#!/usr/bin/env node
/**
 * IBERFIT commercial web: non-mutating public-site audit.
 * Node >=20. No third-party packages, cookies, secrets or deployment writes.
 * Usage: node iberfit_web_live_audit.mjs [--base=https://iberfit.cl] [--timeout=15000]
 */
const ES = [
  '/', '/diagnostico-iri/', '/metodo/', '/presencial/', '/hibrido/',
  '/online/', '/sobre-iberfit/', '/contacto/', '/privacidad/',
  '/entrenador-personal-las-condes/', '/entrenador-personal-vitacura/',
  '/entrenamiento-personal-providencia/', '/entrenador-personal-lo-barnechea/',
  '/personal-trainer-nunoa/', '/entrenador-personal-la-reina/',
  '/entrenador-personal-penalolen/',
];
const EN = [
  '/en/', '/en/iri-assessment/', '/en/method/', '/en/in-person/',
  '/en/hybrid/', '/en/online/', '/en/about/', '/en/contact/', '/en/privacy/',
  '/en/personal-trainer-las-condes/', '/en/personal-trainer-vitacura/',
  '/en/personal-training-providencia/', '/en/personal-trainer-lo-barnechea/',
  '/en/personal-trainer-nunoa/', '/en/personal-trainer-la-reina/',
  '/en/personal-trainer-penalolen/',
];
const expected = [...ES, ...EN];
const args = Object.fromEntries(process.argv.slice(2).map(arg => {
  const m = /^--([\w-]+)=(.+)$/.exec(arg);
  if (!m) throw Error(`Unsupported option: ${arg}`);
  return [m[1], m[2]];
}));
const base = new URL(args.base || 'https://iberfit.cl');
if (!['http:', 'https:'].includes(base.protocol)) throw Error('Invalid URL scheme');
const canonicalOrigin = new URL(args['canonical-origin'] || 'https://iberfit.cl').origin;
const timeout = Math.max(1000, Math.min(30000, Number(args.timeout || 15000)));
if (!Number.isFinite(timeout)) throw Error('Invalid timeout');
const failures = [], warnings = [], pages = [];
async function fetchPage(path) {
  const url = new URL(path, base);
  const res = await fetch(url, {
    redirect: 'manual', signal: AbortSignal.timeout(timeout),
    headers: { 'accept': 'text/html,application/xml,text/plain;q=0.8', 'user-agent': 'IBERFIT-NonMutating-Site-Audit/1.0' },
  });
  const body = await res.text();
  return { status: res.status, headers: res.headers, body, url: url.href };
}
function attributes(tag) {
  const attrs = {};
  for (const m of tag.matchAll(/([\w-]+)\s*=\s*(["'])(.*?)\2/gs)) attrs[m[1].toLowerCase()] = m[3];
  return attrs;
}
async function auditOne(path) {
  try {
    const { status, headers, body } = await fetchPage(path);
    if (status !== 200) failures.push(`${path}: HTTP ${status}, expected 200`);
    if (status !== 200) return { path, status };
    const lang = body.match(/<html\b[^>]*\blang\s*=\s*["']([^"']+)["']/i)?.[1] ?? null;
    const expectedLang = path.startsWith('/en/') ? 'en' : 'es';
    if (!lang?.toLowerCase().startsWith(expectedLang)) failures.push(`${path}: html lang ${lang || 'missing'} (expected ${expectedLang})`);
    const metaTags = [...body.matchAll(/<meta\b[^>]*>/gi)].map(m => attributes(m[0]));
    const robots = metaTags.filter(a => ['robots', 'googlebot'].includes(a.name?.toLowerCase())).map(a => a.content || '').join(',');
    if (/noindex/i.test(robots + ',' + (headers.get('x-robots-tag') || ''))) failures.push(`${path}: noindex present`);
    const canonicalLinks = [...body.matchAll(/<link\b[^>]*>/gi)].map(m => attributes(m[0])).filter(a => (a.rel || '').toLowerCase().split(/\s+/).includes('canonical'));
    const canonical = canonicalLinks[0]?.href ?? null;
    if (canonicalLinks.length !== 1) failures.push(`${path}: expected exactly one canonical; got ${canonicalLinks.length}`);
    if (canonical !== new URL(path, canonicalOrigin).href) failures.push(`${path}: canonical ${canonical || 'missing'} does not match expected`);
    const alternateLinks = [...body.matchAll(/<link\b[^>]*>/gi)]
      .map(m => attributes(m[0]))
      .filter(a => (a.rel || '').toLowerCase().split(/\s+/).includes('alternate') && a.hreflang);
    const alternates = Object.fromEntries(alternateLinks.map(a => [a.hreflang.toLowerCase(), a.href]));
    const pairIndex = expected.indexOf(path) % ES.length;
    const esHref = new URL(ES[pairIndex], canonicalOrigin).href;
    const enHref = new URL(EN[pairIndex], canonicalOrigin).href;
    const foundEs = alternates['es-cl'] || alternates.es;
    const foundEn = alternates.en;
    if (foundEs !== esHref) failures.push(`${path}: hreflang es-CL points to ${foundEs || 'missing'} instead of ${esHref}`);
    if (foundEn !== enHref) failures.push(`${path}: hreflang en points to ${foundEn || 'missing'} instead of ${enHref}`);
    const xDefault = alternates['x-default'] || null;
    if (xDefault && !expected.some(route => new URL(route, canonicalOrigin).href === xDefault))
      warnings.push(`${path}: x-default does not point to a known public route (${xDefault})`);
    const title = body.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i)?.[1].replace(/\s+/g, ' ').trim() || '';
    if (!title) failures.push(`${path}: missing title`);
    const description = metaTags.find(a => a.name?.toLowerCase() === 'description')?.content || '';
    if (!description) warnings.push(`${path}: missing meta description`);
    if (!/<h1\b/i.test(body)) failures.push(`${path}: missing H1`);
    return { path, status, lang, canonical, alternateCount: alternateLinks.length, title, descriptionLength: description.length, esHref: foundEs, enHref: foundEn, xDefault };
  } catch (error) {
    failures.push(`${path}: request failed (${error.name || 'Error'}: ${error.message})`);
    return { path, error: String(error.message) };
  }
}
async function main() {
  if (expected.length !== 32 || new Set(expected).size !== 32) throw Error('Route manifest must contain 32 unique paths');
  try {
    const s = await fetchPage('/sitemap.xml');
    if (s.status !== 200) failures.push(`sitemap.xml: HTTP ${s.status}`);
    const discovered = [...s.body.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/gi)].map(m => m[1]);
    const sitemapPaths = discovered.map(url => { try { return new URL(url).pathname; } catch { return url; } });
    for (const p of expected) if (!sitemapPaths.includes(p)) failures.push(`sitemap missing: ${p}`);
    for (const p of sitemapPaths) if (!expected.includes(p)) warnings.push(`sitemap extra URL: ${p}`);
    if (sitemapPaths.length !== 32) failures.push(`sitemap includes ${sitemapPaths.length} URLs; expected 32`);
  } catch (error) { failures.push(`sitemap request failed: ${error.message}`); }
  try {
    const r = await fetchPage('/robots.txt');
    if (r.status !== 200) failures.push(`robots.txt: HTTP ${r.status}`);
    if (!/Sitemap:\s*https:\/\/iberfit\.cl\/sitemap\.xml/i.test(r.body)) warnings.push('robots.txt does not advertise expected sitemap');
  } catch (error) { failures.push(`robots.txt request failed: ${error.message}`); }
  // Bounded concurrency, never write to the live site.
  let index = 0;
  async function worker() {
    while (index < expected.length) { const path = expected[index++]; pages.push(await auditOne(path)); }
  }
  await Promise.all(Array.from({ length: 4 }, worker));
  const result = { auditedAt: new Date().toISOString(), target: base.href, expectedRoutes: 32,
    reached: pages.filter(p => p.status === 200).length, failureCount: failures.length, warningCount: warnings.length,
    failures, warnings, pages: pages.sort((a,b) => expected.indexOf(a.path) - expected.indexOf(b.path)) };
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
  process.exitCode = failures.length ? 1 : 0;
}
await main();