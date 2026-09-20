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
function fetchExact(url) {
  const marker='\n__IBERFIT_STATUS__';
  const out=execFileSync('curl', ['-sS','--retry','4','--retry-all-errors','-o','-','-w',`${marker}%{http_code}__IBERFIT_URL__%{url_effective}`,url], {encoding:'utf8'});
  const idx=out.lastIndexOf(marker);
  assert(idx>=0,`unable to parse HTTP status for ${url}`);
  const body=out.slice(0,idx);
  const meta=out.slice(idx+marker.length);
  const m=meta.match(/^(\d{3})__IBERFIT_URL__(.*)$/s);
  assert(m,`invalid HTTP metadata for ${url}: ${meta}`);
  return {body,status:Number(m[1]),effective:m[2].trim()};
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
    const requested=`${url}?matrix=${process.env.GITHUB_RUN_ID || Date.now()}`;
    const live=fetchExact(requested);
    assert(live.status===200,`LIVE status not 200 ${url}: ${live.status}`);
    assert(live.effective===requested,`LIVE redirect detected ${url}: ${live.effective}`);
    const can = canonical(live.body);
    const es = getTag(live.body, 'es');
    const en = getTag(live.body, 'en');
    assert(can === pages.get(url).canonical, `LIVE canonical mismatch ${url}: ${can}`);
    assert(es === pages.get(url).es, `LIVE hreflang es mismatch ${url}: ${es}`);
    assert(en === pages.get(url).en, `LIVE hreflang en mismatch ${url}: ${en}`);
  }
  const sitemapReq=`${SITE}/sitemap.xml?matrix=${process.env.GITHUB_RUN_ID || Date.now()}`;
  const liveSitemap=fetchExact(sitemapReq);
  assert(liveSitemap.status===200,`LIVE sitemap status ${liveSitemap.status}`);
  assert(liveSitemap.effective===sitemapReq,`LIVE sitemap redirect ${liveSitemap.effective}`);
  const liveLocs = [...liveSitemap.body.matchAll(/<loc>(https:\/\/iberfit\.cl\/[^<]*)<\/loc>/g)].map(m=>m[1]);
  assert(JSON.stringify(liveLocs.sort()) === JSON.stringify([...locs].sort()), 'LIVE sitemap differs from certified candidate');
  const robotsReq=`${SITE}/robots.txt?matrix=${process.env.GITHUB_RUN_ID || Date.now()}`;
  const liveRobots=fetchExact(robotsReq);
  assert(liveRobots.status===200,`LIVE robots status ${liveRobots.status}`);
  assert(liveRobots.effective===robotsReq,`LIVE robots redirect ${liveRobots.effective}`);
  assert(/Sitemap:\s*https:\/\/iberfit\.cl\/sitemap\.xml/i.test(liveRobots.body), 'LIVE robots.txt missing sitemap declaration');
}

console.log(JSON.stringify({
  sitemapUrls: locs.length,
  reciprocalPairs: pairs.size,
  canonicals: '32/32',
  hreflangReciprocal: '16/16',
  sitemapCoverage: '32/32',
  exactHttp200: process.env.CHECK_LIVE === '1' ? '32/32' : 'not-run',
  redirects: process.env.CHECK_LIVE === '1' ? '0/32' : 'not-run',
  canonicalOnlineEn: `${SITE}/en/online/`,
  guessedOnlineTrainingDeclared: false,
  liveChecked: process.env.CHECK_LIVE === '1'
}, null, 2));
