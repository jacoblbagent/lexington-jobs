#!/usr/bin/env python3
"""Render src/jobsData.ts from jobs.me.json and the seniority cache.

jobsData.ts is what the page renders. The level is LinkedIn's own seniority
field, scraped off the posting page by collect-requirements.py and cached by job
id at ~/.hermes/cache/scratch/lexington/requirements.json.

LinkedIn's field is only the starting point: it tags engineers III and staff
engineers as "Entry level", which reads as wrong in a column. Where the title
carries a clear marker the title wins and the cell says so ("Senior (title)"),
so the guess sits next to the sourced value instead of replacing it silently.
"""
import json
import os
import re
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.expanduser("~/.hermes/cache/scratch/lexington/requirements.json")

HEADER = "export const jobs: Job[] = [\n"

ENTRY = re.compile(r"\b(intern|internship|co-?op|entry[- ]level|junior|jr|new grad|trainee|apprentice)\b", re.I)
RANK = re.compile(r"\b(sr|senior|lead|staff|stf|principal|chief|director|manager|supervisor|head|foreman|iii|iv)\b", re.I)


def level_for(title, field):
    """Title markers first, LinkedIn's field otherwise."""
    if ENTRY.search(title):
        return "Internship (title)" if re.search(r"\b(intern|co-?op)\b", title, re.I) else "Entry level (title)"
    if RANK.search(title):
        return "Staff (title)" if re.search(r"\b(staff|stf)\b", title, re.I) else "Senior (title)"
    if not field or field == "Not Applicable":
        return "Not listed"
    return field


def main():
    jobs = json.load(open(os.path.join(ROOT, "jobs.me.json")))
    cache = {}
    if os.path.exists(CACHE):
        cache = json.load(open(CACHE))

    blocks = []
    counts = {}
    for job in jobs:
        field = (cache.get(job["id"], {}) or {}).get("level") or ""
        level = level_for(job["title"], field)
        counts[level] = counts.get(level, 0) + 1
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
    for level, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {n:3}  {level}")


if __name__ == "__main__":
    main()
