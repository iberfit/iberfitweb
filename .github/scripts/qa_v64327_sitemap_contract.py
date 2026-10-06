#!/usr/bin/env python3
"""V6.43.27: verify page-level sitemap accuracy without altering live copy."""
from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "candidate/v628"
BASE = "04c414f0faacb7466576f6a105aa82d042445d3c"
NAMESPACE = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                          check=True, text=True).stdout.strip()


def entries(xml: bytes) -> dict[str, dict[str, str]]:
    root = ET.fromstring(xml)
    assert root.tag == NAMESPACE + "urlset", "sitemap namespace mismatch"
    result: dict[str, dict[str, str]] = {}
    for element in root.findall(NAMESPACE + "url"):
        fields = {child.tag.removeprefix(NAMESPACE): (child.text or "").strip() for child in element}
        loc = fields.get("loc")
        assert loc and loc not in result, f"missing/duplicate loc: {loc}"
        result[loc] = fields
    return result


before = entries(git("show", f"{BASE}:candidate/v628/sitemap.xml").encode())
after = entries((CANDIDATE / "sitemap.xml").read_bytes())
assert before.keys() == after.keys(), "sitemap URLs changed"
assert len(after) == 32, f"expected 32 canonical URLs, got {len(after)}"

for url, fields in after.items():
    expected_nondate = {key: value for key, value in before[url].items() if key != "lastmod"}
    current_nondate = {key: value for key, value in fields.items() if key != "lastmod"}
    assert current_nondate == expected_nondate, f"SEO metadata changed unexpectedly: {url}"
    changed = date.fromisoformat(fields["lastmod"])
    assert date(2026, 6, 22) <= changed <= datetime.now(timezone.utc).date(), url

# These are grounded in the last committed changes to each actual deployed page,
# not in release time or in the obsolete repository-root sitemap.
assert after["https://iberfit.cl/"]["lastmod"] == "2026-09-28", "Home lastmod"
assert after["https://iberfit.cl/online/"]["lastmod"] == "2026-09-24", "Online lastmod"
assert after["https://iberfit.cl/entrenador-personal-las-condes/"]["lastmod"] == "2026-10-01", "Las Condes lastmod"
assert after["https://iberfit.cl/"]["lastmod"] != after["https://iberfit.cl/entrenador-personal-las-condes/"]["lastmod"]

changed_files = set(git("diff", "--name-only", BASE, "--", "candidate/v628").splitlines())
allowed = {
    "candidate/v628/sitemap.xml",
    "candidate/v628/VERSION",
    "candidate/v628/CHANGELOG.md",
}
assert changed_files and changed_files <= allowed, f"Unexpected product scope: {changed_files}"
assert (CANDIDATE / "VERSION").read_text().strip() == "6.43.27"

print("V64327_SITEMAP_SCOPE_AND_DATES_OK", len(after), sorted(changed_files))
