from pathlib import Path
from urllib.parse import quote, unquote
import re

ROOT = Path('candidate/v628')
PHONE = '56944040032'

PAGES = {
    'entrenador-personal-la-reina/index.html': ('La Reina', 'es'),
    'entrenador-personal-las-condes/index.html': ('Las Condes', 'es'),
    'entrenador-personal-lo-barnechea/index.html': ('Lo Barnechea', 'es'),
    'personal-trainer-nunoa/index.html': ('Ñuñoa', 'es'),
    'entrenador-personal-penalolen/index.html': ('Peñalolén', 'es'),
    'entrenador-personal-vitacura/index.html': ('Vitacura', 'es'),
    'entrenamiento-personal-providencia/index.html': ('Providencia', 'es'),
    'en/personal-trainer-la-reina/index.html': ('La Reina', 'en'),
    'en/personal-trainer-las-condes/index.html': ('Las Condes', 'en'),
    'en/personal-trainer-lo-barnechea/index.html': ('Lo Barnechea', 'en'),
    'en/personal-trainer-nunoa/index.html': ('Ñuñoa', 'en'),
    'en/personal-trainer-penalolen/index.html': ('Peñalolén', 'en'),
    'en/personal-trainer-vitacura/index.html': ('Vitacura', 'en'),
    'en/personal-training-providencia/index.html': ('Providencia', 'en'),
}

WA_RE = re.compile(r'https://wa\.me/56944040032\?text=([^"&]*)')

def replace_whatsapp(src: str, loc: str, lang: str) -> str:
    def repl(m):
        old = unquote(m.group(1))
        iri = ('IRI' in old) or ('Diagnóstico' in old) or ('Assessment' in old)
        if lang == 'es':
            if iri:
                msg = (f'Hola IBERFIT, estoy en {loc} y quiero empezar por el Diagnóstico IRI. '
                       'Mi sector es ___ y mi disponibilidad principal es ___. '
                       'Me gustaría coordinar el primer paso.')
            else:
                msg = (f'Hola IBERFIT, estoy en {loc} y quiero empezar a entrenar con ustedes. '
                       'Mi sector es ___, mi disponibilidad suele ser ___ y mi objetivo principal es ___. '
                       '¿Qué modalidad me recomiendan para empezar?')
        else:
            if iri:
                msg = (f"Hi IBERFIT, I'm in {loc} and I'd like to start with the IRI Assessment. "
                       'My area is ___ and my main availability is ___. '
                       "I'd like to arrange the first step.")
            else:
                msg = (f"Hi IBERFIT, I'm in {loc} and I'd like to start training with you. "
                       'My area is ___, my usual availability is ___ and my main goal is ___. '
                       'Which format would you recommend to get started?')
        return f'https://wa.me/{PHONE}?text=' + quote(msg, safe='')
    return WA_RE.sub(repl, src)


def replace_common(src: str, loc: str, lang: str) -> str:
    if lang == 'es':
        replacements = {
            '<small>Cobertura local</small>': '<small>Entrenamiento disponible</small>',
            'según cobertura': 'con coordinación local',
            'sujeto a cobertura, horario y espacio real de entrenamiento': 'con coordinación de sector, horario y espacio real de entrenamiento',
            'sujeto a sector, espacio disponible y horario': 'coordinado según sector, espacio disponible y horario',
            'La cobertura local se confirma según sector, espacio y horario': f'En {loc}, coordinamos sector, espacio y horario para organizar el entrenamiento presencial',
            'La cobertura local se confirma por sector, espacio disponible y horario': f'En {loc}, coordinamos sector, espacio y horario para organizar el entrenamiento presencial',
            'La cobertura se confirma por sector, espacio disponible y horario': f'En {loc}, coordinamos sector, espacio y horario para organizar el entrenamiento presencial',
            'Antes de confirmar la modalidad revisamos': 'Para organizar la modalidad revisamos',
            'antes de confirmar la modalidad revisamos': 'para organizar la modalidad revisamos',
            'Antes de confirmar se revisa': 'Al organizarlo revisamos',
            'antes de confirmar se revisa': 'al organizarlo revisamos',
            'Presencial según sector y horario': f'Presencial en {loc} · coordinamos sector y horario',
            'Cobertura real': 'Coordinación local',
            'Confirmamos sector y desplazamiento antes de cerrar una frecuencia.': 'Coordinamos sector y desplazamiento para sostener una frecuencia estable.',
            'Cuando sector, acceso y horario hacen viable una frecuencia estable.': 'Coordinamos sector, acceso y horario para mantener una frecuencia estable.',
        }
        for a,b in replacements.items():
            src = src.replace(a,b)
        src = src.replace('>Hablar con IBERFIT</a>', f'>Quiero entrenar en {loc}</a>')
        if loc == 'La Reina':
            src = src.replace('<h1>Primero confirmamos si podemos acompañarte bien en La Reina.</h1>', '<h1>Entrenamiento personal en La Reina, con una forma de trabajo clara desde el principio.</h1>')
            src = src.replace('<p class="lead">Antes de recomendar presencial, revisamos tu sector, tus horarios y el espacio real donde entrenarías.</p>', '<p class="lead">Trabajamos en La Reina y organizamos contigo sector, horarios y espacio para que empezar sea sencillo.</p>')
            src = src.replace('<p class="hero-support">Si la cobertura y la frecuencia tienen sentido, definimos contigo la forma de trabajo. Si no, te proponemos híbrido u online con la misma claridad.</p>', '<p class="hero-support">Domicilio, espacio acordado, híbrido u online: definimos la modalidad que mejor encaja con tu semana y tu forma de entrenar.</p>')
            src = src.replace('aria-label="Qué confirmamos para el entrenamiento en La Reina"', 'aria-label="Cómo organizamos el entrenamiento en La Reina"')
            src = src.replace('<strong>Espacio útil</strong><br>Domicilio, gimnasio de edificio o exterior solo si permiten entrenar con calidad.', '<strong>Espacio útil</strong><br>Adaptamos el trabajo al domicilio, gimnasio de edificio o exterior manteniendo la calidad de la sesión.')
            src = src.replace('<strong>Continuidad</strong><br>Si el presencial no basta, el híbrido conecta supervisión y trabajo guiado.', '<strong>Continuidad</strong><br>El híbrido conecta supervisión y trabajo guiado cuando ayuda a organizar mejor la semana.')
            src = src.replace('<div class="kicker">Antes de recomendar presencial</div><h2>La decisión depende de tres cosas concretas.</h2><p class="lead">No damos por hecha la cobertura solo porque estés en La Reina. Primero comprobamos que podamos prestar el servicio con continuidad y calidad.</p>', '<div class="kicker">Cómo lo organizamos</div><h2>Empezar en La Reina depende de tres decisiones sencillas.</h2><p class="lead">IBERFIT ofrece entrenamiento personal en La Reina. Coordinamos contigo sector, espacio y horario para que el servicio encaje con continuidad en tu semana.</p>')
            src = src.replace('<h3>Cobertura que podamos cumplir</h3><p>Sector, acceso y desplazamiento tienen que permitir una frecuencia realista.</p>', '<h3>Tu sector y acceso</h3><p>Organizamos desplazamiento y horarios para mantener una frecuencia estable.</p>')
            src = src.replace('<h3>Una frecuencia que puedas sostener</h3><p>Si el presencial añade demasiada fricción, el híbrido u online pueden dar más continuidad sin perder seguimiento.</p>', '<h3>Una frecuencia que puedas sostener</h3><p>Presencial, híbrido u online se combinan cuando ayudan a mantener continuidad sin perder seguimiento.</p>')
            src = src.replace('<strong>Sí, IBERFIT contempla entrenamiento presencial en La Reina según sector, espacio disponible y horario.</strong> Al organizarlo revisamos que la frecuencia sea viable y que el entorno permita trabajar con calidad.', '<strong>Sí. IBERFIT ofrece entrenamiento personal presencial en La Reina.</strong> Coordinamos sector, espacio y horario para organizar una frecuencia sostenible y una sesión de calidad.')
        elif loc == 'Vitacura':
            src = src.replace('<h1>Entrenamiento personal en Vitacura, con una modalidad que podamos sostener bien.</h1>', '<h1>Entrenamiento personal en Vitacura, organizado para encajar en tu semana.</h1>')
            src = src.replace('<p class="lead">Antes de confirmar sesiones presenciales revisamos sector, acceso, horario y espacio disponible. La cercanía solo aporta valor si permite mantener una frecuencia realista.</p>', '<p class="lead">Trabajamos en Vitacura y coordinamos contigo sector, acceso, horario y espacio para que el entrenamiento sea fácil de integrar en tu semana.</p>')
            src = src.replace('<p class="hero-support">Podemos trabajar en domicilio o gimnasio de edificio, o combinar presencial y trabajo guiado cuando el formato híbrido reduce fricción.</p>', '<p class="hero-support">Domicilio, gimnasio de edificio o formato híbrido: organizamos la modalidad que mejor acompaña tu objetivo y tu rutina.</p>')
            src = src.replace('Presencial según sector y acceso · Híbrido para combinar supervisión y autonomía · Online desde cualquier lugar.', 'Presencial en Vitacura · Híbrido para combinar supervisión y autonomía · Online desde cualquier lugar.')
            src = src.replace('<strong>Domicilio</strong><br>Si sector, acceso y horario permiten una frecuencia estable.', '<strong>Domicilio</strong><br>Coordinamos sector, acceso y horario para mantener una frecuencia estable.')
            src = src.replace('<strong>Gimnasio de edificio</strong><br>Si el espacio y el equipamiento permiten entrenar con calidad.', '<strong>Gimnasio de edificio</strong><br>Adaptamos la sesión al espacio y al equipamiento disponible manteniendo la calidad del trabajo.')
            src = src.replace('<h2>La cobertura se confirma antes de prometer una frecuencia.</h2><p class="lead">Sector, acceso, horario y espacio disponible determinan si el entrenamiento presencial puede sostenerse con calidad.</p>', '<h2>Entrenamos en Vitacura y organizamos la logística alrededor de tu semana.</h2><p class="lead">Sector, acceso, horario y espacio disponible nos ayudan a definir una frecuencia práctica y una sesión de calidad.</p>')
            src = src.replace('<strong>Qué verificamos contigo</strong><p>Revisamos el acceso al lugar, las condiciones reales del espacio y tu disponibilidad. Si ese encaje no permite continuidad, preferimos proponerte un formato híbrido u online antes que forzar una frecuencia presencial.</p>', '<strong>Qué coordinamos contigo</strong><p>Organizamos el acceso al lugar, las condiciones reales del espacio y tu disponibilidad. Presencial, híbrido u online pueden combinarse para dar continuidad al mismo plan.</p>')
            src = src.replace('<div class="kicker">Antes de recomendar una modalidad</div><h2>Tres cosas tienen que funcionar en la vida real.</h2>', '<div class="kicker">Cómo lo organizamos</div><h2>Tres decisiones hacen que el entrenamiento encaje en la vida real.</h2>')
            src = src.replace('<h3>Coordinación local</h3><p>Confirmamos sector, acceso y horario antes de reservar una frecuencia presencial.</p>', '<h3>Sector y acceso</h3><p>Coordinamos sector, acceso y horario para mantener una frecuencia presencial estable.</p>')
            src = src.replace('<h3>Espacio útil</h3><p>Domicilio o gimnasio de edificio solo tienen sentido si el espacio permite desarrollar la sesión con calidad.</p>', '<h3>Espacio útil</h3><p>Adaptamos la sesión al domicilio o gimnasio de edificio según el espacio y material disponible.</p>')
            src = src.replace('<h3>Frecuencia sostenible</h3><p>Si no conviene que todo sea presencial, el formato híbrido mantiene planificación y seguimiento sin forzar traslados innecesarios.</p>', '<h3>Frecuencia sostenible</h3><p>El formato híbrido permite combinar supervisión presencial y trabajo guiado cuando ayuda a organizar mejor la semana.</p>')
            src = src.replace('<strong>Sí, IBERFIT contempla entrenamiento presencial en Vitacura según sector, espacio disponible y horario.</strong> Al organizarlo revisamos que la frecuencia sea viable y que el entorno permita trabajar con calidad.', '<strong>Sí. IBERFIT ofrece entrenamiento personal presencial en Vitacura.</strong> Coordinamos sector, espacio y horario para organizar una frecuencia sostenible y una sesión de calidad.')
    else:
        replacements = {
            '<small>Local coverage</small>': '<small>Training available</small>',
            'depending on coverage': 'with local coordination',
            'subject to coverage, schedule and real training space': 'with coordination around area, schedule and real training space',
            'subject to area, available training space and schedule': 'coordinated around area, available training space and schedule',
            'subject to area, schedule and a suitable training space': 'with coordination around area, schedule and a suitable training space',
            'Coverage is confirmed by area, available training space and schedule': f'In {loc}, we coordinate area, training space and schedule to organise the in-person service',
            'Local coverage is confirmed by area, training space and schedule': f'In {loc}, we coordinate area, training space and schedule to organise the in-person service',
            'Coverage is confirmed only when the frequency and environment are workable.': 'We coordinate frequency and training environment so the service stays practical and high-quality.',
            'Before confirming the format, we review': 'To organise the format, we review',
            'before confirming the format, we review': 'to organise the format, we review',
            'Before confirming, we review': 'When organising it, we review',
            'before confirming, we review': 'when organising it, we review',
            'In person by area and schedule': f'In-person in {loc} · area and schedule coordinated',
            'Real coverage': 'Local coordination',
            'We confirm area and travel before setting a frequency.': 'We coordinate area and travel to sustain a stable frequency.',
        }
        for a,b in replacements.items():
            src = src.replace(a,b)
        src = src.replace('>Talk to IBERFIT</a>', f'>I want to train in {loc}</a>')
        if loc == 'La Reina':
            src = src.replace('<h1>First we confirm whether we can support you well in La Reina.</h1>', '<h1>Personal training in La Reina, with a clear way to get started.</h1>')
            src = src.replace('<p class="lead">Before recommending in-person training, we check your area, your schedule and the real space where you would train.</p>', '<p class="lead">We work in La Reina and organise area, schedule and training space with you so getting started is straightforward.</p>')
            src = src.replace('<p class="hero-support">If coverage and frequency make sense, we define the format with you. If not, we will recommend hybrid or online support just as clearly.</p>', '<p class="hero-support">Home, an agreed space, hybrid or online: we define the format that best fits your week and the way you train.</p>')
            src = src.replace('aria-label="What we confirm for personal training in La Reina"', 'aria-label="How we organise training in La Reina"')
            src = src.replace('<strong>Usable space</strong><br>Home, condominium gym or outdoors only when the setting supports good training.', '<strong>Usable space</strong><br>We adapt the session to home, a condominium gym or outdoors while protecting training quality.')
            src = src.replace('<strong>Continuity</strong><br>If in-person alone is not enough, hybrid connects supervision and guided work.', '<strong>Continuity</strong><br>Hybrid connects direct supervision and guided work when it helps organise the week better.')
            src = src.replace('<div class="kicker">Before recommending in-person training</div><h2>The decision depends on three concrete things.</h2><p class="lead">We do not assume coverage simply because you are in La Reina. We first check that the service can be delivered with continuity and quality.</p>', '<div class="kicker">How we organise it</div><h2>Getting started in La Reina comes down to three simple decisions.</h2><p class="lead">IBERFIT provides personal training in La Reina. We coordinate area, space and schedule with you so the service fits your week with continuity.</p>')
            src = src.replace('<h3>Coverage we can actually deliver</h3><p>Area, access and travel need to support a realistic training frequency.</p>', '<h3>Your area and access</h3><p>We organise travel and schedules to maintain a stable training frequency.</p>')
            src = src.replace('<h3>A frequency you can sustain</h3><p>If in-person adds too much friction, hybrid or online support may provide better continuity without losing follow-up.</p>', '<h3>A frequency you can sustain</h3><p>In-person, hybrid and online can be combined when that helps maintain continuity without losing follow-up.</p>')
            src = src.replace('<strong>Yes. IBERFIT provides in-person personal training in La Reina coordinated around area, available training space and schedule.</strong> We coordinate frequency and training environment so the service stays practical and high-quality.', '<strong>Yes. IBERFIT provides in-person personal training in La Reina.</strong> We coordinate area, space and schedule to organise a sustainable frequency and a high-quality session.')
        elif loc == 'Vitacura':
            src = src.replace('<h1>Personal training in Vitacura, with a format we can realistically sustain.</h1>', '<h1>Personal training in Vitacura, organised to fit your week.</h1>')
            src = src.replace('<p class="lead">Before confirming in-person sessions, we review area, access, schedule and available training space. Proximity only adds value when it supports a realistic frequency.</p>', '<p class="lead">We work in Vitacura and coordinate area, access, schedule and training space with you so training fits naturally into your week.</p>')
            src = src.replace('<p class="hero-support">We can train at home or in a residential gym, or combine in-person and guided work when a hybrid format reduces friction.</p>', '<p class="hero-support">Home, a residential gym or hybrid coaching: we organise the format that best supports your goal and routine.</p>')
            src = src.replace('In-person according to area and access · Hybrid for supervision plus autonomy · Online from anywhere.', 'In-person in Vitacura · Hybrid for supervision plus autonomy · Online from anywhere.')
            src = src.replace('<strong>Home training</strong><br>When area, access and schedule support a stable frequency.', '<strong>Home training</strong><br>We coordinate area, access and schedule to maintain a stable frequency.')
            src = src.replace('<strong>Residential gym</strong><br>When the space and equipment allow the session to be delivered well.', '<strong>Residential gym</strong><br>We adapt the session to the available space and equipment while protecting training quality.')
            src = src.replace('<h2>Coverage is confirmed before we promise a frequency.</h2><p class="lead">Area, access, schedule and available training space determine whether in-person training can be sustained well.</p>', '<h2>We train in Vitacura and organise the logistics around your week.</h2><p class="lead">Area, access, schedule and available training space help us define a practical frequency and a high-quality session.</p>')
            src = src.replace('<strong>What we confirm with you</strong><p>We review access, the actual training space and your availability. If that combination does not support continuity, we would rather recommend hybrid or online training than force an in-person frequency.</p>', '<strong>What we coordinate with you</strong><p>We organise access, the real training space and your availability. In-person, hybrid and online can be combined to give continuity to the same plan.</p>')
            src = src.replace('<div class="kicker">Before recommending a format</div><h2>Three things have to work in real life.</h2>', '<div class="kicker">How we organise it</div><h2>Three decisions make training fit real life.</h2>')
            src = src.replace('<h3>Local coordination</h3><p>We confirm area, access and schedule before booking an in-person frequency.</p>', '<h3>Area and access</h3><p>We coordinate area, access and schedule to maintain a stable in-person frequency.</p>')
            src = src.replace('<h3>Usable training space</h3><p>Home or residential-gym training only makes sense when the space allows the session to be delivered well.</p>', '<h3>Usable training space</h3><p>We adapt the session to home or a residential gym according to the space and equipment available.</p>')
            src = src.replace('<h3>Sustainable frequency</h3><p>If everything does not need to be in person, hybrid training keeps planning and review connected without forcing unnecessary travel.</p>', '<h3>Sustainable frequency</h3><p>Hybrid coaching combines direct supervision and guided work when that helps organise the week better.</p>')
            src = src.replace('<strong>Yes. IBERFIT provides in-person personal training in Vitacura coordinated around area, available training space and schedule.</strong> We coordinate frequency and training environment so the service stays practical and high-quality.', '<strong>Yes. IBERFIT provides in-person personal training in Vitacura.</strong> We coordinate area, space and schedule to organise a sustainable frequency and a high-quality session.')
    return src

changed = 0
for rel, (loc, lang) in PAGES.items():
    path = ROOT / rel
    src = path.read_text()
    out = replace_common(src, loc, lang)
    out = replace_whatsapp(out, loc, lang)
    if out != src:
        path.write_text(out)
        changed += 1

(ROOT / 'VERSION').write_text('6.43.18\n')
changelog = ROOT / 'CHANGELOG.md'
old = changelog.read_text()
entry = '''\n## 6.43.18 — Confianza local sin fricción\n- Todas las landings locales ES/EN comunican disponibilidad de entrenamiento desde el primer contacto.\n- Sector, espacio y horario se presentan como coordinación operativa, no como duda sobre si IBERFIT puede atender.\n- WhatsApp local parte de “estoy en [comuna] y quiero empezar”, conservando contexto e intención.\n- La Reina y Vitacura eliminan encuadres de “confirmar si podemos” y presentan presencial, híbrido y online como formas de organizar un servicio disponible.\n'''
changelog.write_text(entry + old)

assert changed == 14, changed
print(f'Built V6.43.18 local confidence across {changed} local pages')
