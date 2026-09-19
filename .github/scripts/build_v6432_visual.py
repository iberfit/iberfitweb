from pathlib import Path
import re
import shutil

ROOT = Path('candidate/v628')
SOURCE = Path('.github/assets/v6432')
ASSETS = ROOT / 'assets'
VERSION = ROOT / 'VERSION'
CHANGELOG = ROOT / 'CHANGELOG.md'
HEADERS = ROOT / '_headers'

BASE_VERSION = '6.43.1'
NEW_VERSION = '6.43.2'
CSS_LINK = '<link href="/assets/visual.v6432.css" rel="stylesheet"/>'
A11Y_LINK = '<link href="/assets/a11y.v6431.css" rel="stylesheet"/>'

SCREEN_ASSETS = {
    'app-online-plan.webp': (480, 318),
    'app-online-session.webp': (400, 434),
    'app-online-progress.webp': (400, 411),
    'app-hybrid-feedback.webp': (400, 336),
}

PAGES = [
    ROOT / 'online/index.html',
    ROOT / 'hibrido/index.html',
    ROOT / 'en/online/index.html',
    ROOT / 'en/hybrid/index.html',
]


def fail(message: str):
    raise SystemExit(message)


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        fail(f'{label}: expected exactly one replacement, got {count}')
    return updated


def add_css_link(text: str, label: str) -> str:
    if text.count(CSS_LINK):
        fail(f'{label}: visual CSS link already present')
    if text.count(A11Y_LINK) != 1:
        fail(f'{label}: expected exactly one V6.43.1 accessibility CSS link')
    return text.replace(A11Y_LINK, A11Y_LINK + CSS_LINK, 1)


ONLINE_ES = '''<section class="section app-story-section" id="experiencia-app"><div class="container app-story app-story--online">
<div class="app-story-copy reveal"><div class="kicker">La experiencia online</div><h2>Tu entrenamiento no vive en un PDF.</h2><p class="lead">Planificación, sesión y evolución están conectadas en un mismo entorno para que sepas qué toca, cómo registrarlo y qué cambia después.</p><div class="app-story-points"><article><span>01</span><div><strong>Plan visible</strong><p>Próximas sesiones, objetivos y contexto en un solo lugar.</p></div></article><article><span>02</span><div><strong>Ejecución guiada</strong><p>Series, carga, esfuerzo, descansos y alternativas durante la sesión.</p></div></article><article><span>03</span><div><strong>Evolución con contexto</strong><p>Adherencia y tendencias aparecen cuando los datos permiten interpretarlas.</p></div></article></div><p class="app-visual-note">Capturas reales de la app IBERFIT · entorno de demostración con datos sintéticos.</p></div>
<div class="app-story-stage reveal" aria-label="Vistas reales de planificación, sesión y progreso en la app IBERFIT"><figure class="app-screen app-screen--plan"><img src="/assets/app-online-plan.webp" width="480" height="318" loading="lazy" decoding="async" alt="Vista real de la planificación y próximas sesiones en la app IBERFIT."/></figure><figure class="app-screen app-screen--session"><img src="/assets/app-online-session.webp" width="400" height="434" loading="lazy" decoding="async" alt="Vista real de una sesión guiada en curso en la app IBERFIT."/></figure><figure class="app-screen app-screen--progress"><img src="/assets/app-online-progress.webp" width="400" height="411" loading="lazy" decoding="async" alt="Vista real del seguimiento de progreso en la app IBERFIT."/></figure></div>
</div></section><section class="section section-cream"><div class="container"><div class="section-intro reveal"><div class="kicker">Dirección de principio a fin</div><h2>Antes, durante y después de cada sesión.</h2></div><div class="continuity-rail"><article class="continuity-step reveal"><span>01</span><h3>Plan claro</h3><p>Sabes qué toca y con qué objetivo.</p></article><article class="continuity-step reveal"><span>02</span><h3>Sesión guiada</h3><p>La ejecución conserva instrucciones y alternativas.</p></article><article class="continuity-step reveal"><span>03</span><h3>Feedback útil</h3><p>Tu respuesta queda registrada sin añadir fricción innecesaria.</p></article><article class="continuity-step reveal"><span>04</span><h3>Revisión profesional</h3><p>El siguiente ajuste parte de lo que realmente ocurrió.</p></article></div></div></section>'''

ONLINE_EN = '''<section class="section app-story-section" id="app-experience"><div class="container app-story app-story--online">
<div class="app-story-copy reveal"><div class="kicker">The online experience</div><h2>Your training does not live in a PDF.</h2><p class="lead">Planning, execution and progress stay connected in one environment, so you can see what is next, record what happened and understand what changes.</p><div class="app-story-points"><article><span>01</span><div><strong>Plan visible</strong><p>Upcoming sessions, goals and context in one place.</p></div></article><article><span>02</span><div><strong>Guided execution</strong><p>Sets, workload, effort, recovery and alternatives during the session.</p></div></article><article><span>03</span><div><strong>Progress with context</strong><p>Adherence and trends appear when the available data can support them.</p></div></article></div><p class="app-visual-note">Real IBERFIT app screens · demonstration environment with synthetic data.</p></div>
<div class="app-story-stage reveal" aria-label="Real planning, live-session and progress views from the IBERFIT app"><figure class="app-screen app-screen--plan"><img src="/assets/app-online-plan.webp" width="480" height="318" loading="lazy" decoding="async" alt="Real planning and upcoming-session view in the IBERFIT app."/></figure><figure class="app-screen app-screen--session"><img src="/assets/app-online-session.webp" width="400" height="434" loading="lazy" decoding="async" alt="Real guided live-session view in the IBERFIT app."/></figure><figure class="app-screen app-screen--progress"><img src="/assets/app-online-progress.webp" width="400" height="411" loading="lazy" decoding="async" alt="Real progress-review view in the IBERFIT app."/></figure></div>
</div></section><section class="section section-cream"><div class="container"><div class="section-intro reveal"><div class="kicker">Direction from start to finish</div><h2>Before, during and after every session.</h2></div><div class="continuity-rail"><article class="continuity-step reveal"><span>01</span><h3>Clear plan</h3><p>You know what is next and why.</p></article><article class="continuity-step reveal"><span>02</span><h3>Guided session</h3><p>Execution keeps instructions and practical alternatives.</p></article><article class="continuity-step reveal"><span>03</span><h3>Useful feedback</h3><p>Your response is recorded without unnecessary friction.</p></article><article class="continuity-step reveal"><span>04</span><h3>Professional review</h3><p>The next adjustment starts from what actually happened.</p></article></div></div></section>'''

HYBRID_ES = '''<section class="section hybrid-continuity-section"><div class="container hybrid-continuity">
<div class="hybrid-continuity-copy reveal"><div class="kicker">Entre una sesión y la siguiente</div><h2>Lo presencial continúa cuando te vas.</h2><p class="lead">La sesión en persona no queda aislada: lo que haces, registras y nos cuentas sigue dentro del mismo proceso.</p><div class="app-story-points"><article><span>01</span><div><strong>Supervisión directa</strong><p>Usamos el encuentro presencial para observar, corregir y progresar donde más aporta.</p></div></article><article><span>02</span><div><strong>Trabajo guiado</strong><p>Fuera de la sesión sigues teniendo objetivos, instrucciones y alternativas claras.</p></div></article><article><span>03</span><div><strong>Feedback y ajuste</strong><p>Lo que registras conecta esa sesión con la siguiente decisión.</p></div></article></div><p class="app-visual-note">Captura real de la app IBERFIT · cierre y feedback de sesión en entorno de demostración.</p></div>
<figure class="hybrid-app-screen app-screen reveal"><img src="/assets/app-hybrid-feedback.webp" width="400" height="336" loading="lazy" decoding="async" alt="Vista real del cierre y feedback de una sesión en la app IBERFIT."/><figcaption>El feedback no termina la sesión: alimenta el siguiente ajuste.</figcaption></figure>
</div></section>'''

HYBRID_EN = '''<section class="section hybrid-continuity-section"><div class="container hybrid-continuity">
<div class="hybrid-continuity-copy reveal"><div class="kicker">Between one session and the next</div><h2>In-person work continues after you leave.</h2><p class="lead">The in-person session is not isolated: what you do, record and report stays inside the same process.</p><div class="app-story-points"><article><span>01</span><div><strong>Direct supervision</strong><p>In-person time is used for observation, correction and progression where it adds most value.</p></div></article><article><span>02</span><div><strong>Guided work</strong><p>Between sessions you still have clear goals, instructions and alternatives.</p></div></article><article><span>03</span><div><strong>Feedback and adjustment</strong><p>What you record connects that session with the next decision.</p></div></article></div><p class="app-visual-note">Real IBERFIT app screen · session close and feedback in a demonstration environment.</p></div>
<figure class="hybrid-app-screen app-screen reveal"><img src="/assets/app-hybrid-feedback.webp" width="400" height="336" loading="lazy" decoding="async" alt="Real session-close and feedback view in the IBERFIT app."/><figcaption>Feedback does not just close the session: it informs the next adjustment.</figcaption></figure>
</div></section>'''

OLD_MIDDLE_PATTERN = r'<section class="section"><div class="container"><div class="scope-bar reveal">.*?</section><section class="section section-cream"><div class="container">.*?</section>(?=<section class="section"><div class="container fit-split">)'

CSS = r'''/* IBERFIT WEB V6.43.2 — visual storytelling with real product evidence */
.app-story-section{background:var(--green-dark,#173f2c);color:var(--cream,#f7f4ee);overflow:hidden}
.app-story{display:grid;grid-template-columns:minmax(0,.83fr) minmax(520px,1.17fr);gap:clamp(42px,6vw,88px);align-items:center}
.app-story-copy{max-width:590px}.app-story-copy h2{color:var(--cream,#f7f4ee);max-width:14ch}.app-story-copy>.lead{color:rgba(247,244,238,.86);max-width:55ch}.app-story-copy .kicker{color:var(--gold-light,#d9b568)}
.app-story-points{display:grid;gap:0;margin-top:clamp(28px,4vw,42px);border-top:1px solid rgba(217,181,104,.26)}
.app-story-points article{display:grid;grid-template-columns:42px 1fr;gap:16px;padding:18px 0;border-bottom:1px solid rgba(217,181,104,.18)}
.app-story-points span{font:700 .78rem/1 var(--font-sans,Arial,sans-serif);letter-spacing:.12em;color:var(--gold-light,#d9b568);padding-top:.28rem}.app-story-points strong{display:block;color:inherit;font-size:1.02rem}.app-story-points p{margin:.32rem 0 0;color:inherit;opacity:.76;line-height:1.55}
.app-visual-note{margin:20px 0 0;font-size:.86rem;line-height:1.5;opacity:.67}
.app-story-stage{position:relative;min-height:610px;isolation:isolate}.app-screen{margin:0;border:1px solid rgba(31,61,43,.15);border-radius:20px;overflow:hidden;background:#f7f4ee;box-shadow:0 22px 55px rgba(2,17,12,.18)}.app-screen img{display:block;width:100%;height:auto}
.app-story-stage .app-screen{position:absolute}.app-screen--plan{width:min(78%,480px);right:3%;top:4%;z-index:1}.app-screen--session{width:min(54%,400px);left:0;bottom:1%;z-index:3}.app-screen--progress{width:min(52%,400px);right:0;bottom:2%;z-index:2}
.continuity-rail{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:1px solid rgba(31,61,43,.2);border-bottom:1px solid rgba(31,61,43,.2)}.continuity-step{padding:25px 22px 26px;border-right:1px solid rgba(31,61,43,.16)}.continuity-step:first-child{padding-left:0}.continuity-step:last-child{border-right:0;padding-right:0}.continuity-step>span{display:block;color:var(--gold-text,#806216);font-size:.76rem;font-weight:700;letter-spacing:.12em;margin-bottom:16px}.continuity-step h3{margin:0 0 8px;font-size:1.05rem}.continuity-step p{margin:0;line-height:1.58;opacity:.76}
.hybrid-continuity-section{background:var(--cream,#f7f4ee)}.hybrid-continuity{display:grid;grid-template-columns:minmax(0,1fr) minmax(360px,.86fr);gap:clamp(42px,7vw,96px);align-items:center}.hybrid-continuity-copy{max-width:660px}.hybrid-continuity-copy h2{max-width:15ch}.hybrid-continuity-copy .app-story-points{border-top-color:rgba(31,61,43,.18)}.hybrid-continuity-copy .app-story-points article{border-bottom-color:rgba(31,61,43,.14)}.hybrid-continuity-copy .app-story-points span{color:var(--gold-text,#806216)}.hybrid-app-screen{max-width:560px;justify-self:end}.hybrid-app-screen figcaption{padding:13px 16px 15px;color:rgba(31,61,43,.72);font-size:.84rem;line-height:1.45;background:#fbf8f3}
@media(hover:hover) and (pointer:fine){.app-story-stage .app-screen,.hybrid-app-screen{transition:transform 220ms cubic-bezier(.2,.7,.2,1),box-shadow 220ms cubic-bezier(.2,.7,.2,1)}.app-story-stage:hover .app-screen--plan{transform:translateY(-3px)}.app-story-stage:hover .app-screen--session{transform:translate(-2px,2px)}.app-story-stage:hover .app-screen--progress{transform:translate(2px,1px)}.hybrid-app-screen:hover{transform:translateY(-3px);box-shadow:0 26px 62px rgba(31,61,43,.16)}}
@media(max-width:980px){.app-story{grid-template-columns:1fr;gap:42px}.app-story-copy{max-width:720px}.app-story-stage{min-height:560px;max-width:760px;width:100%;margin-inline:auto}.hybrid-continuity{grid-template-columns:1fr}.hybrid-app-screen{justify-self:start;max-width:620px}.continuity-rail{grid-template-columns:repeat(2,minmax(0,1fr))}.continuity-step:nth-child(2){border-right:0}.continuity-step:nth-child(-n+2){border-bottom:1px solid rgba(31,61,43,.16)}.continuity-step:nth-child(3){padding-left:0}}
@media(max-width:640px){.app-story-stage{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(82%,1fr);gap:14px;min-height:0;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px 18px 18px 0;overscroll-behavior-inline:contain}.app-story-stage .app-screen{position:relative!important;inset:auto!important;width:auto!important;scroll-snap-align:start;box-shadow:0 12px 30px rgba(2,17,12,.14)}.continuity-rail{grid-template-columns:1fr}.continuity-step,.continuity-step:first-child,.continuity-step:nth-child(3),.continuity-step:last-child{padding:19px 0;border-right:0;border-bottom:1px solid rgba(31,61,43,.14)}.continuity-step:last-child{border-bottom:0}.hybrid-app-screen{width:100%}.app-story-points article{grid-template-columns:34px 1fr;gap:12px}}
@media(prefers-reduced-motion:reduce){.app-story-stage .app-screen,.hybrid-app-screen{transition:none!important;transform:none!important}}
'''

# Baseline checks
if VERSION.read_text(encoding='utf-8').strip() != BASE_VERSION:
    fail(f'expected VERSION {BASE_VERSION}')
if len(list(ROOT.rglob('*.html'))) != 33:
    fail('expected exactly 33 HTML routes')
for page in PAGES:
    if not page.is_file():
        fail(f'missing page: {page}')

# Copy curated synthetic QA captures into the candidate.
for name in SCREEN_ASSETS:
    src = SOURCE / name
    if not src.is_file() or src.stat().st_size < 3000:
        fail(f'missing or implausibly small screenshot source: {src}')
    shutil.copyfile(src, ASSETS / name)

# CSS is scoped by class names and linked only on Online/Hybrid ES+EN.
(ASSETS / 'visual.v6432.css').write_text(CSS, encoding='utf-8')

page_configs = {
    ROOT / 'online/index.html': ONLINE_ES,
    ROOT / 'en/online/index.html': ONLINE_EN,
    ROOT / 'hibrido/index.html': HYBRID_ES,
    ROOT / 'en/hybrid/index.html': HYBRID_EN,
}
for page, replacement in page_configs.items():
    text = page.read_text(encoding='utf-8')
    text = add_css_link(text, page.as_posix())
    text = replace_once(text, OLD_MIDDLE_PATTERN, replacement, page.as_posix())
    page.write_text(text, encoding='utf-8')

# Version, changelog and immutable asset caching.
VERSION.write_text(NEW_VERSION + '\n', encoding='utf-8')
entry = '''## 6.43.2 — Visual storytelling for Online + Hybrid\n\n- Rebalanced Online from explanatory blocks toward real product evidence using current IBERFIT app screens captured against synthetic QA data.\n- Added a real app feedback screen to Hybrid to connect in-person work with between-session continuity.\n- Reduced visible repetition while preserving existing fit guidance, AEO answers and final conversion paths.\n- Added responsive, reduced-motion-safe visual composition with no production dependency on GitHub artifacts.\n\n'''
old_changelog = CHANGELOG.read_text(encoding='utf-8')
if '## 6.43.2 — Visual storytelling for Online + Hybrid' not in old_changelog:
    CHANGELOG.write_text(entry + old_changelog, encoding='utf-8')

headers = HEADERS.read_text(encoding='utf-8').rstrip() + '\n'
cache_paths = ['/assets/visual.v6432.css'] + [f'/assets/{name}' for name in SCREEN_ASSETS]
for asset_path in cache_paths:
    block = f'''\n{asset_path}\n  ! Cache-Control\n  Cache-Control: public, max-age=31536000, immutable\n'''
    if asset_path not in headers:
        headers += block
HEADERS.write_text(headers.rstrip() + '\n', encoding='utf-8')

print({'version': NEW_VERSION, 'pages': [p.relative_to(ROOT).as_posix() for p in PAGES], 'screens': SCREEN_ASSETS})
