from pathlib import Path
import re
import subprocess

ROOT = Path('candidate/v628')
BASE = '69c41ce35ca0eba65f4c1b8653f15717bca7037a'

LOCAL = {
    'entrenador-personal-las-condes/index.html': ['La comuna define la cobertura; tu contexto define el plan.', 'No inferimos cómo te mueves, dónde prefieres entrenar ni qué actividades haces por vivir en Las Condes.'],
    'en/personal-trainer-las-condes/index.html': ['The commune defines coverage; your context defines the plan.', 'We do not infer how you move, where you prefer to train or which activities you do from living in Las Condes.'],
    'entrenador-personal-vitacura/index.html': ['La comuna define la cobertura; tu contexto define el plan.', 'No deducimos tus hábitos ni tus preferencias por vivir en Vitacura.'],
    'en/personal-trainer-vitacura/index.html': ['The commune defines coverage; your context defines the plan.', 'We do not infer your habits or preferences from living in Vitacura.'],
    'entrenamiento-personal-providencia/index.html': ['La comuna define la cobertura; tu contexto define el plan.', 'No suponemos que caminas, pedaleas, entrenas fuera o tienes una semana activa por vivir en Providencia.'],
    'en/personal-training-providencia/index.html': ['The commune defines coverage; your context defines the plan.', 'We do not assume you walk, cycle, train outdoors or have an active week because you live in Providencia.'],
    'entrenador-personal-lo-barnechea/index.html': ['La comuna define la cobertura; tu contexto define el plan.', 'No asumimos montaña, bicicleta, trekking ni ninguna otra actividad por vivir en Lo Barnechea.'],
    'en/personal-trainer-lo-barnechea/index.html': ['The commune defines coverage; your context defines the plan.', 'We do not assume mountain activity, cycling, hiking or any other activity from living in Lo Barnechea.'],
    'entrenador-personal-la-reina/index.html': ['La comuna define la cobertura; tu contexto define el plan.', 'Tu forma de entrenar no se deduce de la comuna.'],
    'en/personal-trainer-la-reina/index.html': ['The commune defines coverage; your context defines the plan.', 'Your way of training is not inferred from the commune.'],
    'personal-trainer-nunoa/index.html': ['Tu contexto concreto vale más que cualquier idea sobre la comuna.', 'No inferimos tus hábitos, tus actividades ni tus lugares preferidos por vivir en Ñuñoa.'],
    'en/personal-trainer-nunoa/index.html': ['Your actual context matters more than any idea about the commune.', 'We do not infer your habits, activities or preferred places from living in Ñuñoa.'],
    'entrenador-personal-penalolen/index.html': ['Estar en Peñalolén define la cobertura; tus datos definen el plan.', 'no lo suponemos por vivir en Peñalolén'],
    'en/personal-trainer-penalolen/index.html': ['Being in Peñalolén defines coverage; your information defines the plan.', 'we do not assume it from living in Peñalolén'],
}

TARGET = {
    'entrenador-personal-las-condes/index.html', 'en/personal-trainer-las-condes/index.html',
    'entrenador-personal-vitacura/index.html', 'en/personal-trainer-vitacura/index.html',
    'entrenamiento-personal-providencia/index.html', 'en/personal-training-providencia/index.html',
    'entrenador-personal-lo-barnechea/index.html', 'en/personal-trainer-lo-barnechea/index.html',
}

BANNED_ES = [
    'vida de barrio', 'vida barrial', 'actividad comunitaria', 'precordillera',
    'ciclovía', 'ciclovías', 'infraestructura deportiva', 'entorno verde',
    'movilidad activa', 'escala caminable', 'recursos que ya tienes cerca',
    'formas de moverte por la comuna', 'identidad residencial',
    'parques, cerros, senderos', 'parques y espacios deportivos',
]
BANNED_EN = [
    'neighbourhood life', 'community activity', 'foothills', 'cycle lanes',
    'sports infrastructure', 'green environment', 'active mobility', 'walkable scale',
    'resources already around you', 'ways of moving through the commune',
    'residential identity', 'parks, hills, trails', 'parks and sports spaces',
]

assert (ROOT / 'VERSION').read_text(encoding='utf-8').strip() == '6.43.26'
htmls = sorted(ROOT.rglob('*.html'))
assert len(htmls) == 33, len(htmls)

href_re = re.compile(r'href="([^"]+)"')
canon_re = re.compile(r'<link href="([^"]+)" rel="canonical"\s*/?>')
alt_re = re.compile(r'<link href="([^"]+)" hreflang="([^"]+)" rel="alternate"\s*/?>')

for rel, required in LOCAL.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    low = text.casefold()
    en = rel.startswith('en/')
    for phrase in required:
        assert phrase.casefold() in low, (rel, 'missing', phrase)
    for phrase in (BANNED_EN if en else BANNED_ES):
        assert phrase.casefold() not in low, (rel, 'banned', phrase)
    assert ('Training available' if en else 'Entrenamiento disponible') in text, (rel, 'service badge')
    assert text.count('class="principle-row reveal"') == 3, (rel, 'principles')
    assert text.count('data-aeo-answer') >= 2, (rel, 'answers')
    assert 'wa.me/56944040032' in text, (rel, 'whatsapp')
    expected_date = '2026-10-01' if rel in TARGET else '2026-09-30'
    assert f'"dateModified":"{expected_date}"' in text, (rel, 'dateModified', expected_date)

    before = subprocess.check_output(['git', 'show', f'{BASE}:candidate/v628/{rel}'], text=True)
    before_wa = sorted(h for h in href_re.findall(before) if 'wa.me/56944040032' in h)
    after_wa = sorted(h for h in href_re.findall(text) if 'wa.me/56944040032' in h)
    assert before_wa == after_wa, (rel, 'WHATSAPP_DRIFT')
    assert canon_re.findall(before) == canon_re.findall(text), (rel, 'CANONICAL_DRIFT')
    assert sorted(alt_re.findall(before)) == sorted(alt_re.findall(text)), (rel, 'HREFLANG_DRIFT')

# Previously corrected pages and Home are frozen byte-for-byte in this WIP.
for rel in [
    'index.html', 'en/index.html',
    'entrenador-personal-la-reina/index.html', 'en/personal-trainer-la-reina/index.html',
    'personal-trainer-nunoa/index.html', 'en/personal-trainer-nunoa/index.html',
    'entrenador-personal-penalolen/index.html', 'en/personal-trainer-penalolen/index.html',
]:
    current = (ROOT / rel).read_bytes()
    previous = subprocess.check_output(['git', 'show', f'{BASE}:candidate/v628/{rel}'])
    assert current == previous, (rel, 'FROZEN_PAGE_DRIFT')

# Exact product scope.
expected = {
    'candidate/v628/VERSION', 'candidate/v628/CHANGELOG.md',
    *(f'candidate/v628/{rel}' for rel in TARGET),
}
actual = set(subprocess.check_output(['git', 'diff', '--name-only'], text=True).splitlines())
assert actual == expected, {'missing': sorted(expected - actual), 'extra': sorted(actual - expected)}

print('QA_V64326_LOCAL_EDITORIAL_POLICY_OK', len(LOCAL), len(TARGET), len(htmls))
