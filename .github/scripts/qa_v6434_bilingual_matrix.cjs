const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const ROOT = path.resolve('candidate/v628');
const SITE = 'https://iberfit.cl';

function fail(msg) { console.error(`FAIL: ${msg}`); process.exit(1); }
function assert(cond, msg) { if (!cond) fail(msg); }
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), 'utf8'); }
function getTag(html, hreflang) {
  const patterns = [
    new RegExp(`<link[^>]+href="([^"]+)"[^>]+hreflang="${hreflang}"[^>]+rel="alternate"[^>]*>`, 'i'),
    new RegExp(`<link[^>]+hreflang="${hreflang}"[^>]+rel="alternate"[^>]+href="([^"]+)"[^>]*>`, 'i'),
    new RegExp(`<link[^>]+rel="alternate"[^>]+href="([^"]+)"[^>]+hreflang="${hreflang}"[^>]*>`, 'i'),
    new RegExp(`<link[^>]+rel="alternate"[^>]+hreflang="${hreflang}"[^>]+href="([^"]+)"[^>]*>`, 'i')
  ];
  for (const re of patterns) { const m = html.match(re); if (m) return m[1]; }
  return null;
}
function canonical(html) {
  const m = html.match(/<link[^>]+href="([^"]+)"[^>]+rel="canonical"[^>]*>/i) || html.match(/<link[^>]+rel="canonical"[^>]+href="([^"]+)"[^>]*>/i);
  return m && m[1];
}
function toRel(url) {
  const u = new URL(url);
  assert(u.origin === SITE, `foreign URL in sitemap: ${url}`);
  if (u.pathname === '/') return 'index.html';
  assert(u.pathname.endsWith('/'), `non-directory canonical URL: ${url}`);
  return u.pathname.replace(/^\//,'') + 'index.html';
}
function curl(url) {
  return execFileSync('curl', ['-fsSL','--retry','4','--retry-all-errors', url], {encoding:'utf8'});
}

const sitemap = read('sitemap.xml');
const locs = [...sitemap.matchAll(/<loc>(https:\/\/iberfit\.cl\/[^<]*)<\/loc>/g)].map(m=>m[1]);
assert(locs.length === 32, `expected 32 sitemap URLs, got ${locs.length}`);
assert(new Set(locs).size === 32, 'duplicate sitemap URLs');

const pages = new Map();
for (const url of locs) {
  const rel = toRel(url);
  const full = path.join(ROOT, rel);
  assert(fs.existsSync(full), `sitemap URL has no HTML file: ${url} -> ${rel}`);
  const html = fs.readFileSync(full,'utf8');
  const can = canonical(html);
  assert(can === url, `canonical mismatch ${url}: ${can}`);
  const es = getTag(html, 'es');
  const en = getTag(html, 'en');
  assert(es, `missing hreflang=es: ${url}`);
  assert(en, `missing hreflang=en: ${url}`);
  assert(locs.includes(es), `hreflang es not in sitemap: ${url} -> ${es}`);
  assert(locs.includes(en), `hreflang en not in sitemap: ${url} -> ${en}`);
  pages.set(url,{rel,es,en,canonical:can});
}

const pairs = new Set();
for (const [url, p] of pages) {
  const lang = url.includes('/en/') ? 'en' : 'es';
  const counterpart = lang === 'es' ? p.en : p.es;
  assert(counterpart !== url, `self counterpart for ${url}`);
  const q = pages.get(counterpart);
  assert(q, `counterpart missing from sitemap: ${url} -> ${counterpart}`);
  const back = lang === 'es' ? q.es : q.en;
  assert(back === url, `hreflang not reciprocal: ${url} -> ${counterpart} -> ${back}`);
  pairs.add([url,counterpart].sort().join(' <> '));
}
assert(pairs.size === 16, `expected 16 reciprocal language pairs, got ${pairs.size}`);

const onlineEn = pages.get(`${SITE}/en/online/`);
assert(onlineEn && onlineEn.canonical === `${SITE}/en/online/`, 'EN online canonical drift');
assert(!locs.includes(`${SITE}/en/online-training/`), 'unexpected guessed /en/online-training/ in sitemap');

const robots = read('robots.txt');
assert(/Sitemap:\s*https:\/\/iberfit\.cl\/sitemap\.xml/i.test(robots), 'robots.txt missing sitemap declaration');

if (process.env.CHECK_LIVE === '1') {
  for (const url of locs) {
    const body = curl(`${url}?matrix=${process.env.GITHUB_RUN_ID || Date.now()}`);
    const can = canonical(body);
    const es = getTag(body, 'es');
    const en = getTag(body, 'en');
    assert(can === pages.get(url).canonical, `LIVE canonical mismatch ${url}: ${can}`);
    assert(es === pages.get(url).es, `LIVE hreflang es mismatch ${url}: ${es}`);
    assert(en === pages.get(url).en, `LIVE hreflang en mismatch ${url}: ${en}`);
  }
  const liveSitemap = curl(`${SITE}/sitemap.xml?matrix=${process.env.GITHUB_RUN_ID || Date.now()}`);
  const liveLocs = [...liveSitemap.matchAll(/<loc>(https:\/\/iberfit\.cl\/[^<]*)<\/loc>/g)].map(m=>m[1]);
  assert(JSON.stringify(liveLocs.sort()) === JSON.stringify([...locs].sort()), 'LIVE sitemap differs from certified candidate');
  const liveRobots = curl(`${SITE}/robots.txt?matrix=${process.env.GITHUB_RUN_ID || Date.now()}`);
  assert(/Sitemap:\s*https:\/\/iberfit\.cl\/sitemap\.xml/i.test(liveRobots), 'LIVE robots.txt missing sitemap declaration');
}

console.log(JSON.stringify({
  sitemapUrls: locs.length,
  reciprocalPairs: pairs.size,
  canonicals: '32/32',
  hreflangReciprocal: '16/16',
  sitemapCoverage: '32/32',
  canonicalOnlineEn: `${SITE}/en/online/`,
  guessedOnlineTrainingDeclared: false,
  liveChecked: process.env.CHECK_LIVE === '1'
}, null, 2));
