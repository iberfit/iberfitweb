from pathlib import Path
import json, re, subprocess, sys

root=Path('candidate/v628')
base='5dd5baeddbf5d6dab9d7f6523945482ddce35b9b'
link='<link href="/assets/mobile.v6435.css" rel="stylesheet"/>'
homes={'index.html','en/index.html'}
htmls=sorted(p.relative_to(root).as_posix() for p in root.rglob('*.html'))

def fail(kind, rel='', extra=''):
    print(f'FAIL::{kind}::{rel}::{extra}', file=sys.stderr, flush=True)
    raise SystemExit(1)

print(f'STATIC_QA html={len(htmls)}', flush=True)
if len(htmls)!=33: fail('HTML_COUNT', extra=str(len(htmls)))
for rel in htmls:
    now=(root/rel).read_text(encoding='utf-8')
    try:
        old=subprocess.check_output(['git','show',f'{base}:candidate/v628/{rel}'],text=True)
    except Exception as e:
        fail('BASE_READ',rel,repr(e))
    if now.count(link)!=1: fail('CSS_LINK_COUNT',rel,str(now.count(link)))
    clean=now.replace(link,'')
    if rel not in homes and clean != old:
        idx=next((i for i,(a,b) in enumerate(zip(old,clean)) if a!=b),min(len(old),len(clean)))
        fail('UNEXPECTED_BODY_CHANGE',rel,f'first_diff={idx}; old_len={len(old)}; clean_len={len(clean)}; old={old[max(0,idx-40):idx+80]!r}; new={clean[max(0,idx-40):idx+80]!r}')
    old_head=old.split('</head>',1)[0]
    new_head=clean.split('</head>',1)[0]
    if old_head != new_head:
        idx=next((i for i,(a,b) in enumerate(zip(old_head,new_head)) if a!=b),min(len(old_head),len(new_head)))
        fail('HEAD_DRIFT',rel,f'first_diff={idx}')
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', now, re.S):
        try: json.loads(raw)
        except Exception as e: fail('JSONLD',rel,repr(e))
    if rel in homes:
        def anchors(t): return re.findall(r'<a\b[^>]*href="[^"]+"[^>]*>',t)
        oa,na=anchors(old),anchors(now)
        if oa!=na:
            first=next((i for i,(a,b) in enumerate(zip(oa,na)) if a!=b),min(len(oa),len(na)))
            fail('ANCHOR_DRIFT',rel,f'old={len(oa)} new={len(na)} first={first}; oa={oa[first] if first<len(oa) else None}; na={na[first] if first<len(na) else None}')
        old_answers=re.findall(r'<article class="answer-item" data-aeo-answer>.*?</article>',old,re.S)
        new_answers=re.findall(r'<article class="answer-item" data-aeo-answer>.*?</article>',now,re.S)
        if old_answers!=new_answers: fail('AEO_DRIFT',rel,f'old={len(old_answers)} new={len(new_answers)}')
    print(f'PASS::{rel}', flush=True)
print('STATIC_QA_OK', flush=True)
