from pathlib import Path
import re

ROOT = Path('candidate/v628')
ASSETS = ROOT / 'assets'

version = ROOT / 'VERSION'
assert version.read_text(encoding='utf-8').strip() == '6.43.21'
version.write_text('6.43.22\n', encoding='utf-8')

ux_css = r'''/* IBERFIT WEB V6.43.22 — UX first impression & mobile compression. */

/* Keep headings editorial but avoid avoidable 4–5 line breaks on narrow screens. */
h1,h2{ text-wrap:balance; }
p,li{ text-wrap:pretty; }

/* Home decision architecture: two entry routes, then the three concrete formats. */
.intent-router--compact{
  grid-template-columns:repeat(2,minmax(0,1fr));
  max-width:820px;
}

/* Two verified reviews do not need an autoplay carousel. */
.review-pair{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:clamp(1rem,2.6vw,1.75rem);
}
.review-pair .client-review{ min-width:0; }

/* First-visit consent: same choices and control, materially less obstruction. */
.consent-banner{
  max-width:1040px;
  gap:1.1rem;
  padding:.88rem 1rem;
  border-radius:16px;
}
.consent-banner>div:first-child{ min-width:0; }
.consent-banner strong{
  display:block;
  font-size:1rem;
  line-height:1.15;
}
.consent-banner p{
  max-width:590px;
  margin:.22rem 0 0;
  font-size:.74rem;
  line-height:1.38;
}
.consent-actions{ gap:.38rem; flex-wrap:nowrap; }
.consent-banner .btn,
.consent-banner .consent-link{
  min-height:44px;
  padding:.62rem .78rem;
  font-size:.76rem;
}

/* Horizontal sequences explain their interaction instead of looking accidentally clipped. */
.mobile-swipe-hint{
  display:none;
  margin:.35rem 0 0;
  color:var(--text-tertiary,#5a6a61);
  font-size:.72rem;
  font-weight:750;
  letter-spacing:.02em;
}

/* Online product proof: give real app screens useful reading scale on phones. */
@media(max-width:640px){
  .app-story-stage{ grid-auto-columns:minmax(92%,1fr); }
}

/* Mobile reading rhythm: compress repetition, not information. */
@media(max-width:720px){
  body[data-page="home"] .section{ padding-block:3.35rem; }
  body[data-page="home"] .evidence-process-section{ padding-top:2.9rem; }
  body[data-page="home"] .section-intro{ margin-bottom:2rem; }
  body[data-page="home"] .modality-row--guided{ padding-block:1.45rem; }
  body[data-page="home"] .authenticity-editorial .authenticity-grid{ gap:1.4rem; }

  .mobile-swipe-hint{ display:block; }
  .mobile-swipe-hint::after{ content:"  →"; color:var(--gold-text-strong,#806216); }

  .site-footer{
    margin-top:28px;
    padding:42px 0 22px;
  }
  .site-footer .footer-grid{ gap:1.35rem; }
  .site-footer .footer-brand{ margin-bottom:.75rem; }
  .site-footer p{ margin-bottom:.6rem; }
  .site-footer .footer-links{
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:.18rem .8rem;
  }
  .site-footer .footer-links a{
    display:flex;
    align-items:center;
    min-height:44px;
    padding:.25rem 0;
    border-bottom:1px solid rgba(255,255,255,.07);
  }
  .site-footer .footer-cta{ gap:.65rem; }
  .site-footer .footer-bottom{
    margin-top:1.35rem;
    padding-top:1rem;
    gap:.5rem;
  }
}

@media(max-width:560px){
  .intent-router--compact{ grid-template-columns:1fr; }

  .consent-banner{
    left:.6rem;
    right:.6rem;
    bottom:calc(.6rem + env(safe-area-inset-bottom,0px));
    display:grid;
    gap:.55rem;
    width:auto;
    padding:.7rem .72rem;
    border-radius:16px;
    max-height:44dvh;
    overflow:auto;
    overscroll-behavior:contain;
  }
  .consent-banner strong{ font-size:.94rem; }
  .consent-banner p{ font-size:.68rem; line-height:1.32; }
  .consent-actions{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:.36rem;
    width:100%;
  }
  .consent-actions [data-consent-all],
  .consent-actions [data-consent-necessary],
  .consent-actions [data-consent-audience],
  .consent-actions [data-consent-settings]{
    grid-column:auto;
    width:100%;
    min-width:0;
    min-height:44px;
    padding:.55rem .4rem;
    white-space:normal;
    line-height:1.08;
    text-align:center;
    justify-content:center;
  }
  .consent-actions [data-consent-settings]{
    display:inline-flex;
    align-items:center;
  }
  body:has(.consent-banner) .device-dock{ display:none!important; }

  .review-pair{
    display:grid;
    grid-template-columns:none;
    grid-auto-flow:column;
    grid-auto-columns:minmax(86%,1fr);
    gap:.75rem;
    margin-inline:0 -16px;
    padding:2px 16px 12px 0;
    overflow-x:auto;
    overflow-y:hidden;
    overscroll-behavior-inline:contain;
    scroll-snap-type:x mandatory;
    scrollbar-width:none;
    -webkit-overflow-scrolling:touch;
  }
  .review-pair::-webkit-scrollbar{ display:none; }
  .review-pair .client-review{
    scroll-snap-align:start;
    scroll-snap-stop:always;
  }

  .site-footer .footer-links{ grid-template-columns:repeat(2,minmax(0,1fr)); }
}

@media(prefers-reduced-motion:reduce){
  .review-pair{ scroll-behavior:auto!important; }
}
'''
(ASSETS / 'ux.v64322.css').write_text(ux_css, encoding='utf-8')

ux_js = r'''(() => {
  'use strict';
  const english = (document.documentElement.lang || '').toLowerCase().startsWith('en');
  const label = english ? 'Swipe to see more' : 'Desliza para ver más';
  const selectors = [
    '.evidence-process-media--v6435',
    '.system-rail',
    '.method-cycle',
    '.week-flow',
    '.continuity-rail',
    '.brand-journey--editorial',
    '.app-story-stage',
    '.review-pair'
  ];
  document.addEventListener('DOMContentLoaded', () => {
    selectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(rail => {
        if (rail.nextElementSibling?.classList.contains('mobile-swipe-hint')) return;
        const hint = document.createElement('p');
        hint.className = 'mobile-swipe-hint';
        hint.textContent = label;
        hint.setAttribute('aria-hidden', 'true');
        rail.insertAdjacentElement('afterend', hint);
      });
    });
  });
})();
'''
(ASSETS / 'ux.v64322.js').write_text(ux_js, encoding='utf-8')

# Consent copy stays explicit while becoming more concise.
analytics = (ASSETS / 'analytics.v643.js').read_text(encoding='utf-8')
old_en = 'Optional measurement helps us understand which pages are useful and which actions lead to contact. We never send message content or personal details.'
new_en = 'Optional measurement helps us understand what content is useful and which actions lead to contact. We never measure message content or personal details.'
assert analytics.count(old_en) == 1
analytics = analytics.replace(old_en, new_en)
old_es = 'La medici\\xF3n opcional nos ayuda a saber qu\\xE9 p\\xE1ginas resultan \\xFAtiles y qu\\xE9 acciones terminan en contacto. Nunca enviamos el contenido de mensajes ni datos personales.'
new_es = 'La medici\\xF3n opcional nos ayuda a saber qu\\xE9 contenido resulta \\xFAtil y qu\\xE9 acciones terminan en contacto. Nunca medimos el contenido de mensajes ni datos personales.'
assert analytics.count(old_es) == 1
analytics = analytics.replace(old_es, new_es)
(ASSETS / 'analytics.v64322.js').write_text(analytics, encoding='utf-8')

# Two reviews are evidence, not a carousel product. Keep larger carousels unchanged.
experience = (ASSETS / 'experience.v632.js').read_text(encoding='utf-8')
needle = """    const slides = Array.from(cards.querySelectorAll('.client-review'));
    if (slides.length < 2) return;

    cards.dataset.v629Ready = '1';
"""
replacement = """    const slides = Array.from(cards.querySelectorAll('.client-review'));
    if (slides.length < 2) return;
    if (slides.length === 2) {
      cards.dataset.v629Ready = '1';
      cards.classList.add('review-pair');
      cards.setAttribute('role', 'region');
      cards.setAttribute('aria-label', isEnglish ? 'Real IBERFIT client experiences' : 'Experiencias reales de clientes IBERFIT');
      slides.forEach((slide, index) => {
        slide.classList.remove('reveal');
        slide.classList.add('visible');
        slide.setAttribute('role', 'group');
        slide.setAttribute('aria-label', isEnglish ? `${index + 1} of ${slides.length}` : `${index + 1} de ${slides.length}`);
      });
      return;
    }

    cards.dataset.v629Ready = '1';
"""
assert experience.count(needle) == 1
experience = experience.replace(needle, replacement)
experience = experience.replace('Subject to area and schedule.', 'We coordinate area and schedule with you.')
experience = experience.replace('Según sector y horario.', 'Coordinamos sector y horario contigo.')
(ASSETS / 'experience.v64322.js').write_text(experience, encoding='utf-8')

html_files = sorted(ROOT.rglob('*.html'))
assert len(html_files) == 33, len(html_files)
for path in html_files:
    text = path.read_text(encoding='utf-8')
    # New UX layer always wins the cascade and is explicit in every route.
    if '/assets/ux.v64322.css' not in text:
        marker = '<link href="/assets/contrast.v64321.css" rel="stylesheet"/>'
        if marker in text:
            text = text.replace(marker, marker + '<link href="/assets/ux.v64322.css" rel="stylesheet"/>', 1)
        else:
            text = text.replace('</head>', '<link href="/assets/ux.v64322.css" rel="stylesheet"/></head>', 1)
    text = text.replace('/assets/analytics.v643.js', '/assets/analytics.v64322.js')
    text = text.replace('/assets/experience.v632.js', '/assets/experience.v64322.js')
    if '/assets/ux.v64322.js' not in text:
        text = text.replace('</body>', '<script defer src="/assets/ux.v64322.js"></script></body>', 1)
    path.write_text(text, encoding='utf-8')

# Home: remove the redundant "compare formats" decision card; formats are directly below.
for rel in ['index.html', 'en/index.html']:
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    text = text.replace('class="intent-router reveal"', 'class="intent-router intent-router--compact reveal"', 1)
    text, count = re.subn(
        r'<a class="intent-route"[^>]*data-track="funnel_compare_formats"[^>]*>.*?</a>',
        '', text, count=1, flags=re.S
    )
    assert count == 1, rel
    path.write_text(text, encoding='utf-8')

# Online comparison note must actually explain when another format can be better.
replacements = {
    'online/index.html': (
        'No necesitas experiencia avanzada. El nivel de detalle y acompañamiento se adapta a tu autonomía.',
        'Si necesitas mucha corrección técnica en directo o te cuesta entrenar con autonomía incluso con guía, presencial o híbrido puede darte más apoyo.'
    ),
    'en/online/index.html': (
        'You do not need advanced experience. The level of detail and support adapts to your autonomy.',
        'If you need frequent live technical correction or find it difficult to train autonomously even with guidance, in-person or hybrid coaching may give you more support.'
    ),
}
for rel, (old, new) in replacements.items():
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    assert text.count(old) == 1, rel
    path.write_text(text.replace(old, new), encoding='utf-8')

# Keep release history explicit.
changelog = ROOT / 'CHANGELOG.md'
text = changelog.read_text(encoding='utf-8')
entry = '''\n## 6.43.22 — UX First Impression & Mobile Compression (2026-09-24)\n- Consentimiento inicial más compacto sin eliminar ninguna opción ni preferencia.\n- Home: decisión inicial simplificada; las tres modalidades siguen visibles inmediatamente después.\n- Dos reseñas verificadas pasan de carrusel con autoplay a evidencia estática/eswipe simple.\n- Indicadores discretos para secuencias horizontales en móvil.\n- Footer y ritmo vertical móvil más compactos sin reducir targets táctiles.\n- Capturas reales de la app online ganan escala útil en móvil.\n- Corregida la semántica de “otra opción puede ser mejor” en Online ES/EN.\n- Prevención de copy de incertidumbre en chips locales generados por JS.\n'''
if '## 6.43.22 — UX First Impression' not in text:
    text += entry
changelog.write_text(text, encoding='utf-8')

print('BUILD_V64322_OK', len(html_files))
