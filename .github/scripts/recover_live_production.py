#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

BASE = "https://iberfit.cl"
OUT = Path("recovery/live-production")
UA = "IBERFIT-Recovery-Audit/2026-09-11 (+https://iberfit.cl)"
TIMEOUT = 25

class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("href", "src"):
            value = a.get(key)
            if value:
                self.refs.append(value)
        srcset = a.get("srcset")
        if srcset:
            self.refs.extend(x.strip().split()[0] for x in srcset.split(",") if x.strip())

def request(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = r.read()
        return data, dict(r.headers.items()), r.geturl(), getattr(r, "status", 200)

def same_origin_ref(ref: str, current: str) -> str | None:
    if not ref or ref.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    absolute = urllib.parse.urljoin(current, ref)
    p = urllib.parse.urlsplit(absolute)
    if p.scheme not in ("http", "https") or p.netloc != "iberfit.cl":
        return None
    clean = urllib.parse.urlunsplit(("https", "iberfit.cl", p.path or "/", p.query, ""))
    return clean

def target_for(url: str, content_type: str) -> Path:
    p = urllib.parse.urlsplit(url)
    path = p.path or "/"
    if path == "/":
        return OUT / "site" / "index.html"
    if path.endswith("/"):
        return OUT / "site" / path.lstrip("/") / "index.html"
    return OUT / "site" / path.lstrip("/")

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

OUT.mkdir(parents=True, exist_ok=True)
site = OUT / "site"
site.mkdir(parents=True, exist_ok=True)

seed = {BASE + "/", BASE + "/robots.txt", BASE + "/sitemap.xml", BASE + "/manifest.webmanifest"}
sitemap_bytes, sitemap_headers, _, _ = request(BASE + "/sitemap.xml")
try:
    root = ET.fromstring(sitemap_bytes)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for loc in root.findall(".//s:loc", ns):
        if loc.text:
            seed.add(loc.text.strip())
except Exception:
    pass

queue = list(sorted(seed))
seen = set()
records = []
errors = []

while queue:
    url = queue.pop(0)
    if url in seen:
        continue
    seen.add(url)
    try:
        data, headers, final_url, status = request(url)
        ctype = headers.get("Content-Type", "")
        target = target_for(url, ctype)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rel = target.relative_to(OUT).as_posix()
        records.append({
            "url": url,
            "final_url": final_url,
            "status": status,
            "content_type": ctype,
            "bytes": len(data),
            "sha256": sha256(data),
            "path": rel,
            "cache_control": headers.get("Cache-Control"),
            "etag": headers.get("ETag"),
            "last_modified": headers.get("Last-Modified"),
        })

        text = None
        if "text/html" in ctype:
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("utf-8", errors="replace")
            parser = Collector()
            parser.feed(text)
            for ref in parser.refs:
                candidate = same_origin_ref(ref, url)
                if candidate and candidate not in seen:
                    queue.append(candidate)
        elif "text/css" in ctype:
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("utf-8", errors="replace")
            for ref in re.findall(r"url\(([^)]+)\)", text):
                ref = ref.strip().strip("'\"")
                candidate = same_origin_ref(ref, url)
                if candidate and candidate not in seen:
                    queue.append(candidate)
    except Exception as exc:
        errors.append({"url": url, "error": repr(exc)})

# Deterministic manifest.
records.sort(key=lambda x: x["path"])
manifest_lines = [f'{r["sha256"]}  {r["path"]}' for r in records]
(OUT / "SHA256SUMS.txt").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

meta = {
    "captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "origin": BASE,
    "files": len(records),
    "errors": errors,
    "records": records,
}
(OUT / "RECOVERY_META.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if errors:
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    raise SystemExit(f"Recovery completed with {len(errors)} errors")

print(json.dumps({"origin": BASE, "files": len(records), "errors": 0}, indent=2))
