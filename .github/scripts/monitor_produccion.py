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
APP_BASE = "https://app.iberfit.cl"
UA = "IBERFIT-Synthetic-Monitor/1.1 (+https://iberfit.cl)"
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
    required: bool = True

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

def add(name: str, ok: bool, detail: str, ms: int | None = None, *, required: bool = True):
    checks.append(Check(name=name, ok=ok, detail=detail, ms=ms, required=required))

def parse_version(value: str) -> tuple[int, int]:
    # VERSION debe ser un payload de versión, no HTML que contenga números por casualidad.
    match = re.fullmatch(r"\s*(\d+)\.(\d+)(?:\.\d+)?\s*", value)
    return (int(match.group(1)), int(match.group(2))) if match else (0, 0)

def text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")

production_version_raw = "unknown"
production_version = (0, 0)
try:
    status, final, headers, body, ms = fetch("/VERSION")
    production_version_raw = text(body).strip()
    production_version = parse_version(production_version_raw)
    add("version producción", status == 200 and production_version != (0, 0), production_version_raw, ms, required=False)
except Exception as exc:
    add("version producción", False, repr(exc), required=False)

require_v628_semantics = production_version >= (6, 28)
require_llms_discovery = production_version >= (6, 30)

# Rutas críticas.
for route in CRITICAL:
    try:
        status, final, headers, body, ms = fetch(route)
        body_text = text(body)
        ok = status == 200 and "IBERFIT" in body_text
        add(f"route {route}", ok, f"HTTP {status} · {len(body)} bytes · {final}", ms)
    except Exception as exc:
        add(f"route {route}", False, repr(exc))

# Disponibilidad pública de la app. La raíz debe servir el shell y la
# configuración M26 debe ser JavaScript real, nunca el fallback HTML del SPA.
try:
    status, final, headers, body, ms = fetch(APP_BASE + "/")
    body_text = text(body)
    root_ok = status == 200 and "IBERFIT" in body_text and "<html" in body_text.lower()
    add(
        "app pública /",
        root_ok,
        f"HTTP {status} · {len(body)} bytes · {final}",
        ms,
        required=True,
    )
except Exception as exc:
    add("app pública /", False, repr(exc), required=True)

try:
    app_runtime_path = "/m26/runtime-config.js"
    status, final, headers, body, ms = fetch(APP_BASE + app_runtime_path)
    body_text = text(body)
    content_type = headers.get("Content-Type", headers.get("content-type", ""))
    runtime_ok = (
        status == 200
        and "window.__IBERFIT_M26_RUNTIME__" in body_text
        and "<html" not in body_text.lower()
        and "javascript" in content_type.lower()
    )
    add(
        f"app pública {app_runtime_path}",
        runtime_ok,
        f"HTTP {status} · {len(body)} bytes · {content_type} · {final}",
        ms,
        required=True,
    )
except Exception as exc:
    add("app pública /m26/runtime-config.js", False, repr(exc), required=True)

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

# Descubrimiento por IA. llms.txt forma parte de V6.30 y solo es bloqueante
# cuando esa versión (o posterior) ya está realmente publicada.
try:
    status, final, headers, body, ms = fetch("/llms.txt")
    body_text = text(body)
    llms_ok = (
        status == 200
        and body_text.lstrip().startswith("# IBERFIT")
        and "https://iberfit.cl/sitemap.xml" in body_text
        and "Diagnóstico IRI" in body_text
    )
    add(
        "llms.txt",
        llms_ok,
        f"HTTP {status} · {len(body)} bytes",
        ms,
        required=require_llms_discovery,
    )
except Exception as exc:
    add("llms.txt", False, repr(exc), required=require_llms_discovery)

# Manifest.
try:
    status, final, headers, body, ms = fetch("/manifest.webmanifest")
    manifest = json.loads(text(body))
    ok = status == 200 and manifest.get("name") and manifest.get("icons")
    add("manifest", bool(ok), f"name={manifest.get('name')!r} · icons={len(manifest.get('icons', []))}", ms)
except Exception as exc:
    add("manifest", False, repr(exc))

# Las reglas semánticas nuevas se exigen solo cuando producción declare V6.28+.
published_version = None
try:
    status, final, headers, body, ms = fetch("/VERSION")
    raw_version = text(body).strip()
    parsed_version = parse_version(raw_version)
    if parsed_version != (0, 0):
        published_version = parsed_version
        add("versión publicada", True, raw_version, ms)
    else:
        add("versión publicada", True, "no declarada; se mantienen solo controles operativos", ms)
except Exception:
    add("versión publicada", True, "no expuesta; se mantienen solo controles operativos")

enforce_v628 = bool(published_version and published_version >= (6, 28))

if enforce_v628:
    for route in ("/", "/diagnostico-iri/", "/en/"):
        try:
            status, final, headers, body, ms = fetch(route)
            visible = re.sub(r"<script\\b[^>]*>.*?</script>", " ", text(body), flags=re.I | re.S)
            visible = re.sub(r"<style\\b[^>]*>.*?</style>", " ", visible, flags=re.I | re.S)
            visible = re.sub(r"<[^>]+>", " ", visible)
            low = " ".join(visible.lower().split())
            hits = [term for term in FORBIDDEN_IRI if term in low]
            add(
            f"IRI sin puntuación global {route}",
            not hits,
            "sin términos obsoletos" if not hits else ", ".join(hits),
            required=require_v628_semantics,
        )
        except Exception as exc:
            add(f"IRI sin puntuación global {route}", False, repr(exc), required=require_v628_semantics)

    try:
        status, final, headers, body, ms = fetch("/online/")
        visible = re.sub(r"<[^>]+>", " ", text(body))
        normalized = " ".join(visible.lower().split())
        add(
        "nombre A distancia",
        "a distancia" in normalized,
        "presente" if "a distancia" in normalized else "ausente",
        required=require_v628_semantics,
    )
    except Exception as exc:
        add("nombre A distancia", False, repr(exc), required=require_v628_semantics)
else:
    add("reglas V6.28", True, "pendientes hasta que producción publique V6.28+")

failed = [c for c in checks if not c.ok and c.required]
warnings = [c for c in checks if not c.ok and not c.required]
slow = [c for c in checks if c.ms is not None and c.ms > 5000]

report = {
    "base": BASE,
    "production_version": production_version_raw,
    "v628_semantics_required": require_v628_semantics,
    "checks": [asdict(c) for c in checks],
    "summary": {
        "total": len(checks),
        "failed": len(failed),
        "warnings": len(warnings),
        "slow_over_5s": len(slow),
    },
}

print(json.dumps(report, ensure_ascii=False, indent=2))

if warnings:
    print("\nADVERTENCIAS NO BLOQUEANTES:", file=sys.stderr)
    for c in warnings:
        print(f"- {c.name}: {c.detail}", file=sys.stderr)

if failed:
    print("\nFALLOS:", file=sys.stderr)
    for c in failed:
        print(f"- {c.name}: {c.detail}", file=sys.stderr)
    raise SystemExit(1)

print(
    f"\nIBERFIT producción: PASS · {len(checks)} controles · "
    f"0 fallos · {len(warnings)} advertencias · versión {production_version_raw}"
)
