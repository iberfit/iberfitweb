from pathlib import Path
import re
import subprocess

ROOT = Path('candidate/v628')
BASE = '668c2678dd63a048878abb623699381d70c0763e'

pairs = {
    'entrenador-personal-la-reina/index.html': {
        'required': [
            'La comuna define la cobertura; tu contexto define el plan.',
            'Tu forma de entrenar no se deduce de la comuna.',
            'Entrenamiento disponible',
            'Sí. IBERFIT ofrece entrenamiento personal presencial en La Reina.',
        ],
        'banned': ['vida cotidiana de barrio', 'escala residencial', 'espacios verdes', 'precordillera'],
    },
    'en/personal-trainer-la-reina/index.html': {
        'required': [
            'The commune defines coverage; your context defines the plan.',
            'Your way of training is not inferred from the commune.',
            'Training available',
            'Yes. IBERFIT provides in-person personal training in La Reina.',
        ],
        'banned': ['everyday neighbourhood life', 'residential scale', 'green spaces', 'foothills'],
    },
    'personal-trainer-nunoa/index.html': {
        'required': [
            'Tu contexto concreto vale más que cualquier idea sobre la comuna.',
            'No inferimos tus hábitos, tus actividades ni tus lugares preferidos por vivir en Ñuñoa.',
            'Entrenamiento disponible',
            'Sí. IBERFIT ofrece entrenamiento personal presencial en Ñuñoa',
        ],
        'banned': ['vida de barrio', 'vida barrial', 'actividad comunitaria', 'lugares que disfrutas', 'rutina reconocible'],
    },
    'en/personal-trainer-nunoa/index.html': {
        'required': [
            'Your actual context matters more than any idea about the commune.',
            'We do not infer your habits, activities or preferred places from living in Ñuñoa.',
            'Training available',
            'Yes. IBERFIT provides in-person personal training in Ñuñoa',
        ],
        'banned': ['neighbourhood life', 'community activity', 'favourite places', 'routine you recognise'],
    },
    'entrenador-personal-penalolen/index.html': {
        'required': [
            'Estar en Peñalolén define la cobertura; tus datos definen el plan.',
            'no lo suponemos por vivir en Peñalolén',
            'Entrenamiento disponible',
            'Sí. IBERFIT ofrece entrenamiento personal presencial en Peñalolén.',
        ],
        'banned': ['vida de barrio', 'precordillera', 'cómo vives Peñalolén'],
    },
    'en/personal-trainer-penalolen/index.html': {
        'required': [
            'Being in Peñalolén defines coverage; your information defines the plan.',
            'we do not assume it from living in Peñalolén',
            'Training available',
            'Yes. IBERFIT provides in-person personal training in Peñalolén.',
        ],
        'banned': ['neighbourhood life', 'foothills', 'how you live in Peñalolén'],
    },
}

assert (ROOT / 'VERSION').read_text(encoding='utf-8').strip() == '6.43.25'
htmls = sorted(ROOT.rglob('*.html'))
assert len(htmls) == 33, len(htmls)

href_re = re.compile(r'href="([^"]+)"')


def selected_contracts(text: str):
    hrefs = href_re.findall(text)
    return {
        'wa': sorted(h for h in hrefs if 'wa.me/56944040032' in h),
        'canonical': sorted(h for h in hrefs if h.startswith('https://iberfit.cl/') and ('/en/' in h or 'iberfit.cl/' in h)),
    }

for rel, contract in pairs.items():
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    low = text.casefold()
    for phrase in contract['required']:
        assert phrase.casefold() in low, (rel, 'missing', phrase)
    for phrase in contract['banned']:
        assert phrase.casefold() not in low, (rel, 'banned', phrase)
    assert '"dateModified":"2026-09-30"' in text, (rel, 'dateModified')
    assert text.count('class="principle-row reveal"') == 3, (rel, 'principles')
    assert text.count('data-aeo-answer') >= 2, (rel, 'answers')
    assert 'wa.me/56944040032' in text, (rel, 'whatsapp')

    before = subprocess.check_output(['git', 'show', f'{BASE}:candidate/v628/{rel}'], text=True)
    before_wa = sorted(h for h in href_re.findall(before) if 'wa.me/56944040032' in h)
    after_wa = sorted(h for h in href_re.findall(text) if 'wa.me/56944040032' in h)
    assert before_wa == after_wa, (rel, 'WHATSAPP_DRIFT')

    def tags(s, relname):
        canon = re.findall(r'<link href="([^"]+)" rel="canonical"\s*/?>', s)
        alts = sorted(re.findall(r'<link href="([^"]+)" hreflang="([^"]+)" rel="alternate"\s*/?>', s))
        assert len(canon) == 1, (relname, 'canonical_count', canon)
        return canon, alts

    assert tags(before, rel) == tags(text, rel), (rel, 'SEO_LINK_DRIFT')

# Unrelated local pages are intentionally frozen in this WIP.
for rel in [
    'entrenador-personal-las-condes/index.html', 'en/personal-trainer-las-condes/index.html',
    'entrenador-personal-vitacura/index.html', 'en/personal-trainer-vitacura/index.html',
    'entrenamiento-personal-providencia/index.html', 'en/personal-training-providencia/index.html',
    'entrenador-personal-lo-barnechea/index.html', 'en/personal-trainer-lo-barnechea/index.html',
]:
    current = (ROOT / rel).read_bytes()
    previous = subprocess.check_output(['git', 'show', f'{BASE}:candidate/v628/{rel}'])
    assert current == previous, (rel, 'UNRELATED_LOCAL_DRIFT')

# Systemic negative guards: these exact patterns must not survive in the six corrected pages.
combined = '\n'.join((ROOT / rel).read_text(encoding='utf-8') for rel in pairs)
for phrase in [
    'tu entrenamiento puede sentirse igual de cercano',
    'conectado con una vida cotidiana de barrio',
    'aprovechando todo lo que tu entorno ya ofrece',
    'your training can feel just as close to home',
    'connected to everyday neighbourhood life',
    'making the most of what your surroundings already offer',
]:
    assert phrase.casefold() not in combined.casefold(), phrase

print('QA_V64325_PERSON_FIRST_LOCAL_OK', len(pairs), len(htmls))
