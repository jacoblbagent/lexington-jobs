#!/usr/bin/env python3
"""Render src/jobsData.ts from jobs.me.json and the seniority cache.

jobsData.ts is what the page renders. The level comes from LinkedIn's own
seniority field, scraped off the posting page by collect-requirements.py; the
cache is keyed by job id at ~/.hermes/cache/scratch/lexington/requirements.json.
Postings LinkedIn reports as "Not Applicable" are labelled that way rather than
guessed at, so the column never claims more than the source says.
"""
import json
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.expanduser("~/.hermes/cache/scratch/lexington/requirements.json")

HEADER = "export const jobs: Job[] = [\n"


def main():
    jobs = json.load(open(os.path.join(ROOT, "jobs.me.json")))
    levels = {}
    if os.path.exists(CACHE):
        levels = json.load(open(CACHE))

    blocks = []
    for job in jobs:
        level = (levels.get(job["id"], {}) or {}).get("level") or "Not listed"
        posted = datetime.strptime(job["date"], "%Y-%m-%d").strftime("%b %-d, %Y")
        entry = {
            "id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "posted": posted,
            "url": job["url"],
            "level": level,
            "levelText": level,
        }
        lines = [f'  "{k}": {json.dumps(v, ensure_ascii=False)}' for k, v in entry.items()]
        blocks.append(" {\n" + ",\n".join(lines) + "\n }")

    out = HEADER + ",\n".join(blocks) + "\n];\n"
    with open(os.path.join(ROOT, "src", "jobsData.ts"), "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"wrote src/jobsData.ts: {len(blocks)} roles")


if __name__ == "__main__":
    main()
