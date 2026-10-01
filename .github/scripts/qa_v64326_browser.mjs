import { chromium } from 'playwright';
import fs from 'node:fs';

const base=process.env.BASE_URL||'http://127.0.0.1:4173';
const out=process.env.QA_OUT||'/tmp/v64326-screens';
fs.mkdirSync(out,{recursive:true});

const bannedEs=['vida de barrio','vida barrial','actividad comunitaria','precordillera','ciclovía','ciclovías','infraestructura deportiva','entorno verde','movilidad activa','escala caminable','recursos que ya tienes cerca','formas de moverte por la comuna','identidad residencial','parques, cerros, senderos','parques y espacios deportivos'];
const bannedEn=['neighbourhood life','community activity','foothills','cycle lanes','sports infrastructure','green environment','active mobility','walkable scale','resources already around you','ways of moving through the commune','residential identity','parks, hills, trails','parks and sports spaces'];

const pages=[
  {route:'/entrenador-personal-las-condes/',required:['La comuna define la cobertura; tu contexto define el plan.','No inferimos cómo te mueves, dónde prefieres entrenar ni qué actividades haces por vivir en Las Condes.'],strip:1,target:true},
  {route:'/en/personal-trainer-las-condes/',required:['The commune defines coverage; your context defines the plan.','We do not infer how you move, where you prefer to train or which activities you do from living in Las Condes.'],strip:1,target:true},
  {route:'/entrenador-personal-vitacura/',required:['La comuna define la cobertura; tu contexto define el plan.','No deducimos tus hábitos ni tus preferencias por vivir en Vitacura.'],strip:1,target:true},
  {route:'/en/personal-trainer-vitacura/',required:['The commune defines coverage; your context defines the plan.','We do not infer your habits or preferences from living in Vitacura.'],strip:1,target:true},
  {route:'/entrenamiento-personal-providencia/',required:['La comuna define la cobertura; tu contexto define el plan.','No suponemos que caminas, pedaleas, entrenas fuera o tienes una semana activa por vivir en Providencia.'],strip:1,target:true},
  {route:'/en/personal-training-providencia/',required:['The commune defines coverage; your context defines the plan.','We do not assume you walk, cycle, train outdoors or have an active week because you live in Providencia.'],strip:1,target:true},
  {route:'/entrenador-personal-lo-barnechea/',required:['La comuna define la cobertura; tu contexto define el plan.','No asumimos montaña, bicicleta, trekking ni ninguna otra actividad por vivir en Lo Barnechea.'],strip:1,target:true},
  {route:'/en/personal-trainer-lo-barnechea/',required:['The commune defines coverage; your context defines the plan.','We do not assume mountain activity, cycling, hiking or any other activity from living in Lo Barnechea.'],strip:1,target:true},
  {route:'/entrenador-personal-la-reina/',required:['La comuna define la cobertura; tu contexto define el plan.','Tu forma de entrenar no se deduce de la comuna.'],strip:0,target:false},
  {route:'/en/personal-trainer-la-reina/',required:['The commune defines coverage; your context defines the plan.','Your way of training is not inferred from the commune.'],strip:0,target:false},
  {route:'/personal-trainer-nunoa/',required:['Tu contexto concreto vale más que cualquier idea sobre la comuna.','No inferimos tus hábitos, tus actividades ni tus lugares preferidos por vivir en Ñuñoa.'],strip:1,target:false},
  {route:'/en/personal-trainer-nunoa/',required:['Your actual context matters more than any idea about the commune.','We do not infer your habits, activities or preferred places from living in Ñuñoa.'],strip:1,target:false},
  {route:'/entrenador-personal-penalolen/',required:['Estar en Peñalolén define la cobertura; tus datos definen el plan.','no lo suponemos por vivir en Peñalolén'],strip:1,target:false},
  {route:'/en/personal-trainer-penalolen/',required:['Being in Peñalolén defines coverage; your information defines the plan.','we do not assume it from living in Peñalolén'],strip:1,target:false},
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
      const scopeLink=document.querySelector('section.compact-section .scope-note a');
      const scopeRect=scopeLink?.getBoundingClientRect();
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
        scopeTarget:scopeRect?{w:scopeRect.width,h:scopeRect.height}:null
      };
    });
    const en=spec.route.startsWith('/en/');
    if(errors.length) throw Error(`PAGEERROR ${spec.route} ${width} ${errors.join(' | ')}`);
    if(state.overflow>2) throw Error(`OVERFLOW ${spec.route} ${width} ${state.overflow}`);
    if(!state.skip||!state.nav||!state.footer||state.languages<2||state.whatsapp<1) throw Error(`SHELL ${spec.route} ${width}`);
    if(state.principles!==3) throw Error(`PRINCIPLES ${spec.route} ${width} ${state.principles}`);
    if(state.answers<2) throw Error(`ANSWERS ${spec.route} ${width} ${state.answers}`);
    if(state.strips!==spec.strip) throw Error(`STRIP ${spec.route} ${width} ${state.strips}`);
    const expectedBadge=en?'Training available':'Entrenamiento disponible';
    if(state.badge!==expectedBadge) throw Error(`SERVICE_BADGE ${spec.route} ${width} ${state.badge}`);
    const low=state.text.toLocaleLowerCase(en?'en':'es');
    for(const phrase of spec.required){
      if(!low.includes(phrase.toLocaleLowerCase(en?'en':'es'))) throw Error(`REQUIRED ${spec.route} ${width} ${phrase}`);
    }
    for(const phrase of (en?bannedEn:bannedEs)){
      if(low.includes(phrase.toLocaleLowerCase(en?'en':'es'))) throw Error(`BANNED ${spec.route} ${width} ${phrase}`);
    }
    if(width<=768 && state.scopeTarget && (state.scopeTarget.h<44||state.scopeTarget.w<44)) throw Error(`TOUCH_TARGET ${spec.route} ${width} ${JSON.stringify(state.scopeTarget)}`);
    metrics.push({route:spec.route,width,overflow:state.overflow,height:state.height,h1:state.h1,principles:state.principles,answers:state.answers,strips:state.strips,scopeTarget:state.scopeTarget});
    if(spec.target && (width===390 || (width===1440 && !en))){
      const slug=spec.route.split('/').filter(Boolean).join('-');
      await page.screenshot({path:`${out}/${slug}-${width}.png`,fullPage:true});
    }
    await page.close();
  }
  await context.close();
}
await browser.close();
fs.writeFileSync(`${out}/metrics.json`,JSON.stringify(metrics,null,2));
console.log('BROWSER_V64326_LOCAL_POLICY_OK',metrics.length);
