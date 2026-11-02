import { chromium } from "playwright";
import { writeFile, mkdir } from "node:fs/promises";

const base="http://127.0.0.1:8787";
const pages=[
 {name:"home",path:"/"},
 {name:"iri",path:"/diagnostico-iri/"},
 {name:"online",path:"/online/"}
];
const viewports=[
 {name:"mobile",width:390,height:844,dpr:3},
 {name:"tablet",width:820,height:1180,dpr:2},
 {name:"desktop",width:1440,height:1000,dpr:2}
];
const out=".signature-r423-evidence";
await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true});
const results=[];
try{
 for(const page of pages){
  for(const v of viewports){
   const p=await browser.newPage({viewport:{width:v.width,height:v.height},deviceScaleFactor:v.dpr});
   await p.goto(base+page.path,{waitUntil:"networkidle"});
   await p.waitForTimeout(500);
   const x=await p.evaluate(()=>{
    const visible=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=="none"&&s.visibility!=="hidden"&&Number(s.opacity)!==0};
    const imgs=[...document.images].filter(visible).map(i=>{const r=i.getBoundingClientRect();return {src:i.getAttribute("src")||"",ok:i.complete&&i.naturalWidth>0,left:r.left,right:r.right}});
    const targets=[...document.querySelectorAll("a,button,[role=button]")].filter(visible).map(e=>{const r=e.getBoundingClientRect();return {text:(e.textContent||"").trim().replace(/\s+/g," ").slice(0,60),w:r.width,h:r.height}});
    return {
      signature:document.body.dataset.signature||"",
      h1:[...document.querySelectorAll("h1")].filter(visible).map(e=>(e.textContent||"").trim()),
      iw:innerWidth,bodyW:document.body.scrollWidth,htmlW:document.documentElement.scrollWidth,
      imgs,targets,
      bg:getComputedStyle(document.body).backgroundColor,
      css:[...document.styleSheets].map(s=>s.href||"").filter(Boolean)
    };
   });
   const overflow=Math.max(x.bodyW,x.htmlW)-x.iw;
   const broken=x.imgs.filter(i=>!i.ok);
   const imgOverflow=x.imgs.filter(i=>i.left<-3||i.right>x.iw+3);
   const visiblePeople=x.imgs.filter(i=>/photo-(park-training|initial-eval|trainer-session)/.test(i.src));
   const under24=v.name==="mobile"?x.targets.filter(t=>Math.min(t.w,t.h)<24):[];
   const pass=x.signature==="r423"&&x.h1.length===1&&overflow<=2&&broken.length===0&&imgOverflow.length===0&&visiblePeople.length===0&&under24.length===0&&x.css.some(h=>h.endsWith("/assets/signature-r423.css"));
   await p.screenshot({path:`${out}/${page.name}-${v.name}-${v.width}-dpr${v.dpr}.png`,fullPage:true});
   results.push({page:page.name,...v,overflow,broken:broken.map(x=>x.src),imgOverflow:imgOverflow.map(x=>x.src),visiblePeople:visiblePeople.map(x=>x.src),under24,background:x.bg,pass});
   await p.close();
  }
 }
}finally{await browser.close();}
await writeFile(`${out}/results.json`,JSON.stringify({schema:"iberfit.web.signature-r423.render-qa.v1",results},null,2)+"\n");
console.log(JSON.stringify(results,null,2));
if(results.some(x=>!x.pass))process.exitCode=1;
