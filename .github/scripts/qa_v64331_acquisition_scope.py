#!/usr/bin/env python3
"""Ensure V6.43.31 changes only the explicitly authorized public assets."""
from pathlib import Path
import subprocess
ROOT = Path("candidate/v628")
if (ROOT / "VERSION").read_text().strip() == "6.43.31":
    base = "7018222488e3b251e38cec0a3f4f5abb90c46db4"
    actual = set(subprocess.check_output(["git", "diff", "--name-only", base, "HEAD", "--", str(ROOT)], text=True).splitlines())
    expected = {str(ROOT / p) for p in ("VERSION", "CHANGELOG.md", "assets/analytics-config.js")}
    assert actual == expected, (actual-expected, expected-actual)
    print("COMMERCIAL_ACQUISITION_SCOPE_OK", len(actual))
