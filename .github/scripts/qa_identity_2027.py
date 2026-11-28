#!/usr/bin/env python3
"""Exact scope and geometry guard for the approved 2027 identity; no network."""
from pathlib import Path
import subprocess
import struct
import zlib
import xml.etree.ElementTree as ET

ROOT = Path("candidate/v628")
BASE = "626fb159c3fb45e62cf8ef85cbbdf2dedeada680"
REPLACEMENTS = [["https://iberfit.cl/assets/iberfit-isotipo-oficial.png","https://iberfit.cl/assets/favicon-2027-512x512.png"],["/assets/iberfit-isotipo-oficial.png","/assets/iberfit-isotipo-2027.svg"],["/assets/favicon.ico","/assets/favicon-2027.ico"],["/assets/favicon-48x48.png","/assets/favicon-2027-48x48.png"],["/assets/favicon-96x96.png","/assets/favicon-2027-96x96.png"],["/assets/apple-touch-icon.png","/assets/apple-touch-icon-2027.png"]]
CSS = "\n/* 6.43.36 — approved identity 2027. Preserve existing logo box and header layout. */\n.brand-mark[src=\"/assets/iberfit-isotipo-2027.svg\"]{aspect-ratio:1!important;object-fit:contain!important}\n.cta-panel-inner:after{background-image:url('/assets/iberfit-isotipo-2027-dorado.svg');aspect-ratio:1}\n"
ASSETS = ["iberfit-isotipo-2027.svg","iberfit-isotipo-2027-dorado.svg","favicon-2027.ico","favicon-2027-48x48.png","favicon-2027-96x96.png","apple-touch-icon-2027.png","favicon-2027-192x192.png","favicon-2027-512x512.png"]

def transform(text):
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text

def prior(path):
    return subprocess.check_output(["git", "show", BASE+":"+path.as_posix()])

def png_check(path, size):
    b = path.read_bytes()
    assert b[:8] == b"\x89PNG\r\n\x1a\n"
    i, idat, palette = 8, [], b""
    while i < len(b):
        n = struct.unpack(">I", b[i:i+4])[0]
        kind = b[i+4:i+8]
        data = b[i+8:i+8+n]
        assert zlib.crc32(kind+data) == struct.unpack(">I", b[i+8+n:i+12+n])[0], path
        if kind == b"IHDR":
            assert struct.unpack(">IIBBBBB", data) == (size,size,8,3,0,0,0), path
        if kind == b"PLTE":
            palette = data
        if kind == b"IDAT":
            idat.append(data)
        i += 12+n
    assert i == len(b) and len(palette) == 51
    assert palette[:3] == bytes([31,61,43]) and palette[-3:] == bytes([184,151,58])
    raw = zlib.decompress(b"".join(idat))
    assert len(raw) == size*(size+1)
    assert all(raw[y*(size+1)] == 0 for y in range(size))
    assert max(raw) == 16 and min(raw) == 0

def check():
    pages = sorted(ROOT.rglob("*.html"))
    assert len(pages) == 33
    for p in pages:
        actual = p.read_bytes()
        assert actual == transform(prior(p).decode("utf-8")).encode("utf-8"), ("Non-brand HTML change",p)
        assert b"/assets/iberfit-isotipo-2027.svg" in actual
    css = ROOT/"assets/ux.v64322.css"
    assert css.read_bytes() == prior(css) + CSS.encode()
    manifest = ROOT/"manifest.webmanifest"
    assert manifest.read_bytes() == prior(manifest).replace(b"favicon-192x192.png", b"favicon-2027-192x192.png").replace(b"favicon-512x512.png", b"favicon-2027-512x512.png")
    expected = {p.as_posix() for p in pages} | {(ROOT/"assets"/x).as_posix() for x in ASSETS} | {(ROOT/x).as_posix() for x in ("VERSION","CHANGELOG.md","manifest.webmanifest","sitemap.xml","assets/ux.v64322.css")}
    changed = set(subprocess.check_output(["git","diff","--name-only",BASE,"HEAD","--",ROOT.as_posix()],text=True).splitlines())
    assert changed == expected, (changed-expected,expected-changed)
    master = Path("brand/2027/Principal_Dorado.svg")
    assert subprocess.check_output(["git","hash-object",str(master)],text=True).strip() == "513e821acd346cb55d1939b483507b477ea3afc7"
    namespace = "{http://www.w3.org/2000/svg}"
    original = ET.parse(master).getroot()
    geometry = [p.attrib["d"] for p in original.findall(namespace+"path")]
    assert len(geometry) == 8
    for name in ASSETS[:2]:
        root = ET.parse(ROOT/"assets"/name).getroot()
        assert root.attrib["viewBox"] == original.attrib["viewBox"]
        assert [p.attrib["d"] for p in root.findall(namespace+"path")] == geometry
    for size in (48,96,180,192,512):
        name = "apple-touch-icon-2027.png" if size == 180 else f"favicon-2027-{size}x{size}.png"
        png_check(ROOT/"assets"/name,size)
    ico = (ROOT/"assets/favicon-2027.ico").read_bytes()
    assert ico[:6] == bytes([0,0,1,0,1,0])
    assert ico[22:] == (ROOT/"assets/favicon-2027-48x48.png").read_bytes()
    print("IDENTITY_2027_SCOPE_OK: 33 HTML pages; 8 vector contours; 5 validated raster icons; historical assets preserved")

if __name__ == "__main__":
    check()
