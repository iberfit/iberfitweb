#!/usr/bin/env python3
"""Commercial authority contract: only truthful claims and connected bilingual journeys."""
from pathlib import Path
from html.parser import HTMLParser
import subprocess
import json
import re
from urllib.parse import urlsplit

ROOT = Path("candidate/v628")
BASE = "feec0f32f0aef856dfa3b73cd89c8b49624da6a2"
class Doc(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.feed(path.read_text(encoding="utf-8"))
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"): self.ids.append(a["id"])
        if tag == "a" and a.get("href"): self.hrefs.append(a["href"])

pairs = [
    ("metodo/index.html", "en/method/index.html"),
    ("sobre-iberfit/index.html", "en/about/index.html"),
    ("contacto/index.html", "en/contact/index.html"),
    ("diagnostico-iri/index.html", "en/iri-assessment/index.html"),
    ("presencial/index.html", "en/in-person/index.html"),
    ("hibrido/index.html", "en/hybrid/index.html"),
    ("online/index.html", "en/online/index.html"),
    ("privacidad/index.html", "en/privacy/index.html"),
]
goals = {"objetivos"}
for lang in (0,1):
    method, about, contact, iri = [ROOT / pairs[i][lang] for i in range(4)]
    assert goals <= set(Doc(method).ids)
    assert not ({"fuerza","running","condicion-fisica","retomar"} & set(Doc(method).ids)), "Avoid goal catalogue"
    approved = ("El entrenamiento al servicio de tus objetivos" if lang == 0 else "Training shaped around your goals")
    assert approved in method.read_text(), (method, approved)
    assert {"evidencia","experiencias-reales"} <= set(Doc(about).ids)
    options = contact.read_text()
    for phrase in (("Desarrollar fuerza o rendimiento","Coordinar solo el Diagnóstico IRI") if lang == 0 else ("Develop strength or performance","Arrange the IRI Assessment only")):
        assert phrase in options, (contact, phrase)
    expected = "/contacto/#orientador" if lang == 0 else "/en/contact/#orientador"
    assert expected in Doc(iri).hrefs
    assert expected in Doc(method).hrefs
    for i in range(4,7):
        service = Doc(ROOT/pairs[i][lang])
        assert any(a.startswith("/metodo/#" if lang == 0 else "/en/method/#") for a in service.hrefs)
    for i in (3,4,5,6):
        p=ROOT/pairs[i][lang]
        graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',p.read_text(),re.S).group(1))["@graph"]
        services=[n for n in graph if n.get("@type")=="Service"]
        page=next(n for n in graph if n.get("@id","").endswith("#webpage"))
        assert len(services)==1 and page.get("mainEntity",{}).get("@id")==services[0]["@id"], p
        assert services[0].get("provider",{}).get("@id")=="https://iberfit.cl/#organization", p
    for i in range(8):
        path = ROOT / pairs[i][lang]
        doc = Doc(path)
        for a in doc.hrefs:
            u = urlsplit(a)
            if u.scheme or u.netloc or not u.fragment: continue
            if u.fragment not in goals | {"evidencia","experiencias-reales","orientador","metodo-en-accion","method-in-action"}: continue
            target = ROOT / u.path.strip("/") / "index.html" if u.path else path
            assert target.is_file(), (path,a)
            assert u.fragment in Doc(target).ids, (path,a)
# Protect all prior visual assets, scripts, home and local landing pages from unintended change.
changes = subprocess.check_output(["git","diff","--name-only",BASE,"HEAD","--","candidate/v628"],text=True).splitlines()
allow = {str(ROOT / p) for pair in pairs for p in pair} | {str(ROOT / p) for p in ("VERSION","CHANGELOG.md","sitemap.xml","llms.txt","assets/analytics-config.js")}
assert set(changes) == allow, (set(changes)-allow,allow-set(changes))
print("COMMERCIAL_AUTHORITY_OK: 16 HTML pages, bilingual journey links, goals, standalone IRI, protected assets and pages, bilingual service entities")
