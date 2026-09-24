from pathlib import Path
import html
import re
import runpy

ROOT = Path('candidate/v628')
BASE_BUILDER = Path('.github/scripts/build_v64321_contrast_system.py')

# Build the visual/copy system from the exact V6.43.20 baseline first.
runpy.run_path(str(BASE_BUILDER), run_name='__main__')

assert ROOT.joinpath('VERSION').read_text(encoding='utf-8').strip() == '6.43.21'


def replace_exact(rel: str, old: str, new: str):
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    assert count == 1, (rel, count, old)
    path.write_text(text.replace(old, new), encoding='utf-8')


# Local flexibility callouts: when the message is direct supervision + guided work,
# the destination is Hybrid. Online remains reserved for fully remote intent.
replacements = {
    'entrenador-personal-las-condes/index.html': (
        '<span>¿Tu semana cambia mucho?</span><p>La modalidad híbrida u online puede mantener la continuidad sin obligarte a reorganizar toda tu agenda.</p></div><a class="text-link" href="/online/">Conocer entrenamiento online</a>',
        '<span>¿Tu semana cambia mucho?</span><p>La modalidad híbrida mantiene la supervisión presencial cuando aporta y conecta el resto del trabajo dentro del mismo plan.</p></div><a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>',
    ),
    'en/personal-trainer-las-condes/index.html': (
        '<span>Does your week change frequently?</span><p>Hybrid or online training can protect continuity without forcing you to reorganise the entire week around appointments.</p></div><a class="text-link" href="/en/online/">Explore online training</a>',
        '<span>Does your week change frequently?</span><p>Hybrid training keeps direct supervision where it adds value and connects the rest of the work within the same plan.</p></div><a class="text-link" href="/en/hybrid/">Explore hybrid training</a>',
    ),
    'entrenador-personal-vitacura/index.html': (
        '<span>¿No necesitas presencial todas las semanas?</span><p>Podemos reservar las sesiones directas para cuando realmente aportan y guiar el resto con el mismo plan.</p></div><a class="text-link" href="/online/">Conocer entrenamiento online</a>',
        '<span>¿No necesitas presencial todas las semanas?</span><p>Podemos reservar las sesiones directas para cuando realmente aportan y guiar el resto con el mismo plan.</p></div><a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>',
    ),
    'en/personal-trainer-vitacura/index.html': (
        '<span>Do you really need an in-person session every week?</span><p>Direct supervision can be reserved for the moments where it adds value while the rest stays connected through one plan.</p></div><a class="text-link" href="/en/online/">Explore online training</a>',
        '<span>Do you really need an in-person session every week?</span><p>Direct supervision can be reserved for the moments where it adds value while the rest stays connected through one plan.</p></div><a class="text-link" href="/en/hybrid/">Explore hybrid training</a>',
    ),
    'entrenador-personal-lo-barnechea/index.html': (
        '<span>¿Tu semana cambia mucho?</span><p>Podemos combinar presencial, híbrido u online para mantener continuidad sin obligarte a reorganizar toda tu agenda.</p></div><a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>',
        '<span>¿Tu semana cambia mucho?</span><p>La modalidad híbrida combina encuentros presenciales con trabajo guiado para mantener continuidad sin obligarte a reorganizar toda tu agenda.</p></div><a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>',
    ),
    'en/personal-trainer-lo-barnechea/index.html': (
        '<span>Does your week change a lot?</span><p>We can combine in-person, hybrid or online training so you can stay consistent without reorganising your whole schedule.</p></div><a class="text-link" href="/en/hybrid/">Explore hybrid training</a>',
        '<span>Does your week change a lot?</span><p>Hybrid training combines in-person sessions with guided work so you can stay consistent without reorganising your whole schedule.</p></div><a class="text-link" href="/en/hybrid/">Explore hybrid training</a>',
    ),
    'entrenador-personal-penalolen/index.html': (
        '<span>¿Tu semana cambia mucho?</span><p>Podemos combinar presencial, híbrido u online para mantener continuidad sin perder el hilo del plan.</p></div><a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>',
        '<span>¿Tu semana cambia mucho?</span><p>La modalidad híbrida combina supervisión presencial y trabajo guiado para mantener continuidad sin perder el hilo del plan.</p></div><a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>',
    ),
    'en/personal-trainer-penalolen/index.html': (
        '<span>Does your week change a lot?</span><p>We can combine in-person, hybrid or online training while keeping the plan connected.</p></div><a class="text-link" href="/en/hybrid/">Explore hybrid training</a>',
        '<span>Does your week change a lot?</span><p>Hybrid training combines in-person supervision and guided work while keeping the plan connected.</p></div><a class="text-link" href="/en/hybrid/">Explore hybrid training</a>',
    ),
    'personal-trainer-nunoa/index.html': (
        '<span>¿Tu espacio o tu semana cambian?</span><p>Podemos combinar formatos sin perder el hilo del plan ni obligarte a empezar de cero.</p></div><a class="text-link" href="/online/">Conocer entrenamiento online</a>',
        '<span>¿Tu espacio o tu semana cambian?</span><p>La modalidad híbrida combina supervisión directa y trabajo guiado sin perder el hilo del plan ni obligarte a empezar de cero.</p></div><a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>',
    ),
    'en/personal-trainer-nunoa/index.html': (
        '<span>Does your space or schedule change?</span><p>Formats can be combined without losing the thread of the plan or forcing a restart.</p></div><a class="text-link" href="/en/online/">Explore online training</a>',
        '<span>Does your space or schedule change?</span><p>Hybrid training combines direct supervision and guided work without losing the thread of the plan or forcing a restart.</p></div><a class="text-link" href="/en/hybrid/">Explore hybrid training</a>',
    ),
    'entrenamiento-personal-providencia/index.html': (
        '<span>¿No quieres sumar otro traslado?</span><p>La modalidad híbrida u online puede darte seguimiento sin convertir cada sesión en un problema logístico.</p></div><a class="text-link" href="/online/">Conocer entrenamiento online</a>',
        '<span>¿No quieres sumar otro traslado?</span><p>La modalidad híbrida reserva la supervisión directa para cuando aporta y mantiene el resto del trabajo guiado sin sumar desplazamientos innecesarios.</p></div><a class="text-link" href="/hibrido/">Conocer entrenamiento híbrido</a>',
    ),
    'en/personal-training-providencia/index.html': (
        '<span>Do you want to avoid one more trip?</span><p>Hybrid or online support can preserve continuity without making every session a logistical problem.</p></div><a class="text-link" href="/en/online/">Explore online training</a>',
        '<span>Do you want to avoid one more trip?</span><p>Hybrid training keeps direct supervision for the moments where it adds value and the rest guided without unnecessary travel.</p></div><a class="text-link" href="/en/hybrid/">Explore hybrid training</a>',
    ),
}

for rel, (old, new) in replacements.items():
    replace_exact(rel, old, new)

# Keep the release notes truthful now that CTA destinations are intentionally aligned.
changelog = ROOT / 'CHANGELOG.md'
text = changelog.read_text(encoding='utf-8')
old_note = '- No routing, analytics, structured data or interaction changes.'
new_note = '- Aligns local flexibility callouts with Hybrid when the copy describes direct supervision plus guided work; analytics, structured data and interactions remain unchanged.'
assert text.count(old_note) == 1
changelog.write_text(text.replace(old_note, new_note), encoding='utf-8')


def visible(raw: str) -> str:
    raw = re.sub(r'<script\b.*?</script>|<style\b.*?</style>', ' ', raw, flags=re.I | re.S)
    raw = re.sub(r'<[^>]+>', ' ', raw)
    return re.sub(r'\s+', ' ', html.unescape(raw)).strip()


# Deterministic global audit of every equivalent local scope-note callout.
expected_scope = {
    'entrenador-personal-la-reina/index.html': '/hibrido/',
    'entrenador-personal-las-condes/index.html': '/hibrido/',
    'entrenador-personal-lo-barnechea/index.html': '/hibrido/',
    'entrenador-personal-penalolen/index.html': '/hibrido/',
    'entrenador-personal-vitacura/index.html': '/hibrido/',
    'entrenamiento-personal-providencia/index.html': '/hibrido/',
    'personal-trainer-nunoa/index.html': '/hibrido/',
    'en/personal-trainer-la-reina/index.html': '/en/hybrid/',
    'en/personal-trainer-las-condes/index.html': '/en/hybrid/',
    'en/personal-trainer-lo-barnechea/index.html': '/en/hybrid/',
    'en/personal-trainer-nunoa/index.html': '/en/hybrid/',
    'en/personal-trainer-penalolen/index.html': '/en/hybrid/',
    'en/personal-trainer-vitacura/index.html': '/en/hybrid/',
    'en/personal-training-providencia/index.html': '/en/hybrid/',
}

found = {}
for path in sorted(ROOT.rglob('*.html')):
    rel = path.relative_to(ROOT).as_posix()
    source = path.read_text(encoding='utf-8')
    for match in re.finditer(r'<section class="[^"]*compact-section[^"]*">(.*?)</section>', source, re.I | re.S):
        block = match.group(1)
        if 'scope-note' not in block:
            continue
        links = re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.I | re.S)
        assert len(links) == 1, (rel, links)
        href, label = links[0]
        assert rel not in found, rel
        found[rel] = (href, visible(label), visible(block))

assert set(found) == set(expected_scope), (set(found) - set(expected_scope), set(expected_scope) - set(found))
for rel, expected_href in expected_scope.items():
    href, label, block = found[rel]
    assert href == expected_href, (rel, href, expected_href, block)
    if rel.startswith('en/'):
        assert 'hybrid' in label.lower(), (rel, label)
    else:
        assert 'híbrido' in label.lower(), (rel, label)

# Global label -> destination contract for every text-link CTA on all 33 routes.
for path in sorted(ROOT.rglob('*.html')):
    rel = path.relative_to(ROOT).as_posix()
    source = path.read_text(encoding='utf-8')
    for match in re.finditer(r'<a\b[^>]*class="[^"]*text-link[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', source, re.I | re.S):
        href, raw_label = match.groups()
        label = visible(raw_label).lower()
        if 'entrenamiento híbrido' in label:
            assert href == '/hibrido/', (rel, label, href)
        if 'hybrid training' in label:
            assert href == '/en/hybrid/', (rel, label, href)
        if 'entrenamiento online' in label:
            assert href == '/online/', (rel, label, href)
        if 'online training' in label:
            assert href == '/en/online/', (rel, label, href)
        if 'método iberfit' in label:
            assert href == '/metodo/', (rel, label, href)
        if 'method' in label and rel.startswith('en/') and 'format' not in label:
            assert '/en/method/' in href or href.startswith('https://'), (rel, label, href)

print('FINAL_BUILD_OK', len(sorted(ROOT.rglob('*.html'))), 'scope_notes', len(found), 'semantic_replacements', len(replacements))
