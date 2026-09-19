from pathlib import Path

builder = Path('.github/scripts/build_v6434_human_first.py')
source = builder.read_text(encoding='utf-8')
old = "'The format changes how you train. The service stays complete.'"
new = "'The format changes how training is carried out. The service remains complete.'"
if source.count(old) != 1:
    raise SystemExit(f'expected one legacy EN in-person source literal, got {source.count(old)}')
source = source.replace(old, new, 1)
exec(compile(source, str(builder), 'exec'), {'__name__': '__main__'})
