import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {chromium} from 'playwright';

const root='candidate/v628',base=process.env.BASE_URL||'http://127.0.0.1:4173';
const issues=[],checks={};
function check(ok,code,detail){if(!ok)issues.push({code,detail});}
const version=(await readFile(join(root,'VERSION'),'utf8')).trim();
check(version==='6.43.28','VERSION',version);
const sitemap=await readFile(join(root,'sitemap.xml'),'utf8');
const routes=[...sitemap.matchAll(/<loc>https:\/\/iberfit\.cl([^<]+)<\/loc>/g)].map(x=>x[1]);
check(routes.length===32&&new Set(routes).size===32,'SITEMAP_COUNT',routes.length);
check(routes.filter(x=>x.startsWith('/en/')).length===16,'SITEMAP_LANG_EN',routes.length);
const css=await readFile(join(root,'assets/a11y.v64328.css'),'utf8');
check(css.includes('.answer-source-note')&&css.includes('.page-breadcrumbs'),'CONTRAST_ASSET',css.length);
const redirects=await readFile(join(root,'_redirects'),'utf8');
check(redirects.includes('/en/contacto/ /en/contact/ 301'),'LEGACY_REDIRECT','/en/contacto/');
const link='<link href="/assets/a11y.v64328.css" rel="stylesheet"/>';
for(const route of routes){
 const path=join(root,route.substring(1),'index.html');
 const html=await readFile(path,'utf8');
 const expectedLang=route.startsWith('/en/')?'en':'es';
 check(html.includes('<html lang="'+expectedLang+'"'),'LANG',route);
 check((html.match(/<h1(?:\s|>)/g)||[]).length===1,'H1',route);
 check(html.includes('https://iberfit.cl'+route+'" rel="canonical"'),'CANONICAL',route);
 check(html.includes('rel="alternate"'),'HREFLANG',route);
 check((html.match(/a11y\.v64328\.css/g)||[]).length===1,'VERSIONED_CSS',route);
 check(html.includes('<main')&&html.includes('</main>'),'MAIN',route);
 check(html.includes('<title>')&&html.includes('name="description"'),'METADATA',route);
 for(const m of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)){
   try{const ld=JSON.parse(m[1]);check(!JSON.stringify(ld).includes('"price":'),'PUBLIC_PRICE',route)}
   catch(error){issues.push({code:'JSON_LD',detail:route+': '+error.message})}
 }
}
checks.staticRoutes=routes.length;

if(process.env.BROWSER){
 const browser=await chromium.launch({headless:true,executablePath:process.env.BROWSER,args:['--no-sandbox','--disable-dev-shm-usage']});
 try {
   const context=await browser.newContext({viewport:{width:1440,height:1000},locale:'es-CL'});
   await context.addInitScript({path:'node_modules/axe-core/axe.min.js'});
   for(const route of routes){
     const page=await context.newPage();
     try{
       const response=await page.goto(base+route,{waitUntil:'domcontentloaded',timeout:25000});
       check(response?.ok(),'HTTP',route+': '+response?.status());
       await page.waitForTimeout(180);
       const result=await page.evaluate(async()=>window.axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']},resultTypes:['violations']}));
       for(const violation of result.violations){
         issues.push({code:'AXE_'+violation.id,detail:{route,impact:violation.impact,targets:violation.nodes.map(x=>x.target).slice(0,15)}});
       }
     }catch(error){issues.push({code:'AXE_ERROR',detail:route+': '+error.message})}
     finally{await page.close()}
   }
   await context.close();
   checks.axeRoutes=routes.length;
   const views=[{name:'mobile320',width:320,height:568,mobile:true},{name:'mobile390',width:390,height:844,mobile:true},{name:'tablet768',width:768,height:1024,mobile:false},{name:'desktop1440',width:1440,height:1000,mobile:false}];
   const smokeRoutes=['/','/diagnostico-iri/','/metodo/','/presencial/','/online/','/contacto/','/en/','/en/contact/'];
   let smoke=0;
   for(const view of views){
     const c=await browser.newContext({viewport:{width:view.width,height:view.height},isMobile:view.mobile,hasTouch:view.mobile});
     for(const route of smokeRoutes){
       const page=await c.newPage();
       try {
         await page.goto(base+route,{waitUntil:'domcontentloaded',timeout:25000});
         await page.waitForTimeout(120);
         const metrics=await page.evaluate(()=>({width:innerWidth,body:document.body.scrollWidth,html:document.documentElement.scrollWidth,whatsapp:document.querySelectorAll('a[href*="wa.me"]').length,broken:[...document.images].filter(x=>x.complete&&x.naturalWidth===0).length}));
         check(Math.max(metrics.body,metrics.html)-metrics.width<=2,'OVERFLOW',view.name+': '+route);
         check(metrics.whatsapp>0,'WHATSAPP',view.name+': '+route);
         check(metrics.broken===0,'BROKEN_IMAGE',view.name+': '+route+': '+metrics.broken);
         const button=page.locator('.menu-toggle'),nav=page.locator('.navlinks');
         if(view.width<=768){
           check(await button.isVisible(),'MOBILE_TOGGLE',view.name+': '+route);
           await button.click();
           await page.waitForTimeout(360);
           check(await nav.evaluate(x=>x.classList.contains('open')&&getComputedStyle(x).visibility==='visible'&&Number(getComputedStyle(x).opacity)>.05),'MOBILE_NAV',view.name+': '+route);
           check(await button.getAttribute('aria-expanded')==='true','MENU_ARIA',view.name+': '+route);
         }else{
           check(!(await button.isVisible()),'DESKTOP_TOGGLE',route);
         }
         smoke++;
       }catch(error){issues.push({code:'SMOKE_ERROR',detail:view.name+': '+route+': '+error.message})}
       finally{await page.close()}
     }
     await c.close();
   }
   checks.smokeCases=smoke;
 }finally{await browser.close()}
}
const report={schema:'iberfit.web.v64328.candidate.v1',checkedAt:new Date().toISOString(),version,checks,totalIssues:issues.length,issues};
await mkdir('evidence/v64328-candidate',{recursive:true});
await writeFile('evidence/v64328-candidate/report.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
if(issues.length)process.exit(1);
