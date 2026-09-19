from pathlib import Path
import re

ROOT = Path('candidate/v628')
VERSION = ROOT / 'VERSION'
CHANGELOG = ROOT / 'CHANGELOG.md'
BASE_VERSION = '6.43.3'
NEW_VERSION = '6.43.4'


def fail(msg):
    raise SystemExit(msg)


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel, text):
    (ROOT / rel).write_text(text, encoding='utf-8')


def sub1(text, pattern, replacement, label):
    out, n = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if n != 1:
        fail(f'{label}: expected 1 match, got {n}')
    return out


def humanise_hero(text, h1, lead, support, primary=None, secondary=None, label='hero'):
    pat = r'(<div class="hero-text">\s*<div class="eyebrow">.*?</div>)<h1>.*?</h1><p class="lead">.*?</p><p class="hero-support">.*?</p>'
    rep = rf'\1<h1>{h1}</h1><p class="lead">{lead}</p><p class="hero-support">{support}</p>'
    text = sub1(text, pat, rep, label)
    if primary:
        pat = r'(<div class="hero-actions"><a class="btn btn-primary btn-lg"[^>]*>).*?(</a>)'
        text = sub1(text, pat, rf'\1{primary}\2', label + ' primary CTA')
    if secondary:
        pat = r'(<div class="hero-actions"><a class="btn btn-primary btn-lg".*?</a><a class="btn btn-secondary btn-lg"[^>]*>).*?(</a>)'
        text = sub1(text, pat, rf'\1{secondary}\2', label + ' secondary CTA')
    return text


def humanise_answers(text, kicker, h2, lead, section_id, label):
    pat = rf'(<section class="section answer-section" id="{re.escape(section_id)}"><div class="container answer-shell"><div class="section-intro answer-intro reveal">)<div class="kicker">.*?</div><h2>.*?</h2><p class="lead">.*?</p>(</div>)'
    rep = rf'\1<div class="kicker">{kicker}</div><h2>{h2}</h2><p class="lead">{lead}</p>\2'
    return sub1(text, pat, rep, label)


def humanise_final_cta(text, kicker, h2, body, button, label):
    pat = r'(<section class="section cta-panel"><div class="container cta-panel-inner reveal"><div>)<div class="kicker">.*?</div><h2>.*?</h2><p>.*?</p>(</div><a class="btn btn-primary btn-lg"[^>]*>).*?(</a></div></section>)'
    rep = rf'\1<div class="kicker">{kicker}</div><h2>{h2}</h2><p>{body}</p>\2{button}\3'
    return sub1(text, pat, rep, label)


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        fail(f'{label}: expected 1 exact match, got {n}')
    return text.replace(old, new, 1)


if VERSION.read_text(encoding='utf-8').strip() != BASE_VERSION:
    fail(f'expected VERSION {BASE_VERSION}')

# ES — HOME
p = read('index.html')
p = humanise_hero(p, 'Entrenamiento personal con criterio.', 'Si quieres sentirte mejor, ganar fuerza o volver a entrenar con constancia, no necesitas saber de antemano qué plan te conviene.', 'Empezamos por entender tu punto de partida, tu tiempo y tu realidad. A partir de ahí construimos contigo un plan que podamos revisar y ajustar.', 'Quiero saber por dónde empezar', 'Cuéntanos qué buscas', 'home ES hero')
p = replace_once(p, 'Del punto de partida al siguiente ajuste.', 'Tu plan debería responder a lo que te pasa, no al revés.', 'home ES evidence heading')
p = replace_once(p, 'El método se ve en cosas concretas: una evaluación que deja una referencia, una planificación que puedes entender y una revisión que cambia el plan cuando hay una razón.', 'Por eso primero entendemos cómo llegas, después te damos una dirección clara y seguimos mirando contigo qué conviene mantener o cambiar.', 'home ES evidence lead')
p = humanise_answers(p, 'Dudas antes de empezar', 'Lo esencial, sin rodeos.', 'Qué hacemos, para qué sirve el IRI y cómo cambia el acompañamiento según tu realidad.', 'respuestas-rapidas', 'home ES answers')
p = humanise_final_cta(p, 'Cuando quieras', 'No tienes que tenerlo todo claro para empezar.', 'Cuéntanos qué buscas, qué te preocupa o qué te cuesta sostener. El primer paso es entender tu situación.', 'Cuéntanos tu caso', 'home ES final CTA')
write('index.html', p)

# ES — IRI
p = read('diagnostico-iri/index.html')
p = humanise_hero(p, 'Antes de decirte qué entrenar, queremos entender cómo estás hoy.', 'No es un examen ni tienes que llegar en forma. Es una conversación y una evaluación para saber desde dónde empezamos.', 'Miramos tu contexto, cómo te mueves y cómo respondes al esfuerzo para proponerte un comienzo que tenga sentido para ti.', 'Quiero entender mi punto de partida', 'Ver qué vamos a mirar', 'IRI ES hero')
p = replace_once(p, 'Información útil para decidir, no pruebas por acumular.', 'No vienes a demostrar nada. Venimos a entender qué necesitas.', 'IRI ES section heading')
p = humanise_answers(p, 'Dudas normales antes del IRI', 'Qué pasa en la evaluación y qué hacemos después.', 'Queremos que llegues sabiendo qué vamos a mirar, por qué lo miramos y cómo usamos esa información contigo.', 'respuestas-rapidas', 'IRI ES answers')
p = humanise_final_cta(p, 'Si no sabes por dónde empezar', 'Empezar bien no exige tener todas las respuestas.', 'El IRI nos ayuda a ordenar contigo el punto de partida y convertirlo en prioridades que puedas entender.', 'Quiero empezar por mi punto de partida', 'IRI ES final CTA')
write('diagnostico-iri/index.html', p)

# ES — METHOD
p = read('metodo/index.html')
p = humanise_hero(p, 'Tu plan puede cambiar. El criterio no.', 'Tu cuerpo, tu agenda y tu energía no son iguales todas las semanas. El entrenamiento tiene que poder responder a eso.', 'Por eso no seguimos una rutina por inercia: observamos, te explicamos lo que vemos y ajustamos contigo cuando hay una razón.', 'Ver cómo empezamos', 'Cuéntanos qué te preocupa', 'method ES hero')
p = replace_once(p, 'El método se reconoce en lo que cambia y en lo que se mantiene.', '¿Qué pasa cuando algo cambia?', 'method ES decision heading')
p = humanise_answers(p, 'Lo que quizá te estés preguntando', 'Cómo funciona el método cuando la vida real se mete en medio.', 'Dolor, cansancio, una semana complicada o un progreso más rápido de lo esperado: el método está para ayudarte a decidir qué hacer después.', 'respuestas-rapidas', 'method ES answers')
p = humanise_final_cta(p, 'Si quieres saber cómo encajaría en tu caso', 'No necesitas adaptarte a un método rígido.', 'Cuéntanos qué quieres conseguir y qué te está costando ahora. La estructura está para ayudarte, no para encajarte en una plantilla.', 'Cuéntanos tu situación', 'method ES final CTA')
write('metodo/index.html', p)

# ES — IN PERSON
p = read('presencial/index.html')
p = humanise_hero(p, 'Si te ayuda tener a alguien a tu lado, entrenamos contigo.', 'La supervisión presencial sirve para que no tengas que adivinar si lo estás haciendo bien: podemos observar, corregir y adaptar en el momento.', 'Buscamos un lugar y un horario que puedas sostener de verdad, no solo una sesión que funcione sobre el papel.', 'Quiero saber si hay cobertura para mí', 'Ver cómo trabajamos', 'in-person ES hero')
p = replace_once(p, 'La modalidad cambia la forma de entrenar. El servicio sigue siendo completo.', 'No vienes solo a cumplir una hora. Cada sesión forma parte de tu proceso.', 'in-person ES includes heading')
p = humanise_answers(p, 'Antes de decidir', '¿Necesitas presencial, híbrido u online?', 'La mejor modalidad es la que te da el apoyo que necesitas y que puedes sostener en tu vida real.', 'respuestas-rapidas', 'in-person ES answers')
p = humanise_final_cta(p, 'Si te lo estás preguntando', 'No tienes que decidir la modalidad solo.', 'Cuéntanos dónde entrenas, qué buscas y cuánto acompañamiento crees que necesitas. Lo vemos contigo.', 'Quiero orientación', 'in-person ES final CTA')
write('presencial/index.html', p)

# ES — HYBRID
p = read('hibrido/index.html')
p = humanise_hero(p, 'No tienes que elegir entre acompañamiento y flexibilidad.', 'Si algunas semanas necesitas que estemos contigo y otras prefieres entrenar por tu cuenta, podemos conectar ambas cosas sin perder el hilo.', 'Lo presencial se usa donde más aporta; el resto del proceso sigue guiado y revisado contigo.', 'Quiero saber si el híbrido encaja conmigo', 'Ver cómo trabajamos', 'hybrid ES hero')
p = replace_once(p, 'Lo presencial continúa cuando te vas.', 'Cuando termina la sesión presencial, no te quedas solo con una rutina.', 'hybrid ES app heading')
p = humanise_answers(p, 'Antes de decidir', '¿Y si no puedo hacerlo todo presencial?', 'El híbrido está pensado precisamente para combinar supervisión y autonomía sin convertirlo en dos planes separados.', 'respuestas-rapidas', 'hybrid ES answers')
p = humanise_final_cta(p, 'Si necesitas más flexibilidad', 'Podemos buscar contigo el equilibrio entre supervisión y autonomía.', 'Cuéntanos cómo es tu semana y qué parte te cuesta sostener. A partir de ahí vemos si el formato híbrido tiene sentido para ti.', 'Quiero orientación', 'hybrid ES final CTA')
write('hibrido/index.html', p)

# ES — ONLINE
p = read('online/index.html')
p = humanise_hero(p, 'Entrenar a distancia no debería sentirse como entrenar solo.', 'Sabes qué hacer, por qué lo haces y qué cambiar cuando algo no encaja. Nosotros seguimos el proceso contigo, aunque estemos lejos.', 'Adaptamos el plan a tu experiencia, tu material, tu tiempo y el lugar donde entrenas.', 'Quiero saber cómo sería mi plan online', 'Ver cómo trabajamos', 'online ES hero')
p = replace_once(p, 'Planificación, sesión y evolución están conectadas en un mismo entorno para que sepas qué toca, cómo registrarlo y qué cambia después.', 'Abres la app y encuentras lo que necesitas para entrenar hoy: qué toca, cómo hacerlo, qué registrar y qué revisaremos después.', 'online ES app lead')
p = replace_once(p, '<h3>Plan claro</h3><p>Sabes qué toca y con qué objetivo.</p>', '<h3>Antes de empezar</h3><p>Sabes qué toca y para qué lo estás haciendo.</p>', 'online ES rail 1')
p = replace_once(p, '<h3>Sesión guiada</h3><p>La ejecución conserva instrucciones y alternativas.</p>', '<h3>Mientras entrenas</h3><p>Tienes instrucciones y alternativas para no quedarte bloqueado si algo cambia.</p>', 'online ES rail 2')
p = replace_once(p, '<h3>Feedback útil</h3><p>Tu respuesta queda registrada sin añadir fricción innecesaria.</p>', '<h3>Cuando terminas</h3><p>Nos cuentas cómo fue sin convertir el seguimiento en una tarea pesada.</p>', 'online ES rail 3')
p = replace_once(p, '<h3>Revisión profesional</h3><p>El siguiente ajuste parte de lo que realmente ocurrió.</p>', '<h3>En la revisión</h3><p>Lo que realmente ocurrió nos ayuda a decidir contigo el siguiente ajuste.</p>', 'online ES rail 4')
p = humanise_answers(p, 'Antes de elegir online', '¿Voy a sentir que entreno solo?', 'La distancia cambia dónde entrenas, no cuánto entendemos y revisamos tu proceso.', 'respuestas-rapidas', 'online ES answers')
p = humanise_final_cta(p, 'Si necesitas flexibilidad', 'Tu ubicación no debería decidir la calidad de tu entrenamiento.', 'Cuéntanos dónde entrenas, con qué material cuentas y qué te gustaría conseguir. Te explicamos cómo podría funcionar contigo.', 'Quiero orientación online', 'online ES final CTA')
write('online/index.html', p)

# ES — ABOUT
p = read('sobre-iberfit/index.html')
p = humanise_hero(p, 'Detrás de IBERFIT hay método, pero también una forma muy humana de acompañarte.', 'Queremos que entiendas lo que haces, que puedas preguntar y que sientas que tu contexto importa de verdad.', 'La estructura nos ayuda a trabajar mejor. Nunca debería hacerte sentir como un número o un caso estándar.', 'Conocer cómo trabajamos', 'Cuéntanos qué buscas', 'about ES hero')
p = humanise_answers(p, 'Si quieres conocernos mejor', 'Por qué trabajamos así.', 'IBERFIT nace de una inquietud sencilla: que entrenar tenga sentido para la persona que está delante, no solo sobre el papel.', 'respuestas-rapidas', 'about ES answers')
p = humanise_final_cta(p, 'Si nuestra forma de trabajar conecta contigo', 'Podemos empezar por escucharte.', 'Cuéntanos qué buscas, qué has probado antes o qué te gustaría hacer de otra manera. A partir de ahí vemos juntos el siguiente paso.', 'Cuéntanos tu objetivo', 'about ES final CTA')
write('sobre-iberfit/index.html', p)

# ES — CONTACT
p = read('contacto/index.html')
p = humanise_hero(p, 'Cuéntanos qué buscas. No hace falta que sepas qué modalidad necesitas.', 'Puedes escribirnos con una idea clara, con una duda o simplemente con la sensación de que quieres empezar mejor.', 'Te ayudamos a ordenar el siguiente paso sin presión. Si te resulta más cómodo, el orientador prepara la conversación contigo.', 'Cuéntanos tu situación', 'Prefiero orientarme primero', 'contact ES hero')
p = replace_once(p, 'WhatsApp directo es siempre la opción principal.', 'Si prefieres hablar sin completar nada, escríbenos directamente.', 'contact ES direct note')
p = replace_once(p, 'Si te ayuda, prepara tu consulta en tres pasos.', 'Cuéntanos lo esencial y te ayudamos a ordenar la conversación.', 'contact ES orientador heading')
p = replace_once(p, 'No necesitas completarlo para hablar con IBERFIT. Solo sirve para ordenar el contexto si prefieres llegar a WhatsApp con la consulta preparada.', 'No es un examen ni tienes que saber qué opción elegir. Son tres pasos breves para que podamos entender mejor qué buscas antes de hablar.', 'contact ES orientador lead')
write('contacto/index.html', p)

# EN — HEROES
en_pages = {
    'en/index.html': dict(h1='Personal training. With purpose.', lead='If you want to feel better, get stronger or return to training consistently, you do not need to know in advance which plan is right for you.', support='We start by understanding your baseline, your time and your real life. From there, we build a plan with you and keep reviewing it as things change.', primary='Help me understand where to start', secondary='Tell us what you are looking for'),
    'en/iri-assessment/index.html': dict(h1='Before we tell you what to train, we want to understand where you are today.', lead='This is not an exam and you do not need to arrive fit. It is a conversation and an assessment to understand where we should begin.', support='We look at your context, how you move and how you respond to effort so the first step makes sense for you.', primary='Help me understand my starting point', secondary='See what we assess'),
    'en/method/index.html': dict(h1='Your plan can change. The reasoning should not.', lead='Your body, schedule and energy are not the same every week. Training needs to be able to respond to that.', support='That is why we do not follow a routine on autopilot: we observe, explain what we see and adjust with you when there is a reason.', primary='See how we start', secondary='Tell us what concerns you'),
    'en/in-person/index.html': dict(h1='If having someone beside you helps, we train with you.', lead='In-person coaching means you do not have to guess whether you are doing things well: we can observe, correct and adapt in the moment.', support='We look for a place and schedule you can genuinely sustain, not just a session that works on paper.', primary='Check whether I am in the coverage area', secondary='See how we work'),
    'en/hybrid/index.html': dict(h1='You do not have to choose between support and flexibility.', lead='Some weeks you may need us there with you; other weeks you may prefer to train independently. We can connect both without losing continuity.', support='In-person time is used where it adds most value; the rest of the process stays guided and reviewed with you.', primary='See if hybrid could fit me', secondary='See how we work'),
    'en/online/index.html': dict(h1='Training remotely should not feel like training alone.', lead='You know what to do, why you are doing it and what to change when something no longer fits. We stay involved in the process even when we are not in the same place.', support='We adapt the plan to your experience, equipment, time and training environment.', primary='See what my online plan could look like', secondary='See how we work'),
    'en/about/index.html': dict(h1='There is a method behind IBERFIT, but also a very human way of supporting you.', lead='We want you to understand what you are doing, feel free to ask questions and know that your context genuinely matters.', support='Structure helps us work better. It should never make you feel like a number or a standard case.', primary='See how we work', secondary='Tell us what you are looking for'),
    'en/contact/index.html': dict(h1='Tell us what you are looking for. You do not need to know which format you need.', lead='You can write with a clear goal, a question or simply the feeling that you want to start in a better way.', support='We help you work out the next step without pressure. If you prefer, the optional guide can help you prepare the conversation first.', primary='Tell us about your situation', secondary='Help me think it through first'),
}
for rel, cfg in en_pages.items():
    p = read(rel)
    p = humanise_hero(p, cfg['h1'], cfg['lead'], cfg['support'], cfg['primary'], cfg['secondary'], rel + ' hero')
    write(rel, p)

# EN — concern-led sections
p = read('en/index.html')
p = replace_once(p, 'From baseline to the next adjustment.', 'Your plan should respond to what is happening in your life, not the other way around.', 'home EN evidence heading')
p = replace_once(p, 'The method becomes visible in concrete things: an assessment that leaves a reference point, planning you can understand and review that changes the plan when there is a reason.', 'That is why we first understand where you are, then give you a clear direction and keep reviewing with you what should stay and what should change.', 'home EN evidence lead')
p = humanise_answers(p, 'Questions before you start', 'The essentials, without the jargon.', 'What we do, what the IRI is for and how support changes around your real life.', 'direct-answers', 'home EN answers')
p = humanise_final_cta(p, 'Whenever you are ready', 'You do not need to have everything figured out before you start.', 'Tell us what you want, what worries you or what has been hard to sustain. The first step is understanding your situation.', 'Tell us about your situation', 'home EN final CTA')
write('en/index.html', p)

p = read('en/iri-assessment/index.html')
p = replace_once(p, 'Useful information for decisions—not tests for the sake of testing.', 'You are not here to prove anything. We are here to understand what you need.', 'IRI EN section heading')
p = humanise_answers(p, 'Normal questions before the IRI', 'What happens in the assessment, and what happens afterwards.', 'We want you to arrive knowing what we will look at, why it matters and how we use that information with you.', 'direct-answers', 'IRI EN answers')
p = humanise_final_cta(p, 'If you are not sure where to start', 'Starting well does not require having all the answers.', 'The IRI helps us organise your starting point with you and turn it into priorities you can understand.', 'Start with my baseline', 'IRI EN final CTA')
write('en/iri-assessment/index.html', p)

p = read('en/method/index.html')
p = replace_once(p, 'The method is visible in what changes—and what stays consistent.', 'What happens when something changes?', 'method EN decision heading')
p = humanise_answers(p, 'What you may be wondering', 'How the method works when real life gets in the way.', 'Pain, fatigue, a difficult week or faster progress than expected: the method is there to help decide what should happen next.', 'direct-answers', 'method EN answers')
p = humanise_final_cta(p, 'If you want to know how this would fit your case', 'You should not have to fit yourself into a rigid method.', 'Tell us what you want to achieve and what is difficult right now. Structure is there to support you, not to force you into a template.', 'Tell us about your situation', 'method EN final CTA')
write('en/method/index.html', p)

p = read('en/in-person/index.html')
p = replace_once(p, 'The format changes how we train. The service remains complete.', 'You are not just showing up for an hour. Each session is part of your process.', 'in-person EN includes heading')
p = humanise_answers(p, 'Before you decide', 'Do you need in-person, hybrid or online support?', 'The best format is the one that gives you the support you need and can actually sustain in real life.', 'direct-answers', 'in-person EN answers')
p = humanise_final_cta(p, 'If you are wondering what fits', 'You do not have to choose the format on your own.', 'Tell us where you train, what you are aiming for and how much support you feel you need. We can work it out with you.', 'Help me choose', 'in-person EN final CTA')
write('en/in-person/index.html', p)

p = read('en/hybrid/index.html')
p = replace_once(p, 'In-person work continues after you leave.', 'When the in-person session ends, you are not left alone with a routine.', 'hybrid EN app heading')
p = humanise_answers(p, 'Before you decide', 'What if I cannot do everything in person?', 'Hybrid coaching is designed precisely to combine direct support and independence without turning them into two separate plans.', 'direct-answers', 'hybrid EN answers')
p = humanise_final_cta(p, 'If you need more flexibility', 'We can find the right balance between support and independence with you.', 'Tell us what your week looks like and what has been hard to sustain. Then we can see whether hybrid coaching makes sense for you.', 'Help me work it out', 'hybrid EN final CTA')
write('en/hybrid/index.html', p)

p = read('en/online/index.html')
p = replace_once(p, 'Planning, execution and progress stay connected in one environment, so you can see what is next, record what happened and understand what changes.', 'Open the app and you can see what you need for today: what to do, how to do it, what to record and what we will review afterwards.', 'online EN app lead')
p = replace_once(p, '<h3>Clear plan</h3><p>You know what is next and why.</p>', '<h3>Before you start</h3><p>You know what is next and why you are doing it.</p>', 'online EN rail 1')
p = replace_once(p, '<h3>Guided session</h3><p>Execution keeps instructions and practical alternatives.</p>', '<h3>While you train</h3><p>You have instructions and alternatives so a change does not leave you stuck.</p>', 'online EN rail 2')
p = replace_once(p, '<h3>Useful feedback</h3><p>Your response is recorded without unnecessary friction.</p>', '<h3>When you finish</h3><p>You can tell us how it went without turning follow-up into another chore.</p>', 'online EN rail 3')
p = replace_once(p, '<h3>Professional review</h3><p>The next adjustment starts from what actually happened.</p>', '<h3>At review</h3><p>What actually happened helps us decide the next adjustment with you.</p>', 'online EN rail 4')
p = humanise_answers(p, 'Before choosing online coaching', 'Will I feel like I am training alone?', 'Distance changes where you train, not how carefully we understand and review your process.', 'direct-answers', 'online EN answers')
p = humanise_final_cta(p, 'If you need flexibility', 'Your location should not determine the quality of your training.', 'Tell us where you train, what equipment you have and what you would like to achieve. We will explain how online coaching could work for you.', 'Ask about online coaching', 'online EN final CTA')
write('en/online/index.html', p)

p = read('en/about/index.html')
p = humanise_answers(p, 'If you want to know us better', 'Why we work this way.', 'IBERFIT grew from a simple concern: training should make sense for the person in front of us, not only on paper.', 'direct-answers', 'about EN answers')
p = humanise_final_cta(p, 'If this way of working resonates with you', 'We can start by listening.', 'Tell us what you want, what you have tried before or what you would like to do differently. From there, we can work out the next step together.', 'Tell us your goal', 'about EN final CTA')
write('en/about/index.html', p)

p = read('en/contact/index.html')
p = replace_once(p, 'Direct WhatsApp is always the main option.', 'If you would rather talk without filling anything in, just write to us directly.', 'contact EN direct note')
p = replace_once(p, 'If it helps, prepare your enquiry in three steps.', 'Tell us the essentials and we will help you organise the conversation.', 'contact EN guide heading')
p = replace_once(p, 'You do not need to complete it to speak with IBERFIT. It only helps organise your context if you prefer to arrive at WhatsApp with your enquiry prepared.', 'This is not a test and you do not need to know which option to choose. It is simply three short steps that help us understand what you are looking for before we talk.', 'contact EN guide lead')
write('en/contact/index.html', p)

VERSION.write_text(NEW_VERSION + '\n', encoding='utf-8')
entry = '''## 6.43.4 — Human-first editorial pass\n\n- Rewrites the eight core ES pages and their EN counterparts so visitor concerns come before service language or methodology.\n- Replaces generic hero and CTA wording with contextual actions that answer what a person is likely to be deciding at that point.\n- Reframes direct-answer introductions around normal pre-purchase concerns while preserving the underlying AEO questions and factual answers.\n- Humanises IRI, Method, In-person, Hybrid, Online, About and Contact without changing pricing, coverage, analytics, security, structured data or application evidence.\n- Keeps IBERFIT premium and precise while reducing institutional language where direct second-person language is clearer.\n\n'''
CHANGELOG.write_text(entry + CHANGELOG.read_text(encoding='utf-8'), encoding='utf-8')
print({'version': NEW_VERSION, 'corePages': 16})
