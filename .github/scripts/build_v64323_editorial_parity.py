from pathlib import Path
import re

ROOT = Path('candidate/v628')
VERSION = ROOT / 'VERSION'

assert VERSION.read_text(encoding='utf-8').strip() == '6.43.22'
VERSION.write_text('6.43.23\n', encoding='utf-8')


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel, text):
    (ROOT / rel).write_text(text, encoding='utf-8')


def remove_section_containing(text, marker, rel):
    pos = text.find(marker)
    assert pos >= 0, f'{rel}: marker not found: {marker}'
    start = text.rfind('<section', 0, pos)
    end = text.find('</section>', pos)
    assert start >= 0 and end >= 0, f'{rel}: section bounds not found'
    return text[:start] + text[end + len('</section>'):]


def remove_div_by_class(text, class_name, rel):
    needle = f'<div class="{class_name}"'
    start = text.find(needle)
    assert start >= 0, f'{rel}: div not found: {class_name}'
    token_re = re.compile(r'</?div\b[^>]*>', re.I)
    depth = 0
    for m in token_re.finditer(text, start):
        token = m.group(0)
        if token.startswith('</'):
            depth -= 1
            if depth == 0:
                return text[:start] + text[m.end():]
        else:
            depth += 1
    raise AssertionError(f'{rel}: unbalanced div: {class_name}')


def update_modified(text):
    text, n = re.subn(r'"dateModified":"\d{4}-\d{2}-\d{2}"', '"dateModified":"2026-09-28"', text, count=1)
    assert n == 1
    return text

# 1) Home nomenclature + permanent ES/EN product truth parity.
for rel, old, new in [
    ('index.html', '<span>A distancia desde cualquier lugar</span>', '<span>Online · Desde cualquier lugar</span>'),
    ('en/index.html', '<span>Worldwide</span>', '<span>Online · From anywhere</span>'),
]:
    text = read(rel)
    wa_before = text.count('wa.me/56944040032')
    assert text.count(old) == 1, f'{rel}: expected one old online label'
    text = text.replace(old, new, 1)
    text = update_modified(text)
    assert text.count('wa.me/56944040032') == wa_before
    write(rel, text)

# 2) Hybrid: one proposition, then real product evidence. Remove the repeated photo-story explanation.
for rel in ['hibrido/index.html', 'en/hybrid/index.html']:
    text = read(rel)
    wa_before = text.count('wa.me/56944040032')
    assert text.count('class="section photo-story-section"') == 1, rel
    text = remove_section_containing(text, 'class="section photo-story-section"', rel)
    text = update_modified(text)
    assert text.count('wa.me/56944040032') == wa_before
    write(rel, text)

# 3) In-person: supervision + environments + inclusions already explain the service.
# Remove the second Before/During/After explanation in both languages.
for rel in ['presencial/index.html', 'en/in-person/index.html']:
    text = read(rel)
    wa_before = text.count('wa.me/56944040032')
    assert text.count('class="week-flow"') == 1, rel
    text = remove_section_containing(text, 'class="week-flow"', rel)
    text = update_modified(text)
    assert text.count('wa.me/56944040032') == wa_before
    write(rel, text)

# 4) La Reina: hero + one operational 3-decision block + direct answers.
# Remove the duplicated 01–04 local strip only; keep all real coverage answers.
for rel in ['entrenador-personal-la-reina/index.html', 'en/personal-trainer-la-reina/index.html']:
    text = read(rel)
    wa_before = text.count('wa.me/56944040032')
    assert text.count('class="local-service-strip"') == 1, rel
    text = remove_div_by_class(text, 'local-service-strip', rel)
    text = update_modified(text)
    assert text.count('wa.me/56944040032') == wa_before
    write(rel, text)

# Release note.
changelog = ROOT / 'CHANGELOG.md'
text = changelog.read_text(encoding='utf-8')
entry = '''\n## 6.43.23 — Editorial parity & compression (2026-09-28)\n- Home ES/EN: nomenclatura Online normalizada sin cambiar la propuesta editorial.\n- Paridad IRI ES↔EN convertida en contrato de QA: sin índice sintético global en ninguno de los dos idiomas.\n- Híbrido ES/EN: eliminada una explicación redundante para pasar de proposición a evidencia real de app.\n- Presencial ES/EN: retirado el segundo recorrido Antes/Durante/Después; se conservan supervisión, entornos e inclusiones.\n- La Reina ES/EN: eliminada la cuadrícula 01–04 redundante; se conservan hero, tres decisiones operativas y respuestas directas.\n'''
if '## 6.43.23 — Editorial parity & compression' not in text:
    text += entry
changelog.write_text(text, encoding='utf-8')

html_files = sorted(ROOT.rglob('*.html'))
assert len(html_files) == 33, len(html_files)
print('BUILD_V64323_OK', len(html_files))
