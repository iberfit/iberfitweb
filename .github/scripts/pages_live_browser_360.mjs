import { chromium } from 'playwright';
import axe from 'axe-core';
import fs from 'node:fs';
import assert from 'node:assert/strict';

const base = new URL(process.env.BASE_URL || 'http://127.0.0.1:4173');
const out = process.env.QA_OUT || '/tmp/pages-live-qa';
fs.mkdirSync(out,{recursive:true});
const origin = base.origin;
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
        assert.equal(state.h1,1,'H1 count');
        assert.equal(state.lang,route.startsWith('/en/')?'en':'es','language');
        assert(state.overflow<=2,'horizontal overflow: '+state.overflow);
        assert(state.focusables>0,'no interactive content');
        assert.equal(errors.length,0,'JavaScript error: '+errors.join(' | '));
        assert.equal(assets.length,0,'essential asset error: '+JSON.stringify(assets));
        // Broad synthetic failure budgets, not claims of field Core Web Vitals.
        assert(state.domReady!==null && state.domReady<=15000,'DOM readiness budget');
        let accessibility=[];
        if(representative.has(route) && width!==768){
          await page.addScriptTag({content:axe.source});
          const report=await page.evaluate(async()=>window.axe.run({runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
          accessibility=report.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}));
        }
        results.push({route,width,...state,accessibility});
      }catch(e){
        failures.push({route,width,error:String(e),errors,assets});
      }finally{await page.close();}
    }
    await context.close();
  }
}finally{await browser.close();}
const accessibility=results.flatMap(x=>x.accessibility.map(v=>({route:x.route,width:x.width,...v})));
const report={origin,routeCount:routes.length,viewportCount:widths.length,results,failures,accessibility,notes:'Synthetic Chromium audit with third-party traffic blocked. Axe violations and timing measurements are reported; this is not a field CWV or manual WCAG certification.'};
fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));
console.log('PAGES_BROWSER_360',JSON.stringify({routes:routes.length,checks:results.length,failures:failures.length,axeViolations:accessibility.length,critical:accessibility.filter(x=>x.impact==='critical').length,serious:accessibility.filter(x=>x.impact==='serious').length}));
if(failures.length)throw new Error(JSON.stringify(failures.slice(0,10)));
