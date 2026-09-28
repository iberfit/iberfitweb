from pathlib import Path
import re

ROOT=Path('candidate/v628')

PATCHES={
  'entrenamiento-personal-providencia/index.html':(
    '¿Quieres aprovechar mejor una semana que ya es activa?',
    'La modalidad híbrida conecta sesiones directas con trabajo guiado para integrar entrenamiento y movimiento cotidiano dentro del mismo plan.'
  ),
  'en/personal-training-providencia/index.html':(
    'Want to make the most of a week that is already active?',
    'Hybrid coaching connects direct sessions with guided work so training and everyday movement can belong to the same plan.'
  ),
}


def patch_scope(text,title,body,rel):
    marker='<div class="container scope-note reveal">'
    start=text.find(marker)
    assert start>=0,f'{rel}: scope note not found'
    token_re=re.compile(r'</?div\b[^>]*>',re.I)
    depth=0
    end=None
    for m in token_re.finditer(text,start):
        if m.group(0).startswith('</'):
            depth-=1
            if depth==0:
                end=m.end();break
        else:
            depth+=1
    assert end,f'{rel}: unbalanced scope note'
    block=text[start:end]
    block,n=re.subn(r'<span>.*?</span>',f'<span>{title}</span>',block,count=1,flags=re.S);assert n==1
    block,n=re.subn(r'<p>.*?</p>',f'<p>{body}</p>',block,count=1,flags=re.S);assert n==1
    return text[:start]+block+text[end:]

for rel,(title,body) in PATCHES.items():
    p=ROOT/rel
    text=p.read_text(encoding='utf-8')
    wa=re.findall(r'https://wa\.me/[^\"]+',text)
    text=patch_scope(text,title,body,rel)
    assert re.findall(r'https://wa\.me/[^\"]+',text)==wa
    p.write_text(text,encoding='utf-8')

print('PATCH_V64324_POSITIVE_SCOPE_NOTES_OK',len(PATCHES))
