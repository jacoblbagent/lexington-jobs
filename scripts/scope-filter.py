#!/usr/bin/env python3
"""Narrow the collected dump to mechanical engineering roles.

Scope: titles whose work is mechanical engineering - mechanical engineer and
mechanical designer roles, plus the manufacturing / process / product / design
/ production / tooling / test / reliability engineering roles a mechanical
engineer fills. Other disciplines at the same employers (civil, structural,
electrical, controls, software, ML, healthcare) are dropped by pattern, and
the stragglers by exact title.

Reads jobs.json, writes the surviving jobs to jobs.me.json for review.
"""
import json
import re

ENGINEER = re.compile(
    r"\b(engineer|engineering|designer|draft(sm[ae]n|er|ing)?|cad\b|cad/|technician)", re.I
)
MECHANICAL_DOMAIN = re.compile(
    r"(mechanical|manufactur\w*|process|product|production|design|tooling|hvac|"
    r"thermal|test|validat\w*|ndt|ndi|cad\b|draft\w*|solidworks|reliab\w*|packag\w*|"
    r"plant|project|application|machin\w*|equipment|piping|facilit\w*)",
    re.I,
)

# Other disciplines. A title that names one of these is not a mechanical role.
OTHER_DISCIPLINE = re.compile(
    r"\b(civil|structural|water|wastewater|transportation|highway|bridge|geotech\w*|"
    r"survey\w*|electrical|electronic\w*|controls?|scada|substation|grid|power|"
    r"machine learning|software|data|site reliability|sre|healthcare|clinical|"
    r"nurse|pharmac\w*|chemical|environmental|architect\w*|lighting|fire protection|"
    r"plumbing|traffic|landscape|botan\w*|safety)", re.I
)

# Collected but out of scope on a read of the title.
EXCLUDE = {
    "Advanced Specialist Product Engineering - Thermionic Cathodes for Vacuum Electron Tubes*",
    "AGV Project Engineer",
    "AGV Project Engineer (2027 Grad)",
    "Project Engineer - Autonomous Guided Vehicles",
    "Application Analyst / Logistics Automation Engineer",
    "Engineer – Internal Logistics Innovation & Projects",
    "Distribution Designer 2 - Grid",
    "Senior Distribution Designer 1 -- Grid",
    "BIM Designer - Electrical Project Lead",
    "Data Center Facilities Engineer",
    "Facilities Engineer",
    "Assistant Chief Engineer",
    "Chief Engineer",
    "Vehicle Manufacturing Engineer",
    "DFM Project Engineer",
    "Engineering Internship - Engineering Equipment & Metrology Improvement Intern",
    "HFN: Associate CAD Technician",
    "CAD/CADD Technician III",
    "Industrial CAD Draftsman",
    "Jr. CAD Draftsman",
    "CAD Draftsman",
    "Designer",
    "Designer 1",
    "Designer III",
    "SmartPlant P&ID Designer",
    "Water/Wastewater CAD Technician/Designer (Lexington or Louisville)",
    "Project Engineer (Water)",
    "Site Development Project Engineer",
    "Senior Project Engineer, Alternative Delivery",
    "Project Engineer - Entry Level Kentucky Region 2026 - 2027",
    "Project Engineer Co-Op - Lexington, KY",
    "Project Engineer- Lexington",
    "Project Engineer- Richmond",
    "Junior Construction Project Engineer - Federal Construction",
    "Accura Engineering and Consulting Project Engineer",
    "Piping Engineer (Advanced Manufacturing)",
    "Hardware Design Engineer - R0058471",
    "Design Engineer I",
}

# A technician or drafting title is not an engineering role unless the title
# also says engineer ("Reliability Engineer/Sr. Technician" stays).
TECHNICIAN = re.compile(r"\b(technician|tech|draftsman|drafter)\b", re.I)


def keep(job):
    # Card hrefs carry search-position tracking; the canonical posting URL is
    # the same path without the query string.
    job["url"] = job["url"].split("?")[0]
    title = job["title"]
    if title in EXCLUDE:
        return False
    if OTHER_DISCIPLINE.search(title):
        return False
    if TECHNICIAN.search(title) and not re.search(r"engineer", title, re.I):
        return False
    return bool(ENGINEER.search(title) and MECHANICAL_DOMAIN.search(title))


def main():
    jobs = json.load(open("jobs.json"))
    kept = [j for j in jobs if keep(j)]
    # Same title at the same employer is one role; keep the earliest posting.
    merged = {}
    for j in sorted(kept, key=lambda x: x["date"]):
        key = (j["title"].strip().lower(), j["company"].strip().lower())
        merged.setdefault(key, j)
    kept = sorted(merged.values(), key=lambda x: (x["date"], x["title"]), reverse=True)
    json.dump(kept, open("jobs.me.json", "w"), indent=1)
    print(f"{len(jobs)} collected -> {len(kept)} mechanical engineering roles")
    for j in sorted(kept, key=lambda x: (x["location"], x["title"].lower())):
        print(f"  {j['date']} | {j['location']:14} | {j['company'][:30]:30} | {j['title'][:78]}")


if __name__ == "__main__":
    main()
