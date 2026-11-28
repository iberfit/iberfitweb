#!/usr/bin/env python3
"""Fail closed when current web identity diverges from the approved geometry."""
from pathlib import Path
import hashlib, json, re, struct, subprocess, xml.etree.ElementTree as ET
ROOT = Path("candidate/v628")
ASSETS = ROOT / "assets"
NS = "{http://www.w3.org/2000/svg}"
ROT = "rotate(4.51398846 347 312)"
def blob(b): return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def paths(x): return [p.attrib["d"] for p in x.iter(NS+"path")]

def transform(html):
    """Exact, narrow migration from 6.43.36; preserve all other page bytes."""
    def signature(m):
        a, tagline, end = m.groups()
        foot = "footer-brand" in a
        variant = "oscuro" if foot else "claro"
        alt = "IBERFIT" if foot else ""
        loading = ' loading="lazy"' if foot else ""
        return a + f'<img class="brand-mark" src="/assets/iberfit-firma-norte-{variant}.svg" alt="{alt}" decoding="async"{loading} width="660" height="140"/><small class="brand-caption">{tagline}</small>' + end
    html, count = re.subn(r'(<a\b[^>]*class="brand(?: footer-brand)?"[^>]*>)<img\b[^>]*class="brand-mark"[^>]*\/?><span class="brand-text"><span>IBERFIT</span><small>([\s\S]*?)</small></span>(</a>)', signature, html)
    assert count == 2, ("expected two legacy signatures", count)
    def mark(m):
        return re.sub(r'width="\d+"', 'width="46"', m.group().replace("/assets/iberfit-isotipo-2027.svg","/assets/iberfit-isotipo-norte-verde.svg"))
    html = re.sub(r'<img\b[^>]*src="/assets/iberfit-isotipo-2027\.svg"[^>]*>', mark, html)
    for name in ("styles.v628","hardening.v630","polish.v631","quality.v632","ux.v64322"):
        html = html.replace("/assets/"+name+".css","/assets/"+name+".norte.css")
    for old,new in (("favicon-2027.ico","favicon-norte.ico"),("favicon-2027-48x48.png","favicon-norte-48x48.png"),("favicon-2027-96x96.png","favicon-norte-96x96.png"),("favicon-2027-192x192.png","favicon-norte-192x192.png"),("favicon-2027-512x512.png","favicon-norte-512x512.png"),("apple-touch-icon-2027.png","apple-touch-icon-norte.png")):
        html = html.replace(old,new)
    return html

def check():
    if tuple(map(int,(ROOT/"VERSION").read_text().strip().split("."))) < (6,43,37): return
    original = Path("brand/2027/Principal_Dorado.svg").read_bytes()
    assert blob(original) == "513e821acd346cb55d1939b483507b477ea3afc7"
    geom = paths(ET.fromstring(original))
    for name, sha in {"iberfit-firma-norte-claro.svg":"3fd64a8b031c49aef570712af8019c2f2586505f","iberfit-firma-norte-oscuro.svg":"7a4177bd1f4ce856be5c0dbcaaf39892c8ff9afa","iberfit-isotipo-norte-dorado.svg":"a97753e12ff059a54f971310acde03d6b9500d9a","iberfit-isotipo-norte-verde.svg":"fd0905482979eea88b41da130b1324a1081d46be"}.items():
        b=(ASSETS/name).read_bytes()
        assert blob(b)==sha, name
        root=ET.fromstring(b)
        assert paths(root)[:8]==geom and any(g.get("transform")==ROT for g in root.iter(NS+"g")),name
    pages=list(ROOT.rglob("*.html"))
    assert len(pages)==33
    for p in pages:
        c=p.read_text(encoding="utf-8")
        if (ROOT/"VERSION").read_text().strip()=="6.43.37":
            prior=subprocess.check_output(["git","show","8c80d4b9178a99f837c7df14ee82eccec660f461:"+p.as_posix()]).decode("utf-8")
            assert p.read_bytes()==transform(prior).encode("utf-8"), ("Non-identity page change",p)
        assert c.count('class="brand-mark"')==2 and c.count("/assets/iberfit-firma-norte-claro.svg")==1 and c.count("/assets/iberfit-firma-norte-oscuro.svg")==1,p
        assert not re.search(r'brand-text|iberfit-isotipo-2027|favicon-2027|apple-touch-icon-2027',c),p
        for src in re.findall(r'href="(/assets/[^"]+\.css)"',c):
            assert (ROOT/src.lstrip("/")).is_file(),(p,src)
    manifest=json.loads((ROOT/"manifest.webmanifest").read_text())
    assert len(manifest["icons"])==4
    assert {i["purpose"] for i in manifest["icons"]}=={"any","maskable"}
    for i in manifest["icons"]:
        data=(ROOT/i["src"].lstrip("/")).read_bytes()
        assert data[:8]==b"\x89PNG\r\n\x1a\n"
        assert tuple(map(int,i["sizes"].split("x")))==struct.unpack(">II",data[16:24])
    print("NORTE_IDENTITY_OK: 33 HTML; exact vector hashes; four manifest icons")
if __name__=="__main__": check()
