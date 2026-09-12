#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "recovery/live-production/site"
DST = ROOT / "candidate/v628"

ES_REPORT = """<div aria-label="Ejemplo ilustrativo de Informe IRI" class="report-preview report-preview-v2 reveal">
<div class="report-head"><div><span>Ejemplo ilustrativo · datos ficticios</span><h3>Informe IRI · Línea de base</h3></div><div class="report-brand"><img alt="" aria-hidden="true" decoding="async" height="46" src="/assets/iberfit-isotipo-96.png" width="41"/></div></div>
<div class="report-profile report-profile-v2"><div class="report-status"><small>Evaluación inicial</small><strong>Línea de base</strong><span>Punto de partida para futuras revisiones</span></div><div class="report-profile-copy"><span class="report-label">Objetivo de ejemplo</span><h4>Recuperar constancia y desarrollar fuerza</h4><div class="report-facts"><span><b>3</b> días disponibles</span><span><b>Intermedia</b> experiencia</span><span><b>4 semanas</b> primera revisión</span></div></div></div>
<div class="report-metrics report-metrics-v2"><div class="report-metric report-metric-priority"><div><span>Movilidad y control</span><strong>Prioridad inicial</strong></div><small>La calidad de movimiento orienta selección, rango y progresión de ejercicios.</small></div><div class="report-metric"><div><span>Fuerza por patrones</span><strong>Base funcional</strong></div><small>Se registra por patrones y protocolo, sin resumir dimensiones distintas en una sola cifra.</small></div><div class="report-metric"><div><span>Acondicionamiento</span><strong>Referencia inicial</strong></div><small>La respuesta al esfuerzo y la recuperación se interpretan según el protocolo utilizado.</small></div><div class="report-metric"><div><span>Composición corporal</span><strong>Referencia</strong></div><small>La bioimpedancia se interpreta como una medición contextual y no como un diagnóstico médico.</small></div></div>
<div aria-label="Ejemplo ilustrativo de composición corporal" class="report-bio"><div class="report-bio-head"><span>Composición corporal</span><small>Valores ficticios de bioimpedancia</small></div><div class="report-bio-grid"><div><small>Peso</small><strong>72,4 kg</strong></div><div><small>IMC</small><strong>24,1</strong></div><div><small>Grasa corporal</small><strong>16,8 %</strong></div><div><small>Masa muscular</small><strong>55,1 kg</strong></div><div><small>Agua corporal</small><strong>59,0 %</strong></div><div><small>Grasa visceral</small><strong>6</strong></div></div><p>Valores ilustrativos. La interpretación final depende de las condiciones de medición, del contexto y del conjunto de la evaluación IRI.</p></div>
<div class="report-actions"><div><small>Primera prioridad</small><strong>Movilidad y control</strong><p>Mejorar calidad de movimiento antes de aumentar la exigencia.</p></div><div><small>Inicio sugerido</small><strong>2–3 sesiones por semana</strong><p>Plan individual revisado y ajustado según la respuesta.</p></div></div>
<div class="report-comparison"><strong>Seguimiento longitudinal</strong><p>En una reevaluación, IBERFIT compara únicamente medidas obtenidas con protocolos compatibles. Si cambia el protocolo, el informe lo indica y evita presentar una evolución engañosa.</p></div>
<p class="report-disclaimer">Este ejemplo ficticio muestra cómo el IRI convierte información en decisiones. No representa a una persona real ni sustituye una valoración médica.</p>
</div>"""

EN_REPORT = """<div aria-label="Illustrative IRI Report" class="report-preview report-preview-v2 reveal">
<div class="report-head"><div><span>Illustrative case · fictional data</span><h3>IRI Report · Baseline</h3></div><div class="report-brand"><img alt="" aria-hidden="true" decoding="async" height="46" src="/assets/iberfit-isotipo-96.png" width="41"/></div></div>
<div class="report-profile report-profile-v2"><div class="report-status"><small>Initial assessment</small><strong>Baseline</strong><span>Starting point for future reviews</span></div><div class="report-profile-copy"><span class="report-label">Example goal</span><h4>Rebuild consistency and develop strength</h4><div class="report-facts"><span><b>3</b> available days</span><span><b>Intermediate</b> experience</span><span><b>4 weeks</b> first review</span></div></div></div>
<div class="report-metrics report-metrics-v2"><div class="report-metric report-metric-priority"><div><span>Mobility and control</span><strong>Initial priority</strong></div><small>Movement quality guides exercise selection, range and progression.</small></div><div class="report-metric"><div><span>Strength by movement pattern</span><strong>Functional baseline</strong></div><small>Recorded by movement pattern and protocol, keeping distinct dimensions separate.</small></div><div class="report-metric"><div><span>Conditioning</span><strong>Initial reference</strong></div><small>Response to effort and recovery are interpreted according to the protocol used.</small></div><div class="report-metric"><div><span>Body composition</span><strong>Reference</strong></div><small>Bioimpedance is interpreted in context and is not presented as a medical diagnosis.</small></div></div>
<div aria-label="Illustrative body composition snapshot" class="report-bio"><div class="report-bio-head"><span>Body composition</span><small>Illustrative bioimpedance values</small></div><div class="report-bio-grid"><div><small>Weight</small><strong>72.4 kg</strong></div><div><small>BMI</small><strong>24.1</strong></div><div><small>Body fat</small><strong>16.8%</strong></div><div><small>Muscle mass</small><strong>55.1 kg</strong></div><div><small>Body water</small><strong>59.0%</strong></div><div><small>Visceral fat</small><strong>6</strong></div></div><p>Illustrative values only. Final interpretation depends on measurement conditions, context and the full IRI assessment.</p></div>
<div class="report-actions"><div><small>First priority</small><strong>Mobility and control</strong><p>Improve movement quality before increasing training demand.</p></div><div><small>Suggested start</small><strong>2–3 sessions per week</strong><p>An individual plan reviewed and adjusted to your response.</p></div></div>
<div class="report-comparison"><strong>Longitudinal review</strong><p>At reassessment, IBERFIT compares only measures obtained with compatible protocols. If the protocol changes, the report states it and avoids presenting a misleading progression.</p></div>
<p class="report-disclaimer">This fictional example shows how the IRI turns information into decisions. It does not represent a real person and is not a medical assessment.</p>
</div>"""

CSS_ADD = """
/* V6.28 · Vista longitudinal IRI: consciente del protocolo y sin puntuación global. */
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

/assets/app.v623.js
  Cache-Control: public, max-age=31536000, immutable
  Content-Type: text/javascript; charset=utf-8

/assets/analytics.v6211.js
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
        expected={"/assets/analytics-config.js","/assets/analytics.v6211.js","/assets/app.v623.js"}
        if not expected.issubset(set(p.scripts)): fail(f"{rel}: scripts comunes incompletos")
        if not p.official_mark: fail(f"{rel}: isotipo oficial ausente")
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
    for old in ("iri-report-preview-es-1448.webp","iri-report-preview-es-768.webp","iri-report-preview-es.png"):
        if (DST/"assets"/old).exists(): fail(f"Recurso IRI antiguo presente: {old}")
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

    old_css=DST/"assets/styles.v626.css"
    new_css=DST/"assets/styles.v628.css"
    new_css.write_bytes(old_css.read_bytes())
    old_css.unlink()
    with new_css.open("a",encoding="utf-8") as fh:
        fh.write("\n\n"+CSS_ADD)

    for name in ("iri-report-preview-es-1448.webp","iri-report-preview-es-768.webp","iri-report-preview-es.png"):
        path=DST/"assets"/name
        if path.exists(): path.unlink()

    for page in sorted(DST.rglob("*.html")):
        rel=page.relative_to(DST).as_posix()
        text=page.read_text("utf-8")
        text=text.replace("/assets/styles.v626.css","/assets/styles.v628.css")
        text=text.replace("No invented overall score and no anonymous testimonials.","No invented aggregate rating and no anonymous testimonials.")
        if not rel.startswith("en/"):
            text=localize_spanish(text)
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
