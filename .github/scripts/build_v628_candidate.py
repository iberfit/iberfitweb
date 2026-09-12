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
.consent-banner .btn-ghost{color:#fff;border-color:rgba(255,255,255,.45)}
.consent-banner .btn-ghost:hover{background:rgba(255,255,255,.08)}

/* V6.28 · Capa visual editorial premium */
html{scroll-padding-top:96px}
body{background:
  radial-gradient(circle at 8% 0%,rgba(184,151,58,.055),transparent 32rem),
  linear-gradient(180deg,#fbf8f1 0,#f7f4ee 42rem,#f7f4ee 100%)}
h1,h2{text-wrap:balance}
p{text-wrap:pretty}
.hero{padding-block:clamp(4.5rem,8vw,7.75rem) clamp(3.5rem,7vw,6rem)}
.hero-grid.hero-grid-no-media{max-width:1120px;position:relative}
.hero-grid-no-media .hero-text{max-width:970px;padding-left:clamp(1rem,3vw,2.5rem);border-left:1px solid rgba(184,151,58,.38)}
.hero-grid-no-media .hero-text:before{content:"";position:absolute;left:-1px;top:0;width:2px;height:clamp(3.5rem,8vw,6.5rem);background:linear-gradient(180deg,var(--gold),rgba(184,151,58,0))}
.hero-grid-no-media h1{max-width:14ch;font-size:clamp(3.35rem,7.1vw,7rem);line-height:.94;letter-spacing:-.052em}
.hero-grid-no-media .lead{font-size:clamp(1.08rem,1.65vw,1.32rem);max-width:46rem;line-height:1.72;margin-top:1.45rem}
.hero-grid-no-media .hero-support{max-width:43rem;font-size:.98rem;line-height:1.7}
.hero-grid-no-media .hero-actions{margin-top:2.45rem}
.hero-grid-no-media .hero-meta{margin-top:.25rem;padding-top:1rem;border-top:1px solid rgba(31,61,43,.1);max-width:46rem}
.section{padding-block:clamp(4.5rem,7vw,7.5rem)}
.section-cream{background:linear-gradient(180deg,#f4ecdd 0%,#f9f5ee 58%,#f7f4ee 100%);border-block:1px solid rgba(184,151,58,.08)}
.section-intro{margin-bottom:clamp(2.6rem,5vw,4.25rem)}
.section-intro>h2{max-width:16ch}
.section-intro>.lead{font-size:clamp(1.03rem,1.45vw,1.2rem)}
.kicker,.eyebrow{font-size:.69rem;letter-spacing:.16em}
.btn{position:relative;isolation:isolate;box-shadow:none}
.btn-primary{background:linear-gradient(135deg,#173827 0%,#254d38 100%);box-shadow:0 12px 30px rgba(16,39,27,.18),inset 0 1px 0 rgba(255,255,255,.13)}
.btn-secondary{background:rgba(255,255,255,.7);backdrop-filter:blur(12px);box-shadow:inset 0 0 0 1px rgba(184,151,58,.08)}
@media(hover:hover){
  .btn-primary:hover{transform:translateY(-2px);box-shadow:0 18px 38px rgba(16,39,27,.24),inset 0 1px 0 rgba(255,255,255,.14)}
  .btn-secondary:hover{transform:translateY(-2px);background:#fff;border-color:rgba(184,151,58,.44)}
  .modality-row:hover{background:linear-gradient(90deg,rgba(184,151,58,.055),transparent 72%);padding-inline:.9rem}
}
.modality-row{transition:background .22s ease,padding .22s ease}
.principle-stack{border-top-color:rgba(184,151,58,.38)}
.principle-row{padding-block:clamp(1.55rem,2.8vw,2.15rem)}
.principle-row h3{letter-spacing:-.03em}
.confidence-band{position:relative;overflow:hidden;background:
  radial-gradient(circle at 100% 0%,rgba(184,151,58,.13),transparent 28rem),
  linear-gradient(135deg,#ebe1cf 0%,#f7f3eb 72%)}
.confidence-band:before{content:"IBERFIT";position:absolute;right:-.03em;bottom:-.23em;font-family:Iowan Old Style,Baskerville,Georgia,serif;font-size:clamp(8rem,22vw,22rem);font-weight:700;letter-spacing:-.06em;color:rgba(31,61,43,.025);pointer-events:none}
.confidence-grid{position:relative}
.review-proof{background:
  radial-gradient(circle at 15% 0%,rgba(217,181,104,.12),transparent 24rem),
  linear-gradient(145deg,#10271b 0%,#183a29 55%,#0c2016 100%)}
.review-proof-card{background:linear-gradient(145deg,rgba(255,255,255,.09),rgba(255,255,255,.045));border-color:rgba(217,181,104,.32)}
.origin-section{position:relative;overflow:hidden;background:
  radial-gradient(circle at 8% 12%,rgba(217,181,104,.12),transparent 28rem),
  linear-gradient(145deg,#0c2016 0%,#173827 58%,#10271b 100%);border:0;color:#fff}
.origin-section:before{content:"";position:absolute;right:-10rem;top:-14rem;width:32rem;height:32rem;border:1px solid rgba(217,181,104,.13);border-radius:50%;box-shadow:0 0 0 5rem rgba(217,181,104,.02),0 0 0 10rem rgba(217,181,104,.018)}
.origin-section .founder-grid{position:relative;align-items:start}
.origin-section h2{color:#fff;max-width:11ch;font-size:clamp(2.4rem,5vw,4.7rem);line-height:.98}
.origin-section .kicker{color:var(--gold-light)}
.origin-section .founder-copy{padding-left:clamp(1.4rem,3vw,2.6rem);border-left:1px solid rgba(217,181,104,.42)}
.origin-section .founder-copy p,.origin-section .founder-copy p:first-child{color:rgba(255,255,255,.78);font-size:clamp(1rem,1.35vw,1.15rem)}
.origin-section .founder-copy p:first-child{color:#fff;font-size:clamp(1.1rem,1.55vw,1.32rem)}
.brand-journey{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;margin:2rem 0 1.8rem;background:rgba(217,181,104,.2);border:1px solid rgba(217,181,104,.22);border-radius:22px;overflow:hidden}
.brand-journey article{min-height:178px;padding:1.35rem;background:rgba(4,22,16,.48)}
.brand-journey span{display:block;margin-bottom:1.85rem;color:var(--gold-light);font-size:.66rem;font-weight:850;letter-spacing:.16em}
.brand-journey strong{display:block;color:#fff;font-family:Iowan Old Style,Baskerville,Georgia,serif;font-size:1.45rem;margin-bottom:.55rem}
.brand-journey p{margin:0!important;color:rgba(255,255,255,.66)!important;font-size:.82rem!important;line-height:1.55!important}
.origin-section + .section-cream{border-top:0}
.photo-story-media{box-shadow:0 28px 72px rgba(16,42,29,.16)}
.photo-story-media:after{border-color:rgba(255,255,255,.42)}
.site-header{background:rgba(247,244,238,.88);border-bottom-color:rgba(31,61,43,.08)}
.site-header.scrolled{background:rgba(247,244,238,.94);box-shadow:0 8px 30px rgba(16,32,24,.08)}
@media(max-width:820px){
  .hero-grid-no-media .hero-text{padding-left:1.15rem}
  .origin-section h2{max-width:14ch}
  .brand-journey{grid-template-columns:repeat(2,minmax(0,1fr))}
  .brand-journey article{min-height:0}
  .brand-journey span{margin-bottom:.75rem}
}
@media(max-width:560px){
  .hero{padding-block:3.6rem 3.1rem}
  .hero-grid-no-media h1{font-size:clamp(2.75rem,14vw,4.2rem);line-height:.96}
  .hero-grid-no-media .hero-text{padding-left:.95rem}
  .hero-grid-no-media .hero-actions{gap:.7rem}
  .hero-grid-no-media .hero-actions .btn{width:100%}
  .section{padding-block:4rem}
  .origin-section .founder-copy{padding-left:1rem}
  .brand-journey{grid-template-columns:1fr;border-radius:18px}
}
@media(prefers-reduced-motion:reduce){
  .modality-row,.btn{transition:none!important}
}
.choice-chip{min-height:48px}
@media(max-width:720px){
  .device-dock{
    opacity:0;
    transform:translateY(calc(100% + 1.2rem));
    pointer-events:none;
    transition:opacity .22s ease,transform .22s ease;
  }
  .device-dock.is-visible{
    opacity:1;
    transform:translateY(0);
    pointer-events:auto;
  }
  .device-dock a{min-width:44px;min-height:52px}
}
@media(max-width:430px){input,select,textarea{font-size:16px}}
@media(hover:none){.btn:hover{transform:none}}
@media(prefers-reduced-motion:reduce){
  .reveal{opacity:1!important;transform:none!important}
}
"""


PREMIUM_INTERACTION_CSS = r"""
/* IBERFIT V6.28 · fidelidad e interacción adaptativa */
html{text-rendering:optimizeLegibility}
body{-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
h1,h2{text-wrap:balance}
.lead,.hero-support,.photo-story-copy p,.client-review blockquote{text-wrap:pretty}
.photo-story-media img{image-rendering:auto;transform:translateZ(0);transition:transform .8s cubic-bezier(.2,.7,.2,1),filter .8s ease}
.premium-surface{--mx:50%;--my:50%;--rx:0deg;--ry:0deg;position:relative;isolation:isolate}
.premium-surface:before{content:"";position:absolute;inset:0;z-index:2;border-radius:inherit;pointer-events:none;opacity:0;background:radial-gradient(420px circle at var(--mx) var(--my),rgba(217,181,104,.14),rgba(255,255,255,.035) 32%,transparent 66%);transition:opacity .35s ease}
.premium-surface>*{position:relative;z-index:1}
.btn:active{transform:translateY(0) scale(.985)}
.choice-chip:active,.device-dock a:active{transform:scale(.98)}
.modality-row h3,.principle-row h3{transition:transform .35s cubic-bezier(.2,.7,.2,1),color .35s ease}
.system-stage,.cycle-step{transition:background .35s ease,border-color .35s ease}

@keyframes iberfit-ambient{
  0%{transform:translate3d(0,0,0) scale(1)}
  100%{transform:translate3d(-2%,3%,0) scale(1.055)}
}

@media (hover:hover) and (pointer:fine) and (min-width:1024px){
  html.motion-rich .premium-surface{
    transform:perspective(1400px) rotateX(var(--rx)) rotateY(var(--ry)) translateZ(0);
    transform-style:preserve-3d;
    transition:transform .18s ease-out,box-shadow .45s ease,border-color .45s ease
  }
  html.motion-rich .premium-surface:hover{will-change:transform;box-shadow:0 30px 78px rgba(8,31,20,.18)}
  html.motion-rich .premium-surface:hover:before{opacity:1}
  html.motion-rich .photo-story-media:hover img{transform:scale(1.024)}
  html.motion-rich .system-stage:hover,
  html.motion-rich .cycle-step:hover{background:rgba(255,253,248,.96)}
  html.motion-rich .modality-row:hover h3,
  html.motion-rich .principle-row:hover h3{transform:translateX(6px)}
  html.motion-rich .hero:before{animation:iberfit-ambient 14s ease-in-out infinite alternate}
}

@media (min-width:641px) and (max-width:1100px){
  .system-rail{grid-template-columns:repeat(2,minmax(0,1fr))}
  .system-stage{min-height:180px}
  .system-stage:nth-child(2){border-right:0}
  .system-stage:nth-child(-n+2){border-bottom:1px solid var(--line)}
  .system-stage:nth-child(2):after{display:none}
  .method-cycle{grid-template-columns:repeat(3,minmax(0,1fr))}
  .cycle-step{min-height:205px}
}

@media (max-width:640px){
  .premium-rail{
    display:grid!important;
    grid-template-columns:none!important;
    grid-auto-flow:column;
    grid-auto-columns:minmax(245px,78vw);
    gap:.8rem!important;
    margin-inline:-16px;
    padding:0 22vw 12px 16px;
    overflow-x:auto;
    overflow-y:hidden;
    overscroll-behavior-inline:contain;
    scroll-snap-type:x mandatory;
    scroll-padding-inline:16px;
    scrollbar-width:none;
    background:transparent!important;
    border:0!important;
    -webkit-overflow-scrolling:touch
  }
  .premium-rail::-webkit-scrollbar{display:none}
  .premium-rail>*{
    scroll-snap-align:start;
    scroll-snap-stop:always;
    min-height:205px;
    border:1px solid var(--line)!important;
    border-radius:22px;
    box-shadow:0 16px 36px rgba(16,42,29,.08)
  }
  .system-rail .system-stage:not(:last-child):after{display:none}
  .cycle-step>span{margin-bottom:2rem}
  .system-stage{padding:1.45rem 1.25rem}
}

@media (prefers-reduced-motion:reduce){
  .premium-surface{transform:none!important}
  .premium-surface:before{display:none!important}
  .photo-story-media img{transform:none!important}
  .premium-rail{scroll-behavior:auto!important}
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

def specialize_local_page(text: str, rel: str) -> str:
    """Hace que cada landing local hable desde su realidad urbana, sin estereotipos socioeconómicos."""
    local = {
        "entrenador-personal-las-condes/index.html": {
            "<h1>Entrenamiento personal con criterio en Las Condes.</h1>": "<h1>Entrenar en Las Condes sin que la agenda mande sobre tu plan.</h1>",
            '<p class="lead">Cobertura prioritaria para entrenamiento a domicilio y en gimnasios de edificios, sujeta a disponibilidad y condiciones del espacio.</p>': '<p class="lead">Si entre horarios, desplazamientos y cambios de agenda el entrenamiento siempre queda para después, buscamos una forma que puedas sostener de verdad.</p>',
            '<p class="hero-support">Entrenamiento personal con criterio: diagnóstico, planificación, control y seguimiento.</p>': '<p class="hero-support">Domicilio, gimnasio de edificio o modalidad híbrida: primero entendemos tu semana y después decidimos contigo qué formato tiene sentido.</p>',
            '<div class="kicker">Cobertura y modalidad</div><h2>Entrenar en Las Condes: espacio, horarios y continuidad.</h2>': '<div class="kicker">Entrenar aquí</div><h2>En una comuna extensa, la constancia empieza por reducir fricción.</h2>',
            '<p class="lead">Cobertura prioritaria para entrenamiento a domicilio y en gimnasios de edificios, sujeta a disponibilidad y condiciones del espacio.</p>': '<p class="lead">Un plan puede ser perfecto sobre el papel y fracasar si cada sesión exige una logística imposible. Por eso sector, horario y espacio forman parte del plan desde el principio.</p>',
            "<h2>La modalidad depende del espacio y de cómo encaja en tu semana.</h2>": "<h2>Decidimos contigo cómo hacer que entrenar encaje en tu semana.</h2>",
            "<h3>Ubicación</h3><p>Sectores residenciales extensos hacen importante coordinar horarios y desplazamiento con precisión.</p>": "<h3>Tu semana real</h3><p>Miramos cuándo puedes entrenar de verdad y cuánto margen tienes para desplazarte sin convertir cada sesión en una carrera.</p>",
            "<h3>Objetivo</h3><p>La prioridad puede ser fuerza, salud, composición corporal, rendimiento o retorno progresivo.</p>": "<h3>Qué quieres conseguir</h3><p>El objetivo ordena el plan, pero también cuánto tiempo y frecuencia necesitas para que sea realista.</p>",
            "<h3>Autonomía</h3><p>La logística suele favorecer sesiones presenciales o híbridas cuando existe un espacio adecuado en domicilio o condominio.</p>": "<h3>Dónde puedes entrenar</h3><p>Si tienes un espacio útil en casa o en tu edificio, lo aprovechamos. Si no, buscamos otra opción que mantenga la calidad.</p>",
            "<h3>Seguimiento</h3><p>Toda modalidad incluye planificación, control y revisión, no solo ejecución de sesiones.</p>": "<h3>Cuánta supervisión necesitas</h3><p>No todo tiene que ser presencial. Reservamos la supervisión directa para los momentos en que realmente aporta valor.</p>",
            "<h2>Primero confirmamos sector, espacio y horario.</h2>": "<h2>Primero vemos si podemos hacerlo bien, no solo si podemos ir.</h2>",
            '<p class="lead">IBERFIT no promete disponibilidad automática en toda la comuna. Primero se revisan sector, horarios, espacio y modalidad adecuada para proteger la calidad del servicio.</p>': '<p class="lead">Cuéntanos tu sector, horarios y dónde podrías entrenar. Si la frecuencia presencial no es la mejor opción, te lo diremos y buscaremos una alternativa más sostenible.</p>',
            "<h2>Revisa cobertura y horarios en Las Condes.</h2>": "<h2>Cuéntanos en qué sector de Las Condes estás y cómo es tu semana.</h2>",
            "<p>Comparte sector, objetivo y horarios para recibir una orientación inicial.</p>": "<p>Con esa información podemos orientarte sin hacerte perder tiempo.</p>",
        },
        "entrenador-personal-vitacura/index.html": {
            "<h1>Entrenamiento personal con criterio en Vitacura.</h1>": "<h1>Entrenar en Vitacura con un plan que encaje en tu entorno, no al revés.</h1>",
            '<p class="lead">Servicio presencial según sector, acceso y disponibilidad, con alternativas híbridas para sostener frecuencia.</p>': '<p class="lead">En una comuna residencial y verde, entrenar cerca puede ser una ventaja. La clave es convertir esa comodidad en continuidad y no en improvisación.</p>',
            '<p class="hero-support">Entrenamiento personal con criterio: diagnóstico, planificación, control y seguimiento.</p>': '<p class="hero-support">Podemos trabajar en domicilio, espacios residenciales o combinar sesiones presenciales con trabajo guiado, según lo que realmente te ayude a avanzar.</p>',
            '<div class="kicker">Cobertura y modalidad</div><h2>Entrenar en Vitacura: supervisión y continuidad según tu agenda.</h2>': '<div class="kicker">Entrenar aquí</div><h2>Estar cerca ayuda. Tener dirección marca la diferencia.</h2>',
            '<p class="lead">Servicio presencial según sector, acceso y disponibilidad, con alternativas híbridas para sostener frecuencia.</p>': '<p class="lead">Si tu entorno ya facilita moverte, caminar, usar bicicleta o entrenar cerca de casa, lo tenemos en cuenta. El plan parte de lo que ya forma parte de tu vida.</p>',
            "<h2>La combinación adecuada depende de tu autonomía y disponibilidad.</h2>": "<h2>No necesitas más supervisión de la necesaria; necesitas la adecuada.</h2>",
            "<h3>Ubicación</h3><p>La evaluación inicial permite revisar el espacio disponible y el nivel de autonomía.</p>": "<h3>Tu entorno cuenta</h3><p>Revisamos el espacio que ya tienes disponible y qué podemos aprovechar sin añadir complicaciones.</p>",
            "<h3>Objetivo</h3><p>La prioridad puede ser fuerza, salud, composición corporal, rendimiento o retorno progresivo.</p>": "<h3>Qué quieres mejorar</h3><p>Fuerza, salud, composición corporal o rendimiento requieren prioridades distintas. No empezamos por una rutina estándar.</p>",
            "<h3>Autonomía</h3><p>La combinación presencial y guiada en app puede aportar continuidad cuando la agenda cambia.</p>": "<h3>Autonomía bien guiada</h3><p>Si puedes entrenar parte de la semana por tu cuenta, diseñamos esa parte para que siga conectada con lo que hacemos juntos.</p>",
            "<h3>Seguimiento</h3><p>Toda modalidad incluye planificación, control y revisión, no solo ejecución de sesiones.</p>": "<h3>Revisar sin esperar a que algo falle</h3><p>Seguimos tu respuesta y ajustamos antes de que una semana difícil se convierta en abandono.</p>",
            "<h2>La disponibilidad se revisa junto con acceso y entorno.</h2>": "<h2>Antes de coordinar, vemos cómo encaja el servicio en tu día a día.</h2>",
            '<p class="lead">IBERFIT no promete disponibilidad automática en toda la comuna. Primero se revisan sector, horarios, espacio y modalidad adecuada para proteger la calidad del servicio.</p>': '<p class="lead">Sector, acceso, horario y espacio importan. Los revisamos contigo y te proponemos solo una modalidad que podamos sostener bien.</p>',
            "<h2>Consulta una modalidad viable en Vitacura.</h2>": "<h2>Cuéntanos cómo te gustaría entrenar en Vitacura.</h2>",
            "<p>Comparte sector, objetivo y horarios para recibir una orientación inicial.</p>": "<p>Con tu sector, objetivo y disponibilidad podemos decirte qué opción tiene más sentido.</p>",
        },
        "entrenamiento-personal-providencia/index.html": {
            "<h1>Entrenamiento personal con criterio en Providencia.</h1>": "<h1>Un plan que quepa en una semana que se mueve.</h1>",
            '<p class="lead">Atención según sector y condiciones de acceso, con opciones presenciales, híbridas y a distancia.</p>': '<p class="lead">En Providencia la vida diaria ya implica moverse mucho. El entrenamiento no debería convertirse en otro traslado que compite con tu tiempo.</p>',
            '<p class="hero-support">Entrenamiento personal con criterio: diagnóstico, planificación, control y seguimiento.</p>': '<p class="hero-support">Domicilio, gimnasio de edificio, una combinación híbrida o trabajo a distancia: buscamos la opción más eficiente sin perder seguimiento.</p>',
            '<div class="kicker">Cobertura y modalidad</div><h2>Entrenar en Providencia: una modalidad que funcione con tu rutina.</h2>': '<div class="kicker">Entrenar aquí</div><h2>En Providencia, la eficiencia también forma parte del plan.</h2>',
            '<p class="lead">Atención según sector y condiciones de acceso, con opciones presenciales, híbridas y a distancia.</p>': '<p class="lead">Si ya caminas, usas bicicleta o te mueves mucho durante el día, esa actividad también forma parte del contexto. No empezamos suponiendo que todo ocurre dentro de un gimnasio.</p>',
            "<h2>Domicilio, edificio o distancia: elegimos lo sostenible.</h2>": "<h2>Menos fricción. Más continuidad.</h2>",
            "<h3>Ubicación</h3><p>El servicio puede adaptarse a domicilio, gimnasio de edificio o entrenamiento a distancia.</p>": "<h3>Tu tiempo disponible</h3><p>Buscamos la frecuencia y duración que puedas sostener sin que entrenar dependa de una semana perfecta.</p>",
            "<h3>Objetivo</h3><p>La prioridad puede ser fuerza, salud, composición corporal, rendimiento o retorno progresivo.</p>": "<h3>Tu objetivo real</h3><p>Definimos qué merece prioridad para que el tiempo que dediques tenga una intención clara.</p>",
            "<h3>Autonomía</h3><p>La densidad urbana y los tiempos de traslado hacen especialmente útil planificar una modalidad sostenible.</p>": "<h3>El espacio que ya tienes</h3><p>Casa, edificio, gimnasio o trabajo guiado a distancia: usamos lo que haga más fácil repetir la semana siguiente.</p>",
            "<h3>Seguimiento</h3><p>Toda modalidad incluye planificación, control y revisión, no solo ejecución de sesiones.</p>": "<h3>Una semana difícil no borra el plan</h3><p>Si cambia tu agenda, ajustamos la dosis y protegemos lo importante en vez de empezar de cero.</p>",
            "<h2>La cobertura se revisa junto con tiempos y acceso.</h2>": "<h2>Primero revisamos qué opción te ahorra fricción sin perder calidad.</h2>",
            '<p class="lead">IBERFIT no promete disponibilidad automática en toda la comuna. Primero se revisan sector, horarios, espacio y modalidad adecuada para proteger la calidad del servicio.</p>': '<p class="lead">Cuéntanos dónde estás, qué horarios manejas y con qué espacio cuentas. La mejor modalidad es la que te permite entrenar bien y repetirlo.</p>',
            "<h2>Busca una opción sostenible en Providencia.</h2>": "<h2>Cuéntanos cómo es tu semana en Providencia.</h2>",
            "<p>Comparte sector, objetivo y horarios para recibir una orientación inicial.</p>": "<p>Te orientamos hacia una forma de entrenar que no pelee con tu agenda.</p>",
        },
        "personal-trainer-nunoa/index.html": {
            "<h1>Entrenamiento personal con criterio en Ñuñoa.</h1>": "<h1>Un plan que se adapte a tu barrio, tu espacio y tu semana.</h1>",
            '<p class="lead">Atención presencial en sectores compatibles, además de modalidades híbrida y a distancia.</p>': '<p class="lead">Ñuñoa combina casas, departamentos, espacios comunes y mucha vida de barrio. No hay una sola forma correcta de entrenar aquí.</p>',
            '<p class="hero-support">Entrenamiento personal con criterio: diagnóstico, planificación, control y seguimiento.</p>': '<p class="hero-support">Primero entendemos tu punto de partida y el entorno que realmente tienes; después decidimos contigo cómo entrenar.</p>',
            '<div class="kicker">Cobertura y modalidad</div><h2>Entrenar en Ñuñoa: decidir el plan después de evaluar.</h2>': '<div class="kicker">Entrenar aquí</div><h2>Tu entorno puede cambiar mucho a pocas cuadras. El plan también puede adaptarse.</h2>',
            '<p class="lead">Atención presencial en sectores compatibles, además de modalidades híbrida y a distancia.</p>': '<p class="lead">El espacio, el equipamiento y la facilidad para desplazarte importan tanto como el objetivo. El Diagnóstico IRI nos ayuda a ordenarlo antes de contratar un plan.</p>',
            "<h2>El Diagnóstico IRI orienta la modalidad antes de contratar.</h2>": "<h2>Primero entendemos cómo puedes entrenar; después elegimos la modalidad.</h2>",
            "<h3>Ubicación</h3><p>El Diagnóstico IRI permite definir una estrategia realista antes de contratar un plan.</p>": "<h3>Tu punto de partida</h3><p>El IRI nos ayuda a saber qué necesitas y cuánto acompañamiento aporta valor al principio.</p>",
            "<h3>Objetivo</h3><p>La prioridad puede ser fuerza, salud, composición corporal, rendimiento o retorno progresivo.</p>": "<h3>Lo que quieres conseguir</h3><p>No todo tiene que mejorar a la vez. Elegimos prioridades que puedas notar y sostener.</p>",
            "<h3>Autonomía</h3><p>La elección de modalidad considera espacio, equipamiento, autonomía y frecuencia posible.</p>": "<h3>Tu espacio real</h3><p>Casa, departamento, gimnasio o material básico: partimos de lo que tienes, no de lo que te falta.</p>",
            "<h3>Seguimiento</h3><p>Toda modalidad incluye planificación, control y revisión, no solo ejecución de sesiones.</p>": "<h3>Tu ritmo semanal</h3><p>La frecuencia se construye alrededor de tu semana para que avanzar no dependa de hacerlo todo perfecto.</p>",
            "<h2>Primero revisamos sector, objetivo y entorno.</h2>": "<h2>Antes de coordinar, queremos entender dónde y cómo podrías entrenar.</h2>",
            '<p class="lead">IBERFIT no promete disponibilidad automática en toda la comuna. Primero se revisan sector, horarios, espacio y modalidad adecuada para proteger la calidad del servicio.</p>': '<p class="lead">Sector, espacio y horarios nos ayudan a proponerte una modalidad realista. Si lo presencial no es la mejor combinación, te lo explicamos.</p>',
            "<h2>Define tu punto de partida en Ñuñoa.</h2>": "<h2>Cuéntanos cómo te gustaría entrenar en Ñuñoa.</h2>",
            "<p>Comparte sector, objetivo y horarios para recibir una orientación inicial.</p>": "<p>Empezamos por entender tu contexto, no por venderte una modalidad.</p>",
        },
        "entrenador-personal-lo-barnechea/index.html": {
            "<h1>Entrenamiento personal con criterio en Lo Barnechea.</h1>": "<h1>En Lo Barnechea, la logística también forma parte del plan.</h1>",
            '<p class="lead">Cobertura presencial condicionada por sector, tiempos de desplazamiento y disponibilidad.</p>': '<p class="lead">Las distancias dentro de la comuna pueden cambiar mucho la viabilidad de una frecuencia presencial. Preferimos diseñarlo bien desde el principio.</p>',
            '<p class="hero-support">Entrenamiento personal con criterio: diagnóstico, planificación, control y seguimiento.</p>': '<p class="hero-support">Elegimos contigo qué momentos necesitan presencia directa y cuáles pueden resolverse con trabajo guiado sin perder continuidad.</p>',
            '<div class="kicker">Cobertura y modalidad</div><h2>Entrenar en Lo Barnechea: coordinar bien para sostener el plan.</h2>': '<div class="kicker">Entrenar aquí</div><h2>Cuando las distancias importan, la frecuencia tiene que ser inteligente.</h2>',
            '<p class="lead">Cobertura presencial condicionada por sector, tiempos de desplazamiento y disponibilidad.</p>': '<p class="lead">Lo Barnechea combina zonas urbanas con una relación muy cercana con la montaña y grandes diferencias de desplazamiento. El plan tiene que convivir con esa realidad.</p>',
            "<h2>La frecuencia presencial debe ser compatible con la logística.</h2>": "<h2>No todo tiene que ser presencial para sentirse acompañado.</h2>",
            "<h3>Ubicación</h3><p>La coordinación previa es esencial para mantener puntualidad y continuidad.</p>": "<h3>Tu sector</h3><p>La ubicación cambia cuánto tiempo tiene sentido dedicar a traslados y qué frecuencia podemos sostener bien.</p>",
            "<h3>Objetivo</h3><p>La prioridad puede ser fuerza, salud, composición corporal, rendimiento o retorno progresivo.</p>": "<h3>Tu actividad real</h3><p>Si además haces deporte al aire libre, bicicleta, trekking u otra actividad, lo incorporamos al contexto en vez de ignorarlo.</p>",
            "<h3>Autonomía</h3><p>La modalidad híbrida puede reducir desplazamientos sin perder evaluación ni supervisión periódica.</p>": "<h3>Presencial cuando aporta</h3><p>Usamos las sesiones directas para técnica, evaluaciones y ajustes que merece la pena observar en persona.</p>",
            "<h3>Seguimiento</h3><p>Toda modalidad incluye planificación, control y revisión, no solo ejecución de sesiones.</p>": "<h3>Continuidad entre sesiones</h3><p>El trabajo guiado mantiene el plan vivo entre encuentros y evita depender de un traslado para cada entrenamiento.</p>",
            "<h2>Sector y desplazamiento se confirman antes de reservar.</h2>": "<h2>Antes de reservar, vemos qué frecuencia podemos sostener bien.</h2>",
            '<p class="lead">IBERFIT no promete disponibilidad automática en toda la comuna. Primero se revisan sector, horarios, espacio y modalidad adecuada para proteger la calidad del servicio.</p>': '<p class="lead">Cuéntanos tu sector y horarios. Si una frecuencia presencial alta añade más fricción que valor, te propondremos otra combinación.</p>',
            "<h2>Revisa viabilidad presencial en Lo Barnechea.</h2>": "<h2>Cuéntanos en qué sector de Lo Barnechea estás.</h2>",
            "<p>Comparte sector, objetivo y horarios para recibir una orientación inicial.</p>": "<p>Con eso podemos proponerte una frecuencia realista antes de que organices tu semana.</p>",
        },
        "entrenador-personal-la-reina/index.html": {
            "<h1>Entrenamiento personal con criterio en La Reina.</h1>": "<h1>Entrenar cerca, con continuidad y sin complicarlo de más.</h1>",
            '<p class="lead">Servicio a domicilio o en espacios acordados, sujeto a sector y disponibilidad.</p>': '<p class="lead">La escala residencial y los espacios verdes de La Reina permiten pensar el entrenamiento cerca de tu vida cotidiana. Nuestro trabajo es darle estructura.</p>',
            '<p class="hero-support">Entrenamiento personal con criterio: diagnóstico, planificación, control y seguimiento.</p>': '<p class="hero-support">Domicilio, espacio acordado o modalidad híbrida: elegimos contigo la forma que puedas repetir sin perder seguimiento.</p>',
            '<div class="kicker">Cobertura y modalidad</div><h2>Entrenar en La Reina: aprovechar el entorno sin improvisar.</h2>': '<div class="kicker">Entrenar aquí</div><h2>La cercanía puede convertirse en una ventaja si el plan tiene dirección.</h2>',
            '<p class="lead">Servicio a domicilio o en espacios acordados, sujeto a sector y disponibilidad.</p>': '<p class="lead">Si ya caminas, pedaleas o haces actividad al aire libre, también lo tenemos en cuenta. El entrenamiento no empieza y termina en una sesión.</p>',
            "<h2>El espacio y tu autonomía determinan la mejor combinación.</h2>": "<h2>Aprovechamos lo que tienes cerca sin perder criterio.</h2>",
            "<h3>Ubicación</h3><p>La evaluación inicial confirma si el entorno permite trabajar con seguridad y continuidad.</p>": "<h3>Tu espacio</h3><p>Revisamos qué se puede hacer bien en casa o en un espacio cercano antes de pedirte más equipamiento o desplazamientos.</p>",
            "<h3>Objetivo</h3><p>La prioridad puede ser fuerza, salud, composición corporal, rendimiento o retorno progresivo.</p>": "<h3>Tu objetivo</h3><p>El entorno ayuda, pero la prioridad la marca lo que quieres mejorar y tu punto de partida.</p>",
            "<h3>Autonomía</h3><p>Las opciones presencial e híbrida permiten combinar supervisión y autonomía según experiencia.</p>": "<h3>Tu autonomía</h3><p>Podemos combinar supervisión y trabajo por tu cuenta a medida que ganas seguridad y control.</p>",
            "<h3>Seguimiento</h3><p>Toda modalidad incluye planificación, control y revisión, no solo ejecución de sesiones.</p>": "<h3>Lo que ocurre fuera de la sesión</h3><p>Actividad, recuperación y cambios de semana también cuentan cuando decidimos qué hacer después.</p>",
            "<h2>Antes de reservar, validamos espacio y disponibilidad.</h2>": "<h2>Primero vemos cómo entrenar cerca sin comprometer la calidad.</h2>",
            '<p class="lead">IBERFIT no promete disponibilidad automática en toda la comuna. Primero se revisan sector, horarios, espacio y modalidad adecuada para proteger la calidad del servicio.</p>': '<p class="lead">Cuéntanos sector, horarios y espacio disponible. Te diremos con claridad qué modalidad podemos sostener bien.</p>',
            "<h2>Consulta cobertura y modalidad en La Reina.</h2>": "<h2>Cuéntanos cómo sería más fácil entrenar en La Reina.</h2>",
            "<p>Comparte sector, objetivo y horarios para recibir una orientación inicial.</p>": "<p>La idea es encontrar una forma que puedas mantener, no añadir otra obligación a tu semana.</p>",
        },
        "entrenador-personal-penalolen/index.html": {
            "<h1>Entrenamiento personal con criterio en Peñalolén.</h1>": "<h1>Peñalolén no se entrena igual en todos sus sectores.</h1>",
            '<p class="lead">Cobertura selectiva según sector y logística, con alternativas híbrida y a distancia.</p>': '<p class="lead">La comuna cambia mucho entre sectores y también cambia la facilidad para desplazarse. Por eso aquí la ubicación no es un detalle: forma parte de la decisión.</p>',
            '<p class="hero-support">Entrenamiento personal con criterio: diagnóstico, planificación, control y seguimiento.</p>': '<p class="hero-support">Primero entendemos dónde estás, qué espacio tienes y qué frecuencia es viable; después decidimos contigo la modalidad.</p>',
            '<div class="kicker">Cobertura y modalidad</div><h2>Entrenar en Peñalolén: continuidad cuando la logística importa.</h2>': '<div class="kicker">Entrenar aquí</div><h2>Tu sector cambia la logística. No debería cambiar la calidad del seguimiento.</h2>',
            '<p class="lead">Cobertura selectiva según sector y logística, con alternativas híbrida y a distancia.</p>': '<p class="lead">Peñalolén tiene realidades distintas entre barrios y zonas cercanas al pie de monte. No usamos una única respuesta para toda la comuna.</p>',
            "<h2>La distancia puede cambiar la frecuencia, no el seguimiento.</h2>": "<h2>La modalidad se decide sector por sector, persona por persona.</h2>",
            "<h3>Ubicación</h3><p>La recomendación se realiza después de revisar ubicación, objetivo y capacidad de entrenamiento autónomo.</p>": "<h3>Tu sector</h3><p>Primero vemos dónde estás y cuánto esfuerzo supone llegar o coordinar una sesión presencial.</p>",
            "<h3>Objetivo</h3><p>La prioridad puede ser fuerza, salud, composición corporal, rendimiento o retorno progresivo.</p>": "<h3>Qué quieres conseguir</h3><p>La prioridad del plan no cambia por vivir más lejos; cambia la forma más inteligente de acompañarte.</p>",
            "<h3>Autonomía</h3><p>Cuando la distancia limita la frecuencia presencial, las sesiones guiadas a distancia pueden sostener el plan.</p>": "<h3>Qué puedes hacer por tu cuenta</h3><p>Si puedes entrenar algunos días con guía clara, la modalidad híbrida puede proteger continuidad sin multiplicar desplazamientos.</p>",
            "<h3>Seguimiento</h3><p>Toda modalidad incluye planificación, control y revisión, no solo ejecución de sesiones.</p>": "<h3>Seguimiento sin desaparecer</h3><p>Que una semana tenga menos presencialidad no significa perder contacto ni entrenar sin dirección.</p>",
            "<h2>Primero revisamos sector y frecuencia posible.</h2>": "<h2>Primero revisamos tu sector y la frecuencia que de verdad podemos sostener.</h2>",
            '<p class="lead">IBERFIT no promete disponibilidad automática en toda la comuna. Primero se revisan sector, horarios, espacio y modalidad adecuada para proteger la calidad del servicio.</p>': '<p class="lead">Cuéntanos en qué sector estás, tus horarios y dónde podrías entrenar. Con eso podemos proponerte una opción honesta antes de coordinar.</p>',
            "<h2>Encuentra una frecuencia sostenible en Peñalolén.</h2>": "<h2>Cuéntanos en qué sector de Peñalolén estás.</h2>",
            "<p>Comparte sector, objetivo y horarios para recibir una orientación inicial.</p>": "<p>No asumimos que toda la comuna funciona igual. Empezamos por tu realidad concreta.</p>",
        },
    }

    for old, new in local.get(rel, {}).items():
        text = text.replace(old, new)

    # El hero habla primero a la persona; el bloque siguiente desarrolla el contexto local.
    hero_leads = {
        "entrenador-personal-las-condes/index.html": (
            "Un plan puede ser perfecto sobre el papel y fracasar si cada sesión exige una logística imposible. Por eso sector, horario y espacio forman parte del plan desde el principio.",
            "Si entre horarios, desplazamientos y cambios de agenda el entrenamiento siempre queda para después, buscamos una forma que puedas sostener de verdad.",
        ),
        "entrenador-personal-vitacura/index.html": (
            "Si tu entorno ya facilita moverte, caminar, usar bicicleta o entrenar cerca de casa, lo tenemos en cuenta. El plan parte de lo que ya forma parte de tu vida.",
            "En una comuna residencial y verde, entrenar cerca puede ser una ventaja. La clave es convertir esa comodidad en continuidad y no en improvisación.",
        ),
        "entrenamiento-personal-providencia/index.html": (
            "Si ya caminas, usas bicicleta o te mueves mucho durante el día, esa actividad también forma parte del contexto. No empezamos suponiendo que todo ocurre dentro de un gimnasio.",
            "En Providencia la vida diaria ya implica moverse mucho. El entrenamiento no debería convertirse en otro traslado que compite con tu tiempo.",
        ),
        "personal-trainer-nunoa/index.html": (
            "El espacio, el equipamiento y la facilidad para desplazarte importan tanto como el objetivo. El Diagnóstico IRI nos ayuda a ordenarlo antes de contratar un plan.",
            "Ñuñoa combina casas, departamentos, espacios comunes y mucha vida de barrio. No hay una sola forma correcta de entrenar aquí.",
        ),
        "entrenador-personal-lo-barnechea/index.html": (
            "Lo Barnechea combina zonas urbanas con una relación muy cercana con la montaña y grandes diferencias de desplazamiento. El plan tiene que convivir con esa realidad.",
            "Las distancias dentro de Lo Barnechea pueden cambiar mucho la viabilidad de una frecuencia presencial. Preferimos diseñarlo bien desde el principio.",
        ),
        "entrenador-personal-la-reina/index.html": (
            "Si ya caminas, pedaleas o haces actividad al aire libre, también lo tenemos en cuenta. El entrenamiento no empieza y termina en una sesión.",
            "La escala residencial y los espacios verdes de La Reina permiten pensar el entrenamiento cerca de tu vida cotidiana. Nuestro trabajo es darle estructura.",
        ),
        "entrenador-personal-penalolen/index.html": (
            "Peñalolén tiene realidades distintas entre barrios y zonas cercanas al pie de monte. No usamos una única respuesta para toda la comuna.",
            "La comuna cambia mucho entre sectores y también cambia la facilidad para desplazarse. Por eso aquí la ubicación no es un detalle: forma parte de la decisión.",
        ),
    }
    if rel in hero_leads:
        old, new = hero_leads[rel]
        text = text.replace(old, new, 1)

    hero_meta = {
        "entrenador-personal-las-condes/index.html": "Presencial según sector y horario · Híbrido cuando reduce fricción · A distancia desde cualquier lugar.",
        "entrenador-personal-vitacura/index.html": "Presencial según sector y acceso · Híbrido para combinar supervisión y autonomía · A distancia desde cualquier lugar.",
        "entrenamiento-personal-providencia/index.html": "Presencial, híbrido o a distancia según tu semana, espacio y tiempos de traslado.",
        "personal-trainer-nunoa/index.html": "Presencial según sector · Híbrido si combina mejor con tu espacio y semana · A distancia desde cualquier lugar.",
        "entrenador-personal-lo-barnechea/index.html": "Presencial cuando aporta · Híbrido para reducir desplazamientos · A distancia desde cualquier lugar.",
        "entrenador-personal-la-reina/index.html": "Domicilio o espacio acordado según sector · Híbrido para sumar autonomía · A distancia desde cualquier lugar.",
        "entrenador-personal-penalolen/index.html": "La modalidad se decide según sector, frecuencia viable y espacio disponible.",
    }
    if rel in hero_meta:
        text = text.replace(
            "Entrenamiento presencial en comunas seleccionadas de Santiago. Entrenamiento a distancia disponible desde cualquier lugar.",
            hero_meta[rel],
            1,
        )

    scope_notes = {
        "entrenador-personal-las-condes/index.html": ("¿Tu semana cambia mucho?", "La modalidad híbrida o a distancia puede mantener la continuidad sin obligarte a reorganizar toda tu agenda."),
        "entrenador-personal-vitacura/index.html": ("¿No necesitas presencial todas las semanas?", "Podemos reservar las sesiones directas para cuando realmente aportan y guiar el resto con el mismo plan."),
        "entrenamiento-personal-providencia/index.html": ("¿No quieres sumar otro traslado?", "La modalidad híbrida o a distancia puede darte seguimiento sin convertir cada sesión en un problema logístico."),
        "personal-trainer-nunoa/index.html": ("¿Tu espacio o tu semana cambian?", "Podemos combinar formatos sin perder el hilo del plan ni obligarte a empezar de cero."),
        "entrenador-personal-lo-barnechea/index.html": ("¿La distancia complica la frecuencia presencial?", "Podemos usar la presencialidad de forma estratégica y mantener el trabajo guiado entre sesiones."),
        "entrenador-personal-la-reina/index.html": ("¿Prefieres combinar cercanía y autonomía?", "La modalidad híbrida puede ayudarte a aprovechar tu entorno sin perder supervisión cuando hace falta."),
        "entrenador-personal-penalolen/index.html": ("¿Tu sector hace difícil sostener la presencialidad?", "La frecuencia puede cambiar. El seguimiento y la dirección del plan no tienen por qué desaparecer."),
    }
    if rel in scope_notes:
        title, body = scope_notes[rel]
        text = text.replace(
            '<span>¿Fuera de cobertura o con horarios variables?</span><p>El entrenamiento a distancia está disponible desde cualquier lugar y mantiene planificación, sesiones guiadas y seguimiento.</p>',
            f'<span>{title}</span><p>{body}</p>',
            1,
        )

    bottom_cta = {
        "entrenador-personal-las-condes/index.html": "Ver qué opción encaja",
        "entrenador-personal-vitacura/index.html": "Ver qué opción me conviene",
        "entrenamiento-personal-providencia/index.html": "Ver cómo encajarlo en mi semana",
        "personal-trainer-nunoa/index.html": "Ver qué modalidad encaja conmigo",
        "entrenador-personal-lo-barnechea/index.html": "Revisar una frecuencia realista",
        "entrenador-personal-la-reina/index.html": "Ver qué opción encaja conmigo",
        "entrenador-personal-penalolen/index.html": "Revisar mi sector y frecuencia",
    }
    if rel in bottom_cta:
        text = text.replace(
            ">Consultar cobertura y horarios</a>",
            f">{bottom_cta[rel]}</a>",
            1,
        )

    meta_descriptions = {
        "entrenador-personal-las-condes/index.html": "Entrenamiento personal en Las Condes pensado para una agenda real: domicilio, gimnasio de edificio o híbrido según sector, espacio y horarios.",
        "entrenador-personal-vitacura/index.html": "Entrenamiento personal en Vitacura que aprovecha tu entorno y combina supervisión y autonomía según sector, espacio y disponibilidad.",
        "entrenamiento-personal-providencia/index.html": "Entrenamiento personal en Providencia sin sumar fricción: presencial, híbrido o a distancia según tu semana, espacio y tiempos de traslado.",
        "personal-trainer-nunoa/index.html": "Entrenamiento personal en Ñuñoa adaptado a tu barrio, espacio y semana. IRI para decidir modalidad y frecuencia antes de empezar.",
        "entrenador-personal-lo-barnechea/index.html": "Entrenamiento personal en Lo Barnechea con frecuencia pensada según sector y distancias, combinando presencial e híbrido cuando aporta continuidad.",
        "entrenador-personal-la-reina/index.html": "Entrenamiento personal en La Reina cerca de tu rutina, combinando domicilio, autonomía y seguimiento según espacio, sector y disponibilidad.",
        "entrenador-personal-penalolen/index.html": "Entrenamiento personal en Peñalolén decidido según tu sector, espacio y frecuencia posible, con seguimiento presencial, híbrido o a distancia.",
    }
    if rel in meta_descriptions:
        description = meta_descriptions[rel]
        text = re.sub(
            r'(<meta\b(?=[^>]*\bname="description")[^>]*\bcontent=")[^"]*(")',
            lambda match: match.group(1) + description + match.group(2),
            text,
            count=1,
            flags=re.I,
        )

    if rel in local:
        text = re.sub(
            r'>Consultar disponibilidad en [^<]+</a>',
            '>Hablar con IBERFIT</a>',
            text,
            count=1,
            flags=re.I,
        )

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

    refinements = {
        "index.html": {
            "IBERFIT nació para que entrenar tenga una dirección que puedas entender. Por eso cada mejora de la marca tiene que ayudarte a entender mejor, decidir mejor o sostener mejor tu proceso.": "IBERFIT nació de una pregunta sencilla: ¿cómo hacer que una persona no solo entrene, sino que entienda lo que está haciendo y pueda sostenerlo? Desde entonces, cada mejora tiene que aportar en una de tres cosas.",
            "Antes de decirte qué hacer, queremos comprender dónde estás y qué necesitas.": "Escuchamos tu contexto antes de proponerte qué hacer.",
            "Medimos y registramos solo cuando esa información puede mejorar una decisión.": "Los datos solo valen si ayudan a tomar una decisión mejor.",
            "El plan tiene que poder vivir contigo cuando cambian tu semana, tu contexto o tus objetivos.": "El plan tiene que poder adaptarse cuando tu vida cambia.",
            '<div class="kicker">Lo que no cambia</div><h2>La información y los ajustes forman parte del proceso.</h2>': '<div class="kicker">Nuestra promesa</div><h2>Hay cosas que cambian contigo. Nuestro criterio no.</h2>',
            '<p><strong>Continuidad</strong>La evaluación, las sesiones y los cambios quedan conectados.</p><p><strong>Criterio profesional</strong>Las herramientas apoyan la decisión; no la sustituyen.</p><p><strong>Adaptación real</strong>El plan responde a evolución, contexto y adherencia.</p>': '<p><strong>Claridad</strong>Puedes preguntar y entender por qué proponemos algo.</p><p><strong>Continuidad</strong>Lo que ocurre hoy sirve para decidir mejor el siguiente paso.</p><p><strong>Decisión humana</strong>La tecnología ayuda; no decide por ti.</p>',
        },
        "sobre-iberfit/index.html": {
            "<title>Sobre IBERFIT | Una forma más clara de avanzar</title>": "<title>Sobre IBERFIT | Una marca con método y conversación</title>",
            'content="IBERFIT conecta evaluación, planificación, control y seguimiento para ayudarte a entender tu punto de partida y avanzar con una dirección clara." name="description"': 'content="Conoce por qué nació IBERFIT y cómo una marca con método, conversación y mejora continua busca ayudarte a entender, decidir y sostener mejor tu proceso." name="description"',
            'content="Sobre IBERFIT | Una forma más clara de avanzar" property="og:title"': 'content="Sobre IBERFIT | Una marca con método y conversación" property="og:title"',
            'content="IBERFIT conecta evaluación, planificación, control y seguimiento para ayudarte a entender tu punto de partida y avanzar con una dirección clara." property="og:description"': 'content="Conoce por qué nació IBERFIT y cómo una marca con método, conversación y mejora continua busca ayudarte a entender, decidir y sostener mejor tu proceso." property="og:description"',
            'content="Sobre IBERFIT | Una forma más clara de avanzar" name="twitter:title"': 'content="Sobre IBERFIT | Una marca con método y conversación" name="twitter:title"',
            'content="IBERFIT conecta evaluación, planificación, control y seguimiento para ayudarte a entender tu punto de partida y avanzar con una dirección clara." name="twitter:description"': 'content="Conoce por qué nació IBERFIT y cómo una marca con método, conversación y mejora continua busca ayudarte a entender, decidir y sostener mejor tu proceso." name="twitter:description"',
            "<h1>Tu entrenamiento debe tener una dirección clara.</h1>": "<h1>Una marca con método. Y con conversación.</h1>",
            "<p class=\"lead\">IBERFIT conecta evaluación, planificación, control y seguimiento para ayudarte a comprender tu punto de partida y avanzar hacia tus objetivos.</p><p class=\"hero-support\">Sabes qué estás trabajando, por qué se prioriza y cuándo conviene ajustar el plan.</p>": "<p class=\"lead\">IBERFIT tiene una forma de trabajar, pero no queremos que sientas que debes encajar en una plantilla. Queremos entenderte, explicarte las decisiones y mejorar el servicio cuando encontramos una forma mejor de ayudarte.</p><p class=\"hero-support\">La marca es IBERFIT. La experiencia debe seguir sintiéndose humana.</p>",
            "<h2>Criterio profesional, trato cercano y un proceso que puedes comprender.</h2>": "<h2>El método pone orden. La conversación lo hace humano.</h2>",
            '<div class="kicker">Lo que puedes esperar</div><h2>Un acompañamiento profesional que también se entiende.</h2>': '<div class="kicker">Nuestra promesa</div><h2>No podemos prometerte el mismo resultado que a otra persona. Sí podemos prometerte cómo vamos a trabajar.</h2>',
            '<article class="principle-row reveal"><h3>Decisiones explicadas</h3><p>Entiendes qué se está trabajando y qué motivo hay detrás de cada prioridad.</p></article>': '<article class="principle-row reveal"><h3>Escuchar antes de decidir</h3><p>Tu contexto forma parte de la decisión desde el principio.</p></article>',
            '<article class="principle-row reveal"><h3>Plan adaptado</h3><p>El entrenamiento responde a tu experiencia, disponibilidad, objetivos y evolución.</p></article>': '<article class="principle-row reveal"><h3>Explicar el porqué</h3><p>Queremos que puedas entender qué proponemos y qué motivo hay detrás.</p></article>',
            '<article class="principle-row reveal"><h3>Seguimiento real</h3><p>La respuesta al entrenamiento se revisa para ajustar cuando hace falta.</p></article>': '<article class="principle-row reveal"><h3>Revisar antes de repetir</h3><p>Si tu respuesta o tu realidad cambian, el plan también puede cambiar.</p></article>',
            '<article class="principle-row reveal"><h3>Continuidad</h3><p>La evaluación, las sesiones y los cambios forman parte de un mismo proceso.</p></article>': '<article class="principle-row reveal"><h3>Hablar con claridad</h3><p>Si una opción no tiene sentido para tu contexto, preferimos decirlo.</p></article>',
        },
        "metodo/index.html": {
            "<h1>Un método para decidir mejor.</h1>": "<h1>Un método para que cada decisión tenga sentido.</h1>",
            "<p class=\"lead\">Una estructura profesional que reduce improvisación sin convertir a las personas en números.</p><p class=\"hero-support\">Cada decisión debe poder explicarse, registrarse y revisarse.</p>": "<p class=\"lead\">No queremos que entrenes siguiendo instrucciones que no entiendes.</p><p class=\"hero-support\">El método nos ayuda a escuchar, ordenar la información y explicarte por qué proponemos cada paso. Después lo revisamos contigo.</p>",
            "<p class=\"hero-meta\">El método se mantiene en presencial, híbrido y a distancia.</p>": "<p class=\"hero-meta\">El mismo criterio, estés donde estés.</p>",
        },
        "diagnostico-iri/index.html": {
            "<p class=\"lead\">Una evaluación estructurada que convierte información relevante en prioridades y decisiones prácticas.</p><p class=\"hero-support\">No busca etiquetarte. Busca orientar el primer plan y dejar una base para revisar la evolución.</p>": "<p class=\"lead\">Antes de proponerte un plan, queremos conocerte un poco mejor.</p><p class=\"hero-support\">El IRI reúne la información que puede ayudarnos a decidir contigo cómo empezar y deja una referencia clara para revisar tu evolución.</p>",
        },
        "contacto/index.html": {
            "<p class=\"lead\">Puedes escribir directamente o utilizar el orientador breve para ordenar la consulta.</p><p class=\"hero-support\">No pedimos datos personales en el orientador. Tus respuestas solo se incorporan al mensaje si decides abrir WhatsApp.</p>": "<p class=\"lead\">Escríbenos aunque todavía no tengas claro qué necesitas.</p><p class=\"hero-support\">Podemos empezar por una conversación. Si prefieres, el orientador breve te ayuda a ordenar tu consulta sin enviar nada hasta que tú decides abrir WhatsApp.</p>",
        },
        "presencial/index.html": {
            "<p class=\"lead\">Sesiones presenciales con planificación individual, control técnico y seguimiento entre decisiones.</p><p class=\"hero-support\">Disponible en comunas seleccionadas de Santiago, según sector, horario y condiciones del espacio.</p>": "<p class=\"lead\">Si necesitas que estemos ahí contigo, la sesión presencial nos permite observar, corregir y adaptar en el momento.</p><p class=\"hero-support\">Antes de empezar, confirmamos contigo que ubicación, horario y espacio tengan sentido.</p>",
        },
        "hibrido/index.html": {
            "<p class=\"lead\">Combina sesiones presenciales estratégicas con trabajo independiente claramente pautado y revisado.</p><p class=\"hero-support\">La parte presencial depende de cobertura. La planificación y el seguimiento continúan entre sesiones.</p>": "<p class=\"lead\">Hay semanas en las que vernos en persona aporta mucho y otras en las que necesitas entrenar por tu cuenta sin perder dirección.</p><p class=\"hero-support\">La modalidad híbrida conecta ambos momentos dentro del mismo plan y seguimiento.</p>",
        },
        "online/index.html": {
            "<h1>Dirección profesional desde cualquier lugar.</h1>": "<h1>Estar lejos no debería significar entrenar sin dirección.</h1>",
            "<p class=\"lead\">Planificación individual, sesiones guiadas y seguimiento estructurado sin depender de una ubicación concreta.</p><p class=\"hero-support\">Disponible para cualquier persona, con independencia de su país, ciudad o experiencia previa.</p>": "<p class=\"lead\">Te damos un plan claro, lo adaptamos a tu entorno y revisamos contigo lo que va pasando, estés donde estés.</p><p class=\"hero-support\">No necesitas vivir cerca ni tener experiencia avanzada para sentirte acompañado.</p>",
        },
    }

    for old, new in refinements.get(rel, {}).items():
        text = text.replace(old, new)

    if rel == "sobre-iberfit/index.html":
        story = """<section class="section origin-section"><div class="container founder-grid"><div class="reveal"><div class="kicker">Nuestra historia</div><h2>IBERFIT no nació para añadir otra rutina. Nació para que entrenar tuviera más sentido.</h2></div><div class="founder-copy reveal"><p>IBERFIT parte de una pregunta sencilla: ¿por qué tantas personas entrenan sin tener claro si lo que hacen tiene sentido para ellas?</p><p>La pregunta nace de algo que se repetía demasiado: rutinas genéricas, mediciones que nadie explicaba y planes que seguían iguales aunque cambiara la vida de la persona.</p><p>Su fundador se formó universitariamente en España. Después vivió una etapa en Alemania, regresó a España y continuó allí su experiencia profesional antes de trasladarse a Chile. Ese recorrido fue dando forma a una manera exigente de trabajar: entender antes de prescribir, explicar las decisiones, observar la respuesta y ajustar cuando hace falta.</p><div class="brand-journey" aria-label="Recorrido que da origen a IBERFIT"><article><span>01</span><strong>España</strong><p>Formación universitaria y primeras bases de una forma de trabajar con criterio.</p></article><article><span>02</span><strong>Alemania</strong><p>Una etapa de vida en otro contexto europeo que amplió la perspectiva.</p></article><article><span>03</span><strong>España</strong><p>Regreso y experiencia profesional trabajando en España.</p></article><article><span>04</span><strong>Chile</strong><p>El lugar donde ese recorrido termina dando forma a IBERFIT como marca.</p></article></div><p>Después fueron apareciendo necesidades nuevas: evaluar mejor el punto de partida, conectar lo que ocurre entre sesiones y poder acompañar sin depender siempre de un lugar. El Diagnóstico IRI, el seguimiento y las distintas modalidades nacen de esas necesidades, no de querer acumular servicios.</p><p>Hoy IBERFIT sigue creciendo con la misma regla: si algo no ayuda a entender mejor, decidir mejor o sostener mejor el proceso, no aporta.</p></div></div></section><section class="section section-cream"><div class="container"><div class="section-intro reveal"><div class="kicker">Una marca que sigue mejorando</div><h2>Mejorar no es añadir más. Es aportar más.</h2><p class="lead">Cada herramienta, cada cambio y cada nueva forma de acompañar tiene que ganarse su lugar ayudando a la persona que entrena.</p></div><div class="principle-stack"><article class="principle-row reveal"><h3>Entender antes de proponer</h3><p>Empezamos por tu contexto y tu punto de partida, no por una rutina que ya estaba escrita.</p></article><article class="principle-row reveal"><h3>Convertir datos en decisiones</h3><p>El IRI y el seguimiento sirven para explicar qué estamos viendo y qué conviene hacer con esa información.</p></article><article class="principle-row reveal"><h3>Acompañar también entre sesiones</h3><p>El valor no termina cuando acaba una sesión. Lo que ocurre después también ayuda a decidir el siguiente paso.</p></article><article class="principle-row reveal"><h3>Usar tecnología sin perder lo humano</h3><p>La tecnología puede ayudarnos a recordar, comparar y explicar mejor. La decisión y la conversación siguen siendo humanas.</p></article></div></div></section>"""
        text = re.sub(
            r'<section class="section origin-section">.*?</section>',
            story,
            text,
            count=1,
            flags=re.S,
        )

    if rel == "index.html" and "Mejorar no es añadir más. Es aportar más." not in text:
        teaser = """<section class="section section-cream"><div class="container"><div class="section-intro reveal"><div class="kicker">Por qué existe IBERFIT</div><h2>Mejorar no es añadir más. Es aportar más.</h2><p class="lead">IBERFIT nació de una pregunta sencilla: ¿cómo hacer que una persona no solo entrene, sino que entienda lo que está haciendo y pueda sostenerlo? Desde entonces, cada mejora tiene que aportar en una de tres cosas.</p><a class="text-link" href="/sobre-iberfit/">Conocer la historia de IBERFIT</a></div><div class="principle-stack"><article class="principle-row reveal"><h3>Entender mejor</h3><p>Escuchamos tu contexto antes de proponerte qué hacer.</p></article><article class="principle-row reveal"><h3>Decidir mejor</h3><p>Los datos solo valen si ayudan a tomar una decisión mejor.</p></article><article class="principle-row reveal"><h3>Sostener mejor</h3><p>El plan tiene que poder adaptarse cuando tu vida cambia.</p></article></div></div></section>"""
        text = text.replace('<section class="section review-proof">', teaser + '<section class="section review-proof">', 1)

    return text


def refine_client_language(text: str, rel: str) -> str:
    """Segunda pasada: hablar desde la experiencia del cliente, no desde la operación interna."""
    replacements = {
        "metodo/index.html": {
            "La personalización comienza con información, no con preferencias del entrenador.": "No empezamos por lo que al entrenador le gusta hacer. Empezamos por lo que tú necesitas.",
            "La estructura protege la calidad; el contenido responde a la persona.": "La estructura nos ayuda a mantener la calidad; lo que hacemos dentro de ella se adapta a ti.",
            "Solo se registra aquello que puede ayudar a interpretar o ajustar.": "Guardamos solo la información que puede ayudarnos a entender cómo vas o a decidir un cambio.",
            "Una rutina no se mantiene por inercia cuando el contexto cambia.": "Si tu contexto cambia, no seguimos con lo mismo por inercia.",
            "Se detiene, adapta o sustituye el ejercicio y se registra el motivo.": "Paramos, adaptamos o cambiamos el ejercicio y dejamos claro por qué.",
            "Se reorganiza la dosis para proteger continuidad y calidad.": "Reorganizamos la semana para que puedas mantener continuidad sin perder calidad.",
            "Sesiones, respuesta y ajustes se conectan dentro del proceso.": "Lo que pasó en una sesión no se pierde: sirve para decidir la siguiente.",
            "IBERFIT protege una forma común de evaluar y revisar.": "Aunque cambie la modalidad, queremos que la forma de evaluar y revisar siga siendo coherente.",
        },
        "diagnostico-iri/index.html": {
            "La bioimpedancia aporta información orientativa y se interpreta junto con el resto de la evaluación.": "La bioimpedancia nos da una referencia más; nunca la leemos aislada del resto.",
            "Mediciones útiles para establecer una referencia y revisar cambios cuando corresponde.": "Tomamos medidas que puedan servir como referencia cuando volvamos a revisar cómo vas.",
            "Observación de movimientos relevantes para seleccionar y adaptar ejercicios.": "Te vemos moverte para elegir mejor qué ejercicios y variantes tienen sentido para ti.",
            "Lectura por patrones para identificar una base funcional y prioridades de desarrollo.": "Miramos la fuerza por patrones para entender tu base y ordenar prioridades.",
            "Respuesta al esfuerzo y recuperación mediante pruebas apropiadas al contexto.": "Vemos cómo respondes al esfuerzo y cómo recuperas con pruebas acordes a tu contexto.",
            "No todo puede progresar a la vez. Se ordenan las necesidades más relevantes.": "No intentamos mejorar todo a la vez. Priorizamos lo que más puede ayudarte ahora.",
            "Se define una dosis y una selección de ejercicios coherentes con el punto de partida.": "A partir de ahí definimos cuánto, cómo y con qué ejercicios conviene empezar.",
        },
        "presencial/index.html": {
            "La sesión responde a prioridades definidas, no a una rutina improvisada.": "La sesión tiene un propósito claro; no llegamos a improvisar qué toca.",
            "Correcciones y adaptaciones durante la ejecución.": "Corregimos y adaptamos mientras entrenas, no días después.",
            "Volumen, intensidad y descansos se definen y registran.": "Definimos carga y descansos con un motivo y dejamos registro para poder ajustar.",
            "Lo ocurrido en la sesión orienta la siguiente decisión.": "Lo que pasa hoy nos ayuda a decidir qué hacer la próxima vez.",
            "Se revisa el objetivo de la sesión y el estado actual.": "Antes de empezar revisamos qué toca y cómo llegas ese día.",
            "Se supervisa ejecución, esfuerzo y respuesta.": "Durante la sesión observamos técnica, esfuerzo y respuesta.",
            "Se registra lo relevante y se ajusta lo siguiente.": "Después guardamos lo importante para no empezar de cero en la siguiente sesión.",
        },
        "hibrido/index.html": {
            "El registro de la sesión permite conectar lo que ocurre hoy con la siguiente decisión.": "Lo que haces por tu cuenta no se pierde: lo usamos para decidir el siguiente paso.",
            "Se utilizan donde la supervisión directa aporta mayor valor.": "Reservamos las sesiones presenciales para lo que realmente merece ser visto y corregido en directo.",
            "Las sesiones autónomas incluyen instrucciones, carga y alternativas.": "Cuando entrenas por tu cuenta, recibes instrucciones, carga y alternativas claras.",
            "La respuesta del cliente no queda fuera del proceso.": "Lo que nos cuentas después también forma parte del proceso.",
            "Lo presencial y lo autónomo forman un mismo plan.": "Todo forma parte del mismo plan, aunque unas sesiones las hagamos juntos y otras no.",
            "Se comprueba adherencia, respuesta y necesidad de cambios.": "Revisamos qué pudiste hacer, cómo respondiste y qué conviene cambiar.",
        },
        "online/index.html": {
            "Cada sesión tiene estructura, objetivo y criterios de progresión.": "Cada sesión te dice qué hacer, para qué y cómo saber cuándo avanzar.",
            "Repeticiones, tiempo, distancia o esfuerzo se definen según el ejercicio.": "La carga se expresa de una forma que puedas aplicar con claridad en cada ejercicio.",
            "La sesión contempla espacio, material, experiencia y limitaciones.": "El plan parte del espacio, el material, la experiencia y las limitaciones que realmente tienes.",
            "Recibes sesiones comprensibles y adaptadas a tu entorno.": "Recibes sesiones que puedes entender y aplicar en tu entorno real.",
            "Se revisa lo realizado y se modifica la planificación cuando corresponde.": "Revisamos lo que hiciste y cambiamos el plan cuando hay una razón para hacerlo.",
        },
    }
    for old, new in replacements.get(rel, {}).items():
        text = text.replace(old, new)
    return text


def humanize_ctas(text: str, rel: str) -> str:
    """CTA de marca: claros y humanos, sin sonar administrativos."""
    text = text.replace(">Solicitar IRI</a>", ">Empezar por el IRI</a>")

    page_replacements = {
        "index.html": {
            ">Solicitar orientación inicial</a>": ">Hablar con IBERFIT</a>",
            ">Solicitar Diagnóstico IRI</a>": ">Empezar por el IRI</a>",
        },
        "diagnostico-iri/index.html": {
            ">Solicitar Diagnóstico IRI</a>": ">Quiero hacer mi Diagnóstico IRI</a>",
        },
        "metodo/index.html": {
            ">Solicitar Diagnóstico IRI</a>": ">Empezar por el IRI</a>",
        },
        "presencial/index.html": {
            ">Solicitar orientación</a>": ">Hablar con IBERFIT</a>",
            ">Usar el orientador de modalidad</a>": ">Ver qué opción encaja conmigo</a>",
            ">Solicitar Diagnóstico IRI</a>": ">Empezar por el IRI</a>",
        },
        "hibrido/index.html": {
            ">Solicitar orientación</a>": ">Hablar con IBERFIT</a>",
            ">Usar el orientador de modalidad</a>": ">Ver qué opción encaja conmigo</a>",
            ">Solicitar Diagnóstico IRI</a>": ">Empezar por el IRI</a>",
        },
        "online/index.html": {
            ">Solicitar orientación</a>": ">Hablar con IBERFIT</a>",
            ">Usar el orientador de modalidad</a>": ">Ver qué opción encaja conmigo</a>",
            ">Solicitar Diagnóstico IRI</a>": ">Empezar por el IRI</a>",
        },
        "sobre-iberfit/index.html": {
            ">Solicitar orientación inicial</a>": ">Hablar con IBERFIT</a>",
            ">Solicitar Diagnóstico IRI</a>": ">Empezar por el IRI</a>",
        },
        "contacto/index.html": {
            ">Solicitar Diagnóstico IRI</a>": ">Empezar por el IRI</a>",
        },
    }
    for old, new in page_replacements.get(rel, {}).items():
        text = text.replace(old, new)

    if rel != "diagnostico-iri/index.html":
        text = text.replace(">Solicitar Diagnóstico IRI</a>", ">Empezar por el IRI</a>")
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



def upgrade_photo_fidelity(text: str) -> str:
    """Deja que el navegador elija 640/960/1448 según ancho real y densidad de píxel."""
    def replace_picture(match):
        block=match.group(0)
        source=re.search(r'src="/assets/(photo-[a-z0-9-]+)-1448\.webp"',block,flags=re.I)
        if not source:
            return block
        base=source.group(1)
        variants=(640,960,1448)
        if not all((DST/"assets"/f"{base}-{width}.webp").exists() for width in variants):
            return block
        block=re.sub(r'<source\b[^>]*>',"",block,flags=re.I)
        src=f'/assets/{base}-1448.webp'
        srcset=", ".join(f"/assets/{base}-{width}.webp {width}w" for width in variants)
        sizes="(max-width: 850px) calc(100vw - 32px), (max-width: 1180px) 54vw, 690px"
        if ' srcset=' not in block:
            block=block.replace(
                f'src="{src}"',
                f'src="{src}" srcset="{srcset}" sizes="{sizes}"',
                1,
            )
        return block

    return re.sub(r"<picture>.*?</picture>",replace_picture,text,flags=re.I|re.S)


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
        if "photo-story-media" in text and "-1448.webp" in text:
            if " 640w" not in text or " 960w" not in text or " 1448w" not in text or ' sizes="' not in text:
                fail(f"{rel}: fotografía sin selección por densidad")
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
        fh.write("\n\n"+CSS_ADD+"\n\n"+PREMIUM_INTERACTION_CSS)

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
    app_text += r"""
;document.addEventListener('DOMContentLoaded',()=>{const dock=document.querySelector('.device-dock');if(!dock)return;const hero=document.querySelector('.hero,.page-hero');let ticking=false;const update=()=>{const threshold=hero?Math.min(140,Math.max(72,hero.offsetHeight*.18)):80;dock.classList.toggle('is-visible',window.scrollY>threshold);ticking=false};const requestUpdate=()=>{if(!ticking){ticking=true;requestAnimationFrame(update)}};update();addEventListener('scroll',requestUpdate,{passive:true});addEventListener('resize',requestUpdate,{passive:true})});
"""

    app_text += r"""
;document.addEventListener('DOMContentLoaded',()=>{const reduce=matchMedia('(prefers-reduced-motion: reduce)');const fine=matchMedia('(hover:hover) and (pointer:fine) and (min-width:1024px)');const compact=matchMedia('(max-width:640px)');const surfaces=Array.from(document.querySelectorAll('.photo-story-media,.report-preview-v2,.client-review,.review-proof-card,.alternative-note,.price-panel,.contact-option'));surfaces.forEach(el=>el.classList.add('premium-surface'));const syncMotion=()=>document.documentElement.classList.toggle('motion-rich',fine.matches&&!reduce.matches);const watch=(mq,fn)=>{if(mq.addEventListener)mq.addEventListener('change',fn);else mq.addListener(fn)};syncMotion();watch(fine,syncMotion);watch(reduce,syncMotion);surfaces.forEach(el=>{let frame=0;el.addEventListener('pointermove',event=>{if(!fine.matches||reduce.matches)return;if(frame)cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{const rect=el.getBoundingClientRect();if(!rect.width||!rect.height)return;const x=Math.max(0,Math.min(1,(event.clientX-rect.left)/rect.width));const y=Math.max(0,Math.min(1,(event.clientY-rect.top)/rect.height));el.style.setProperty('--mx',(x*100)+'%');el.style.setProperty('--my',(y*100)+'%');el.style.setProperty('--rx',((0.5-y)*1.15)+'deg');el.style.setProperty('--ry',((x-0.5)*1.35)+'deg')})},{passive:true});el.addEventListener('pointerleave',()=>{if(frame)cancelAnimationFrame(frame);el.style.setProperty('--mx','50%');el.style.setProperty('--my','50%');el.style.setProperty('--rx','0deg');el.style.setProperty('--ry','0deg')},{passive:true})});const rails=Array.from(document.querySelectorAll('.system-rail,.method-cycle'));const isEn=(document.documentElement.lang||'').toLowerCase().startsWith('en');const syncRails=()=>rails.forEach(rail=>{rail.classList.toggle('premium-rail',compact.matches);if(compact.matches){rail.tabIndex=0;if(!rail.dataset.premiumLabel){rail.dataset.premiumLabel='1';rail.setAttribute('aria-label',isEn?'Training process steps. Swipe horizontally.':'Etapas del proceso. Desliza horizontalmente.')}}else{rail.removeAttribute('tabindex');if(rail.dataset.premiumLabel){rail.removeAttribute('aria-label');delete rail.dataset.premiumLabel}}});syncRails();watch(compact,syncRails)});
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
            text=specialize_local_page(text, rel)
            text=humanize_brand_voice(text, rel)
            text=refine_client_language(text, rel)
            text=humanize_ctas(text, rel)
        if rel in {"contacto/index.html","en/contact/index.html"}:
            text=text.replace(
                '<form class="orientador-card reveal" data-orientador-form="" novalidate="">',
                '<form class="orientador-card reveal" data-orientador-form="" novalidate=""><p class="sr-only" data-orientador-status="" aria-live="polite"></p>',
            )
        text=upgrade_photo_fidelity(text)
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
        "- Controles automáticos contra regresiones de nomenclatura, IRI y versionado.\n"
        "- Fotografía responsive sensible a densidad para pantallas Retina/alta resolución.\n"
        "- Interacción premium adaptativa: profundidad en escritorio, composición táctil específica en móvil/tableta y respeto estricto de reducir movimiento.\n",
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
