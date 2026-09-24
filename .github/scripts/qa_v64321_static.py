from pathlib import Path
import subprocess,re,json,html

BASE='a9af3b52d67332f323f5e648613e609661f31639'
root=Path('candidate/v628')
assert root.joinpath('VERSION').read_text().strip()=='6.43.21'
htmls=sorted(root.rglob('*.html'))
assert len(htmls)==33
link='<link href="/assets/contrast.v64321.css" rel="stylesheet"/>'
mutable={
 'candidate/v628/index.html','candidate/v628/en/index.html',
 'candidate/v628/entrenador-personal-las-condes/index.html','candidate/v628/en/personal-trainer-las-condes/index.html',
 'candidate/v628/entrenador-personal-vitacura/index.html','candidate/v628/en/personal-trainer-vitacura/index.html',
 'candidate/v628/entrenador-personal-lo-barnechea/index.html','candidate/v628/en/personal-trainer-lo-barnechea/index.html',
 'candidate/v628/entrenador-personal-penalolen/index.html','candidate/v628/en/personal-trainer-penalolen/index.html',
 'candidate/v628/personal-trainer-nunoa/index.html','candidate/v628/en/personal-trainer-nunoa/index.html',
 'candidate/v628/entrenamiento-personal-providencia/index.html','candidate/v628/en/personal-training-providencia/index.html',
}
def extract(pattern,text): return re.findall(pattern,text,re.I|re.S)
def visible(raw):
 raw=re.sub(r'<script\b.*?</script>|<style\b.*?</style>',' ',raw,flags=re.I|re.S)
 raw=re.sub(r'<[^>]+>',' ',raw)
 return re.sub(r'\s+',' ',html.unescape(raw)).strip()

visible_by_rel={}
for p in htmls:
 rel=p.as_posix(); new=p.read_text(encoding='utf-8'); assert new.count('contrast.v64321.css')==1,rel
 old=subprocess.check_output(['git','show',f'{BASE}:{rel}'],text=True)
 no_css=new.replace(link,'')
 if rel not in mutable: assert no_css==old,rel
 else: assert no_css.split('</head>',1)[0]==old.split('</head>',1)[0],rel
 for pattern in [r'<link\b[^>]*rel="canonical"[^>]*>',r'<link\b[^>]*hreflang="[^"]+"[^>]*>',r'href="https://wa\.me/[^"]+"',r'<script type="application/ld\+json">(.*?)</script>',r'<script\b[^>]*src="/assets/(?:analytics-config\.js|analytics\.v643\.js)"[^>]*>']:
  assert extract(pattern,no_css)==extract(pattern,old),(rel,pattern)
 for raw in extract(r'<script type="application/ld\+json">(.*?)</script>',new): json.loads(raw)
 body=re.search(r'<body\b.*?</body>',new,re.I|re.S)
 visible_by_rel[p.relative_to(root).as_posix()]=visible(body.group(0) if body else new)

changed=set(subprocess.check_output(['git','diff','--name-only',BASE,'--','candidate/v628'],text=True).splitlines())
expected={'candidate/v628/VERSION','candidate/v628/CHANGELOG.md','candidate/v628/assets/contrast.v64321.css'}|{p.as_posix() for p in htmls}
assert changed==expected,(changed-expected,expected-changed)
subprocess.check_call(['git','diff','--exit-code',BASE,'--','candidate/v628/_headers'])

commercial='\n'.join(visible_by_rel.values())
for phrase in ['Primero vemos si podemos hacerlo bien, no solo si podemos ir','We first check whether we can deliver the service well','Según cobertura presencial','Where in-person coverage allows','viabilidad de una frecuencia presencial','frecuencia es viable','frecuencia viable','cuando la ubicación lo permite','Cuando el sector y el horario hacen viable','disponibilidad presencial se revisa','El sector se confirma primero','Antes de reservar, vemos qué frecuencia podemos sostener bien','Primero revisamos tu sector y la frecuencia que de verdad podemos sostener','¿Tu sector hace difícil sostener la presencialidad?','promise an impractical in-person routine','when the area makes it viable','what frequency is viable','viable frequency','In-person availability is reviewed individually','We confirm the area first','We first review your area and the frequency we can truly sustain','Does your area make frequent in-person work difficult?']:
 assert phrase.lower() not in commercial.lower(),phrase

scope_expected={
'entrenador-personal-la-reina/index.html':'/hibrido/','entrenador-personal-las-condes/index.html':'/hibrido/','entrenador-personal-lo-barnechea/index.html':'/hibrido/','entrenador-personal-penalolen/index.html':'/hibrido/','entrenador-personal-vitacura/index.html':'/hibrido/','entrenamiento-personal-providencia/index.html':'/hibrido/','personal-trainer-nunoa/index.html':'/hibrido/',
'en/personal-trainer-la-reina/index.html':'/en/hybrid/','en/personal-trainer-las-condes/index.html':'/en/hybrid/','en/personal-trainer-lo-barnechea/index.html':'/en/hybrid/','en/personal-trainer-nunoa/index.html':'/en/hybrid/','en/personal-trainer-penalolen/index.html':'/en/hybrid/','en/personal-trainer-vitacura/index.html':'/en/hybrid/','en/personal-training-providencia/index.html':'/en/hybrid/'}
found={}
for p in htmls:
 rel=p.relative_to(root).as_posix(); text=p.read_text(encoding='utf-8')
 for m in re.finditer(r'<section class="[^"]*compact-section[^"]*">(.*?)</section>',text,re.I|re.S):
  block=m.group(1)
  if 'scope-note' not in block: continue
  links=re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',block,re.I|re.S); assert len(links)==1,(rel,links)
  found[rel]=(links[0][0],visible(links[0][1]),visible(block))
assert set(found)==set(scope_expected),(set(found)-set(scope_expected),set(scope_expected)-set(found))
for rel,expected_href in scope_expected.items():
 href,label,block=found[rel]; assert href==expected_href,(rel,href,expected_href,block)
 assert ('hybrid' in label.lower()) if rel.startswith('en/') else ('híbrido' in label.lower()),(rel,label)

for p in htmls:
 rel=p.relative_to(root).as_posix(); text=p.read_text(encoding='utf-8')
 for m in re.finditer(r'<a\b[^>]*class="[^"]*text-link[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',text,re.I|re.S):
  href,label=m.group(1),visible(m.group(2)).lower()
  if 'entrenamiento híbrido' in label: assert href=='/hibrido/',(rel,label,href)
  if 'hybrid training' in label: assert href=='/en/hybrid/',(rel,label,href)
  if 'entrenamiento online' in label: assert href=='/online/',(rel,label,href)
  if 'online training' in label: assert href=='/en/online/',(rel,label,href)

css=root.joinpath('assets/contrast.v64321.css').read_text(encoding='utf-8')
for token in ['--text-secondary:#44564c','--gold-text-strong:#806216','--line-gold-strong:rgba(128,98,22,.38)','body:is([data-page="local"],[data-page="local_en"]) .scope-note','background:rgba(255,253,248,.92)','section-cream','min-height:44px']: assert token in css,token
assert '#755916' not in css

def rgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def lum(h):
 vals=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb(h)]; return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
def contrast(a,b):
 x,y=lum(a),lum(b); return (max(x,y)+.05)/(min(x,y)+.05)
for fg,bg in [('#44564c','#eee5d7'),('#44564c','#fffdf8'),('#806216','#eee5d7'),('#806216','#fffdf8'),('#D9B568','#1F3D2B')]:
 ratio=contrast(fg,bg); assert ratio>=4.5,(fg,bg,ratio); print('CONTRAST',fg,bg,round(ratio,2))
assert 'Aligns local flexibility callouts with Hybrid' in root.joinpath('CHANGELOG.md').read_text(encoding='utf-8')
print('STATIC_OK',len(htmls),len(changed),'scope_notes',len(found))
