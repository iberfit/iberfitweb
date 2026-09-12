#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import quote
import re

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "candidate/v628/assets/app.v628.js"
CSS = ROOT / "candidate/v628/assets/styles.v628.css"
HOME_ES = ROOT / "candidate/v628/index.html"
HOME_EN = ROOT / "candidate/v628/en/index.html"
CONTACT_ES = ROOT / "candidate/v628/contacto/index.html"
CONTACT_EN = ROOT / "candidate/v628/en/contact/index.html"

MARKER = "/* V6.28 · estado semántico del dock móvil */"
BLOCK = r'''
/* V6.28 · estado semántico del dock móvil */
;document.addEventListener('DOMContentLoaded',()=>{
  const dock=document.querySelector('.device-dock');
  if(!dock)return;
  const page=(document.body.dataset.page||'').trim();
  const current={home:'home',iri:'iri',contact:'contact'}[page]||'';
  dock.querySelectorAll('[data-dock]').forEach(link=>{
    if(current&&link.dataset.dock===current)link.setAttribute('aria-current','page');
    else link.removeAttribute('aria-current');
  });
});
'''

BENCHMARK_CSS_MARKER = "/* V6.28 · arquitectura de decisión benchmark 120+ */"
BENCHMARK_CSS = r'''
/* V6.28 · arquitectura de decisión benchmark 120+ */
.intent-router{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:.75rem;
  margin:-1.2rem 0 2rem;
}
.intent-route{
  display:grid;
  gap:.28rem;
  min-height:118px;
  padding:1.05rem 1.1rem;
  border:1px solid rgba(31,61,43,.12);
  border-radius:18px;
  background:rgba(255,255,255,.54);
  transition:transform .2s ease,border-color .2s ease,background .2s ease,box-shadow .2s ease;
}
.intent-route>span{
  color:var(--gold);
  font-size:.65rem;
  font-weight:850;
  letter-spacing:.12em;
  text-transform:uppercase;
}
.intent-route>strong{
  color:var(--green);
  font-family:Iowan Old Style,Baskerville,Georgia,serif;
  font-size:1.08rem;
  line-height:1.16;
}
.intent-route>small{
  color:var(--muted);
  font-size:.78rem;
  line-height:1.45;
}
.modality-row--guided{
  grid-template-columns:minmax(170px,.58fr) minmax(145px,.64fr) minmax(270px,1.25fr) auto;
  align-items:start;
}
.modality-meta{
  display:grid;
  gap:.42rem;
  color:var(--muted);
  font-size:.82rem;
  line-height:1.45;
}
.modality-meta span{
  display:grid;
  grid-template-columns:7.7rem 1fr;
  gap:.65rem;
}
.modality-meta b{
  color:var(--green);
  font-size:.68rem;
  letter-spacing:.07em;
  text-transform:uppercase;
}
.orientador-reassurance{
  margin:1.05rem 0 0;
  padding:.85rem 1rem;
  border:1px solid rgba(217,181,104,.28);
  border-radius:16px;
  background:rgba(255,255,255,.08);
  color:rgba(255,255,255,.82);
  font-size:.84rem;
  line-height:1.5;
  position:relative;
  z-index:1;
}
.orientador-reassurance strong{color:var(--gold-light)}
#formatos{scroll-margin-top:110px}
@media(hover:hover) and (pointer:fine){
  .intent-route:hover{
    transform:translateY(-2px);
    border-color:rgba(184,151,58,.45);
    background:rgba(255,255,255,.82);
    box-shadow:0 14px 34px rgba(16,42,29,.1);
  }
}
@media(max-width:980px){
  .intent-router{grid-template-columns:1fr}
  .intent-route{min-height:0}
  .modality-row--guided{grid-template-columns:1fr}
  .modality-meta span{grid-template-columns:minmax(6.8rem,.34fr) 1fr}
}
@media(max-width:560px){
  .intent-router{margin:-.6rem 0 1.55rem}
  .intent-route{padding:.95rem 1rem;border-radius:16px}
  .modality-meta span{grid-template-columns:1fr;gap:.12rem}
  .orientador-reassurance{font-size:.8rem}
}
@media(prefers-reduced-motion:reduce){
  .intent-route{transition:none!important}
}
'''

PHONE = "56944040032"
GENERAL_MESSAGES = {
    CONTACT_ES: (
        "Hola IBERFIT, quiero recibir orientación sobre entrenamiento y saber qué opción puede encajar mejor conmigo.",
        ("Escribir a IBERFIT", "Prefiero escribir directamente"),
    ),
    CONTACT_EN: (
        "Hello IBERFIT, I would like guidance about training and which option might fit me best.",
        ("Message IBERFIT", "I would rather write directly"),
    ),
}

GUIDE_PREFIXES = (
    (
        "Hola IBERFIT, quiero recibir orientación inicial sobre el Diagnóstico IRI.",
        "Hola IBERFIT, completé el orientador y quiero saber qué opción de entrenamiento puede encajar mejor conmigo.",
    ),
    (
        "Hello IBERFIT, I would like initial guidance about the IRI Assessment.",
        "Hello IBERFIT, I completed the guide and would like to know which training option might fit me best.",
    ),
)

HOME_REPLACEMENTS = {
    HOME_ES: [
        (
            '<div class="section-intro reveal"><div class="kicker">Formas de trabajar</div><h2>La forma puede cambiar. El acompañamiento no.</h2></div><div class="modality-list">',
            '<div class="section-intro reveal"><div class="kicker">Formas de trabajar</div><h2>La forma puede cambiar. El acompañamiento no.</h2></div>'
            '<nav class="intent-router reveal" aria-label="Elige tu siguiente paso">'
            '<a class="intent-route" href="/diagnostico-iri/"><span>Quiero entender</span><strong>Mi punto de partida</strong><small>Empieza por el Diagnóstico IRI y convierte la evaluación en prioridades.</small></a>'
            '<a class="intent-route" href="#formatos"><span>Quiero comparar</span><strong>Las formas de entrenar</strong><small>Presencial, híbrida o a distancia según tu contexto y autonomía.</small></a>'
            '<a class="intent-route" href="/contacto/#orientador"><span>Prefiero orientación</span><strong>No sé qué opción me conviene</strong><small>Ordena tu consulta en tres pasos y decide después de hablar con IBERFIT.</small></a>'
            '</nav><div class="modality-list" id="formatos">',
        ),
        (
            '<article class="modality-row reveal"><div><span>Comunas seleccionadas de Santiago</span><h3>Presencial</h3></div><p>Supervisión directa en el espacio acordado.</p><a class="text-link" href="/presencial/">Conocer modalidad</a></article>',
            '<article class="modality-row modality-row--guided reveal"><div><span>Comunas seleccionadas de Santiago</span><h3>Presencial</h3></div><p>Supervisión directa en el espacio acordado.</p><div class="modality-meta"><span><b>Ideal si</b> valoras corrección inmediata y compartir el mismo espacio.</span><span><b>Cómo te acompañamos</b> supervisión directa y seguimiento dentro del mismo plan.</span></div><a class="text-link" href="/presencial/">Conocer modalidad</a></article>',
        ),
        (
            '<article class="modality-row reveal"><div><span>Según cobertura presencial</span><h3>Híbrida</h3></div><p>Combina supervisión directa y trabajo guiado a distancia.</p><a class="text-link" href="/hibrido/">Conocer modalidad</a></article>',
            '<article class="modality-row modality-row--guided reveal"><div><span>Según cobertura presencial</span><h3>Híbrida</h3></div><p>Combina supervisión directa y trabajo guiado a distancia.</p><div class="modality-meta"><span><b>Ideal si</b> quieres alternar momentos de supervisión directa con autonomía.</span><span><b>Cómo te acompañamos</b> conectamos las sesiones presenciales y el trabajo guiado en un mismo proceso.</span></div><a class="text-link" href="/hibrido/">Conocer modalidad</a></article>',
        ),
        (
            '<article class="modality-row reveal"><div><span>Desde cualquier lugar</span><h3>A distancia</h3></div><p>Planificación completa, sesiones guiadas y seguimiento remoto.</p><a class="text-link" href="/online/">Conocer modalidad</a></article>',
            '<article class="modality-row modality-row--guided reveal"><div><span>Desde cualquier lugar</span><h3>A distancia</h3></div><p>Planificación completa, sesiones guiadas y seguimiento remoto.</p><div class="modality-meta"><span><b>Ideal si</b> necesitas continuidad sin depender de una ubicación concreta.</span><span><b>Cómo te acompañamos</b> planificación, feedback y revisión con una dirección clara entre sesiones.</span></div><a class="text-link" href="/online/">Conocer modalidad</a></article>',
        ),
    ],
    HOME_EN: [
        (
            '<div class="section-intro reveal"><div class="kicker">Ways to work with IBERFIT</div><h2>The standard stays consistent. The training format changes.</h2></div><div class="modality-list">',
            '<div class="section-intro reveal"><div class="kicker">Ways to work with IBERFIT</div><h2>The standard stays consistent. The training format changes.</h2></div>'
            '<nav class="intent-router reveal" aria-label="Choose your next step">'
            '<a class="intent-route" href="/en/iri-assessment/"><span>I want to understand</span><strong>My starting point</strong><small>Start with the IRI Assessment and turn the evaluation into clear priorities.</small></a>'
            '<a class="intent-route" href="#formatos"><span>I want to compare</span><strong>The training formats</strong><small>In person, hybrid or online depending on context and autonomy.</small></a>'
            '<a class="intent-route" href="/en/contact/#orientador"><span>I would like guidance</span><strong>I am not sure what fits</strong><small>Organise your enquiry in three steps and decide after speaking with IBERFIT.</small></a>'
            '</nav><div class="modality-list" id="formatos">',
        ),
        (
            '<article class="modality-row reveal"><div><span>Selected areas of Santiago</span><h3>In person</h3></div><p>Direct supervision in the agreed training space.</p><a class="text-link" href="/en/in-person/">Explore this format</a></article>',
            '<article class="modality-row modality-row--guided reveal"><div><span>Selected areas of Santiago</span><h3>In person</h3></div><p>Direct supervision in the agreed training space.</p><div class="modality-meta"><span><b>Best if</b> you value immediate correction and sharing the same training space.</span><span><b>How we support you</b> direct supervision and ongoing review within the same plan.</span></div><a class="text-link" href="/en/in-person/">Explore this format</a></article>',
        ),
        (
            '<article class="modality-row reveal"><div><span>Where in-person coverage allows</span><h3>Hybrid</h3></div><p>Combines direct supervision with guided independent training.</p><a class="text-link" href="/en/hybrid/">Explore this format</a></article>',
            '<article class="modality-row modality-row--guided reveal"><div><span>Where in-person coverage allows</span><h3>Hybrid</h3></div><p>Combines direct supervision with guided independent training.</p><div class="modality-meta"><span><b>Best if</b> you want to alternate direct supervision with greater autonomy.</span><span><b>How we support you</b> in-person sessions and guided training stay connected within one process.</span></div><a class="text-link" href="/en/hybrid/">Explore this format</a></article>',
        ),
        (
            '<article class="modality-row reveal"><div><span>Worldwide</span><h3>Online</h3></div><p>Complete planning, guided sessions and remote review.</p><a class="text-link" href="/en/online/">Explore this format</a></article>',
            '<article class="modality-row modality-row--guided reveal"><div><span>Worldwide</span><h3>Online</h3></div><p>Complete planning, guided sessions and remote review.</p><div class="modality-meta"><span><b>Best if</b> you need continuity without depending on a specific location.</span><span><b>How we support you</b> planning, feedback and review keep a clear direction between sessions.</span></div><a class="text-link" href="/en/online/">Explore this format</a></article>',
        ),
    ],
}

CONTACT_REASSURANCE = {
    CONTACT_ES: (
        '<h2>Cuéntanos lo esencial en tres pasos.</h2><p class="lead">No intenta evaluarte ni darte una respuesta automática. Solo nos ayuda a empezar la conversación con un poco más de contexto.</p>',
        '<h2>Cuéntanos lo esencial en tres pasos.</h2><p class="lead">No intenta evaluarte ni darte una respuesta automática. Solo nos ayuda a empezar la conversación con un poco más de contexto.</p><p class="orientador-reassurance"><strong>Sin compromiso.</strong> Sirve para ordenar la conversación; no te obliga a contratar y no envía nada por sí solo.</p>',
    ),
    CONTACT_EN: (
        '<h2>Organise your enquiry in three steps.</h2><p class="lead">It does not replace the IRI Assessment or provide a prescription. It simply prepares a clearer first message.</p>',
        '<h2>Organise your enquiry in three steps.</h2><p class="lead">It does not replace the IRI Assessment or provide a prescription. It simply prepares a clearer first message.</p><p class="orientador-reassurance"><strong>No commitment.</strong> It only helps organise the conversation; it does not require you to buy anything and sends nothing by itself.</p>',
    ),
}


def general_whatsapp(message: str) -> str:
    return f"https://wa.me/{PHONE}?text={quote(message, safe='')}"


def replace_contact_links(path: Path, message: str, labels: tuple[str, ...]) -> int:
    if not path.is_file():
        raise SystemExit(f"No existe {path}")
    html = path.read_text("utf-8")
    target = general_whatsapp(message)
    total = 0
    for label in labels:
        pattern = re.compile(
            rf'(<a\b[^>]*\bhref=")https://wa\.me/{PHONE}\?text=[^"]+("[^>]*>{re.escape(label)}</a>)'
        )
        html, count = pattern.subn(rf'\1{target}\2', html)
        total += count
    path.write_text(html, encoding="utf-8")
    return total


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    if not path.is_file():
        raise SystemExit(f"No existe {path}")
    html = path.read_text("utf-8")
    count = html.count(old)
    if count != 1:
        raise SystemExit(f"{path}: {label} debía aparecer una vez y apareció {count}")
    path.write_text(html.replace(old, new, 1), encoding="utf-8")


if not APP.is_file():
    raise SystemExit(f"No existe {APP}")
if not CSS.is_file():
    raise SystemExit(f"No existe {CSS}")

source = APP.read_text("utf-8")
if MARKER in source:
    raise SystemExit("El postprocesado del dock ya estaba presente antes de aplicarlo")
if "data-dock=\"home\"" not in source or "data-dock=\"iri\"" not in source or "data-dock=\"contact\"" not in source:
    raise SystemExit("No se encontró la estructura esperada del dock móvil")

for old, new in GUIDE_PREFIXES:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"El prefijo dinámico del orientador debía aparecer una vez y apareció {count}: {old}")
    source = source.replace(old, new, 1)

APP.write_text(source.rstrip() + "\n" + BLOCK.lstrip(), encoding="utf-8")

result = APP.read_text("utf-8")
required = [
    MARKER,
    "aria-current','page",
    "{home:'home',iri:'iri',contact:'contact'}",
    GUIDE_PREFIXES[0][1],
    GUIDE_PREFIXES[1][1],
]
missing = [token for token in required if token not in result]
if missing:
    raise SystemExit("Postprocesado incompleto: " + ", ".join(missing))
for old, _ in GUIDE_PREFIXES:
    if old in result:
        raise SystemExit(f"Persistió un prefijo antiguo del orientador: {old}")

for path, replacements in HOME_REPLACEMENTS.items():
    for index, (old, new) in enumerate(replacements, start=1):
        replace_once(path, old, new, f"mejora de decisión Home #{index}")

for path, (old, new) in CONTACT_REASSURANCE.items():
    replace_once(path, old, new, "reaseguro del orientador")

css = CSS.read_text("utf-8")
if BENCHMARK_CSS_MARKER in css:
    raise SystemExit("La capa CSS del benchmark ya existía antes del postprocesado")
CSS.write_text(css.rstrip() + "\n\n" + BENCHMARK_CSS.strip() + "\n", encoding="utf-8")

for path, (message, labels) in GENERAL_MESSAGES.items():
    changed = replace_contact_links(path, message, labels)
    # Dos enlaces con el CTA principal y uno de escritura directa: tres por idioma.
    if changed != 3:
        raise SystemExit(f"{path}: se esperaban 3 enlaces generales de WhatsApp y se modificaron {changed}")
    html = path.read_text("utf-8")
    target = general_whatsapp(message)
    for label in labels:
        if f'>{label}</a>' not in html:
            raise SystemExit(f"{path}: falta el CTA esperado {label}")
    if html.count(target) != 3:
        raise SystemExit(f"{path}: el mensaje general no quedó exactamente en tres CTA")

validation = {
    HOME_ES: ("intent-router", 'id="formatos"', "modality-row--guided", "Prefiero orientación"),
    HOME_EN: ("intent-router", 'id="formatos"', "modality-row--guided", "I would like guidance"),
    CONTACT_ES: ("orientador-reassurance", "Sin compromiso."),
    CONTACT_EN: ("orientador-reassurance", "No commitment."),
}
for path, tokens in validation.items():
    html = path.read_text("utf-8")
    for token in tokens:
        if token not in html:
            raise SystemExit(f"{path}: falta la mejora benchmark esperada: {token}")
if BENCHMARK_CSS_MARKER not in CSS.read_text("utf-8"):
    raise SystemExit("No quedó registrada la capa CSS del benchmark")

print("Benchmark 120+: decisión Home, comparación de modalidades y orientador sin presión aplicados en ES/EN.")
print("Dock móvil: aria-current añadido. Contacto y orientador: intención de WhatsApp alineada en ES/EN.")
