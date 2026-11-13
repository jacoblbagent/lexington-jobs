#!/usr/bin/env python3
"""Inline the level filter into the jobs page.

Same shape as inject-location-filter.py: the Astryx renderer strips script, so
the filter is added after the fact as one <script> just before </body>, read
from scripts/level-filter.js. It reuses the location filter's styles, so no
second <style> block is written. Re-running is a no-op thanks to the marker
attribute. Must be injected after the location filter, which owns row
visibility; the level filter calls back into it.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MARKER = "data-arden-jobs-level"
PAGES = ["index.html"]

js = (ROOT / "scripts" / "level-filter.js").read_text(encoding="utf-8")
if "</script" in js:
    raise SystemExit("scripts/level-filter.js must not contain </script")

payload = f'<script {MARKER}="js">\n{js}</script>\n'

for name in PAGES:
    page = DOCS / name
    html = page.read_text(encoding="utf-8")
    if MARKER in html:
        print(f"skipped (already filtered): {page.name}")
        continue
    if html.count("</body>") != 1:
        raise SystemExit(f"{page.name}: expected exactly one </body>")
    page.write_text(html.replace("</body>", payload + "</body>"), encoding="utf-8")
    print(f"injected level filter: {page.name}")
