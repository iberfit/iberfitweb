#!/usr/bin/env python3
"""Certify and package the static public website; never deploy or access Supabase."""
import argparse
import hashlib
import json
import pathlib
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, urljoin

BASE = "424700ae15c6138c8a07f15f82f5b34d62c51a9f"
ORIGIN = "https://iberfit.cl"
ROOT = pathlib.Path("candidate/v628")
FROZEN = ("index.html", "entrenador-personal-las-condes/index.html")
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.canonical = []
        self.alt = {}
        self.refs = []
        self.schema = []
        self.capture = False
        self.lang = ""
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang", "")
        if tag == "h1":
            self.h1 += 1
        if tag == "link":
            if a.get("rel") == "canonical":
                self.canonical.append(a.get("href"))
            if a.get("rel") == "alternate" and a.get("hreflang"):
                self.alt[a["hreflang"]] = a.get("href")
        if tag in ("a", "link", "script", "img", "source"):
            for key in ("href", "src"):
                if a.get(key):
                    self.refs.append(a[key])
        if tag == "script" and a.get("type") == "application/ld+json":
            self.capture = True
            self.schema.append("")
    def handle_data(self, data):
        if self.capture:
            self.schema[-1] += data
    def handle_endtag(self, tag):
        if tag == "script":
            self.capture = False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="release-web")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    urls = [x.text for x in ET.parse(ROOT / "sitemap.xml").findall("{*}url/{*}loc")]
    assert len(urls) == len(set(urls)) == 32
    assert all(u.startswith(ORIGIN + "/") for u in urls)
    robots = (ROOT / "robots.txt").read_text()
    assert "User-agent: OAI-SearchBot\nAllow: /" in robots
    assert "Sitemap: " + ORIGIN + "/sitemap.xml" in robots
    assert (ROOT / "VERSION").read_text().strip() == "6.43.29"
    subprocess.run(["python3", ".github/scripts/sitemap_lastmod.py", "--check"], check=True)
    for path in FROZEN:
        actual = (ROOT / path).read_bytes()
        original = subprocess.check_output(["git", "show", BASE + ":" + (ROOT/path).as_posix()])
        assert actual == original, "Frozen page changed: " + path
    pages = {}
    missing = []
    for url in urls:
        path = urlsplit(url).path
        page = Page()
        page.feed((ROOT / path.lstrip("/") / "index.html").read_text(encoding="utf-8"))
        assert page.canonical == [url], (url, page.canonical)
        assert page.h1 == 1, (url, "H1", page.h1)
        assert page.lang in ("en", "es"), (url, page.lang)
        assert page.schema, (url, "missing schema")
        for schema in page.schema:
            json.loads(schema)
        pages[url] = page
        for ref in page.refs:
            if ref.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
                continue
            resolved = urlsplit(urljoin(url, ref))
            if resolved.netloc != "iberfit.cl":
                continue
            target = ROOT / unquote(resolved.path).lstrip("/")
            if not target.exists() and not (target / "index.html").exists():
                missing.append((url, ref))
    for url, page in pages.items():
        other = "en" if page.lang == "es" else "es"
        assert page.alt.get(page.lang) == url, (url, "self hreflang")
        alt = page.alt.get(other)
        assert alt in pages and pages[alt].alt.get(page.lang) == url, (url, "reciprocal hreflang")
    if missing:
        raise AssertionError("Broken internal references: " + repr(missing))
    out.mkdir(parents=True, exist_ok=True)
    hashes = {}
    with zipfile.ZipFile(out / "IBERFIT-WEB-6.43.29.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            hashes[rel] = hashlib.sha256(data).hexdigest()
            z.writestr(rel, data)
    with zipfile.ZipFile(out / "IBERFIT-WEB-6.43.29.zip") as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(hashes)
        for name in z.namelist():
            assert hashlib.sha256(z.read(name)).hexdigest() == hashes[name]
    (out / "SHA256.json").write_text(json.dumps({"source":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),"files":hashes},indent=2)+"\n")
    print(f"PASS: {len(pages)} pages, reciprocal hreflang, JSON-LD, internal links, frozen pages, {len(hashes)} packaged files")
if __name__ == "__main__":
    main()
