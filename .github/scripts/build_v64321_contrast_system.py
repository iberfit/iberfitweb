from pathlib import Path

ROOT = Path('candidate/v628')
VERSION = ROOT / 'VERSION'
CHANGELOG = ROOT / 'CHANGELOG.md'
CSS_LINK = '<link href="/assets/contrast.v64321.css" rel="stylesheet"/>'

assert VERSION.read_text(encoding='utf-8').strip() == '6.43.20'
htmls = sorted(ROOT.rglob('*.html'))
assert len(htmls) == 33, len(htmls)

def replace_exact(path: Path, old: str, new: str):
    text = path.read_text(encoding='utf-8')
    assert text.count(old) == 1, (path, old, text.count(old))
    path.write_text(text.replace(old, new), encoding='utf-8')

def apply(path: Path, replacements):
    for old, new in replacements:
        replace_exact(path, old, new)

# Home: hybrid availability is stated, not framed as conditional coverage.
apply(ROOT / 'index.html', [
    ('<span>Según cobertura presencial</span><h3>Híbrida</h3>', '<span>En estas comunas + seguimiento a distancia</span><h3>Híbrida</h3>'),
])
apply(ROOT / 'en/index.html', [
    ('<span>Where in-person coverage allows</span><h3>Hybrid</h3>', '<span>In these areas + remote support</span><h3>Hybrid</h3>'),
])

# Las Condes: remove the final remaining "can we do it?" framing.
apply(ROOT / 'entrenador-personal-las-condes/index.html', [
    ('<div class="kicker">Antes de reservar</div><h2>Primero vemos si podemos hacerlo bien, no solo si podemos ir.</h2><p class="lead">Cuéntanos tu sector, horarios y dónde podrías entrenar. Si la frecuencia presencial no es la mejor opción, te lo diremos y buscaremos una alternativa más sostenible.</p>', '<div class="kicker">Antes de empezar</div><h2>Organizamos contigo una forma de entrenar que encaje en tu semana.</h2><p class="lead">Cuéntanos tu sector, tus horarios y dónde prefieres entrenar. Con eso coordinamos contigo una combinación presencial, híbrida u online que puedas sostener.</p>'),
    ('<strong>Sí, IBERFIT contempla entrenamiento presencial en Las Condes según sector, espacio disponible y horario.</strong> Al organizarlo revisamos que la frecuencia sea viable y que el entorno permita trabajar con calidad.', '<strong>Sí. IBERFIT ofrece entrenamiento personal presencial en Las Condes.</strong> Coordinamos contigo sector, espacio y horario para organizar una frecuencia sostenible y una sesión de calidad.'),
    ('>Ver qué opción encaja</a>', '>Quiero empezar en Las Condes</a>'),
])
apply(ROOT / 'en/personal-trainer-las-condes/index.html', [
    ('<div class="kicker">Before booking</div><h2>We first check whether we can deliver the service well, not only whether we can travel there.</h2><p class="lead">Share your area, schedule and available training space. If a high in-person frequency is not the best fit, we will say so and suggest a more sustainable option.</p>', '<div class="kicker">Before you start</div><h2>We organise training around the week you actually have.</h2><p class="lead">Tell us your area, schedule and preferred training space. From there, we organise an in-person, hybrid or online combination you can realistically sustain.</p>'),
    ('>See what fits</a>', '>I want to start in Las Condes</a>'),
])

# Lo Barnechea: retain logistics as useful context, but make service certainty explicit.
apply(ROOT / 'entrenador-personal-lo-barnechea/index.html', [
    ('<h1>En Lo Barnechea, la logística también forma parte del plan.</h1>', '<h1>En Lo Barnechea, organizamos el entrenamiento para que encaje de verdad en tu semana.</h1>'),
    ('<p class="lead">Las distancias dentro de Lo Barnechea pueden cambiar mucho la viabilidad de una frecuencia presencial. Preferimos diseñarlo bien desde el principio.</p>', '<p class="lead">Entrenamos contigo en Lo Barnechea. Organizamos sector, horarios y frecuencia para que el plan funcione de verdad en tu semana.</p>'),
    ('<p class="hero-meta">Presencial cuando aporta · Híbrido para reducir desplazamientos · Online desde cualquier lugar.</p>', '<p class="hero-meta">Presencial en Lo Barnechea · Híbrido para sumar flexibilidad · Online desde cualquier lugar.</p>'),
    ('<strong>Domicilio</strong><br>Puede reducir desplazamientos cuando la ubicación lo permite.', '<strong>Domicilio</strong><br>Entrenar en tu domicilio puede simplificar la semana cuando es el formato que mejor te encaja.'),
    ('<strong>Espacio residencial</strong><br>Si el entorno y el equipamiento son adecuados para el objetivo.', '<strong>Espacio residencial</strong><br>Si cuentas con gimnasio de edificio o un espacio útil, adaptamos allí la sesión.'),
    ('<h2>Cuando las distancias importan, la frecuencia tiene que ser inteligente.</h2><p class="lead">Las diferencias de desplazamiento entre sectores de Lo Barnechea pueden cambiar la frecuencia presencial que tiene sentido sostener. El plan debe considerar esa logística desde el principio.</p>', '<h2>La frecuencia se organiza alrededor de tu semana, no al revés.</h2><p class="lead">Coordinamos los encuentros presenciales para que aporten valor y usamos el híbrido cuando te ayuda a mantener continuidad sin reorganizar toda tu agenda.</p>'),
    ('<p>La ubicación cambia cuánto tiempo tiene sentido dedicar a traslados y qué frecuencia podemos sostener bien.</p>', '<p>Tu sector nos ayuda a organizar horarios y desplazamientos sin convertirlos en una carga para tu semana.</p>'),
    ('<div class="kicker">Antes de reservar</div><h2>Antes de reservar, vemos qué frecuencia podemos sostener bien.</h2><p class="lead">Cuéntanos tu sector y horarios. Si una frecuencia presencial alta añade más fricción que valor, te propondremos otra combinación.</p>', '<div class="kicker">Antes de empezar</div><h2>Organizamos contigo una frecuencia que puedas sostener.</h2><p class="lead">Cuéntanos tu sector y tus horarios. A partir de ahí organizamos contigo la combinación presencial, híbrida u online que mejor encaje en tu semana.</p>'),
    ('<span>¿La distancia complica la frecuencia presencial?</span><p>Podemos usar la presencialidad de forma estratégica y mantener el trabajo guiado entre sesiones.</p></div><a class="text-link" href="/online/">Conocer entrenamiento online</a>', '<span>¿Tu semana cambia mucho?</span><p>Podemos combinar presencial, híbrido u online para mantener continuidad sin obligarte a reorganizar toda tu agenda.</p></div><a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>'),
    ('<strong>Sí, IBERFIT contempla entrenamiento presencial en Lo Barnechea según sector, espacio disponible y horario.</strong> Al organizarlo revisamos que la frecuencia sea viable y que el entorno permita trabajar con calidad.', '<strong>Sí. IBERFIT ofrece entrenamiento personal presencial en Lo Barnechea.</strong> Coordinamos contigo sector, espacio y horario para organizar una frecuencia sostenible y una sesión de calidad.'),
    ('<p>Con eso podemos proponerte una frecuencia realista antes de que organices tu semana.</p>', '<p>Con tu sector y disponibilidad podemos organizar contigo una forma de empezar que encaje en tu semana.</p>'),
    ('>Revisar una frecuencia realista</a>', '>Quiero empezar en Lo Barnechea</a>'),
])
apply(ROOT / 'en/personal-trainer-lo-barnechea/index.html', [
    ('<h1>In Lo Barnechea, logistics are part of the training plan.</h1>', '<h1>In Lo Barnechea, we organise training around the week you actually have.</h1>'),
    ('<p class="lead">Travel time can vary substantially across the commune. We would rather design the right frequency from the start than promise an impractical in-person routine.</p>', '<p class="lead">We train with you in Lo Barnechea. We organise area, schedule and frequency so the plan works in your real week.</p>'),
    ('<p class="hero-meta">In person where it adds value · Hybrid to reduce travel · Online from anywhere.</p>', '<p class="hero-meta">In person in Lo Barnechea · Hybrid for added flexibility · Online from anywhere.</p>'),
    ('<strong>Home training</strong><br>Can reduce travel when the area makes it viable.', '<strong>Home training</strong><br>Training at home can simplify your week when that format suits you best.'),
    ('<strong>Residential space</strong><br>When the environment and equipment suit the goal.', '<strong>Residential space</strong><br>If you have a condominium gym or useful training space, we adapt the session there.'),
    ('<h2>When distance matters, frequency has to be intelligent.</h2><p class="lead">Travel conditions can differ substantially between areas of Lo Barnechea and can change the in-person frequency that is realistic to sustain. The plan should account for that logistics from the start.</p>', '<h2>Your training frequency should fit your week, not the other way around.</h2><p class="lead">We organise in-person sessions where they add value and use hybrid support when it helps you stay consistent without reorganising your whole schedule.</p>'),
    ('<p>Location changes how much time travel deserves and what frequency can be sustained.</p>', '<p>Your area helps us organise schedules and travel without turning them into a burden on your week.</p>'),
    ('<div class="kicker">Before booking</div><h2>We first establish what frequency can be delivered well.</h2><p class="lead">Tell us your area and schedules. If a high in-person frequency creates more friction than value, we will recommend a different combination.</p>', '<div class="kicker">Before you start</div><h2>We organise a frequency you can realistically sustain.</h2><p class="lead">Tell us your area and usual schedule. From there, we organise the in-person, hybrid or online combination that best fits your week.</p>'),
    ('<span>Does distance make frequent in-person work difficult?</span><p>We can use direct supervision strategically and keep guided work connected between sessions.</p></div><a class="text-link" href="/en/online/">Explore online training</a>', '<span>Does your week change a lot?</span><p>We can combine in-person, hybrid or online training so you can stay consistent without reorganising your whole schedule.</p></div><a class="text-link" href="/en/hybrid/">Explore hybrid training</a>'),
    ('<strong>Yes. IBERFIT provides in-person personal training in Lo Barnechea coordinated around area, available training space and schedule.</strong> We coordinate frequency and training environment so the service stays practical and high-quality.', '<strong>Yes. IBERFIT provides in-person personal training in Lo Barnechea.</strong> We organise area, training space and schedule with you so the frequency is sustainable and each session can be delivered well.'),
    ('<p>That lets us suggest a realistic frequency before you reorganise your week.</p>', '<p>With your area and availability, we can organise a way to start that fits your week.</p>'),
    ('>Review a realistic frequency</a>', '>I want to start in Lo Barnechea</a>'),
])

# Peñalolén: availability is explicit; area and schedule organise the service rather than gate it.
apply(ROOT / 'entrenador-personal-penalolen/index.html', [
    ('<h1>Peñalolén no se entrena igual en todos sus sectores.</h1>', '<h1>Entrenamiento personal en Peñalolén, organizado alrededor de tu sector y tu semana.</h1>'),
    ('<p class="lead">La comuna cambia mucho entre sectores y también cambia la facilidad para desplazarse. Por eso aquí la ubicación no es un detalle: forma parte de la decisión.</p>', '<p class="lead">Entrenamos contigo en Peñalolén. Coordinamos sector, horarios y espacio para que el entrenamiento encaje de forma clara en tu semana.</p>'),
    ('<p class="hero-support">Primero entendemos dónde estás, qué espacio tienes y qué frecuencia es viable; después decidimos contigo la modalidad.</p>', '<p class="hero-support">Domicilio, espacio residencial, híbrido u online: organizamos contigo la modalidad que mejor acompañe tu objetivo y tu rutina.</p>'),
    ('<p class="hero-meta">La modalidad se decide según sector, frecuencia viable y espacio disponible.</p>', '<p class="hero-meta">Presencial en Peñalolén · Híbrido para sumar flexibilidad · Online desde cualquier lugar.</p>'),
    ('<strong>Domicilio</strong><br>Cuando el sector y el horario hacen viable la atención presencial.', '<strong>Domicilio</strong><br>Coordinamos sector y horario para integrar la sesión en tu semana.'),
    ('<strong>El sector se confirma primero</strong><p>En Peñalolén la disponibilidad presencial se revisa de forma individual porque la logística cambia mucho dentro de la comuna. El objetivo es evitar promesas genéricas y proponerte una frecuencia que realmente podamos sostener bien.</p>', '<strong>Tu sector nos ayuda a organizar la semana</strong><p>Peñalolén tiene sectores con tiempos de desplazamiento distintos. Usamos esa información para coordinar horarios y frecuencia contigo sin convertir la logística en una barrera.</p>'),
    ('<h2>La modalidad se decide sector por sector, persona por persona.</h2>', '<h2>La modalidad se organiza contigo, alrededor de tu semana.</h2>'),
    ('<div class="kicker">Antes de reservar</div><h2>Primero revisamos tu sector y la frecuencia que de verdad podemos sostener.</h2><p class="lead">Cuéntanos en qué sector estás, tus horarios y dónde podrías entrenar. Con eso podemos proponerte una opción honesta antes de coordinar.</p>', '<div class="kicker">Antes de empezar</div><h2>Organizamos contigo sector, espacio y frecuencia.</h2><p class="lead">Cuéntanos en qué sector estás, tus horarios y dónde prefieres entrenar. Con eso coordinamos contigo una forma de empezar que puedas sostener.</p>'),
    ('<span>¿Tu sector hace difícil sostener la presencialidad?</span><p>La frecuencia puede cambiar. El seguimiento y la dirección del plan no tienen por qué desaparecer.</p></div><a class="text-link" href="/online/">Conocer entrenamiento online</a>', '<span>¿Tu semana cambia mucho?</span><p>Podemos combinar presencial, híbrido u online para mantener continuidad sin perder el hilo del plan.</p></div><a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>'),
    ('<strong>Sí, IBERFIT contempla entrenamiento presencial en Peñalolén según sector, espacio disponible y horario.</strong> Al organizarlo revisamos que la frecuencia sea viable y que el entorno permita trabajar con calidad.', '<strong>Sí. IBERFIT ofrece entrenamiento personal presencial en Peñalolén.</strong> Coordinamos contigo sector, espacio y horario para organizar una frecuencia sostenible y una sesión de calidad.'),
    ('>Revisar mi sector y frecuencia</a>', '>Quiero empezar en Peñalolén</a>'),
])
apply(ROOT / 'en/personal-trainer-penalolen/index.html', [
    ('<h1>Peñalolén does not work the same way in every area.</h1>', '<h1>Personal training in Peñalolén, organised around your area and your week.</h1>'),
    ('<p class="lead">Travel, access and the training environment change significantly across the commune. Here, location is part of the decision rather than a footnote.</p>', '<p class="lead">We train with you in Peñalolén. We organise area, schedule and training space so the plan fits clearly into your week.</p>'),
    ('<p class="hero-support">We first understand where you are, the space you have and what frequency is viable, then choose the format with you.</p>', '<p class="hero-support">Home, residential space, hybrid or online: we organise the format with you around your goal and routine.</p>'),
    ('<p class="hero-meta">The format is decided by area, viable frequency and available training space.</p>', '<p class="hero-meta">In person in Peñalolén · Hybrid for added flexibility · Online from anywhere.</p>'),
    ('<strong>Home training</strong><br>When area and schedule make in-person work viable.', '<strong>Home training</strong><br>We coordinate area and schedule so the session fits your week.'),
    ('<strong>We confirm the area first</strong><p>In-person availability is reviewed individually because logistics vary substantially within Peñalolén. The aim is to avoid generic promises and recommend a frequency we can genuinely sustain well.</p>', '<strong>Your area helps us organise the week</strong><p>Travel time varies across Peñalolén. We use that information to coordinate schedule and frequency with you without turning logistics into a barrier.</p>'),
    ('<h2>The format is decided area by area, person by person.</h2>', '<h2>We organise the format with you around your real week.</h2>'),
    ('<div class="kicker">Before booking</div><h2>We first review your area and the frequency we can truly sustain.</h2><p class="lead">Tell us your area, schedule and where you could train. That lets us suggest an honest option before arranging sessions.</p>', '<div class="kicker">Before you start</div><h2>We organise area, training space and frequency with you.</h2><p class="lead">Tell us your area, schedule and preferred training space. From there, we coordinate a way to start that you can sustain.</p>'),
    ('<span>Does your area make frequent in-person work difficult?</span><p>The frequency can change without losing ongoing review or direction.</p></div><a class="text-link" href="/en/online/">Explore online training</a>', '<span>Does your week change a lot?</span><p>We can combine in-person, hybrid or online training while keeping the plan connected.</p></div><a class="text-link" href="/en/hybrid/">Explore hybrid training</a>'),
    ('<strong>Yes. IBERFIT provides in-person personal training in Peñalolén coordinated around area, available training space and schedule.</strong> We coordinate frequency and training environment so the service stays practical and high-quality.', '<strong>Yes. IBERFIT provides in-person personal training in Peñalolén.</strong> We organise area, training space and schedule with you so the frequency is sustainable and each session can be delivered well.'),
    ('>Review my area and frequency</a>', '>I want to start in Peñalolén</a>'),
])

# Ñuñoa: keep the useful context, remove conditional availability language.
apply(ROOT / 'personal-trainer-nunoa/index.html', [
    ('<p class="hero-meta">Presencial según sector · Híbrido si combina mejor con tu espacio y semana · Online desde cualquier lugar.</p>', '<p class="hero-meta">Presencial en Ñuñoa · Híbrido para combinar supervisión y autonomía · Online desde cualquier lugar.</p>'),
    ('<div class="kicker">Antes de reservar</div><h2>Antes de coordinar, queremos entender dónde y cómo podrías entrenar.</h2><p class="lead">Sector, espacio y horarios nos ayudan a proponerte una modalidad realista. Si lo presencial no es la mejor combinación, te lo explicamos.</p>', '<div class="kicker">Antes de empezar</div><h2>Organizamos contigo dónde, cuándo y cómo entrenar.</h2><p class="lead">Cuéntanos tu sector, el espacio que tienes y tus horarios. Con eso coordinamos contigo una modalidad que encaje en tu semana.</p>'),
    ('<strong>Sí, IBERFIT contempla entrenamiento presencial en Ñuñoa según sector, espacio disponible y horario.</strong> Al organizarlo revisamos que la frecuencia sea viable y que el entorno permita trabajar con calidad.', '<strong>Sí. IBERFIT ofrece entrenamiento personal presencial en Ñuñoa.</strong> Coordinamos contigo sector, espacio y horario para organizar una frecuencia sostenible y una sesión de calidad.'),
    ('>Ver qué modalidad encaja conmigo</a>', '>Quiero empezar en Ñuñoa</a>'),
])
apply(ROOT / 'en/personal-trainer-nunoa/index.html', [
    ('<p class="hero-meta">In person by area · Hybrid when it fits your space and week better · Online from anywhere.</p>', '<p class="hero-meta">In person in Ñuñoa · Hybrid for supervision plus autonomy · Online from anywhere.</p>'),
    ('<div class="kicker">Before booking</div><h2>We want to understand where and how you could actually train.</h2><p class="lead">Area, space and schedules help us recommend something realistic. If in-person work is not the best combination, we explain why.</p>', '<div class="kicker">Before you start</div><h2>We organise where, when and how you train with you.</h2><p class="lead">Tell us your area, available training space and schedule. From there, we coordinate a format that fits your week.</p>'),
    ('>See what fits</a>', '>I want to start in Ñuñoa</a>'),
])

# Providencia AEO should also state availability plainly.
apply(ROOT / 'entrenamiento-personal-providencia/index.html', [
    ('<strong>Sí, IBERFIT contempla entrenamiento presencial en Providencia según sector, espacio disponible y horario.</strong> Al organizarlo revisamos que la frecuencia sea viable y que el entorno permita trabajar con calidad.', '<strong>Sí. IBERFIT ofrece entrenamiento personal presencial en Providencia.</strong> Coordinamos contigo sector, espacio y horario para organizar una frecuencia sostenible y una sesión de calidad.'),
])

for path in htmls:
    text = path.read_text(encoding='utf-8')
    assert text.count('</head>') == 1, path
    assert 'contrast.v64321.css' not in text, path
    path.write_text(text.replace('</head>', CSS_LINK + '</head>'), encoding='utf-8')

VERSION.write_text('6.43.21\n', encoding='utf-8')
entry = '''## 6.43.21 — Contrast & visual hierarchy\n\n- Strengthens secondary text contrast on cream/light surfaces.\n- Gives shared callouts and editorial rows clearer surface/border separation.\n- Uses a darker bronze for small labels on light backgrounds while preserving light gold on dark sections.\n- Removes residual uncertainty-first wording from Las Condes, Lo Barnechea, Peñalolén and Ñuñoa and makes hybrid availability explicit on Home.\n- Keeps the IBERFIT palette unchanged: deep green, gold and warm cream.\n- No routing, analytics, structured data or interaction changes.\n\n'''
old = CHANGELOG.read_text(encoding='utf-8')
CHANGELOG.write_text(entry + old, encoding='utf-8')
print(f'BUILT {len(htmls)} HTML files')
