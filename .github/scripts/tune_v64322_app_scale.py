from pathlib import Path

path = Path('candidate/v628/assets/ux.v64322.css')
css = path.read_text(encoding='utf-8')
old = 'grid-auto-columns:minmax(92%,1fr)'
new = 'grid-auto-columns:minmax(94%,1fr)'
assert css.count(old) == 1, css.count(old)
path.write_text(css.replace(old, new), encoding='utf-8')
print('V64322_APP_SCALE_OK')
