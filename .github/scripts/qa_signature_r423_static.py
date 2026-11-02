#!/usr/bin/env python3
from pathlib import Path
import re, subprocess, hashlib, json

ROOT=Path(__file__).resolve().parents[2]
BASE="424700ae15c6138c8a07f15f82f5b34d62c51a9f"
PAGES=[
 "candidate/v628/index.html",
 "candidate/v628/diagnostico-iri/index.html",
 "candidate/v628/online/index.html",
]

def show_base(path):
    return subprocess.check_output(["git","show",f"{BASE}:{path}"],cwd=ROOT,text=True)

def tags(pattern,text):
    return re.findall(pattern,text,re.I|re.S)

def one(pattern,text,name):
    m=re.search(pattern,text,re.I|re.S)
    if not m: raise AssertionError(f"{name}_MISSING")
    return re.sub(r"\s+"," ",m.group(1)).strip()

def norm_jsonld(text):
    vals=[]
    for raw in tags(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>',text):
        vals.append(re.sub(r"\s+"," ",raw).strip())
    return vals

def anchor_hrefs(text):
    return tags(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>',text)

def script_srcs(text):
    return tags(r'<script\b[^>]*src=["\']([^"\']+)["\'][^>]*>',text)

def hreflang(text):
    return sorted(tags(r'<link\b[^>]*hreflang=["\']([^"\']+)["\'][^>]*href=["\']([^"\']+)["\'][^>]*>',text))

results=[]
for rel in PAGES:
    base=show_base(rel)
    cur=(ROOT/rel).read_text()
    checks={}
    checks["title"]=one(r'<title>(.*?)</title>',cur,"TITLE")==one(r'<title>(.*?)</title>',base,"BASE_TITLE")
    checks["canonical"]=one(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']',cur,"CANONICAL")==one(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']',base,"BASE_CANONICAL")
    checks["robots"]=one(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']',cur,"ROBOTS")==one(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']',base,"BASE_ROBOTS")
    checks["hreflang"]=hreflang(cur)==hreflang(base)
    checks["jsonld"]=norm_jsonld(cur)==norm_jsonld(base)
    checks["scripts"]=script_srcs(cur)==script_srcs(base)
    checks["anchors"]=anchor_hrefs(cur)==anchor_hrefs(base)
    checks["h1"]=one(r'<h1[^>]*>(.*?)</h1>',cur,"H1")==one(r'<h1[^>]*>(.*?)</h1>',base,"BASE_H1")
    checks["signature_css"]='/assets/signature-r423.css' in cur
    checks["signature_body"]='data-signature="r423"' in cur
    if rel.endswith("v628/index.html"):
        checks["home_hero_product"]='class="editorial-hero-media signature-product-proof"' in cur and 'src="/assets/app-online-progress.webp"' in cur
        checks["home_old_hero_removed"]='Escena ilustrativa · Entrenamiento presencial</figcaption>' not in cur
        checks["home_human_media_removed"]='photo-initial-eval-1448.webp' not in cur and 'photo-trainer-session-1448.webp' not in cur
    if rel.endswith("diagnostico-iri/index.html"):
        checks["iri_human_media_removed"]='photo-initial-eval-1448.webp' not in cur
    failed=[k for k,v in checks.items() if not v]
    if failed: raise AssertionError(f"{rel} FAILED {failed}")
    results.append({"page":rel,"checks":checks,"sha256":hashlib.sha256(cur.encode()).hexdigest()})

print(json.dumps({"schema":"iberfit.web.signature-r423.static-qa.v1","baseline":BASE,"results":results},ensure_ascii=False,indent=2))
