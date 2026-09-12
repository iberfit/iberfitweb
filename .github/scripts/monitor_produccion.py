#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from xml.etree import ElementTree as ET

BASE = "https://iberfit.cl"
UA = "IBERFIT-Synthetic-Monitor/1.0 (+https://iberfit.cl)"
TIMEOUT = 15
CRITICAL = [
    "/",
    "/diagnostico-iri/",
    "/metodo/",
    "/presencial/",
    "/hibrido/",
    "/online/",
    "/contacto/",
    "/privacidad/",
    "/en/",
]

FORBIDDEN_IRI = (
    "overall index",
    "overall score",
    "iri global",
    "índice global",
    "indice global",
    "puntuación global",
    "puntuacion global",
)

@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    ms: int | None = None

checks: list[Check] = []

def fetch(path: str, *, attempts: int = 2):
    url = path if path.startswith("http") else BASE + path
    last = None
    for attempt in range(attempts):
        start = time.perf_counter()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                data = response.read()
                ms = int((time.perf_counter() - start) * 1000)
                return response.status, response.geturl(), dict(response.headers.items()), data, ms
        except Exception as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(1.0)
    raise last

def add(name: str, ok: bool, detail: str, ms: int | None = None):
    checks.append(Check(name=name, ok=ok, detail=detail, ms=ms))

def text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")

# Rutas críticas.
for route in CRITICAL:
    try:
        status, final, headers, body, ms = fetch(route)
        body_text = text(body)
        ok = status == 200 and "IBERFIT" in body_text
        add(f"route {route}", ok, f"HTTP {status} · {len(body)} bytes · {final}", ms)
    except Exception as exc:
        add(f"route {route}", False, repr(exc))

# Headers de seguridad en la raíz.
try:
    status, final, headers, body, ms = fetch("/")
    lower = {k.lower(): v for k, v in headers.items()}
    expected = {
        "content-security-policy",
        "strict-transport-security",
        "x-content-type-options",
        "referrer-policy",
        "permissions-policy",
    }
    for header in sorted(expected):
        add(f"header {header}", header in lower, lower.get(header, "ausente"))
except Exception as exc:
    add("headers raíz", False, repr(exc))

# Sitemap: válido y todas sus URLs responden.
sitemap_urls: list[str] = []
try:
    status, final, headers, body, ms = fetch("/sitemap.xml")
    root = ET.fromstring(body)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = [loc.text.strip() for loc in root.findall(".//s:loc", ns) if loc.text]
    add("sitemap parse", status == 200 and len(sitemap_urls) >= 20, f"{len(sitemap_urls)} URLs", ms)
except Exception as exc:
    add("sitemap parse", False, repr(exc))

for url in sitemap_urls:
    try:
        status, final, headers, body, ms = fetch(url)
        add(f"sitemap {url}", status == 200, f"HTTP {status}", ms)
    except Exception as exc:
        add(f"sitemap {url}", False, repr(exc))

# Robots.
try:
    status, final, headers, body, ms = fetch("/robots.txt")
    body_text = text(body)
    add("robots", status == 200 and "sitemap:" in body_text.lower(), f"HTTP {status}", ms)
except Exception as exc:
    add("robots", False, repr(exc))

# Manifest.
try:
    status, final, headers, body, ms = fetch("/manifest.webmanifest")
    manifest = json.loads(text(body))
    ok = status == 200 and manifest.get("name") and manifest.get("icons")
    add("manifest", bool(ok), f"name={manifest.get('name')!r} · icons={len(manifest.get('icons', []))}", ms)
except Exception as exc:
    add("manifest", False, repr(exc))

# Reglas metodológicas/comerciales visibles.
for route in ("/", "/diagnostico-iri/", "/en/"):
    try:
        status, final, headers, body, ms = fetch(route)
        visible = re.sub(r"<script\b[^>]*>.*?</script>", " ", text(body), flags=re.I | re.S)
        visible = re.sub(r"<style\b[^>]*>.*?</style>", " ", visible, flags=re.I | re.S)
        visible = re.sub(r"<[^>]+>", " ", visible)
        low = " ".join(visible.lower().split())
        hits = [term for term in FORBIDDEN_IRI if term in low]
        add(f"IRI sin puntuación global {route}", not hits, "sin términos obsoletos" if not hits else ", ".join(hits))
    except Exception as exc:
        add(f"IRI sin puntuación global {route}", False, repr(exc))

try:
    status, final, headers, body, ms = fetch("/online/")
    visible = re.sub(r"<[^>]+>", " ", text(body))
    normalized = " ".join(visible.lower().split())
    add("nombre A distancia", "a distancia" in normalized, "presente" if "a distancia" in normalized else "ausente")
except Exception as exc:
    add("nombre A distancia", False, repr(exc))

failed = [c for c in checks if not c.ok]
slow = [c for c in checks if c.ms is not None and c.ms > 5000]

report = {
    "base": BASE,
    "checks": [asdict(c) for c in checks],
    "summary": {
        "total": len(checks),
        "failed": len(failed),
        "slow_over_5s": len(slow),
    },
}

print(json.dumps(report, ensure_ascii=False, indent=2))

if failed:
    print("\nFALLOS:", file=sys.stderr)
    for c in failed:
        print(f"- {c.name}: {c.detail}", file=sys.stderr)
    raise SystemExit(1)

print(f"\nIBERFIT producción: PASS · {len(checks)} controles · 0 fallos")
