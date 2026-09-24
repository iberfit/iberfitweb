from pathlib import Path
from urllib.parse import quote
import json, re

ROOT = Path('candidate/v628')
VERSION = '6.43.19'
AREAS_ES = 'Las Condes, Vitacura, Providencia, Lo Barnechea, Ñuñoa, La Reina y Peñalolén'
AREAS_EN = 'Las Condes, Vitacura, Providencia, Lo Barnechea, Ñuñoa, La Reina and Peñalolén'


def wa(text: str) -> str:
    return 'https://wa.me/56944040032?text=' + quote(text, safe='')


def replace_exact(path: Path, old: str, new: str, *, count=None):
    text = path.read_text(encoding='utf-8')
    n = text.count(old)
    if n == 0:
        raise SystemExit(f'MISSING_REPLACEMENT::{path}::{old[:120]}')
    if count is not None and n != count:
        raise SystemExit(f'COUNT_MISMATCH::{path}::{n}!={count}::{old[:120]}')
    path.write_text(text.replace(old, new), encoding='utf-8')


def replace_regex(path: Path, pattern: str, repl: str, *, count=1):
    text = path.read_text(encoding='utf-8')
    out, n = re.subn(pattern, repl, text, count=count)
    if n != count:
        raise SystemExit(f'REGEX_COUNT::{path}::{n}!={count}::{pattern[:120]}')
    path.write_text(out, encoding='utf-8')


home = ROOT / 'index.html'
pres = ROOT / 'presencial/index.html'
hyb = ROOT / 'hibrido/index.html'
contact = ROOT / 'contacto/index.html'
home_en = ROOT / 'en/index.html'
pres_en = ROOT / 'en/in-person/index.html'
hyb_en = ROOT / 'en/hybrid/index.html'
contact_en = ROOT / 'en/contact/index.html'
online = ROOT / 'online/index.html'
online_en = ROOT / 'en/online/index.html'

# HOME: name the real service footprint instead of suggesting uncertain coverage.
replace_exact(home,
    'Presencial en comunas seleccionadas de Santiago · Híbrido según cobertura · Online desde cualquier lugar.',
    f'Presencial en {AREAS_ES} · Híbrido en estas comunas · Online desde cualquier lugar.')
replace_exact(home_en,
    'In person in selected areas of Santiago · Hybrid where coverage allows · Online worldwide.',
    f'In person in {AREAS_EN} · Hybrid in these areas · Online worldwide.')

# IN-PERSON ES: availability is explicit; logistics are coordinated afterwards.
pres_header_old = 'https://wa.me/56944040032?text=Hola%20IBERFIT%2C%20estoy%20viendo%20el%20entrenamiento%20presencial%20y%20quiero%20empezar%20por%20el%20Diagn%C3%B3stico%20IRI.%20Me%20gustar%C3%ADa%20saber%20c%C3%B3mo%20coordinarlo%20y%20qu%C3%A9%20cobertura%20tienen.'
pres_header_new = wa('Hola IBERFIT, estoy viendo el entrenamiento presencial y quiero empezar por el Diagnóstico IRI. Estoy en una de sus comunas de entrenamiento y me gustaría coordinar el primer paso.')
replace_exact(pres, pres_header_old, pres_header_new, count=2)
replace_exact(pres,
    'https://wa.me/56944040032?text=Hola%20IBERFIT%2C%20estoy%20buscando%20entrenamiento%20personal%20presencial.%20Me%20gustar%C3%ADa%20contarles%20mi%20objetivo%20y%20saber%20qu%C3%A9%20disponibilidad%20y%20cobertura%20tienen.',
    wa('Hola IBERFIT, quiero empezar con entrenamiento personal presencial. Estoy en una de sus comunas de entrenamiento; mi sector es ___, mi disponibilidad suele ser ___ y mi objetivo principal es ___.'))
replace_exact(pres, 'Quiero saber si hay cobertura para mí', 'Quiero empezar presencial')
replace_exact(pres, 'Comunas seleccionadas de Santiago', f'{AREAS_ES}', count=6)
replace_exact(pres, 'La ubicación y el espacio de entrenamiento se confirman antes de comenzar.', 'Coordinamos contigo la ubicación, el espacio y el horario antes de comenzar.')
replace_exact(pres, '<span>Cobertura local</span><strong>Las Condes, Vitacura, Providencia, Lo Barnechea, Ñuñoa, La Reina y Peñalolén</strong>', '<span>Entrenamiento presencial</span><strong>7 comunas de Santiago</strong>')
replace_exact(pres, '<strong>Domicilio</strong><br>Según sector y horario.', '<strong>Domicilio</strong><br>Coordinamos sector y horario contigo.')
replace_exact(pres, '<strong>Gimnasio de edificio</strong><br>Cuando el espacio permite trabajar bien.', '<strong>Gimnasio de edificio</strong><br>Organizamos la sesión según el espacio disponible.')
replace_exact(pres, '<strong>Parque o zona verde</strong><br>Si el entorno y las condiciones son adecuados.', '<strong>Parque o zona verde</strong><br>Elegimos un entorno adecuado para entrenar con calidad.')
replace_exact(pres, 'Dispones de un espacio compatible dentro de la cobertura.', 'Entrenas en una de nuestras comunas presenciales y cuentas con un espacio que podemos organizar contigo.')
replace_exact(pres, '<div class="kicker">Cobertura local</div><h2>Consulta la disponibilidad según comuna.</h2><p class="lead">Cada página explica las condiciones prácticas del servicio presencial. La disponibilidad se confirma siempre de manera individual.</p>', '<div class="kicker">Dónde entrenamos</div><h2>Entrenamos presencialmente en estas comunas.</h2><p class="lead">Selecciona tu comuna para ver cómo organizamos allí el servicio, los espacios habituales y el contacto directo para empezar.</p>')
replace_exact(pres, '<strong>Puede realizarse en un espacio acordado y adecuado, según cobertura.</strong>', f'<strong>Puede realizarse en {AREAS_ES}, en un espacio acordado y adecuado.</strong>')

# HYBRID ES: explicit local footprint; online remains the alternative outside it.
replace_exact(hyb, 'Presencial según zona · Seguimiento a distancia', f'Presencial en {AREAS_ES} · Seguimiento a distancia entre sesiones')
replace_exact(hyb, 'Si no existe cobertura presencial o prefieres trabajar completamente a distancia, la modalidad a distancia mantiene planificación y seguimiento.', f'Si estás fuera de {AREAS_ES} o prefieres trabajar completamente a distancia, la modalidad online mantiene planificación y seguimiento.')

# CONTACT ES: remove availability/coverage as the visitor's first question.
replace_exact(contact, 'Contacta a IBERFIT o utiliza el orientador opcional para consultar modalidad, cobertura y disponibilidad del Diagnóstico IRI.', 'Contacta a IBERFIT o utiliza el orientador opcional para elegir modalidad, coordinar el Diagnóstico IRI y empezar con un siguiente paso claro.', count=4)
replace_exact(contact, 'Presencial según cobertura · Online desde cualquier lugar.', f'Presencial en {AREAS_ES} · Online desde cualquier lugar.')
replace_exact(contact, 'Consulta disponibilidad, cobertura o el Diagnóstico IRI.', 'Cuéntanos tu objetivo, tu comuna y tu disponibilidad; coordinamos contigo el mejor siguiente paso.')

# IN-PERSON EN.
pres_en_header_old = 'https://wa.me/56944040032?text=Hi%20IBERFIT%2C%20I%27ve%20been%20looking%20at%20in-person%20training%20and%20I%27d%20like%20to%20start%20with%20the%20IRI%20Assessment.%20Could%20you%20tell%20me%20how%20to%20arrange%20it%20and%20what%20areas%20you%20cover%3F'
pres_en_header_new = wa("Hi IBERFIT, I've been looking at in-person training and I'd like to start with the IRI Assessment. I'm in one of your in-person training areas and I'd like to arrange the first step.")
replace_exact(pres_en, pres_en_header_old, pres_en_header_new, count=2)
replace_exact(pres_en,
    'https://wa.me/56944040032?text=Hi%20IBERFIT%2C%20I%27m%20looking%20for%20in-person%20personal%20training.%20I%27d%20like%20to%20tell%20you%20my%20goal%20and%20understand%20your%20availability%20and%20coverage.',
    wa("Hi IBERFIT, I'd like to start in-person personal training. I'm in one of your training areas; my neighbourhood is ___, my usual availability is ___ and my main goal is ___."))
replace_exact(pres_en, 'Check whether I am in the coverage area', 'I want to start in person')
replace_exact(pres_en, 'Selected areas of Santiago', AREAS_EN, count=6)
replace_exact(pres_en, 'Training location and available space are confirmed before the service begins.', 'We coordinate the training location, available space and schedule with you before the service begins.')
replace_exact(pres_en, '<span>Local coverage</span><strong>Las Condes, Vitacura, Providencia, Lo Barnechea, Ñuñoa, La Reina and Peñalolén</strong>', '<span>In-person training</span><strong>7 areas of Santiago</strong>')
replace_exact(pres_en, '<strong>Home training</strong><br>Subject to area and schedule.', '<strong>Home training</strong><br>We coordinate the neighbourhood and schedule with you.')
replace_exact(pres_en, '<strong>Condominium gym</strong><br>When the space supports quality training.', '<strong>Condominium gym</strong><br>We organise the session around the available space.')
replace_exact(pres_en, '<strong>Park or green space</strong><br>When the environment and conditions are suitable.', '<strong>Park or green space</strong><br>We choose an environment that supports quality training.')
replace_exact(pres_en, 'You have a compatible training space within the service area.', 'You are based in one of our in-person areas and have a training space we can organise with you.')
replace_exact(pres_en, '<div class="kicker">Local service pages</div><h2>Explore availability by area.</h2><p class="lead">Each page explains the practical coverage considerations for in-person training. Availability is always confirmed individually.</p>', '<div class="kicker">Where we train</div><h2>We provide in-person training in these areas.</h2><p class="lead">Choose your area to see how we organise the service there, typical training environments and the direct route to get started.</p>')
replace_exact(pres_en, '<strong>It can take place in an agreed, appropriate space within the service area.</strong>', f'<strong>It can take place in {AREAS_EN}, in an agreed and appropriate training space.</strong>')

# HYBRID EN.
replace_exact(hyb_en, 'In person by area · Remote review', f'In person in {AREAS_EN} · Remote review between sessions')
replace_exact(hyb_en, 'Where in-person coverage is unavailable, online training maintains planning and ongoing review.', f'If you are outside {AREAS_EN}, or prefer to work fully remotely, online training maintains planning and ongoing review.')

# CONTACT EN.
replace_exact(contact_en, 'Contact IBERFIT or use the optional enquiry guide to discuss training options, availability and the IRI Assessment.', 'Contact IBERFIT or use the optional enquiry guide to choose a training format, arrange the IRI Assessment and start with a clear next step.', count=4)
replace_exact(contact_en, 'In person by service area · Online worldwide.', f'In person in {AREAS_EN} · Online worldwide.')
replace_exact(contact_en, 'Ask about availability, coverage or the IRI Assessment.', 'Tell us your goal, your area and your schedule; we will organise the best next step with you.')

# Online already follows the desired rule: assert that it is available everywhere.
for path, marker in [(online, 'Disponible desde cualquier lugar'), (online_en, 'Available worldwide')]:
    text = path.read_text(encoding='utf-8')
    if marker not in text:
        raise SystemExit(f'ONLINE_CERTAINTY_MISSING::{path}::{marker}')

# Guard against reintroducing operational uncertainty on the commercial journey.
checks = {
    home: ['Híbrido según cobertura'],
    pres: ['qué cobertura tienen', 'Quiero saber si hay cobertura para mí', 'La ubicación y el espacio de entrenamiento se confirman', 'Cobertura local', 'Consulta la disponibilidad según comuna', 'La disponibilidad se confirma siempre de manera individual', 'dentro de la cobertura', 'según cobertura.</strong>'],
    hyb: ['Presencial según zona', 'Si no existe cobertura presencial'],
    contact: ['modalidad, cobertura y disponibilidad', 'Presencial según cobertura', 'Consulta disponibilidad, cobertura'],
    home_en: ['Hybrid where coverage allows'],
    pres_en: ['what areas you cover', 'availability and coverage', 'Check whether I am in the coverage area', 'confirmed before the service begins', 'Local coverage', 'Subject to area and schedule', 'within the service area', 'Explore availability by area', 'Availability is always confirmed individually'],
    hyb_en: ['In person by area', 'Where in-person coverage is unavailable'],
    contact_en: ['training options, availability', 'In person by service area', 'Ask about availability, coverage'],
}
for path, forbidden in checks.items():
    text = path.read_text(encoding='utf-8')
    for phrase in forbidden:
        if phrase.lower() in text.lower():
            raise SystemExit(f'FORBIDDEN_UNCERTAINTY::{path}::{phrase}')

# JSON-LD remains valid after the editorial replacements.
for p in ROOT.rglob('*.html'):
    text = p.read_text(encoding='utf-8')
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, flags=re.S):
        json.loads(raw)

(ROOT / 'VERSION').write_text(VERSION + '\n', encoding='utf-8')
changelog = ROOT / 'CHANGELOG.md'
old = changelog.read_text(encoding='utf-8')
entry = '''## 6.43.19 — Service certainty\n\n- Makes the in-person footprint explicit across Home, In-person, Hybrid and Contact in ES/EN.\n- Reframes location, space and schedule as service coordination rather than uncertainty about whether IBERFIT can deliver.\n- Keeps Online explicitly available from anywhere and preserves the distinction between service availability and personal format fit.\n\n'''
changelog.write_text(entry + old, encoding='utf-8')
print('V64319_BUILD_OK')
