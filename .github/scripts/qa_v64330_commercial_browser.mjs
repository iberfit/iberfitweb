import { chromium } from 'playwright';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const base = process.env.BASE_URL || 'http://127.0.0.1:4173';
const out = process.env.QA_OUT || '/tmp/authority-qa';
fs.mkdirSync(out,{recursive:true});
const routes=['/metodo/','/en/method/','/sobre-iberfit/','/en/about/','/contacto/','/en/contact/','/diagnostico-iri/','/en/iri-assessment/','/presencial/','/en/in-person/','/hibrido/','/en/hybrid/','/online/','/en/online/'];
const browser=await chromium.launch({headless:true});
const results=[];
try {
  for(const width of [390,768,1440]){
    const context=await browser.newContext({viewport:{width,height:1000}});
    await context.addInitScript(()=>localStorage.setItem('iberfit_consent_v2',JSON.stringify({necessary:true,analytics:false,marketing:false})));
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
        for(const id of ['objetivos','fuerza','running','condicion-fisica','retomar']) assert.equal(await page.locator('#'+id).count(),1,route+' '+id);
        await page.locator('#objetivos').scrollIntoViewIfNeeded();
      }
      if(route==='/sobre-iberfit/'||route==='/en/about/'){
        assert.equal(await page.locator('#evidencia').count(),1);
        await page.locator('#evidencia').scrollIntoViewIfNeeded();
      }
      if(route==='/contacto/'||route==='/en/contact/'){
        const en=route.startsWith('/en/');
        const goals=en?['Improve my running or prepare for a race','Arrange the IRI Assessment only']:['Mejorar en running o preparar una carrera','Coordinar solo el Diagnóstico IRI'];
        for(const goal of goals){
          await page.reload({waitUntil:'load'});
          const chip=page.locator('#objetivo + .choice-grid button').filter({hasText:goal});
          await chip.waitFor();
          await chip.click();
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
}finally{await browser.close();}
fs.writeFileSync(out+'/metrics.json',JSON.stringify(results,null,2));
console.log('COMMERCIAL_BROWSER_OK',results.length);
