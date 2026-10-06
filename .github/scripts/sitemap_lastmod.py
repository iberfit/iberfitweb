#!/usr/bin/env python3
"""Update candidate/v628/sitemap.xml using actual HTML modification dates.

Use committed per-page Git history, not the build date. An uncommitted HTML
change in the current release is dated to the UTC release day. This tool
does not update unrelated URLs or touch any page content.

Run after updating HTML and before the certified product commit:
    python3 .github/scripts/sitemap_lastmod.py
Check in CI or after certification:
    python3 .github/scripts/sitemap_lastmod.py --check
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone, date
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "candidate" / "v628"
SITEMAP = SITE / "sitemap.xml"
DOMAIN = "iberfit.cl"
XMLNS = "http://www.sitemaps.org/schemas/sitemap/0.9"
Q = lambda tag: f"{{{XMLNS}}}{tag}"


def git_output(*args: str) -> str:
    cmd = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, check=True,
    )
    return cmd.stdout.strip()


def relative_url_for(page: Path) -> str:
    rel = page.relative_to(SITE).as_posix()
    if rel == "index.html":
        return "/"
    if not rel.endswith("/index.html"):
        raise ValueError(f"Not a canonical HTML route: {rel}")
    return "/" + rel.removesuffix("index.html")


def page_for_url(url: str) -> Path:
    u = urlsplit(url)
    if u.scheme != "https" or u.netloc != DOMAIN or u.query or u.fragment:
        raise ValueError(f"Invalid canonical sitemap URL: {url}")
    if not u.path.startswith("/") or (u.path != "/" and not u.path.endswith("/")):
        raise ValueError(f"Non-canonical sitemap path: {url}")
    path = unquote(u.path)
    if ".." in path.split("/") or "\\" in path:
        raise ValueError(f"Unsafe sitemap path: {url}")
    relative = path.lstrip("/")
    page = SITE / relative / "index.html"
    if not page.is_file() or not page.resolve().is_relative_to(SITE.resolve()):
        raise ValueError(f"Missing published HTML page for {url}: {page}")
    return page


def last_content_change(page: Path) -> str:
    relative = page.relative_to(ROOT).as_posix()
    status = git_output("status", "--porcelain", "--", relative)
    if status:
        # Changed in this release but not yet committed: date of publication.
        return datetime.now(timezone.utc).date().isoformat()
    change = git_output("log", "-1", "--format=%cs", "HEAD", "--", relative)
    if not change:
        raise ValueError(f"No Git history for published page: {relative}")
    parsed = date.fromisoformat(change)
    if parsed > datetime.now(timezone.utc).date():
        raise ValueError(f"Future-dated HTML commit: {relative} -> {change}")
    return parsed.isoformat()


def generate() -> bytes:
    ET.register_namespace("", XMLNS)
    root = ET.parse(SITEMAP).getroot()
    if root.tag != Q("urlset"):
        raise ValueError("Expected standard sitemap urlset namespace")
    entries = root.findall(Q("url"))
    published = {relative_url_for(p) for p in SITE.rglob("index.html")}
    seen: set[str] = set()
    if not entries or len(entries) != len(published):
        raise ValueError(f"Sitemap/page count mismatch: sitemap={len(entries)}, pages={len(published)}")
    for entry in entries:
        loc = entry.find(Q("loc"))
        if loc is None or not loc.text:
            raise ValueError("Sitemap entry without loc")
        page = page_for_url(loc.text.strip())
        route = relative_url_for(page)
        if route in seen:
            raise ValueError(f"Duplicate sitemap route: {route}")
        seen.add(route)
        lastmod = entry.find(Q("lastmod"))
        if lastmod is None:
            lastmod = ET.SubElement(entry, Q("lastmod"))
        lastmod.text = last_content_change(page)
    if seen != published:
        raise ValueError(f"Sitemap coverage drift: missing={published-seen}, extra={seen-published}")
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if sitemap would change")
    args = parser.parse_args()
    result = generate()
    previous = SITEMAP.read_bytes()
    if args.check:
        if result != previous:
            print("SITEMAP_LASTMOD_DRIFT: run sitemap_lastmod.py and commit result", file=sys.stderr)
            return 1
        print("SITEMAP_LASTMOD_OK", len(ET.fromstring(result).findall(Q("url"))))
    else:
        if result != previous:
            SITEMAP.write_bytes(result)
            print("SITEMAP_UPDATED", len(ET.fromstring(result).findall(Q("url"))))
        else:
            print("SITEMAP_ALREADY_CURRENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
