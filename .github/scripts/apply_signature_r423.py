#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
PAGES=[
    ROOT/"candidate/v628/index.html",
    ROOT/"candidate/v628/diagnostico-iri/index.html",
    ROOT/"candidate/v628/online/index.html",
]
LINK='<link href="/assets/signature-r423.css" rel="stylesheet"/>'
BODY_SIG='data-signature="r423"'

def apply_common(text,path):
    if LINK not in text:
        anchor='<link href="/assets/ux.v64322.css" rel="stylesheet"/>'
        if anchor not in text:
            raise SystemExit(f"SIGNATURE_CSS_ANCHOR_MISSING:{path}")
        text=text.replace(anchor,anchor+LINK,1)
    m=re.search(r'<body\b([^>]*)>',text,re.I)
    if not m:
        raise SystemExit(f"BODY_MISSING:{path}")
    if BODY_SIG not in m.group(0):
        old=m.group(0)
        new=old[:-1]+' '+BODY_SIG+'>'
        text=text.replace(old,new,1)
    return text

def patch_home(text):
    pattern=re.compile(
        r'<figure class="editorial-hero-media"><picture><img\b[^>]*src="/assets/photo-park-training-1448\.webp"[^>]*></picture><figcaption>Escena ilustrativa · Entrenamiento presencial</figcaption></figure>',
        re.I
    )
    replacement=(
        '<figure class="editorial-hero-media signature-product-proof">'
        '<img alt="Vista real de seguimiento y evolución en la app IBERFIT con datos de demostración." '
        'decoding="async" fetchpriority="high" height="411" loading="eager" '
        'src="/assets/app-online-progress.webp" width="400"/>'
        '<figcaption>Vista real de seguimiento y evolución en la app IBERFIT · datos de demostración.</figcaption>'
        '</figure>'
    )
    if replacement in text:
        return text
    text,n=pattern.subn(replacement,text,count=1)
    if n!=1:
        raise SystemExit("HOME_HERO_MEDIA_ANCHOR_MISSING")
    return text

for path in PAGES:
    text=path.read_text(encoding="utf-8")
    text=apply_common(text,path)
    if path.name=="index.html" and path.parent.name=="v628":
        text=patch_home(text)
    path.write_text(text,encoding="utf-8")
    print("SIGNATURE_R423_APPLIED",path.relative_to(ROOT))
