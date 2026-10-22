#!/usr/bin/env node
/** IBERFIT live-site content audit. Read-only; Node 20+, no external packages. */
const fs = require('node:fs');
const original = fs.readFileSync('tools/iberfit-web-live-audit.mjs','utf8');
function routes(name) {const body=original.match(new RegExp('const '+name+' = \\[([\\s\\S]*?)\\];'))?.[1]; if(!body) throw Error('Missing route manifest '+name); return [...body.matchAll(/'([^']+)'/g)].map(x=>x[1]);}
const ES=routes('ES'), EN=routes('EN'), paths=[...ES,...EN], origin='https://iberfit.cl';
const decode=s=>s.replace(/&(?:nbsp|amp|quot|apos|lt|gt|#\d+);/gi,m=>({'&nbsp;':' ','&amp;':'&','&quot;':'"','&apos;':"'",'&lt;':'<','&gt;':'>'})[m.toLowerCase()]||' ');
const strip=s=>decode((s||'').replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ')).trim();
function attrs(tag){const a={};for(const m of tag.matchAll(/([\w:-]+)\s*=\s*(['"])(.*?)\2/gs))a[m[1].toLowerCase()]=m[3];return a;}
const tokenize=s=>s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,' ').split(/\s+/).filter(Boolean);
const grams=t=>{const s=new Set();for(let i=0;i<t.length-4;i++)s.add(t.slice(i,i+5).join(' '));return s;};
const dice=(a,b)=>{if(!(a.size&&b.size))return null;let count=0;for(const t of a)if(b.has(t))count++;return Math.round(2000*count/(a.size+b.size))/10;};
async function inspect(path) {
 const resp=await fetch(origin+path,{signal:AbortSignal.timeout(18000),headers:{'user-agent':'IBERFIT-ReadOnly-Content-Audit/1.0'},redirect:'manual'});
 const html=await resp.text(), main=html.match(/<main\b[^>]*>([\s\S]*?)<\/main>/i)?.[1]||html.replace(/<(?:header|footer|nav)\b[^>]*>[\s\S]*?<\/(?:header|footer|nav)>/gi,' ');
 const body=strip(main), words=tokenize(body);
 const title=strip(html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]);
 const desc=([...html.matchAll(/<meta\b[^>]*>/gi)].map(m=>attrs(m[0])).find(x=>x.name==='description')||{}).content||'';
 const img=[...main.matchAll(/<img\b[^>]*>/gi)].map(m=>attrs(m[0]));
 const links=[...html.matchAll(/<a\b[^>]*>/gi)].map(m=>attrs(m[0])).filter(x=>x.href);
 const internal=new Set(),unknown=new Set(),whatsapp=[];
 for(const a of links){if(/(?:wa\.me|api\.whatsapp\.com)/i.test(a.href))whatsapp.push(a.href);try{const u=new URL(a.href,origin+path);if(u.origin===origin){if(paths.includes(u.pathname))internal.add(u.pathname);else if(!u.pathname.startsWith('/assets/')&&!['/sitemap.xml','/robots.txt'].includes(u.pathname))unknown.add(u.pathname);}}catch{}}
 const headings={};for(const h of ['h1','h2'])headings[h]=[...main.matchAll(new RegExp('<'+h+'\\b[^>]*>([\\s\\S]*?)<\\/'+h+'>','gi'))].map(m=>strip(m[1]));
 return {path,http:resp.status,title,description:desc,mainWords:words.length,headings,images:img.length,imagesMissingAlt:img.filter(x=>!('alt'in x)).length,internalLinks:[...internal],unknownInternalLinks:[...unknown],whatsappLinks:[...new Set(whatsapp)],excerpt:body.slice(0,520),_gram:grams(words)};
}
async function main(){
 if(paths.length!==32)throw Error('Route count must remain 32');
 const errors=[],pages=[];let next=0;
 await Promise.all(Array.from({length:4},async()=>{while(next<paths.length){const p=paths[next++];try{const a=await inspect(p);pages.push(a);if(a.http!==200)errors.push(p+' HTTP '+a.http);}catch(e){pages.push({path:p,error:e.message});errors.push(p+': '+e.message);}}}));
 pages.sort((a,b)=>paths.indexOf(a.path)-paths.indexOf(b.path));
 const backlinks=Object.fromEntries(paths.map(p=>[p,0])),depth=Object.fromEntries(paths.map(p=>[p,null]));depth['/']=0;depth['/en/']=0;
 for(const page of pages)for(const x of page.internalLinks||[])backlinks[x]++;
 for(let i=0;i<32;i++){let update=false;for(const page of pages){if(depth[page.path]===null)continue;for(const x of page.internalLinks||[])if(depth[x]===null||depth[x]>depth[page.path]+1){depth[x]=depth[page.path]+1;update=true}}if(!update)break}
 const pairs=[];for(const list of [ES.slice(9),EN.slice(9)])for(let i=0;i<list.length;i++)for(let j=i+1;j<list.length;j++){const a=pages.find(p=>p.path===list[i]),b=pages.find(p=>p.path===list[j]);const pct=dice(a._gram||new Set(),b._gram||new Set());if(pct!==null)pairs.push({a:a.path,b:b.path,fiveWordShingleSimilarityPercent:pct})}
 pairs.sort((a,b)=>b.fiveWordShingleSimilarityPercent-a.fiveWordShingleSimilarityPercent);
 const recs=[];for(const page of pages){if(page.http!==200)continue;if(page.imagesMissingAlt)recs.push({page:page.path,reason:'images-missing-alt',count:page.imagesMissingAlt});if(page.mainWords<130)recs.push({page:page.path,reason:'short-main-text',words:page.mainWords});if(depth[page.path]===null)recs.push({page:page.path,reason:'unreachable-from-home'});if(depth[page.path]>3)recs.push({page:page.path,reason:'deep-navigation',depth:depth[page.path]});if(page.unknownInternalLinks.length)recs.push({page:page.path,reason:'link-not-in-sitemap',paths:page.unknownInternalLinks});}
 const report={auditedAt:new Date().toISOString(),origin,checked:paths.length,reached:pages.filter(p=>p.http===200).length,errors,summary:{zeroInbound:paths.filter(p=>backlinks[p]===0),unreachableFromHome:paths.filter(p=>depth[p]===null),maxNavigationDepth:Math.max(...Object.values(depth).filter(x=>x!==null)),pagesWithWhatsapp:pages.filter(p=>p.whatsappLinks?.length).length,imagesMissingAlt:pages.reduce((s,p)=>s+(p.imagesMissingAlt||0),0),localPageSimilarityHighest:pairs.slice(0,14),opportunities:recs.length},opportunities:recs,pages:pages.map(({_gram,...p})=>({...p,inbound:backlinks[p.path],clickDepth:depth[p.path]}))};
 console.log(JSON.stringify(report,null,2));if(errors.length)process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exitCode=1});