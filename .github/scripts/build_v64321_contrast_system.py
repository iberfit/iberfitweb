from pathlib import Path

ROOT = Path('candidate/v628')
VERSION = ROOT / 'VERSION'
CHANGELOG = ROOT / 'CHANGELOG.md'
CSS_LINK = '<link href="/assets/contrast.v64321.css" rel="stylesheet"/>'

assert VERSION.read_text(encoding='utf-8').strip() == '6.43.20'
htmls = sorted(ROOT.rglob('*.html'))
assert len(htmls) == 33, len(htmls)

for path in htmls:
    text = path.read_text(encoding='utf-8')
    assert text.count('</head>') == 1, path
    assert 'contrast.v64321.css' not in text, path
    text = text.replace('</head>', CSS_LINK + '</head>')
    path.write_text(text, encoding='utf-8')

VERSION.write_text('6.43.21\n', encoding='utf-8')
entry = '''## 6.43.21 — Contrast & visual hierarchy\n\n- Strengthens secondary text contrast on cream/light surfaces.\n- Gives shared callouts and editorial rows clearer surface/border separation.\n- Uses a darker bronze for small labels on light backgrounds while preserving light gold on dark sections.\n- Keeps the IBERFIT palette unchanged: deep green, gold and warm cream.\n- No copy, routing, analytics, structured data or interaction changes.\n\n'''
old = CHANGELOG.read_text(encoding='utf-8')
CHANGELOG.write_text(entry + old, encoding='utf-8')
print(f'BUILT {len(htmls)} HTML files')
