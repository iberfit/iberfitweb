from pathlib import Path

ROOT = Path('candidate/v628')


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{rel}: expected exactly 1 occurrence, found {count}: {old[:90]!r}')
    write(rel, text.replace(old, new, 1))


def replace_many(rel: str, old: str, new: str, allowed_counts=(4, 5)) -> None:
    text = read(rel)
    count = text.count(old)
    if count not in allowed_counts:
        raise SystemExit(f'{rel}: expected occurrences {allowed_counts}, found {count}: {old[:90]!r}')
    write(rel, text.replace(old, new))


def replace_date(rel: str) -> None:
    replace_once(rel, '"dateModified":"2026-09-28"', '"dateModified":"2026-09-30"')


# ---------------------------------------------------------------------------
# Editorial rule V6.43.25
# Person -> real context -> service decision. The commune states coverage only.
# A territorial characteristic must not be used to infer habits, identity or
# preferred activities. Real activities can enter the plan only when the person
# says they are already part of their week and they change a training decision.
# ---------------------------------------------------------------------------

# La Reina — ES
p = 'entrenador-personal-la-reina/index.html'
replace_once(p,
    'Entrenamiento personal en La Reina, conectado con una vida cotidiana de barrio y espacios verdes.',
    'Entrenamiento personal en La Reina, organizado alrededor de tu espacio, tus horarios y tu objetivo.')
replace_once(p,
    'La escala residencial, los espacios verdes y la cercanía a la precordillera ofrecen muchas maneras de integrar el movimiento cerca de casa y de tu rutina.',
    'Coordinamos contigo el lugar de entrenamiento, la disponibilidad y la frecuencia para que el plan sea viable desde el principio.')
replace_once(p,
    'Partimos del espacio que tienes, de cómo te gusta moverte y de tus horarios para construir una experiencia que se sienta hecha para ti.',
    'Casa, gimnasio de edificio u otro espacio adecuado pueden funcionar: la elección depende de tus necesidades reales y de lo que permita entrenar bien.')
replace_once(p,
    'Presencial en La Reina · Espacios verdes y entorno cotidiano cuando suman · Híbrido para ampliar opciones · Online desde cualquier lugar.',
    'Presencial en La Reina · Sector, espacio y horario coordinados · Híbrido para sumar autonomía · Online desde cualquier lugar.')
replace_once(p,
    '<div class="kicker">Tu entorno a favor</div><h2>Una comuna que permite entrenar cerca de tu vida real.</h2><p class="lead">La Reina conserva una escala residencial y una relación cercana con parques y precordillera. Eso permite pensar el entrenamiento desde lo que ya tienes alrededor, no desde un escenario ideal.</p>',
    '<div class="kicker">Decisiones que sí importan</div><h2>La comuna define la cobertura; tu contexto define el plan.</h2><p class="lead">La Reina es una zona de servicio presencial. A partir de ahí, elegimos contigo espacio, horario, frecuencia y modalidad según lo que realmente necesites para entrenar bien.</p>')
replace_once(p,
    '<div class="local-context-note reveal"><strong>Cercanía, espacio y movimiento cotidiano</strong><p>Si caminar, salir a un parque, entrenar en casa o moverte hacia la precordillera ya forman parte de tu semana, los tratamos como información útil para diseñar el plan.</p></div>',
    '<div class="local-context-note reveal"><strong>Sector, espacio y disponibilidad</strong><p>Estos datos sí cambian una decisión real del servicio: dónde conviene entrenar, cuánto apoyo presencial aporta valor y cómo sostener la frecuencia.</p></div>')
replace_once(p,
    '<div class="section-head reveal local-decision-head"><div class="kicker">Hecho para ti</div><h2>Convertimos esas posibilidades en una forma de entrenar propia.</h2></div>',
    '<div class="section-head reveal local-decision-head"><div class="kicker">La persona primero</div><h2>Tu forma de entrenar no se deduce de la comuna.</h2></div>')
replace_once(p,
    '<article class="principle-row reveal"><h3>Tu espacio cotidiano</h3><p>Casa, un espacio residencial o un entorno exterior pueden convertirse en escenarios útiles si encajan con tu objetivo.</p></article>',
    '<article class="principle-row reveal"><h3>Tu espacio disponible</h3><p>Casa, gimnasio de edificio u otro espacio adecuado se valoran por equipamiento, privacidad, seguridad y ajuste al objetivo.</p></article>')
replace_once(p,
    '<article class="principle-row reveal"><h3>La actividad que ya disfrutas</h3><p>Lo que haces fuera de la sesión también puede informar carga, recuperación y progresión.</p></article>',
    '<article class="principle-row reveal"><h3>Tu actividad real</h3><p>Si caminas, corres, pedaleas, haces deporte u otra actividad, la incorporamos porque forma parte de tu semana y puede cambiar carga, recuperación o progresión.</p></article>')
replace_once(p,
    '<span>¿Prefieres combinar cercanía y autonomía?</span><p>La modalidad híbrida puede ayudarte a aprovechar tu entorno sin perder supervisión cuando hace falta.</p>',
    '<span>¿Necesitas combinar supervisión y autonomía?</span><p>La modalidad híbrida conecta sesiones presenciales y trabajo guiado cuando esa combinación mejora tu continuidad.</p>')
replace_date(p)

# La Reina — EN
p = 'en/personal-trainer-la-reina/index.html'
replace_once(p,
    'Personal training in La Reina, connected to everyday neighbourhood life and green spaces.',
    'Personal training in La Reina, organised around your space, schedule and goal.')
replace_once(p,
    'Its residential scale, green spaces and proximity to the foothills create many ways to make movement part of life close to home.',
    'We coordinate training space, availability and frequency with you so the plan is workable from the start.')
replace_once(p,
    'We start with the space you have, the way you enjoy moving and your schedule to build an experience that feels made for you.',
    'Home, a building gym or another suitable space can all work: the choice depends on your real needs and what allows good training.')
replace_once(p,
    'In-person in La Reina · Green and everyday spaces when they add value · Hybrid for more options · Online from anywhere.',
    'In-person in La Reina · Area, space and schedule coordinated · Hybrid for more autonomy · Online from anywhere.')
replace_once(p,
    '<div class="kicker">Your surroundings on your side</div><h2>A place where training can stay close to real life.</h2><p class="lead">La Reina keeps a residential scale and a close relationship with parks and the foothills. That lets us design training from what is already around you rather than from an idealised setup.</p>',
    '<div class="kicker">Decisions that matter</div><h2>The commune defines coverage; your context defines the plan.</h2><p class="lead">La Reina is an in-person service area. From there, we choose training space, schedule, frequency and format with you according to what you actually need to train well.</p>')
replace_once(p,
    '<div class="local-context-note reveal"><strong>Proximity, space and everyday movement</strong><p>If walking, using a park, training at home or heading towards the foothills are already part of your week, we treat them as useful information for the plan.</p></div>',
    '<div class="local-context-note reveal"><strong>Area, space and availability</strong><p>These details change real service decisions: where training works best, how much in-person support adds value and how to sustain frequency.</p></div>')
replace_once(p,
    '<div class="section-head reveal local-decision-head"><div class="kicker">Made for you</div><h2>We turn those possibilities into your own way of training.</h2></div>',
    '<div class="section-head reveal local-decision-head"><div class="kicker">Person first</div><h2>Your way of training is not inferred from the commune.</h2></div>')
replace_once(p,
    '<article class="principle-row reveal"><h3>Your everyday space</h3><p>Home, a residential space or an outdoor setting can all become useful training environments when they fit the goal.</p></article>',
    '<article class="principle-row reveal"><h3>Your available space</h3><p>Home, a building gym or another suitable space are assessed by equipment, privacy, safety and fit with the goal.</p></article>')
replace_once(p,
    '<article class="principle-row reveal"><h3>The activity you already enjoy</h3><p>What you do outside sessions can inform workload, recovery and progression.</p></article>',
    '<article class="principle-row reveal"><h3>Your real activity</h3><p>If you walk, run, cycle, play sport or do another activity, we include it because it is part of your week and can change workload, recovery or progression.</p></article>')
replace_once(p,
    '<span>Would you rather combine proximity and autonomy?</span><p>Hybrid support can help you use your environment without losing direct supervision when it matters.</p>',
    '<span>Do you need to combine supervision and autonomy?</span><p>Hybrid training connects in-person sessions and guided work when that combination improves continuity.</p>')
replace_date(p)

# Ñuñoa — ES
p = 'personal-trainer-nunoa/index.html'
old_desc = 'Entrenamiento personal en Ñuñoa con diagnóstico, planificación y seguimiento, conectado con tu vida de barrio, el espacio que ya tienes y las formas de moverte que disfrutas.'
new_desc = 'Entrenamiento personal en Ñuñoa con diagnóstico, planificación y seguimiento; coordinamos sector, espacio, horario y modalidad según tu contexto.'
replace_many(p, old_desc, new_desc)
replace_once(p,
    'Ñuñoa tiene vida de barrio, plazas y parques: tu entrenamiento puede sentirse igual de cercano.',
    'Entrenamiento personal en Ñuñoa, con una forma de trabajo adaptada a tu semana.')
replace_once(p,
    'Casas, departamentos, gimnasios de edificio, plazas y parques crean muchas maneras de integrar el entrenamiento sin separarlo de la vida que ya haces en tu barrio.',
    'Coordinamos sector, espacio, horario y frecuencia para elegir una modalidad que puedas sostener y una sesión que pueda hacerse bien.')
replace_once(p,
    'Partimos del espacio y la rutina que ya tienes para construir una forma de entrenar que puedas reconocer como tuya.',
    'Casa, gimnasio de edificio u otro espacio adecuado son opciones si encajan con tu objetivo y con el equipamiento disponible.')
replace_once(p,
    'Presencial en Ñuñoa · Barrio, plazas y parques como posibilidades · Híbrido para sumar autonomía · Online desde cualquier lugar.',
    'Presencial en Ñuñoa · Sector, espacio y horario coordinados · Híbrido para sumar autonomía · Online desde cualquier lugar.')
replace_once(p,
    'aria-label="Formas de entrenar cerca de tu vida en Ñuñoa"',
    'aria-label="Opciones de espacio y acompañamiento para entrenar en Ñuñoa"')
replace_once(p,
    '<div class="local-service-chip"><b>03</b><span><strong>Plazas, parques y exterior</strong><br>La vida de barrio ofrece espacios que pueden sumar movimiento y variedad cuando encajan contigo.</span></div>',
    '<div class="local-service-chip"><b>03</b><span><strong>Otro espacio adecuado</strong><br>Si tienes acceso a otro lugar útil para entrenar, lo evaluamos por seguridad, equipamiento y ajuste al objetivo.</span></div>')
replace_once(p,
    '<div class="kicker">Cerca de tu vida</div><h2>Entrenar cerca de casa puede ser una fortaleza.</h2><p class="lead">Ñuñoa tiene una vida barrial muy vinculada a plazas, parques y actividad comunitaria. Ese entorno permite pensar el entrenamiento desde lugares y rutinas que ya te resultan familiares.</p>',
    '<div class="kicker">Lo que cambia la decisión</div><h2>Tu contexto concreto vale más que cualquier idea sobre la comuna.</h2><p class="lead">Estar en Ñuñoa nos dice dónde prestar el servicio; para diseñarlo bien necesitamos saber tu sector, tus horarios, el espacio disponible y el tipo de apoyo que te aporta más valor.</p>')
replace_once(p,
    '<div class="local-context-note reveal"><strong>Que el plan se parezca a tu vida</strong><p>No necesitamos inventar una rutina completamente ajena a tu semana. Podemos construir desde tu espacio, tus recorridos, los lugares que disfrutas y el movimiento que ya existe.</p></div>',
    '<div class="local-context-note reveal"><strong>Datos reales, no supuestos</strong><p>No inferimos tus hábitos, tus actividades ni tus lugares preferidos por vivir en Ñuñoa. Solo incorporamos lo que tú nos cuentas y lo que cambia una decisión de entrenamiento.</p></div>')
replace_once(p,
    '<div class="kicker">Una rutina reconocible</div><h2>Elegimos contigo una forma de entrenar que se sienta cercana.</h2><p class="lead">La mejor combinación es la que te permite progresar sin perder el vínculo con lo que disfrutas hacer.</p>',
    '<div class="kicker">La persona primero</div><h2>El plan se construye contigo, no alrededor de un perfil de Ñuñoa.</h2><p class="lead">La mejor combinación es la que responde a tu objetivo, tu agenda y los recursos que realmente tienes.</p>')
replace_once(p,
    '<article class="principle-row reveal"><h3>Lo que te gusta repetir</h3><p>Las actividades y lugares que disfrutas ayudan a construir adherencia y una semana más propia.</p></article>',
    '<article class="principle-row reveal"><h3>Tu actividad real</h3><p>Si ya haces alguna actividad, la integramos porque forma parte de tu semana y puede modificar carga, recuperación o prioridades.</p></article>')
replace_date(p)

# Ñuñoa — EN
p = 'en/personal-trainer-nunoa/index.html'
old_desc = 'Personal training in Ñuñoa with assessment, planning and follow-up, connected to neighbourhood life, the space you already have and the ways you enjoy moving.'
new_desc = 'Personal training in Ñuñoa with assessment, planning and follow-up; we coordinate area, space, schedule and format around your actual context.'
replace_many(p, old_desc, new_desc, allowed_counts=(4,))
replace_once(p,
    'Ñuñoa has neighbourhood life, plazas and parks: your training can feel just as close to home.',
    'Personal training in Ñuñoa, with a way of working adapted to your week.')
replace_once(p,
    'Houses, apartments, building gyms, plazas and parks create many ways to integrate training without separating it from the life you already have in your neighbourhood.',
    'We coordinate area, space, schedule and frequency to choose a format you can sustain and a session that can be delivered well.')
replace_once(p,
    'We start with the space and routine you already have to build a way of training you can genuinely recognise as your own.',
    'Home, a building gym or another suitable space are options when they fit your goal and the equipment available.')
replace_once(p,
    'In-person in Ñuñoa · Neighbourhood, plazas and parks as possibilities · Hybrid for more autonomy · Online from anywhere.',
    'In-person in Ñuñoa · Area, space and schedule coordinated · Hybrid for more autonomy · Online from anywhere.')
replace_once(p,
    'aria-label="Ways to train close to everyday life in Ñuñoa"',
    'aria-label="Training-space and coaching options in Ñuñoa"')
replace_once(p,
    '<div class="local-service-chip"><b>03</b><span><strong>Plazas, parks and outdoors</strong><br>Neighbourhood life offers spaces that can add movement and variety when they fit you.</span></div>',
    '<div class="local-service-chip"><b>03</b><span><strong>Another suitable space</strong><br>If you have access to another useful training space, we assess it by safety, equipment and fit with the goal.</span></div>')
replace_once(p,
    '<div class="kicker">Close to real life</div><h2>Training close to home can be a strength.</h2><p class="lead">Ñuñoa has a strong neighbourhood life connected to plazas, parks and community activity. That makes it possible to build training around places and routines that already feel familiar.</p>',
    '<div class="kicker">What changes the decision</div><h2>Your actual context matters more than any idea about the commune.</h2><p class="lead">Being in Ñuñoa tells us where to provide the service; to design it well we need your area, schedule, available space and the level of support that adds value for you.</p>')
replace_once(p,
    '<div class="local-context-note reveal"><strong>Let the plan look like your life</strong><p>We do not need to invent a routine completely separate from your week. We can build from your space, routes, favourite places and the movement already present.</p></div>',
    '<div class="local-context-note reveal"><strong>Real information, not assumptions</strong><p>We do not infer your habits, activities or preferred places from living in Ñuñoa. We only include what you tell us and what changes a training decision.</p></div>')
replace_once(p,
    '<div class="kicker">A routine you recognise</div><h2>Together we choose a way of training that feels close to you.</h2><p class="lead">The best combination is the one that helps you progress without losing connection to what you enjoy doing.</p>',
    '<div class="kicker">Person first</div><h2>The plan is built with you, not around a Ñuñoa profile.</h2><p class="lead">The best combination is the one that matches your goal, schedule and the resources you actually have.</p>')
replace_once(p,
    '<article class="principle-row reveal"><h3>What you enjoy repeating</h3><p>Activities and places you enjoy can support adherence and make the week feel more yours.</p></article>',
    '<article class="principle-row reveal"><h3>Your real activity</h3><p>If you already do another activity, we include it because it is part of your week and can change workload, recovery or priorities.</p></article>')
replace_date(p)

# Peñalolén — ES
p = 'entrenador-personal-penalolen/index.html'
old_desc = 'Entrenamiento personal en Peñalolén con diagnóstico, planificación y seguimiento, aprovechando tu rutina, tu espacio y las posibilidades de movimiento de tu entorno.'
new_desc = 'Entrenamiento personal en Peñalolén con diagnóstico, planificación y seguimiento; coordinamos sector, espacio, horario y modalidad según tu contexto.'
replace_many(p, old_desc, new_desc)
replace_once(p,
    'Entrenamiento personal en Peñalolén, aprovechando todo lo que tu entorno ya ofrece.',
    'Entrenamiento personal en Peñalolén, organizado desde tu contexto real.')
replace_once(p,
    'Peñalolén combina vida de barrio, parques, espacios deportivos y cercanía a la precordillera. Eso abre distintas formas de moverte y entrenar sin alejar el plan de tu vida real.',
    'Coordinamos sector, espacio, horario y frecuencia para elegir una forma de entrenar que sea viable, segura y sostenible.')
replace_once(p,
    'Si ya caminas, usas parques, haces actividad al aire libre o prefieres entrenar en casa, partimos de ahí y lo convertimos en una ventaja para tu planificación.',
    'Si ya caminas, corres, haces deporte, entrenas en casa o realizas actividad al aire libre, lo incorporamos porque forma parte de tu semana; no lo suponemos por vivir en Peñalolén.')
replace_once(p,
    'Presencial en Peñalolén · Exterior cuando suma · Híbrido para conectar supervisión y autonomía · Online desde cualquier lugar.',
    'Presencial en Peñalolén · Sector, espacio y horario coordinados · Híbrido para conectar supervisión y autonomía · Online desde cualquier lugar.')
replace_once(p,
    'aria-label="Formas de aprovechar tu entorno para entrenar en Peñalolén"',
    'aria-label="Opciones de espacio y acompañamiento para entrenar en Peñalolén"')
replace_once(p,
    '<div class="local-service-chip"><b>03</b><span><strong>Parques y espacios abiertos</strong><br>Peñalolén ofrece alternativas al aire libre que pueden sumar cuando encajan con tu objetivo y tus preferencias.</span></div>',
    '<div class="local-service-chip"><b>03</b><span><strong>Otro espacio adecuado</strong><br>Si tienes acceso a otro lugar útil para entrenar, lo evaluamos por seguridad, equipamiento y ajuste al objetivo.</span></div>')
replace_once(p,
    '<div class="kicker">Vivir y entrenar aquí</div><h2>Tu entorno no limita el plan: le da opciones.</h2><p class="lead">Parques, vida de barrio y cercanía a la precordillera forman parte de la realidad de Peñalolén. IBERFIT usa ese contexto para elegir contigo una forma de entrenar que se sienta natural y propia.</p>',
    '<div class="kicker">Tu contexto, no un arquetipo</div><h2>Estar en Peñalolén define la cobertura; tus datos definen el plan.</h2><p class="lead">Para decidir bien no necesitamos asumir cómo te mueves por la comuna. Necesitamos tu sector, espacio, horarios, objetivo y actividad real.</p>')
replace_once(p,
    '<div class="local-context-note reveal"><strong>Lo que ya forma parte de tu vida cuenta</strong><p>Caminar, moverte al aire libre, usar un parque o tener un espacio en casa no son piezas separadas del entrenamiento. Cuando son relevantes para ti, las incorporamos al contexto del plan.</p></div>',
    '<div class="local-context-note reveal"><strong>Lo que ya haces sí cuenta</strong><p>Caminar, correr, bicicleta, trekking, deporte u otra actividad se incorporan solo cuando forman parte de tu vida y cambian carga, recuperación o planificación.</p></div>')
replace_once(p,
    '<div class="kicker">Hecho para tu semana</div><h2>Diseñamos el plan alrededor de cómo vives Peñalolén.</h2><p class="lead">No partimos de una modalidad cerrada: partimos de ti, de lo que ya haces y de dónde te resulta más fácil mantener una buena rutina.</p>',
    '<div class="kicker">Hecho para tu semana</div><h2>Diseñamos el plan alrededor de tu semana, no de una idea sobre Peñalolén.</h2><p class="lead">No partimos de una modalidad cerrada: partimos de ti, de lo que ya haces y de dónde te resulta más fácil mantener una buena rutina.</p>')
replace_once(p,
    '<article class="principle-row reveal"><h3>El lugar que te resulta natural</h3><p>Casa, gimnasio de edificio o exterior pueden ser buenos escenarios si permiten entrenar con intención y seguridad.</p></article>',
    '<article class="principle-row reveal"><h3>El espacio que tienes disponible</h3><p>Casa, gimnasio de edificio u otro lugar adecuado se valoran por seguridad, equipamiento y ajuste al objetivo.</p></article>')
replace_date(p)

# Peñalolén — EN
p = 'en/personal-trainer-penalolen/index.html'
old_desc = 'Personal training in Peñalolén with assessment, planning and follow-up, built around your routine, your space and the movement opportunities already present in your surroundings.'
new_desc = 'Personal training in Peñalolén with assessment, planning and follow-up; we coordinate area, space, schedule and format around your actual context.'
replace_many(p, old_desc, new_desc, allowed_counts=(4,))
replace_once(p,
    'Personal training in Peñalolén, making the most of what your surroundings already offer.',
    'Personal training in Peñalolén, organised around your actual context.')
replace_once(p,
    'Peñalolén combines neighbourhood life, parks, sports spaces and proximity to the foothills. That creates more than one good way to move and train without separating the plan from real life.',
    'We coordinate area, space, schedule and frequency to choose a way of training that is workable, safe and sustainable.')
replace_once(p,
    'If walking, parks, outdoor activity or training at home are already part of your week, we start there and turn that context into an advantage for your plan.',
    'If you already walk, run, play sport, train at home or do outdoor activity, we include it because it is part of your week; we do not assume it from living in Peñalolén.')
replace_once(p,
    'In-person in Peñalolén · Outdoors when it adds value · Hybrid to connect coaching and autonomy · Online from anywhere.',
    'In-person in Peñalolén · Area, space and schedule coordinated · Hybrid to connect coaching and autonomy · Online from anywhere.')
replace_once(p,
    'aria-label="Ways to use your surroundings for training in Peñalolén"',
    'aria-label="Training-space and coaching options in Peñalolén"')
replace_once(p,
    '<div class="local-service-chip"><b>03</b><span><strong>Parks and open spaces</strong><br>Peñalolén offers outdoor options that can add value when they fit your goals and preferences.</span></div>',
    '<div class="local-service-chip"><b>03</b><span><strong>Another suitable space</strong><br>If you have access to another useful training space, we assess it by safety, equipment and fit with the goal.</span></div>')
replace_once(p,
    '<div class="kicker">Living and training here</div><h2>Your surroundings do not limit the plan: they give it options.</h2><p class="lead">Parks, neighbourhood life and proximity to the foothills are part of Peñalolén. IBERFIT uses that context to build a way of training that feels natural and genuinely yours.</p>',
    '<div class="kicker">Your context, not an archetype</div><h2>Being in Peñalolén defines coverage; your information defines the plan.</h2><p class="lead">To make good decisions we do not need to assume how you move around the commune. We need your area, available space, schedule, goal and real activity.</p>')
replace_once(p,
    '<div class="local-context-note reveal"><strong>What is already part of your life counts</strong><p>Walking, moving outdoors, using a park or having training space at home are not separate from the plan. When they matter to you, they become useful planning context.</p></div>',
    '<div class="local-context-note reveal"><strong>What you actually do counts</strong><p>Walking, running, cycling, hiking, sport or another activity are included only when they are part of your life and change workload, recovery or planning.</p></div>')
replace_once(p,
    '<div class="kicker">Built around your week</div><h2>We design the plan around how you live in Peñalolén.</h2><p class="lead">We do not start with a fixed format. We start with you, what you already do and where a good routine feels easiest to repeat.</p>',
    '<div class="kicker">Built around your week</div><h2>We design the plan around your week, not around an idea of Peñalolén.</h2><p class="lead">We do not start with a fixed format. We start with you, what you already do and where a good routine feels easiest to repeat.</p>')
replace_once(p,
    '<article class="principle-row reveal"><h3>The place that feels natural</h3><p>Home, a building gym or outdoors can all work when they support purposeful, safe training.</p></article>',
    '<article class="principle-row reveal"><h3>The space you have available</h3><p>Home, a building gym or another suitable place are assessed by safety, equipment and fit with the goal.</p></article>')
replace_date(p)

# Version + changelog
(ROOT / 'VERSION').write_text('6.43.25\n', encoding='utf-8')
changelog = ROOT / 'CHANGELOG.md'
current = changelog.read_text(encoding='utf-8')
entry = '''## 6.43.25 — Person-first local editorial rule\n\n- Corrects the systemic local-page pattern that inferred lifestyle or preferred activity from the commune.\n- La Reina, Ñuñoa and Peñalolén now use the commune to state service coverage while sector, space, schedule, frequency, goals and the person’s real activity drive training decisions.\n- Real walking, running, cycling, sport or outdoor activity can still inform planning when the client actually does it; it is never inferred from address alone.\n- Spanish and English are updated as structural pairs, while contextual WhatsApp intent, canonical/hreflang architecture, direct service answers and modality truth are preserved.\n- Adds explicit regression guards so neighbourhood/territorial storytelling cannot silently return to these pages.\n\n'''
if not current.startswith('## 6.43.25 — Person-first local editorial rule'):
    changelog.write_text(entry + current, encoding='utf-8')

print('BUILD_V64325_PERSON_FIRST_LOCAL_OK')
