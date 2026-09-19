from pathlib import Path

ROOT = Path("candidate/v628")
EXPECTED_VERSION = "6.43"
NEW_VERSION = "6.43.1"
ASSET = "/assets/a11y.v6431.css"
MARKER = '<link href="/assets/aeo.v639.css" rel="stylesheet"/>'

version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
if version != EXPECTED_VERSION:
    raise SystemExit(f"expected VERSION {EXPECTED_VERSION}, got {version}")

css = """/* IBERFIT WEB V6.43.1 — WCAG-safe gold text on light surfaces. */
:root{--gold-text:#806216}

/* Small gold labels on cream/paper need a darker bronze tone for AA contrast. */
.kicker,
.eyebrow,
.price-name,
.iri-phase-label,
.card-index{color:var(--gold-text)}

/* Gold-filled controls keep the brand surface but use dark ink for contrast. */
.btn-gold,
.price-badge{color:var(--green-dark)}

/* Dark surfaces retain the lighter brand gold, where contrast is already strong. */
.section-dark .kicker,
.section-dark .eyebrow,
.evidence-process-section .kicker,
.evidence-process-section .eyebrow,
.card-dark .kicker,
.card-dark .eyebrow,
.cta-band .kicker,
.cta-band .eyebrow,
.price-card.featured .price-name{color:var(--gold-light)}

.price-card.featured .price-badge{color:#fff}
"""
(ROOT / "assets/a11y.v6431.css").write_text(css, encoding="utf-8")

htmls = sorted(ROOT.rglob("*.html"))
if len(htmls) != 33:
    raise SystemExit(f"expected 33 HTML files, got {len(htmls)}")

for path in htmls:
    text = path.read_text(encoding="utf-8")
    if ASSET in text:
        raise SystemExit(f"asset already present in {path}")
    if text.count(MARKER) != 1:
        raise SystemExit(f"AEO stylesheet marker mismatch in {path}: {text.count(MARKER)}")
    text = text.replace(MARKER, MARKER + f'<link href="{ASSET}" rel="stylesheet"/>', 1)
    path.write_text(text, encoding="utf-8")

headers = ROOT / "_headers"
headers_text = headers.read_text(encoding="utf-8")
if ASSET not in headers_text:
    headers_text += (
        f"\n{ASSET}\n"
        "  ! Cache-Control\n"
        "  Cache-Control: public, max-age=31536000, immutable\n"
        "  Content-Type: text/css; charset=utf-8\n"
    )
headers.write_text(headers_text, encoding="utf-8")

(ROOT / "VERSION").write_text(NEW_VERSION + "\n", encoding="utf-8")

changelog = ROOT / "CHANGELOG.md"
old = changelog.read_text(encoding="utf-8")
entry = """# Cambios V6.43.1

- Se corrige el contraste de etiquetas doradas pequeñas sobre fondos crema/papel mediante un tono bronce de texto (`#806216`) sin alterar el dorado de marca de superficies o fondos oscuros.
- Botones y badges con relleno dorado pasan a tinta verde oscura para conservar legibilidad AA; las variantes sobre fondos oscuros mantienen el tratamiento claro.
- No cambia el contenido visible, la jerarquía, el layout, SEO/AEO, JSON-LD, analítica ni JavaScript.
- Se añade un asset CSS versionado e inmutable (`a11y.v6431.css`) para no mutar assets ya cacheados de V6.43.

"""
changelog.write_text(entry + old, encoding="utf-8")

print({"version": NEW_VERSION, "html": len(htmls), "asset": ASSET})
