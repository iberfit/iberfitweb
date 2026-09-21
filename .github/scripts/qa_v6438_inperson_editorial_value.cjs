const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const ROOT=path.resolve('candidate/v628');
const BASE='http://127.0.0.1:4176';
const EVIDENCE='/tmp/v6438-evidence';
fs.mkdirSync(EVIDENCE,{recursive:true});
function files(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{const p=path.join(dir,e.name);return e.isDirectory()?files(p):(e.isFile()&&e.name.endsWith('.html')?[p]:[])});}
function routeFor(file){const rel=path.relative(ROOT,file).split(path.sep).join('/');if(rel==='index.html')return '/';if(rel==='404.html')return '/404.html';return '/'+rel.replace(/index\.html$/,'');}
(async()=>{
  const htmls=files(ROOT).sort();if(htmls.length!==33)throw new Error(`EXPECTED_33_HTML:${htmls.length}`);
  const routes=htmls.map(routeFor),errors=[];
  const browser=await chromium.launch({headless:true});
  for(const vp of [{width:390,height:844,name:'mobile'},{width:1440,height:900,name:'desktop'}]){
    const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height}});
    for(const route of routes){
      const page=await ctx.newPage(),errs=[];page.on('pageerror',e=>errs.push(String(e)));page.on('console',m=>{if(m.type()==='error')errs.push(`console:${m.text()}`)});
      const res=await page.goto(BASE+route,{waitUntil:'networkidle'});if(!res||!res.ok())errors.push(`${vp.name}:${route}:HTTP_${res?.status()}`);
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);if(overflow>2)errors.push(`${vp.name}:${route}:OVERFLOW_${overflow}`);
      if(errs.length)errors.push(`${vp.name}:${route}:${errs.join('|')}`);await page.close();
    }
    await ctx.close();
  }
  for(const [route,lang] of [['/presencial/','es'],['/en/in-person/','en']]){
    for(const vp of [{width:390,height:844,name:'mobile'},{width:1440,height:900,name:'desktop'}]){
      const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height}});const page=await ctx.newPage();await page.goto(BASE+route,{waitUntil:'networkidle'});
      const grid=page.locator('.deliverable-grid'),items=grid.locator(':scope > .deliverable');
      if(await items.count()!==4)errors.push(`${lang}:${vp.name}:DELIVERABLE_COUNT_${await items.count()}`);
      await grid.scrollIntoViewIfNeeded();
      const metrics=await grid.evaluate(el=>{const s=getComputedStyle(el),first=getComputedStyle(el.firstElementChild),r=el.getBoundingClientRect();return {display:s.display,columns:s.gridTemplateColumns,height:r.height,firstRadius:first.borderRadius,firstBg:first.backgroundColor};});
      if(metrics.display!=='grid')errors.push(`${lang}:${vp.name}:DISPLAY_${metrics.display}`);
      if(metrics.firstRadius!=='0px')errors.push(`${lang}:${vp.name}:RADIUS_${metrics.firstRadius}`);
      if(vp.name==='mobile'){
        if(metrics.height>700)errors.push(`${lang}:MOBILE_TOO_TALL_${metrics.height}`);
        if(metrics.columns.trim().split(/\s+/).length!==1)errors.push(`${lang}:MOBILE_COLUMNS_${metrics.columns}`);
      }else{
        if(metrics.height>520)errors.push(`${lang}:DESKTOP_TOO_TALL_${metrics.height}`);
        if(metrics.columns.trim().split(/\s+/).length!==2)errors.push(`${lang}:DESKTOP_COLUMNS_${metrics.columns}`);
      }
      if(lang==='es')await page.screenshot({path:path.join(EVIDENCE,`presencial-${vp.name}.png`),fullPage:true});
      await ctx.close();
    }
  }
  await browser.close();
  if(errors.length){console.error(errors.join('\n'));process.exit(1)}
  console.log(JSON.stringify({routes:routes.length,inPersonPages:2,viewports:2,editorialGrid:'ok'}));
})().catch(e=>{console.error(e);process.exit(1)});
