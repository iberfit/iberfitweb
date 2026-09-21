from pathlib import Path

ROOT = Path('candidate/v628')
VERSION = ROOT / 'VERSION'
CHANGELOG = ROOT / 'CHANGELOG.md'
HOME_FILES = [ROOT / 'index.html', ROOT / 'en/index.html']
CSS = ROOT / 'assets/focus.v6436.css'
JS = ROOT / 'assets/focus.v6436.js'

assert VERSION.read_text(encoding='utf-8').strip() == '6.43.5'

css = r'''/* IBERFIT WEB V6.43.6 — focused IRI preview on Home */
.report-focus-v6436 .report-metrics-v2{padding-bottom:.15rem}
.report-focus-v6436 .report-metrics-v2>.report-metric:nth-child(n+3){display:none}
.report-more-v6436{margin-top:1rem;border-top:1px solid rgba(184,151,58,.26);padding-top:.85rem}
.report-more-v6436>summary{list-style:none;display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:48px;padding:.7rem .85rem;border:1px solid rgba(184,151,58,.28);border-radius:14px;background:rgba(255,255,255,.68);color:var(--green);font-weight:850;cursor:pointer;transition:background .2s ease,border-color .2s ease}
.report-more-v6436>summary::-webkit-details-marker{display:none}
.report-more-v6436>summary:after{content:'+';display:grid;place-items:center;width:1.8rem;height:1.8rem;flex:0 0 auto;border-radius:50%;background:var(--green);color:#fff;font-size:1.1rem;line-height:1;transition:transform .2s ease}
.report-more-v6436[open]>summary:after{content:'−';transform:rotate(180deg)}
.report-more-v6436>summary:hover{background:#fff;border-color:rgba(184,151,58,.5)}
.report-more-content-v6436{padding:.95rem .15rem .1rem}
.report-more-content-v6436 .report-metric{display:grid!important}
.report-more-content-v6436 .report-bio{margin-top:.8rem}
.report-more-content-v6436 .report-comparison{margin-top:.8rem}
.report-more-content-v6436 .report-disclaimer{margin-top:.75rem}
.report-focus-v6436 .report-actions{margin-top:.85rem}
@media(max-width:600px){
  .report-focus-v6436{padding:1rem!important}
  .report-focus-v6436 .report-head{padding-bottom:.85rem}
  .report-focus-v6436 .report-profile{padding:.95rem 0}
  .report-focus-v6436 .report-actions{grid-template-columns:1fr!important;gap:.55rem}
  .report-more-v6436>summary{font-size:.85rem;padding:.68rem .75rem}
}
@media(prefers-reduced-motion:reduce){.report-more-v6436>summary,.report-more-v6436>summary:after{transition:none!important}}
'''

js = r'''(()=>{"use strict";const enhance=()=>{document.querySelectorAll('.report-preview-v2').forEach(report=>{if(report.dataset.focusV6436==='1')return;const metrics=report.querySelector('.report-metrics-v2'),bio=report.querySelector('.report-bio'),comparison=report.querySelector('.report-comparison'),disclaimer=report.querySelector('.report-disclaimer');if(!metrics||!bio||!comparison||!disclaimer)return;const items=[...metrics.querySelectorAll(':scope > .report-metric')];if(items.length<3)return;const details=document.createElement('details');details.className='report-more-v6436';const summary=document.createElement('summary');summary.textContent=document.documentElement.lang==='en'?'See more of this IRI example':'Ver más del ejemplo IRI';const content=document.createElement('div');content.className='report-more-content-v6436';const extraMetrics=document.createElement('div');extraMetrics.className='report-metrics report-metrics-v2 report-extra-metrics-v6436';items.slice(2).forEach(item=>extraMetrics.appendChild(item));content.appendChild(extraMetrics);content.appendChild(bio);content.appendChild(comparison);content.appendChild(disclaimer);details.append(summary,content);report.appendChild(details);report.classList.add('report-focus-v6436');report.dataset.focusV6436='1'});};document.readyState==='loading'?document.addEventListener('DOMContentLoaded',enhance,{once:true}):enhance()})();
'''

for path in HOME_FILES:
    text = path.read_text(encoding='utf-8')
    assert '/assets/focus.v6436.css' not in text
    assert '/assets/focus.v6436.js' not in text
    assert 'report-preview report-preview-v2' in text
    text = text.replace('</head>', '<link href="/assets/focus.v6436.css" rel="stylesheet"/></head>', 1)
    text = text.replace('</body>', '<script defer src="/assets/focus.v6436.js"></script></body>', 1)
    path.write_text(text, encoding='utf-8')

CSS.write_text(css, encoding='utf-8')
JS.write_text(js, encoding='utf-8')
VERSION.write_text('6.43.6\n', encoding='utf-8')

entry = '''## V6.43.6 — Home IRI focus\n\n- Keeps the Home IRI example concise by default while preserving the deeper report content behind a native accessible disclosure.\n- Leaves the dedicated IRI page unchanged as the full explanation surface.\n- Adds only a Home-scoped CSS/JS enhancement; without JavaScript the original complete report remains visible.\n\n'''
old = CHANGELOG.read_text(encoding='utf-8')
if not old.startswith('## V6.43.6'):
    CHANGELOG.write_text(entry + old, encoding='utf-8')

print({'version':'6.43.6','homes':[str(p) for p in HOME_FILES],'css':str(CSS),'js':str(JS)})
