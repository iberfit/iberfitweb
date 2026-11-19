#!/usr/bin/env node
const BASE='https://iberfit.cl';
const redirects=[
 ['/diagnostico-iri.html','/diagnostico-iri/'],
 ['/metodo.html','/metodo/'],
 ['/presencial.html','/presencial/'],
 ['/hibrido.html','/hibrido/'],
 ['/online.html','/online/'],
 ['/sobre.html','/sobre-iberfit/'],
 ['/sobre-iberfit.html','/sobre-iberfit/'],
 ['/contacto.html','/contacto/'],
 ['/privacidad.html','/privacidad/'],
 ['/en.html','/en/'],
];
const fail=[], evidence={checkedAt:new Date().toISOString(),redirects:[],headers:{},resources:{},observations:{}};
const req=async(path,opts={})=>{
 const r=await fetch(BASE+path,{redirect:opts.redirect||'manual',headers:{'user-agent':'IBERFIT-Live-HTTP-Audit/1.0'}});
 return {status:r.status,location:r.headers.get('location'),headers:Object.fromEntries(r.headers.entries()),text:opts.body===false?'':await r.text(),url:r.url};
};
for(const [from,to] of redirects){
 const r=await req(from);
 evidence.redirects.push({from,to,status:r.status,location:r.location});
 if(![301,302,307,308].includes(r.status))fail.push({code:'REDIRECT_STATUS',from,status:r.status});
 const loc=r.location?new URL(r.location,BASE).pathname:'';
 if(loc!==to)fail.push({code:'REDIRECT_TARGET',from,expected:to,actual:loc});
}
const home=await req('/');
const required={
 'content-security-policy':/default-src 'self'/,
 'strict-transport-security':/max-age=31536000/i,
 'x-frame-options':/^DENY$/i,
 'x-content-type-options':/^nosniff$/i,
 'referrer-policy':/strict-origin-when-cross-origin/i,
 'permissions-policy':/camera=\(\)/i
};
for(const [h,re] of Object.entries(required)){
 const v=home.headers[h]||''; evidence.headers[h]=v; if(!re.test(v))fail.push({code:'HEADER_MISSING_OR_UNEXPECTED',header:h,value:v});
}
for(const p of ['/robots.txt','/sitemap.xml','/llms.txt','/assets/styles.v628.css','/assets/photo-park-training-1448.webp','/__iberfit_missing_404_probe__']){
 const r=await req(p,{redirect:'follow'});
 evidence.resources[p]={status:r.status,cacheControl:r.headers['cache-control']||null,contentType:r.headers['content-type']||null,bytes:Buffer.byteLength(r.text)};
 if(p==='/robots.txt'){
  evidence.observations.robotsManaged=/BEGIN Cloudflare Managed content/.test(r.text);
  evidence.observations.robotsHasSitemap=/Sitemap:\s*https:\/\/iberfit\.cl\/sitemap\.xml/i.test(r.text);
  if(!evidence.observations.robotsHasSitemap)fail.push({code:'ROBOTS_SITEMAP_MISSING'});
 }
 if(p==='/sitemap.xml'){
  const count=(r.text.match(/<loc>/g)||[]).length;evidence.observations.sitemapUrls=count;
  if(count!==32)fail.push({code:'SITEMAP_URL_COUNT',count});
 }
 if(p==='/llms.txt'&&r.status!==200)fail.push({code:'LLMS_STATUS',status:r.status});
 if(p.includes('missing_404')&&r.status!==404)fail.push({code:'CUSTOM_404_STATUS',status:r.status});
 if(p==='/assets/styles.v628.css'&&!/immutable/i.test(r.headers['cache-control']||''))fail.push({code:'CSS_CACHE_NOT_IMMUTABLE',value:r.headers['cache-control']});
 if(p.endsWith('.webp')&&!/immutable/i.test(r.headers['cache-control']||''))fail.push({code:'IMAGE_CACHE_NOT_IMMUTABLE',value:r.headers['cache-control']});
}
const oldEn=await req('/en/contacto/');
evidence.observations.enContactoLegacy={status:oldEn.status,location:oldEn.location};
const deployment=await fetch('https://d18cb0e7.web-iberfit.pages.dev/',{redirect:'follow'});
evidence.observations.deploymentHomeStatus=deployment.status;
const out={schema:'iberfit.live-http-surface.v1',evidence,failures:fail,ok:fail.length===0};
console.log(JSON.stringify(out,null,2));
import fs from 'node:fs';fs.mkdirSync('evidence/live-http',{recursive:true});fs.writeFileSync('evidence/live-http/report.json',JSON.stringify(out,null,2)+'\n');
if(fail.length)process.exit(1);
