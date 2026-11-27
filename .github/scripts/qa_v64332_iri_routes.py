#!/usr/bin/env python3
"""Exact-scope commercial journey guard; no visual assets or unrelated content changed."""
from pathlib import Path
import re
import subprocess
from urllib.parse import quote, urlsplit, parse_qs
import xml.etree.ElementTree as ET

BASE = "06ea490fc2fb71586d58dff3dec53c6ca58bd68f"
ROOT = Path("candidate/v628")
IRI = {"diagnostico-iri/index.html", "en/iri-assessment/index.html"}
HERO = {"index.html", "en/index.html", "metodo/index.html", "en/method/index.html"}
def expected(original, path):
    if path in IRI:
        return original
    en = path.startswith("en/")
    hero = re.search(r'<div class="hero-actions">.*?</div>', original, re.S)
    hero = hero.group(0) if hero else ""
    match = re.search(r'href="(https://wa\.me/[^"]+)"', hero)
    generic = ("Hi IBERFIT, I would like some guidance on your personal training options. Could we talk?" if en else
               "Hola IBERFIT, me gustaría recibir orientación sobre las modalidades de entrenamiento personal. ¿Podemos conversar?")
    wa = match.group(1) if match else "https://wa.me/56944040032?text=" + quote(generic, safe="-_.!~*'()")
    assert urlsplit(wa).hostname == "wa.me"
    assert "IRI" not in parse_qs(urlsplit(wa).query).get("text", [""])[0], (path, wa)
    def anchor(m):
        pos = m[2]
        label = ("Get in touch" if pos == "header" else "Talk to IBERFIT") if en else ("Hablemos" if pos == "header" else "Hablar con IBERFIT")
        return m[1] + "cta_contact_" + pos + m[3] + wa + m[4] + label + m[5]
    c, count = re.subn(r'(<a\b[^>]*data-track=")cta_iri_(header|footer)("[^>]*href=")[^"]+("[^>]*>)[^<]*(</a>)', anchor, original)
    assert count == 2, (path, count)
    if path in HERO:
        m = re.search(r'(<a\b[^>]*data-track="cta_hero_primary"[^>]*href=")([^"]+)("[^>]*>)([^<]+)(</a>)(<a\b[^>]*data-track="cta_hero_secondary"[^>]*href=")([^"]+)("[^>]*>)([^<]+)(</a>)', hero)
        assert m and m[2] == ("/en/iri-assessment/" if en else "/diagnostico-iri/") and m[7].startswith("https://wa.me/"), path
        primary = m[4] if path in {"index.html", "en/index.html"} else ("Help me get started" if en else "Orientarme para empezar")
        secondary = "Explore the IRI Assessment" if en else "Conocer el Diagnóstico IRI"
        c = c.replace(m[0], m[1]+m[7]+m[3]+primary+m[5]+m[6]+m[2]+m[8]+secondary+m[10], 1)
        sentence = " You can start training without purchasing the IRI Assessment." if en else " Puedes comenzar a entrenar sin contratar el Diagnóstico IRI."
        c, count = re.subn(r'(<p class="hero-support">)([^<]+)(</p>)', lambda m: m[1]+m[2]+sentence+m[3], c, count=1)
        assert count == 1, path
    return c

def main():
    urls = [x.text for x in ET.parse(ROOT/"sitemap.xml").findall("{*}url/{*}loc")]
    assert len(urls) == len(set(urls)) == 32
    changed = set()
    for url in urls:
        path = urlsplit(url).path.lstrip("/") + "index.html"
        target = ROOT/path
        before = subprocess.check_output(["git", "show", BASE+":"+target.as_posix()]).decode("utf-8")
        after = target.read_bytes().decode("utf-8")
        assert after == expected(before, path), ("Unexpected edit", path)
        if path not in IRI:
            assert len(re.findall(r'data-track="cta_contact_(?:header|footer)"', after)) == 2
            assert not re.search(r'data-track="cta_iri_(?:header|footer)"', after)
            changed.add(target.as_posix())
        else:
            assert after == before
    assert len(changed) == 30
    names = set(subprocess.check_output(["git","diff","--name-only",BASE,"HEAD","--",ROOT.as_posix()],text=True).splitlines())
    assert names == changed | {str(ROOT/"VERSION"), str(ROOT/"CHANGELOG.md"), str(ROOT/"sitemap.xml")}, names
    print("IRI_ROUTES_OK: 30 general routes, 2 independent IRI routes unchanged, 4 explicit hero choices, exact scope")
if __name__ == "__main__":
    main()
