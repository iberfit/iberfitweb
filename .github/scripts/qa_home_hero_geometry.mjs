import {spawn} from "node:child_process";
import {readFile,rm,mkdir} from "node:fs/promises";

const browser=process.env.BROWSER;
if(!browser) throw new Error("BROWSER_REQUIRED");
const base="http://127.0.0.1:4173/";

const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function waitJson(url,tries=60){
  for(let i=0;i<tries;i++){
    try{const r=await fetch(url); if(r.ok) return await r.json();}catch{}
    await sleep(100);
  }
  throw new Error("CDP_NOT_READY");
}

const profile="/tmp/iberfit-hero-cdp";
await rm(profile,{recursive:true,force:true});
await mkdir(profile,{recursive:true});
const proc=spawn(browser,[
  "--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage",
  "--no-first-run","--no-default-browser-check",
  "--remote-debugging-address=127.0.0.1","--remote-debugging-port=0",
  "--user-data-dir="+profile,"about:blank"
],{stdio:"ignore"});

async function devtoolsPort(){
  for(let i=0;i<100;i++){
    try{
      const s=await readFile(profile+"/DevToolsActivePort","utf8");
      const p=Number(s.split(/\r?\n/)[0]);
      if(Number.isFinite(p)&&p>0)return p;
    }catch{}
    if(proc.exitCode!==null)throw new Error("CHROME_EXITED_BEFORE_CDP:"+proc.exitCode);
    await sleep(100);
  }
  throw new Error("DEVTOOLS_ACTIVE_PORT_NOT_FOUND");
}

try{
  const port=await devtoolsPort();
  await waitJson("http://127.0.0.1:"+port+"/json/version");
  const target=await fetch("http://127.0.0.1:"+port+"/json/new?about:blank",{method:"PUT"}).then(r=>r.json());
  const ws=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{ws.addEventListener("open",resolve,{once:true});ws.addEventListener("error",reject,{once:true});});
  let seq=0;
  const pending=new Map();
  ws.addEventListener("message",ev=>{
    const m=JSON.parse(ev.data);
    if(m.id&&pending.has(m.id)){const {resolve,reject}=pending.get(m.id);pending.delete(m.id);m.error?reject(new Error(JSON.stringify(m.error))):resolve(m.result);}
  });
  const call=(method,params={})=>new Promise((resolve,reject)=>{
    const id=++seq; pending.set(id,{resolve,reject}); ws.send(JSON.stringify({id,method,params}));
  });
  await call("Runtime.enable");
  await call("Page.enable");

  const views=[
    {name:"desktop1440",width:1440,height:1000,dpr:2,mobile:false},
    {name:"desktop1280",width:1280,height:900,dpr:2,mobile:false},
    {name:"tablet820",width:820,height:1180,dpr:2,mobile:false},
    {name:"mobile390",width:390,height:844,dpr:3,mobile:true}
  ];

  const results=[];
  for(const v of views){
    await call("Emulation.setDeviceMetricsOverride",{width:v.width,height:v.height,deviceScaleFactor:v.dpr,mobile:v.mobile});
    await call("Page.navigate",{url:base});
    for(let i=0;i<50;i++){
      const r=await call("Runtime.evaluate",{expression:"document.readyState",returnByValue:true});
      if(r.result.value==="complete") break;
      await sleep(100);
    }
    await sleep(300);
    const expr=`(()=> {
      const rect=e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
      const hero=document.querySelector('.hero');
      const text=document.querySelector('.hero-text');
      const media=document.querySelector('.editorial-hero-media');
      const img=media?.querySelector('img');
      const actions=document.querySelector('.hero-actions');
      const meta=document.querySelector('.hero-meta');
      const h1=document.querySelector('.hero h1');
      const pseudo=media?getComputedStyle(media,'::before'):null;
      const visible=e=>{if(!e)return false;const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};
      const targets=[...document.querySelectorAll('.site-header a,.site-header button,.hero a')].filter(visible).map(e=>{const r=e.getBoundingClientRect();return {t:(e.textContent||'').trim().replace(/\\s+/g,' ').slice(0,80),w:r.width,h:r.height,left:r.left,right:r.right};});
      return {
        innerWidth,
        scrollWidth:document.documentElement.scrollWidth,
        hero:rect(hero),text:rect(text),media:rect(media),img:rect(img),actions:rect(actions),meta:rect(meta),h1:rect(h1),
        fadeWidth:pseudo?parseFloat(pseudo.width):null,
        fadeRatio:pseudo?parseFloat(pseudo.width)/media.getBoundingClientRect().width:null,
        imageFilter:img?getComputedStyle(img).filter:null,
        natural:{w:img?.naturalWidth||0,h:img?.naturalHeight||0},
        targets
      };
    })()`;
    const r=await call("Runtime.evaluate",{expression:expr,returnByValue:true});
    const m=r.result.value;
    const failures=[];
    if(m.scrollWidth>m.innerWidth+2) failures.push("HORIZONTAL_OVERFLOW");
    if(!m.natural.w||!m.natural.h) failures.push("IMAGE_NOT_LOADED");
    if(v.width>1180 && m.fadeRatio!==null && m.fadeRatio>.085) failures.push("FADE_TOO_WIDE:"+m.fadeRatio.toFixed(3));

    if(v.width>1180){
      if(m.text.right>m.media.left-8) failures.push("TEXT_PHOTO_OVERLAP:"+(m.text.right-m.media.left).toFixed(1));
      if(m.actions.right>m.media.left-8) failures.push("CTA_PHOTO_OVERLAP");
      if(m.meta.right>m.media.left-8) failures.push("META_PHOTO_OVERLAP");
      if(m.media.width<v.width*.32) failures.push("PHOTO_TOO_NARROW");
    }else{
      if(m.media.top<m.text.bottom-1) failures.push("STACK_OVERLAP");
      const stackGap=m.media.top-m.text.bottom;
      if(stackGap>32) failures.push("STACK_GAP_TOO_LARGE:"+stackGap.toFixed(1));
      const gutter=v.width<=420?16:24;
      if(m.h1.left<gutter-1) failures.push("CONTENT_GUTTER_LEFT:"+m.h1.left.toFixed(1));
      if(m.actions.left<gutter-1) failures.push("CTA_GUTTER_LEFT:"+m.actions.left.toFixed(1));
      if(m.innerWidth-m.media.right>22) failures.push("PHOTO_NOT_FULL_BLEED:"+(m.innerWidth-m.media.right).toFixed(1));
    }

    if(v.width<=420){
      const bad=m.targets.filter(x=>x.w<44||x.h<44);
      if(bad.length) failures.push("MOBILE_TARGET_UNDER_44:"+bad.map(x=>x.t).join("|"));
      if(m.h1.right>m.innerWidth+2||m.h1.left<-2) failures.push("H1_CLIPPED");
    }

    results.push({view:v,...m,failures,pass:failures.length===0});
  }

  console.log(JSON.stringify({schema:"iberfit.home.hero.geometry.v1",results},null,2));
  if(results.some(x=>!x.pass)) process.exitCode=1;
  ws.close();
} finally {
  proc.kill("SIGKILL");
}
