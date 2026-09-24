from pathlib import Path
import json,re

ROOT=Path('candidate/v628')
VERSION='6.43.20'
AREAS_ES='Las Condes, Vitacura, Providencia, Lo Barnechea, Ñuñoa, La Reina y Peñalolén'
AREAS_EN='Las Condes, Vitacura, Providencia, Lo Barnechea, Ñuñoa, La Reina and Peñalolén'

def rx(path, old, new, count=1):
    p=ROOT/path
    t=p.read_text(encoding='utf-8')
    n=t.count(old)
    if n!=count: raise SystemExit(f'COUNT::{path}::{n}!={count}::{old[:120]}')
    p.write_text(t.replace(old,new),encoding='utf-8')

# Home: keep service certainty, but speak to the visitor.
rx('index.html',
   f'Presencial en {AREAS_ES} · Híbrido en estas comunas · Online desde cualquier lugar.',
   f'En {AREAS_ES} podemos entrenar contigo en presencial o híbrido · Desde cualquier lugar, online.')
rx('en/index.html',
   f'In person in {AREAS_EN} · Hybrid in these areas · Online worldwide.',
   f'If you are in {AREAS_EN}, we can work with you in person or in a hybrid format · From anywhere, online.')

# In-person: turn a service statement into a direct answer to the client.
rx('presencial/index.html',
   'Entrenamos presencialmente en estas comunas.',
   'Si estás en una de estas comunas, podemos entrenar contigo en presencial.')
rx('presencial/index.html',
   'Selecciona tu comuna para ver cómo organizamos allí el servicio, los espacios habituales y el contacto directo para empezar.',
   'Elige tu comuna para ver cómo podemos organizar contigo el lugar, el horario y el primer paso.')
rx('en/in-person/index.html',
   'We provide in-person training in these areas.',
   'If you are in one of these areas, we can train with you in person.')
rx('en/in-person/index.html',
   'Choose your area to see how we organise the service there, typical training environments and the direct route to get started.',
   'Choose your area to see how we can organise the location, schedule and first step with you.')

# Hybrid: address the person rather than describing the format.
rx('hibrido/index.html',
   f'Presencial en {AREAS_ES} · Seguimiento a distancia entre sesiones',
   f'Si estás en {AREAS_ES}, combinamos contigo sesiones presenciales y seguimiento a distancia.')
rx('en/hybrid/index.html',
   f'In person in {AREAS_EN} · Remote review between sessions',
   f'If you are in {AREAS_EN}, we can combine in-person sessions with remote support between sessions.')

# Contact: make availability feel like a direct answer, not a catalogue label.
rx('contacto/index.html',
   f'Presencial en {AREAS_ES} · Online desde cualquier lugar.',
   f'Si estás en {AREAS_ES}, podemos verte presencialmente · Desde cualquier lugar, podemos acompañarte online.')
rx('en/contact/index.html',
   f'In person in {AREAS_EN} · Online worldwide.',
   f'If you are in {AREAS_EN}, we can work with you in person · From anywhere, we can support you online.')

# Preserve structural / technical contracts.
for p in ROOT.rglob('*.html'):
    text=p.read_text(encoding='utf-8')
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S): json.loads(raw)

(ROOT/'VERSION').write_text(VERSION+'\n',encoding='utf-8')
ch=ROOT/'CHANGELOG.md'
old=ch.read_text(encoding='utf-8')
entry='''## 6.43.20 — Client voice\n\n- Keeps service availability explicit while rewriting the remaining institutional phrasing to speak directly to the client.\n- Applies the same human-first voice to Home, In-person, Hybrid and Contact in ES/EN.\n- Leaves structure, styling, tracking, technical SEO and service facts unchanged.\n\n'''
ch.write_text(entry+old,encoding='utf-8')
print('V64320_BUILD_OK')
