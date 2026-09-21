from pathlib import Path

ROOT = Path('candidate/v628')
VERSION = ROOT / 'VERSION'
CHANGELOG = ROOT / 'CHANGELOG.md'
CSS = ROOT / 'assets/chrome.v6439.css'
JS = ROOT / 'assets/chrome.v6439.js'

assert VERSION.read_text(encoding='utf-8').strip() == '6.43.8'
htmls = sorted(ROOT.rglob('*.html'))
assert len(htmls) == 33

css = r'''/* IBERFIT WEB V6.43.9 — mobile chrome balance */
@media(max-width:720px){
  .device-dock.dock-suppressed-v6439{
    opacity:0!important;
    transform:translateY(calc(100% + 1.35rem))!important;
    pointer-events:none!important;
  }
}
@media(prefers-reduced-motion:reduce){
  .device-dock{transition:none!important}
}
'''

js = r'''(()=>{
  'use strict';
  const init=()=>{
    const dock=document.querySelector('.device-dock');
    if(!dock)return;
    const mobile=matchMedia('(max-width:720px)');
    let ctaVisible=false,footerVisible=false;
    const isEditable=el=>{
      if(!el||el===document.body)return false;
      if(el.matches?.('textarea,select,[contenteditable="true"],[contenteditable=""]'))return true;
      if(!el.matches?.('input'))return false;
      const type=(el.getAttribute('type')||'text').toLowerCase();
      return !['button','submit','reset','checkbox','radio','range','color','file','hidden','image'].includes(type);
    };
    const visible=el=>!!(el&&el.isConnected&&!el.hidden&&el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden'&&getComputedStyle(el).display!=='none');
    const sync=()=>{
      if(!mobile.matches){
        dock.classList.remove('dock-suppressed-v6439');
        dock.removeAttribute('data-dock-suppressed');
        dock.removeAttribute('aria-hidden');
        dock.inert=false;
        return;
      }
      const reasons=[];
      if(visible(document.querySelector('.consent-banner')))reasons.push('consent');
      if(visible(document.querySelector('.consent-modal')))reasons.push('privacy');
      if(document.body.classList.contains('nav-panel-open'))reasons.push('menu');
      if(isEditable(document.activeElement))reasons.push('editing');
      if(ctaVisible)reasons.push('cta');
      if(footerVisible)reasons.push('footer');
      const suppressed=reasons.length>0;
      dock.classList.toggle('dock-suppressed-v6439',suppressed);
      if(suppressed){
        dock.dataset.dockSuppressed=reasons.join(',');
        dock.setAttribute('aria-hidden','true');
        dock.inert=true;
      }else{
        dock.removeAttribute('data-dock-suppressed');
        dock.removeAttribute('aria-hidden');
        dock.inert=false;
      }
    };
    const observeSurface=(selector,setter,threshold)=>{
      const el=document.querySelector(selector);if(!el||!('IntersectionObserver'in window))return;
      new IntersectionObserver(entries=>{
        const e=entries[0];setter(!!(e?.isIntersecting&&e.intersectionRatio>=threshold));sync();
      },{threshold:[0,threshold,.5,1]}).observe(el);
    };
    observeSurface('.cta-panel',v=>ctaVisible=v,.2);
    observeSurface('.site-footer',v=>footerVisible=v,.02);
    new MutationObserver(sync).observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['class','hidden','style']});
    document.addEventListener('focusin',sync,true);
    document.addEventListener('focusout',()=>requestAnimationFrame(sync),true);
    addEventListener('resize',sync,{passive:true});
    addEventListener('pageshow',sync,{passive:true});
    mobile.addEventListener?.('change',sync);
    window.visualViewport?.addEventListener('resize',sync,{passive:true});
    sync();
  };
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',init,{once:true}):init();
})();
'''

for path in htmls:
    text = path.read_text(encoding='utf-8')
    assert '/assets/chrome.v6439.css' not in text
    assert '/assets/chrome.v6439.js' not in text
    text = text.replace('</head>', '<link href="/assets/chrome.v6439.css" rel="stylesheet"/></head>', 1)
    text = text.replace('</body>', '<script defer src="/assets/chrome.v6439.js"></script></body>', 1)
    path.write_text(text, encoding='utf-8')

CSS.write_text(css, encoding='utf-8')
JS.write_text(js, encoding='utf-8')
VERSION.write_text('6.43.9\n', encoding='utf-8')
entry = '''## V6.43.9 — Mobile chrome balance\n\n- Keeps the mobile navigation dock available during exploration but suppresses it whenever a higher-priority surface is active.\n- The dock now yields to consent/privacy, the open navigation panel, editable controls, the final CTA and the footer, then returns automatically.\n- Destinations, analytics, navigation semantics and desktop behaviour remain unchanged.\n\n'''
old = CHANGELOG.read_text(encoding='utf-8')
if not old.startswith('## V6.43.9'):
    CHANGELOG.write_text(entry + old, encoding='utf-8')
print({'version':'6.43.9','html':len(htmls),'assets':[str(CSS),str(JS)]})
