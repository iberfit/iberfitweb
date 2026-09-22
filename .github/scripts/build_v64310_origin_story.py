from pathlib import Path
import re

ROOT = Path('candidate/v628')
VERSION = ROOT / 'VERSION'
CHANGELOG = ROOT / 'CHANGELOG.md'
CSS = ROOT / 'assets/story.v64310.css'
ES = ROOT / 'sobre-iberfit/index.html'
EN = ROOT / 'en/about/index.html'

assert VERSION.read_text(encoding='utf-8').strip() == '6.43.8'
assert ES.exists() and EN.exists()

css = r'''/* IBERFIT WEB V6.43.10 — evocative institutional origin story */
body[data-page="about"] .origin-section{
  background:
    radial-gradient(circle at 8% 8%,rgba(217,181,104,.16),transparent 28rem),
    radial-gradient(circle at 88% 76%,rgba(217,181,104,.08),transparent 24rem),
    linear-gradient(145deg,#0a1d14,#153725 56%,#0d2519);
}
body[data-page="about"] .origin-section .founder-grid--journey{align-items:start}
body[data-page="about"] .origin-section .founder-copy{max-width:46rem}
body[data-page="about"] .origin-section .founder-copy p{
  color:rgba(255,255,255,.74);
  font-size:clamp(1rem,1.25vw,1.13rem);
  line-height:1.78;
}
body[data-page="about"] .origin-section .founder-copy p:first-child{
  color:#fff;
  font-family:Iowan Old Style,Baskerville,Georgia,serif;
  font-size:clamp(1.3rem,2vw,1.75rem);
  line-height:1.42;
  letter-spacing:-.018em;
}
.origin-manifesto{
  display:grid;
  grid-template-columns:minmax(120px,.28fr) minmax(0,1fr);
  gap:clamp(1.2rem,4vw,3rem);
  align-items:start;
  margin:clamp(2.5rem,6vw,5rem) 0;
  padding:clamp(1.6rem,4vw,2.8rem) 0;
  border-top:1px solid rgba(217,181,104,.28);
  border-bottom:1px solid rgba(217,181,104,.28);
}
.origin-manifesto>span{
  color:var(--gold-light,#d9b568);
  font-size:.68rem;
  font-weight:850;
  letter-spacing:.16em;
  text-transform:uppercase;
}
.origin-manifesto p{
  margin:0;
  max-width:34ch;
  color:#fff;
  font-family:Iowan Old Style,Baskerville,Georgia,serif;
  font-size:clamp(1.75rem,3.4vw,3.25rem);
  line-height:1.08;
  letter-spacing:-.035em;
}
@media(min-width:641px){
  body[data-page="about"] .brand-journey--story{
    gap:0;
    background:transparent;
    border:0;
    border-top:1px solid rgba(217,181,104,.3);
    border-radius:0;
    overflow:visible;
  }
  body[data-page="about"] .brand-journey--story article{
    position:relative;
    min-height:250px;
    padding:2rem 1.5rem 1.5rem;
    background:transparent;
    border-right:1px solid rgba(217,181,104,.16);
  }
  body[data-page="about"] .brand-journey--story article:last-child{border-right:0}
  body[data-page="about"] .brand-journey--story article:before{
    content:"";
    position:absolute;
    top:-5px;
    left:1.5rem;
    width:9px;
    height:9px;
    border-radius:50%;
    background:var(--gold-light,#d9b568);
    box-shadow:0 0 0 7px rgba(217,181,104,.08);
  }
  body[data-page="about"] .brand-journey--story .journey-current{
    background:linear-gradient(180deg,rgba(217,181,104,.10),transparent 78%);
  }
}
body[data-page="about"] .brand-journey--story .journey-phase{color:rgba(255,255,255,.62)}
body[data-page="about"] .brand-journey--story strong{font-size:clamp(1.45rem,2vw,1.8rem)}
body[data-page="about"] .brand-journey--story p{color:rgba(255,255,255,.64)!important;line-height:1.62!important}
body[data-page="about"] .journey-outro--story{
  display:grid;
  grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);
  gap:clamp(1.4rem,5vw,4rem);
  margin-top:clamp(2rem,5vw,4rem);
  padding-top:clamp(1.5rem,3vw,2.4rem);
  border-top:1px solid rgba(217,181,104,.2);
}
body[data-page="about"] .journey-outro--story p{
  margin:0;
  color:rgba(255,255,255,.68);
  line-height:1.72;
}
body[data-page="about"] .journey-outro--story p:first-child{
  color:#fff;
  font-family:Iowan Old Style,Baskerville,Georgia,serif;
  font-size:clamp(1.18rem,1.8vw,1.55rem);
  line-height:1.45;
}
@media(max-width:640px){
  .origin-manifesto{grid-template-columns:1fr;gap:.8rem;margin:2.2rem 0;padding:1.5rem 0}
  .origin-manifesto p{font-size:clamp(1.75rem,9vw,2.55rem)}
  body[data-page="about"] .brand-journey--story article:before{display:none}
  body[data-page="about"] .journey-outro--story{grid-template-columns:1fr;gap:1rem;margin-top:2rem}
}
'''

es_section = '''<section class="section origin-section"><div class="container"><div class="founder-grid founder-grid--journey"><div class="reveal"><div class="kicker">Nuestra historia</div><h2>Antes de ser un método, IBERFIT fue una inquietud: entender mejor para acompañar mejor.</h2></div><div class="founder-copy reveal"><p>IBERFIT no empieza con una rutina, sino con una pregunta que ha acompañado todo el recorrido de la marca: ¿cómo hacer que el entrenamiento tenga más sentido para la persona que lo vive?</p><p>De esa inquietud nace una búsqueda alrededor de la salud, el movimiento y el entrenamiento. La formación universitaria específica en España aporta una base sólida. El recorrido europeo por los contextos español y alemán amplía la mirada: distintas formas de entender la precisión, la constancia, el proceso y el acompañamiento. De vuelta en España, esas ideas se contrastan, se aplican y maduran. Más tarde, en Chile, todo ese recorrido se adapta a una nueva realidad y toma forma propia.</p></div></div><div class="origin-manifesto reveal"><span>Una convicción</span><p>El método solo merece la pena si ayuda a una persona real a entender, decidir y avanzar mejor.</p></div><div class="brand-journey brand-journey--editorial brand-journey--story reveal" aria-label="Recorrido que da origen a IBERFIT"><article><div class="journey-head"><div class="journey-meta"><span class="journey-step">01</span><span class="journey-phase">La base</span></div><img class="journey-flag-img" src="/assets/flag-es.svg" alt="" width="72" height="48" decoding="async"/></div><strong>España</strong><p>La formación universitaria aporta lenguaje, estructura y una base específica para comprender salud y entrenamiento con mayor profundidad.</p></article><article><div class="journey-head"><div class="journey-meta"><span class="journey-step">02</span><span class="journey-phase">La perspectiva</span></div><img class="journey-flag-img" src="/assets/flag-de.svg" alt="" width="72" height="48" decoding="async"/></div><strong>Alemania</strong><p>El contacto con otro contexto amplía la mirada y refuerza el valor de la precisión, la consistencia y el respeto por el proceso.</p></article><article><div class="journey-head"><div class="journey-meta"><span class="journey-step">03</span><span class="journey-phase">La maduración</span></div><img class="journey-flag-img" src="/assets/flag-es.svg" alt="" width="72" height="48" decoding="async"/></div><strong>España</strong><p>La experiencia acumulada se aplica, se contrasta y madura hasta convertirse en una forma de trabajar cada vez más propia.</p></article><article class="journey-current"><div class="journey-head"><div class="journey-meta"><span class="journey-step">04</span><span class="journey-phase">La forma propia</span></div><img class="journey-flag-img" src="/assets/flag-cl.svg" alt="" width="72" height="48" decoding="async"/></div><strong>Chile</strong><p>El recorrido se adapta a una nueva realidad y se convierte en IBERFIT: una marca propia que une método, cercanía y seguimiento.</p></article></div><div class="journey-outro journey-outro--story reveal"><p>De esa evolución nacen el Diagnóstico IRI, el seguimiento y las modalidades presencial, híbrida y online. No como productos aislados, sino como respuestas distintas a una misma pregunta: ¿qué necesita esta persona, hoy, para avanzar con sentido?</p><p>IBERFIT sigue creciendo desde esa idea: medir cuando aporta claridad, usar tecnología cuando ayuda, cambiar cuando la realidad cambia y conservar siempre lo que no debería perderse —criterio, conversación y humanidad.</p></div></div></section>'''

en_section = '''<section class="section origin-section"><div class="container"><div class="founder-grid founder-grid--journey"><div class="reveal"><div class="kicker">Our story</div><h2>Before it became a method, IBERFIT began with a question: how can we understand better in order to support better?</h2></div><div class="founder-copy reveal"><p>IBERFIT does not begin with a routine. It begins with a question that has followed the brand throughout its journey: how can training make more sense for the person actually living it?</p><p>That question grew into an ongoing interest in health, movement and training. Specialised university education in Spain provided a strong foundation. A European journey through Spanish and German contexts broadened the perspective, revealing different ways of understanding precision, consistency, process and support. Back in Spain, those ideas were applied, tested and allowed to mature. Later, in Chile, that entire journey adapted to a new reality and took on a form of its own.</p></div></div><div class="origin-manifesto reveal"><span>A conviction</span><p>A method is only worthwhile if it helps a real person understand, decide and move forward better.</p></div><div class="brand-journey brand-journey--editorial brand-journey--story reveal" aria-label="The journey that shaped IBERFIT"><article><div class="journey-head"><div class="journey-meta"><span class="journey-step">01</span><span class="journey-phase">The foundation</span></div><img class="journey-flag-img" src="/assets/flag-es.svg" alt="" width="72" height="48" decoding="async"/></div><strong>Spain</strong><p>University education provides language, structure and a specialised foundation for understanding health and training in greater depth.</p></article><article><div class="journey-head"><div class="journey-meta"><span class="journey-step">02</span><span class="journey-phase">Perspective</span></div><img class="journey-flag-img" src="/assets/flag-de.svg" alt="" width="72" height="48" decoding="async"/></div><strong>Germany</strong><p>Exposure to another context broadens the perspective and reinforces the value of precision, consistency and respect for the process.</p></article><article><div class="journey-head"><div class="journey-meta"><span class="journey-step">03</span><span class="journey-phase">Maturation</span></div><img class="journey-flag-img" src="/assets/flag-es.svg" alt="" width="72" height="48" decoding="async"/></div><strong>Spain</strong><p>The accumulated experience is applied, tested and refined until it becomes an increasingly distinct way of working.</p></article><article class="journey-current"><div class="journey-head"><div class="journey-meta"><span class="journey-step">04</span><span class="journey-phase">A form of its own</span></div><img class="journey-flag-img" src="/assets/flag-cl.svg" alt="" width="72" height="48" decoding="async"/></div><strong>Chile</strong><p>The journey adapts to a new reality and becomes IBERFIT: a distinct brand bringing together method, closeness and ongoing review.</p></article></div><div class="journey-outro journey-outro--story reveal"><p>That evolution gave rise to the IRI Assessment, ongoing review and in-person, hybrid and online training. Not as isolated products, but as different answers to the same question: what does this person need, today, to move forward with purpose?</p><p>IBERFIT continues to grow from the same idea: measure when it brings clarity, use technology when it helps, change when reality changes, and always preserve what should never be lost — judgement, conversation and humanity.</p></div></div></section>'''

pat = re.compile(r'<section class="section origin-section">.*?</section>', re.S)
for path, section, date_from, date_to in [
    (ES, es_section, '"dateModified":"2026-09-19"', '"dateModified":"2026-09-22"'),
    (EN, en_section, '"dateModified":"2026-09-19"', '"dateModified":"2026-09-22"'),
]:
    text = path.read_text(encoding='utf-8')
    assert '/assets/story.v64310.css' not in text
    assert len(pat.findall(text)) == 1, path
    text = pat.sub(section, text, count=1)
    text = text.replace(date_from, date_to, 1)
    text = text.replace('</head>', '<link href="/assets/story.v64310.css" rel="stylesheet"/></head>', 1)
    path.write_text(text, encoding='utf-8')

CSS.write_text(css, encoding='utf-8')
VERSION.write_text('6.43.10\n', encoding='utf-8')
entry = '''## V6.43.10 — Evocative institutional origin story\n\n- Rewrites the IBERFIT origin as an institutional story rather than a founder biography.\n- Preserves only verified pillars: passion for training and health, university education in Spain, Spanish and German contexts, later adaptation in Chile.\n- Connects the European journey directly to the present-day IRI, review process and training formats.\n- Refines the visual journey on desktop while preserving the existing swipe interaction on mobile.\n\n'''
old = CHANGELOG.read_text(encoding='utf-8')
if not old.startswith('## V6.43.10'):
    CHANGELOG.write_text(entry + old, encoding='utf-8')
print({'version':'6.43.10','pages':[str(ES),str(EN)],'asset':str(CSS)})
