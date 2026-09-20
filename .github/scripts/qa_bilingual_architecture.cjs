const fs = require('fs');
const path = require('path');

const ROOT = path.resolve('candidate/v628');
const SITE = 'https://iberfit.cl';

function fail(msg) { console.error(`FAIL: ${msg}`); process.exit(1); }
function assert(cond, msg) { if (!cond) fail(msg); }
function read(rel) { return fs.readFileSync(path.join(ROOT, rel), 'utf8'); }
function getAlt(html, hreflang) {
  const pats = [
    new RegExp(`<link[^>]+href="([^"]+)"[^>]+hreflang="${hreflang}"[^>]+rel="alternate"[^>]*>`, 'i'),
    new RegExp(`<link[^>]+hreflang="${hreflang}"[^>]+rel="alternate"[^>]+href="([^"]+)"[^>]*>`, 'i'),
    new RegExp(`<link[^>]+rel="alternate"[^>]+href="([^"]+)"[^>]+hreflang="${hreflang}"[^>]*>`, 'i'),
    new RegExp(`<link[^>]+rel="alternate"[^>]+hreflang="${hreflang}"[^>]+href="([^"]+)"[^>]*>`, 'i')
  ];
  for (const re of pats) { const m=html.match(re); if (m) return m[1]; }
  return null;
}
function canonical(html) {
  const m=html.match(/<link[^>]+href="([^"]+)"[^>]+rel="canonical"[^>]*>/i)||html.match(/<link[^>]+rel="canonical"[^>]+href="([^"]+)"[^>]*>/i);
  return m&&m[1];
}
function relFrom(url) {
  const u=new URL(url);
  assert(u.origin===SITE,`foreign URL ${url}`);
  if(u.pathname==='/') return 'index.html';
  assert(u.pathname.endsWith('/'),`non-directory URL ${url}`);
  return u.pathname.replace(/^\//,'')+'index.html';
}

const sitemap=read('sitemap.xml');
const urls=[...sitemap.matchAll(/<loc>(https:\/\/iberfit\.cl\/[^<]*)<\/loc>/g)].map(m=>m[1]);
assert(urls.length===32,`expected 32 sitemap URLs, got ${urls.length}`);
assert(new Set(urls).size===32,'duplicate sitemap URLs');

const pages=new Map();
for(const url of urls){
  const rel=relFrom(url);
  assert(fs.existsSync(path.join(ROOT,rel)),`missing HTML for ${url}`);
  const html=read(rel);
  const can=canonical(html), es=getAlt(html,'es'), en=getAlt(html,'en');
  assert(can===url,`canonical mismatch ${url} -> ${can}`);
  assert(es&&en,`missing es/en hreflang on ${url}`);
  assert(urls.includes(es),`ES alternate not in sitemap ${url} -> ${es}`);
  assert(urls.includes(en),`EN alternate not in sitemap ${url} -> ${en}`);
  pages.set(url,{es,en});
}

const pairs=new Set();
for(const [url,p] of pages){
  const isEn=url.includes('/en/');
  const other=isEn?p.es:p.en;
  const q=pages.get(other);
  assert(q,`missing counterpart ${url} -> ${other}`);
  const back=isEn?q.en:q.es;
  assert(back===url,`non-reciprocal hreflang ${url} -> ${other} -> ${back}`);
  pairs.add([url,other].sort().join(' <> '));
}
assert(pairs.size===16,`expected 16 language pairs, got ${pairs.size}`);
assert(pages.has(`${SITE}/en/online/`),'missing canonical /en/online/ route');
assert(!urls.includes(`${SITE}/en/online-training/`),'guessed /en/online-training/ must not enter sitemap');
assert(/Sitemap:\s*https:\/\/iberfit\.cl\/sitemap\.xml/i.test(read('robots.txt')),'robots.txt missing sitemap declaration');

console.log(JSON.stringify({urls:32,pairs:16,canonicals:'32/32',hreflang:'16/16 reciprocal',sitemap:'32/32',onlineEn:`${SITE}/en/online/`},null,2));
