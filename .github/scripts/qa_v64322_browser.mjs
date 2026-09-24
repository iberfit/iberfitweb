import { chromium } from 'playwright';
import fs from 'node:fs';

const base=process.env.BASE_URL||'http://127.0.0.1:4173';
const out=process.env.QA_OUT||'/tmp/v64322-screens';
fs.mkdirSync(out,{recursive:true});
const routes=['/','/en/','/online/','/en/online/','/presencial/','/hibrido/','/contacto/','/entrenador-personal-las-condes/','/en/personal-trainer-las-condes/'];
const browser=await chromium.launch({headless:true});
const metrics=[];
for(const width of [390,768,1440]){
  const height=1000;
  const context=await browser.newContext({viewport:{width,height}});
  for(const route of routes){
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.addInitScript(()=>localStorage.removeItem('iberfit_consent_v2'));
    const response=await page.goto(base+route,{waitUntil:'networkidle'});
    if(!response?.ok()) throw Error(`HTTP ${route} ${response?.status()}`);
    const state=await page.evaluate(()=>{
      const d=document.documentElement;
      const banner=document.querySelector('.consent-banner');
      const br=banner?.getBoundingClientRect();
      const consentButtons=banner?[...banner.querySelectorAll('button')].map(b=>({text:b.textContent.trim(),h:b.getBoundingClientRect().height,w:b.getBoundingClientRect().width})):[];
      const footer=document.querySelector('.site-footer');
      const fr=footer?.getBoundingClientRect();
      const homeRouter=document.querySelector('.intent-router--compact');
      const reviewPair=document.querySelector('.review-pair');
      const reviewControls=document.querySelector('.review-carousel-controls');
      const appFirst=document.querySelector('.app-story-stage .app-screen');
      const ar=appFirst?.getBoundingClientRect();
      const hints=[...document.querySelectorAll('.mobile-swipe-hint')].map(x=>({display:getComputedStyle(x).display,text:x.textContent.trim()}));
      return {
        overflow:d.scrollWidth-d.clientWidth,
        text:document.body.innerText,
        banner:br?{h:br.height,w:br.width,bottom:innerHeight-br.bottom}:null,
        consentButtons,
        footerHeight:fr?.height||null,
        routerCount:homeRouter?.querySelectorAll('.intent-route').length||0,
        modalityCount:document.querySelectorAll('.modality-row--guided').length,
        reviewPairCount:reviewPair?.querySelectorAll('.client-review').length||0,
        reviewControls:!!reviewControls,
        reviewScroll:reviewPair?{scrollWidth:reviewPair.scrollWidth,clientWidth:reviewPair.clientWidth}:null,
        appWidth:ar?.width||null,
        hints,
        scripts:[...document.scripts].map(s=>s.src),
        css:[...document.styleSheets].map(s=>s.href||'')
      };
    });
    if(errors.length) throw Error(`PAGEERROR ${route} ${width} ${errors.join(' | ')}`);
    if(state.overflow>2) throw Error(`OVERFLOW ${route} ${width} ${state.overflow}`);
    if(!state.css.some(x=>x.includes('ux.v64322.css'))||!state.scripts.some(x=>x.includes('ux.v64322.js'))) throw Error(`ASSETS ${route}`);
    if(!state.banner) throw Error(`CONSENT_MISSING ${route} ${width}`);
    if(state.consentButtons.length!==4) throw Error(`CONSENT_CHOICES ${route} ${width} ${JSON.stringify(state.consentButtons)}`);
    if(width<=768 && state.consentButtons.some(x=>x.h<44||x.w<44)) throw Error(`CONSENT_TOUCH ${route} ${width} ${JSON.stringify(state.consentButtons)}`);
    if(width===390 && state.banner.h>260) throw Error(`CONSENT_TOO_TALL ${route} ${state.banner.h}`);
    if(width===1440 && state.banner.h>150) throw Error(`CONSENT_DESKTOP_TOO_TALL ${route} ${state.banner.h}`);
    if(route==='/'||route==='/en/'){
      if(state.routerCount!==2||state.modalityCount!==3) throw Error(`HOME_DECISION ${route} ${width} ${state.routerCount}/${state.modalityCount}`);
      if(state.reviewPairCount!==2||state.reviewControls) throw Error(`REVIEWS ${route} ${width} ${state.reviewPairCount}/${state.reviewControls}`);
      if(width===390 && (!state.reviewScroll||state.reviewScroll.scrollWidth<=state.reviewScroll.clientWidth)) throw Error(`REVIEW_SWIPE ${route}`);
    }
    if(route==='/online/'||route==='/en/online/'){
      if(width===390 && (!state.appWidth||state.appWidth<315)) throw Error(`APP_SCALE ${route} ${state.appWidth}`);
      if(route==='/online/'&&!state.text.includes('Si necesitas mucha corrección técnica en directo')) throw Error('ONLINE_ES_SEMANTIC');
      if(route==='/en/online/'&&!state.text.includes('If you need frequent live technical correction')) throw Error('ONLINE_EN_SEMANTIC');
    }
    if(route.includes('las-condes')){
      if(state.text.includes('Según sector y horario')||state.text.includes('Subject to area and schedule')) throw Error(`LOCAL_UNCERTAINTY ${route}`);
    }
    if(width<=390 && ['/', '/en/','/online/','/en/online/','/presencial/','/hibrido/'].includes(route)){
      if(!state.hints.some(h=>h.display!=='none')) throw Error(`SWIPE_HINT ${route}`);
    }
    metrics.push({route,width,...state,text:undefined,scripts:undefined,css:undefined,hints:state.hints.length});
    if((width===390||width===1440)&&['/','/online/','/entrenador-personal-las-condes/'].includes(route)){
      const slug=route==='/'?'home':route==='/online/'?'online':'las-condes';
      await page.screenshot({path:`${out}/${slug}-${width}.png`,fullPage:true});
      await page.locator('.consent-banner').screenshot({path:`${out}/${slug}-consent-${width}.png`});
    }
    await page.close();
  }
  await context.close();
}
await browser.close();
fs.writeFileSync(`${out}/metrics.json`,JSON.stringify(metrics,null,2));
console.log('BROWSER_V64322_OK',metrics.length);
