#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const ROOT='candidate/v628';
const files=[];
function walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);e.isDirectory()?walk(p):files.push(p)}}
walk(ROOT);
const rel=p=>p.slice(ROOT.length+1).split(path.sep).join('/');
const htmlFiles=files.filter(p=>p.endsWith('.html'));
const codeFiles=files.filter(p=>/\.(?:html|js|css|json|txt|xml|md|webmanifest)$/.test(p));
const textByFile=new Map(codeFiles.map(p=>[rel(p),fs.readFileSync(p,'utf8')]));

const findings=[];
const evidence={};
const add=(severity,code,file,detail)=>findings.push({severity,code,file,detail});

evidence.counts={
  packageFiles:files.length,
  html:htmlFiles.length,
  css:files.filter(p=>p.endsWith('.css')).length,
  js:files.filter(p=>p.endsWith('.js')).length,
  webp:files.filter(p=>p.endsWith('.webp')).length,
  png:files.filter(p=>p.endsWith('.png')).length
};

const secretPatterns=[
  [/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,'PRIVATE_KEY'],
  [/\bsk-[A-Za-z0-9_-]{20,}\b/,'OPENAI_LIKE_SECRET'],
  [/\b(?:CLOUDFLARE_API_TOKEN|SUPABASE_SERVICE_ROLE_KEY|AWS_SECRET_ACCESS_KEY)\s*[:=]\s*['"][^'"]+/i,'SECRET_ASSIGNMENT'],
  [/\bBearer\s+[A-Za-z0-9._-]{30,}/i,'BEARER_TOKEN'],
  [/\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\b/,'JWT']
];
for(const [file,text] of textByFile) for(const [re,code] of secretPatterns) if(re.test(text)) add('critical',code,file,'possible embedded secret');

const jsonLd=[];
const images=[];
const targetBlank=[];
const waLinks=[];
const mailLinks=[];
const telephoneLinks=[];
const appMentions=[];
const promiseMentions=[];
const priceMentions=[];
const names=[];
const forms=[];
const externalOrigins=new Set();

for(const p of htmlFiles){
  const file=rel(p), s=fs.readFileSync(p,'utf8');
  for(const m of s.matchAll(/<script[^>]+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)){
    try{JSON.parse(m[1]);jsonLd.push({file,ok:true})}catch(e){jsonLd.push({file,ok:false,error:String(e)});add('error','INVALID_JSONLD',file,String(e))}
  }
  for(const m of s.matchAll(/<img\b([^>]*)>/gi)){
    const attrs=m[1]; const src=(attrs.match(/\bsrc=["']([^"']+)/i)||[])[1]||'';
    const alt=(attrs.match(/\balt=["']([^"']*)/i)||[]);
    images.push({file,src,hasAlt:!!alt.length,alt:alt[1]??null});
    if(!alt.length)add('error','IMG_ALT_MISSING',file,src);
  }
  for(const m of s.matchAll(/<a\b([^>]*)>/gi)){
    const attrs=m[1], href=(attrs.match(/\bhref=["']([^"']+)/i)||[])[1]||'';
    const target=(attrs.match(/\btarget=["']([^"']+)/i)||[])[1]||'';
    const relA=(attrs.match(/\brel=["']([^"']+)/i)||[])[1]||'';
    if(target==='_blank'){targetBlank.push({file,href,rel:relA}); if(!/noopener/i.test(relA))add('error','TARGET_BLANK_NO_NOOPENER',file,href)}
    if(/wa\.me/i.test(href))waLinks.push({file,href});
    if(/^mailto:/i.test(href))mailLinks.push({file,href});
    if(/^tel:/i.test(href))telephoneLinks.push({file,href});
    try{const u=new URL(href,'https://iberfit.cl'); if(/^https?:/.test(u.protocol)&&u.hostname!=='iberfit.cl')externalOrigins.add(u.origin)}catch{}
  }
  for(const m of s.matchAll(/<form\b([^>]*)>([\s\S]*?)<\/form>/gi)){
    const body=m[2];
    forms.push({file,action:(m[1].match(/action=["']([^"']*)/i)||[])[1]||'',inputs:[...body.matchAll(/<(?:input|select|textarea)\b([^>]*)>/gi)].map(x=>({name:(x[1].match(/name=["']([^"']*)/i)||[])[1]||'',type:(x[1].match(/type=["']([^"']*)/i)||[])[1]||'',autocomplete:(x[1].match(/autocomplete=["']([^"']*)/i)||[])[1]||''}))});
  }
  const visible=s.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ');
  for(const re of [/\bapp\b/ig,/aplicaci[oó]n/ig,/real[- ]?time/ig,/tiempo real/ig]) if(re.test(visible)) appMentions.push({file,pattern:String(re)});
  for(const re of [/garant\w*/ig,/disponibilidad/ig,/24\/7/ig,/videollamada/ig,/video call/ig,/tiempo de respuesta/ig,/response time/ig]) if(re.test(visible)) promiseMentions.push({file,pattern:String(re)});
  for(const re of [/\$\s*\d[\d.]{2,}/g,/\bCLP\b/ig,/\bprecio\b/ig,/\bprice\b/ig]) if(re.test(visible)) priceMentions.push({file,pattern:String(re)});
  for(const name of ['María José Lucero','Rafael Velasco']) if(visible.includes(name)) names.push({file,name});
}

const allCss=files.filter(p=>p.endsWith('.css')).map(p=>fs.readFileSync(p,'utf8')).join('\n');
evidence.fonts={
  fontFaceCount:(allCss.match(/@font-face/gi)||[]).length,
  googleFontsRefs:(allCss.match(/fonts\.googleapis\.com/gi)||[]).length,
  families:[...new Set([...allCss.matchAll(/font-family\s*:\s*([^;}{]+)/gi)].map(m=>m[1].trim()))].slice(0,50)
};

const headers=fs.readFileSync(path.join(ROOT,'_headers'),'utf8');
const redirects=fs.readFileSync(path.join(ROOT,'_redirects'),'utf8');
evidence.securityHeaders={
  csp:/Content-Security-Policy:/i.test(headers),
  hsts:/Strict-Transport-Security:/i.test(headers),
  frameDeny:/X-Frame-Options:\s*DENY/i.test(headers),
  nosniff:/X-Content-Type-Options:\s*nosniff/i.test(headers),
  referrer:/Referrer-Policy:/i.test(headers),
  permissions:/Permissions-Policy:/i.test(headers),
};
evidence.redirects=redirects.split(/\r?\n/).filter(x=>x.trim()&&!x.trim().startsWith('#'));

const analytics=textByFile.get('assets/analytics.v64322.js')||'';
const analyticsConfig=textByFile.get('assets/analytics-config.js')||'';
evidence.analytics={
  ga4PublicId:(analyticsConfig.match(/ga4MeasurementId:\s*["']([^"']+)/)||[])[1]||null,
  metaPixelPublicId:(analyticsConfig.match(/metaPixelId:\s*["']([^"']+)/)||[])[1]||null,
  consentDefaultDenied:/analytics_storage:"denied"/.test(analytics)&&/ad_storage:"denied"/.test(analytics),
  loadsGaAfterAnalyticsConsent:/d\(\)&&A\(\)/.test(analytics),
  loadsMetaAfterMarketingConsent:/i\(\)&&\$\(\)/.test(analytics),
  anonymizeIp:/anonymize_ip:!0/.test(analytics),
  googleSignalsDisabled:/allow_google_signals:!1/.test(analytics),
  personalizationDisabled:/allow_ad_personalization_signals:!1/.test(analytics),
  tracksGenerateLead:/generate_lead/.test(analytics),
  tracksWhatsapp:/whatsapp_click/.test(analytics),
  tracksEmail:/contact_email_click/.test(analytics),
  storageKeys:[...new Set([...analytics.matchAll(/(?:localStorage|sessionStorage)\.(?:getItem|setItem)\(([^)]+)/g)].map(m=>m[1]))]
};

const home=fs.readFileSync(path.join(ROOT,'index.html'),'utf8');
const iri=fs.readFileSync(path.join(ROOT,'diagnostico-iri/index.html'),'utf8');
const presencial=fs.readFileSync(path.join(ROOT,'presencial/index.html'),'utf8');
const online=fs.readFileSync(path.join(ROOT,'online/index.html'),'utf8');
const hybrid=fs.readFileSync(path.join(ROOT,'hibrido/index.html'),'utf8');
const contact=fs.readFileSync(path.join(ROOT,'contacto/index.html'),'utf8');
const strip=s=>s.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi,' ').replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi,' ').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
const homeV=strip(home), iriV=strip(iri), presencialV=strip(presencial), onlineV=strip(online), hybridV=strip(hybrid), contactV=strip(contact);

evidence.commercial={
  homeDirectContact:/Cu[eé]ntanos qu[eé] buscas|Cu[eé]ntanos tu caso/i.test(homeV),
  homeIriCTA:/Empezar por el IRI|Diagn[oó]stico IRI/i.test(homeV),
  contactHasNoCommitment:/sin compromiso/i.test(contactV)&&/no te obliga a contratar/i.test(contactV),
  presencialMentionsHome:/domicilio/i.test(presencialV),
  presencialMentionsBuildingGym:/gimnasio de edificio/i.test(presencialV),
  presencialMentionsOutdoor:/parque|zona verde|entorno exterior/i.test(presencialV),
  presencialExplicitNoOwnGym:/no (?:tenemos|dispone|contamos con) (?:un )?gimnasio propio/i.test(presencialV),
  onlineNamedCanonical:/entrenamiento personal online/i.test(onlineV),
  hybridNamed:/h[ií]brid/i.test(hybridV),
  iriExplicitInitial:/evaluaci[oó]n inicial|l[ií]nea de base/i.test(iriV),
  iriSeparatesEvolution:/no es.*(?:evoluci[oó]n|seguimiento)|seguimiento.*posterior/i.test(iriV),
  iriBioimpedanceNotMedical:/no es un diagn[oó]stico m[eé]dico/i.test(iriV),
  fictitiousDemo:/datos ficticios|ejemplo ficticio|datos de ejemplo/i.test(homeV+' '+iriV),
  googleReviews:names,
};

evidence.forms=forms;
evidence.links={
  whatsappCount:waLinks.length,
  whatsappUnique:[...new Set(waLinks.map(x=>x.href))].length,
  emailCount:mailLinks.length,
  telephoneCount:telephoneLinks.length,
  targetBlankCount:targetBlank.length,
  externalOrigins:[...externalOrigins].sort()
};
evidence.contentFlags={appMentions,promiseMentions,priceMentions};
evidence.jsonLd={blocks:jsonLd.length,invalid:jsonLd.filter(x=>!x.ok)};
evidence.images={count:images.length,missingAlt:images.filter(x=>!x.hasAlt)};

if(evidence.counts.packageFiles!==117)add('error','PACKAGE_FILE_COUNT','candidate/v628',String(evidence.counts.packageFiles));
if(evidence.counts.html!==33)add('error','HTML_COUNT','candidate/v628',String(evidence.counts.html));
if(!Object.values(evidence.securityHeaders).every(Boolean))add('error','SECURITY_HEADERS_INCOMPLETE','_headers',JSON.stringify(evidence.securityHeaders));
if(!evidence.analytics.consentDefaultDenied)add('error','CONSENT_NOT_DEFAULT_DENIED','assets/analytics.v64322.js','');
if(evidence.jsonLd.invalid.length)add('error','JSONLD_INVALID','candidate/v628',JSON.stringify(evidence.jsonLd.invalid));
if(evidence.images.missingAlt.length)add('error','IMAGE_ALT_GAPS','candidate/v628',String(evidence.images.missingAlt.length));

const out={schema:'iberfit.static-prod-integrity.v1',checkedAt:new Date().toISOString(),sourceSha:'424700ae15c6138c8a07f15f82f5b34d62c51a9f',evidence,findings,ok:!findings.some(x=>['critical','error'].includes(x.severity))};
fs.mkdirSync('evidence/static-prod',{recursive:true});
fs.writeFileSync('evidence/static-prod/report.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));
if(!out.ok)process.exit(1);
