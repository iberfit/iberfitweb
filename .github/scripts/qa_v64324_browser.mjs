import { chromium } from 'playwright';
import fs from 'node:fs';

const base=process.env.BASE_URL||'http://127.0.0.1:4173';
const out=process.env.QA_OUT||'/tmp/v64324-screens';
fs.mkdirSync(out,{recursive:true});

const pages=[
  ['/entrenador-personal-penalolen/','Peñalolén',['precordillera','vida de barrio']],
  ['/en/personal-trainer-penalolen/','Peñalolén',['foothills','neighbourhood life']],
  ['/entrenador-personal-la-reina/','La Reina',['espacios verdes','precordillera']],
  ['/en/personal-trainer-la-reina/','La Reina',['green spaces','foothills']],
  ['/entrenador-personal-las-condes/','Las Condes',['parques','espacios deportivos']],
  ['/en/personal-trainer-las-condes/','Las Condes',['parks','sports']],
  ['/entrenador-personal-vitacura/','Vitacura',['ciclovías','verde']],
  ['/en/personal-trainer-vitacura/','Vitacura',['cycleways','green']],
  ['/entrenamiento-personal-providencia/','Providencia',['ciclovías','movimiento diario']],
  ['/en/personal-training-providencia/','Providencia',['cycleways','everyday movement']],
  ['/personal-trainer-nunoa/','Ñuñoa',['plazas','vida de barrio']],
  ['/en/personal-trainer-nunoa/','Ñuñoa',['plazas','neighbourhood life']],
  ['/entrenador-personal-lo-barnechea/','Lo Barnechea',['montaña','trekking']],
  ['/en/personal-trainer-lo-barnechea/','Lo Barnechea',['mountain','hiking']],
];

const banned=[
  'tu sector cambia la logística','reducir fricción','coste logístico','carga para tu semana','otro traslado','desplazamientos innecesarios','cobertura presencial según sector','según cobertura presencial',
  'your area changes the logistics','reduce friction','logistical cost','travel burden','another journey','unnecessary travel','in-person coverage depending on area','subject to area and schedule'
];

const browser=await chromium.launch({headless:true});
const metrics=[];
for(const width of [390,768,1440]){
  const context=await browser.newContext({viewport:{width,height:1000}});
  for(const [route,commune,markers] of pages){
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    await page.addInitScript(()=>localStorage.setItem('iberfit_consent_v2',JSON.stringify({necessary:true,analytics:false,marketing:false})));
    const response=await page.goto(base+route,{waitUntil:'networkidle'});
    if(!response?.ok()) throw Error(`HTTP ${route} ${response?.status()}`);
    const state=await page.evaluate(()=>{
      const d=document.documentElement;
      return {
        overflow:d.scrollWidth-d.clientWidth,
        height:document.body.scrollHeight,
        text:(document.body.innerText||''),
        h1:document.querySelector('h1')?.textContent?.trim()||'',
        context:document.querySelector('.local-context-note')?.textContent?.trim()||'',
        principles:document.querySelectorAll('.principle-row').length,
        answers:document.querySelectorAll('.answer-item').length,
        strips:document.querySelectorAll('.local-service-strip').length,
        whatsapp:document.querySelectorAll('a[href*="wa.me/56944040032"]').length,
        skip:!!document.querySelector('.skip'),
        nav:!!document.querySelector('.site-header'),
        footer:!!document.querySelector('.site-footer'),
        languages:document.querySelectorAll('.lang-switch a').length,
        serviceBadge:document.querySelector('.local-place-copy small')?.textContent?.trim()||''
      };
    });
    if(errors.length) throw Error(`PAGEERROR ${route} ${width} ${errors.join(' | ')}`);
    if(state.overflow>2) throw Error(`OVERFLOW ${route} ${width} ${state.overflow}`);
    if(!state.skip||!state.nav||!state.footer||state.languages<2||state.whatsapp<1) throw Error(`SHELL ${route} ${width}`);
    if(state.principles!==3) throw Error(`PRINCIPLES ${route} ${width} ${state.principles}`);
    if(state.answers<2) throw Error(`ANSWERS ${route} ${width} ${state.answers}`);
    if(route.includes('la-reina')){
      if(state.strips!==0) throw Error(`LA_REINA_STRIP ${route} ${width}`);
    }else if(state.strips!==1){
      throw Error(`LOCAL_STRIP ${route} ${width} ${state.strips}`);
    }
    const low=state.text.toLocaleLowerCase('es');
    for(const marker of markers){
      if(!low.includes(marker.toLocaleLowerCase('es'))) throw Error(`GROUNDING ${route} ${width} ${marker}`);
    }
    for(const phrase of banned){
      if(low.includes(phrase.toLocaleLowerCase('es'))) throw Error(`NEGATIVE_LOCAL_FRAME ${route} ${width} ${phrase}`);
    }
    const expectedBadge=route.startsWith('/en/')?'Training available':'Entrenamiento disponible';
    if(state.serviceBadge!==expectedBadge) throw Error(`SERVICE_CERTAINTY ${route} ${width} ${state.serviceBadge}`);

    // Lo Barnechea outdoor context is only valid when explicitly conditional.
    if(route==='/entrenador-personal-lo-barnechea/'&&!state.text.includes('Si la montaña, la bicicleta, el trekking o el movimiento exterior ya están en tu vida')) throw Error('LO_BARNECHEA_CONDITIONAL_ES');
    if(route==='/en/personal-trainer-lo-barnechea/'&&!state.text.includes('If mountains, cycling, hiking or outdoor movement are already part of your life')) throw Error('LO_BARNECHEA_CONDITIONAL_EN');

    metrics.push({route,width,overflow:state.overflow,height:state.height,h1:state.h1,principles:state.principles,answers:state.answers,strips:state.strips});
    const isEnglish=route.startsWith('/en/');
    if(width===390 || (width===1440 && !isEnglish)){
      const slug=route.split('/').filter(Boolean).join('-')||'home';
      await page.screenshot({path:`${out}/${slug}-${width}.png`,fullPage:true});
    }
    await page.close();
  }
  await context.close();
}
await browser.close();
fs.writeFileSync(`${out}/metrics.json`,JSON.stringify(metrics,null,2));
console.log('BROWSER_V64324_LOCAL_OPPORTUNITY_OK',metrics.length);
