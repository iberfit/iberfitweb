from pathlib import Path
import subprocess,re,json,html

BASE='86f62e1f813e10720769a1a9c46887b6d79097b9'
root=Path('candidate/v628')
assert root.joinpath('VERSION').read_text().strip()=='6.43.22'
htmls=sorted(root.rglob('*.html'))
assert len(htmls)==33,len(htmls)

def extract(pattern,text): return re.findall(pattern,text,re.I|re.S)
def visible(raw):
    raw=re.sub(r'<script\b.*?</script>|<style\b.*?</style>',' ',raw,flags=re.I|re.S)
    raw=re.sub(r'<[^>]+>',' ',raw)
    return re.sub(r'\s+',' ',html.unescape(raw)).strip()

for p in htmls:
    rel=p.as_posix(); new=p.read_text(encoding='utf-8')
    old=subprocess.check_output(['git','show',f'{BASE}:{rel}'],text=True)
    assert new.count('/assets/ux.v64322.css')==1,rel
    assert new.count('/assets/ux.v64322.js')==1,rel
    assert '/assets/analytics.v64322.js' in new,rel
    assert '/assets/analytics.v643.js' not in new,rel
    # SEO, structured data and contextual WhatsApp contracts are not part of this UX change.
    for pattern in [
        r'<link\b[^>]*rel="canonical"[^>]*>',
        r'<link\b[^>]*hreflang="[^"]+"[^>]*>',
        r'href="https://wa\.me/[^"]+"',
        r'<script type="application/ld\+json">(.*?)</script>'
    ]:
        assert extract(pattern,new)==extract(pattern,old),(rel,pattern)
    for raw in extract(r'<script type="application/ld\+json">(.*?)</script>',new): json.loads(raw)

# Home decision architecture: IRI / guidance entry routes, then all three formats.
for rel in ['index.html','en/index.html']:
    text=root.joinpath(rel).read_text(encoding='utf-8')
    router=re.search(r'<nav class="intent-router intent-router--compact reveal".*?</nav>',text,re.S)
    assert router,rel
    assert router.group(0).count('class="intent-route"')==2,rel
    assert 'funnel_compare_formats' not in router.group(0),rel
    assert 'funnel_iri_start' in router.group(0) and 'funnel_guide_start' in router.group(0),rel
    assert text.count('class="modality-row modality-row--guided reveal"')==3,rel

# Online comparison note now states a real decision boundary.
es=root.joinpath('online/index.html').read_text(encoding='utf-8')
en=root.joinpath('en/online/index.html').read_text(encoding='utf-8')
assert 'Si necesitas mucha corrección técnica en directo' in es
assert 'presencial o híbrido puede darte más apoyo' in es
assert 'If you need frequent live technical correction' in en
assert 'in-person or hybrid coaching may give you more support' in en
assert 'No necesitas experiencia avanzada. El nivel de detalle' not in es
assert 'You do not need advanced experience. The level of detail' not in en

# Review system: exactly two reviews stay as evidence, without autoplay controls.
experience=root.joinpath('assets/experience.v64322.js').read_text(encoding='utf-8')
for token in ["slides.length === 2","cards.classList.add('review-pair')","return;","slides.length < 2"]:
    assert token in experience,token
assert 'Subject to area and schedule.' not in experience
assert 'Según sector y horario.' not in experience
assert 'We coordinate area and schedule with you.' in experience
assert 'Coordinamos sector y horario contigo.' in experience

# Consent: all user choices remain available; only first-impression density changes.
analytics=root.joinpath('assets/analytics.v64322.js').read_text(encoding='utf-8')
for token in ['data-consent-all','data-consent-audience','data-consent-necessary','data-consent-settings','data-consent-save']:
    assert token in analytics,token
assert 'Nunca medimos el contenido de mensajes ni datos personales.' in analytics.replace('\\xF3','ó').replace('\\xE9','é').replace('\\xFA','ú') or 'Nunca medimos el contenido de mensajes ni datos personales.' in analytics.encode().decode('unicode_escape',errors='ignore')
assert 'We never measure message content or personal details.' in analytics

css=root.joinpath('assets/ux.v64322.css').read_text(encoding='utf-8')
for token in [
    '.intent-router--compact','.review-pair','.consent-banner','.mobile-swipe-hint',
    'grid-auto-columns:minmax(92%,1fr)','min-height:44px','body[data-page="home"] .section',
    '.site-footer .footer-links','body:has(.consent-banner) .device-dock'
]: assert token in css,token
js=root.joinpath('assets/ux.v64322.js').read_text(encoding='utf-8')
for token in ['Swipe to see more','Desliza para ver más','.app-story-stage','.review-pair']:
    assert token in js,token

# V6.43.21 contrast and semantic guarantees remain intact.
contrast=root.joinpath('assets/contrast.v64321.css').read_text(encoding='utf-8')
for token in ['--text-secondary:#44564c','--gold-text-strong:#806216','--line-gold-strong:rgba(128,98,22,.38)','background:rgba(255,253,248,.92)','min-height:44px']:
    assert token in contrast,token
assert '#755916' not in contrast
commercial='\n'.join(visible(p.read_text(encoding='utf-8')) for p in htmls)
for phrase in ['Primero vemos si podemos hacerlo bien, no solo si podemos ir','Según cobertura presencial','Where in-person coverage allows','In-person availability is reviewed individually','We confirm the area first']:
    assert phrase.lower() not in commercial.lower(),phrase

changed=set(subprocess.check_output(['git','diff','--name-only',BASE,'--','candidate/v628'],text=True).splitlines())
expected={'candidate/v628/VERSION','candidate/v628/CHANGELOG.md','candidate/v628/assets/ux.v64322.css','candidate/v628/assets/ux.v64322.js','candidate/v628/assets/analytics.v64322.js','candidate/v628/assets/experience.v64322.js'}|{p.as_posix() for p in htmls}
assert changed==expected,(changed-expected,expected-changed)
subprocess.check_call(['git','diff','--exit-code',BASE,'--','candidate/v628/_headers'])
print('STATIC_V64322_OK',len(htmls),len(changed))
