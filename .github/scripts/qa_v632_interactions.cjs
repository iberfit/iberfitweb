const { chromium } = require('playwright');
const fs = require('fs');
const assert = require('node:assert/strict');
const out = '/tmp/v632-evidence';
const base = 'http://127.0.0.1:4173';
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  for (const width of [320,390,768,1024,1365,1600]) {
   const context=await browser.newContext({viewport:{width,height:900}});
   const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base);await page.getByRole('button',{name:'Solo necesarias',exact:true}).click();
   if(width<=1380){
    const toggle=page.locator('[data-menu-toggle]');await toggle.click();
    assert.equal(await page.locator('.nav-panel-backdrop').count(),1,'one menu controller');
    assert.equal(await page.locator('footer.site-footer').evaluate(el=>el.inert),true);
    assert.equal(await toggle.getAttribute('aria-label'),'Cerrar menú');
    await page.keyboard.press('Escape');assert.equal(await toggle.getAttribute('aria-expanded'),'false');
    assert.equal(await page.locator('footer.site-footer').evaluate(el=>el.inert),false);
    await toggle.click();await page.setViewportSize({width:1600,height:900});
    assert.equal(await page.locator('body').evaluate(el=>el.classList.contains('nav-panel-open')),false);
    assert.equal(await page.locator('[data-navlinks]').getAttribute('aria-hidden'),'false');
    await page.setViewportSize({width,height:900});
   }
   await page.screenshot({path:`${out}/home-${width}.png`,fullPage:true});
   assert.deepEqual(errors,[],`no errors ${width}`);await context.close();
  }
  for(const [route,en] of [['/contacto/',false],['/en/contact/',true]]){
   const context=await browser.newContext({viewport:{width:390,height:844}});
   const page=await context.newPage();await page.goto(base+route);
   await page.getByRole('button',{name:en?'Necessary only':'Solo necesarias',exact:true}).click();
   const next=page.locator('[data-step="1"] [data-next-step]');await next.click();
   assert.equal(await page.locator('[data-step="1"]').getAttribute('aria-hidden'),'false');
   assert.equal(await page.evaluate(()=>document.activeElement.classList.contains('choice-chip')),true,'invalid goal focus visible');
   const goal=page.locator('#objetivo + .choice-grid .choice-chip').first();await goal.click();
   const chosen=await goal.textContent();await next.click();
   assert.equal(await page.evaluate(()=>document.activeElement.classList.contains('choice-chip')),true,'step focus visible');
   await page.locator('[data-step="2"] [data-next-step]').click();
   await page.locator('[data-step="3"] button[type="submit"]').click();
   assert.equal(await page.locator('.orientador-summary dd').first().textContent(),chosen);
   const href=await page.locator('[data-orientador-whatsapp]').getAttribute('href');assert.ok(decodeURIComponent(href).includes(chosen));
   await page.screenshot({path:`${out}/guide-${en?'en':'es'}.png`,fullPage:true});
   await page.locator('.orientador-edit').click();assert.equal(await goal.getAttribute('aria-pressed'),'true');
   assert.equal(await page.locator('[data-step="1"]').getAttribute('aria-hidden'),'false');
   const newGoal=page.locator('#objetivo + .choice-grid .choice-chip').nth(1);await newGoal.click();await next.click();await page.locator('[data-step="2"] [data-next-step]').click();await page.locator('[data-step="3"] button[type="submit"]').click();
   assert.equal(await page.locator('.orientador-summary dd').first().textContent(),await newGoal.textContent());
   // Dialog traps focus and restores it on both close and save.
   await page.locator('[data-open-consent]').click();
   const close=page.locator('.consent-close');await page.keyboard.press('Shift+Tab');
   assert.equal(await page.evaluate(()=>document.activeElement.hasAttribute('data-consent-save')),true);
   await page.keyboard.press('Tab');assert.equal(await close.evaluate(el=>el===document.activeElement),true);
   await page.keyboard.press('Escape');assert.equal(await page.locator('[data-open-consent]').evaluate(el=>el===document.activeElement),true);
   await page.locator('[data-open-consent]').click();await page.locator('[data-consent-save]').click();
   assert.equal(await page.locator('main').evaluate(el=>el.inert),false);assert.equal(await page.locator('.consent-modal').count(),0);
   await context.close();
  }
  const context=await browser.newContext({viewport:{width:1365,height:900}});const p=await context.newPage();await p.goto(base);await p.getByRole('button',{name:'Solo necesarias',exact:true}).click();
  await p.locator('[data-review-next]').click();const active=await p.locator('.review-slide.is-active').getAttribute('data-review-index');
  await p.waitForTimeout(6500);assert.equal(await p.locator('.review-slide.is-active').getAttribute('data-review-index'),active,'rotation stays paused while using controls');
  assert.equal(await p.locator('.review-carousel-dot[aria-pressed="true"]').count(),1);
  await p.emulateMedia({reducedMotion:'reduce'});assert.equal(await p.locator('[data-review-pause]').isDisabled(),true);
  await context.close();
  fs.writeFileSync(`${out}/interactions.json`,JSON.stringify({ok:true,checks:['single menu and resize recovery','visible guide focus','summary and edit ES/EN','consent keyboard and restore','carousel focus pause and reduced motion']},null,2));
  console.log('V632_INTERACTIONS=PASS');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
