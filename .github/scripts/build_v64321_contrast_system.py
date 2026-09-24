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

# Lo Barnechea still carried an older uncertainty-first tone. Keep logistics as useful
# context, but make availability clear and speak directly to the client.
es = ROOT / 'entrenador-personal-lo-barnechea/index.html'
for old, new in [
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
]:
    replace_exact(es, old, new)

en = ROOT / 'en/personal-trainer-lo-barnechea/index.html'
for old, new in [
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
]:
    replace_exact(en, old, new)

for path in htmls:
    text = path.read_text(encoding='utf-8')
    assert text.count('</head>') == 1, path
    assert 'contrast.v64321.css' not in text, path
    path.write_text(text.replace('</head>', CSS_LINK + '</head>'), encoding='utf-8')

VERSION.write_text('6.43.21\n', encoding='utf-8')
entry = '''## 6.43.21 — Contrast & visual hierarchy\n\n- Strengthens secondary text contrast on cream/light surfaces.\n- Gives shared callouts and editorial rows clearer surface/border separation.\n- Uses a darker bronze for small labels on light backgrounds while preserving light gold on dark sections.\n- Removes the remaining uncertainty-first wording from Lo Barnechea ES/EN and speaks directly to the client.\n- Keeps the IBERFIT palette unchanged: deep green, gold and warm cream.\n- No routing, analytics, structured data or interaction changes.\n\n'''
old = CHANGELOG.read_text(encoding='utf-8')
CHANGELOG.write_text(entry + old, encoding='utf-8')
print(f'BUILT {len(htmls)} HTML files')
