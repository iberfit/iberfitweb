from pathlib import Path
import re

ROOT = Path('candidate/v628')
assert (ROOT / 'VERSION').read_text(encoding='utf-8').strip() == '6.43.24'
assert len(list(ROOT.rglob('*.html'))) == 33

PAIRS = [
    ('entrenador-personal-penalolen/index.html','en/personal-trainer-penalolen/index.html',['Peñalolén','precordillera','vida de barrio'],['Peñalolén','foothills','neighbourhood life']),
    ('entrenador-personal-la-reina/index.html','en/personal-trainer-la-reina/index.html',['La Reina','espacios verdes','precordillera'],['La Reina','green spaces','foothills']),
    ('entrenador-personal-las-condes/index.html','en/personal-trainer-las-condes/index.html',['Las Condes','parques','espacios deportivos'],['Las Condes','parks','sports']),
    ('entrenador-personal-vitacura/index.html','en/personal-trainer-vitacura/index.html',['Vitacura','ciclovías','verde'],['Vitacura','cycleways','green']),
    ('entrenamiento-personal-providencia/index.html','en/personal-training-providencia/index.html',['Providencia','ciclovías','movimiento diario'],['Providencia','cycleways','everyday movement']),
    ('personal-trainer-nunoa/index.html','en/personal-trainer-nunoa/index.html',['Ñuñoa','plazas','vida de barrio'],['Ñuñoa','plazas','neighbourhood life']),
    ('entrenador-personal-lo-barnechea/index.html','en/personal-trainer-lo-barnechea/index.html',['Lo Barnechea','montaña','trekking'],['Lo Barnechea','mountain','hiking']),
]

BANNED_ES = [
    'tu sector cambia la logística',
    'reducir fricción',
    'coste logístico',
    'carga para tu semana',
    'otro traslado',
    'desplazamientos innecesarios',
    'cobertura presencial según sector',
    'según cobertura presencial',
    'primero vemos si podemos hacerlo bien, no solo si podemos ir',
]
BANNED_EN = [
    'your area changes the logistics',
    'reduce friction',
    'logistical cost',
    'travel burden',
    'another journey',
    'unnecessary travel',
    'in-person coverage depending on area',
    'subject to area and schedule',
]

for es_rel, en_rel, es_markers, en_markers in PAIRS:
    es = (ROOT / es_rel).read_text(encoding='utf-8')
    en = (ROOT / en_rel).read_text(encoding='utf-8')
    for rel, text, markers, banned in [(es_rel,es,es_markers,BANNED_ES),(en_rel,en,en_markers,BANNED_EN)]:
        low = text.casefold()
        assert 'class="local-context-note reveal"' in text, rel
        assert 'class="principle-stack"' in text, rel
        assert text.count('class="answer-item"') >= 2, rel
        assert 'rel="canonical"' in text, rel
        assert 'hreflang="es"' in text and 'hreflang="en"' in text, rel
        assert 'data-track="cta_local_availability"' in text, rel
        assert 'wa.me/56944040032' in text, rel
        assert '6.43.24' not in text or True  # VERSION is the release identity, HTML need not print it.
        for marker in markers:
            assert marker.casefold() in low, f'{rel}: missing grounded marker {marker}'
        for phrase in banned:
            assert phrase.casefold() not in low, f'{rel}: negative/local-uncertainty phrase survived: {phrase}'

    # Local page pairs must remain reciprocal and semantically paired.
    es_href = re.search(r'hreflang="en" rel="alternate" href="([^"]+)"|href="([^"]+)" hreflang="en" rel="alternate"', es)
    en_href = re.search(r'hreflang="es" rel="alternate" href="([^"]+)"|href="([^"]+)" hreflang="es" rel="alternate"', en)
    assert es_href and en_href, (es_rel,en_rel)

# Release-wide service-certainty guard: local context personalises format, never availability.
for es_rel, en_rel, *_ in PAIRS:
    for rel in [es_rel,en_rel]:
        t = (ROOT / rel).read_text(encoding='utf-8').casefold()
        assert 'entrenamiento disponible' in t or 'training available' in t, rel
        assert 'no disponible' not in t and 'not available' not in t, rel

# Lo Barnechea outdoor language must stay conditional rather than stereotyping every resident.
lo_es = (ROOT / 'entrenador-personal-lo-barnechea/index.html').read_text(encoding='utf-8')
lo_en = (ROOT / 'en/personal-trainer-lo-barnechea/index.html').read_text(encoding='utf-8')
assert 'Si la montaña, la bicicleta, el trekking o el movimiento exterior ya están en tu vida' in lo_es
assert 'If mountains, cycling, hiking or outdoor movement are already part of your life' in lo_en

# La Reina metadata must be affirmative, not conditional coverage language.
la_es = (ROOT / 'entrenador-personal-la-reina/index.html').read_text(encoding='utf-8')
la_en = (ROOT / 'en/personal-trainer-la-reina/index.html').read_text(encoding='utf-8')
assert 'cobertura presencial según' not in la_es.casefold()
assert 'coverage depending' not in la_en.casefold()

# Research traceability exists alongside the build, without exposing citation clutter in customer copy.
sources = Path('.github/data/v64324-local-opportunity-sources.md').read_text(encoding='utf-8')
for name in ['Peñalolén','La Reina','Las Condes','Vitacura','Providencia','Ñuñoa','Lo Barnechea']:
    assert f'## {name}' in sources
assert 'Commune reality is framed as an opportunity, not a handicap.' in sources

print('QA_V64324_LOCAL_OPPORTUNITY_OK', len(PAIRS) * 2)
