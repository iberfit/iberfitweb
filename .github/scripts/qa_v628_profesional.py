#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path("candidate/v628")
ASSETS = ROOT / "assets"

class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.canonical = []
        self.alternates = {}
        self.external = []
        self.visible = []
        self.jsonld = []
        self._in_script = False
        self._script_type = ""
        self._script_buf = []

    def handle_starttag(self, tag, attrs_list):
        attrs = {k: (v or "") for k, v in attrs_list}
        if tag == "html":
            self.lang = attrs.get("lang", "")
        if tag == "link":
            rel = attrs.get("rel", "")
            href = attrs.get("href", "")
            if rel == "canonical" and href:
                self.canonical.append(href)
            if rel == "alternate" and attrs.get("hreflang") and href:
                self.alternates[attrs["hreflang"]] = href
        for key in ("href", "src"):
            value = attrs.get(key, "")
            if value.startswith(("https://", "http://")):
                self.external.append(value)
        if tag == "script":
            self._in_script = True
            self._script_type = attrs.get("type", "")
            self._script_buf = []

    def handle_endtag(self, tag):
        if tag == "script":
            if self._script_type == "application/ld+json":
                self.jsonld.append("".join(self._script_buf).strip())
            self._in_script = False
            self._script_type = ""
            self._script_buf = []

    def handle_data(self, data):
        if self._in_script:
            self._script_buf.append(data)
        else:
            value = " ".join(data.split())
            if value:
                self.visible.append(value)

def fail(errors, message):
    errors.append(message)

def main():
    errors = []
    pages = sorted(ROOT.rglob("*.html"))
    if not pages:
        raise SystemExit("No hay HTML para auditar")

    # Presupuestos conservadores: evitan crecimiento silencioso sin forzar rediseño.
    limits = {
        "styles.v628.css": 120_000,
        "app.v623.js": 40_000,
        "analytics.v6211.js": 25_000,
        "analytics-config.js": 5_000,
        "iberfit-isotipo-oficial.png": 50_000,
    }
    for name, limit in limits.items():
        path = ASSETS / name
        if not path.exists():
            fail(errors, f"Recurso crítico ausente: {name}")
        elif path.stat().st_size > limit:
            fail(errors, f"Presupuesto excedido: {name}={path.stat().st_size} > {limit} bytes")

    # Ninguna imagen responsive individual debe superar 450 KB.
    for image in ASSETS.glob("*.webp"):
        if image.stat().st_size > 450_000:
            fail(errors, f"Imagen demasiado pesada: {image.name}={image.stat().st_size} bytes")

    allowed_external_hosts = {
        "iberfit.cl",
        "app.iberfit.cl",
        "wa.me",
        "www.google.com",
        "share.google",
        "www.googletagmanager.com",
        "connect.facebook.net",
        "www.facebook.com",
    }
    spanish_forbidden = re.compile(r"\b(longevity|wellness|coaching|assessment)\b", re.I)

    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        if rel == "404.html":
            continue
        text = page.read_text("utf-8")
        parser = AuditParser()
        parser.feed(text)

        if len(parser.canonical) != 1:
            fail(errors, f"{rel}: canonical debe existir exactamente una vez")
        for lang in ("es", "en", "x-default"):
            if lang not in parser.alternates:
                fail(errors, f"{rel}: hreflang {lang} ausente")

        for url in parser.external:
            host = (urlparse(url).hostname or "").lower()
            if host and host not in allowed_external_hosts:
                fail(errors, f"{rel}: tercero no autorizado {host} ({url})")

        if parser.lang == "es":
            visible = " ".join(parser.visible)
            hit = spanish_forbidden.search(visible)
            if hit:
                fail(errors, f"{rel}: nombre comercial no castellano visible: {hit.group(0)}")

        for raw in parser.jsonld:
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                fail(errors, f"{rel}: JSON-LD inválido: {exc}")
                continue
            serialized = json.dumps(data, ensure_ascii=False)
            if "IBERFIT" not in serialized:
                fail(errors, f"{rel}: JSON-LD sin referencia IBERFIT")

    # Evitar secretos o credenciales accidentales en el sitio estático.
    secret_patterns = (
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"service_role", re.I),
        re.compile(r"SUPABASE_SERVICE_ROLE", re.I),
        re.compile(r"PRIVATE_KEY", re.I),
    )
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".css", ".json", ".webmanifest", ".txt", ".md"}:
            continue
        source = path.read_text("utf-8", errors="ignore")
        for pattern in secret_patterns:
            if pattern.search(source):
                fail(errors, f"{path.relative_to(ROOT)}: posible secreto expuesto ({pattern.pattern})")

    if errors:
        raise SystemExit("QA profesional V6.28 FAIL\n- " + "\n- ".join(errors))

    total_assets = sum(p.stat().st_size for p in ASSETS.iterdir() if p.is_file())
    print(f"QA profesional V6.28 PASS · {len(pages)} HTML · activos {total_assets/1024:.1f} KiB · 0 terceros inesperados · 0 secretos")

if __name__ == "__main__":
    main()
