#!/usr/bin/env python3
"""Curated "requires 3 or more years" data for the jobs page.

The posting bodies are cached by collect-requirements.py, but the reduced
requirements list is capped at eight items, so the years line can be cut. This
file is curated by hand from the full posting text: one entry per listing that
states a minimum of three or more years of experience, with the sentence that
says so. Listings whose years are "preferred"/"desired", whose range starts
below three (0-3, 1-3), or whose alternative path needs only two years are
deliberately absent.

This script writes src/experience.json and asserts every quoted line still
appears in the cached posting, so a stale quote fails loudly instead of
silently flagging the wrong role. Run it only when the curation changes:

    python3 scripts/build-experience-data.py
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.expanduser("~/.hermes/cache/scratch/lexington/pages")
OUT = os.path.join(ROOT, "src", "experience.json")

# id -> (minimum years the posting asks for, a phrase that identifies the line)
FLAGGED = {
    "4488559479": (3, "3+ years of related experience"),
    "4490000385": (5, "Minimum 5 years of Process Engineering"),
    "4484293181": (3, "3+ years of engineering experience in a manufacturing environment"),
    "4481220072": (7, "7+ years of experience designing HVAC"),
    "4488608614": (5, "5+ years in mechanical design field"),
    "4489485028": (10, "More than ten years of directly relevant mechanical engineering experience"),
    "4485025183": (5, "5 years of experience in manufacturing continuous improvement"),
    "4451116062": (5, "5 to 7 years of experience in mechanical design"),
    "4486412525": (10, "10+ years of experience in industrial or commercial construction projects"),
    "4478493689": (4, "At least four years of related experience"),
    "4486407865": (3, "Minimum of 3 years’ experience in product engineering"),
    "4450378497": (8, "8–10+ years of progressive experience in mechanical design"),
    "4457611949": (5, "A minimum of 5 years of experience in project execution"),
    "4457115202": (5, "5 years manufacturing experience in CPG or process industry"),
    "4478738071": (3, "3+ years in automotive manufacturing"),
    "4439454815": (10, "10+ years of experience in injection molding"),
    "4478555579": (3, "More than 3 years of automotive manufacturing experience"),
    "4452826365": (5, "5+ years of engineering experience in a manufacturing environment"),
    "4480454944": (3, "3+ years of engineering experience in a manufacturing setting"),
    "4480717291": (10, "10+ years of experience in industrial or commercial construction projects"),
    "4481702262": (10, "10+ years of experience in industrial or commercial construction projects"),
    "4481239386": (10, "10+ yrs industrial/commercial construction projects"),
    "4476135882": (5, "Minimum 5 years practical work experience designing automotive components"),
    "4440733922": (7, "7+ years in automotive manufacturing"),
    "4471809117": (15, "15+ years of experience"),
    "4481203176": (5, "5+ years of experience in mechanical design"),
    "4456917642": (3, "Minimum 3-5 years of pharmaceutical manufacturing"),
    "4456358305": (7, "7 yrs. of practical automotive design experience"),
    "4367639683": (5, "Five or more years’ experience in metal forming"),
    "4365242747": (10, "10 to 20 years' experience designing mechanical building systems"),
    "4342797000": (5, "5 to 10+ years' experience designing mechanical building systems"),
    "4314971665": (3, "3 years of experience in manufacturing engineering"),
    "4295949522": (10, "10+ years working in an MEP engineering consulting firm"),
}


def blocks_for(job_id):
    """The posting's text blocks, via collect-requirements.py's own reducer."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "collect_requirements", os.path.join(ROOT, "scripts", "collect-requirements.py")
    )
    if spec is None or spec.loader is None:
        sys.exit("could not load scripts/collect-requirements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path = os.path.join(PAGES, job_id + ".html")
    with open(path, encoding="utf-8", errors="replace") as handle:
        page = handle.read()
    return [text for text, _kind in module.blocks(module.body_html(page))]


def main():
    out = {}
    for job_id, (years, needle) in FLAGGED.items():
        try:
            blocks = blocks_for(job_id)
        except FileNotFoundError:
            sys.exit(f"{job_id}: no cached posting under {PAGES}")
        hit = next((text for text in blocks if needle in text), None)
        if hit is None:
            sys.exit(f"{job_id}: quote no longer in the posting: {needle!r}")
        # The quoted line is the evidence, so keep it whole rather than a
        # snippet: the page shows it as the tooltip.
        out[job_id] = {"minYears": years, "evidence": re.sub(r"\s+", " ", hit).strip()}

    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(out, handle, indent=1, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    print(f"wrote {OUT}: {len(out)} listings at 3+ years")


if __name__ == "__main__":
    main()
