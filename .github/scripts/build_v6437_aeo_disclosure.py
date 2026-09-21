from pathlib import Path

ROOT = Path('candidate/v628')
VERSION = ROOT / 'VERSION'
CHANGELOG = ROOT / 'CHANGELOG.md'
CSS = ROOT / 'assets/aeo-disclosure.v6437.css'
JS = ROOT / 'assets/aeo-disclosure.v6437.js'

assert VERSION.read_text(encoding='utf-8').strip() == '6.43.6'
htmls = sorted(ROOT.rglob('*.html'))
assert len(htmls) == 33

targets = []
for path in htmls:
    text = path.read_text(encoding='utf-8')
    if 'answer-section' in text and 'answer-item' in text:
        targets.append(path)

assert targets, 'NO_AEO_TARGETS'

css = r'''/* IBERFIT WEB V6.43.7 — progressive AEO disclosure */
.answer-section.aeo-disclosure-v6437 .answer-list{display:grid;gap:.65rem}
.answer-disclosure-v6437{border-top:1px solid rgba(31,61,43,.13);padding:0;background:transparent}
.answer-disclosure-v6437:last-child{border-bottom:1px solid rgba(31,61,43,.13)}
.answer-disclosure-v6437>summary{list-style:none;display:grid;grid-template-columns:2.2rem minmax(0,1fr) 2rem;align-items:center;gap:.8rem;min-height:62px;padding:.95rem .15rem;color:var(--green);cursor:pointer;font-weight:850;line-height:1.3}
.answer-disclosure-v6437>summary::-webkit-details-marker{display:none}
.answer-index-v6437{font-size:.64rem;letter-spacing:.12em;color:#806216;font-weight:900}
.answer-question-v6437{font-family:Iowan Old Style,Baskerville,Times New Roman,Georgia,serif;font-size:clamp(1.05rem,1.7vw,1.28rem);letter-spacing:-.012em}
.answer-toggle-v6437{display:grid;place-items:center;width:1.75rem;height:1.75rem;border-radius:50%;border:1px solid rgba(184,151,58,.42);color:var(--green);font-size:1rem;line-height:1;transition:transform .2s ease,background .2s ease,color .2s ease}
.answer-toggle-v6437:before{content:'+'}
.answer-disclosure-v6437[open] .answer-toggle-v6437{background:var(--green);color:#fff;transform:rotate(180deg)}
.answer-disclosure-v6437[open] .answer-toggle-v6437:before{content:'−'}
.answer-body-v6437{padding:.05rem 2.95rem 1.2rem 3rem;color:var(--muted);line-height:1.65}
.answer-body-v6437>:last-child{margin-bottom:0}
@media(hover:hover){.answer-disclosure-v6437>summary:hover .answer-question-v6437{color:#13291d}.answer-disclosure-v6437>summary:hover .answer-toggle-v6437{border-color:rgba(184,151,58,.75)}}
@media(max-width:600px){
  .answer-section.aeo-disclosure-v6437 .section-intro,.answer-section.aeo-disclosure-v6437 .section-head{margin-bottom:1.25rem}
  .answer-disclosure-v6437>summary{grid-template-columns:1.75rem minmax(0,1fr) 1.8rem;gap:.55rem;min-height:58px;padding:.82rem 0}
  .answer-index-v6437{font-size:.58rem}
  .answer-question-v6437{font-size:1.04rem;line-height:1.28}
  .answer-body-v6437{padding:.05rem .2rem 1rem 2.3rem;font-size:.91rem;line-height:1.58}
}
@media(prefers-reduced-motion:reduce){.answer-toggle-v6437{transition:none!important}}
'''

js = r'''(()=>{"use strict";const enhance=()=>{document.querySelectorAll('.answer-section').forEach((section,sectionIndex)=>{if(section.dataset.aeoV6437==='1')return;const list=section.querySelector('.answer-list');if(!list)return;const items=[...list.querySelectorAll(':scope > .answer-item')];if(!items.length)return;const group=`iberfit-aeo-${sectionIndex}`;let made=0;items.forEach((item,index)=>{const question=item.querySelector('h2,h3,h4');if(!question)return;const details=document.createElement('details');details.className='answer-disclosure-v6437';details.name=group;const summary=document.createElement('summary');const number=document.createElement('span');number.className='answer-index-v6437';number.textContent=String(index+1).padStart(2,'0');const label=document.createElement('span');label.className='answer-question-v6437';label.textContent=question.textContent.trim();const toggle=document.createElement('span');toggle.className='answer-toggle-v6437';toggle.setAttribute('aria-hidden','true');summary.append(number,label,toggle);const body=document.createElement('div');body.className='answer-body-v6437';[...item.childNodes].forEach(node=>{if(node!==question)body.appendChild(node)});details.append(summary,body);item.replaceWith(details);made++});if(made){section.classList.add('aeo-disclosure-v6437');section.dataset.aeoV6437='1'}})};document.readyState==='loading'?document.addEventListener('DOMContentLoaded',enhance,{once:true}):enhance()})();
'''

for path in targets:
    text = path.read_text(encoding='utf-8')
    assert '/assets/aeo-disclosure.v6437.css' not in text
    assert '/assets/aeo-disclosure.v6437.js' not in text
    text = text.replace('</head>', '<link href="/assets/aeo-disclosure.v6437.css" rel="stylesheet"/></head>', 1)
    text = text.replace('</body>', '<script defer src="/assets/aeo-disclosure.v6437.js"></script></body>', 1)
    path.write_text(text, encoding='utf-8')

CSS.write_text(css, encoding='utf-8')
JS.write_text(js, encoding='utf-8')
VERSION.write_text('6.43.7\n', encoding='utf-8')
entry = f'''## V6.43.7 — AEO disclosure\n\n- Converts {len(targets)} AEO answer surfaces into native progressive disclosures when JavaScript is available.\n- Keeps every answer in source HTML and preserves the original fully visible content when JavaScript is unavailable.\n- Uses native exclusive details groups so only one answer can be open per section.\n\n'''
old = CHANGELOG.read_text(encoding='utf-8')
if not old.startswith('## V6.43.7'):
    CHANGELOG.write_text(entry + old, encoding='utf-8')
print({'version':'6.43.7','targets':len(targets),'files':[str(p.relative_to(ROOT)) for p in targets]})
