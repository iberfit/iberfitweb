import { chromium } from 'playwright';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const base = process.env.BASE_URL || 'http://127.0.0.1:4173';
const out = process.env.QA_OUT || '/tmp/authority-qa';
fs.mkdirSync(out,{recursive:true});
const routes=['/metodo/','/en/method/','/sobre-iberfit/','/en/about/','/contacto/','/en/contact/','/diagnostico-iri/','/en/iri-assessment/','/presencial/','/en/in-person/','/hibrido/','/en/hybrid/','/online/','/en/online/','/privacidad/','/en/privacy/'];
const browser=await chromium.launch({headless:true});
const results=[];
try {
  for(const width of [390,768,1440]){
    const context=await browser.newContext({viewport:{width,height:1000}});
    await context.addInitScript(()=>localStorage.setItem('iberfit_consent_v2',JSON.stringify({version:'2026-07-12-v2',necessary:true,analytics:false,marketing:false})));
    for(const route of routes){
      const page=await context.newPage();
      const errors=[];
      page.on('pageerror',e=>errors.push(String(e)));
      const response=await page.goto(base+route,{waitUntil:'domcontentloaded'});
      assert(response?.ok(),route);
      await page.evaluate(()=>document.fonts.ready);
      const state=await page.evaluate(()=>({h1:document.querySelectorAll('h1').length,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,lang:document.documentElement.lang}));
      assert.equal(state.h1,1,route);
      assert(state.overflow<=2,route+' overflow '+state.overflow);
      assert.equal(state.lang,route.startsWith('/en/')?'en':'es');
      if(route==='/metodo/'||route==='/en/method/'){
        for(const id of ['objetivos']) assert.equal(await page.locator('#'+id).count(),1,route+' '+id);
        await page.locator('#objetivos').scrollIntoViewIfNeeded();
      }
      if(route==='/sobre-iberfit/'||route==='/en/about/'){
        assert.equal(await page.locator('#evidencia').count(),1);
        await page.locator('#evidencia').scrollIntoViewIfNeeded();
      }
      if(route==='/contacto/'||route==='/en/contact/'){
        const en=route.startsWith('/en/');
        const goals=en?['Develop strength or performance','Arrange the IRI Assessment only']:['Desarrollar fuerza o rendimiento','Coordinar solo el Diagnóstico IRI'];
        for(const goal of goals){
          await page.reload({waitUntil:'load'});
          const chip=page.locator('#objetivo + .choice-grid button').filter({hasText:goal});
          if(width<=720){await chip.waitFor();await chip.click();}
          else {await page.locator('#objetivo').selectOption({label:goal});}
          assert.equal(await page.locator('#objetivo').inputValue(),goal);
          await page.locator('[data-step="1"] [data-next-step]').click();
          await page.locator('[data-step="2"] [data-next-step]').click();
          await page.locator('[data-step="3"] button[type="submit"]').click();
          const result=page.locator('[data-orientador-result]');
          await result.waitFor({state:'visible'});
          const href=await page.locator('[data-orientador-whatsapp]').getAttribute('href');
          const message=new URL(href);
          assert.equal(message.hostname,'wa.me');
          assert.equal(message.pathname,'/56944040032');
          assert(message.searchParams.get('text')?.includes(goal),route+' '+goal);
          // No message is sent; the actual outbound link is never clicked.
          results.push({route,width,goal,whatsappDraft:'verified'});
        }
      }
      assert.equal(errors.length,0,route+' '+errors.join(' | '));
      results.push({route,width,...state});
      if(width===390&&['/metodo/','/en/method/','/sobre-iberfit/','/contacto/'].includes(route)){
        await page.screenshot({path:out+'/'+route.replaceAll('/','_')+'.png',fullPage:true});
      }
      await page.close();
    }
    await context.close();
  }

  // Check the actual Norte editorial layout, including intermediate desktop widths.
  // Preserve the historical audit when certifying a previously published version.
  const version = (await (await fetch(base+'/VERSION')).text()).trim();
  const versionParts = version.split('.').map(Number);
  const norteEditorial = versionParts[0]>6 || (versionParts[0]===6 && (versionParts[1]>43 || (versionParts[1]===43 && versionParts[2]>=37)));
  if(norteEditorial){
    for(const width of [360,390,768,901,1024,1440]){
      const ctx=await browser.newContext({viewport:{width,height:900},deviceScaleFactor:1,reducedMotion:'reduce'});
      await ctx.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
      await ctx.addInitScript(()=>localStorage.setItem('iberfit_consent_v2',JSON.stringify({version:'2026-07-12-v2',necessary:true,analytics:false,marketing:false})));
      try{
        for(const route of ['/','/en/']){
          const page=await ctx.newPage();
          try{
            const errors=[];
            page.on('pageerror',e=>errors.push(String(e)));
            const response=await page.goto(base+route,{waitUntil:'load'});
            assert(response?.ok(),route);
            await page.evaluate(()=>document.fonts.ready);
            const cover=page.locator('.editorial-hero');
            const img=cover.locator('.editorial-hero-media img');
            await img.evaluate(e=>e.decode());
            const layout=await cover.evaluate(el=>{
              const get=s=>{const e=el.querySelector(s),r=e.getBoundingClientRect(),c=getComputedStyle(e);return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,right:r.right,display:c.display,visibility:c.visibility}};
              const i=el.querySelector('.editorial-hero-media img');
              return {heading:get('h1'),text:get('.hero-text'),media:get('.editorial-hero-media'),image:get('.editorial-hero-media img'),actions:get('.hero-actions'),meta:get('.hero-meta'),caption:get('figcaption'),naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth};
            });
            assert(layout.overflow<=2,route+' '+width+' cover overflow');
            assert(layout.naturalWidth>0&&layout.naturalHeight>0,route+' cover image');
            assert(layout.media.y>=layout.text.bottom-2,route+' cover must follow text');
            assert(layout.image.width>0&&layout.image.height>0&&layout.caption.height>0,route+' photo/caption');
            assert(layout.actions.height>0&&layout.meta.height>0,route+' contact and service context visible');
            assert(layout.media.right<=width+2&&layout.heading.right<=width+2,route+' clipping');
            for(const cta of await cover.locator('.hero-actions a').all()){
              const box=await cta.boundingBox();
              assert(box&&box.height>=44&&box.x>=-1&&box.x+box.width<=width+2,route+' CTA touch/width');
            }
            assert.equal(errors.length,0,route+' '+errors.join(' | '));
            await page.screenshot({path:out+'/editorial-'+(route==='/en/'?'en':'es')+'-'+width+'.png',fullPage:width===390||width===1440});
            results.push({route,width,editorial:layout});
          }finally{await page.close();}
        }
      }finally{await ctx.close();}
    }
  }

  const origin=new URL(base).origin;
  const ctx=await browser.newContext();
  await ctx.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());
  const p=await ctx.newPage();
  await p.goto(base+'/contacto/?utm_source=chatgpt.com&utm_campaign=private_test_value',{waitUntil:'load'});
  assert.equal(await p.evaluate(()=>sessionStorage.getItem('iberfit_acquisition_v1')),null);
  await p.locator('[data-consent-audience]').click();
  const events=()=>p.evaluate(()=>window.dataLayer.map(a=>Array.from(a)).filter(a=>a[0]==='event'));
  let e=await events();
  assert.equal(e.filter(a=>a[1]==='acquisition_context').length,1);
  assert.equal(e.find(a=>a[1]==='acquisition_context')[2].acquisition_source,'chatgpt');
  assert(!JSON.stringify(e.find(a=>a[1]==='acquisition_context')).includes('private_test_value'));
  await p.goto(base+'/metodo/',{waitUntil:'load'});
  await p.evaluate(()=>window.iberfitTrack('whatsapp_click'));
  e=await events();
  assert.equal(e.find(a=>a[1]==='contact_intent')[2].acquisition_source,'chatgpt');
  await p.locator('[data-open-consent]').first().click();
  await p.locator('[data-consent-analytics]').uncheck();
  await p.locator('[data-consent-save]').click();
  assert.equal(await p.evaluate(()=>sessionStorage.getItem('iberfit_acquisition_v1')),null);
  await p.evaluate(()=>window.iberfitTrack('whatsapp_click'));
  assert.equal((await events()).filter(a=>a[1]==='contact_intent').length,1);
  results.push({acquisition:'consent, source category, navigation, contact attribution, revocation verified'});
  await ctx.close();

  // Google Business Profile is classified only by our explicit public tag;
  // ordinary Google referrals and arbitrary UTM text are not mislabeled.
  for(const [tag,expected] of [['google_business_profile','google_business_profile'],['google','google'],['instagram','instagram'],['facebook','facebook'],['unrecognized_private_value','direct']]){
    const c=await browser.newContext();
    await c.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());
    const page=await c.newPage();
    await page.goto(base+'/contacto/?utm_source='+tag+'&utm_campaign=private_campaign_test',{waitUntil:'load'});
    assert.equal(await page.evaluate(()=>sessionStorage.getItem('iberfit_acquisition_v1')),null);
    await page.locator('[data-consent-audience]').click();
    assert.equal(await page.evaluate(()=>sessionStorage.getItem('iberfit_acquisition_v1')),expected);
    await page.goto(base+'/metodo/',{waitUntil:'load'});
    await page.evaluate(()=>window.iberfitTrack('whatsapp_click'));
    const event=await page.evaluate(()=>window.dataLayer.map(x=>Array.from(x)).find(x=>x[0]==='event'&&x[1]==='contact_intent'));
    assert.equal(event[2].acquisition_source,expected);
    assert(!JSON.stringify(event).includes('private_campaign_test'));
    assert(!JSON.stringify(event).includes('unrecognized_private_value'));
    await page.locator('[data-open-consent]').first().click();
    await page.locator('[data-consent-analytics]').uncheck();
    await page.locator('[data-consent-save]').click();
    assert.equal(await page.evaluate(()=>sessionStorage.getItem('iberfit_acquisition_v1')),null);
    await c.close();
    results.push({acquisitionSource:expected,consent:'verified',contact:'verified',revocation:'verified'});
  }
  const noAudience=await browser.newContext();
  await noAudience.route('**/*',r=>new URL(r.request().url()).origin===origin?r.continue():r.abort());
  const noAudiencePage=await noAudience.newPage();
  await noAudiencePage.goto(base+'/contacto/?utm_source=google_business_profile',{waitUntil:'load'});
  await noAudiencePage.locator('[data-consent-necessary]').click();
  await noAudiencePage.evaluate(()=>window.iberfitTrack('whatsapp_click'));
  assert.equal(await noAudiencePage.evaluate(()=>sessionStorage.getItem('iberfit_acquisition_v1')),null);
  assert.equal(await noAudiencePage.evaluate(()=>window.dataLayer.map(x=>Array.from(x)).filter(x=>x[0]==='event'&&['acquisition_context','contact_intent','generate_lead'].includes(x[1])).length),0);
  await noAudience.close();
  results.push({acquisition:'necessary-only consent denies attribution'});
}finally{await browser.close();}
fs.writeFileSync(out+'/metrics.json',JSON.stringify(results,null,2));
console.log('COMMERCIAL_BROWSER_OK',results.length);
