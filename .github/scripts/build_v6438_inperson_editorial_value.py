from pathlib import Path

ROOT = Path('candidate/v628')
VERSION = ROOT / 'VERSION'
CHANGELOG = ROOT / 'CHANGELOG.md'
TARGETS = [ROOT / 'presencial/index.html', ROOT / 'en/in-person/index.html']
CSS = ROOT / 'assets/inperson.v6438.css'

assert VERSION.read_text(encoding='utf-8').strip() == '6.43.7'
for path in TARGETS:
    assert path.exists(), path

css = r'''/* IBERFIT WEB V6.43.8 — in-person editorial value composition */
body[data-page="modality_in_person"] .deliverable-grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:0;
  overflow:visible;
  border:0;
  border-top:1px solid rgba(184,151,58,.48);
  border-bottom:1px solid rgba(184,151,58,.48);
  border-radius:0;
  background:transparent;
}
body[data-page="modality_in_person"] .deliverable{
  min-height:0;
  padding:clamp(1.45rem,2.6vw,2.15rem) clamp(1rem,2.8vw,2.35rem);
  display:grid;
  grid-template-columns:2.8rem minmax(0,1fr);
  grid-template-rows:auto 1fr;
  column-gap:1rem;
  align-items:start;
  background:transparent;
  border:0;
  border-radius:0;
  box-shadow:none;
  transition:background .22s ease;
}
body[data-page="modality_in_person"] .deliverable:nth-child(odd){border-right:1px solid rgba(31,61,43,.12)}
body[data-page="modality_in_person"] .deliverable:nth-child(-n+2){border-bottom:1px solid rgba(31,61,43,.12)}
body[data-page="modality_in_person"] .deliverable>span{
  grid-row:1/3;
  margin:0;
  padding-top:.16rem;
  color:#806216;
  font-size:.66rem;
  font-weight:900;
  letter-spacing:.15em;
}
body[data-page="modality_in_person"] .deliverable h3{
  margin:0 0 .55rem;
  font-size:clamp(1.24rem,2vw,1.58rem);
  line-height:1.08;
  letter-spacing:-.025em;
}
body[data-page="modality_in_person"] .deliverable p{
  margin:0;
  color:var(--muted);
  font-size:.94rem;
  line-height:1.62;
  max-width:34rem;
}
@media(hover:hover){
  body[data-page="modality_in_person"] .deliverable:hover{background:rgba(255,255,255,.42)}
}
@media(max-width:640px){
  body[data-page="modality_in_person"] .deliverable-grid{grid-template-columns:1fr}
  body[data-page="modality_in_person"] .deliverable{
    padding:1.05rem 0;
    grid-template-columns:2.2rem minmax(0,1fr);
    column-gap:.65rem;
    border-right:0!important;
    border-bottom:1px solid rgba(31,61,43,.12)!important;
  }
  body[data-page="modality_in_person"] .deliverable:last-child{border-bottom:0!important}
  body[data-page="modality_in_person"] .deliverable>span{font-size:.59rem;padding-top:.12rem}
  body[data-page="modality_in_person"] .deliverable h3{font-size:1.14rem;margin-bottom:.32rem}
  body[data-page="modality_in_person"] .deliverable p{font-size:.88rem;line-height:1.5}
  body[data-page="modality_in_person"] .section-intro:has(+ .deliverable-grid){margin-bottom:1.15rem}
}
@media(prefers-reduced-motion:reduce){body[data-page="modality_in_person"] .deliverable{transition:none!important}}
'''

for path in TARGETS:
    text = path.read_text(encoding='utf-8')
    assert 'data-page="modality_in_person"' in text
    assert 'class="deliverable-grid"' in text
    assert text.count('class="deliverable reveal"') == 4
    assert '/assets/inperson.v6438.css' not in text
    text = text.replace('</head>', '<link href="/assets/inperson.v6438.css" rel="stylesheet"/></head>', 1)
    path.write_text(text, encoding='utf-8')

CSS.write_text(css, encoding='utf-8')
VERSION.write_text('6.43.8\n', encoding='utf-8')
entry = '''## V6.43.8 — In-person editorial value\n\n- Replaces the four-card visual treatment on the in-person service with an open editorial matrix.\n- On mobile, the same content becomes four compact ruled rows instead of a tall card stack.\n- Copy, pricing, coverage, structured data and service semantics remain unchanged.\n\n'''
old = CHANGELOG.read_text(encoding='utf-8')
if not old.startswith('## V6.43.8'):
    CHANGELOG.write_text(entry + old, encoding='utf-8')
print({'version':'6.43.8','targets':[str(p.relative_to(ROOT)) for p in TARGETS],'css':str(CSS)})
