import { chromium } from 'playwright';
import axe from 'axe-core';
import fs from 'node:fs';
import assert from 'node:assert/strict';

const base = new URL(process.env.BASE_URL || 'http://127.0.0.1:4173');
const out = process.env.QA_OUT || '/tmp/pages-live-qa';
fs.mkdirSync(out,{recursive:true});
const origin = base.origin;
const versionResponse=await fetch(new URL('/VERSION?release_audit='+encodeURIComponent(process.env.GITHUB_RUN_ID||'local'),base));
assert(versionResponse.ok,'VERSION unavailable');
const observedVersion=(await versionResponse.text()).trim();
assert(/^\d+\.\d+\.\d+$/.test(observedVersion),'invalid VERSION');
if(process.env.EXPECTED_VERSION)assert.equal(observedVersion,process.env.EXPECTED_VERSION,'published VERSION mismatch');
const [major,minor,patch]=observedVersion.split('.').map(Number);
const identity2027=major>6||(major===6&&(minor>43||(minor===43&&patch>=36)));
const identityNorte=major>6||(major===6&&(minor>43||(minor===43&&patch>=37)));
const strictA11y=major>6||(major===6&&(minor>43||(minor===43&&patch>=33)));
const sitemap = await fetch(new URL('/sitemap.xml',base));
assert(sitemap.ok,'sitemap unavailable');
const xml=await sitemap.text();
const routes=[...xml.matchAll(/<loc>(https:\/\/iberfit\.cl\/[^<]*)<\/loc>/g)].map(x=>new URL(x[1]).pathname);
assert(routes.length>0 && new Set(routes).size===routes.length,'invalid sitemap routes');
const widths=[390,768,1440];
const representative=new Set(['/','/metodo/','/diagnostico-iri/','/contacto/','/presencial/','/hibrido/','/online/','/en/','/en/method/','/en/iri-assessment/','/en/contact/']);
const browser=await chromium.launch({headless:true});
const results=[],failures=[];
try{
  for(const width of widths){
    const context=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1});
    // Never send synthetic test traffic to external analytics or WhatsApp.
    await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
    await context.addInitScript(()=>{
      localStorage.setItem('iberfit_consent_v2',JSON.stringify({version:'2026-07-12-v2',necessary:true,analytics:false,marketing:false}));
      window.__releaseVitals={lcp:0,cls:0};
      try{
        new PerformanceObserver(list=>{for(const e of list.getEntries())window.__releaseVitals.lcp=e.startTime;}).observe({type:'largest-contentful-paint',buffered:true});
        new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)window.__releaseVitals.cls+=e.value;}).observe({type:'layout-shift',buffered:true});
      }catch{}
    });
    for(const route of routes){
      const page=await context.newPage();
      const errors=[],assets=[];
      page.on('pageerror',e=>errors.push(String(e)));
      page.on('response',r=>{
        const type=r.request().resourceType();
        if(new URL(r.url()).origin===origin && r.status()>=400 && ['script','stylesheet','font','image'].includes(type))assets.push({status:r.status(),url:new URL(r.url()).pathname});
      });
      try{
        const response=await page.goto(new URL(route,base).href,{waitUntil:'load',timeout:25000});
        assert(response?.ok(),'non-success navigation');
        await page.evaluate(()=>document.fonts.ready);
        const state=await page.evaluate(()=>{
          const n=performance.getEntriesByType('navigation')[0];
          return {
            h1:document.querySelectorAll('h1').length,
            lang:document.documentElement.lang,
            overflow:Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth),
            focusables:[...document.querySelectorAll('a[href],button,input,select,textarea')].filter(x=>x.getClientRects().length).length,
            ttfb:n?Math.round(n.responseStart):null,
            domReady:n?Math.round(n.domContentLoadedEventEnd):null,
            load:n?Math.round(n.loadEventEnd):null,
            transferBytes:performance.getEntriesByType('resource').reduce((s,x)=>s+(x.transferSize||0),n?.transferSize||0),
            lcp:Math.round(window.__releaseVitals.lcp),
            cls:Number(window.__releaseVitals.cls.toFixed(4))
          };
        });
        if (major>6||(major===6&&(minor>43||(minor===43&&patch>=35)))) {
          assert.equal(await page.locator('.local-place-badge').count(),0,'obsolete local badge');
        }
        if(identity2027){
          const marks=page.locator('img.brand-mark');
          assert.equal(await marks.count(),2,'header/footer marks');
          for(let i=0;i<await marks.count();i++){
            const mark=marks.nth(i);
            await mark.evaluate(e=>e.decode());
            assert(await mark.evaluate((e,norte)=>{const path=new URL(e.currentSrc).pathname;return e.complete&&e.naturalWidth>0&&e.naturalHeight>0&&getComputedStyle(e).objectFit==='contain'&&(norte?Math.abs(e.naturalWidth/e.naturalHeight-660/140)<.05&&path==='/assets/iberfit-firma-norte-'+(e.closest('.site-footer')?'oscuro':'claro')+'.svg':e.naturalWidth===e.naturalHeight&&path==='/assets/iberfit-isotipo-2027.svg')},identityNorte),'brand geometry or source');
          }
          if(route==='/'&&width===390){
            const icons=await page.evaluate(async()=>{
              const m=await (await fetch('/manifest.webmanifest')).json();
              return Promise.all(m.icons.map(async i=>{
                const r=await fetch(i.src);if(!r.ok)throw Error(i.src);
                const b=await createImageBitmap(await r.blob());
                const size=b.width+'x'+b.height;b.close();return [i.src,size,i.sizes,i.purpose];
              }));
            });
            assert.equal(icons.length,identityNorte?4:2);
            for(const [src,size,declared,purpose] of icons){assert(identityNorte?/\/(?:favicon-norte-|icon-norte-maskable-)/.test(src):src.includes('favicon-2027-'));assert.equal(size,declared);if(identityNorte)assert(['any','maskable'].includes(purpose))}
            if(identityNorte)assert.equal(icons.filter(i=>i[3]==='maskable').length,2);
          }
        }
        assert.equal(state.h1,1,'H1 count');
        assert.equal(state.lang,route.startsWith('/en/')?'en':'es','language');
        assert(state.overflow<=2,'horizontal overflow: '+state.overflow);
        assert(state.focusables>0,'no interactive content');
        assert.equal(errors.length,0,'JavaScript error: '+errors.join(' | '));
        assert.equal(assets.length,0,'essential asset error: '+JSON.stringify(assets));
        // Broad synthetic failure budgets, not claims of field Core Web Vitals.
        assert(state.domReady!==null && state.domReady<=15000,'DOM readiness budget');
        let accessibility=[];
        if(strictA11y || (representative.has(route) && width!==768)){
          await page.evaluate(axe.source);
          const report=await page.evaluate(async()=>window.axe.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
          accessibility=report.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length,targets:v.nodes.map(n=>n.target)}));
        }
        let keyboardChecks=0;
        if(strictA11y){
          const rails=page.locator('[data-a11y-scroll="true"]');
          for(let i=0;i<await rails.count();i++){
            const rail=rails.nth(i);
            await rail.focus();
            assert(await rail.evaluate(e=>document.activeElement===e && e.tabIndex===0 && !!(e.getAttribute('aria-label')||e.getAttribute('aria-labelledby'))),'rail focus or name');
            await page.keyboard.press('Home');
            await page.keyboard.press('ArrowRight');
            await page.waitForFunction(e=>e.scrollLeft>2,await rail.elementHandle(),{timeout:2000});
            await page.keyboard.press('End');
            await page.waitForFunction(e=>e.scrollWidth-e.clientWidth-e.scrollLeft<=3,await rail.elementHandle(),{timeout:2000});
            await page.keyboard.press('Home');
            await page.waitForFunction(e=>e.scrollLeft<=3,await rail.elementHandle(),{timeout:2000});
            keyboardChecks++;
          }
        }
        if(identity2027&&route==='/'&&(width===390||width===1440)){
          await page.locator('.site-header .brand').screenshot({path:out+'/brand-'+width+'.png'});
          await page.locator('.site-footer .footer-brand').screenshot({path:out+'/footer-brand-'+width+'.png'});
        }
        results.push({route,width,...state,accessibility,keyboardChecks});
      }catch(e){
        failures.push({route,width,error:String(e),errors,assets});
      }finally{await page.close();}
    }
    await context.close();
  }
}finally{await browser.close();}
const accessibility=results.flatMap(x=>x.accessibility.map(v=>({route:x.route,width:x.width,...v})));
const report={origin,observedVersion,strictA11y,routeCount:routes.length,viewportCount:widths.length,results,failures,accessibility,notes:'Synthetic Chromium audit with third-party traffic blocked. Axe violations and timing measurements are reported; this is not a field CWV or manual WCAG certification.'};
fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));
console.log('PAGES_BROWSER_360',JSON.stringify({routes:routes.length,checks:results.length,failures:failures.length,keyboardChecks:results.reduce((sum,x)=>sum+x.keyboardChecks,0),axeViolations:accessibility.length,critical:accessibility.filter(x=>x.impact==='critical').length,serious:accessibility.filter(x=>x.impact==='serious').length}));
if(failures.length)throw new Error(JSON.stringify(failures.slice(0,10)));
if(strictA11y){
  assert(results.some(x=>x.keyboardChecks>0),'keyboard checks missing');
  assert.equal(accessibility.length,0,'Accessibility regression: '+JSON.stringify(accessibility.slice(0,8)));
}
