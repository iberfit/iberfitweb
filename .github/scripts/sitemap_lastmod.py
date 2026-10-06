#!/usr/bin/env python3
"""Maintain sitemap lastmod from the last committed change to each public HTML page.

Usage:
  python3 .github/scripts/sitemap_lastmod.py --write
  python3 .github/scripts/sitemap_lastmod.py --check

Commits to styles, deploy configuration or the sitemap itself do not change
page dates. The history must be available (git fetch-depth: 0 in CI).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "candidate" / "v628"
SITEMAP = PUBLIC / "sitemap.xml"
URL_BLOCK = re.compile(r"<url>.*?</url>", re.DOTALL)
LOC = re.compile(r"<loc>([^<]+)</loc>")
LASTMOD = re.compile(r"<lastmod>([^<]*)</lastmod>")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def page_lastmod(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "iberfit.cl"
        or not parsed.path.startswith("/")
        or not parsed.path.endswith("/")
        or parsed.query
        or parsed.fragment
        or ".." in parsed.path.split("/")
    ):
        raise ValueError(f"Invalid canonical sitemap URL: {url}")

    page = PUBLIC / parsed.path.lstrip("/") / "index.html"
    if not page.is_file():
        raise ValueError(f"Sitemap URL lacks public HTML: {url} ({page})")

    relative_path = page.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", relative_path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    date = result.stdout.strip()
    if not DATE.fullmatch(date):
        raise ValueError(
            f"No trustworthy git commit date for {relative_path}; "
            "do not invent a sitemap lastmod"
        )
    return date


def refresh(content: str) -> tuple[str, list[str], int]:
    parsed = ET.fromstring(content)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    entries = parsed.findall(f"{namespace}url")
    blocks = list(URL_BLOCK.finditer(content))
    if not entries or len(entries) != len(blocks):
        raise ValueError("Sitemap XML and URL entries do not match")
    seen: set[str] = set()
    issues: list[str] = []
    updated_count = 0

    def replace_block(match: re.Match[str]) -> str:
        nonlocal updated_count
        block = match.group(0)
        loc = LOC.search(block)
        lastmod = LASTMOD.search(block)
        if not loc or not lastmod:
            raise ValueError("Sitemap URL missing loc or lastmod")
        url = loc.group(1)
        if url in seen:
            raise ValueError(f"Duplicate sitemap URL: {url}")
        seen.add(url)
        expected = page_lastmod(url)
        current = lastmod.group(1)
        if current != expected:
            issues.append(f"{url}: {current} -> {expected}")
            updated_count += 1
        return block[:lastmod.start(1)] + expected + block[lastmod.end(1):]

    result = URL_BLOCK.sub(replace_block, content)
    if len(seen) != len(entries):
        raise ValueError("Sitemap URL validation incomplete")
    ET.fromstring(result)
    return result, issues, updated_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Fail on stale lastmod")
    mode.add_argument("--write", action="store_true", help="Refresh from git history")
    args = parser.parse_args()

    original = SITEMAP.read_text(encoding="utf-8")
    new, issues, changed = refresh(original)
    if args.check and issues:
        print("Sitemap lastmod is stale:", file=sys.stderr)
        for issue in issues:
            print(f" - {issue}", file=sys.stderr)
        return 1
    if args.write and changed:
        SITEMAP.write_text(new, encoding="utf-8")
    print(f"Sitemap lastmod: {len(URL_BLOCK.findall(original))} public URLs; "
          f"{changed} stale dates; mode={'check' if args.check else 'write'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError, ET.ParseError) as exc:
        print(f"Sitemap validation failed: {exc}", file=sys.stderr)
        sys.exit(2)
