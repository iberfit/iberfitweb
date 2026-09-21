const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve('candidate/v628');
const BASE = 'http://127.0.0.1:4175';
const EVIDENCE='/tmp/v6437-evidence';
fs.mkdirSync(EVIDENCE,{recursive:true});
function files(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{const p=path.join(dir,e.name);return e.isDirectory()?files(p):(e.isFile()&&e.name.endsWith('.html')?[p]:[])});}
function routeFor(file){const rel=path.relative(ROOT,file).split(path.sep).join('/');if(rel==='index.html')return '/';if(rel==='404.html')return '/404.html';return '/'+rel.replace(/index\.html$/,'');}
(async()=>{
  const htmls=files(ROOT).sort();
  if(htmls.length!==33) throw new Error(`EXPECTED_33_HTML:${htmls.length}`);
  const routes=htmls.map(routeFor);
  const targetRoutes=htmls.filter(f=>{const t=fs.readFileSync(f,'utf8');return t.includes('answer-section')&&t.includes('answer-item')}).map(routeFor);
  if(!targetRoutes.length) throw new Error('NO_AEO_TARGET_ROUTES');
  const browser=await chromium.launch({headless:true});
  const errors=[];

  for(const vp of [{width:390,height:844,name:'mobile'},{width:1440,height:900,name:'desktop'}]){
    const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height}});
    for(const route of routes){
      const page=await ctx.newPage();const errs=[];
      page.on('pageerror',e=>errs.push(String(e)));
      page.on('console',m=>{if(m.type()==='error')errs.push(`console:${m.text()}`)});
      const res=await page.goto(BASE+route,{waitUntil:'networkidle'});
      if(!res||!res.ok())errors.push(`${vp.name}:${route}:HTTP_${res?.status()}`);
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
      if(overflow>2)errors.push(`${vp.name}:${route}:OVERFLOW_${overflow}`);
      if(errs.length)errors.push(`${vp.name}:${route}:${errs.join('|')}`);
      await page.close();
    }
    await ctx.close();
  }

  for(const route of targetRoutes){
    const noJs=await browser.newContext({viewport:{width:390,height:844},javaScriptEnabled:false});
    const p0=await noJs.newPage();await p0.goto(BASE+route,{waitUntil:'domcontentloaded'});
    const sourceCount=await p0.locator('.answer-list > .answer-item').count();
    if(sourceCount<1)errors.push(`${route}:NOJS_SOURCE_COUNT_${sourceCount}`);
    if(await p0.locator('.answer-disclosure-v6437').count())errors.push(`${route}:NOJS_DISCLOSURE_PRESENT`);
    await noJs.close();

    const ctx=await browser.newContext({viewport:{width:390,height:844}});
    const page=await ctx.newPage();await page.goto(BASE+route,{waitUntil:'networkidle'});
    const details=page.locator('.answer-list > details.answer-disclosure-v6437');
    const count=await details.count();
    if(count!==sourceCount)errors.push(`${route}:DETAIL_COUNT_${count}_SOURCE_${sourceCount}`);
    if(await page.locator('.answer-list > .answer-item').count())errors.push(`${route}:LEGACY_ITEMS_REMAIN`);
    if(await page.locator('.answer-section[data-aeo-v6437="1"]').count()<1)errors.push(`${route}:SECTION_NOT_ENHANCED`);
    if(count>0){
      const first=details.nth(0);await first.locator('summary').focus();await page.keyboard.press('Enter');
      if(!(await first.evaluate(el=>el.open)))errors.push(`${route}:KEYBOARD_OPEN_FAILED`);
      if(count>1){const second=details.nth(1);await second.locator('summary').click();if(!(await second.evaluate(el=>el.open)))errors.push(`${route}:SECOND_OPEN_FAILED`);if(await first.evaluate(el=>el.open))errors.push(`${route}:FIRST_NOT_CLOSED`);}
    }
    if(route==='/')await page.screenshot({path:path.join(EVIDENCE,'home-es-aeo-disclosure-390.png'),fullPage:true});
    await ctx.close();
  }
  await browser.close();
  if(errors.length){console.error(errors.join('\n'));process.exit(1)}
  console.log(JSON.stringify({routes:routes.length,targetRoutes:targetRoutes.length,progressiveDisclosure:'ok'}));
})().catch(e=>{console.error(e);process.exit(1)});
