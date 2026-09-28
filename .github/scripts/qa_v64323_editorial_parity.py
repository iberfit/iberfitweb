from pathlib import Path

ROOT = Path('candidate/v628')
assert (ROOT / 'VERSION').read_text(encoding='utf-8').strip() == '6.43.23'
htmls = sorted(ROOT.rglob('*.html'))
assert len(htmls) == 33, len(htmls)


def page(rel):
    return (ROOT / rel).read_text(encoding='utf-8')

es = page('index.html')
en = page('en/index.html')

# Home nomenclature.
assert 'Online · Desde cualquier lugar' in es
assert 'A distancia desde cualquier lugar' not in es
assert 'Online · From anywhere' in en

# Product truth parity: both current Homes expose the same new IRI report model,
# keep distinct dimensions separate and reject legacy synthetic/global scoring.
for text, rel in [(es, 'index.html'), (en, 'en/index.html')]:
    low = text.lower()
    assert '64 overall' not in low, rel
    assert 'overall index' not in low, rel
    assert 'overall score' not in low, rel
    assert 'report-status' in text, rel
    assert 'report-preview-v2' in text, rel
    assert 'report-profile-v2' in text, rel
    assert 'bioimped' in low, rel

assert 'sin resumir dimensiones distintas en una sola cifra' in es.lower()
assert 'keeping distinct dimensions separate' in en.lower()

# Hybrid: proposition -> product proof. Bind the contract to the actual evidence
# container and its three semantic steps, not to an invented per-item class.
hybrid_contracts = {
    'hibrido/index.html': ['Supervisión directa', 'Trabajo guiado', 'Feedback y ajuste'],
    'en/hybrid/index.html': ['Direct supervision', 'Guided work', 'Feedback and adjustment'],
}
for rel, markers in hybrid_contracts.items():
    text = page(rel)
    assert 'class="section photo-story-section"' not in text, rel
    assert 'app-hybrid-feedback.webp' in text, rel
    assert 'class="app-story-points"' in text, rel
    assert 'hybrid-continuity-section' in text, rel
    for marker in markers:
        assert marker in text, (rel, marker)

# In-person: retain concrete service evidence; remove duplicate Before/During/After journey.
for rel in ['presencial/index.html', 'en/in-person/index.html']:
    text = page(rel)
    assert 'class="week-flow"' not in text, rel
    assert 'photo-story-section' in text, rel
    assert 'deliverable-grid' in text, rel
    assert 'local-service-strip' in text, rel

# La Reina: one operational layer plus direct answers, not two parameterized grids.
for rel in ['entrenador-personal-la-reina/index.html', 'en/personal-trainer-la-reina/index.html']:
    text = page(rel)
    assert 'class="local-service-strip"' not in text, rel
    assert text.count('class="principle-row reveal"') == 3, rel
    assert text.count('class="answer-item"') >= 2, rel
    assert 'La Reina' in text, rel

# Safety: no critical route or accessibility/navigation primitives were lost.
for rel in ['index.html','en/index.html','hibrido/index.html','en/hybrid/index.html','presencial/index.html','en/in-person/index.html','entrenador-personal-la-reina/index.html','en/personal-trainer-la-reina/index.html']:
    text = page(rel)
    assert 'class="skip"' in text, rel
    assert 'site-header' in text and 'site-footer' in text, rel
    assert 'wa.me/56944040032' in text, rel
    assert 'dateModified":"2026-09-28"' in text, rel

print('STATIC_V64323_OK', len(htmls))
