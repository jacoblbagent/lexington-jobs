#!/usr/bin/env python3
"""Inline the experience filter into the jobs page.

Same shape as inject-favorites.py: the Astryx renderer strips script, so the
"3+ years" checkbox, its styles and the curated flag list
(src/experience.json) are added after the fact from scripts/experience-filter.*.
The JSON rides in a script[type="application/json"] block the filter reads, so
the data stays out of the script body and is still reviewable. The marker makes
a second run a no-op.

Must run after inject-location-filter.py and inject-favorites.py: the checkbox
joins that filter's row and inserts at the same point as the favorites box, so
running later puts it to the right of it.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MARKER = "data-arden-jobs-experience"
PAGES = ["index.html"]

css = (ROOT / "scripts" / "experience-filter.css").read_text(encoding="utf-8")
js = (ROOT / "scripts" / "experience-filter.js").read_text(encoding="utf-8")
data = json.loads((ROOT / "src" / "experience.json").read_text(encoding="utf-8"))

for guard in ("</script", "</style"):
    if guard in js or guard in css:
        raise SystemExit(f"scripts/experience-filter.* must not contain {guard}")

payload = (
    f'<style {MARKER}="css">\n{css}</style>\n'
    f'<script type="application/json" id="arden-experience-data">'
    f'{json.dumps(data, ensure_ascii=False, sort_keys=True)}</script>\n'
    f'<script {MARKER}="js">\n{js}</script>\n'
)

for name in PAGES:
    page = DOCS / name
    html = page.read_text(encoding="utf-8")
    if MARKER in html:
        print(f"skipped (already has the experience filter): {page.name}")
        continue
    if html.count("</body>") != 1:
        raise SystemExit(f"{page.name}: expected exactly one </body>")
    page.write_text(html.replace("</body>", payload + "</body>"), encoding="utf-8")
    print(f"injected experience filter: {page.name} ({len(data)} flagged listings)")
