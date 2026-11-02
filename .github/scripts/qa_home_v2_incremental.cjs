const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const candidate='http://127.0.0.1:4173';
const baseline='http://127.0.0.1:4174';
const out='/tmp/iberfit-home-v2';
fs.mkdirSync(out,{recursive:true});

const views=[
  {name:'desktop',width:1440,height:1000,dpr:2},
  {name:'tablet',width:820,height:1180,dpr:2},
  {name:'mobile',width:390,height:844,dpr:3},
];

async function inspect(page,url){
  const errs=[];
  page.on('pageerror',e=>errs.push('pageerror:'+e.message));
  page.on('console',m=>{ if(m.type()==='error') errs.push('console:'+m.text()); });
  await page.addInitScript(()=>localStorage.setItem('iberfit_consent_v2',JSON.stringify({analytics:false,marketing:false,necessary:true,timestamp:Date.now()})));
  const res=await page.goto(url,{waitUntil:'networkidle',timeout:30000});
  if(!res||res.status()!==200) throw Error('HTTP '+url+' '+(res&&res.status()));
  await page.waitForTimeout(250);
  const data=await page.evaluate(()=>({
    h1:(document.querySelector('h1')?.textContent||'').trim(),
    text:(document.body.innerText||'').replace(/\s+/g,' ').trim(),
    sw:document.documentElement.scrollWidth,
    cw:document.documentElement.clientWidth,
    imgs:[...document.images].map(i=>({src:i.getAttribute('src')||'',ok:i.complete&&i.naturalWidth>0,alt:i.alt||''})),
    css:[...document.styleSheets].map(s=>s.href||''),
    canonical:document.querySelector('link[rel=canonical]')?.href||'',
    schema:[...document.querySelectorAll('script[type="application/ld+json"]')].map(x=>x.textContent).join('\n'),
    links:[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'))
  }));
  return {data,errs};
}

(async()=>{
 const browser=await chromium.launch({headless:true});
 const results=[];
 for(const v of views){
   const ctx=await browser.newContext({viewport:{width:v.width,height:v.height},deviceScaleFactor:v.dpr});
   const bp=await ctx.newPage(), cp=await ctx.newPage();
   const b=await inspect(bp,baseline+'/');
   const c=await inspect(cp,candidate+'/');
   if(b.errs.length||c.errs.length) throw Error(v.name+' runtime '+JSON.stringify({b:b.errs,c:c.errs}));
   if(c.data.text!==b.data.text) throw Error(v.name+' BODY_TEXT_CHANGED');
   if(c.data.h1!==b.data.h1) throw Error(v.name+' H1_CHANGED');
   if(c.data.canonical!==b.data.canonical) throw Error(v.name+' CANONICAL_CHANGED');
   if(c.data.schema!==b.data.schema) throw Error(v.name+' SCHEMA_CHANGED');
   if(JSON.stringify(c.data.links)!==JSON.stringify(b.data.links)) throw Error(v.name+' LINKS_CHANGED');
   if(JSON.stringify(c.data.imgs.map(x=>[x.src,x.alt]))!==JSON.stringify(b.data.imgs.map(x=>[x.src,x.alt]))) throw Error(v.name+' IMAGES_CHANGED');
   if(c.data.imgs.some(x=>!x.ok)) throw Error(v.name+' BROKEN_IMAGE');
   if(c.data.sw>c.data.cw+2) throw Error(v.name+' OVERFLOW '+(c.data.sw-c.data.cw));
   if(!c.data.css.some(x=>x.includes('signature-home.v644.css'))) throw Error(v.name+' SIGNATURE_CSS_MISSING');
   await bp.screenshot({path:path.join(out,'baseline-'+v.name+'.png'),fullPage:true});
   await cp.screenshot({path:path.join(out,'candidate-'+v.name+'.png'),fullPage:true});
   await cp.screenshot({path:path.join(out,'candidate-'+v.name+'-viewport.png'),fullPage:false});
   results.push({view:v,overflow:c.data.sw-c.data.cw,images:c.data.imgs.length,h1:c.data.h1,pass:true});
   await bp.close();await cp.close();await ctx.close();
 }
 await browser.close();
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({ok:true,results},null,2));
 console.log(JSON.stringify({ok:true,results},null,2));
})().catch(e=>{console.error(e);process.exit(1);});