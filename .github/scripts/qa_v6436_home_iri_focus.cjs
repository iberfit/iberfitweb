const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve('candidate/v628');
const BASE = 'http://127.0.0.1:4174';
const EVIDENCE = '/tmp/v6436-evidence';
fs.mkdirSync(EVIDENCE, { recursive: true });

function htmlFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const p = path.join(dir, entry.name);
    return entry.isDirectory() ? htmlFiles(p) : (entry.isFile() && entry.name.endsWith('.html') ? [p] : []);
  });
}
function routeFor(file) {
  const rel = path.relative(ROOT, file).split(path.sep).join('/');
  if (rel === 'index.html') return '/';
  if (rel === '404.html') return '/404.html';
  return '/' + rel.replace(/index\.html$/, '');
}

(async()=>{
  const routes = htmlFiles(ROOT).map(routeFor).sort();
  if (routes.length !== 33) throw new Error(`EXPECTED_33_HTML:${routes.length}`);
  const browser = await chromium.launch({ headless: true });
  const errors = [];
  for (const viewport of [{width:390,height:844,name:'mobile'},{width:1440,height:900,name:'desktop'}]) {
    const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height } });
    for (const route of routes) {
      const page = await context.newPage();
      const pageErrors=[];
      page.on('pageerror', e=>pageErrors.push(String(e)));
      page.on('console', msg=>{ if(msg.type()==='error') pageErrors.push(`console:${msg.text()}`); });
      const response = await page.goto(BASE + route, { waitUntil:'networkidle' });
      if (!response || !response.ok()) errors.push(`${viewport.name}:${route}:HTTP_${response?.status()}`);
      const overflow = await page.evaluate(()=>document.documentElement.scrollWidth - innerWidth);
      if (overflow > 2) errors.push(`${viewport.name}:${route}:OVERFLOW_${overflow}`);
      if (pageErrors.length) errors.push(`${viewport.name}:${route}:${pageErrors.join('|')}`);
      await page.close();
    }
    await context.close();
  }

  const context = await browser.newContext({ viewport:{width:390,height:844} });
  for (const [route,lang] of [['/','es'],['/en/','en']]) {
    const page = await context.newPage();
    await page.goto(BASE + route, { waitUntil:'networkidle' });
    await page.locator('.report-preview-v2').scrollIntoViewIfNeeded();
    const enhanced = await page.locator('.report-preview-v2').getAttribute('data-focus-v6436');
    if (enhanced !== '1') errors.push(`${lang}:NOT_ENHANCED`);
    const detail = page.locator('.report-more-v6436');
    if (await detail.count() !== 1) errors.push(`${lang}:DETAIL_COUNT`);
    const visibleMetrics = await page.locator('.report-preview-v2 > .report-metrics-v2 > .report-metric').count();
    if (visibleMetrics !== 2) errors.push(`${lang}:VISIBLE_METRICS_${visibleMetrics}`);
    const hiddenMetrics = await page.locator('.report-more-content-v6436 .report-metric').count();
    if (hiddenMetrics < 1) errors.push(`${lang}:DETAIL_METRICS_${hiddenMetrics}`);
    if (await page.locator('.report-more-content-v6436 .report-bio').count() !== 1) errors.push(`${lang}:BIO_NOT_MOVED`);
    if (await page.locator('.report-more-content-v6436 .report-comparison').count() !== 1) errors.push(`${lang}:COMPARISON_NOT_MOVED`);
    if (await page.locator('.report-more-content-v6436 .report-disclaimer').count() !== 1) errors.push(`${lang}:DISCLAIMER_NOT_MOVED`);
    const collapsedHeight = await page.locator('.report-preview-v2').evaluate(el=>el.getBoundingClientRect().height);
    if (lang==='es') await page.screenshot({path:path.join(EVIDENCE,'home-es-iri-collapsed-390.png'),fullPage:true});
    await detail.locator('summary').focus();
    await page.keyboard.press('Enter');
    if (!(await detail.evaluate(el=>el.open))) errors.push(`${lang}:KEYBOARD_OPEN_FAILED`);
    const expandedHeight = await page.locator('.report-preview-v2').evaluate(el=>el.getBoundingClientRect().height);
    if (expandedHeight - collapsedHeight < 180) errors.push(`${lang}:COMPACTION_TOO_SMALL:${collapsedHeight}:${expandedHeight}`);
    if (lang==='es') await page.screenshot({path:path.join(EVIDENCE,'home-es-iri-expanded-390.png'),fullPage:true});
    await page.close();
  }
  await context.close();

  for (const route of ['/','/en/']) {
    const noJs = await browser.newContext({ viewport:{width:390,height:844}, javaScriptEnabled:false });
    const page = await noJs.newPage();
    await page.goto(BASE + route, { waitUntil:'domcontentloaded' });
    if (await page.locator('.report-more-v6436').count() !== 0) errors.push(`${route}:NOJS_DETAIL_PRESENT`);
    if (await page.locator('.report-preview-v2 .report-bio').count() !== 1) errors.push(`${route}:NOJS_BIO_MISSING`);
    const metrics = await page.locator('.report-preview-v2 .report-metric').count();
    if (metrics < 4) errors.push(`${route}:NOJS_METRICS_${metrics}`);
    const overflow = await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
    if (overflow > 2) errors.push(`${route}:NOJS_OVERFLOW_${overflow}`);
    await noJs.close();
  }

  await browser.close();
  if (errors.length) {
    console.error(errors.join('\n'));
    process.exit(1);
  }
  console.log(JSON.stringify({routes:routes.length,viewports:2,homeDisclosure:'ok',noJsFallback:'ok'}));
})().catch(err=>{console.error(err);process.exit(1)});
