import { chromium } from 'playwright';
import fs from 'node:fs';

const base=process.env.BASE_URL||'http://127.0.0.1:4173';
const out=process.env.QA_OUT||'/tmp/v64321-screens';
fs.mkdirSync(out,{recursive:true});
const routes=[
'/','/presencial/','/hibrido/','/online/','/entrenador-personal-las-condes/','/entrenador-personal-vitacura/','/entrenador-personal-lo-barnechea/','/entrenador-personal-penalolen/','/personal-trainer-nunoa/','/entrenador-personal-la-reina/',
'/en/','/en/in-person/','/en/hybrid/','/en/online/','/en/personal-trainer-las-condes/','/en/personal-trainer-vitacura/','/en/personal-trainer-lo-barnechea/','/en/personal-trainer-penalolen/','/en/personal-trainer-nunoa/','/en/personal-trainer-la-reina/'
];
const localHybrid={
'/entrenador-personal-las-condes/':'/hibrido/','/entrenador-personal-vitacura/':'/hibrido/','/entrenador-personal-lo-barnechea/':'/hibrido/','/entrenador-personal-penalolen/':'/hibrido/','/personal-trainer-nunoa/':'/hibrido/','/entrenador-personal-la-reina/':'/hibrido/',
'/en/personal-trainer-las-condes/':'/en/hybrid/','/en/personal-trainer-vitacura/':'/en/hybrid/','/en/personal-trainer-lo-barnechea/':'/en/hybrid/','/en/personal-trainer-penalolen/':'/en/hybrid/','/en/personal-trainer-nunoa/':'/en/hybrid/','/en/personal-trainer-la-reina/':'/en/hybrid/'
};
const browser=await chromium.launch({headless:true}); const metrics=[];
for(const width of [390,768,1440]){
 const context=await browser.newContext({viewport:{width,height:1000}});
 for(const route of routes){
  const page=await context.newPage(); const errors=[]; page.on('pageerror',e=>errors.push(String(e)));
  const response=await page.goto(base+route,{waitUntil:'networkidle'});
  if(!response?.ok()) throw Error(`HTTP ${route} ${response?.status()}`);
  const s=await page.evaluate(()=>{
   const d=document.documentElement,scope=document.querySelector('.scope-note');
   const scopeLink=scope?.querySelector('a'); const r=scopeLink?.getBoundingClientRect();
   const styles=[...document.styleSheets].map(x=>x.href||'').join('\n');
   return {overflow:d.scrollWidth-d.clientWidth,loaded:styles.includes('contrast.v64321.css'),text:document.body.innerText,
    scopeHref:scopeLink?.getAttribute('href')||null,scopeLabel:scopeLink?.textContent?.trim()||null,scopeText:scope?.innerText||null,
    scopeP:scope?getComputedStyle(scope.querySelector('p')).color:null,scopeSpan:scope?getComputedStyle(scope.querySelector('span')).color:null,
    scopeBorder:scope?getComputedStyle(scope).borderTopColor:null,scopeBg:scope?getComputedStyle(scope).backgroundColor:null,
    scopeTarget:r?{w:r.width,h:r.height}:null};
  });
  if(!s.loaded||s.overflow>2||errors.length) throw Error(`QA ${route} ${width} ${JSON.stringify({...s,text:undefined,errors})}`);
  if(localHybrid[route]){
   if(s.scopeHref!==localHybrid[route]||!/h[ií]brid/i.test(s.scopeLabel||'')) throw Error(`SEMANTIC ${route} ${width} ${JSON.stringify(s)}`);
   if(s.scopeP!=='rgb(68, 86, 76)') throw Error(`SCOPE_TEXT ${route} ${width} ${s.scopeP}`);
   if(s.scopeSpan!=='rgb(128, 98, 22)') throw Error(`SCOPE_GOLD ${route} ${width} ${s.scopeSpan}`);
   if(width<=768 && s.scopeTarget && (s.scopeTarget.h<44||s.scopeTarget.w<44)) throw Error(`TOUCH ${route} ${width} ${JSON.stringify(s.scopeTarget)}`);
  }
  if(route==='/'&&(s.text.includes('Según cobertura presencial')||!s.text.includes('En estas comunas + seguimiento a distancia'))) throw Error('HOME_ES_COPY');
  if(route==='/en/'&&(s.text.includes('Where in-person coverage allows')||!s.text.includes('In these areas + remote support'))) throw Error('HOME_EN_COPY');
  if(route==='/entrenador-personal-las-condes/'&&s.text.includes('Primero vemos si podemos hacerlo bien')) throw Error('LAS_CONDES_OLD');
  if(route==='/entrenador-personal-vitacura/'&&!s.scopeText?.includes('guiar el resto con el mismo plan')) throw Error('VITACURA_SCOPE');
  metrics.push({route,width,overflow:s.overflow,scopeHref:s.scopeHref,scopeLabel:s.scopeLabel,scopeP:s.scopeP,scopeSpan:s.scopeSpan,scopeBorder:s.scopeBorder,scopeBg:s.scopeBg,scopeTarget:s.scopeTarget});
  if(width===390||width===1440){
   const slug=route==='/'?'home-es':route==='/en/'?'home-en':route.replace(/^\/+|\/+$/g,'').replaceAll('/','-');
   await page.screenshot({path:`${out}/${slug}-${width}.png`,fullPage:true});
  }
  await page.close();
 }
 await context.close();
}
await browser.close();
fs.writeFileSync(`${out}/metrics.json`,JSON.stringify(metrics,null,2));
console.log('BROWSER_OK',metrics.length);
