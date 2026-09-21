from pathlib import Path
import re

ROOT = Path('candidate/v628')

if (ROOT / 'VERSION').read_text(encoding='utf-8').strip() != '6.43.4':
    raise SystemExit('Expected V6.43.4 runtime baseline')

STYLE_LINK = '<link href="/assets/mobile.v6435.css" rel="stylesheet"/>'

ES_SECTION = '''<section class="section evidence-process-section"><div class="container evidence-process evidence-process--v6435"><div class="evidence-process-copy reveal"><div class="kicker">IBERFIT en práctica</div><h2>Lo que hacemos hoy tiene que servir para decidir mejor mañana.</h2><p class="lead">Antes de entrenar observamos cómo llegas. Durante la sesión miramos cómo respondes. Después usamos lo que ocurrió para decidir contigo el siguiente paso.</p><p class="evidence-process-note">Menos explicación abstracta. Más señales reales del proceso.</p></div><div class="evidence-process-media evidence-process-media--v6435 reveal" aria-label="Evaluación, sesión y seguimiento dentro del proceso IBERFIT"><figure class="evidence-shot evidence-shot--eval"><picture><img alt="Preparación de una evaluación inicial IBERFIT con material de medición y planificación." decoding="async" height="1086" loading="lazy" src="/assets/photo-initial-eval-1448.webp" srcset="/assets/photo-initial-eval-640.webp 640w, /assets/photo-initial-eval-960.webp 960w, /assets/photo-initial-eval-1448.webp 1448w" sizes="(max-width: 640px) 78vw, 31vw" width="1448"/></picture><figcaption><b>Antes</b><span>Entendemos cómo llegas y qué conviene priorizar.</span></figcaption></figure><figure class="evidence-shot evidence-shot--training"><picture><img alt="Revisión de una sesión de entrenamiento con apoyo de la planificación IBERFIT." decoding="async" height="1086" loading="lazy" src="/assets/photo-trainer-session-1448.webp" srcset="/assets/photo-trainer-session-640.webp 640w, /assets/photo-trainer-session-960.webp 960w, /assets/photo-trainer-session-1448.webp 1448w" sizes="(max-width: 640px) 78vw, 24vw" width="1448"/></picture><figcaption><b>Durante</b><span>Observamos, registramos y adaptamos cuando hace falta.</span></figcaption></figure><figure class="evidence-shot evidence-shot--product"><img alt="Vista real de seguimiento y evolución en la app IBERFIT con datos de demostración." decoding="async" height="411" loading="lazy" src="/assets/app-online-progress.webp" width="400"/><figcaption><b>Después</b><span>El registro ayuda a decidir contigo el siguiente ajuste · datos de demostración.</span></figcaption></figure></div></div></section>'''

EN_SECTION = '''<section class="section evidence-process-section"><div class="container evidence-process evidence-process--v6435"><div class="evidence-process-copy reveal"><div class="kicker">IBERFIT in practice</div><h2>What we do today should help us decide better with you tomorrow.</h2><p class="lead">Before training, we look at how you arrive. During the session, we watch how you respond. Afterwards, we use what happened to decide the next step with you.</p><p class="evidence-process-note">Less abstract explanation. More visible evidence of the process.</p></div><div class="evidence-process-media evidence-process-media--v6435 reveal" aria-label="Assessment, training session and ongoing review within the IBERFIT process"><figure class="evidence-shot evidence-shot--eval"><picture><img alt="Preparation for an initial IBERFIT assessment with measurement and planning material." decoding="async" height="1086" loading="lazy" src="/assets/photo-initial-eval-1448.webp" srcset="/assets/photo-initial-eval-640.webp 640w, /assets/photo-initial-eval-960.webp 960w, /assets/photo-initial-eval-1448.webp 1448w" sizes="(max-width: 640px) 78vw, 31vw" width="1448"/></picture><figcaption><b>Before</b><span>We understand how you arrive and what should be prioritised.</span></figcaption></figure><figure class="evidence-shot evidence-shot--training"><picture><img alt="Review of a training session supported by IBERFIT planning." decoding="async" height="1086" loading="lazy" src="/assets/photo-trainer-session-1448.webp" srcset="/assets/photo-trainer-session-640.webp 640w, /assets/photo-trainer-session-960.webp 960w, /assets/photo-trainer-session-1448.webp 1448w" sizes="(max-width: 640px) 78vw, 24vw" width="1448"/></picture><figcaption><b>During</b><span>We observe, record and adapt when needed.</span></figcaption></figure><figure class="evidence-shot evidence-shot--product"><img alt="Real IBERFIT app view showing ongoing review and progress with demonstration data." decoding="async" height="411" loading="lazy" src="/assets/app-online-progress.webp" width="400"/><figcaption><b>Afterwards</b><span>The record helps us decide the next adjustment with you · demonstration data.</span></figcaption></figure></div></div></section>'''

section_re = re.compile(r'<section class="section evidence-process-section">.*?</section>(?=<section class="section">)', re.S)

for rel, replacement in [('index.html', ES_SECTION), ('en/index.html', EN_SECTION)]:
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    text, count = section_re.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit(f'Could not replace evidence section in {rel}: {count}')
    path.write_text(text, encoding='utf-8')

html_files = sorted(ROOT.rglob('*.html'))
if len(html_files) != 33:
    raise SystemExit(f'Expected 33 HTML files, got {len(html_files)}')
for path in html_files:
    text = path.read_text(encoding='utf-8')
    if STYLE_LINK in text:
        raise SystemExit(f'V6.43.5 stylesheet already present: {path}')
    if '</head>' not in text:
        raise SystemExit(f'Missing head close: {path}')
    text = text.replace('</head>', STYLE_LINK + '</head>', 1)
    path.write_text(text, encoding='utf-8')

css = r'''/* IBERFIT WEB V6.43.5 — mobile art direction and purposeful interaction */

/* Home: practice is evidence; the following System section remains the conceptual explanation. */
.evidence-process--v6435{
  grid-template-columns:minmax(0,.67fr) minmax(0,1.33fr);
  align-items:center;
}
.evidence-process-note{
  margin:1.3rem 0 0;
  padding-top:1rem;
  border-top:1px solid rgba(217,181,104,.24);
  color:rgba(255,255,255,.62);
  font-size:.78rem;
  line-height:1.55;
}
.evidence-process-media--v6435{
  display:grid;
  grid-template-columns:minmax(0,1.12fr) minmax(0,.88fr);
  grid-template-rows:auto auto;
  gap:.9rem;
  align-items:stretch;
}
.evidence-process-media--v6435 .evidence-shot{transform:none!important}
.evidence-process-media--v6435 .evidence-shot--eval{grid-row:1/3}
.evidence-process-media--v6435 .evidence-shot--training{grid-column:2;grid-row:1}
.evidence-process-media--v6435 .evidence-shot--product{grid-column:2;grid-row:2;background:#0b2419}
.evidence-process-media--v6435 .evidence-shot img{
  width:100%;
  height:100%;
  min-height:0;
  object-fit:cover;
}
.evidence-process-media--v6435 .evidence-shot--eval img{aspect-ratio:4/5}
.evidence-process-media--v6435 .evidence-shot--training img{aspect-ratio:16/10}
.evidence-process-media--v6435 .evidence-shot--product img{
  aspect-ratio:auto;
  object-fit:contain;
  background:#0b2419;
}
.evidence-process-media--v6435 .evidence-shot figcaption{
  display:grid;
  grid-template-columns:auto 1fr;
  gap:.65rem;
  align-items:baseline;
}
.evidence-process-media--v6435 .evidence-shot figcaption b{
  color:var(--gold-light,#d9b568);
  font-size:.63rem;
  letter-spacing:.11em;
  text-transform:uppercase;
}
.evidence-process-media--v6435 .evidence-shot figcaption span{line-height:1.45}

/* Mobile hero: keep the human visual present without making the first screen excessively tall. */
@media(max-width:640px){
  body[data-page="home"] .editorial-hero-media{
    margin:0;
    overflow:hidden;
    border-radius:22px;
  }
  body[data-page="home"] .editorial-hero-media picture{display:block}
  body[data-page="home"] .editorial-hero-media img{
    display:block;
    width:100%;
    aspect-ratio:5/4;
    object-fit:cover;
    object-position:center 48%;
  }
  body[data-page="home"] .editorial-hero-media figcaption{
    padding:.65rem .15rem 0;
    font-size:.68rem;
    line-height:1.4;
  }
}

/* Shared mobile sequence pattern: swipe, snap and a visible next-item peek. No autoplay. */
@media(max-width:640px){
  .evidence-process--v6435{grid-template-columns:1fr;gap:1.65rem}
  .evidence-process-media--v6435,
  body[data-page="home"] .system-rail,
  body[data-page="method"] .method-cycle,
  body[data-page="modality_in_person"] .week-flow,
  body[data-page="modality_online"] .continuity-rail,
  body[data-page="about"] .brand-journey--editorial{
    display:grid!important;
    grid-template-columns:none!important;
    grid-template-rows:none!important;
    grid-auto-flow:column;
    grid-auto-columns:minmax(245px,78vw);
    gap:.8rem!important;
    width:auto;
    margin-inline:0 -16px;
    padding:4px 16px 14px 0;
    overflow-x:auto;
    overflow-y:hidden;
    overscroll-behavior-inline:contain;
    scroll-snap-type:x mandatory;
    scroll-padding-inline:0;
    scrollbar-width:none;
    -webkit-overflow-scrolling:touch;
    border:0!important;
    background:transparent!important;
  }
  .evidence-process-media--v6435::-webkit-scrollbar,
  body[data-page="home"] .system-rail::-webkit-scrollbar,
  body[data-page="method"] .method-cycle::-webkit-scrollbar,
  body[data-page="modality_in_person"] .week-flow::-webkit-scrollbar,
  body[data-page="modality_online"] .continuity-rail::-webkit-scrollbar,
  body[data-page="about"] .brand-journey--editorial::-webkit-scrollbar{display:none}

  .evidence-process-media--v6435>* ,
  body[data-page="home"] .system-rail>* ,
  body[data-page="method"] .method-cycle>* ,
  body[data-page="modality_in_person"] .week-flow>* ,
  body[data-page="modality_online"] .continuity-rail>* ,
  body[data-page="about"] .brand-journey--editorial>*{
    scroll-snap-align:start;
    scroll-snap-stop:always;
  }

  .evidence-process-media--v6435 .evidence-shot--eval,
  .evidence-process-media--v6435 .evidence-shot--training,
  .evidence-process-media--v6435 .evidence-shot--product{
    grid-column:auto!important;
    grid-row:auto!important;
    min-height:0;
    display:block!important;
    border-radius:20px!important;
    box-shadow:0 15px 34px rgba(0,0,0,.18)!important;
  }
  .evidence-process-media--v6435 .evidence-shot img,
  .evidence-process-media--v6435 .evidence-shot--eval img,
  .evidence-process-media--v6435 .evidence-shot--training img{
    width:100%;
    height:auto;
    aspect-ratio:5/4;
    object-fit:cover;
  }
  .evidence-process-media--v6435 .evidence-shot--product img{
    aspect-ratio:400/411;
    object-fit:contain;
  }
  .evidence-process-media--v6435 .evidence-shot figcaption{
    min-height:76px;
    padding:.78rem .9rem .86rem;
  }

  body[data-page="home"] .system-stage,
  body[data-page="method"] .cycle-step,
  body[data-page="modality_in_person"] .week-step,
  body[data-page="modality_online"] .continuity-step,
  body[data-page="about"] .brand-journey--editorial article{
    min-height:205px!important;
    padding:1.35rem 1.2rem!important;
    border:1px solid rgba(31,61,43,.13)!important;
    border-radius:20px!important;
    background:rgba(255,253,249,.82)!important;
    box-shadow:0 14px 34px rgba(16,42,29,.10)!important;
  }
  body[data-page="home"] .system-stage:not(:last-child):after{display:none!important}
  body[data-page="home"] .system-stage{display:grid;grid-template-columns:auto 1fr;gap:.9rem}
  body[data-page="method"] .cycle-step>span,
  body[data-page="modality_in_person"] .week-step>span,
  body[data-page="modality_online"] .continuity-step>span{margin-bottom:1.3rem}
  body[data-page="modality_in_person"] .week-step{border-left:2px solid var(--gold)!important}
  body[data-page="modality_online"] .continuity-step{border-bottom:0!important}

  /* About uses a dark editorial rail; preserve its visual identity. */
  body[data-page="about"] .brand-journey--editorial{margin-top:2rem!important;margin-bottom:1.6rem!important}
  body[data-page="about"] .brand-journey--editorial article{
    background:linear-gradient(155deg,rgba(255,255,255,.085),rgba(255,255,255,.03))!important;
    border-color:rgba(217,181,104,.28)!important;
    box-shadow:0 16px 38px rgba(0,0,0,.17)!important;
  }
  body[data-page="about"] .brand-journey--editorial .journey-current{
    background:linear-gradient(155deg,rgba(217,181,104,.15),rgba(255,255,255,.04))!important;
    border-color:rgba(217,181,104,.48)!important;
  }
}

/* Tablet: keep enough density to feel editorial, never like a desktop grid squeezed smaller. */
@media(min-width:641px) and (max-width:900px){
  .evidence-process--v6435{grid-template-columns:1fr;gap:2rem}
  .evidence-process-media--v6435{max-width:780px}
}

/* Motion is always caused by the person. Scroll snapping remains available without animation. */
@media(prefers-reduced-motion:reduce){
  .evidence-process-media--v6435,
  body[data-page="home"] .system-rail,
  body[data-page="method"] .method-cycle,
  body[data-page="modality_in_person"] .week-flow,
  body[data-page="modality_online"] .continuity-rail,
  body[data-page="about"] .brand-journey--editorial{
    scroll-behavior:auto!important;
  }
}
'''
(ROOT / 'assets/mobile.v6435.css').write_text(css, encoding='utf-8')

(ROOT / 'VERSION').write_text('6.43.5\n', encoding='utf-8')

changelog = ROOT / 'CHANGELOG.md'
existing = changelog.read_text(encoding='utf-8')
entry = '''## 6.43.5 — Mobile experience & art direction\n\n- Home separates visual evidence from the conceptual IBERFIT system to remove duplicated explanation.\n- The practice section now shows assessment, supervised training and real product follow-up as one visible sequence.\n- Mobile uses purposeful horizontal scroll-snap rails for genuine sequences (Home system, Method, in-person weekly flow, Online continuity and brand journey).\n- Home hero is shorter on mobile to improve rhythm while preserving the same SEO copy and high-priority image.\n- No autoplay, no gratuitous motion, no SEO/meta/schema changes and no analytics/menu regressions.\n\n'''
if '## 6.43.5' in existing:
    raise SystemExit('CHANGELOG already contains 6.43.5')
changelog.write_text(entry + existing, encoding='utf-8')

print({'version':'6.43.5','html':len(html_files),'style':'assets/mobile.v6435.css'})
