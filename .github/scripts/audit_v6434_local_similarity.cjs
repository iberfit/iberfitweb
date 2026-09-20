const fs=require('fs');
const path=require('path');

const root=path.resolve('candidate/v628');
const pages=[
  ['Las Condes','entrenador-personal-las-condes/index.html'],
  ['Vitacura','entrenador-personal-vitacura/index.html'],
  ['Providencia','entrenamiento-personal-providencia/index.html'],
  ['Lo Barnechea','entrenador-personal-lo-barnechea/index.html'],
  ['Ñuñoa','personal-trainer-nunoa/index.html'],
  ['La Reina','entrenador-personal-la-reina/index.html'],
  ['Peñalolén','entrenador-personal-penalolen/index.html']
];

function mainText(rel, commune){
  let html=fs.readFileSync(path.join(root,rel),'utf8');
  html=(html.match(/<main\b[^>]*>([\s\S]*?)<\/main>/i)||[])[1]||'';
  html=html.replace(/<script[\s\S]*?<\/script>/gi,' ').replace(/<style[\s\S]*?<\/style>/gi,' ');
  let text=html.replace(/<[^>]+>/g,' ').replace(/&nbsp;/g,' ').replace(/&amp;/g,'&').replace(/&#[0-9]+;/g,' ');
  const variants=[commune, commune.normalize('NFD').replace(/[\u0300-\u036f]/g,''), 'IBERFIT'];
  for(const v of variants){ text=text.replace(new RegExp(v.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi'),' '); }
  text=text.toLowerCase().replace(/[^a-záéíóúüñ0-9]+/gi,' ').replace(/\s+/g,' ').trim();
  return text;
}
function shingles(text,n=5){
  const w=text.split(' ').filter(Boolean), s=new Set();
  for(let i=0;i<=w.length-n;i++) s.add(w.slice(i,i+n).join(' '));
  return s;
}
function jaccard(a,b){
  let inter=0; for(const x of a) if(b.has(x)) inter++;
  const union=a.size+b.size-inter;
  return union?inter/union:0;
}
function headings(rel){
  const html=fs.readFileSync(path.join(root,rel),'utf8');
  return [...html.matchAll(/<(h1|h2|h3)[^>]*>([\s\S]*?)<\/\1>/gi)].map(m=>m[2].replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim());
}

const docs=pages.map(([name,rel])=>({name,rel,text:mainText(rel,name),heads:headings(rel)}));
const rows=[];
for(let i=0;i<docs.length;i++) for(let j=i+1;j<docs.length;j++){
  const a=shingles(docs[i].text),b=shingles(docs[j].text);
  const sim=jaccard(a,b);
  const hA=new Set(docs[i].heads.map(x=>x.toLowerCase()));
  const hB=new Set(docs[j].heads.map(x=>x.toLowerCase()));
  const shared=[...hA].filter(x=>hB.has(x));
  rows.push({a:docs[i].name,b:docs[j].name,shingle5:Number(sim.toFixed(3)),sharedHeadings:shared.length});
}
rows.sort((x,y)=>y.shingle5-x.shingle5);
const avg=rows.reduce((s,r)=>s+r.shingle5,0)/rows.length;
const max=rows[0];
console.log(JSON.stringify({pages:docs.map(d=>({name:d.name,headings:d.heads})),pairwise:rows,averageShingle5:Number(avg.toFixed(3)),highest:max},null,2));
if(max.shingle5>0.42) process.exitCode=2;
