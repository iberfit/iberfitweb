#!/usr/bin/env node
import {spawn} from "node:child_process";
import {readFile,rm,mkdir,writeFile} from "node:fs/promises";

const browser=process.env.BROWSER;
if(!browser) throw new Error("BROWSER_REQUIRED");
const profile="/tmp/iberfit-device-smoke";
await rm(profile,{recursive:true,force:true}); await mkdir(profile,{recursive:true});
const proc=spawn(browser,[
  "--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage",
  "--no-first-run","--no-default-browser-check","--remote-debugging-address=127.0.0.1",
  "--remote-debugging-port=0","--user-data-dir="+profile,"about:blank"
],{stdio:"ignore"});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function port(){
 for(let i=0;i<100;i++){try{const s=await readFile(profile+"/DevToolsActivePort","utf8");const p=+s.split(/\r?\n/)[0];if(p)return p}catch{};await sleep(80)}
 throw new Error("NO_CDP_PORT");
}
const p=await port();
const target=await fetch(`http://127.0.0.1:${p}/json/new?about:blank`,{method:"PUT"}).then(r=>r.json());
const ws=new WebSocket(target.webSocketDebuggerUrl);
await new Promise((res,rej)=>{ws.addEventListener("open",res,{once:true});ws.addEventListener("error",rej,{once:true})});
let seq=0;const pending=new Map();
ws.addEventListener("message",e=>{const m=JSON.parse(e.data);if(m.id&&pending.has(m.id)){const x=pending.get(m.id);pending.delete(m.id);m.error?x.reject(new Error(JSON.stringify(m.error))):x.resolve(m.result)}});
const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
await call("Runtime.enable"); await call("Page.enable");

const views=[
 {name:"mobile320",width:320,height:568,mobile:true,dpr:2},
 {name:"mobile390",width:390,height:844,mobile:true,dpr:3},
 {name:"tablet768",width:768,height:1024,mobile:false,dpr:2},
 {name:"desktop1440",width:1440,height:1000,mobile:false,dpr:1}
];
const routes=["/","/diagnostico-iri/","/metodo/","/presencial/","/online/","/contacto/","/en/","/en/contact/"];
const out=[];
for(const v of views){
 await call("Emulation.setDeviceMetricsOverride",{width:v.width,height:v.height,deviceScaleFactor:v.dpr,mobile:v.mobile});
 if(v.mobile) await call("Emulation.setTouchEmulationEnabled",{enabled:true,maxTouchPoints:5});
 else await call("Emulation.setTouchEmulationEnabled",{enabled:false});
 for(const route of routes){
  await call("Page.navigate",{url:"https://iberfit.cl"+route});
  for(let i=0;i<80;i++){
   const r=await call("Runtime.evaluate",{expression:"document.readyState",returnByValue:true});
   if(r.result.value==="complete")break; await sleep(75);
  }
  await sleep(200);
  const expr=`(()=> {
    const visible=e=>{if(!e)return false;const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity||1)>.05};
    const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};
    const imgs=[...document.images].map(i=>({src:i.currentSrc||i.src,complete:i.complete,naturalWidth:i.naturalWidth})).filter(x=>x.complete&&x.naturalWidth===0);
    const wa=[...document.querySelectorAll('a[href*="wa.me"]')].map(a=>a.href);
    const email=[...document.querySelectorAll('a[href^="mailto:"],a[href*="/cdn-cgi/l/email-protection"]')].map(a=>a.href);
    const targets=[...document.querySelectorAll('.btn,.menu-toggle,.lang-switch a,.device-dock a,.intent-route,.consent-link,select')].filter(visible).map(e=>({label:(e.textContent||e.getAttribute('aria-label')||'').trim().replace(/\\s+/g,' ').slice(0,80),...rect(e)}));
    const toggle=document.querySelector('.menu-toggle'),nav=document.querySelector('.navlinks');
    const menu={toggleVisible:visible(toggle),navBefore:visible(nav),toggleRect:toggle?rect(toggle):null,navRect:null,navAfter:null,ariaControls:toggle?.getAttribute('aria-controls')||null,navId:nav?.id||null};
    if(visible(toggle)){toggle.click();menu.navAfter=visible(nav);menu.navRect=nav?rect(nav):null;}
    return {
      url:location.href,lang:document.documentElement.lang,h1:document.querySelectorAll('h1').length,
      bodyWidth:document.body.scrollWidth,htmlWidth:document.documentElement.scrollWidth,innerWidth,
      main:document.querySelector('main')?rect(document.querySelector('main')):null,
      brokenImages:imgs,whatsapp:wa,emailLinks:email,targets,menu,
      consent:!!document.querySelector('.consent-banner'),
      canonical:document.querySelector('link[rel="canonical"]')?.href||'',
      pageErrors:window.__iberfitSmokeErrors||[]
    };
  })()`;
  const r=await call("Runtime.evaluate",{expression:expr,returnByValue:true});
  const m=r.result.value, failures=[];
  // A click starts the CSS visibility/opacity transition; sample the finished state,
  // not the zero-opacity first animation frame.
  if(v.width<=1024 && m.menu.toggleVisible){
    await sleep(360);
    const state=await call("Runtime.evaluate",{expression:`(()=>{const n=document.querySelector('.navlinks'),t=document.querySelector('.menu-toggle'); if(!n||!t)return {visible:false,rect:null,expanded:null,open:false}; const r=n.getBoundingClientRect(),c=getComputedStyle(n);return {visible:r.width>0&&r.height>0&&c.display!=='none'&&c.visibility!=='hidden'&&Number(c.opacity||1)>.05,rect:{x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom},expanded:t.getAttribute('aria-expanded'),open:n.classList.contains('open')}})()`,returnByValue:true});
    const updated=state.result.value;
    m.menu.navAfter=updated.visible;
    m.menu.navRect=updated.rect;
    m.menu.ariaExpanded=updated.expanded;
    m.menu.hasOpenClass=updated.open;
  }
  const overflow=Math.max(m.bodyWidth,m.htmlWidth)-m.innerWidth;
  if(overflow>2)failures.push("HORIZONTAL_OVERFLOW:"+overflow);
  if(m.h1!==1)failures.push("H1_COUNT:"+m.h1);
  if(!m.main||m.main.x<-2||m.main.right>m.innerWidth+2)failures.push("MAIN_GEOMETRY");
  if(m.brokenImages.length)failures.push("BROKEN_IMAGES:"+m.brokenImages.length);
  if(!m.canonical)failures.push("CANONICAL_MISSING");
  if(!m.whatsapp.length)failures.push("WHATSAPP_LINK_MISSING");
  if(v.width<=1024){
    if(!m.menu.toggleVisible)failures.push("COMPACT_MENU_TOGGLE_MISSING");
    if(m.menu.navBefore)failures.push("COMPACT_MENU_OPEN_ON_LOAD");
    if(!m.menu.navAfter||!m.menu.hasOpenClass||m.menu.ariaExpanded!=="true")failures.push("COMPACT_MENU_DID_NOT_OPEN");
    if(m.menu.navRect&&(m.menu.navRect.x<-1||m.menu.navRect.right>m.innerWidth+1))failures.push("MENU_OUT_OF_VIEWPORT");
    if(m.menu.ariaControls!==m.menu.navId)failures.push("MENU_ARIA_CONTROLS");
  }else{
    if(m.menu.toggleVisible)failures.push("DESKTOP_MOBILE_TOGGLE_VISIBLE");
    if(!m.menu.navBefore)failures.push("DESKTOP_NAV_HIDDEN");
  }
  if(v.mobile){
    const bad=m.targets.filter(x=>x.w<44||x.h<44);
    if(bad.length)failures.push("TOUCH_TARGETS_UNDER_44:"+bad.map(x=>x.label+"="+Math.round(x.w)+"x"+Math.round(x.h)).slice(0,12).join("|"));
  }
  out.push({view:v.name,route,...m,failures,pass:failures.length===0});
 }
}
await mkdir("evidence/live-device-smoke",{recursive:true});
const summary={
 schema:"iberfit.live-device-smoke.v1",checkedAt:new Date().toISOString(),
 total:out.length,passed:out.filter(x=>x.pass).length,failed:out.filter(x=>!x.pass).length,
 failures:out.filter(x=>!x.pass).map(x=>({view:x.view,route:x.route,failures:x.failures}))
};
await writeFile("evidence/live-device-smoke/report.json",JSON.stringify({summary,results:out},null,2)+"\n");
console.log(JSON.stringify(summary,null,2));
ws.close();proc.kill("SIGKILL");
if(summary.failed)process.exit(1);
