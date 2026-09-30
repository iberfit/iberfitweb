import { chromium } from 'playwright';
import fs from 'node:fs';

const base=process.env.BASE_URL||'http://127.0.0.1:4173';
const out=process.env.QA_OUT||'/tmp/v64325-screens';
fs.mkdirSync(out,{recursive:true});

const pages=[
  {
    route:'/entrenador-personal-la-reina/',
    required:['La comuna define la cobertura; tu contexto define el plan.','Tu forma de entrenar no se deduce de la comuna.'],
    banned:['vida cotidiana de barrio','escala residencial','espacios verdes','precordillera'],
    strip:0
  },
  {
    route:'/en/personal-trainer-la-reina/',
    required:['The commune defines coverage; your context defines the plan.','Your way of training is not inferred from the commune.'],
    banned:['everyday neighbourhood life','residential scale','green spaces','foothills'],
    strip:0
  },
  {
    route:'/personal-trainer-nunoa/',
    required:['Tu contexto concreto vale más que cualquier idea sobre la comuna.','No inferimos tus hábitos, tus actividades ni tus lugares preferidos por vivir en Ñuñoa.'],
    banned:['vida de barrio','vida barrial','actividad comunitaria','lugares que disfrutas','rutina reconocible'],
    strip:1
  },
  {
    route:'/en/personal-trainer-nunoa/',
    required:['Your actual context matters more than any idea about the commune.','We do not infer your habits, activities or preferred places from living in Ñuñoa.'],
    banned:['neighbourhood life','community activity','favourite places','routine you recognise'],
    strip:1
  },
  {
    route:'/entrenador-personal-penalolen/',
    required:['Estar en Peñalolén define la cobertura; tus datos definen el plan.','no lo suponemos por vivir en Peñalolén'],
    banned:['vida de barrio','precordillera','cómo vives Peñalolén'],
    strip:1
  },
  {
    route:'/en/personal-trainer-penalolen/',
    required:['Being in Peñalolén defines coverage; your information defines the plan.','we do not assume it from living in Peñalolén'],
    banned:['neighbourhood life','foothills','how you live in Peñalolén'],
    strip:1
  }
];

const browser=await chromium.launch({headless:true});
const metrics=[];
for(const width of [390,768,1440]){
  const context=await browser.newContext({viewport:{width,height:1000}});
  for(const spec of pages){
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.addInitScript(()=>localStorage.setItem('iberfit_consent_v2',JSON.stringify({necessary:true,analytics:false,marketing:false})));
    const response=await page.goto(base+spec.route,{waitUntil:'networkidle'});
    if(!response?.ok()) throw Error(`HTTP ${spec.route} ${response?.status()}`);
    const state=await page.evaluate(()=>{
      const d=document.documentElement;
      const targets=[...document.querySelectorAll('a,button,input,select,textarea')].filter(el=>{
        const r=el.getBoundingClientRect();
        const s=getComputedStyle(el);
        return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;
      });
      return {
        overflow:d.scrollWidth-d.clientWidth,
        height:document.body.scrollHeight,
        text:document.body.innerText||'',
        h1:document.querySelector('h1')?.textContent?.trim()||'',
        principles:document.querySelectorAll('.principle-row').length,
        answers:document.querySelectorAll('.answer-item,.answer-disclosure-v6437').length,
        strips:document.querySelectorAll('.local-service-strip').length,
        whatsapp:document.querySelectorAll('a[href*="wa.me/56944040032"]').length,
        skip:!!document.querySelector('.skip'),
        nav:!!document.querySelector('.site-header'),
        footer:!!document.querySelector('.site-footer'),
        languages:document.querySelectorAll('.lang-switch a').length,
        badge:document.querySelector('.local-place-copy small')?.textContent?.trim()||'',
        minTarget:targets.length?Math.min(...targets.map(el=>el.getBoundingClientRect().height)):999
      };
    });
    if(errors.length) throw Error(`PAGEERROR ${spec.route} ${width} ${errors.join(' | ')}`);
    if(state.overflow>2) throw Error(`OVERFLOW ${spec.route} ${width} ${state.overflow}`);
    if(!state.skip||!state.nav||!state.footer||state.languages<2||state.whatsapp<1) throw Error(`SHELL ${spec.route} ${width}`);
    if(state.principles!==3) throw Error(`PRINCIPLES ${spec.route} ${width} ${state.principles}`);
    if(state.answers<2) throw Error(`ANSWERS ${spec.route} ${width} ${state.answers}`);
    if(state.strips!==spec.strip) throw Error(`STRIP ${spec.route} ${width} ${state.strips}`);
    const en=spec.route.startsWith('/en/');
    const expectedBadge=en?'Training available':'Entrenamiento disponible';
    if(state.badge!==expectedBadge) throw Error(`SERVICE_BADGE ${spec.route} ${width} ${state.badge}`);
    const low=state.text.toLocaleLowerCase(en?'en':'es');
    for(const phrase of spec.required){
      if(!low.includes(phrase.toLocaleLowerCase(en?'en':'es'))) throw Error(`REQUIRED ${spec.route} ${width} ${phrase}`);
    }
    for(const phrase of spec.banned){
      if(low.includes(phrase.toLocaleLowerCase(en?'en':'es'))) throw Error(`BANNED ${spec.route} ${width} ${phrase}`);
    }
    if(width<=768 && state.minTarget<43.5) throw Error(`TOUCH_TARGET ${spec.route} ${width} ${state.minTarget}`);
    metrics.push({route:spec.route,width,overflow:state.overflow,height:state.height,h1:state.h1,principles:state.principles,answers:state.answers,strips:state.strips,minTarget:state.minTarget});
    if(width===390 || (width===1440 && !en)){
      const slug=spec.route.split('/').filter(Boolean).join('-');
      await page.screenshot({path:`${out}/${slug}-${width}.png`,fullPage:true});
    }
    await page.close();
  }
  await context.close();
}
await browser.close();
fs.writeFileSync(`${out}/metrics.json`,JSON.stringify(metrics,null,2));
console.log('BROWSER_V64325_PERSON_FIRST_LOCAL_OK',metrics.length);
