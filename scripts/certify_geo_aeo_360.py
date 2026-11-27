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
    ap.add_argument("--version", help="Expected public release version")
    args = ap.parse_args()
    version = (ROOT / "VERSION").read_text().strip()
    assert all(x.isdigit() for x in version.split(".")) and len(version.split(".")) >= 3, version
    assert args.version is None or args.version == version, (args.version, version)
    package = f"IBERFIT-WEB-{version}.zip"
    out = pathlib.Path(args.out)
    urls = [x.text for x in ET.parse(ROOT / "sitemap.xml").findall("{*}url/{*}loc")]
    assert len(urls) == len(set(urls)) == 32
    assert all(u.startswith(ORIGIN + "/") for u in urls)
    robots = (ROOT / "robots.txt").read_text()
    assert "User-agent: OAI-SearchBot\nAllow: /" in robots
    assert "Sitemap: " + ORIGIN + "/sitemap.xml" in robots
    subprocess.run(["python3", ".github/scripts/sitemap_lastmod.py"], check=True)
    subprocess.run(["git", "diff", "--exit-code", "--", str(ROOT / "sitemap.xml")], check=True)
    subprocess.run(["python3", ".github/scripts/sitemap_lastmod.py", "--check"], check=True)
    for path in FROZEN:
        actual = (ROOT / path).read_bytes()
        original = subprocess.check_output(["git", "show", BASE + ":" + (ROOT/path).as_posix()])
        # Preserve the original freeze except for the exact, approved 6.43.32
        # commercial link/text transformation. Never relax the remaining bytes.
        if tuple(map(int, version.split("."))) >= (6, 43, 32):
            import runpy
            transform = runpy.run_path(".github/scripts/qa_v64332_iri_routes.py")["expected"]
            original = transform(original.decode("utf-8"), path).encode("utf-8")
        # 6.43.34 explicitly authorizes editorial text updates on the Las Condes
        # local landing page only; pin the reviewed bytes, not a relaxed freeze.
        if tuple(map(int, version.split("."))) >= (6, 43, 34) and path == "entrenador-personal-las-condes/index.html":
            original = subprocess.check_output(["git", "show", "d8103afe76a8552532ffefc45c5564427ccda8ed:" + (ROOT/path).as_posix()])
        assert actual == original, "Frozen page changed beyond the approved commercial scope: " + path
    # Exact release scope: preserve every HTML byte, IRI content, commercial
    # path, imagery, analytics, headers and other assets in this maintenance release.
    if version == "6.43.33":
        prior = "4f5769613f6b724adf6843f9d6588a9833a89f2c"
        changed = set(subprocess.check_output(["git", "diff", "--name-only", prior, "HEAD", "--", ROOT.as_posix()], text=True).splitlines())
        allowed = {str(ROOT / p) for p in ("VERSION", "CHANGELOG.md", "assets/ux.v64322.css", "assets/ux.v64322.js")}
        assert changed == allowed, (changed - allowed, allowed - changed)
        print("A11Y_RELEASE_SCOPE_OK", len(changed))
    if version == "6.43.34":
        prior = "4e37bc9d1ff22f4a3ded1a45f36be2de14644f74"
        local = ["entrenador-personal-las-condes/index.html","entrenamiento-personal-providencia/index.html","entrenador-personal-vitacura/index.html","entrenador-personal-lo-barnechea/index.html","personal-trainer-nunoa/index.html","entrenador-personal-la-reina/index.html","entrenador-personal-penalolen/index.html","en/personal-trainer-las-condes/index.html","en/personal-training-providencia/index.html","en/personal-trainer-vitacura/index.html","en/personal-trainer-lo-barnechea/index.html","en/personal-trainer-nunoa/index.html","en/personal-trainer-la-reina/index.html","en/personal-trainer-penalolen/index.html"]
        changed = set(subprocess.check_output(["git", "diff", "--name-only", prior, "HEAD", "--", ROOT.as_posix()], text=True).splitlines())
        required = {str(ROOT / p) for p in local + ["VERSION", "CHANGELOG.md"]}
        allowed = required | {str(ROOT / "sitemap.xml")}
        assert required <= changed <= allowed, (changed - allowed, required - changed)
        import re
        for path in local:
            rel = (ROOT/path).as_posix()
            original = subprocess.check_output(["git", "show", prior+":"+rel]).decode("utf-8")
            actual = (ROOT/path).read_text(encoding="utf-8")
            approved = subprocess.check_output(["git", "show", "d8103afe76a8552532ffefc45c5564427ccda8ed:"+rel]).decode("utf-8")
            assert actual == approved, ("Unreviewed editorial text", path)
            # Only visible text inside main may change; preserve every tag,
            # attribute, href, head, footer and structured-data byte.
            def structure(html):
                match = re.search(r"<main\b[\s\S]*?</main>", html)
                assert match
                return (html[:match.start()], re.findall(r"<[^>]+>", match.group()), html[match.end():])
            assert structure(original) == structure(actual), ("Markup changed", path)
            assert ("El Diagnóstico IRI es opcional." in actual if not path.startswith("en/") else "The IRI Assessment is optional." in actual)
        print("LOCAL_EDITORIAL_SCOPE_OK", len(local), "pages; HTML structure and other public assets preserved")
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
    with zipfile.ZipFile(out / package, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            hashes[rel] = hashlib.sha256(data).hexdigest()
            z.writestr(rel, data)
    with zipfile.ZipFile(out / package) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(hashes)
        for name in z.namelist():
            assert hashlib.sha256(z.read(name)).hexdigest() == hashes[name]
    (out / "SHA256.json").write_text(json.dumps({"source":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),"files":hashes},indent=2)+"\n")
    print(f"PASS: {len(pages)} pages, reciprocal hreflang, JSON-LD, internal links, frozen pages, {len(hashes)} packaged files")
if __name__ == "__main__":
    main()
