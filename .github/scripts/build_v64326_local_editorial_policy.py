from pathlib import Path
import re

ROOT = Path('candidate/v628')
VERSION_FROM = '6.43.25'
VERSION_TO = '6.43.26'
DATE_TO = '2026-10-01'


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding='utf-8')


def sub_first(text: str, pattern: str, replacement: str, label: str) -> str:
    out, n = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 replacement, found {n}')
    return out


def sub_nth(text: str, pattern: str, replacement: str, index: int, label: str) -> str:
    matches = list(re.finditer(pattern, text, flags=re.S))
    if len(matches) <= index:
        raise SystemExit(f'{label}: expected occurrence {index + 1}, found {len(matches)}')
    m = matches[index]
    return text[:m.start()] + replacement + text[m.end():]


def update_description(text: str, new_desc: str, rel: str) -> str:
    m = re.search(r'<meta content="([^"]+)" name="description"/>', text)
    if not m:
        raise SystemExit(f'{rel}: description meta not found')
    old = m.group(1)
    count = text.count(old)
    if count not in (4, 5):
        raise SystemExit(f'{rel}: expected description repeated 4 or 5 times, found {count}')
    return text.replace(old, new_desc)


def block_head(kicker: str, h2: str, lead: str) -> str:
    return f'<div class="section-head reveal"><div class="kicker">{kicker}</div><h2>{h2}</h2><p class="lead">{lead}</p></div>'


def context_note(title: str, body: str) -> str:
    return f'<div class="local-context-note reveal"><strong>{title}</strong><p>{body}</p></div>'


def principles(rows):
    items = ''.join(
        f'<article class="principle-row reveal"><h3>{title}</h3><p>{body}</p></article>'
        for title, body in rows
    )
    return f'<div class="principle-stack">{items}</div>'


COMMON_ES_ROWS = [
    ('Tu espacio real', 'Casa, gimnasio de edificio u otro espacio adecuado se valoran por equipamiento, privacidad, seguridad y ajuste al objetivo.'),
    ('Tu actividad real', 'Si ya haces deporte, caminas, corres, pedaleas u otra actividad, la incorporamos porque forma parte de tu semana y puede cambiar carga, recuperación o prioridades.'),
    ('El apoyo que necesitas', 'Presencial, híbrido u online ajustan el nivel de supervisión sin cambiar la dirección del plan.'),
]

COMMON_EN_ROWS = [
    ('Your actual space', 'Home, a building gym or another suitable space are assessed by equipment, privacy, safety and fit with the goal.'),
    ('Your actual activity', 'If you already play sport, walk, run, cycle or do another activity, we include it because it is part of your week and can change workload, recovery or priorities.'),
    ('The support you need', 'In-person, hybrid or online training adjust the level of supervision without changing the direction of the plan.'),
]

PAGES = {
    'entrenador-personal-las-condes/index.html': {
        'desc': 'Entrenamiento personal en Las Condes con diagnóstico, planificación y seguimiento; coordinamos sector, espacio, horario, frecuencia y modalidad según tu contexto.',
        'hero': (
            'Entrenamiento personal en Las Condes, organizado alrededor de tu objetivo y tu semana.',
            'Coordinamos sector, espacio, horario y frecuencia para elegir una modalidad que puedas sostener y una sesión que pueda hacerse bien.',
            'Domicilio, gimnasio de edificio u otro espacio adecuado son opciones si encajan con tu objetivo y con el equipamiento realmente disponible.',
        ),
        'hero_meta': 'Presencial en Las Condes · Sector, espacio y horario coordinados · Híbrido para sumar autonomía · Online desde cualquier lugar.',
        'strip_label': 'Opciones de espacio y acompañamiento para entrenar en Las Condes',
        'chip3': ('Otro espacio adecuado', 'Si tienes acceso a otro lugar útil para entrenar, lo evaluamos por seguridad, equipamiento y ajuste al objetivo.'),
        'head1': ('Lo que cambia la decisión', 'La comuna define la cobertura; tu contexto define el plan.', 'Estar en Las Condes nos dice dónde prestar el servicio; para organizarlo bien necesitamos tu sector, horario, espacio disponible y una frecuencia realista.'),
        'note': ('Datos reales, no supuestos', 'No inferimos cómo te mueves, dónde prefieres entrenar ni qué actividades haces por vivir en Las Condes. Solo usamos información que tú nos das y que cambia una decisión del plan.'),
        'head2': ('La persona primero', 'El plan se construye contigo, no alrededor de un perfil de Las Condes.', 'La mejor combinación responde a tu objetivo, tu agenda, el espacio que realmente tienes y el apoyo que necesitas.'),
        'rows': COMMON_ES_ROWS,
    },
    'en/personal-trainer-las-condes/index.html': {
        'desc': 'Personal training in Las Condes with assessment, planning and follow-up; we coordinate area, training space, schedule, frequency and format around your actual context.',
        'hero': (
            'Personal training in Las Condes, organised around your goal and your week.',
            'We coordinate area, training space, schedule and frequency to choose a format you can sustain and a session that can be delivered well.',
            'Home, a building gym or another suitable space are options when they fit your goal and the equipment actually available.',
        ),
        'hero_meta': 'In-person in Las Condes · Area, space and schedule coordinated · Hybrid for more autonomy · Online from anywhere.',
        'strip_label': 'Training space and support options in Las Condes',
        'chip3': ('Another suitable space', 'If you have access to another useful place to train, we assess it for safety, equipment and fit with the goal.'),
        'head1': ('What changes the decision', 'The commune defines coverage; your context defines the plan.', 'Being in Las Condes tells us where to provide the service; to organise it well we need your area, schedule, available space and a realistic frequency.'),
        'note': ('Real information, not assumptions', 'We do not infer how you move, where you prefer to train or which activities you do from living in Las Condes. We only use information you give us when it changes a training decision.'),
        'head2': ('Person first', 'The plan is built with you, not around a Las Condes profile.', 'The best combination responds to your goal, schedule, the space you actually have and the support you need.'),
        'rows': COMMON_EN_ROWS,
    },
    'entrenador-personal-vitacura/index.html': {
        'desc': 'Entrenamiento personal en Vitacura con diagnóstico, planificación y seguimiento; coordinamos sector, espacio, equipamiento, horario y modalidad según tu contexto.',
        'hero': (
            'Entrenamiento personal en Vitacura, coordinado con tu espacio, tu horario y tu objetivo.',
            'Partimos de tu sector, la disponibilidad que tienes y el espacio real donde podrías entrenar para elegir una modalidad sostenible.',
            'Domicilio, gimnasio de edificio u otro espacio adecuado pueden funcionar cuando permiten entrenar con calidad y progresión.',
        ),
        'hero_meta': 'Presencial en Vitacura · Sector, espacio y horario coordinados · Híbrido para sumar autonomía · Online desde cualquier lugar.',
        'strip_label': 'Opciones de espacio y acompañamiento para entrenar en Vitacura',
        'chip3': ('Otro espacio adecuado', 'Si tienes acceso a otro lugar útil para entrenar, lo evaluamos por seguridad, equipamiento y ajuste al objetivo.'),
        'head1': ('Decisiones concretas', 'La comuna define la cobertura; tu contexto define el plan.', 'Vitacura es una zona de servicio presencial. Para diseñar bien la experiencia necesitamos conocer tu sector, el espacio disponible, el equipamiento real y los horarios que puedes sostener.'),
        'note': ('Sin perfiles por comuna', 'No deducimos tus hábitos ni tus preferencias por vivir en Vitacura. Si una actividad o un espacio forman parte de tu vida, entran en el plan porque tú nos lo cuentas y porque cambian una decisión.'),
        'head2': ('La persona primero', 'Tu forma de entrenar se decide contigo, no a partir de una idea sobre Vitacura.', 'Objetivo, experiencia, agenda, espacio y necesidad de supervisión son los datos que dan forma al plan.'),
        'rows': COMMON_ES_ROWS,
    },
    'en/personal-trainer-vitacura/index.html': {
        'desc': 'Personal training in Vitacura with assessment, planning and follow-up; we coordinate area, space, equipment, schedule and format around your actual context.',
        'hero': (
            'Personal training in Vitacura, coordinated around your space, schedule and goal.',
            'We start from your area, availability and the actual space where you could train to choose a format you can sustain.',
            'Home, a building gym or another suitable space can work when they allow high-quality, progressive training.',
        ),
        'hero_meta': 'In-person in Vitacura · Area, space and schedule coordinated · Hybrid for more autonomy · Online from anywhere.',
        'strip_label': 'Training space and support options in Vitacura',
        'chip3': ('Another suitable space', 'If you have access to another useful place to train, we assess it for safety, equipment and fit with the goal.'),
        'head1': ('Concrete decisions', 'The commune defines coverage; your context defines the plan.', 'Vitacura is an in-person service area. To design the experience well we need your area, available space, actual equipment and the schedule you can sustain.'),
        'note': ('No commune-based profiles', 'We do not infer your habits or preferences from living in Vitacura. If an activity or space is part of your life, it enters the plan because you tell us and because it changes a decision.'),
        'head2': ('Person first', 'Your way of training is decided with you, not from an idea about Vitacura.', 'Goal, experience, schedule, space and need for supervision are the information that shape the plan.'),
        'rows': COMMON_EN_ROWS,
    },
    'entrenamiento-personal-providencia/index.html': {
        'desc': 'Entrenamiento personal en Providencia con diagnóstico, planificación y seguimiento; coordinamos sector, espacio, horario, frecuencia y modalidad según tu contexto.',
        'hero': (
            'Entrenamiento personal en Providencia, organizado para encajar en tu semana real.',
            'Coordinamos sector, horario, frecuencia y espacio disponible para decidir cómo conviene entrenar y cuánto acompañamiento directo aporta valor.',
            'No damos por hecho cómo es tu rutina: trabajamos con lo que realmente haces, necesitas y puedes sostener.',
        ),
        'hero_meta': 'Presencial en Providencia · Sector, espacio y horario coordinados · Híbrido para sumar autonomía · Online desde cualquier lugar.',
        'strip_label': 'Opciones de espacio y acompañamiento para entrenar en Providencia',
        'chip3': ('Otro espacio adecuado', 'Si tienes acceso a otro lugar útil para entrenar, lo evaluamos por seguridad, equipamiento y ajuste al objetivo.'),
        'head1': ('Tu realidad primero', 'La comuna define la cobertura; tu contexto define el plan.', 'Estar en Providencia define dónde podemos prestar el servicio; tu sector, agenda, espacio, frecuencia y objetivo determinan cómo conviene organizarlo.'),
        'note': ('Lo que cuenta es lo que haces de verdad', 'No suponemos que caminas, pedaleas, entrenas fuera o tienes una semana activa por vivir en Providencia. Si alguna de esas actividades existe, la incorporamos porque tú la realizas y puede cambiar la planificación.'),
        'head2': ('La persona primero', 'El entrenamiento se integra en tu semana real, no en una rutina atribuida a Providencia.', 'La modalidad y la dosis de supervisión se eligen con tus datos, tu experiencia y tus preferencias.'),
        'rows': COMMON_ES_ROWS,
    },
    'en/personal-training-providencia/index.html': {
        'desc': 'Personal training in Providencia with assessment, planning and follow-up; we coordinate area, space, schedule, frequency and format around your actual context.',
        'hero': (
            'Personal training in Providencia, organised to fit your actual week.',
            'We coordinate area, schedule, frequency and available space to decide how training should work and how much direct support adds value.',
            'We do not assume what your routine looks like: we work with what you actually do, need and can sustain.',
        ),
        'hero_meta': 'In-person in Providencia · Area, space and schedule coordinated · Hybrid for more autonomy · Online from anywhere.',
        'strip_label': 'Training space and support options in Providencia',
        'chip3': ('Another suitable space', 'If you have access to another useful place to train, we assess it for safety, equipment and fit with the goal.'),
        'head1': ('Your reality first', 'The commune defines coverage; your context defines the plan.', 'Being in Providencia defines where we can provide the service; your area, schedule, space, frequency and goal determine how it should be organised.'),
        'note': ('What matters is what you actually do', 'We do not assume you walk, cycle, train outdoors or have an active week because you live in Providencia. If any of those activities are real, we include them because you do them and they can change the plan.'),
        'head2': ('Person first', 'Training fits your actual week, not a routine attributed to Providencia.', 'The format and amount of supervision are chosen from your information, experience and preferences.'),
        'rows': COMMON_EN_ROWS,
    },
    'entrenador-personal-lo-barnechea/index.html': {
        'desc': 'Entrenamiento personal en Lo Barnechea con diagnóstico, planificación y seguimiento; coordinamos sector, espacio, horario, frecuencia y modalidad según tu contexto.',
        'hero': (
            'Entrenamiento personal en Lo Barnechea, coordinado desde tu sector, tu espacio y tu disponibilidad.',
            'Partimos de tu ubicación concreta, el lugar donde puedes entrenar y los horarios que puedes sostener para organizar una modalidad que tenga sentido para ti.',
            'Tu objetivo, tu experiencia y las actividades que realmente haces completan la información necesaria para planificar bien.',
        ),
        'hero_meta': 'Presencial en Lo Barnechea · Sector, espacio y horario coordinados · Híbrido para sumar autonomía · Online desde cualquier lugar.',
        'strip_label': 'Opciones de espacio y acompañamiento para entrenar en Lo Barnechea',
        'chip3': ('Otro espacio adecuado', 'Si tienes acceso a otro lugar útil para entrenar, lo evaluamos por seguridad, equipamiento y ajuste al objetivo.'),
        'head1': ('Coordinación precisa', 'La comuna define la cobertura; tu contexto define el plan.', 'En Lo Barnechea, conocer el sector exacto, el espacio disponible, el horario y la frecuencia deseada permite organizar el servicio con precisión desde el principio.'),
        'note': ('Tu actividad la cuentas tú', 'No asumimos montaña, bicicleta, trekking ni ninguna otra actividad por vivir en Lo Barnechea. Si forman parte de tu semana, las integramos porque son datos reales que pueden modificar carga y recuperación.'),
        'head2': ('La persona primero', 'Tu plan responde a tu vida, no a una imagen de Lo Barnechea.', 'El lugar de entrenamiento, la modalidad y el grado de supervisión se eligen según objetivo, agenda, recursos y preferencias reales.'),
        'rows': COMMON_ES_ROWS,
    },
    'en/personal-trainer-lo-barnechea/index.html': {
        'desc': 'Personal training in Lo Barnechea with assessment, planning and follow-up; we coordinate area, space, schedule, frequency and format around your actual context.',
        'hero': (
            'Personal training in Lo Barnechea, coordinated from your area, space and availability.',
            'We start from your exact location, the place where you can train and the schedule you can sustain to organise a format that makes sense for you.',
            'Your goal, experience and the activities you actually do complete the information needed to plan well.',
        ),
        'hero_meta': 'In-person in Lo Barnechea · Area, space and schedule coordinated · Hybrid for more autonomy · Online from anywhere.',
        'strip_label': 'Training space and support options in Lo Barnechea',
        'chip3': ('Another suitable space', 'If you have access to another useful place to train, we assess it for safety, equipment and fit with the goal.'),
        'head1': ('Precise coordination', 'The commune defines coverage; your context defines the plan.', 'In Lo Barnechea, knowing the exact area, available space, schedule and desired frequency lets us organise the service precisely from the start.'),
        'note': ('You tell us what your activity actually is', 'We do not assume mountain activity, cycling, hiking or any other activity from living in Lo Barnechea. If they are part of your week, we include them because they are real information that can change workload and recovery.'),
        'head2': ('Person first', 'Your plan responds to your life, not to an image of Lo Barnechea.', 'Training space, format and level of supervision are chosen from your goal, schedule, actual resources and preferences.'),
        'rows': COMMON_EN_ROWS,
    },
}

HEAD_PATTERN = r'<div class="section-head reveal"><div class="kicker">.*?</div><h2>.*?</h2><p class="lead">.*?</p></div>'
NOTE_PATTERN = r'<div class="local-context-note reveal"><strong>.*?</strong><p>.*?</p></div>'
PRINCIPLES_PATTERN = r'<div class="principle-stack">(?:<article class="principle-row reveal"><h3>.*?</h3><p>.*?</p></article>){3}</div>'

for rel, cfg in PAGES.items():
    text = read(rel)
    text = update_description(text, cfg['desc'], rel)
    h1, lead, support = cfg['hero']
    text = sub_first(
        text,
        r'<h1>.*?</h1><p class="lead">.*?</p><p class="hero-support">.*?</p>',
        f'<h1>{h1}</h1><p class="lead">{lead}</p><p class="hero-support">{support}</p>',
        rel + ':hero',
    )
    text = sub_first(text, r'<p class="hero-meta">.*?</p>', f'<p class="hero-meta">{cfg["hero_meta"]}</p>', rel + ':hero-meta')
    text = sub_first(text, r'(<div class="local-service-strip" aria-label=")[^"]+("\s*>)', rf'\1{cfg["strip_label"]}\2', rel + ':strip-label')
    chip_title, chip_body = cfg['chip3']
    text = sub_first(
        text,
        r'<div class="local-service-chip"><b>03</b><span><strong>.*?</strong><br>.*?</span></div>',
        f'<div class="local-service-chip"><b>03</b><span><strong>{chip_title}</strong><br>{chip_body}</span></div>',
        rel + ':chip3',
    )
    text = sub_nth(text, HEAD_PATTERN, block_head(*cfg['head1']), 0, rel + ':section-head-1')
    text = sub_first(text, NOTE_PATTERN, context_note(*cfg['note']), rel + ':context-note')
    text = sub_nth(text, HEAD_PATTERN, block_head(*cfg['head2']), 1, rel + ':section-head-2')
    text = sub_first(text, PRINCIPLES_PATTERN, principles(cfg['rows']), rel + ':principles')
    old_date = '"dateModified":"2026-09-28"'
    if text.count(old_date) != 1:
        raise SystemExit(f'{rel}: expected one old dateModified, found {text.count(old_date)}')
    text = text.replace(old_date, f'"dateModified":"{DATE_TO}"', 1)
    write(rel, text)

version_path = ROOT / 'VERSION'
if version_path.read_text(encoding='utf-8').strip() != VERSION_FROM:
    raise SystemExit('VERSION baseline mismatch')
version_path.write_text(VERSION_TO + '\n', encoding='utf-8')

changelog_path = ROOT / 'CHANGELOG.md'
changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## 6.43.26 — Local editorial policy\n\n- Applies the person-first local editorial rule to all seven commune landing pages.\n- Removes territorial lifestyle storytelling from Las Condes, Vitacura, Providencia and Lo Barnechea in ES/EN.\n- Preserves local coverage, canonical/hreflang, direct answers, WhatsApp context and operational service variables.\n- Adds a global QA contract so commune → assumed lifestyle copy cannot return.\n\n'''
if '## 6.43.26 — Local editorial policy' in changelog:
    raise SystemExit('CHANGELOG already contains V6.43.26')
changelog_path.write_text(entry + changelog, encoding='utf-8')

print('BUILD_V64326_LOCAL_EDITORIAL_POLICY_OK', len(PAGES))
