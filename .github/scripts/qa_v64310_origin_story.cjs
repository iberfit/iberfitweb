const { chromium } = require('playwright');
const fs=require('fs'),path=require('path');
const ROOT=path.resolve('candidate/v628'),BASE='http://127.0.0.1:4178',EVIDENCE='/tmp/v64310-evidence';
fs.mkdirSync(EVIDENCE,{recursive:true});
function files(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{const p=path.join(dir,e.name);return e.isDirectory()?files(p):(e.isFile()&&e.name.endsWith('.html')?[p]:[])});}
function routeFor(file){const rel=path.relative(ROOT,file).split(path.sep).join('/');if(rel==='index.html')return '/';if(rel==='404.html')return '/404.html';return '/'+rel.replace(/index\.html$/,'');}
const consent={version:'2026-07-12-v2',analytics:false,marketing:false,updatedAt:'2026-09-22T00:00:00.000Z'};
(async()=>{
  const htmls=files(ROOT).sort();if(htmls.length!==33)throw new Error(`EXPECTED_33_HTML:${htmls.length}`);
  const routes=htmls.map(routeFor),errors=[];const browser=await chromium.launch({headless:true});
  for(const vp of [{width:390,height:844,name:'mobile'},{width:1440,height:900,name:'desktop'}]){
    const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height}});
    await ctx.addInitScript(c=>localStorage.setItem('iberfit_consent_v2',JSON.stringify(c)),consent);
    for(const route of routes){
      const page=await ctx.newPage(),errs=[];page.on('pageerror',e=>errs.push(String(e)));page.on('console',m=>{if(m.type()==='error')errs.push(`console:${m.text()}`)});
      const res=await page.goto(BASE+route,{waitUntil:'networkidle'});if(!res||!res.ok())errors.push(`${vp.name}:${route}:HTTP_${res?.status()}`);
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);if(overflow>2)errors.push(`${vp.name}:${route}:OVERFLOW_${overflow}`);
      if(errs.length)errors.push(`${vp.name}:${route}:${errs.join('|')}`);await page.close();
    }
    await ctx.close();
  }
  for(const spec of [
    {route:'/sobre-iberfit/',lang:'es',title:'Antes de ser un método, IBERFIT fue una inquietud',manifesto:'El método solo merece la pena',need:'¿qué necesita esta persona, hoy, para avanzar con sentido?',old:'un entrenador español'},
    {route:'/en/about/',lang:'en',title:'Before it became a method, IBERFIT began with a question',manifesto:'A method is only worthwhile',need:'what does this person need, today, to move forward with purpose?',old:'Spanish trainer'}
  ]){
    for(const vp of [{width:390,height:844,name:'mobile'},{width:1440,height:900,name:'desktop'}]){
      const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height}});await ctx.addInitScript(c=>localStorage.setItem('iberfit_consent_v2',JSON.stringify(c)),consent);const page=await ctx.newPage();
      await page.goto(BASE+spec.route,{waitUntil:'networkidle'});
      const text=await page.locator('.origin-section').innerText();
      if(!text.includes(spec.title))errors.push(`${spec.lang}:${vp.name}:MISSING_TITLE`);
      if(!text.includes(spec.manifesto))errors.push(`${spec.lang}:${vp.name}:MISSING_MANIFESTO`);
      if(!text.includes(spec.need))errors.push(`${spec.lang}:${vp.name}:MISSING_PERSON_QUESTION`);
      if(text.toLowerCase().includes(spec.old.toLowerCase()))errors.push(`${spec.lang}:${vp.name}:OLD_FOUNDER_FRAMING`);
      const css=await page.locator('link[href="/assets/story.v64310.css"]').count();if(css!==1)errors.push(`${spec.lang}:${vp.name}:CSS_${css}`);
      const cards=await page.locator('.brand-journey--story article').count();if(cards!==4)errors.push(`${spec.lang}:${vp.name}:JOURNEY_${cards}`);
      const manifest=await page.locator('.origin-manifesto').evaluate(el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return {w:r.width,h:r.height,display:s.display}});if(manifest.w<250||manifest.h<80)errors.push(`${spec.lang}:${vp.name}:MANIFESTO_GEOMETRY_${JSON.stringify(manifest)}`);
      if(vp.name==='mobile'){
        const rail=page.locator('.brand-journey--story');await rail.scrollIntoViewIfNeeded();
        const state=await rail.evaluate(el=>({sw:el.scrollWidth,cw:el.clientWidth,snap:getComputedStyle(el).scrollSnapType}));
        if(state.sw<=state.cw+40||!state.snap.includes('x'))errors.push(`${spec.lang}:mobile:RAIL_${JSON.stringify(state)}`);
      }
      await page.locator('.origin-section').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(EVIDENCE,`${spec.lang}-${vp.name}-origin.png`),fullPage:false});await ctx.close();
    }
  }
  await browser.close();
  if(errors.length){console.error(errors.join('\n'));process.exit(1)}
  console.log(JSON.stringify({routes:routes.length,viewports:2,aboutPages:2,story:'ok',mobileRail:'ok'}));
})().catch(e=>{console.error(e);process.exit(1)});
