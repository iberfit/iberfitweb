const { chromium } = require('playwright');
const fs=require('fs'),path=require('path');
const ROOT=path.resolve('candidate/v628'),BASE='http://127.0.0.1:4177',EVIDENCE='/tmp/v6439-evidence';
fs.mkdirSync(EVIDENCE,{recursive:true});
function files(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>{const p=path.join(dir,e.name);return e.isDirectory()?files(p):(e.isFile()&&e.name.endsWith('.html')?[p]:[])});}
function routeFor(file){const rel=path.relative(ROOT,file).split(path.sep).join('/');if(rel==='index.html')return '/';if(rel==='404.html')return '/404.html';return '/'+rel.replace(/index\.html$/,'');}
const consent={version:'2026-07-12-v2',analytics:false,marketing:false,updatedAt:'2026-09-21T00:00:00.000Z'};
const seedConsent=()=>{localStorage.setItem('iberfit_consent_v2',JSON.stringify({version:'2026-07-12-v2',analytics:false,marketing:false,updatedAt:'2026-09-21T00:00:00.000Z'}));};
(async()=>{
 const htmls=files(ROOT).sort();if(htmls.length!==33)throw new Error(`EXPECTED_33_HTML:${htmls.length}`);
 const routes=htmls.map(routeFor),errors=[];const browser=await chromium.launch({headless:true});
 for(const vp of [{width:390,height:844,name:'mobile'},{width:1440,height:900,name:'desktop'}]){
   const ctx=await browser.newContext({viewport:{width:vp.width,height:vp.height}});await ctx.addInitScript(seedConsent);
   for(const route of routes){
     const page=await ctx.newPage(),errs=[];page.on('pageerror',e=>errs.push(String(e)));page.on('console',m=>{if(m.type()==='error')errs.push(`console:${m.text()}`)});
     const res=await page.goto(BASE+route,{waitUntil:'networkidle'});if(!res||!res.ok())errors.push(`${vp.name}:${route}:HTTP_${res?.status()}`);
     const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);if(overflow>2)errors.push(`${vp.name}:${route}:OVERFLOW_${overflow}`);
     const refs=await page.evaluate(()=>({css:[...document.querySelectorAll('link[href="/assets/chrome.v6439.css"]')].length,js:[...document.querySelectorAll('script[src="/assets/chrome.v6439.js"]')].length}));
     if(refs.css!==1||refs.js!==1)errors.push(`${vp.name}:${route}:REFS_${JSON.stringify(refs)}`);
     if(errs.length)errors.push(`${vp.name}:${route}:${errs.join('|')}`);await page.close();
   } await ctx.close();
 }
 // Fresh consent must outrank the mobile dock.
 {
   const ctx=await browser.newContext({viewport:{width:390,height:844}});const page=await ctx.newPage();await page.goto(BASE+'/',{waitUntil:'networkidle'});
   await page.waitForSelector('.consent-banner');await page.evaluate(()=>scrollTo(0,Math.min(900,document.body.scrollHeight/3)));
   await page.waitForFunction(()=>document.querySelector('.device-dock')?.classList.contains('is-visible'));
   await page.waitForFunction(()=>document.querySelector('.device-dock')?.dataset.dockSuppressed?.includes('consent'));
   const consentState=await page.locator('.device-dock').evaluate(el=>({suppressed:el.classList.contains('dock-suppressed-v6439'),hidden:el.getAttribute('aria-hidden'),inert:el.inert,reasons:el.dataset.dockSuppressed||''}));
   if(!consentState.suppressed||consentState.hidden!=='true'||!consentState.inert||!consentState.reasons.includes('consent'))errors.push(`CONSENT_PRIORITY_${JSON.stringify(consentState)}`);
   await page.screenshot({path:path.join(EVIDENCE,'home-consent-dock-suppressed-390.png'),fullPage:false});
   await page.click('[data-consent-necessary]');await page.waitForSelector('.consent-banner',{state:'detached'});
   await page.waitForFunction(()=>{const d=document.querySelector('.device-dock');return d?.classList.contains('is-visible')&&!d.classList.contains('dock-suppressed-v6439')&&!d.inert});
   await page.screenshot({path:path.join(EVIDENCE,'home-dock-normal-390.png'),fullPage:false});
   // Menu wins over the dock and closing it restores the dock.
   await page.click('[data-menu-toggle]');await page.waitForFunction(()=>document.body.classList.contains('nav-panel-open'));
   await page.waitForFunction(()=>document.querySelector('.device-dock')?.dataset.dockSuppressed?.includes('menu'));
   await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.body.classList.contains('nav-panel-open'));
   await page.waitForFunction(()=>{const d=document.querySelector('.device-dock');return d?.classList.contains('is-visible')&&!d.classList.contains('dock-suppressed-v6439')});
   // Final conversion surface wins over the dock.
   await page.locator('.cta-panel').scrollIntoViewIfNeeded();
   await page.waitForFunction(()=>document.querySelector('.device-dock')?.dataset.dockSuppressed?.includes('cta'));
   await page.screenshot({path:path.join(EVIDENCE,'home-final-cta-dock-suppressed-390.png'),fullPage:false});
   await page.locator('.site-footer').scrollIntoViewIfNeeded();
   await page.waitForFunction(()=>document.querySelector('.device-dock')?.dataset.dockSuppressed?.includes('footer'));
   await ctx.close();
 }
 // Editing state: exercise the real Contact select after making the native control visible in the QA DOM.
 {
   const ctx=await browser.newContext({viewport:{width:390,height:844}});await ctx.addInitScript(seedConsent);const page=await ctx.newPage();await page.goto(BASE+'/contacto/',{waitUntil:'networkidle'});
   await page.locator('#orientador').scrollIntoViewIfNeeded();await page.waitForFunction(()=>document.querySelector('.device-dock')?.classList.contains('is-visible'));
   await page.evaluate(()=>{const s=document.querySelector('#objetivo');s.classList.remove('is-enhanced');s.style.display='block';s.focus();});
   await page.waitForFunction(()=>document.querySelector('.device-dock')?.dataset.dockSuppressed?.includes('editing'));
   await page.evaluate(()=>document.querySelector('#objetivo')?.blur());
   await page.waitForFunction(()=>!((document.querySelector('.device-dock')?.dataset.dockSuppressed||'').includes('editing')));
   await ctx.close();
 }
 await browser.close();
 if(errors.length){console.error(errors.join('\n'));process.exit(1)}
 console.log(JSON.stringify({routes:routes.length,viewports:2,consent:'ok',menu:'ok',finalCta:'ok',footer:'ok',editing:'ok'}));
})().catch(e=>{console.error(e);process.exit(1)});
