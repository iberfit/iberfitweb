from pathlib import Path

root = Path('candidate/v628')
old = (root / 'assets/analytics.v632.js').read_text(encoding='utf-8')
marker = 'window.iberfitTrack=(e,t={})=>{const n={...k()};Object.entries(t).forEach(([r,s])=>{s!=null&&(n[r]=L(s))}),l.debug&&console.info("[IBERFIT analytics]",e,n),d()&&(window.gtag("event",e,n),(e==="whatsapp_click"||e==="contact_email_click")&&window.gtag("event","generate_lead",{...n,lead_source:e==="whatsapp_click"?"whatsapp":"email"})),i()&&window.fbq&&["whatsapp_click","contact_email_click","format_guide_whatsapp_open"].includes(e)&&window.fbq("track","Lead",{content_name:e,page_group:n.page_group})};'
replacement = 'const G="iberfit_lead_session_v1",P=()=>{try{return sessionStorage.getItem(G)==="1"}catch{return!1}},R=()=>{try{sessionStorage.setItem(G,"1")}catch{}};window.iberfitTrack=(e,t={})=>{const n={...k()};Object.entries(t).forEach(([r,s])=>{s!=null&&(n[r]=L(s))}),l.debug&&console.info("[IBERFIT analytics]",e,n),d()&&(window.gtag("event",e,n),(e==="whatsapp_click"||e==="contact_email_click")&&(()=>{const s=e==="whatsapp_click"?"whatsapp":"email";window.gtag("event","contact_intent",{...n,lead_source:s}),P()||(R(),window.gtag("event","generate_lead",{...n,lead_source:s}))})()),i()&&window.fbq&&["whatsapp_click","contact_email_click","format_guide_whatsapp_open"].includes(e)&&window.fbq("track","Lead",{content_name:e,page_group:n.page_group})};'
if old.count(marker) != 1:
    raise SystemExit('analytics marker mismatch')
(root / 'assets/analytics.v643.js').write_text(old.replace(marker, replacement, 1), encoding='utf-8')

htmls = sorted(root.rglob('*.html'))
if len(htmls) != 33:
    raise SystemExit(f'expected 33 html routes, got {len(htmls)}')
for p in htmls:
    text = p.read_text(encoding='utf-8')
    if text.count('/assets/analytics.v632.js') != 1:
        raise SystemExit(f'analytics ref mismatch {p}')
    p.write_text(text.replace('/assets/analytics.v632.js', '/assets/analytics.v643.js'), encoding='utf-8')

patches = {
    'index.html': [
        ('<a class="intent-route" href="/diagnostico-iri/">', '<a class="intent-route" data-cta-position="intent_router" data-track="funnel_iri_start" href="/diagnostico-iri/">'),
        ('<a class="intent-route" href="#formatos">', '<a class="intent-route" data-cta-position="intent_router" data-track="funnel_compare_formats" href="#formatos">'),
        ('<a class="intent-route" href="/contacto/#orientador">', '<a class="intent-route" data-cta-position="intent_router" data-track="funnel_guide_start" href="/contacto/#orientador">'),
        ('<a class="text-link" href="/presencial/">Conocer modalidad</a>', '<a class="text-link" data-cta-position="formats" data-track="format_in_person_open" href="/presencial/">Conocer modalidad</a>'),
        ('<a class="text-link" href="/hibrido/">Conocer modalidad</a>', '<a class="text-link" data-cta-position="formats" data-track="format_hybrid_open" href="/hibrido/">Conocer modalidad</a>'),
        ('<a class="text-link" href="/online/">Conocer modalidad</a>', '<a class="text-link" data-cta-position="formats" data-track="format_online_open" href="/online/">Conocer modalidad</a>'),
        ('<a class="review-source-link" href="https://share.google/xZmHR5R4JZzDFQcli"', '<a class="review-source-link" data-cta-position="reviews" data-track="google_reviews_section_click" href="https://share.google/xZmHR5R4JZzDFQcli"'),
    ],
    'en/index.html': [
        ('<a class="intent-route" href="/en/iri-assessment/">', '<a class="intent-route" data-cta-position="intent_router" data-track="funnel_iri_start" href="/en/iri-assessment/">'),
        ('<a class="intent-route" href="#formatos">', '<a class="intent-route" data-cta-position="intent_router" data-track="funnel_compare_formats" href="#formatos">'),
        ('<a class="intent-route" href="/en/contact/#orientador">', '<a class="intent-route" data-cta-position="intent_router" data-track="funnel_guide_start" href="/en/contact/#orientador">'),
        ('<a class="text-link" href="/en/in-person/">Explore this format</a>', '<a class="text-link" data-cta-position="formats" data-track="format_in_person_open" href="/en/in-person/">Explore this format</a>'),
        ('<a class="text-link" href="/en/hybrid/">Explore this format</a>', '<a class="text-link" data-cta-position="formats" data-track="format_hybrid_open" href="/en/hybrid/">Explore this format</a>'),
        ('<a class="text-link" href="/en/online/">Explore this format</a>', '<a class="text-link" data-cta-position="formats" data-track="format_online_open" href="/en/online/">Explore this format</a>'),
        ('<a class="review-source-link" href="https://share.google/xZmHR5R4JZzDFQcli"', '<a class="review-source-link" data-cta-position="reviews" data-track="google_reviews_section_click" href="https://share.google/xZmHR5R4JZzDFQcli"'),
    ],
    'contacto/index.html': [
        ('<a class="btn btn-primary" data-orientador-whatsapp=""', '<a class="btn btn-primary" data-cta-position="guide_result" data-track="cta_guide_whatsapp" data-orientador-whatsapp=""'),
        ('<a class="text-link" href="https://wa.me/56944040032?text=Hola%20IBERFIT%2C%20quiero%20recibir%20orientaci%C3%B3n%20sobre%20entrenamiento', '<a class="text-link" data-cta-position="guide_result" data-track="cta_guide_direct" href="https://wa.me/56944040032?text=Hola%20IBERFIT%2C%20quiero%20recibir%20orientaci%C3%B3n%20sobre%20entrenamiento'),
        ('<a class="text-link" data-track="cta_contact_whatsapp"', '<a class="text-link" data-cta-position="contact_options" data-track="cta_contact_whatsapp"'),
    ],
    'en/contact/index.html': [
        ('<a class="btn btn-primary" data-orientador-whatsapp=""', '<a class="btn btn-primary" data-cta-position="guide_result" data-track="cta_guide_whatsapp" data-orientador-whatsapp=""'),
        ('<a class="text-link" href="https://wa.me/56944040032?text=Hello%20IBERFIT', '<a class="text-link" data-cta-position="guide_result" data-track="cta_guide_direct" href="https://wa.me/56944040032?text=Hello%20IBERFIT'),
        ('<a class="text-link" data-track="cta_contact_whatsapp"', '<a class="text-link" data-cta-position="contact_options" data-track="cta_contact_whatsapp"'),
    ],
}
for rel, replacements in patches.items():
    p = root / rel
    text = p.read_text(encoding='utf-8')
    for before, after in replacements:
        if text.count(before) != 1:
            raise SystemExit(f'patch marker mismatch {rel}: {before[:100]} count={text.count(before)}')
        text = text.replace(before, after, 1)
    p.write_text(text, encoding='utf-8')

headers = root / '_headers'
headers_text = headers.read_text(encoding='utf-8')
cache_block = '\n/assets/analytics.v643.js\n  ! Cache-Control\n  Cache-Control: public, max-age=31536000, immutable\n  Content-Type: text/javascript; charset=utf-8\n'
if '/assets/analytics.v643.js' not in headers_text:
    headers_text += cache_block
headers.write_text(headers_text, encoding='utf-8')

(root / 'VERSION').write_text('6.43\n', encoding='utf-8')
changelog = root / 'CHANGELOG.md'
old_changelog = changelog.read_text(encoding='utf-8')
entry = '''# Cambios V6.43

- Se refuerza la observabilidad CRO sin modificar la experiencia visual ni el contenido visible.
- Los clics de WhatsApp y correo generan `contact_intent`; `generate_lead` se limita a una vez por sesión para evitar inflar leads por clics repetidos.
- Se instrumentan las rutas de decisión de Home: IRI, comparación de modalidades, orientador, cada modalidad y reseñas de Google.
- Se instrumentan las dos salidas del resultado del orientador y se conserva la trazabilidad por posición de CTA.
- La medición sigue condicionada al consentimiento de analítica; no se añaden datos personales ni contenido de mensajes a GA4.
- `analytics.v632.js` permanece intacto como rollback; V6.43 usa un asset versionado nuevo y cacheable.

'''
changelog.write_text(entry + old_changelog, encoding='utf-8')
print({'html': len(htmls), 'version': '6.43', 'analytics': 'analytics.v643.js'})
