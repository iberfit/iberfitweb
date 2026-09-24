from pathlib import Path

source = Path('.github/scripts/build_v64319_service_certainty.py')
text = source.read_text(encoding='utf-8')
patches = [
    (
        "replace_exact(pres, 'Comunas seleccionadas de Santiago', f'{AREAS_ES}', count=6)",
        "replace_exact(pres, 'Comunas seleccionadas de Santiago', f'{AREAS_ES}', count=4)",
    ),
    (
        "replace_exact(pres_en, 'Selected areas of Santiago', AREAS_EN, count=6)",
        "replace_exact(pres_en, 'Selected areas of Santiago', AREAS_EN, count=4)",
    ),
    (
        "replace_exact(pres_en, '<strong>It can take place in an agreed, appropriate space within the service area.</strong>', f'<strong>It can take place in {AREAS_EN}, in an agreed and appropriate training space.</strong>')",
        "replace_exact(pres_en, '<strong>In an agreed suitable environment, subject to coverage.</strong>', f'<strong>It can take place in {AREAS_EN}, in an agreed and appropriate training space.</strong>')",
    ),
]
for old, new in patches:
    if old not in text:
        raise SystemExit(f'COMPAT_PATTERN_MISSING::{old}')
    text = text.replace(old, new, 1)
exec(compile(text, str(source), 'exec'), {'__name__': '__main__', '__file__': str(source)})
