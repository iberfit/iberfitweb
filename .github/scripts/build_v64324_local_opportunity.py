from pathlib import Path
import json
import re

ROOT = Path('candidate/v628')
VERSION = ROOT / 'VERSION'
TODAY = '2026-09-28'

assert VERSION.read_text(encoding='utf-8').strip() == '6.43.23'
VERSION.write_text('6.43.24\n', encoding='utf-8')


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel, text):
    (ROOT / rel).write_text(text, encoding='utf-8')


def section_bounds(text, start):
    end = text.find('</section>', start)
    assert end >= 0, 'section end not found'
    return start, end + len('</section>')


def hero_bounds(text):
    start = text.find('<section class="hero">')
    assert start >= 0, 'hero not found'
    return section_bounds(text, start)


def next_section_exact(text, after, class_name):
    start = text.find(f'<section class="{class_name}">', after)
    assert start >= 0, f'section class not found: {class_name}'
    return section_bounds(text, start)


def replace_div_by_class(text, class_name, replacement):
    needle = f'<div class="{class_name}"'
    start = text.find(needle)
    assert start >= 0, f'div not found: {class_name}'
    token_re = re.compile(r'</?div\b[^>]*>', re.I)
    depth = 0
    for m in token_re.finditer(text, start):
        token = m.group(0)
        if token.startswith('</'):
            depth -= 1
            if depth == 0:
                return text[:start] + replacement + text[m.end():]
        else:
            depth += 1
    raise AssertionError(f'unbalanced div: {class_name}')


def sub_one(pattern, replacement, text, label):
    out, n = re.subn(pattern, replacement, text, count=1, flags=re.S)
    assert n == 1, f'{label}: expected one replacement, got {n}'
    return out


def update_hero(text, cfg):
    hs, he = hero_bounds(text)
    hero = text[hs:he]
    hero = sub_one(r'<h1>.*?</h1>', f'<h1>{cfg["h1"]}</h1>', hero, 'hero h1')
    hero = sub_one(r'<p class="lead">.*?</p>', f'<p class="lead">{cfg["lead"]}</p>', hero, 'hero lead')
    hero = sub_one(r'<p class="hero-support">.*?</p>', f'<p class="hero-support">{cfg["support"]}</p>', hero, 'hero support')
    hero = sub_one(r'<p class="hero-meta">.*?</p>', f'<p class="hero-meta">{cfg["meta"]}</p>', hero, 'hero meta')
    if cfg.get('strip'):
        assert 'class="local-service-strip"' in hero
        chips = ''.join(
            f'<div class="local-service-chip"><b>{i:02d}</b><span><strong>{title}</strong><br>{body}</span></div>'
            for i, (title, body) in enumerate(cfg['strip'], 1)
        )
        aria = cfg['strip_aria']
        replacement = f'<div class="local-service-strip" aria-label="{aria}">{chips}</div>'
        hero = replace_div_by_class(hero, 'local-service-strip', replacement)
    return text[:hs] + hero + text[he:]


def context_section(cfg):
    return (
        '<section class="section"><div class="container">'
        '<div class="section-head reveal">'
        f'<div class="kicker">{cfg["context_kicker"]}</div>'
        f'<h2>{cfg["context_h2"]}</h2>'
        f'<p class="lead">{cfg["context_lead"]}</p>'
        '</div>'
        '<div class="local-context-note reveal">'
        f'<strong>{cfg["note_title"]}</strong><p>{cfg["note_body"]}</p>'
        '</div></div></section>'
    )


def principle_stack(cfg):
    rows = ''.join(
        f'<article class="principle-row reveal"><h3>{title}</h3><p>{body}</p></article>'
        for title, body in cfg['principles']
    )
    return f'<div class="principle-stack">{rows}</div>'


def decision_section(cfg):
    return (
        '<section class="section section-cream"><div class="container">'
        '<div class="section-head reveal">'
        f'<div class="kicker">{cfg["decision_kicker"]}</div>'
        f'<h2>{cfg["decision_h2"]}</h2>'
        f'<p class="lead">{cfg["decision_lead"]}</p>'
        '</div>' + principle_stack(cfg) + '</div></section>'
    )


def combined_section(cfg):
    return (
        '<section class="section"><div class="container">'
        '<div class="section-head reveal">'
        f'<div class="kicker">{cfg["context_kicker"]}</div>'
        f'<h2>{cfg["context_h2"]}</h2>'
        f'<p class="lead">{cfg["context_lead"]}</p>'
        '</div>'
        '<div class="local-context-note reveal">'
        f'<strong>{cfg["note_title"]}</strong><p>{cfg["note_body"]}</p>'
        '</div>'
        '<div class="section-head reveal local-decision-head">'
        f'<div class="kicker">{cfg["decision_kicker"]}</div>'
        f'<h2>{cfg["decision_h2"]}</h2>'
        '</div>' + principle_stack(cfg) + '</div></section>'
    )


def set_meta_descriptions(text, desc):
    text = sub_one(r'<meta content="[^"]*" name="description"/>', f'<meta content="{desc}" name="description"/>', text, 'meta description')
    text = sub_one(r'<meta content="[^"]*" property="og:description"/>', f'<meta content="{desc}" property="og:description"/>', text, 'og description')
    text = sub_one(r'<meta content="[^"]*" name="twitter:description"/>', f'<meta content="{desc}" name="twitter:description"/>', text, 'twitter description')
    return text


def update_jsonld(text, cfg):
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
    assert m, f'{cfg["rel"]}: jsonld missing'
    data = json.loads(m.group(1))
    aliases = [x.casefold() for x in cfg['aliases']]

    def walk(node):
        if isinstance(node, dict):
            for k, v in list(node.items()):
                if k == 'dateModified':
                    node[k] = TODAY
                elif k == 'description' and isinstance(v, str) and any(a in v.casefold() for a in aliases):
                    node[k] = cfg['description']
                else:
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    return text[:m.start(1)] + payload + text[m.end(1):]


PAGES = [
    {
        'rel':'entrenador-personal-penalolen/index.html','aliases':['Peñalolén','Penalolen'],'description':'Entrenamiento personal en Peñalolén con diagnóstico, planificación y seguimiento, aprovechando tu rutina, tu espacio y las posibilidades de movimiento de tu entorno.',
        'h1':'Entrenamiento personal en Peñalolén, aprovechando todo lo que tu entorno ya ofrece.',
        'lead':'Peñalolén combina vida de barrio, parques, espacios deportivos y cercanía a la precordillera. Eso abre distintas formas de moverte y entrenar sin alejar el plan de tu vida real.',
        'support':'Si ya caminas, usas parques, haces actividad al aire libre o prefieres entrenar en casa, partimos de ahí y lo convertimos en una ventaja para tu planificación.',
        'meta':'Presencial en Peñalolén · Exterior cuando suma · Híbrido para conectar supervisión y autonomía · Online desde cualquier lugar.',
        'strip_aria':'Formas de aprovechar tu entorno para entrenar en Peñalolén','strip':[
            ('Domicilio','Tu casa puede ser el punto de partida si es donde mejor encaja una sesión de calidad.'),
            ('Espacio residencial','Aprovechamos gimnasio de edificio o espacios comunes cuando forman parte natural de tu rutina.'),
            ('Parques y espacios abiertos','Peñalolén ofrece alternativas al aire libre que pueden sumar cuando encajan con tu objetivo y tus preferencias.'),
            ('Híbrido','Combina supervisión directa y trabajo guiado para darte más maneras de sostener el mismo plan.')],
        'context_kicker':'Vivir y entrenar aquí','context_h2':'Tu entorno no limita el plan: le da opciones.',
        'context_lead':'Parques, vida de barrio y cercanía a la precordillera forman parte de la realidad de Peñalolén. IBERFIT usa ese contexto para elegir contigo una forma de entrenar que se sienta natural y propia.',
        'note_title':'Lo que ya forma parte de tu vida cuenta','note_body':'Caminar, moverte al aire libre, usar un parque o tener un espacio en casa no son piezas separadas del entrenamiento. Cuando son relevantes para ti, las incorporamos al contexto del plan.',
        'decision_kicker':'Hecho para tu semana','decision_h2':'Diseñamos el plan alrededor de cómo vives Peñalolén.','decision_lead':'No partimos de una modalidad cerrada: partimos de ti, de lo que ya haces y de dónde te resulta más fácil mantener una buena rutina.',
        'principles':[
            ('Tu movimiento cotidiano','Lo que ya haces durante la semana nos ayuda a ajustar carga, recuperación y prioridades sin empezar de cero.'),
            ('El lugar que te resulta natural','Casa, gimnasio de edificio o exterior pueden ser buenos escenarios si permiten entrenar con intención y seguridad.'),
            ('El acompañamiento que más te aporta','Presencial, híbrido u online se combinan para darte supervisión donde suma y autonomía bien guiada donde ya la tienes.')],
        'remove_next_plain':True,
    },
    {
        'rel':'en/personal-trainer-penalolen/index.html','aliases':['Peñalolén','Penalolen'],'description':'Personal training in Peñalolén with assessment, planning and follow-up, built around your routine, your space and the movement opportunities already present in your surroundings.',
        'h1':'Personal training in Peñalolén, making the most of what your surroundings already offer.',
        'lead':'Peñalolén combines neighbourhood life, parks, sports spaces and proximity to the foothills. That creates more than one good way to move and train without separating the plan from real life.',
        'support':'If walking, parks, outdoor activity or training at home are already part of your week, we start there and turn that context into an advantage for your plan.',
        'meta':'In-person in Peñalolén · Outdoors when it adds value · Hybrid to connect coaching and autonomy · Online from anywhere.',
        'strip_aria':'Ways to use your surroundings for training in Peñalolén','strip':[
            ('At home','Home can be the starting point when it is where a high-quality session fits best.'),
            ('Residential space','We can use a building gym or shared space when it naturally fits your routine.'),
            ('Parks and open spaces','Peñalolén offers outdoor options that can add value when they fit your goals and preferences.'),
            ('Hybrid','Combine direct coaching and guided training to create more ways to sustain the same plan.')],
        'context_kicker':'Living and training here','context_h2':'Your surroundings do not limit the plan: they give it options.',
        'context_lead':'Parks, neighbourhood life and proximity to the foothills are part of Peñalolén. IBERFIT uses that context to build a way of training that feels natural and genuinely yours.',
        'note_title':'What is already part of your life counts','note_body':'Walking, moving outdoors, using a park or having training space at home are not separate from the plan. When they matter to you, they become useful planning context.',
        'decision_kicker':'Built around your week','decision_h2':'We design the plan around how you live in Peñalolén.','decision_lead':'We do not start with a fixed format. We start with you, what you already do and where a good routine feels easiest to repeat.',
        'principles':[
            ('Your everyday movement','What you already do during the week helps us calibrate workload, recovery and priorities.'),
            ('The place that feels natural','Home, a building gym or outdoors can all work when they support purposeful, safe training.'),
            ('The coaching that adds most value','In-person, hybrid and online can combine direct supervision with well-guided autonomy.')],
        'remove_next_plain':True,
    },
    {
        'rel':'entrenador-personal-la-reina/index.html','aliases':['La Reina'],'description':'Entrenamiento personal en La Reina con diagnóstico, planificación y seguimiento; presencial, híbrido u online organizados alrededor de tu rutina, tu espacio y tu forma de moverte.',
        'h1':'Entrenamiento personal en La Reina, conectado con una vida cotidiana de barrio y espacios verdes.',
        'lead':'La escala residencial, los espacios verdes y la cercanía a la precordillera ofrecen muchas maneras de integrar el movimiento cerca de casa y de tu rutina.',
        'support':'Partimos del espacio que tienes, de cómo te gusta moverte y de tus horarios para construir una experiencia que se sienta hecha para ti.',
        'meta':'Presencial en La Reina · Espacios verdes y entorno cotidiano cuando suman · Híbrido para ampliar opciones · Online desde cualquier lugar.',
        'context_kicker':'Tu entorno a favor','context_h2':'Una comuna que permite entrenar cerca de tu vida real.',
        'context_lead':'La Reina conserva una escala residencial y una relación cercana con parques y precordillera. Eso permite pensar el entrenamiento desde lo que ya tienes alrededor, no desde un escenario ideal.',
        'note_title':'Cercanía, espacio y movimiento cotidiano','note_body':'Si caminar, salir a un parque, entrenar en casa o moverte hacia la precordillera ya forman parte de tu semana, los tratamos como información útil para diseñar el plan.',
        'decision_kicker':'Hecho para ti','decision_h2':'Convertimos esas posibilidades en una forma de entrenar propia.','decision_lead':'La modalidad se elige por lo que te ayuda a avanzar y disfrutar de una rutina sostenible.',
        'principles':[
            ('Tu espacio cotidiano','Casa, un espacio residencial o un entorno exterior pueden convertirse en escenarios útiles si encajan con tu objetivo.'),
            ('La actividad que ya disfrutas','Lo que haces fuera de la sesión también puede informar carga, recuperación y progresión.'),
            ('Tu mezcla de supervisión y autonomía','Presencial, híbrido u online se combinan para acompañarte con el nivel de apoyo que realmente te aporta.')],
        'combined':True,
    },
    {
        'rel':'en/personal-trainer-la-reina/index.html','aliases':['La Reina'],'description':'Personal training in La Reina with assessment, planning and follow-up; in-person, hybrid or online coaching organised around your routine, your space and the way you like to move.',
        'h1':'Personal training in La Reina, connected to everyday neighbourhood life and green spaces.',
        'lead':'Its residential scale, green spaces and proximity to the foothills create many ways to make movement part of life close to home.',
        'support':'We start with the space you have, the way you enjoy moving and your schedule to build an experience that feels made for you.',
        'meta':'In-person in La Reina · Green and everyday spaces when they add value · Hybrid for more options · Online from anywhere.',
        'context_kicker':'Your surroundings on your side','context_h2':'A place where training can stay close to real life.',
        'context_lead':'La Reina keeps a residential scale and a close relationship with parks and the foothills. That lets us design training from what is already around you rather than from an idealised setup.',
        'note_title':'Proximity, space and everyday movement','note_body':'If walking, using a park, training at home or heading towards the foothills are already part of your week, we treat them as useful information for the plan.',
        'decision_kicker':'Made for you','decision_h2':'We turn those possibilities into your own way of training.','decision_lead':'The format is chosen for what helps you progress and enjoy a routine you can keep.',
        'principles':[
            ('Your everyday space','Home, a residential space or an outdoor setting can all become useful training environments when they fit the goal.'),
            ('The activity you already enjoy','What you do outside sessions can inform workload, recovery and progression.'),
            ('Your balance of coaching and autonomy','In-person, hybrid and online can combine to give you the level of support that adds the most value.')],
        'combined':True,
    },
    {
        'rel':'entrenador-personal-las-condes/index.html','aliases':['Las Condes'],'description':'Entrenamiento personal en Las Condes con diagnóstico, planificación y seguimiento, aprovechando la variedad de espacios deportivos, parques y opciones de movilidad de tu entorno.',
        'h1':'En Las Condes, tener muchas opciones alrededor puede jugar a favor de tu constancia.',
        'lead':'Parques, espacios deportivos, gimnasios de edificio y distintas formas de moverte por la comuna amplían las posibilidades para colocar el entrenamiento donde mejor funciona para ti.',
        'support':'No necesitas adaptarte a un único formato: usamos tu objetivo, tu rutina y los recursos que ya tienes cerca para construir una experiencia personal.',
        'meta':'Presencial en Las Condes · Distintos espacios para entrenar · Híbrido para sumar flexibilidad · Online desde cualquier lugar.',
        'strip_aria':'Opciones para entrenar en Las Condes','strip':[
            ('Domicilio','Una opción directa cuando quieres integrar la sesión en el lugar donde ya transcurre tu día.'),
            ('Gimnasio de edificio','Aprovechamos equipamiento cercano cuando permite trabajar con calidad y progresión.'),
            ('Parques y espacios deportivos','La variedad de espacios de la comuna amplía las posibilidades de movimiento cuando encajan con tu plan.'),
            ('Híbrido','Te permite combinar sesiones directas con trabajo guiado manteniendo una sola dirección.')],
        'context_kicker':'Más posibilidades','context_h2':'Más opciones alrededor de ti significan más formas de construir constancia.',
        'context_lead':'Las Condes reúne parques, infraestructura deportiva y distintas alternativas de movilidad. En vez de imponer un único escenario, usamos esa variedad para acercar el plan a tu vida.',
        'note_title':'Tu entorno ya tiene recursos','note_body':'Un gimnasio de edificio, un parque cercano, tu domicilio o la actividad que haces durante la semana pueden convertirse en parte útil del sistema cuando aportan a tu objetivo.',
        'decision_kicker':'Tu mejor combinación','decision_h2':'Elegimos contigo qué recursos merece la pena aprovechar.','decision_lead':'La calidad no depende de entrenar siempre en el mismo lugar, sino de que cada sesión tenga una intención clara dentro del plan.',
        'principles':[
            ('Lo que tienes cerca','Partimos de los espacios y opciones que ya están integrados en tu día para hacer el plan más personal.'),
            ('Cómo te mueves en tu semana','Tu actividad cotidiana aporta contexto para ajustar carga y recuperación.'),
            ('Dónde la supervisión suma más','Reservamos la presencia directa para lo que merece observarse y guiamos con claridad el resto del trabajo.')],
    },
    {
        'rel':'en/personal-trainer-las-condes/index.html','aliases':['Las Condes'],'description':'Personal training in Las Condes with assessment, planning and follow-up, making use of the variety of sports spaces, parks and mobility options around you.',
        'h1':'In Las Condes, having more options around you can work in favour of consistency.',
        'lead':'Parks, sports spaces, building gyms and different ways of moving through the commune create more possibilities to place training where it works best for you.',
        'support':'You do not have to fit one fixed format. We use your goals, routine and nearby resources to build a genuinely personal experience.',
        'meta':'In-person in Las Condes · Different spaces to train · Hybrid for more flexibility · Online from anywhere.',
        'strip_aria':'Training options in Las Condes','strip':[
            ('At home','A direct option when you want the session to fit where everyday life already happens.'),
            ('Building gym','We use nearby equipment when it supports high-quality, progressive training.'),
            ('Parks and sports spaces','The variety of local spaces creates more movement options when they fit your plan.'),
            ('Hybrid','Combine direct sessions with guided work while keeping one clear direction.')],
        'context_kicker':'More possibilities','context_h2':'More options around you mean more ways to build consistency.',
        'context_lead':'Las Condes brings together parks, sports infrastructure and different mobility options. Instead of forcing one setting, we use that variety to bring the plan closer to your life.',
        'note_title':'Your surroundings already have useful resources','note_body':'A building gym, a nearby park, your home or the activity already present in your week can become useful parts of the system when they support your goal.',
        'decision_kicker':'Your best combination','decision_h2':'Together we choose which resources are worth using.','decision_lead':'Quality does not depend on always training in the same place. It depends on every session having a clear purpose within the plan.',
        'principles':[
            ('What is already close','We start from spaces and options that already fit your day so the plan feels more personal.'),
            ('How you move through the week','Everyday activity gives us context to calibrate workload and recovery.'),
            ('Where direct coaching adds most','We use in-person supervision where observation matters and guide the rest with the same clarity.')],
    },
    {
        'rel':'entrenador-personal-vitacura/index.html','aliases':['Vitacura'],'description':'Entrenamiento personal en Vitacura con diagnóstico, planificación y seguimiento, aprovechando su entorno residencial, parques, espacios verdes y opciones de movilidad activa.',
        'h1':'Vitacura ofrece un entorno verde y activo: hagamos que juegue a favor de tu plan.',
        'lead':'Barrios residenciales, parques, ciclovías y espacios para caminar o moverte al aire libre amplían las posibilidades de integrar el entrenamiento en tu rutina.',
        'support':'Domicilio, gimnasio de edificio, exterior o híbrido pueden formar parte del mismo plan según lo que disfrutas, lo que ya haces y lo que quieres conseguir.',
        'meta':'Presencial en Vitacura · Entorno verde y activo · Híbrido para combinar supervisión y autonomía · Online desde cualquier lugar.',
        'strip_aria':'Opciones para aprovechar tu entorno en Vitacura','strip':[
            ('Domicilio','Entrenar cerca de tu rutina puede ser una gran base cuando el espacio permite trabajar bien.'),
            ('Gimnasio de edificio','Aprovechamos el equipamiento disponible para convertir cercanía en constancia.'),
            ('Parques y movimiento exterior','Los espacios verdes pueden sumar variedad cuando encajan con tu objetivo y tus preferencias.'),
            ('Híbrido','Combina momentos de supervisión directa con autonomía guiada dentro del mismo plan.')],
        'context_kicker':'Tu entorno también suma','context_h2':'El lugar donde vives puede ser parte del entrenamiento, no solo el escenario.',
        'context_lead':'Vitacura ha desarrollado una identidad residencial y verde junto a opciones para caminar y pedalear. Si ese tipo de movimiento ya está en tu vida, lo incorporamos como contexto útil.',
        'note_title':'Movimiento cotidiano + entrenamiento con intención','note_body':'Caminar, pedalear o usar espacios verdes no sustituye un plan cuando necesitas uno; nos ayuda a entender mejor tu actividad total y a decidir dónde poner el estímulo que falta.',
        'decision_kicker':'Una experiencia propia','decision_h2':'Usamos tu entorno para darte más opciones, no más reglas.','decision_lead':'El plan puede cambiar de escenario sin perder criterio ni seguimiento.',
        'principles':[
            ('Tu espacio más cómodo','Casa, edificio o exterior pueden aportar si ayudan a entrenar con calidad y a disfrutar del proceso.'),
            ('Tu actividad cotidiana','Lo que ya haces caminando, en bici o al aire libre entra en la lectura global de tu semana.'),
            ('Supervisión donde aporta','Combinamos presencia y trabajo guiado para darte apoyo directo y autonomía sin romper el hilo del plan.')],
    },
    {
        'rel':'en/personal-trainer-vitacura/index.html','aliases':['Vitacura'],'description':'Personal training in Vitacura with assessment, planning and follow-up, making use of its residential setting, parks, green spaces and active-mobility options.',
        'h1':'Vitacura offers a green, active setting: let us make it work in favour of your plan.',
        'lead':'Residential neighbourhoods, parks, cycleways and places to walk or move outdoors create more ways to integrate training into your routine.',
        'support':'Home, a building gym, outdoor training or hybrid coaching can all belong to the same plan depending on what you enjoy, already do and want to achieve.',
        'meta':'In-person in Vitacura · Green, active surroundings · Hybrid to combine coaching and autonomy · Online from anywhere.',
        'strip_aria':'Ways to use your surroundings in Vitacura','strip':[
            ('At home','Training close to your routine can be a strong base when the space supports good work.'),
            ('Building gym','We use available equipment to turn proximity into consistency.'),
            ('Parks and outdoor movement','Green spaces can add variety when they fit your goal and preferences.'),
            ('Hybrid','Combine direct coaching with guided autonomy inside one plan.')],
        'context_kicker':'Your surroundings add value too','context_h2':'Where you live can be part of training, not just the backdrop.',
        'context_lead':'Vitacura has developed a residential, green character alongside options for walking and cycling. If that movement is already part of your life, it becomes useful planning context.',
        'note_title':'Everyday movement + purposeful training','note_body':'Walking, cycling or using green spaces does not replace a plan when you need one; it helps us understand total activity and decide where the missing stimulus belongs.',
        'decision_kicker':'A personal experience','decision_h2':'We use your surroundings to give you more options, not more rules.','decision_lead':'The setting can change without losing coaching quality or continuity.',
        'principles':[
            ('Your most comfortable space','Home, a building gym or outdoors can all add value when they support good training and enjoyment.'),
            ('Your everyday activity','Walking, cycling and outdoor movement are part of the overall reading of your week.'),
            ('Coaching where it adds value','We combine direct sessions and guided work so support and autonomy remain part of one plan.')],
    },
    {
        'rel':'entrenamiento-personal-providencia/index.html','aliases':['Providencia'],'description':'Entrenamiento personal en Providencia con diagnóstico, planificación y seguimiento, integrando movimiento cotidiano, espacios cercanos y una modalidad que encaje en tu vida urbana.',
        'h1':'En Providencia, moverte ya forma parte del día. Tu plan puede empezar desde ahí.',
        'lead':'Una comuna de escala caminable, conectada por ciclovías y con parques permite que la actividad cotidiana tenga un lugar real dentro de la planificación.',
        'support':'Si caminas, usas bicicleta, entrenas cerca de casa o te mueves mucho durante el día, todo eso suma información para construir el estímulo que realmente necesitas.',
        'meta':'Presencial en Providencia · Tu movimiento diario también cuenta · Híbrido para ampliar opciones · Online desde cualquier lugar.',
        'strip_aria':'Formas de integrar el entrenamiento en Providencia','strip':[
            ('Domicilio','Una forma de entrenar cerca de tu día a día con una sesión diseñada para tu objetivo.'),
            ('Gimnasio de edificio','El espacio que ya tienes a mano puede convertirse en una base estable para progresar.'),
            ('Parques y entorno urbano','Los espacios abiertos pueden complementar el plan cuando encajan con la sesión y contigo.'),
            ('Híbrido','Combina contacto directo y trabajo guiado para que el plan pueda acompañar semanas diferentes.')],
        'context_kicker':'La ciudad activa también cuenta','context_h2':'Tu movimiento diario puede convertirse en una ventaja para decidir mejor.',
        'context_lead':'Providencia apuesta por una movilidad a escala humana, con ciclovías y recorridos que facilitan caminar y pedalear. Para IBERFIT, ese movimiento es parte de tu contexto, no algo que queda fuera del plan.',
        'note_title':'No todo empieza al entrar a una sesión','note_body':'Los pasos, trayectos en bicicleta y actividad cotidiana ayudan a leer mejor tu semana. El entrenamiento añade lo que falta con una intención concreta.',
        'decision_kicker':'Entrenamiento que se integra','decision_h2':'Construimos sobre el movimiento que ya existe en tu vida.','decision_lead':'Así el plan se siente menos como una pieza aislada y más como una parte coherente de tu semana.',
        'principles':[
            ('Tu movimiento diario','Lo que ya haces aporta información para ajustar dosis, recuperación y prioridades.'),
            ('El espacio que mejor te acompaña','Casa, edificio o exterior pueden formar parte del plan si hacen más natural repetir una buena sesión.'),
            ('La supervisión que necesitas','Elegimos contigo qué conviene observar en directo y qué puedes realizar con autonomía bien guiada.')],
        'remove_next_plain':True,
    },
    {
        'rel':'en/personal-training-providencia/index.html','aliases':['Providencia'],'description':'Personal training in Providencia with assessment, planning and follow-up, integrating everyday movement, nearby spaces and a format that fits urban life.',
        'h1':'In Providencia, movement is already part of the day. Your plan can start there.',
        'lead':'A walkable, well-connected commune with cycleways and parks gives everyday activity a real place inside training planning.',
        'support':'If you walk, cycle, train close to home or simply move a lot through the day, that all gives us useful information for the stimulus you actually need.',
        'meta':'In-person in Providencia · Everyday movement counts too · Hybrid for more options · Online from anywhere.',
        'strip_aria':'Ways to integrate training in Providencia','strip':[
            ('At home','A way to train close to everyday life with a session designed around your goal.'),
            ('Building gym','A space already within reach can become a stable base for progress.'),
            ('Parks and urban spaces','Open spaces can complement the plan when they fit the session and your preferences.'),
            ('Hybrid','Combine direct contact and guided work so the same plan can follow different kinds of weeks.')],
        'context_kicker':'An active city counts too','context_h2':'Everyday movement can become an advantage for better decisions.',
        'context_lead':'Providencia promotes human-scale mobility through cycleways and routes that support walking and cycling. For IBERFIT, that movement is part of your context, not something outside the plan.',
        'note_title':'Training does not only begin when a session starts','note_body':'Steps, cycling trips and everyday activity help us read the week more accurately. Training then adds what is missing with a clear purpose.',
        'decision_kicker':'Training that integrates','decision_h2':'We build on the movement already present in your life.','decision_lead':'The plan feels less like a separate task and more like a coherent part of your week.',
        'principles':[
            ('Your everyday movement','What you already do helps us calibrate dose, recovery and priorities.'),
            ('The space that works with you','Home, a building gym or outdoors can belong to the plan when they make a good session easier to repeat.'),
            ('The coaching you need','Together we decide what benefits from direct observation and what you can perform with well-guided autonomy.')],
        'remove_next_plain':True,
    },
    {
        'rel':'personal-trainer-nunoa/index.html','aliases':['Ñuñoa','Nunoa'],'description':'Entrenamiento personal en Ñuñoa con diagnóstico, planificación y seguimiento, conectado con tu vida de barrio, el espacio que ya tienes y las formas de moverte que disfrutas.',
        'h1':'Ñuñoa tiene vida de barrio, plazas y parques: tu entrenamiento puede sentirse igual de cercano.',
        'lead':'Casas, departamentos, gimnasios de edificio, plazas y parques crean muchas maneras de integrar el entrenamiento sin separarlo de la vida que ya haces en tu barrio.',
        'support':'Partimos del espacio y la rutina que ya tienes para construir una forma de entrenar que puedas reconocer como tuya.',
        'meta':'Presencial en Ñuñoa · Barrio, plazas y parques como posibilidades · Híbrido para sumar autonomía · Online desde cualquier lugar.',
        'strip_aria':'Formas de entrenar cerca de tu vida en Ñuñoa','strip':[
            ('Casa o departamento','Partimos del espacio real que tienes y diseñamos la sesión para aprovecharlo bien.'),
            ('Gimnasio de edificio','El equipamiento cercano puede convertirse en una base práctica para progresar.'),
            ('Plazas, parques y exterior','La vida de barrio ofrece espacios que pueden sumar movimiento y variedad cuando encajan contigo.'),
            ('Híbrido','Combina momentos de supervisión con autonomía guiada para mantener una experiencia personal.')],
        'context_kicker':'Cerca de tu vida','context_h2':'Entrenar cerca de casa puede ser una fortaleza.',
        'context_lead':'Ñuñoa tiene una vida barrial muy vinculada a plazas, parques y actividad comunitaria. Ese entorno permite pensar el entrenamiento desde lugares y rutinas que ya te resultan familiares.',
        'note_title':'Que el plan se parezca a tu vida','note_body':'No necesitamos inventar una rutina completamente ajena a tu semana. Podemos construir desde tu espacio, tus recorridos, los lugares que disfrutas y el movimiento que ya existe.',
        'decision_kicker':'Una rutina reconocible','decision_h2':'Elegimos contigo una forma de entrenar que se sienta cercana.','decision_lead':'La mejor combinación es la que te permite progresar sin perder el vínculo con lo que disfrutas hacer.',
        'principles':[
            ('Tu espacio real','Casa, departamento, edificio o exterior pueden ser buenos puntos de partida cuando responden al objetivo.'),
            ('Lo que te gusta repetir','Las actividades y lugares que disfrutas ayudan a construir adherencia y una semana más propia.'),
            ('Cómo quieres estar acompañado','Presencial, híbrido u online ajustan el nivel de supervisión sin cambiar la dirección del plan.')],
        'remove_next_plain':True,
    },
    {
        'rel':'en/personal-trainer-nunoa/index.html','aliases':['Ñuñoa','Nunoa'],'description':'Personal training in Ñuñoa with assessment, planning and follow-up, connected to neighbourhood life, the space you already have and the ways you enjoy moving.',
        'h1':'Ñuñoa has neighbourhood life, plazas and parks: your training can feel just as close to home.',
        'lead':'Houses, apartments, building gyms, plazas and parks create many ways to integrate training without separating it from the life you already have in your neighbourhood.',
        'support':'We start with the space and routine you already have to build a way of training you can genuinely recognise as your own.',
        'meta':'In-person in Ñuñoa · Neighbourhood, plazas and parks as possibilities · Hybrid for more autonomy · Online from anywhere.',
        'strip_aria':'Ways to train close to everyday life in Ñuñoa','strip':[
            ('Home or apartment','We start from the space you actually have and design the session to use it well.'),
            ('Building gym','Nearby equipment can become a practical base for progression.'),
            ('Plazas, parks and outdoors','Neighbourhood life offers spaces that can add movement and variety when they fit you.'),
            ('Hybrid','Combine coaching moments with guided autonomy while keeping the experience personal.')],
        'context_kicker':'Close to real life','context_h2':'Training close to home can be a strength.',
        'context_lead':'Ñuñoa has a strong neighbourhood life connected to plazas, parks and community activity. That makes it possible to build training around places and routines that already feel familiar.',
        'note_title':'Let the plan look like your life','note_body':'We do not need to invent a routine completely separate from your week. We can build from your space, routes, favourite places and the movement already present.',
        'decision_kicker':'A routine you recognise','decision_h2':'Together we choose a way of training that feels close to you.','decision_lead':'The best combination is the one that helps you progress without losing connection to what you enjoy doing.',
        'principles':[
            ('Your real space','Home, apartment, building or outdoors can all be good starting points when they serve the goal.'),
            ('What you enjoy repeating','Activities and places you enjoy can support adherence and make the week feel more yours.'),
            ('How you want to be coached','In-person, hybrid and online adjust the level of supervision without changing the direction of the plan.')],
        'remove_next_plain':True,
    },
    {
        'rel':'entrenador-personal-lo-barnechea/index.html','aliases':['Lo Barnechea'],'description':'Entrenamiento personal en Lo Barnechea con diagnóstico, planificación y seguimiento, incorporando tu espacio, tu rutina y, si forma parte de tu vida, la actividad de montaña y al aire libre.',
        'h1':'En Lo Barnechea, la montaña y los espacios abiertos amplían lo que tu plan puede ser.',
        'lead':'Parques, cerros, senderos y espacios residenciales hacen posible combinar sesiones estructuradas con una vida activa al aire libre cuando eso forma parte de ti.',
        'support':'Si la montaña, la bicicleta, el trekking o el movimiento exterior ya están en tu vida, los incorporamos al plan para que sumen a tu objetivo en lugar de tratarlos como algo aparte.',
        'meta':'Presencial en Lo Barnechea · Actividad exterior integrada cuando forma parte de ti · Híbrido para ampliar opciones · Online desde cualquier lugar.',
        'strip_aria':'Formas de entrenar en Lo Barnechea','strip':[
            ('Domicilio','Tu propio espacio puede ser una base excelente para sesiones estructuradas y cómodas.'),
            ('Espacio residencial','Un gimnasio de edificio o espacio útil cercano puede integrarse en el plan con naturalidad.'),
            ('Montaña y exterior','Si ya forman parte de tu vida, los tratamos como actividad real que merece entrar en la planificación.'),
            ('Híbrido','Combina momentos de observación directa con trabajo guiado para darte más libertad sin perder criterio.')],
        'context_kicker':'Tu actividad también es contexto','context_h2':'Lo que haces fuera de la sesión puede ser una ventaja.',
        'context_lead':'Lo Barnechea ofrece parques, cerros y espacios abiertos donde muchas actividades pueden formar parte de una vida activa. Para IBERFIT, si están en tu semana, también forman parte de la lectura de carga y recuperación.',
        'note_title':'Montaña, bici o trekking: si son tuyos, entran en el plan','note_body':'No asumimos que debas hacer actividad exterior. Pero si ya la disfrutas, la incorporamos para equilibrar estímulos, recuperación y progresión con una visión completa de tu semana.',
        'decision_kicker':'Un plan que suma lo que ya disfrutas','decision_h2':'Integramos tu vida activa en vez de pedirte que la dejes fuera.','decision_lead':'Así las sesiones de entrenamiento y tus actividades favoritas pueden empujar en la misma dirección.',
        'principles':[
            ('Tu actividad exterior','Si caminas por cerros, pedaleas o haces trekking, ajustamos la planificación para que esa carga también cuente.'),
            ('Tu base de entrenamiento','Domicilio, espacio residencial o exterior se eligen por cómo apoyan tu objetivo y tus preferencias.'),
            ('Tu equilibrio de apoyo y autonomía','La modalidad híbrida permite observar, ajustar y después darte trabajo guiado que conviva con el resto de tu vida activa.')],
        'remove_next_plain':True,
    },
    {
        'rel':'en/personal-trainer-lo-barnechea/index.html','aliases':['Lo Barnechea'],'description':'Personal training in Lo Barnechea with assessment, planning and follow-up, incorporating your space, routine and, when it is already part of your life, mountain and outdoor activity.',
        'h1':'In Lo Barnechea, the mountains and open spaces can expand what your plan can be.',
        'lead':'Parks, hills, trails and residential spaces make it possible to combine structured sessions with an active outdoor life when that is already part of who you are.',
        'support':'If mountains, cycling, hiking or outdoor movement are already part of your life, we incorporate them into the plan so they support your goal rather than sit outside it.',
        'meta':'In-person in Lo Barnechea · Outdoor activity integrated when it is part of your life · Hybrid for more options · Online from anywhere.',
        'strip_aria':'Ways to train in Lo Barnechea','strip':[
            ('At home','Your own space can be an excellent base for structured, comfortable sessions.'),
            ('Residential space','A building gym or useful nearby space can fit naturally into the plan.'),
            ('Mountains and outdoors','If they are already part of your life, we treat them as real activity that belongs in planning.'),
            ('Hybrid','Combine direct observation with guided work to create more freedom without losing direction.')],
        'context_kicker':'Your activity is context too','context_h2':'What you do outside sessions can be an advantage.',
        'context_lead':'Lo Barnechea offers parks, hills and open spaces where many activities can be part of an active life. For IBERFIT, when they are in your week, they also belong in the reading of workload and recovery.',
        'note_title':'Mountains, cycling or hiking: if they are yours, they belong in the plan','note_body':'We never assume you should train outdoors. But if you already enjoy it, we integrate it to balance stimulus, recovery and progression across the whole week.',
        'decision_kicker':'A plan that adds what you already enjoy','decision_h2':'We integrate your active life instead of asking you to leave it outside.','decision_lead':'Structured training and the activities you enjoy can then move in the same direction.',
        'principles':[
            ('Your outdoor activity','If you hike, cycle or spend time on the hills, we account for that workload when planning the week.'),
            ('Your training base','Home, residential space or outdoors are chosen for how well they support your goals and preferences.'),
            ('Your balance of support and autonomy','Hybrid coaching lets us observe, adjust and then guide work that fits the rest of your active life.')],
        'remove_next_plain':True,
    },
]

# Protect contextual WhatsApp URLs exactly, while rebuilding only local editorial layers.
for cfg in PAGES:
    rel = cfg['rel']
    text = read(rel)
    wa_before = re.findall(r'https://wa\.me/[^\"]+', text)
    assert wa_before, f'{rel}: expected contextual WhatsApp links'

    text = set_meta_descriptions(text, cfg['description'])
    text = update_jsonld(text, cfg)
    text = update_hero(text, cfg)

    _, hero_end = hero_bounds(text)
    cs, ce = next_section_exact(text, hero_end, 'section')
    if cfg.get('combined'):
        text = text[:cs] + combined_section(cfg) + text[ce:]
    else:
        text = text[:cs] + context_section(cfg) + text[ce:]
        context_end = text.find('</section>', cs) + len('</section>')
        ds, de = next_section_exact(text, context_end, 'section section-cream')
        text = text[:ds] + decision_section(cfg) + text[de:]
        if cfg.get('remove_next_plain'):
            decision_end = text.find('</section>', ds) + len('</section>')
            ns = text.find('<section class="section">', decision_end)
            # Only remove a direct plain editorial section before the next compact/answer/CTA layer.
            next_other = min([x for x in [text.find('<section class="section compact-section"', decision_end), text.find('<section class="section answer-section"', decision_end), text.find('<section class="section cta-panel"', decision_end)] if x >= 0] or [10**9])
            if ns >= 0 and ns < next_other:
                _, ne = section_bounds(text, ns)
                text = text[:ns] + text[ne:]

    wa_after = re.findall(r'https://wa\.me/[^\"]+', text)
    assert wa_after == wa_before, f'{rel}: WhatsApp contract changed'
    write(rel, text)

# Changelog
changelog = ROOT / 'CHANGELOG.md'
old = changelog.read_text(encoding='utf-8')
entry = '''\n## 6.43.24 — Local opportunity layer (2026-09-28)\n- Rebuilt all seven local landing-page pairs (ES/EN) around verified local opportunities rather than deficits or logistical friction.\n- Peñalolén: neighbourhood life, parks, sport spaces and foothill context become optional planning assets.\n- La Reina: residential/green scale and foothill context become ways to keep training close to real life.\n- Las Condes: parks, sport infrastructure and mobility variety become a broader set of training options.\n- Vitacura: green residential setting, walking and cycling become useful total-activity context.\n- Providencia: human-scale walking/cycling and everyday movement are explicitly recognised inside planning.\n- Ñuñoa: neighbourhood life, plazas and parks support a closer, more recognisable training experience.\n- Lo Barnechea: mountain/outdoor activity is conditionally integrated when it is already part of the client’s life.\n- Service availability stays affirmative; WhatsApp URLs, canonical/hreflang architecture and IBERFIT modality truth are preserved.\n'''
if '## 6.43.24 — Local opportunity layer' not in old:
    changelog.write_text(old + entry, encoding='utf-8')

html_files = sorted(ROOT.rglob('*.html'))
assert len(html_files) == 33, len(html_files)
print('BUILD_V64324_LOCAL_OPPORTUNITY_OK', len(PAGES), len(html_files))
