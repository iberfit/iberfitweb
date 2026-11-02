import { chromium } from "playwright";
import { mkdir, writeFile } from "node:fs/promises";

const base="http://127.0.0.1:8791";
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
const out="signature-r423-art-evidence";
await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true});
const results=[];
try{
  for(const page of pages){
    for(const v of viewports){
      const p=await browser.newPage({viewport:{width:v.width,height:v.height},deviceScaleFactor:v.dpr});
      await p.goto(base+page.path,{waitUntil:"networkidle"});
      await p.waitForTimeout(450);
      const x=await p.evaluate(()=>({
        signature:document.body.dataset.signature||"",
        h1:(document.querySelector("h1")?.textContent||"").trim(),
        bodyWidth:document.body.scrollWidth,
        innerWidth,
        broken:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src),
        people:[...document.images].filter(i=>/photo-(park-training|initial-eval|trainer-session)/.test(i.getAttribute("src")||"")).filter(i=>{const r=i.getBoundingClientRect(),s=getComputedStyle(i);return r.width>0&&r.height>0&&s.display!=="none"&&s.visibility!=="hidden"}).map(i=>i.getAttribute("src"))
      }));
      const file=`${out}/${page.name}-${v.name}-${v.width}-dpr${v.dpr}.png`;
      await p.screenshot({path:file,fullPage:true});
      results.push({page:page.name,...v,...x,file,pass:x.signature==="r423"&&x.bodyWidth<=x.innerWidth+2&&x.broken.length===0&&x.people.length===0});
      await p.close();
    }
  }
}finally{await browser.close();}
await writeFile(`${out}/results.json`,JSON.stringify({schema:"iberfit.web.signature-r423.art-review.v1",results},null,2)+"\n");
console.log(JSON.stringify(results,null,2));
if(results.some(x=>!x.pass))process.exitCode=1;
