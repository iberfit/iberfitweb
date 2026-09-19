from pathlib import Path
import shutil

ROOT = Path('candidate/v628')
SOURCE = Path('.github/assets/v6433/app-online-plan.webp')
ASSETS = ROOT / 'assets'
VERSION = ROOT / 'VERSION'
CHANGELOG = ROOT / 'CHANGELOG.md'
HEADERS = ROOT / '_headers'

BASE_VERSION = '6.43.2'
NEW_VERSION = '6.43.3'
CSS_NAME = 'polish.v6433.css'
CSS_LINK = f'<link href="/assets/{CSS_NAME}" rel="stylesheet"/>'
PLAN_NAME = 'app-online-plan-v6433.webp'


def fail(message: str):
    raise SystemExit(message)


def replace_exact(path: Path, old: str, new: str, label: str):
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        fail(f'{label}: expected exactly one match, got {count}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


if VERSION.read_text(encoding='utf-8').strip() != BASE_VERSION:
    fail(f'expected VERSION {BASE_VERSION}')
if not SOURCE.exists() or SOURCE.stat().st_size < 5000:
    fail('missing corrected Online plan crop')

html_files = sorted(ROOT.rglob('*.html'))
if len(html_files) != 33:
    fail(f'expected 33 HTML files, got {len(html_files)}')

for path in html_files:
    text = path.read_text(encoding='utf-8')
    if CSS_LINK in text:
        fail(f'{path}: V6.43.3 CSS already linked')
    if '</head>' not in text:
        fail(f'{path}: missing </head>')
    path.write_text(text.replace('</head>', CSS_LINK + '</head>', 1), encoding='utf-8')

# Replace the broken Online plan crop with a fresh crop from the current authenticated QA client surface.
for rel in ('online/index.html', 'en/online/index.html'):
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    old = 'src="/assets/app-online-plan.webp" width="480" height="318"'
    new = f'src="/assets/{PLAN_NAME}" width="760" height="387"'
    if text.count(old) != 1:
        fail(f'{rel}: expected old Online plan image once')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')

# Humanise the brand origin without changing the underlying chronology or methodological claims.
about_es = ROOT / 'sobre-iberfit/index.html'
replace_exact(
    about_es,
    'La marca nace de una formación universitaria en España y de un recorrido europeo que permitió conocer de cerca dos contextos distintos, el español y el alemán, antes de consolidarse en Chile. De ese contraste se extrae una forma de trabajar propia: evaluar antes de prescribir, planificar con intención, controlar la respuesta y ajustar con criterio.',
    'La marca nace de una pasión por el entrenamiento y de una inquietud constante por la salud, acompañadas por una formación universitaria específica en España y por un recorrido europeo que permitió conocer de cerca los contextos español y alemán antes de consolidarse en Chile. Esa combinación de vocación, formación y experiencia fue dando forma a una manera propia de trabajar: evaluar antes de prescribir, planificar con intención, controlar la respuesta y ajustar con criterio.',
    'Spanish origin story',
)
replace_exact(
    about_es,
    '<strong>Nace de formación universitaria en España y de un recorrido europeo con exposición a los contextos español y alemán antes de consolidarse en Chile.</strong> Ese recorrido se traduce en método, precisión, proceso y adaptación.',
    '<strong>Nace de una pasión por el entrenamiento y de una inquietud constante por la salud, respaldadas por formación universitaria específica en España y enriquecidas por un recorrido europeo por los contextos español y alemán antes de consolidarse en Chile.</strong> Esa combinación se traduce en método, precisión, proceso y adaptación.',
    'Spanish origin AEO answer',
)

about_en = ROOT / 'en/about/index.html'
replace_exact(
    about_en,
    'The brand grows from university training in Spain and a European journey that brought direct exposure to both Spanish and German contexts before taking shape in Chile. That contrast helped define a distinct way of working: assess before prescribing, plan with intent, monitor the response and adjust with judgement.',
    'The brand grew from a passion for training and a lasting curiosity about health, supported by specialised university education in Spain and enriched by a European journey through Spanish and German contexts before taking shape in Chile. That combination of vocation, education and experience helped define a distinct way of working: assess before prescribing, plan with intent, monitor the response and adjust with judgement.',
    'English origin story',
)
replace_exact(
    about_en,
    '<strong>It grows from university education in Spain and a European path shaped by Spanish and German contexts before consolidating in Chile.</strong> That journey informs method, precision, process and adaptation.',
    '<strong>It grew from a passion for training and a lasting curiosity about health, supported by specialised university education in Spain and enriched by a European journey through Spanish and German contexts before taking shape in Chile.</strong> That combination is reflected in method, precision, process and adaptation.',
    'English origin AEO answer',
)

CSS = r'''/* IBERFIT WEB V6.43.3 — aesthetic polish: CTA system + app storytelling */
/* Final CTA: one coherent conversion surface instead of oversized copy + isolated button. */
.cta-panel{padding-top:clamp(1.5rem,3vw,2.5rem)}
.cta-panel-inner{position:relative;isolation:isolate;overflow:hidden;display:grid!important;grid-template-columns:minmax(0,1fr)!important;align-items:start!important;justify-content:initial!important;gap:0!important;padding:clamp(2.35rem,5vw,4.35rem)!important;background:radial-gradient(circle at 88% 42%,rgba(217,181,104,.15),transparent 18rem),linear-gradient(145deg,#173827,#1f4933 58%,#173827)!important;border:1px solid rgba(217,181,104,.18);border-radius:28px!important;box-shadow:0 24px 64px rgba(4,22,16,.16)!important}
.cta-panel-inner:after{content:"";position:absolute;z-index:-1;right:clamp(1.5rem,6vw,5.5rem);top:50%;width:clamp(170px,19vw,300px);aspect-ratio:173/192;transform:translateY(-50%);background:url('/assets/iberfit-isotipo-oficial.png') center/contain no-repeat;opacity:.055;filter:grayscale(1) brightness(2.1);pointer-events:none}
.cta-panel-inner>div{position:relative;z-index:1;max-width:min(760px,72%)}
.cta-panel-inner h2{max-width:23ch!important;font-size:clamp(2.05rem,3.45vw,3.5rem)!important;line-height:1.02!important;letter-spacing:-.038em;margin-bottom:1rem!important;text-wrap:balance}
.cta-panel-inner p{max-width:44rem!important;margin:0!important;color:rgba(255,255,255,.77)!important;font-size:clamp(.96rem,1.2vw,1.04rem);line-height:1.65}
.cta-panel-inner>.btn{position:relative;z-index:1;justify-self:start!important;align-self:auto!important;margin-top:1.65rem;min-height:50px;padding-inline:1.45rem!important;background:linear-gradient(135deg,#d9b568,#b8973a)!important;color:#10271b!important;border-color:rgba(255,255,255,.12)!important;box-shadow:0 12px 30px rgba(4,22,16,.22)!important}
@media(hover:hover) and (pointer:fine){.cta-panel-inner>.btn:hover{transform:translateY(-2px);box-shadow:0 17px 36px rgba(4,22,16,.28)!important}}

/* Online app evidence: avoid cramped two-column layouts and use a crop that actually shows the planning UI. */
.app-story{grid-template-columns:minmax(280px,.88fr) minmax(0,1.12fr)!important;gap:clamp(36px,5vw,72px)!important}
.app-story-copy,.app-story-stage{min-width:0}
.app-story-stage{width:100%;min-height:560px!important}
.app-screen--plan{width:min(86%,560px)!important;right:1%!important;top:2%!important}
.app-screen--session{width:min(49%,390px)!important;left:0!important;bottom:1%!important}
.app-screen--progress{width:min(49%,390px)!important;right:0!important;bottom:2%!important}
.app-screen--plan img{aspect-ratio:760/387;object-fit:cover;background:#0b1d15}

@media(max-width:1160px){.app-story{grid-template-columns:1fr!important}.app-story-copy{max-width:720px!important}.app-story-stage{max-width:760px;margin-inline:auto}.app-story-copy h2{max-width:18ch!important}}
@media(max-width:760px){.cta-panel-inner{padding:2rem 1.35rem!important;border-radius:22px!important}.cta-panel-inner:after{right:-1.75rem;top:40%;width:180px;opacity:.035}.cta-panel-inner>div{max-width:100%}.cta-panel-inner h2{max-width:20ch!important;font-size:clamp(2rem,9vw,2.8rem)!important}.cta-panel-inner>.btn{width:100%;justify-self:stretch!important;margin-top:1.4rem}.app-story-stage{min-height:0!important}}
@media(prefers-reduced-motion:reduce){.cta-panel-inner>.btn{transition:none!important}}
'''
(ASSETS / CSS_NAME).write_text(CSS, encoding='utf-8')
shutil.copyfile(SOURCE, ASSETS / PLAN_NAME)

VERSION.write_text(NEW_VERSION + '\n', encoding='utf-8')

entry = '''## 6.43.3 — Aesthetic polish and CTA system\n\n- Redesigns the shared final CTA across the full site so the action is integrated with the message instead of floating in unused space; adds a subtle official IBERFIT watermark and preserves accessible contrast.\n- Replaces the visually broken Online planning crop with a fresh authenticated QA crop that shows actionable planning content instead of an empty surface.\n- Makes the Online evidence layout more robust at intermediate desktop/tablet widths to avoid cramped or clipped composition.\n- Rewrites the IBERFIT origin in ES/EN to lead with passion for training and curiosity about health, while preserving the verified Spain → Germany → Spain → Chile journey and method.\n\n'''
CHANGELOG.write_text(entry + CHANGELOG.read_text(encoding='utf-8'), encoding='utf-8')

headers = HEADERS.read_text(encoding='utf-8')
for asset in (CSS_NAME, PLAN_NAME):
    block = f'\n/assets/{asset}\n  Cache-Control: public, max-age=31536000, immutable\n'
    if f'/assets/{asset}' not in headers:
        headers += block
HEADERS.write_text(headers, encoding='utf-8')

print({'version': NEW_VERSION, 'html': len(html_files), 'css': CSS_NAME, 'plan': PLAN_NAME})
