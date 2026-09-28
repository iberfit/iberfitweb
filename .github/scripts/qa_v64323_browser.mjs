import { chromium } from 'playwright';
import fs from 'node:fs';

const base=process.env.BASE_URL||'http://127.0.0.1:4173';
const out=process.env.QA_OUT||'/tmp/v64323-screens';
fs.mkdirSync(out,{recursive:true});
const routes=['/','/en/','/hibrido/','/en/hybrid/','/presencial/','/en/in-person/','/entrenador-personal-la-reina/','/en/personal-trainer-la-reina/'];
const browser=await chromium.launch({headless:true});
const metrics=[];

for(const width of [390,768,1440]){
  const context=await browser.newContext({viewport:{width,height:1000}});
  for(const route of routes){
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.addInitScript(()=>localStorage.removeItem('iberfit_consent_v2'));
    const response=await page.goto(base+route,{waitUntil:'networkidle'});
    if(!response?.ok()) throw Error(`HTTP ${route} ${response?.status()}`);
    const state=await page.evaluate(()=>{
      const d=document.documentElement;
      const onlineLabel=document.querySelector('.modality-list .modality-row:last-child > div > span')?.textContent?.trim()||'';
      return {
        overflow:d.scrollWidth-d.clientWidth,
        height:document.body.scrollHeight,
        text:document.body.textContent||'',
        onlineLabel,
        photoStories:document.querySelectorAll('.photo-story-section').length,
        weekFlows:document.querySelectorAll('.week-flow').length,
        localStrips:document.querySelectorAll('.local-service-strip').length,
        principles:document.querySelectorAll('.principle-row').length,
        answers:document.querySelectorAll('.answer-item').length,
        appHybrid:!!document.querySelector('img[src*="app-hybrid-feedback.webp"]'),
        appPoints:document.querySelectorAll('.app-story-points > article').length,
        reportStatus:document.querySelectorAll('.report-status').length,
        whatsapp:document.querySelectorAll('a[href*="wa.me/56944040032"]').length,
        skip:!!document.querySelector('.skip'),
        header:!!document.querySelector('.site-header'),
        footer:!!document.querySelector('.site-footer'),
        localStripOff:document.body.dataset.localStrip==='off'
      };
    });
    if(errors.length) throw Error(`PAGEERROR ${route} ${width} ${errors.join(' | ')}`);
    if(state.overflow>2) throw Error(`OVERFLOW ${route} ${width} ${state.overflow}`);
    if(!state.skip||!state.header||!state.footer||state.whatsapp<1) throw Error(`SHELL ${route} ${width}`);

    if(route==='/'||route==='/en/'){
      if(state.reportStatus<1) throw Error(`IRI_REPORT ${route}`);
      const low=state.text.toLowerCase();
      if(low.includes('64 overall')||low.includes('overall index')||low.includes('overall score')) throw Error(`IRI_OLD_SCORE ${route}`);
      if(route==='/'&&state.onlineLabel!=='Online · Desde cualquier lugar') throw Error(`HOME_ONLINE_ES ${state.onlineLabel}`);
      if(route==='/en/'&&state.onlineLabel!=='Online · From anywhere') throw Error(`HOME_ONLINE_EN ${state.onlineLabel}`);
    }
    if(route==='/hibrido/'||route==='/en/hybrid/'){
      if(state.photoStories!==0||!state.appHybrid||state.appPoints!==3) throw Error(`HYBRID_PROOF ${route} ${JSON.stringify(state)}`);
      const markers=route==='/hibrido/'?['Supervisión directa','Trabajo guiado','Feedback y ajuste']:['Direct supervision','Guided work','Feedback and adjustment'];
      for(const marker of markers) if(!state.text.includes(marker)) throw Error(`HYBRID_MARKER ${route} ${marker}`);
    }
    if(route==='/presencial/'||route==='/en/in-person/'){
      if(state.weekFlows!==0||state.photoStories<1||state.localStrips<1) throw Error(`INPERSON_STRUCTURE ${route} ${JSON.stringify(state)}`);
    }
    if(route.includes('la-reina')){
      if(!state.localStripOff||state.localStrips!==0||state.principles!==3||state.answers<2) throw Error(`LA_REINA_STRUCTURE ${route} ${JSON.stringify(state)}`);
    }

    metrics.push({route,width,overflow:state.overflow,height:state.height,onlineLabel:state.onlineLabel,photoStories:state.photoStories,weekFlows:state.weekFlows,localStrips:state.localStrips,principles:state.principles,answers:state.answers,appPoints:state.appPoints,whatsapp:state.whatsapp});
    if((width===390||width===1440)&&['/','/en/','/hibrido/','/presencial/','/entrenador-personal-la-reina/'].includes(route)){
      const slug=route==='/'?'home-es':route==='/en/'?'home-en':route.split('/').filter(Boolean).pop();
      await page.screenshot({path:`${out}/${slug}-${width}.png`,fullPage:true});
    }
    await page.close();
  }
  await context.close();
}
await browser.close();
fs.writeFileSync(`${out}/metrics.json`,JSON.stringify(metrics,null,2));
console.log('BROWSER_V64323_OK',metrics.length);
