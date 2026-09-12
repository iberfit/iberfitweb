#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "recovery/live-production/site"
DST = ROOT / "candidate/v628"

ES_REPORT = """<div aria-label="Ejemplo ilustrativo de Informe IRI" class="report-preview report-preview-v2 reveal">
<div class="report-head"><div><span>Ejemplo ilustrativo · datos ficticios</span><h3>Informe IRI · Línea de base</h3></div><div class="report-brand"><img alt="" aria-hidden="true" decoding="async" height="46" src="/assets/iberfit-isotipo-oficial.png" width="41"/></div></div>
<div class="report-profile report-profile-v2"><div class="report-status"><small>Evaluación inicial</small><strong>Línea de base</strong><span>Punto de partida para futuras revisiones</span></div><div class="report-profile-copy"><span class="report-label">Objetivo de ejemplo</span><h4>Recuperar constancia y desarrollar fuerza</h4><div class="report-facts"><span><b>3</b> días disponibles</span><span><b>Intermedia</b> experiencia</span><span><b>4 semanas</b> primera revisión</span></div></div></div>
<div class="report-metrics report-metrics-v2"><div class="report-metric report-metric-priority"><div><span>Movilidad y control</span><strong>Prioridad inicial</strong></div><small>La calidad de movimiento orienta selección, rango y progresión de ejercicios.</small></div><div class="report-metric"><div><span>Fuerza por patrones</span><strong>Base funcional</strong></div><small>Se registra por patrones y protocolo, sin resumir dimensiones distintas en una sola cifra.</small></div><div class="report-metric"><div><span>Acondicionamiento</span><strong>Referencia inicial</strong></div><small>La respuesta al esfuerzo y la recuperación se interpretan según el protocolo utilizado.</small></div><div class="report-metric"><div><span>Composición corporal</span><strong>Referencia</strong></div><small>La bioimpedancia se interpreta como una medición contextual y no como un diagnóstico médico.</small></div></div>
<div aria-label="Ejemplo ilustrativo de composición corporal" class="report-bio"><div class="report-bio-head"><span>Composición corporal</span><small>Valores ficticios de bioimpedancia</small></div><div class="report-bio-grid"><div><small>Peso</small><strong>72,4 kg</strong></div><div><small>IMC</small><strong>24,1</strong></div><div><small>Grasa corporal</small><strong>16,8 %</strong></div><div><small>Masa muscular</small><strong>55,1 kg</strong></div><div><small>Agua corporal</small><strong>59,0 %</strong></div><div><small>Grasa visceral</small><strong>6</strong></div></div><p>Valores ilustrativos. La interpretación final depende de las condiciones de medición, del contexto y del conjunto de la evaluación IRI.</p></div>
<div class="report-actions"><div><small>Primera prioridad</small><strong>Movilidad y control</strong><p>Mejorar calidad de movimiento antes de aumentar la exigencia.</p></div><div><small>Inicio sugerido</small><strong>2–3 sesiones por semana</strong><p>Plan individual revisado y ajustado según la respuesta.</p></div></div>
<div class="report-comparison"><strong>Seguimiento longitudinal</strong><p>En una reevaluación, IBERFIT compara únicamente medidas obtenidas con protocolos compatibles. Si cambia el protocolo, el informe lo indica y evita presentar una evolución engañosa.</p></div>
<p class="report-disclaimer">Este ejemplo ficticio muestra cómo el IRI convierte información en decisiones. No representa a una persona real ni sustituye una valoración médica.</p>
</div>"""

EN_REPORT = """<div aria-label="Illustrative IRI Report" class="report-preview report-preview-v2 reveal">
<div class="report-head"><div><span>Illustrative case · fictional data</span><h3>IRI Report · Baseline</h3></div><div class="report-brand"><img alt="" aria-hidden="true" decoding="async" height="46" src="/assets/iberfit-isotipo-oficial.png" width="41"/></div></div>
<div class="report-profile report-profile-v2"><div class="report-status"><small>Initial assessment</small><strong>Baseline</strong><span>Starting point for future reviews</span></div><div class="report-profile-copy"><span class="report-label">Example goal</span><h4>Rebuild consistency and develop strength</h4><div class="report-facts"><span><b>3</b> available days</span><span><b>Intermediate</b> experience</span><span><b>4 weeks</b> first review</span></div></div></div>
<div class="report-metrics report-metrics-v2"><div class="report-metric report-metric-priority"><div><span>Mobility and control</span><strong>Initial priority</strong></div><small>Movement quality guides exercise selection, range and progression.</small></div><div class="report-metric"><div><span>Strength by movement pattern</span><strong>Functional baseline</strong></div><small>Recorded by movement pattern and protocol, keeping distinct dimensions separate.</small></div><div class="report-metric"><div><span>Conditioning</span><strong>Initial reference</strong></div><small>Response to effort and recovery are interpreted according to the protocol used.</small></div><div class="report-metric"><div><span>Body composition</span><strong>Reference</strong></div><small>Bioimpedance is interpreted in context and is not presented as a medical diagnosis.</small></div></div>
<div aria-label="Illustrative body composition snapshot" class="report-bio"><div class="report-bio-head"><span>Body composition</span><small>Illustrative bioimpedance values</small></div><div class="report-bio-grid"><div><small>Weight</small><strong>72.4 kg</strong></div><div><small>BMI</small><strong>24.1</strong></div><div><small>Body fat</small><strong>16.8%</strong></div><div><small>Muscle mass</small><strong>55.1 kg</strong></div><div><small>Body water</small><strong>59.0%</strong></div><div><small>Visceral fat</small><strong>6</strong></div></div><p>Illustrative values only. Final interpretation depends on measurement conditions, context and the full IRI assessment.</p></div>
<div class="report-actions"><div><small>First priority</small><strong>Mobility and control</strong><p>Improve movement quality before increasing training demand.</p></div><div><small>Suggested start</small><strong>2–3 sessions per week</strong><p>An individual plan reviewed and adjusted to your response.</p></div></div>
<div class="report-comparison"><strong>Longitudinal review</strong><p>At reassessment, IBERFIT compares only measures obtained with compatible protocols. If the protocol changes, the report states it and avoids presenting a misleading progression.</p></div>
<p class="report-disclaimer">This fictional example shows how the IRI turns information into decisions. It does not represent a real person and is not a medical assessment.</p>
</div>"""

CSS_ADD = """
/* V6.28 · Interacción accesible y vista longitudinal IRI. */
.brand-mark{width:auto!important;height:48px!important;aspect-ratio:173/192;object-fit:contain}
.sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
.lang-switch a{display:inline-flex;align-items:center;justify-content:center;min-height:36px;padding:.35rem .25rem}
.photo-story-copy > .kicker{color:#775b12}
/* Vista longitudinal IRI: consciente del protocolo y sin puntuación global. */
.report-preview-v2 .report-profile-v2{grid-template-columns:minmax(180px,.55fr) minmax(0,1fr)}
.report-status{align-self:stretch;display:flex;flex-direction:column;justify-content:center;padding:1rem 1.05rem;border-radius:18px;background:linear-gradient(145deg,#173827,#234d36);box-shadow:0 12px 28px rgba(20,43,30,.1)}
.report-status small{color:var(--gold-light);font-size:.62rem;font-weight:850;text-transform:uppercase;letter-spacing:.1em}
.report-status strong{margin:.3rem 0;color:#fff;font-family:"Iowan Old Style",Baskerville,Georgia,serif;font-size:1.35rem}
.report-status span{color:rgba(255,255,255,.72);font-size:.7rem;line-height:1.4}
.report-metrics-v2 .report-metric{grid-template-columns:1fr;padding:.72rem .55rem}
.report-metrics-v2 .report-metric>div{align-items:flex-start}
.report-metrics-v2 .report-metric>div strong{max-width:46%;text-align:right;font-family:inherit;font-size:.78rem;line-height:1.35}
.report-metrics-v2 .report-metric i{display:none}
.report-metrics-v2 .report-metric small{grid-column:1;color:#66756b;line-height:1.45}
.report-comparison{margin-top:1rem;padding:1rem 1.05rem;border:1px solid rgba(184,151,58,.28);border-radius:16px;background:rgba(184,151,58,.07)}
.report-comparison strong{display:block;color:var(--green);font-size:.82rem;margin-bottom:.3rem}
.report-comparison p{margin:0;color:#5f6f65;font-size:.72rem;line-height:1.5}
@media(max-width:720px){.report-preview-v2 .report-profile-v2{grid-template-columns:1fr}.report-status{text-align:center}.report-metrics-v2 .report-metric>div{gap:.55rem}.report-metrics-v2 .report-metric>div strong{max-width:52%}}
@media(max-width:430px){.report-metrics-v2 .report-metric>div{display:grid}.report-metrics-v2 .report-metric>div strong{max-width:none;text-align:left}}

/* V6.28 · Ergonomía táctil premium y foco visible. */
a,button,[role="button"],select,input,textarea{touch-action:manipulation}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{
  outline:3px solid rgba(184,151,58,.58);
  outline-offset:3px;
}
.lang-switch a{min-width:44px;min-height:44px;padding:.5rem .55rem;border-radius:999px}
.menu-toggle{min-height:44px}
.consent-close{width:44px;height:44px}
.consent-link{display:inline-flex;align-items:center;min-height:44px;padding:.65rem}
.consent-actions .btn,.consent-dialog .btn{min-height:44px}
.choice-chip{min-height:48px}
@media(max-width:720px){.device-dock a{min-width:44px;min-height:52px}}
@media(max-width:430px){input,select,textarea{font-size:16px}}
@media(hover:none){.btn:hover{transform:none}}
@media(prefers-reduced-motion:reduce){
  .reveal{opacity:1!important;transform:none!important}
}
"""

HEADERS = """/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://connect.facebook.net; connect-src 'self' https://www.google-analytics.com https://region1.google-analytics.com https://analytics.google.com https://www.facebook.com; img-src 'self' data: https://www.facebook.com; style-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'

/assets/analytics-config.js
  Cache-Control: no-store
  Content-Type: text/javascript; charset=utf-8

/assets/styles.v628.css
  Cache-Control: public, max-age=31536000, immutable
  Content-Type: text/css; charset=utf-8

/assets/app.v628.js
  Cache-Control: public, max-age=31536000, immutable
  Content-Type: text/javascript; charset=utf-8

/assets/analytics.v628.js
  Cache-Control: public, max-age=31536000, immutable
  Content-Type: text/javascript; charset=utf-8

/assets/*.webp
  Cache-Control: public, max-age=2592000
  Content-Type: image/webp

/assets/*.png
  Cache-Control: public, max-age=2592000
  Content-Type: image/png

/assets/*.ico
  Cache-Control: public, max-age=2592000
  Content-Type: image/x-icon

/manifest.webmanifest
  Cache-Control: public, max-age=0, must-revalidate
  Content-Type: application/manifest+json; charset=utf-8

/*.html
  Cache-Control: public, max-age=0, must-revalidate

/
  Cache-Control: public, max-age=0, must-revalidate
"""

REDIRECTS = """# Cloudflare Pages redirects
/diagnostico-iri.html /diagnostico-iri/ 301
/metodo.html /metodo/ 301
/presencial.html /presencial/ 301
/hibrido.html /hibrido/ 301
/online.html /online/ 301
/sobre.html /sobre-iberfit/ 301
/sobre-iberfit.html /sobre-iberfit/ 301
/contacto.html /contacto/ 301
/privacidad.html /privacidad/ 301
/en.html /en/ 301
"""

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1=0; self.lang=None; self.title=""; self.in_title=False
        self.desc=None; self.canonical=None; self.styles=[]; self.scripts=[]
        self.refs=[]; self.official_mark=False
    def handle_starttag(self, tag, attrs_list):
        attrs={k:(v or "") for k,v in attrs_list}
        if tag=="html": self.lang=attrs.get("lang")
        if tag=="h1": self.h1 += 1
        if tag=="title": self.in_title=True
        if tag=="meta" and attrs.get("name","").lower()=="description": self.desc=attrs.get("content")
        if tag=="link":
            if attrs.get("rel")=="canonical": self.canonical=attrs.get("href")
            if attrs.get("rel")=="stylesheet": self.styles.append(attrs.get("href",""))
        if tag=="script" and attrs.get("src"): self.scripts.append(attrs["src"])
        if tag=="img" and attrs.get("src") in {"/assets/iberfit-isotipo-96.png","/assets/iberfit-isotipo-192.png"}:
            self.official_mark=True
        for key in ("href","src"):
            if attrs.get(key): self.refs.append(attrs[key])
        if attrs.get("srcset"):
            self.refs.extend(x.strip().split()[0] for x in attrs["srcset"].split(",") if x.strip())
    def handle_endtag(self, tag):
        if tag=="title": self.in_title=False
    def handle_data(self, data):
        if self.in_title: self.title += data

def localize_spanish(text: str) -> str:
    pairs = (
        ('"description":"In-person services in selected areas"','"description":"Servicios presenciales en comunas seleccionadas"'),
        ('"name":"Worldwide"','"name":"Cobertura internacional"'),
        ('"description":"Online personal training"','"description":"Entrenamiento personal a distancia"'),
        ('"name":"Diagnóstico IBERFIT IRI / IRI Assessment"','"name":"Diagnóstico IBERFIT IRI"'),
        ('"areaServed":"Selected areas of Santiago"','"areaServed":"Comunas seleccionadas de Santiago"'),
        ('"areaServed":"Santiago and remote support"','"areaServed":"Santiago y acompañamiento a distancia"'),
        ('"name":"Online personal training","areaServed":"Worldwide"','"name":"Entrenamiento personal a distancia","areaServed":"Cobertura internacional"'),
    )
    for old,new in pairs:
        text=text.replace(old,new)
    text=text.replace("Online","A distancia").replace("online","a distancia")
    text=text.replace("/A distancia/","/online/").replace("/a distancia/","/online/")
    text=text.replace("modality_a distancia","modality_online")
    return text

def humanize_brand_voice(text: str, rel: str) -> str:
    """IBERFIT habla como marca: cercana, clara y profesional, nunca como marca personal."""
    common = {
        "La modalidad responde a tu contexto real.": "La modalidad tiene que encajar en tu vida real.",
        "Una semana ilustrativa, no una plantilla fija.": "Así podría verse una semana, pero la tuya no tiene por qué ser igual.",
        "La modalidad se recomienda después de entender el punto de partida.": "No elegimos la modalidad por comodidad ni por una plantilla: primero entendemos tu punto de partida.",
        "El Diagnóstico IRI ayuda a definir el nivel de supervisión y la forma de trabajo más coherentes.": "El Diagnóstico IRI nos ayuda a decidir contigo cuánta supervisión necesitas y qué forma de trabajo tiene más sentido.",
    }
    for old, new in common.items():
        text = text.replace(old, new)

    per_page = {
        "index.html": {
            "Evaluamos tu punto de partida, planificamos según tus necesidades y revisamos tu evolución para que cada decisión tenga un motivo.": "Antes de decirte qué hacer, queremos entender dónde estás. Evaluamos tu punto de partida, construimos un plan que tenga sentido para ti y lo vamos ajustando a medida que avanzas.",
            "Diagnóstico, planificación, control y seguimiento dentro de una misma experiencia.": "Tú ves el entrenamiento. Detrás hay diagnóstico, planificación, control y seguimiento para que no tengas que avanzar a ciegas.",
            "El plan se observa, se registra y se ajusta contigo.": "Tu plan cambia contigo.",
            "IBERFIT combina supervisión, herramientas de seguimiento y conversaciones claras para que sepas qué estás haciendo y por qué.": "Entrenar con IBERFIT significa saber qué estás haciendo, por qué lo haces y qué vamos a cambiar cuando tu cuerpo, tu semana o tus objetivos cambien.",
            "La evaluación termina en una recomendación, no en una lista de resultados.": "No queremos darte una hoja llena de datos. Queremos que salgas sabiendo qué conviene hacer ahora.",
            "Medir solo tiene valor cuando cambia una decisión.": "Medimos para tomar mejores decisiones, no para llenar gráficos.",
            "El estándar se mantiene. Cambia la forma de recibirlo.": "La forma puede cambiar. El acompañamiento no.",
            "El progreso se construye con un plan que también te ayuda a seguir.": "Avanzar también depende de sentir que el plan encaja contigo.",
        },
        "metodo/index.html": {
            "Una estructura profesional que reduce improvisación sin convertir a las personas en números. Cada decisión debe poder explicarse, registrarse y revisarse.": "No entrenas para encajar en un sistema. El sistema existe para que podamos explicarte cada decisión, recordar lo que ha pasado y ajustar sin improvisar.",
            "La estructura está para ayudarte, no para encasillarte.": "El método está para darte dirección, no para meterte en una plantilla.",
            "Cada sesión parte de una intención, utiliza la información necesaria y deja una base para decidir el siguiente paso.": "Cada sesión tiene una intención, pero también espacio para escuchar lo que está pasando ese día. Usamos la información que hace falta y dejamos registro de lo importante para decidir contigo el siguiente paso.",
            "El seguimiento no ocurre al final. Forma parte de cada vuelta.": "No esperamos al final para preguntarnos si está funcionando.",
            "La calidad no depende de recordar qué ocurrió la semana anterior.": "No queremos depender de la memoria para saber cómo vas.",
        },
        "sobre-iberfit/index.html": {
            "IBERFIT conecta evaluación, planificación, control y seguimiento para ayudarte a comprender tu punto de partida y avanzar hacia tus objetivos. Sabes qué estás trabajando, por qué se prioriza y cuándo conviene ajustar el plan.": "IBERFIT nace para que entrenar no sea seguir instrucciones que nadie te explica. Queremos que entiendas tu punto de partida, qué estamos priorizando y por qué el plan cambia cuando tú cambias.",
            "El centro del proceso eres tú: tu contexto, tus objetivos y tu evolución.": "IBERFIT tiene una forma de trabajar. El centro sigues siendo tú: tu contexto, tus objetivos, tus dudas y tu evolución.",
            "Una marca ordenada debe sentirse también en la forma de acompañar a cada persona.": "Queremos que esa claridad se note también en cómo te hablamos, cómo te explicamos el plan y cómo respondemos cuando algo cambia.",
            "Una forma más clara de avanzar hacia tus objetivos.": "IBERFIT nace de una convicción sencilla.",
            "IBERFIT nace de la experiencia de un entrenador español formado y con trayectoria profesional en Europa, donde desarrolló una forma de trabajar basada en evaluación, planificación, control y seguimiento.": "IBERFIT nace de una idea sencilla: entrenar bien no debería sentirse como seguir instrucciones que nadie te explica.",
            "Ese enfoque se traduce en un servicio pensado para comprender tu punto de partida, definir prioridades claras y adaptar el entrenamiento a tus objetivos, tu contexto y tu evolución.": "Después de formarse y trabajar profesionalmente en Europa, su fundador llega a Chile con una forma de hacer las cosas ya muy clara: evaluar antes de prescribir, planificar con criterio, observar la respuesta y ajustar cuando hace falta.",
            "No se trata de recibir una rutina genérica, sino de contar con una dirección clara, saber qué estás trabajando y poder ajustar el proceso cuando sea necesario.": "En Chile, esa forma de trabajar toma el nombre de IBERFIT: una marca con método, pero cercana. Queremos que entiendas lo que hacemos contigo, que puedas preguntar y que el plan tenga sentido en tu vida real.",
        },
        "diagnostico-iri/index.html": {
            "Una evaluación estructurada que convierte información relevante en prioridades y decisiones prácticas. No busca etiquetarte. Busca orientar el primer plan y dejar una base para revisar la evolución.": "Antes de proponerte un plan, queremos conocerte un poco mejor. El IRI reúne la información que realmente puede ayudarnos a decidir contigo cómo empezar y deja una base clara para revisar cómo vas evolucionando.",
            "La evaluación inicial reúne contexto, composición corporal y capacidades físicas. Después se interpreta contigo y se convierte en prioridades concretas.": "La evaluación reúne tu contexto, algunas medidas y capacidades físicas. Pero los datos no se quedan en una pantalla: los comentamos contigo y los convertimos en prioridades que puedas entender.",
            "Recibes una lectura que conecta resultados, prioridades y próximos pasos.": "Queremos que salgas sabiendo qué conviene priorizar y cuál es el siguiente paso.",
        },
        "contacto/index.html": {
            "Puedes escribir directamente o utilizar el orientador breve para ordenar la consulta. No pedimos datos personales en el orientador. Tus respuestas solo se incorporan al mensaje si decides abrir WhatsApp.": "Puedes escribirnos directamente, aunque todavía no tengas claro qué modalidad necesitas. Si prefieres ordenar un poco la idea, el orientador breve te ayuda a preparar el mensaje sin pedirte datos personales. Nada se envía hasta que tú decides abrir WhatsApp.",
            "Ordena tu consulta en tres pasos.": "Cuéntanos lo esencial en tres pasos.",
            "No reemplaza el Diagnóstico IRI ni emite una prescripción. Prepara un mensaje inicial más claro.": "No intenta evaluarte ni darte una respuesta automática. Solo nos ayuda a empezar la conversación con un poco más de contexto.",
            "La vía más directa.": "Si prefieres hablar directamente, estamos aquí.",
        },
        "presencial/index.html": {
            "Sesiones presenciales con planificación individual, control técnico y seguimiento entre decisiones. Disponible en comunas seleccionadas de Santiago, según sector, horario y condiciones del espacio.": "Si necesitas que estemos ahí contigo, la sesión presencial permite ver, corregir y adaptar en el momento. Antes de empezar confirmamos que la ubicación, el horario y el espacio tengan sentido para ti.",
            "La sesión presencial facilita ajustar técnica, carga y variantes en el momento, sin perder la continuidad del plan.": "Estar contigo en la sesión nos permite corregir a tiempo, ajustar la carga y ver detalles que a veces no se cuentan con palabras.",
            "Si la logística dificulta sostener la frecuencia, la modalidad híbrida u a distancia puede ofrecer más continuidad.": "Si la logística hace difícil mantener la frecuencia, la modalidad híbrida o a distancia puede darte más continuidad.",
        },
        "hibrido/index.html": {
            "Combina sesiones presenciales estratégicas con trabajo independiente claramente pautado y revisado. La parte presencial depende de cobertura. La planificación y el seguimiento continúan entre sesiones.": "Hay momentos en los que vernos en persona aporta mucho y otros en los que lo importante es que puedas entrenar por tu cuenta sin quedarte sin dirección. La modalidad híbrida conecta ambas cosas.",
            "Las sesiones estratégicas, el trabajo autónomo y la revisión quedan coordinados para que entrenar por tu cuenta no signifique hacerlo sin dirección.": "Lo que haces por tu cuenta sigue formando parte del mismo plan: sabes qué toca, por qué y qué revisaremos después.",
        },
        "online/index.html": {
            "Dirección profesional desde cualquier lugar.": "Estar lejos no debería significar entrenar sin dirección.",
            "Planificación individual, sesiones guiadas y seguimiento estructurado sin depender de una ubicación concreta. Disponible para cualquier persona, con independencia de su país, ciudad o experiencia previa.": "Te damos un plan claro, lo adaptamos a tu entorno y revisamos contigo lo que va pasando, estés donde estés. No necesitas vivir cerca ni tener experiencia avanzada.",
            "El registro y el feedback orientan los ajustes periódicos.": "Lo que nos cuentas y lo que registras nos ayuda a decidir qué mantener y qué cambiar.",
        },
    }

    for old, new in per_page.get(rel, {}).items():
        text = text.replace(old, new)
    return text


def enrich_structured_data(text: str, rel: str) -> str:
    """Añade semántica específica por página sin inventar datos operativos."""
    pattern = re.compile(
        r'(<script[^>]+type="application/ld\+json"[^>]*>)(.*?)(</script>)',
        re.I | re.S,
    )
    match = pattern.search(text)
    if not match:
        return text

    try:
        payload = json.loads(match.group(2))
    except json.JSONDecodeError:
        return text

    graph = payload.get("@graph")
    if not isinstance(graph, list):
        return text

    if rel == "index.html":
        canonical = "https://iberfit.cl/"
    else:
        canonical = "https://iberfit.cl/" + rel.removesuffix("index.html")

    parser = PageParser()
    parser.feed(text)
    title = parser.title.strip() or "IBERFIT"
    description = (parser.desc or "").strip()

    page_id = canonical + "#webpage"
    breadcrumb_items = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "IBERFIT",
            "item": "https://iberfit.cl/",
        }
    ]

    page_name = title.split("|")[0].strip()
    if canonical != "https://iberfit.cl/":
        breadcrumb_items.append(
            {
                "@type": "ListItem",
                "position": 2,
                "name": page_name,
                "item": canonical,
            }
        )

    graph.append(
        {
            "@type": "WebPage",
            "@id": page_id,
            "url": canonical,
            "name": page_name,
            "description": description,
            "isPartOf": {"@id": "https://iberfit.cl/#website"},
            "about": {"@id": "https://iberfit.cl/#business"},
            "inLanguage": "en" if rel.startswith("en/") else "es",
        }
    )
    graph.append(
        {
            "@type": "BreadcrumbList",
            "@id": canonical + "#breadcrumb",
            "itemListElement": breadcrumb_items,
        }
    )

    service_pages = {
        "diagnostico-iri/index.html": {
            "name": "Diagnóstico IBERFIT IRI",
            "description": description,
            "offers": {
                "@type": "Offer",
                "price": "30000",
                "priceCurrency": "CLP",
                "url": canonical,
            },
        },
        "presencial/index.html": {
            "name": "Entrenamiento personal presencial",
            "description": description,
            "areaServed": {"@type": "City", "name": "Santiago"},
        },
        "hibrido/index.html": {
            "name": "Entrenamiento personal híbrido",
            "description": description,
            "areaServed": {"@type": "City", "name": "Santiago"},
        },
        "online/index.html": {
            "name": "Entrenamiento personal a distancia",
            "description": description,
            "areaServed": {"@type": "Place", "name": "Cobertura internacional"},
        },
    }

    local_pages = {
        "entrenador-personal-las-condes/index.html": "Las Condes",
        "entrenador-personal-vitacura/index.html": "Vitacura",
        "entrenamiento-personal-providencia/index.html": "Providencia",
        "personal-trainer-nunoa/index.html": "Ñuñoa",
        "entrenador-personal-lo-barnechea/index.html": "Lo Barnechea",
        "entrenador-personal-la-reina/index.html": "La Reina",
        "entrenador-personal-penalolen/index.html": "Peñalolén",
    }
    if rel in local_pages:
        comuna = local_pages[rel]
        service_pages[rel] = {
            "name": f"Entrenamiento personal en {comuna}",
            "description": description,
            "areaServed": {"@type": "AdministrativeArea", "name": comuna},
        }

    service = service_pages.get(rel)
    if service:
        graph.append(
            {
                "@type": "Service",
                "@id": canonical + "#service",
                **service,
                "url": canonical,
                "provider": {"@id": "https://iberfit.cl/#business"},
            }
        )
        graph[-3]["mainEntity"] = {"@id": canonical + "#service"}

    if rel == "contacto/index.html":
        graph[-2]["@type"] = "ContactPage"

    payload["@graph"] = graph
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return text[:match.start()] + match.group(1) + encoded + match.group(3) + text[match.end():]


def differentiate_local_page(text: str, rel: str) -> str:
    """Reduce repetición entre landings locales usando solo contenido ya respaldado por cada página."""
    variants = {
        "entrenador-personal-las-condes/index.html": {
            "Entrenamiento personal en Las Condes con una propuesta realista.": "Entrenar en Las Condes: espacio, horarios y continuidad.",
            "No todas las personas necesitan la misma combinación.": "La modalidad depende del espacio y de cómo encaja en tu semana.",
            "La cobertura se confirma de forma individual.": "Primero confirmamos sector, espacio y horario.",
            "Consulta disponibilidad en Las Condes.": "Revisa cobertura y horarios en Las Condes.",
        },
        "entrenador-personal-vitacura/index.html": {
            "Entrenamiento personal en Vitacura con una propuesta realista.": "Entrenar en Vitacura: supervisión y continuidad según tu agenda.",
            "No todas las personas necesitan la misma combinación.": "La combinación adecuada depende de tu autonomía y disponibilidad.",
            "La cobertura se confirma de forma individual.": "La disponibilidad se revisa junto con acceso y entorno.",
            "Consulta disponibilidad en Vitacura.": "Consulta una modalidad viable en Vitacura.",
        },
        "entrenamiento-personal-providencia/index.html": {
            "Entrenamiento personal en Providencia con una propuesta realista.": "Entrenar en Providencia: una modalidad que funcione con tu rutina.",
            "No todas las personas necesitan la misma combinación.": "Domicilio, edificio o distancia: elegimos lo sostenible.",
            "La cobertura se confirma de forma individual.": "La cobertura se revisa junto con tiempos y acceso.",
            "Consulta disponibilidad en Providencia.": "Busca una opción sostenible en Providencia.",
        },
        "personal-trainer-nunoa/index.html": {
            "Entrenamiento personal en Ñuñoa con una propuesta realista.": "Entrenar en Ñuñoa: decidir el plan después de evaluar.",
            "No todas las personas necesitan la misma combinación.": "El Diagnóstico IRI orienta la modalidad antes de contratar.",
            "La cobertura se confirma de forma individual.": "Primero revisamos sector, objetivo y entorno.",
            "Consulta disponibilidad en Ñuñoa.": "Define tu punto de partida en Ñuñoa.",
        },
        "entrenador-personal-lo-barnechea/index.html": {
            "Entrenamiento personal en Lo Barnechea con una propuesta realista.": "Entrenar en Lo Barnechea: coordinar bien para sostener el plan.",
            "No todas las personas necesitan la misma combinación.": "La frecuencia presencial debe ser compatible con la logística.",
            "La cobertura se confirma de forma individual.": "Sector y desplazamiento se confirman antes de reservar.",
            "Consulta disponibilidad en Lo Barnechea.": "Revisa viabilidad presencial en Lo Barnechea.",
        },
        "entrenador-personal-la-reina/index.html": {
            "Entrenamiento personal en La Reina con una propuesta realista.": "Entrenar en La Reina: aprovechar el entorno sin improvisar.",
            "No todas las personas necesitan la misma combinación.": "El espacio y tu autonomía determinan la mejor combinación.",
            "La cobertura se confirma de forma individual.": "Antes de reservar, validamos espacio y disponibilidad.",
            "Consulta disponibilidad en La Reina.": "Consulta cobertura y modalidad en La Reina.",
        },
        "entrenador-personal-penalolen/index.html": {
            "Entrenamiento personal en Peñalolén con una propuesta realista.": "Entrenar en Peñalolén: continuidad cuando la logística importa.",
            "No todas las personas necesitan la misma combinación.": "La distancia puede cambiar la frecuencia, no el seguimiento.",
            "La cobertura se confirma de forma individual.": "Primero revisamos sector y frecuencia posible.",
            "Consulta disponibilidad en Peñalolén.": "Encuentra una frecuencia sostenible en Peñalolén.",
        },
    }
    for old, new in variants.get(rel, {}).items():
        text = text.replace(old, new)

    meta_descriptions = {
        "entrenador-personal-las-condes/index.html": "Entrenamiento personal en Las Condes según sector, espacio y horarios, con diagnóstico, planificación y seguimiento IBERFIT.",
        "entrenador-personal-vitacura/index.html": "Entrenamiento personal en Vitacura con opciones presenciales e híbridas según acceso, disponibilidad y nivel de autonomía.",
        "entrenamiento-personal-providencia/index.html": "Entrenamiento personal en Providencia con modalidad presencial, híbrida o a distancia según acceso, rutina y tiempos de traslado.",
        "personal-trainer-nunoa/index.html": "Entrenamiento personal en Ñuñoa con Diagnóstico IRI para definir modalidad, espacio, equipamiento y frecuencia de forma realista.",
        "entrenador-personal-lo-barnechea/index.html": "Entrenamiento personal en Lo Barnechea según sector y desplazamiento, con opciones híbridas para sostener continuidad y seguimiento.",
        "entrenador-personal-la-reina/index.html": "Entrenamiento personal en La Reina según espacio y disponibilidad, combinando supervisión, autonomía, planificación y seguimiento.",
        "entrenador-personal-penalolen/index.html": "Entrenamiento personal en Peñalolén según sector y frecuencia posible, con alternativas híbridas y a distancia para mantener continuidad.",
    }
    description = meta_descriptions.get(rel)
    if description:
        text = re.sub(
            r'(<meta\b(?=[^>]*\bname="description")[^>]*\bcontent=")[^"]*(")',
            lambda match: match.group(1) + description + match.group(2),
            text,
            count=1,
            flags=re.I,
        )

    text = text.replace(
        "Presencial, híbrido u a distancia se recomiendan por necesidad y contexto, no por una plantilla.",
        "Las modalidades presencial, híbrida o a distancia se recomiendan según la necesidad y el contexto, no por una plantilla.",
    )
    return text


def replace_spanish_report(text: str) -> str:
    start='<figure class="iri-showcase reveal">'
    s=text.index(start)
    e=text.index("</figure>",s)+len("</figure>")
    return text[:s]+ES_REPORT+text[e:]

def replace_english_report(text: str) -> str:
    start='<div aria-label="IRI Performance Report" class="report-preview reveal">'
    suffix='</div></div></section><section class="section decision-section">'
    s=text.index(start)
    e=text.index(suffix,s)+len("</div>")
    return text[:s]+EN_REPORT+text[e:]

def resolve_local(page: Path, value: str) -> Path|None:
    if not value or value.startswith(("#","mailto:","tel:","javascript:","data:")):
        return None
    parsed=urlparse(value)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    target=(DST/parsed.path.lstrip("/")) if parsed.path.startswith("/") else (page.parent/parsed.path)
    if parsed.path.endswith("/"): target=target/"index.html"
    return target.resolve()

def validate() -> None:
    errors=[]
    def fail(message): errors.append(message)
    html=sorted(DST.rglob("*.html"))
    if len(html)!=33: fail(f"Se esperaban 33 páginas HTML y hay {len(html)}")
    titles={}; descriptions={}
    forbidden=("overall index","overall score","iri global","índice global","indice global","puntuación global","puntuacion global","global score")
    for page in html:
        rel=page.relative_to(DST).as_posix()
        text=page.read_text("utf-8"); low=text.lower()
        p=PageParser(); p.feed(text)
        if p.h1!=1: fail(f"{rel}: H1={p.h1}")
        if p.lang not in {"es","en"}: fail(f"{rel}: idioma inválido")
        if not p.title.strip(): fail(f"{rel}: sin título")
        else: titles.setdefault(p.title.strip(),[]).append(rel)
        if not p.desc or len(p.desc.strip())<50: fail(f"{rel}: descripción débil")
        else: descriptions.setdefault(p.desc.strip(),[]).append(rel)
        if not p.canonical: fail(f"{rel}: sin canonical")
        if p.styles!=["/assets/styles.v628.css"]: fail(f"{rel}: CSS inesperado {p.styles}")
        expected={"/assets/analytics-config.js","/assets/analytics.v628.js","/assets/app.v628.js"}
        if not expected.issubset(set(p.scripts)): fail(f"{rel}: scripts comunes incompletos")
        if "/assets/iberfit-isotipo-oficial.png" not in p.refs: fail(f"{rel}: isotipo oficial canónico ausente")
        for ref in p.refs:
            target=resolve_local(page,ref)
            if target is not None and not target.exists(): fail(f"{rel}: recurso local ausente {ref}")
        for term in forbidden:
            if term in low: fail(f"{rel}: lenguaje IRI obsoleto: {term}")
        if not rel.startswith("en/") and rel!="404.html":
            visible=re.sub(r"<script\b[^>]*>.*?</script>"," ",text,flags=re.I|re.S)
            visible=re.sub(r"<[^>]+>"," ",visible)
            if re.search(r"\bonline\b",visible,flags=re.I): fail(f"{rel}: nombre comercial Online aún visible")
            if re.search(r"\bonline\b"," ".join((p.title,p.desc or "")),flags=re.I): fail(f"{rel}: Online aún en metadatos")
    for _,pages in titles.items():
        if len(pages)>1: fail(f"Título duplicado: {pages}")
    for _,pages in descriptions.items():
        if len(pages)>1: fail(f"Descripción duplicada: {pages}")
    for rel in ("index.html","diagnostico-iri/index.html","en/index.html","en/iri-assessment/index.html"):
        text=(DST/rel).read_text("utf-8")
        if "report-preview-v2" not in text or "report-comparison" not in text:
            fail(f"{rel}: vista IRI longitudinal ausente")

    structured_required = {
        "diagnostico-iri/index.html": ('"@type":"Service"', '"price":"30000"', '"priceCurrency":"CLP"'),
        "contacto/index.html": ('"@type":"ContactPage"',),
        "metodo/index.html": ('"@type":"BreadcrumbList"',),
        "online/index.html": ('"name":"Entrenamiento personal a distancia"',),
        "entrenador-personal-las-condes/index.html": ('"areaServed":{"@type":"AdministrativeArea","name":"Las Condes"}',),
    }
    for rel, markers in structured_required.items():
        source=(DST/rel).read_text("utf-8")
        for marker in markers:
            if marker not in source:
                fail(f"{rel}: dato estructurado ausente {marker}")
        if '"description":""' in source:
            fail(f"{rel}: descripción vacía en datos estructurados")
    for old in ("iri-report-preview-es-1448.webp","iri-report-preview-es-768.webp","iri-report-preview-es.png"):
        if (DST/"assets"/old).exists(): fail(f"Recurso IRI antiguo presente: {old}")
    for asset in DST.rglob("*"):
        if asset.is_file() and asset.suffix.lower() in {".html",".css",".js",".json",".webmanifest",".md",".txt"}:
            source=asset.read_text("utf-8",errors="ignore")
            for legacy in (
                "iberfit-isotipo-96.png",
                "iberfit-isotipo-192.png",
                "iberfit-isotipo-verde-96.png",
                "iberfit-isotipo-verde-192.png",
            ):
                if legacy in source:
                    fail(f"{asset.relative_to(DST)}: referencia a isotipo legado {legacy}")

    headers=(DST/"_headers").read_text("utf-8")
    if "/assets/styles.v628.css" not in headers: fail("_headers no referencia styles.v628.css")
    if "styles.v625.css" in headers or "styles.v626.css" in headers: fail("_headers conserva CSS antiguo")
    if "Content-Security-Policy" not in headers: fail("CSP ausente")
    for rel in ("index.html","en/index.html","sobre-iberfit/index.html","en/about/index.html"):
        if "https://share.google/xZmHR5R4JZzDFQcli" not in (DST/rel).read_text("utf-8"):
            fail(f"{rel}: fuente de reseñas Google ausente")
    if (DST/"VERSION").read_text("utf-8").strip()!="6.28": fail("VERSION no es 6.28")
    if errors:
        raise SystemExit("QA V6.28 FAIL\n- "+"\n- ".join(errors))
    print(f"QA V6.28 PASS · {len(html)} páginas · 0 errores")

def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"No existe la captura certificada: {SRC}")
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC,DST)

    # Cloudflare transforma robots.txt en el borde; el repositorio conserva la política fuente.
    (DST/"robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: https://iberfit.cl/sitemap.xml\n",encoding="utf-8")

    # Fijar el isotipo oficial exacto aportado por IBERFIT.
    official_logo = ROOT / "brand/Isotipo_IBERFIT_Oficial.png"
    if not official_logo.exists():
        raise SystemExit(f"No existe el isotipo oficial canónico: {official_logo}")
    shutil.copy2(official_logo, DST / "assets/iberfit-isotipo-oficial.png")

    old_css=DST/"assets/styles.v626.css"
    new_css=DST/"assets/styles.v628.css"
    new_css.write_bytes(old_css.read_bytes())
    old_css.unlink()
    with new_css.open("a",encoding="utf-8") as fh:
        fh.write("\n\n"+CSS_ADD)

    for name in (
        "iri-report-preview-es-1448.webp",
        "iri-report-preview-es-768.webp",
        "iri-report-preview-es.png",
        "iberfit-isotipo-96.png",
        "iberfit-isotipo-192.png",
        "iberfit-isotipo-verde-96.png",
        "iberfit-isotipo-verde-192.png",
    ):
        path=DST/"assets"/name
        if path.exists(): path.unlink()

    old_app_js = DST / "assets/app.v623.js"
    app_js = DST / "assets/app.v628.js"
    app_text = old_app_js.read_text("utf-8")
    app_text = app_text.replace("/assets/iberfit-isotipo-96.png","/assets/iberfit-isotipo-oficial.png")
    app_text = app_text.replace("/assets/iberfit-isotipo-192.png","/assets/iberfit-isotipo-oficial.png")
    app_text += r"""
;document.addEventListener('DOMContentLoaded',()=>{const form=document.querySelector('[data-orientador-form]');if(!form)return;const isEn=(document.documentElement.lang||'').toLowerCase().startsWith('en');const status=form.querySelector('[data-orientador-status]');const steps=Array.from(form.querySelectorAll('[data-step]'));const result=form.querySelector('[data-orientador-result]');const copy=isEn?{step:'Step',of:'of',choose:'Choose a main goal to continue.',ready:'Your initial guidance is ready. Review it before opening WhatsApp.'}:{step:'Paso',of:'de',choose:'Selecciona un objetivo principal para continuar.',ready:'Tu orientación inicial está preparada. Revísala antes de abrir WhatsApp.'};const announce=message=>{if(status)status.textContent=message};const syncSteps=()=>{let activeIndex=0;steps.forEach((step,index)=>{const active=step.classList.contains('active');step.setAttribute('aria-hidden',String(!active));if(active)activeIndex=index});const active=steps[activeIndex];if(active?.classList.contains('active')){const title=active.querySelector('h3')?.textContent?.trim()||'';announce(`${copy.step} ${activeIndex+1} ${copy.of} ${steps.length}: ${title}`)}};const observer=new MutationObserver(syncSteps);steps.forEach(step=>observer.observe(step,{attributes:true,attributeFilter:['class']}));if(result){result.setAttribute('role','region');result.setAttribute('aria-live','polite');new MutationObserver(()=>{if(!result.hidden)announce(copy.ready)}).observe(result,{attributes:true,attributeFilter:['hidden','class']})}form.addEventListener('click',event=>{if(event.target.closest('[data-next-step]'))setTimeout(()=>{if(steps[0]?.classList.contains('active')&&!form.elements.objetivo?.value)announce(copy.choose)},0)});form.querySelectorAll('select').forEach(select=>{const grid=select.nextElementSibling;if(!grid?.classList.contains('choice-grid'))return;const buttons=Array.from(grid.querySelectorAll('.choice-chip'));const syncChoice=()=>buttons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.value===select.value)));buttons.forEach(button=>button.setAttribute('aria-pressed','false'));select.addEventListener('change',syncChoice);syncChoice()});syncSteps()});
"""
    app_js.write_text(app_text,encoding="utf-8")
    old_app_js.unlink()

    old_analytics_js = DST / "assets/analytics.v6211.js"
    analytics_js = DST / "assets/analytics.v628.js"
    analytics_text = old_analytics_js.read_text("utf-8")
    analytics_text = analytics_text.replace(
        "const parse = value => { try { return JSON.parse(value); } catch (_) { return null; } };\n  let consent = parse(localStorage.getItem(storageKey));",
        "const parse = value => { try { return JSON.parse(value); } catch (_) { return null; } };\n"
        "  const safeStorage = {\n"
        "    get(key){ try { return window.localStorage.getItem(key); } catch (_) { return null; } },\n"
        "    set(key,value){ try { window.localStorage.setItem(key,value); return true; } catch (_) { return false; } }\n"
        "  };\n"
        "  let consent = parse(safeStorage.get(storageKey));"
    )
    analytics_text = analytics_text.replace(
        "localStorage.setItem(storageKey, JSON.stringify(consent));",
        "safeStorage.set(storageKey, JSON.stringify(consent));"
    )
    analytics_js.write_text(analytics_text,encoding="utf-8")
    old_analytics_js.unlink()

    for page in sorted(DST.rglob("*.html")):
        rel=page.relative_to(DST).as_posix()
        text=page.read_text("utf-8")
        text=text.replace("/assets/styles.v626.css","/assets/styles.v628.css")
        text=text.replace("/assets/app.v623.js","/assets/app.v628.js")
        text=text.replace("/assets/analytics.v6211.js","/assets/analytics.v628.js")
        text=re.sub(
            r'(<img\b(?=[^>]*class="brand-mark")[^>]*?)height="48"([^>]*?)width="48"',
            r'\1height="48"\2width="43"',
            text,
            flags=re.I,
        )
        text=text.replace("/assets/iberfit-isotipo-96.png","/assets/iberfit-isotipo-oficial.png")
        text=text.replace("/assets/iberfit-isotipo-192.png","/assets/iberfit-isotipo-oficial.png")
        text=text.replace("/assets/iberfit-isotipo-verde-96.png","/assets/iberfit-isotipo-oficial.png")
        text=text.replace("/assets/iberfit-isotipo-verde-192.png","/assets/iberfit-isotipo-oficial.png")
        text=text.replace("No invented overall score and no anonymous testimonials.","No invented aggregate rating and no anonymous testimonials.")
        if not rel.startswith("en/"):
            text=localize_spanish(text)
            text=differentiate_local_page(text, rel)
            text=humanize_brand_voice(text, rel)
        if rel in {"contacto/index.html","en/contact/index.html"}:
            text=text.replace(
                '<form class="orientador-card reveal" data-orientador-form="" novalidate="">',
                '<form class="orientador-card reveal" data-orientador-form="" novalidate=""><p class="sr-only" data-orientador-status="" aria-live="polite"></p>',
            )
        text=enrich_structured_data(text, rel)
        page.write_text(text,encoding="utf-8")

    for rel in ("index.html","diagnostico-iri/index.html"):
        p=DST/rel
        p.write_text(replace_spanish_report(p.read_text("utf-8")),encoding="utf-8")
    for rel in ("en/index.html","en/iri-assessment/index.html"):
        p=DST/rel
        p.write_text(replace_english_report(p.read_text("utf-8")),encoding="utf-8")

    (DST/"_headers").write_text(HEADERS,encoding="utf-8")
    (DST/"_redirects").write_text(REDIRECTS,encoding="utf-8")
    (DST/"VERSION").write_text("6.28\n",encoding="utf-8")
    (DST/"README.md").write_text(
        "# IBERFIT Web V6.28\n\n"
        "Candidata reproducible construida desde la V6.26 certificada en producción.\n\n"
        "No desplegar sin revisión visual real en móvil, tableta y escritorio.\n",
        encoding="utf-8",
    )
    (DST/"CHANGELOG.md").write_text(
        "# Cambios V6.28\n\n"
        "- Nombres comerciales visibles en castellano: Online pasa a A distancia; se conserva /online/ por compatibilidad.\n"
        "- IRI web alineado con IRI 2.0: línea de base, seguimiento longitudinal y sin puntuación global.\n"
        "- Informe IRI rasterizado antiguo sustituido por HTML accesible y adaptable.\n"
        "- Caché CSS corregida y versionada con styles.v628.css.\n"
        "- Controles automáticos contra regresiones de nomenclatura, IRI y versionado.\n",
        encoding="utf-8",
    )
    (DST/"IBERFIT_WEB_V6_28_CAMBIOS.md").write_text(
        "# IBERFIT WEB V6.28 · Candidata de recuperación\n\n"
        "Base certificada: producción V6.26 capturada desde iberfit.cl.\n\n"
        "## Gate pendiente\n"
        "Revisión visual real en móvil, tableta y escritorio sobre preview antes de cualquier promoción.\n",
        encoding="utf-8",
    )
    validate()

if __name__=="__main__":
    main()
