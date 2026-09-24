from pathlib import Path

source = Path('.github/scripts/build_v64319_service_certainty.py')
text = source.read_text(encoding='utf-8')
old_es = "replace_exact(pres, 'Comunas seleccionadas de Santiago', f'{AREAS_ES}', count=6)"
new_es = "replace_exact(pres, 'Comunas seleccionadas de Santiago', f'{AREAS_ES}', count=4)"
old_en = "replace_exact(pres_en, 'Selected areas of Santiago', AREAS_EN, count=6)"
new_en = "replace_exact(pres_en, 'Selected areas of Santiago', AREAS_EN, count=4)"
for old, new in [(old_es, new_es), (old_en, new_en)]:
    if old not in text:
        raise SystemExit(f'COMPAT_PATTERN_MISSING::{old}')
    text = text.replace(old, new, 1)
exec(compile(text, str(source), 'exec'), {'__name__': '__main__', '__file__': str(source)})
