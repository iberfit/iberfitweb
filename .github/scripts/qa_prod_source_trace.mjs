#!/usr/bin/env node
import { readdir, readFile, stat, mkdir, writeFile } from 'node:fs/promises';
import { join, relative, posix } from 'node:path';
import { createHash } from 'node:crypto';

const ROOT='candidate/v628';
const ORIGINS=[
  {name:'production',url:'https://iberfit.cl'},
  {name:'deployment',url:'https://d18cb0e7.web-iberfit.pages.dev'}
];
const OUT=process.env.QA_OUT||'evidence/prod-source-trace';

async function walk(dir){
  const out=[];
  for(const e of await readdir(dir,{withFileTypes:true})){
    const p=join(dir,e.name);
    if(e.isDirectory()) out.push(...await walk(p));
    else if(e.isFile()) out.push(p);
  }
  return out;
}
const sha=b=>createHash('sha256').update(b).digest('hex');
function urlPath(rel){
  const p=rel.split('\\').join('/');
  if(p==='index.html') return '/';
  if(p.endsWith('/index.html')) return '/'+p.slice(0,-'index.html'.length);
  return '/'+p;
}
async function fetchBytes(url){
  const r=await fetch(url,{redirect:'follow',headers:{'user-agent':'IBERFIT-Production-Source-Trace/1.0'}});
  const body=Buffer.from(await r.arrayBuffer());
  return {status:r.status,ok:r.ok,finalUrl:r.url,body,headers:Object.fromEntries(r.headers.entries())};
}
function textDiffHint(local,remote){
  const a=local.toString('utf8'), b=remote.toString('utf8');
  let p=0; while(p<a.length&&p<b.length&&a[p]===b[p])p++;
  let s=0; while(s<a.length-p&&s<b.length-p&&a[a.length-1-s]===b[b.length-1-s])s++;
  return {
    deltaBytes:Buffer.byteLength(b)-Buffer.byteLength(a),
    commonPrefixChars:p,
    commonSuffixChars:s,
    localChanged:a.slice(p,a.length-s).slice(0,1600),
    remoteChanged:b.slice(p,b.length-s).slice(0,2600)
  };
}
const all=(await walk(ROOT)).map(p=>relative(ROOT,p).split('\\').join('/')).sort();
const configFiles=['_headers','_redirects'];
const publishable=all.filter(x=>!configFiles.includes(x));
if(all.length!==117) throw new Error('EXPECTED_117_PACKAGE_FILES_GOT_'+all.length);
if(publishable.length!==115) throw new Error('EXPECTED_115_PUBLISHED_ASSETS_GOT_'+publishable.length);

const results=[];
for(const rel of publishable){
  const local=await readFile(join(ROOT,rel));
  const localSha=sha(local);
  const row={path:rel,urlPath:urlPath(rel),localBytes:local.length,localSha256:localSha,origins:{}};
  for(const origin of ORIGINS){
    try{
      const x=await fetchBytes(origin.url+row.urlPath);
      row.origins[origin.name]={
        status:x.status,
        finalUrl:x.finalUrl,
        bytes:x.body.length,
        sha256:sha(x.body),
        match:sha(x.body)===localSha,
        contentType:x.headers['content-type']||null,
        etag:x.headers.etag||null,
        xRobotsTag:x.headers['x-robots-tag']||null,
        cfCacheStatus:x.headers['cf-cache-status']||null,
        ...(sha(x.body)!==localSha && (/\.html$/.test(rel)||rel==='robots.txt') ? {diffHint:textDiffHint(local,x.body)} : {})
      };
    }catch(e){
      row.origins[origin.name]={error:String(e),match:false};
    }
  }
  results.push(row);
}

for(const cfg of configFiles){
  const x=await fetchBytes(ORIGINS[0].url+'/'+cfg);
  results.push({path:cfg,config:true,productionStatus:x.status,servedAsStaticAsset:x.status>=200&&x.status<300});
}

const assetRows=results.filter(x=>!x.config);
const summary={
  schema:'iberfit.prod-source-trace.v1',
  checkedAt:new Date().toISOString(),
  expectedSourceSha:'424700ae15c6138c8a07f15f82f5b34d62c51a9f',
  packageFiles:all.length,
  cloudflareConfigFiles:configFiles.length,
  expectedPublishedAssets:publishable.length,
  origins:{},
  configs:{}
};
for(const o of ORIGINS){
  const mismatches=assetRows.filter(r=>!r.origins[o.name]?.match);
  const statuses={};
  for(const r of assetRows){
    const k=String(r.origins[o.name]?.status??'ERR'); statuses[k]=(statuses[k]||0)+1;
  }
  summary.origins[o.name]={
    origin:o.url,
    compared:assetRows.length,
    exactMatches:assetRows.length-mismatches.length,
    mismatches:mismatches.length,
    statuses,
    mismatchPaths:mismatches.slice(0,50).map(r=>({path:r.path,remote:r.origins[o.name]}))
  };
}
for(const cfg of results.filter(x=>x.config)) summary.configs[cfg.path]={status:cfg.productionStatus,servedAsStaticAsset:cfg.servedAsStaticAsset};

await mkdir(OUT,{recursive:true});
await writeFile(join(OUT,'source-trace.json'),JSON.stringify({summary,results},null,2)+'\n');
console.log(JSON.stringify(summary,null,2));

const prod=summary.origins.production;
const dep=summary.origins.deployment;
const expectedProdLayer=new Set([
  '404.html','robots.txt',
  ...publishable.filter(x=>x.endsWith('.html'))
]);
const prodMismatchSet=new Set(assetRows.filter(r=>!r.origins.production?.match).map(r=>r.path));
const prodLayerExpected=prodMismatchSet.size===expectedProdLayer.size && [...prodMismatchSet].every(x=>expectedProdLayer.has(x));
summary.productionLayerClassification=prodLayerExpected ? 'ONLY_HTML_AND_ROBOTS_TRANSFORMED' : 'UNEXPECTED_ASSET_MISMATCHES';
if(dep.mismatches!==0) throw new Error('DEPLOYMENT_URL_DOES_NOT_MATCH_CHECKPOINT');
if(!prodLayerExpected) throw new Error('PRODUCTION_HAS_UNEXPECTED_ASSET_MISMATCHES');
if(summary.configs._headers.servedAsStaticAsset) throw new Error('_headers_SHOULD_NOT_BE_STATIC_ASSET');
if(summary.configs._redirects.servedAsStaticAsset) throw new Error('_redirects_SHOULD_NOT_BE_STATIC_ASSET');
console.log('PRODUCTION_SOURCE_EXACT_MATCH_115_OF_115');
